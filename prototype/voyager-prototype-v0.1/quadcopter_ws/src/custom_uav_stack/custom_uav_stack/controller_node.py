#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import numpy as np

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from std_msgs.msg import Float64MultiArray, Bool

class PID:
    def __init__(self, kp, ki, kd, limit_integral=5.0, limit_output=10.0, d_filter_alpha=0.25):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.limit_integral = limit_integral
        self.limit_output = limit_output
        self.d_filter_alpha = d_filter_alpha
        self.integral = 0.0
        self.last_error = 0.0
        self.filtered_d = 0.0
        self.first_run = True

    def update(self, error, dt):
        if dt <= 0.0:
            return 0.0
        p_term = self.kp * error
        
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.limit_integral, self.limit_integral)
        i_term = self.ki * self.integral
        
        if self.first_run:
            d_term = 0.0
            self.first_run = False
        else:
            raw_d = (error - self.last_error) / dt
            # Low pass filter on derivative term
            self.filtered_d = self.d_filter_alpha * raw_d + (1.0 - self.d_filter_alpha) * self.filtered_d
            d_term = self.kd * self.filtered_d
        
        self.last_error = error
        output = p_term + i_term + d_term
        return np.clip(output, -self.limit_output, self.limit_output)

    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.filtered_d = 0.0
        self.first_run = True

class QuadcopterController(Node):
    def __init__(self):
        super().__init__('quadcopter_controller')
        
        # --- Drone Constants (matching simulator) ---
        self.m = 1.5           # mass (kg)
        self.g = 9.81          # gravity (m/s^2)
        self.d_arm = 0.25
        self.l = self.d_arm / np.sqrt(2.0)
        self.k_f = 1.5e-5      # thrust coefficient
        self.k_m = 2.25e-7     # torque coefficient
        self.max_motor_speed = 800.0  # rad/s
        
        # --- State variables ---
        self.armed = False
        self.pos = np.zeros(3)
        self.vel = np.zeros(3)
        self.q = np.array([1.0, 0.0, 0.0, 0.0])  # qw, qx, qy, qz
        self.euler = np.zeros(3)  # roll, pitch, yaw (radians)
        self.w = np.zeros(3)  # p, q, r (body angular rates)
        
        # Setpoints
        self.target_pos = np.zeros(3)
        self.target_yaw = 0.0
        
        self.target_roll_deg = 0.0
        self.target_pitch_deg = 0.0
        
        # --- Controller Gains ---
        # Position PID (outputs desired acceleration in world x, y, z)
        self.pid_x = PID(kp=1.5, ki=0.05, kd=1.2, limit_integral=2.0, limit_output=4.0, d_filter_alpha=0.5)
        self.pid_y = PID(kp=1.5, ki=0.05, kd=1.2, limit_integral=2.0, limit_output=4.0, d_filter_alpha=0.5)
        self.pid_z = PID(kp=3.0, ki=0.15, kd=2.2, limit_integral=3.0, limit_output=8.0, d_filter_alpha=0.5)
        
        # Attitude Loop (P-only, converts angle error to desired angular rate)
        self.kp_att_rp = 6.5
        self.kp_att_y = 4.0
        
        # Rate PID (outputs desired moment/torque in body x, y, z)
        self.pid_roll_rate = PID(kp=0.15, ki=0.08, kd=0.015, limit_integral=0.5, limit_output=1.5, d_filter_alpha=0.10)
        self.pid_pitch_rate = PID(kp=0.15, ki=0.08, kd=0.015, limit_integral=0.5, limit_output=1.5, d_filter_alpha=0.10)
        self.pid_yaw_rate = PID(kp=0.25, ki=0.05, kd=0.005, limit_integral=0.5, limit_output=1.0, d_filter_alpha=0.10)
        
        # Timing
        self.last_odom_time = self.get_clock().now()
        self.last_imu_time = self.get_clock().now()
        
        # --- Publishers & Subscribers ---
        self.motor_pub = self.create_publisher(Float64MultiArray, '/actuators/motor_speeds', 10)
        self.telemetry_pub = self.create_publisher(Float64MultiArray, '/controller/telemetry', 10)
        
        self.odom_sub = self.create_subscription(Odometry, '/sim/odom', self.odom_callback, 10)
        self.imu_sub = self.create_subscription(Imu, '/sim/imu', self.imu_callback, 10)
        
        self.setpoint_sub = self.create_subscription(
            PoseStamped, '/controller/setpoint', self.setpoint_callback, 10)
        self.tuning_sub = self.create_subscription(
            Float64MultiArray, '/controller/pid_tuning', self.tuning_callback, 10)
        self.arm_sub = self.create_subscription(
            Bool, '/controller/arm_disarm', self.arm_callback, 10)
            
        # Watchdog timer to safety-disarm if telemetry times out (0.5 seconds)
        self.watchdog = self.create_timer(0.1, self.safety_watchdog)
        
        self.get_logger().info("Cascaded PID Flight Controller Node initialized.")

    def arm_callback(self, msg: Bool):
        self.armed = msg.data
        if self.armed:
            self.reset_integrators()
            # Set target setpoint to current position/heading to avoid takeoff jumps
            self.target_pos = np.copy(self.pos)
            self.target_yaw = self.euler[2]
            self.get_logger().info("VEHICLE ARMED")
        else:
            self.get_logger().info("VEHICLE DISARMED")

    def setpoint_callback(self, msg: PoseStamped):
        self.target_pos[0] = msg.pose.position.x
        self.target_pos[1] = msg.pose.position.y
        self.target_pos[2] = msg.pose.position.z
        
        # Extract yaw from quaternion setpoint
        q = [msg.pose.orientation.w, msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z]
        _, _, yaw = self.quat_to_euler(q)
        self.target_yaw = yaw

    def tuning_callback(self, msg: Float64MultiArray):
        # Expected size: 13
        if len(msg.data) == 13:
            data = msg.data
            self.pid_x.kp = data[0]
            self.pid_x.kd = data[1]
            self.pid_x.ki = data[2]
            
            self.pid_y.kp = data[0]
            self.pid_y.kd = data[1]
            self.pid_y.ki = data[2]
            
            self.pid_z.kp = data[3]
            self.pid_z.kd = data[4]
            self.pid_z.ki = data[5]
            
            self.kp_att_rp = data[6]
            self.kp_att_y = data[7]
            
            self.pid_roll_rate.kp = data[8]
            self.pid_roll_rate.kd = data[9]
            self.pid_roll_rate.ki = data[10]
            
            self.pid_pitch_rate.kp = data[8]
            self.pid_pitch_rate.kd = data[9]
            self.pid_pitch_rate.ki = data[10]
            
            self.pid_yaw_rate.kp = data[11]
            self.pid_yaw_rate.kd = 0.0 # Yaw rate derivative is 0 by default
            self.pid_yaw_rate.ki = data[12]
            
            self.get_logger().info("PID parameters updated successfully!")

    def quat_to_euler(self, q):
        qw, qx, qy, qz = q
        # Roll
        sinr_cosp = 2.0 * (qw * qx + qy * qz)
        cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
        roll = np.arctan2(sinr_cosp, cosr_cosp)
        
        # Pitch
        sinp = 2.0 * (qw * qy - qz * qx)
        if np.abs(sinp) >= 1.0:
            pitch = np.sign(sinp) * np.pi / 2.0
        else:
            pitch = np.arcsin(sinp)
            
        # Yaw
        siny_cosp = 2.0 * (qw * qz + qx * qy)
        cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        
        return roll, pitch, yaw

    def reset_integrators(self):
        self.pid_x.reset()
        self.pid_y.reset()
        self.pid_z.reset()
        self.pid_roll_rate.reset()
        self.pid_pitch_rate.reset()
        self.pid_yaw_rate.reset()

    def safety_watchdog(self):
        # Disarm if orientation exceeds 60 degrees (crash)
        roll_deg = np.degrees(self.euler[0])
        pitch_deg = np.degrees(self.euler[1])
        if self.armed and (abs(roll_deg) > 60.0 or abs(pitch_deg) > 60.0):
            self.armed = False
            self.get_logger().warn("CRASH DETECTED! DISARMING FOR SAFETY.")
            
        # Check telemetry timeout
        now = self.get_clock().now()
        dt_odom = (now - self.last_odom_time).nanoseconds / 1e9
        dt_imu = (now - self.last_imu_time).nanoseconds / 1e9
        if self.armed and (dt_odom > 0.5 or dt_imu > 0.5):
            self.armed = False
            self.get_logger().warn("TELEMETRY TIMEOUT! DISARMING FOR SAFETY.")

    def odom_callback(self, msg: Odometry):
        now = self.get_clock().now()
        self.last_odom_time = now
        dt = 0.02  # Enforce nominal 50Hz step for position PID stability
        
        # Update current position and velocity (in world frame)
        self.pos[0] = msg.pose.pose.position.x
        self.pos[1] = msg.pose.pose.position.y
        self.pos[2] = msg.pose.pose.position.z
        
        # Rotate linear velocities from body to world frame
        # Odometry twist linear is in child_frame (body frame)
        self.q = np.array([msg.pose.pose.orientation.w, msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z])
        self.euler[0], self.euler[1], self.euler[2] = self.quat_to_euler(self.q)
        
        qw, qx, qy, qz = self.q
        R = np.array([
            [1.0 - 2.0*(qy**2 + qz**2), 2.0*(qx*qy - qw*qz), 2.0*(qx*qz + qw*qy)],
            [2.0*(qx*qy + qw*qz), 1.0 - 2.0*(qx**2 + qz**2), 2.0*(qy*qz - qw*qx)],
            [2.0*(qx*qz - qw*qy), 2.0*(qy*qz + qw*qx), 1.0 - 2.0*(qx**2 + qy**2)]
        ])
        vel_body = np.array([msg.twist.twist.linear.x, msg.twist.twist.linear.y, msg.twist.twist.linear.z])
        self.vel = R @ vel_body
        
        # Run position loop if armed
        if self.armed:
            self.run_position_control(dt)
        else:
            self.publish_zero_motors()
            
    def imu_callback(self, msg: Imu):
        now = self.get_clock().now()
        self.last_imu_time = now
        dt = 0.004  # Enforce nominal 250Hz step for attitude/rate PID stability
        
        # Update orientation and body rates
        self.q = np.array([msg.orientation.w, msg.orientation.x, msg.orientation.y, msg.orientation.z])
        self.euler[0], self.euler[1], self.euler[2] = self.quat_to_euler(self.q)
        self.w = np.array([msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z])
        
        # Run inner attitude and rate loops if armed
        if self.armed:
            self.run_attitude_rate_control(dt)
        else:
            self.publish_zero_motors()

    def run_position_control(self, dt):
        if dt <= 0.0:
            return
            
        # 1. Position error
        err_pos = self.target_pos - self.pos
        
        # 2. PID outputs desired acceleration in world frame
        ax_des = self.pid_x.update(err_pos[0], dt)
        ay_des = self.pid_y.update(err_pos[1], dt)
        az_des = self.pid_z.update(err_pos[2], dt)
        
        # 3. Rotate horizontal accelerations into yaw-aligned body frame
        yaw = self.euler[2]
        ax_body = ax_des * np.cos(yaw) + ay_des * np.sin(yaw)
        ay_body = -ax_des * np.sin(yaw) + ay_des * np.cos(yaw)
        
        # 4. Convert horizontal accelerations to target tilt angles
        # pitch: forward acceleration -> pitch down (negative pitch)
        # roll: leftward acceleration -> roll left (negative roll)
        self.target_pitch_deg = np.degrees(ax_body / self.g)
        self.target_roll_deg = np.degrees(-ay_body / self.g)
        
        # Limit target angles to +- 25 degrees
        self.target_pitch_deg = np.clip(self.target_pitch_deg, -25.0, 25.0)
        self.target_roll_deg = np.clip(self.target_roll_deg, -25.0, 25.0)
        
        # 5. Vertical channel -> desired thrust magnitude
        # Feedforward term: m * g, divided by cos(roll)*cos(pitch) to compensate tilt
        cos_roll = np.cos(np.radians(self.target_roll_deg))
        cos_pitch = np.cos(np.radians(self.target_pitch_deg))
        tilt_comp = cos_roll * cos_pitch
        if tilt_comp < 0.5:
            tilt_comp = 0.5 # prevent division by very small numbers
            
        self.thrust_des = self.m * (self.g + az_des) / tilt_comp
        # Limit thrust to physical boundaries
        max_thrust = 4.0 * self.k_f * (self.max_motor_speed ** 2)
        self.thrust_des = np.clip(self.thrust_des, 0.0, max_thrust)

    def run_attitude_rate_control(self, dt):
        if dt <= 0.0:
            return
            
        # Wait until position loop has run at least once to get thrust_des
        if not hasattr(self, 'thrust_des'):
            self.thrust_des = self.m * self.g
            
        # 1. Attitude Loop (P controller on angle error)
        roll_target = np.radians(self.target_roll_deg)
        pitch_target = np.radians(self.target_pitch_deg)
        
        err_roll = roll_target - self.euler[0]
        err_pitch = pitch_target - self.euler[1]
        
        # Yaw wrapping: wrap yaw error to [-pi, pi]
        err_yaw = self.target_yaw - self.euler[2]
        err_yaw = (err_yaw + np.pi) % (2.0 * np.pi) - np.pi
        
        # Desired body rates (rad/s)
        p_des = self.kp_att_rp * err_roll
        q_des = self.kp_att_rp * err_pitch
        r_des = self.kp_att_y * err_yaw
        
        # 2. Rate Loop (PID controller on rate error)
        err_p = p_des - self.w[0]
        err_q = q_des - self.w[1]
        err_r = r_des - self.w[2]
        
        tau_x = self.pid_roll_rate.update(err_p, dt)
        tau_y = self.pid_pitch_rate.update(err_q, dt)
        tau_z = self.pid_yaw_rate.update(err_r, dt)
        
        # 3. Motor Mixer (solving mapping for X-quad)
        T = self.thrust_des
        
        F = np.zeros(4)
        F[0] = T/4.0 + tau_x/(4.0*self.l) - tau_y/(4.0*self.l) + tau_z/(4.0*(self.k_m/self.k_f * self.l))
        F[1] = T/4.0 - tau_x/(4.0*self.l) + tau_y/(4.0*self.l) + tau_z/(4.0*(self.k_m/self.k_f * self.l))
        F[2] = T/4.0 - tau_x/(4.0*self.l) - tau_y/(4.0*self.l) - tau_z/(4.0*(self.k_m/self.k_f * self.l))
        F[3] = T/4.0 + tau_x/(4.0*self.l) + tau_y/(4.0*self.l) - tau_z/(4.0*(self.k_m/self.k_f * self.l))
        
        # Simple drag to thrust ratio for yaw moment: c = k_m
        # Let's verify mixer equations with physical properties:
        # F_1 = T/4 + tau_x/(4l) - tau_y/(4l) + tau_z/(4 * (k_m / k_f))
        # Let's write them cleanly:
        c = self.k_m / self.k_f
        F[0] = T/4.0 + tau_x/(4.0*self.l) - tau_y/(4.0*self.l) + tau_z/(4.0*c)
        F[1] = T/4.0 - tau_x/(4.0*self.l) + tau_y/(4.0*self.l) + tau_z/(4.0*c)
        F[2] = T/4.0 - tau_x/(4.0*self.l) - tau_y/(4.0*self.l) - tau_z/(4.0*c)
        F[3] = T/4.0 + tau_x/(4.0*self.l) + tau_y/(4.0*self.l) - tau_z/(4.0*c)
        
        # Force to motor speeds (rad/s)
        F = np.clip(F, 0.0, None)
        cmd_speeds = np.sqrt(F / self.k_f)
        cmd_speeds = np.clip(cmd_speeds, 0.0, self.max_motor_speed)
        
        # Publish motor speeds
        msg = Float64MultiArray()
        msg.data = list(cmd_speeds)
        self.motor_pub.publish(msg)
        
        # Publish telemetry
        self.publish_telemetry(cmd_speeds)

    def publish_zero_motors(self):
        msg = Float64MultiArray()
        msg.data = [0.0, 0.0, 0.0, 0.0]
        self.motor_pub.publish(msg)
        self.publish_telemetry([0.0, 0.0, 0.0, 0.0])

    def publish_telemetry(self, cmd_speeds):
        # [px, py, pz, roll, pitch, yaw, target_x, target_y, target_z, target_roll, target_pitch, target_yaw, m1, m2, m3, m4, armed]
        telem = Float64MultiArray()
        telem.data = [
            self.pos[0], self.pos[1], self.pos[2],
            np.degrees(self.euler[0]), np.degrees(self.euler[1]), np.degrees(self.euler[2]),
            self.target_pos[0], self.target_pos[1], self.target_pos[2],
            self.target_roll_deg, self.target_pitch_deg, np.degrees(self.target_yaw),
            cmd_speeds[0], cmd_speeds[1], cmd_speeds[2], cmd_speeds[3],
            1.0 if self.armed else 0.0
        ]
        self.telemetry_pub.publish(telem)

def main(args=None):
    rclpy.init(args=args)
    node = QuadcopterController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
