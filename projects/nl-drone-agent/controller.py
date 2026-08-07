"""
Full 6-DOF Cascaded Position, Attitude, and Differential Thrust Controller for Voyager Hexacopter.

Closes the loop on horizontal (XY) position, altitude (Z), and attitude (pitch, roll, yaw)
via differential rotor thrust allocation across all 6 hexacopter rotors.
"""
import numpy as np
import mujoco

TOW = 37.291          # kg
G = 9.81
N_ROTORS = 6
ARM_LENGTH = 1.12      # m
HOVER_THRUST_PER_ROTOR = (TOW * G) / N_ROTORS  # ~60.97 N
MAX_THRUST_PER_ROTOR = HOVER_THRUST_PER_ROTOR * 2.2 # ~134.14 N


def quat2euler(q):
    """Convert quaternion [qw, qx, qy, qz] to Euler angles [roll, pitch, yaw] in radians."""
    w, x, y, z = q
    # Roll (x-axis rotation)
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2.0 * (w * y - z * x)
    sinp = np.clip(sinp, -1.0, 1.0)
    pitch = np.arcsin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)

    return np.array([roll, pitch, yaw])


class Hexacopter6DOFController:
    """
    Cascaded 6-DOF controller for the 37.291kg Voyager Hexacopter in MuJoCo.
    - Outer Loop: Position & Velocity (calculates target vertical acceleration & desired tilt angles)
    - Inner Loop: Attitude (Roll, Pitch, Yaw angle & rate control)
    - Mixer: Differential thrust mapping to 6 rotor sites at 60-degree increments.
    """
    def __init__(self, model: mujoco.MjModel, data: mujoco.MjData):
        self.m = model
        self.d = data

        # Target state [x, y, z, yaw_rad]
        self.target_pos = np.array([0.0, 0.0, 2.0])
        self.target_yaw = 0.0
        self.velocity_mode = False
        self.target_vel = np.array([0.0, 0.0, 0.0])

        # Outer Loop Position Gains (XY & Z)
        self.kp_z, self.kd_z = 35.0, 22.0
        self.kp_xy, self.kd_xy = 1.8, 2.5
        self.max_tilt_rad = np.radians(18.0) # ~0.314 rad

        # Inner Loop Attitude Gains (Roll, Pitch, Yaw)
        self.kp_roll, self.kd_roll = 12.0, 3.5
        self.kp_pitch, self.kd_pitch = 12.0, 3.5
        self.kp_yaw, self.kd_yaw = 8.0, 2.5

        # Precompute rotor positions (6 rotors at 60 deg increments)
        self.rotor_pos = []
        for i in range(N_ROTORS):
            angle = np.radians(i * 60.0)
            rx = ARM_LENGTH * np.cos(angle)
            ry = ARM_LENGTH * np.sin(angle)
            self.rotor_pos.append((rx, ry))

    def set_target_position(self, x: float, y: float, z: float, yaw_deg: float = 0.0):
        self.target_pos = np.array([float(x), float(y), float(z)])
        self.target_yaw = np.radians(float(yaw_deg))
        self.velocity_mode = False

    def set_target_velocity(self, vx: float, vy: float, vz: float):
        self.target_vel = np.array([float(vx), float(vy), float(vz)])
        self.velocity_mode = True

    def compute_rotor_thrusts(self) -> np.ndarray:
        # Read sensor data / state from MuJoCo
        pos = self.d.qpos[0:3]
        quat = self.d.qpos[3:7]
        vel = self.d.qvel[0:3]
        angvel = self.d.qvel[3:6]
        roll, pitch, yaw = quat2euler(quat)

        # 1. Outer Loop (Z Altitude Control)
        if self.velocity_mode:
            err_z_vel = self.target_vel[2] - vel[2]
            acc_z_cmd = 8.0 * err_z_vel
        else:
            err_z_pos = self.target_pos[2] - pos[2]
            err_z_vel = -vel[2]
            acc_z_cmd = self.kp_z * err_z_pos + self.kd_z * err_z_vel

        # Total vertical thrust accounting for tilt compensation
        tilt_comp = np.cos(roll) * np.cos(pitch)
        tilt_comp = max(0.7, tilt_comp) # avoid division by zero or extreme tilt
        total_thrust_cmd = TOW * (G + acc_z_cmd) / tilt_comp
        total_thrust_cmd = np.clip(total_thrust_cmd, 0.0, MAX_THRUST_PER_ROTOR * N_ROTORS * 0.95)
        base_rotor_thrust = total_thrust_cmd / N_ROTORS

        # 2. Outer Loop (XY Position & Horizontal Acceleration Control)
        if self.velocity_mode:
            a_x_world = 3.0 * (self.target_vel[0] - vel[0])
            a_y_world = 3.0 * (self.target_vel[1] - vel[1])
        else:
            err_x_pos = self.target_pos[0] - pos[0]
            err_y_pos = self.target_pos[1] - pos[1]
            a_x_world = self.kp_xy * err_x_pos - self.kd_xy * vel[0]
            a_y_world = self.kp_xy * err_y_pos - self.kd_xy * vel[1]

        # Rotate world acceleration command to body frame
        a_x_body = a_x_world * np.cos(yaw) + a_y_world * np.sin(yaw)
        a_y_body = -a_x_world * np.sin(yaw) + a_y_world * np.cos(yaw)

        # Desired pitch & roll angles (small angle approximation: a_x / g ~ pitch)
        pitch_target = np.clip(a_x_body / G, -self.max_tilt_rad, self.max_tilt_rad)
        roll_target = np.clip(-a_y_body / G, -self.max_tilt_rad, self.max_tilt_rad)

        # 3. Inner Loop (Attitude & Rate Control)
        err_roll = roll_target - roll
        err_pitch = pitch_target - pitch
        err_yaw = (self.target_yaw - yaw + np.pi) % (2 * np.pi) - np.pi

        # Desired moments
        u_roll = self.kp_roll * err_roll - self.kd_roll * angvel[0]
        u_pitch = self.kp_pitch * err_pitch - self.kd_pitch * angvel[1]
        u_yaw = self.kp_yaw * err_yaw - self.kd_yaw * angvel[2]

        # 4. Mixer: Map commands to 6 rotors
        thrusts = np.zeros(N_ROTORS)
        for i in range(N_ROTORS):
            rx, ry = self.rotor_pos[i]
            spin = 1.0 if i % 2 == 0 else -1.0
            
            # Differential thrust contributions
            dT_pitch = - u_pitch * (rx / ARM_LENGTH) * 15.0
            dT_roll = u_roll * (ry / ARM_LENGTH) * 15.0
            dT_yaw = spin * u_yaw * 5.0
            
            t_i = base_rotor_thrust + dT_pitch + dT_roll + dT_yaw
            thrusts[i] = np.clip(t_i, 0.0, MAX_THRUST_PER_ROTOR)

        return thrusts
