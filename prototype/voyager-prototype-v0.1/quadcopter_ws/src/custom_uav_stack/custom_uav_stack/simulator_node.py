#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import numpy as np
import time

from geometry_msgs.msg import PoseStamped, Wrench, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from std_msgs.msg import Float64MultiArray, Bool
from tf2_ros import TransformBroadcaster

class QuadcopterSimulator(Node):
    def __init__(self):
        super().__init__('quadcopter_simulator')
        
        # --- Physical Parameters ---
        self.m = 1.5           # mass (kg)
        self.g = 9.81          # gravity (m/s^2)
        
        # Moments of inertia (kg*m^2)
        self.Ixx = 0.015
        self.Iyy = 0.015
        self.Izz = 0.025
        self.I = np.diag([self.Ixx, self.Iyy, self.Izz])
        self.I_inv = np.diag([1.0/self.Ixx, 1.0/self.Iyy, 1.0/self.Izz])
        
        self.d_arm = 0.25      # arm length (m)
        self.l = self.d_arm / np.sqrt(2.0)  # motor layout distance to axes (X-quad)
        
        # Rotor coefficients
        self.k_f = 1.5e-5      # thrust coefficient (N / (rad/s)^2)
        self.k_m = 2.25e-7     # torque coefficient (N*m / (rad/s)^2)
        
        # Drag coefficients
        self.C_drag_xy = 0.15   # horizontal translation drag
        self.C_drag_z = 0.30    # vertical translation drag
        self.C_rot = 0.05       # rotational damping
        
        # Max motor speed limit
        self.max_motor_speed = 800.0  # rad/s
        
        # --- State Vector ---
        # S = [x, y, z, vx, vy, vz, qw, qx, qy, qz, p, q, r]
        self.state = np.array([0.0, 0.0, 0.0,  # position
                               0.0, 0.0, 0.0,  # velocity
                               1.0, 0.0, 0.0, 0.0,  # quaternion
                               0.0, 0.0, 0.0]) # body angular velocity
        
        # Motor speeds state (rad/s)
        self.motor_speeds = np.zeros(4)
        
        # External disturbances (wind forces and moments in world/body frames)
        self.dist_force_world = np.zeros(3)
        self.dist_torque_body = np.zeros(3)
        
        # Simulation parameters
        self.dt = 0.004  # Integration step size (250 Hz)
        
        # --- ROS 2 Publishers & Subscribers ---
        self.odom_pub = self.create_publisher(Odometry, '/sim/odom', 10)
        self.imu_pub = self.create_publisher(Imu, '/sim/imu', 10)
        
        self.motor_sub = self.create_subscription(
            Float64MultiArray, '/actuators/motor_speeds', self.motor_callback, 10)
        self.dist_sub = self.create_subscription(
            Wrench, '/sim/disturbance', self.disturbance_callback, 10)
        self.reset_sub = self.create_subscription(
            Bool, '/sim/reset', self.reset_callback, 10)
        
        # TF Broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Simulation Timer
        self.timer = self.create_timer(self.dt, self.physics_step)
        
        # Setup telemetry tracking (for specific force calculations)
        self.linear_accel_body = np.zeros(3)
        
        self.get_logger().info("Quadcopter 6-DOF Simulator Node initialized.")

    def motor_callback(self, msg: Float64MultiArray):
        if len(msg.data) == 4:
            self.motor_speeds = np.array(msg.data)
            # Clamp commanded speeds
            self.motor_speeds = np.clip(self.motor_speeds, 0.0, self.max_motor_speed)

    def disturbance_callback(self, msg: Wrench):
        self.dist_force_world = np.array([msg.force.x, msg.force.y, msg.force.z])
        self.dist_torque_body = np.array([msg.torque.x, msg.torque.y, msg.torque.z])

    def reset_callback(self, msg: Bool):
        if msg.data:
            self.state = np.array([0.0, 0.0, 0.0,  # position
                                   0.0, 0.0, 0.0,  # velocity
                                   1.0, 0.0, 0.0, 0.0,  # quaternion
                                   0.0, 0.0, 0.0]) # body angular velocity
            self.motor_speeds = np.zeros(4)
            self.dist_force_world = np.zeros(3)
            self.dist_torque_body = np.zeros(3)
            self.get_logger().info("Simulator state reset to origin.")

    def get_rotation_matrix(self, q):
        qw, qx, qy, qz = q
        # Ensure normalization
        norm = np.linalg.norm(q)
        if norm > 1e-6:
            qw, qx, qy, qz = q / norm
        
        R = np.array([
            [1.0 - 2.0*(qy**2 + qz**2), 2.0*(qx*qy - qw*qz), 2.0*(qx*qz + qw*qy)],
            [2.0*(qx*qy + qw*qz), 1.0 - 2.0*(qx**2 + qz**2), 2.0*(qy*qz - qw*qx)],
            [2.0*(qx*qz - qw*qy), 2.0*(qy*qz + qw*qx), 1.0 - 2.0*(qx**2 + qy**2)]
        ])
        return R

    def quaternion_derivative(self, q, w):
        qw, qx, qy, qz = q
        p, q_rate, r = w
        
        dq = 0.5 * np.array([
            -qx*p - qy*q_rate - qz*r,
             qw*p + qy*r - qz*q_rate,
             qw*q_rate - qx*r + qz*p,
             qw*r + qx*q_rate - qy*p
        ])
        return dq

    def dynamics(self, state, motor_speeds):
        # Unpack state
        pos = state[0:3]
        vel = state[3:6]
        q = state[6:10]
        w = state[10:13]
        
        # Normalize quaternion
        q_norm = np.linalg.norm(q)
        if q_norm > 1e-6:
            q = q / q_norm
            
        R = self.get_rotation_matrix(q)
        
        # Calculate motor thrusts (X-quad layout)
        # Motor 1 (FR): CW/CCW depending on config. Let's follow:
        # Motor 1: Front Right (CCW)
        # Motor 2: Rear Left (CCW)
        # Motor 3: Front Left (CW)
        # Motor 4: Rear Right (CW)
        F = self.k_f * (motor_speeds ** 2)
        total_thrust = np.sum(F)
        
        # Torques in body frame
        # Roll: FR and RR push right up -> negative roll (roll right). Let's be consistent:
        # Let's define:
        # FR (1) and RR (4) are on y < 0, so pushing them up gives roll to the left (positive roll)
        # FL (3) and RL (2) are on y > 0, so pushing them up gives roll to the right (negative roll)
        tau_x = self.l * (F[0] - F[1] - F[2] + F[3])
        # Pitch: FL and FR are on x > 0, so pushing them up gives pitch down (negative pitch)
        # RL and RR are on x < 0, so pushing them up gives pitch up (positive pitch)
        tau_y = self.l * (-F[0] + F[1] - F[2] + F[3])
        # Yaw: CCW rotors (1, 2) produce CW reaction torque (positive yaw)
        # CW rotors (3, 4) produce CCW reaction torque (negative yaw)
        tau_z = self.k_m * (motor_speeds[0]**2 + motor_speeds[1]**2 - motor_speeds[2]**2 - motor_speeds[3]**2)
        
        # Translational dynamics
        g_world = np.array([0.0, 0.0, -self.g])
        thrust_body = np.array([0.0, 0.0, total_thrust])
        thrust_world = R @ thrust_body
        
        # Drag force in world frame
        drag_force = -np.array([
            self.C_drag_xy * vel[0],
            self.C_drag_xy * vel[1],
            self.C_drag_z * vel[2]
        ])
        
        accel_world = (thrust_world + drag_force + self.dist_force_world) / self.m + g_world
        
        # Store specific force (what IMU measures)
        # Specific force in body frame: R^T * (accel_world - g_world)
        self.linear_accel_body = R.T @ (accel_world - g_world)
        
        # Rotational dynamics
        moments_body = np.array([tau_x, tau_y, tau_z]) + self.dist_torque_body - self.C_rot * w
        # Rigid body angular acceleration: w_dot = I_inv * (moments - w x (I * w))
        w_dot = self.I_inv @ (moments_body - np.cross(w, self.I @ w))
        
        # Quaternion derivative
        dq = self.quaternion_derivative(q, w)
        
        # Return state derivatives
        dst = np.zeros(13)
        dst[0:3] = vel
        dst[3:6] = accel_world
        dst[6:10] = dq
        dst[10:13] = w_dot
        return dst

    def physics_step(self):
        # Runge-Kutta 4th Order (RK4) integration
        s = self.state
        u = self.motor_speeds
        
        k1 = self.dynamics(s, u)
        k2 = self.dynamics(s + 0.5 * self.dt * k1, u)
        k3 = self.dynamics(s + 0.5 * self.dt * k2, u)
        k4 = self.dynamics(s + self.dt * k3, u)
        
        self.state = s + (self.dt / 6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)
        
        # Normalize quaternion to prevent drift
        q = self.state[6:10]
        q_norm = np.linalg.norm(q)
        if q_norm > 1e-6:
            self.state[6:10] = q / q_norm
            
        # Ground collision modeling
        pos = self.state[0:3]
        vel = self.state[3:6]
        if pos[2] <= 0.0:
            # Clamp height to ground level
            self.state[2] = 0.0
            
            # If falling onto the ground, stop vertical velocity
            if vel[2] < 0.0:
                self.state[5] = 0.0
            
            # Ground friction/damping when resting on the ground
            # If thrust is not enough to lift off, damp horizontal speeds and angles
            total_thrust = np.sum(self.k_f * (self.motor_speeds**2))
            if total_thrust < (self.m * self.g - 0.1):
                self.state[3:5] = 0.0  # vx, vy = 0
                # Restore orientation to level ground
                self.state[6:10] = np.array([1.0, 0.0, 0.0, 0.0]) # level roll/pitch/yaw
                self.state[10:13] = 0.0  # angular rates = 0
                
        # Publish messages
        self.publish_topics()

    def publish_topics(self):
        now = self.get_clock().now().to_msg()
        
        # Unpack state
        pos = self.state[0:3]
        vel = self.state[3:6]
        q = self.state[6:10]
        w = self.state[10:13]
        
        # 1. Publish Odometry
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        
        odom.pose.pose.position.x = pos[0]
        odom.pose.pose.position.y = pos[1]
        odom.pose.pose.position.z = pos[2]
        
        odom.pose.pose.orientation.w = q[0]
        odom.pose.pose.orientation.x = q[1]
        odom.pose.pose.orientation.y = q[2]
        odom.pose.pose.orientation.z = q[3]
        
        # Rotate velocity to body frame for twist
        R = self.get_rotation_matrix(q)
        vel_body = R.T @ vel
        odom.twist.twist.linear.x = vel_body[0]
        odom.twist.twist.linear.y = vel_body[1]
        odom.twist.twist.linear.z = vel_body[2]
        
        odom.twist.twist.angular.x = w[0]
        odom.twist.twist.angular.y = w[1]
        odom.twist.twist.angular.z = w[2]
        
        self.odom_pub.publish(odom)
        
        # 2. Publish IMU
        imu = Imu()
        imu.header.stamp = now
        imu.header.frame_id = 'base_link'
        
        # Add slight white noise to IMU readings
        gyro_noise = np.random.normal(0, 0.01, 3)
        accel_noise = np.random.normal(0, 0.1, 3)
        
        imu.angular_velocity.x = w[0] + gyro_noise[0]
        imu.angular_velocity.y = w[1] + gyro_noise[1]
        imu.angular_velocity.z = w[2] + gyro_noise[2]
        
        imu.linear_acceleration.x = self.linear_accel_body[0] + accel_noise[0]
        imu.linear_acceleration.y = self.linear_accel_body[1] + accel_noise[1]
        imu.linear_acceleration.z = self.linear_accel_body[2] + accel_noise[2]
        
        # Pass simulated orientation estimation (could represent internal filter)
        imu.orientation.w = q[0]
        imu.orientation.x = q[1]
        imu.orientation.y = q[2]
        imu.orientation.z = q[3]
        
        self.imu_pub.publish(imu)
        
        # 3. Publish TF transform
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        
        t.transform.translation.x = pos[0]
        t.transform.translation.y = pos[1]
        t.transform.translation.z = pos[2]
        t.transform.rotation.w = q[0]
        t.transform.rotation.x = q[1]
        t.transform.rotation.y = q[2]
        t.transform.rotation.z = q[3]
        
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = QuadcopterSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
