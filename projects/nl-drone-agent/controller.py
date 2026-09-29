"""
Full 6-DOF Cascaded Position, Attitude, and Differential Thrust Controller for Voyager Hexacopter.

Supports pluggable simulation backends:
  - MujocoBackend (MuJoCo physics simulation)
  - VoyagerSimBackend (C++ Voyager-Sim 6-DOF physics engine)
"""
import os
import sys
from abc import ABC, abstractmethod
import numpy as np

# Ensure voyager_sim_py can be loaded from local directory or build/
_build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../build"))
if _build_dir not in sys.path:
    sys.path.insert(0, _build_dir)
_local_dir = os.path.abspath(os.path.dirname(__file__))
if _local_dir not in sys.path:
    sys.path.insert(0, _local_dir)

try:
    import mujoco
    HAS_MUJOCO = True
except ImportError:
    mujoco = None
    HAS_MUJOCO = False

try:
    import voyager_sim_py
    HAS_VOYAGER_SIM = True
except ImportError:
    voyager_sim_py = None
    HAS_VOYAGER_SIM = False

TOW = 37.291          # kg
G = 9.81
N_ROTORS = 6
ARM_LENGTH = 1.12      # m
HOVER_THRUST_PER_ROTOR = (TOW * G) / N_ROTORS  # ~60.97 N
MAX_THRUST_PER_ROTOR = HOVER_THRUST_PER_ROTOR * 2.2 # ~134.14 N
DEFAULT_INITIAL_POS = (0.0, 0.0, 2.0)  # Starting vehicle position [x, y, z] matching hexacopter.xml (qpos0)
DEFAULT_INITIAL_YAW = 0.0


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


# ==============================================================================
# Simulation Backend Abstraction
# ==============================================================================

class SimulationBackend(ABC):
    """Abstract interface defining the flight physics simulator backend."""

    @property
    @abstractmethod
    def dt(self) -> float:
        """Simulation timestep in seconds."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the simulator state to origin/default."""
        ...

    @abstractmethod
    def reset_to(self, x: float, y: float, z: float, yaw_deg: float = 0.0) -> None:
        """Reset vehicle state to a given 3D position and yaw."""
        ...

    @abstractmethod
    def step(self, total_thrust: float, tau_x: float, tau_y: float, tau_z: float, dt: float | None = None) -> None:
        """Advance the physics simulation using the given thrust and body moments."""
        ...

    @abstractmethod
    def get_telemetry(self) -> dict:
        """
        Return noise-free vehicle telemetry dict:
        {
            "x": float, "y": float, "z": float,
            "vx": float, "vy": float, "vz": float,
            "roll_deg": float, "pitch_deg": float, "yaw_deg": float,
            "angvel_x": float, "angvel_y": float, "angvel_z": float,
        }
        """
        ...


class MujocoBackend(SimulationBackend):
    """
    Simulation backend wrapping MuJoCo physics (hexacopter.xml).
    Preserves exact MuJoCo state extraction and stepping behavior.
    """
    def __init__(self, model: "mujoco.MjModel | None" = None, data: "mujoco.MjData | None" = None, model_path: str | None = None):
        if not HAS_MUJOCO:
            raise RuntimeError("mujoco Python package is not available.")
        if model is not None and data is not None:
            self.m = model
            self.d = data
        elif model_path is not None:
            self.m = mujoco.MjModel.from_xml_path(model_path)
            self.d = mujoco.MjData(self.m)
        else:
            default_path = os.path.join(os.path.dirname(__file__), "hexacopter.xml")
            self.m = mujoco.MjModel.from_xml_path(default_path)
            self.d = mujoco.MjData(self.m)

        # Precompute rotor positions (6 rotors at 60 deg increments)
        self.rotor_pos = []
        for i in range(N_ROTORS):
            angle = np.radians(i * 60.0)
            rx = ARM_LENGTH * np.cos(angle)
            ry = ARM_LENGTH * np.sin(angle)
            self.rotor_pos.append((rx, ry))

    @property
    def dt(self) -> float:
        return float(self.m.opt.timestep)

    def reset(self) -> None:
        mujoco.mj_resetData(self.m, self.d)
        mujoco.mj_forward(self.m, self.d)

    def reset_to(self, x: float, y: float, z: float, yaw_deg: float = 0.0) -> None:
        mujoco.mj_resetData(self.m, self.d)
        self.d.qpos[0] = float(x)
        self.d.qpos[1] = float(y)
        self.d.qpos[2] = float(z)
        yaw_rad = np.radians(yaw_deg)
        self.d.qpos[3] = np.cos(yaw_rad / 2.0)
        self.d.qpos[4] = 0.0
        self.d.qpos[5] = 0.0
        self.d.qpos[6] = np.sin(yaw_rad / 2.0)
        mujoco.mj_forward(self.m, self.d)

    def step(self, total_thrust: float, tau_x: float, tau_y: float, tau_z: float, dt: float | None = None) -> None:
        # Differential thrust mapping to 6 rotors
        thrusts = np.zeros(N_ROTORS)
        base_rotor_thrust = total_thrust / N_ROTORS
        for i in range(N_ROTORS):
            rx, ry = self.rotor_pos[i]
            spin = 1.0 if i % 2 == 0 else -1.0
            dT_pitch = - tau_y * (rx / ARM_LENGTH) * 15.0
            dT_roll = tau_x * (ry / ARM_LENGTH) * 15.0
            dT_yaw = spin * tau_z * 5.0
            t_i = base_rotor_thrust + dT_pitch + dT_roll + dT_yaw
            thrusts[i] = np.clip(t_i, 0.0, MAX_THRUST_PER_ROTOR)

        self.d.ctrl[:] = thrusts
        mujoco.mj_step(self.m, self.d)

    def get_telemetry(self) -> dict:
        pos = self.d.qpos[0:3]
        quat = self.d.qpos[3:7]
        vel = self.d.qvel[0:3]
        angvel = self.d.qvel[3:6]
        roll, pitch, yaw = quat2euler(quat)
        return {
            "x": float(pos[0]),
            "y": float(pos[1]),
            "z": float(pos[2]),
            "vx": float(vel[0]),
            "vy": float(vel[1]),
            "vz": float(vel[2]),
            "roll_deg": float(np.degrees(roll)),
            "pitch_deg": float(np.degrees(pitch)),
            "yaw_deg": float(np.degrees(yaw)),
            "angvel_x": float(angvel[0]),
            "angvel_y": float(angvel[1]),
            "angvel_z": float(angvel[2]),
        }


# Note on PID Gains from prototype controller_node.py (1.5kg quadcopter baseline):
# For reference only:
#   Position PID: kp_xy = 1.5, ki_xy = 0.05, kd_xy = 1.2
#   Altitude PID: kp_z  = 3.0, ki_z  = 0.15, kd_z  = 2.2
#   Attitude P:   kp_att_rp = 6.5, kp_att_y = 4.0
#   Rate PID:     kp_rate = 0.15, ki_rate = 0.08, kd_rate = 0.015


class VoyagerSimBackend(SimulationBackend):
    """
    Simulation backend wrapping the headless C++ Voyager-Sim 6-DOF physics engine.
    Constructed with the 37.291kg hexacopter parameters from DESIGN_LOCK.md.
    Telemetry is extracted directly and noise-free from raw voyager::sim::State.
    """
    def __init__(
        self,
        mass: float = TOW,         # 37.291 kg (DESIGN_LOCK.md)
        Ixx: float = 5.8965,       # kg*m^2
        Iyy: float = 5.8815,       # kg*m^2
        Izz: float = 11.1390,      # kg*m^2
        dt: float = 0.002,         # 500 Hz integration step
        initial_pos: tuple[float, float, float] = DEFAULT_INITIAL_POS,
        initial_yaw_deg: float = DEFAULT_INITIAL_YAW,
    ):
        if not HAS_VOYAGER_SIM:
            raise RuntimeError("voyager_sim_py module could not be imported.")
        self.mass = mass
        self.Ixx = Ixx
        self.Iyy = Iyy
        self.Izz = Izz
        self._dt = dt
        self._initial_pos = initial_pos
        self._initial_yaw_deg = initial_yaw_deg

        self.engine = voyager_sim_py.VoyagerSimEngine(mass, Ixx, Iyy, Izz)

        # Precompute rotor positions (6 rotors at 60 deg increments)
        self.rotor_pos = []
        for i in range(N_ROTORS):
            angle = np.radians(i * 60.0)
            rx = ARM_LENGTH * np.cos(angle)
            ry = ARM_LENGTH * np.sin(angle)
            self.rotor_pos.append((rx, ry))

        # Initialize to starting pose matching hexacopter.xml default (2.0m altitude)
        self.reset()

    @property
    def dt(self) -> float:
        return self._dt

    def reset(self) -> None:
        self.reset_to(self._initial_pos[0], self._initial_pos[1], self._initial_pos[2], self._initial_yaw_deg)

    def reset_to(self, x: float, y: float, z: float, yaw_deg: float = 0.0) -> None:
        yaw_rad = np.radians(yaw_deg)
        qw = float(np.cos(yaw_rad / 2.0))
        qz = float(np.sin(yaw_rad / 2.0))
        self.engine.reset_to(float(x), float(y), float(z), qw, 0.0, 0.0, qz)

    def step(self, total_thrust: float, tau_x: float, tau_y: float, tau_z: float, dt: float | None = None) -> None:
        step_dt = dt if dt is not None else self._dt
        # Differential thrust mapping across 6 rotors (matching hexacopter.xml actuator geometry)
        base_rotor_thrust = total_thrust / N_ROTORS
        net_thrust = 0.0
        phys_tau_x = 0.0
        phys_tau_y = 0.0
        phys_tau_z = 0.0
        for i in range(N_ROTORS):
            rx, ry = self.rotor_pos[i]
            spin = 1.0 if i % 2 == 0 else -1.0
            dT_pitch = - tau_y * (rx / ARM_LENGTH) * 15.0
            dT_roll = tau_x * (ry / ARM_LENGTH) * 15.0
            dT_yaw = spin * tau_z * 5.0
            t_i = np.clip(base_rotor_thrust + dT_pitch + dT_roll + dT_yaw, 0.0, MAX_THRUST_PER_ROTOR)
            net_thrust += t_i
            phys_tau_x += ry * t_i
            phys_tau_y += -rx * t_i
            phys_tau_z += spin * 0.02 * t_i

        inputs = voyager_sim_py.Inputs(float(net_thrust), float(phys_tau_x), float(phys_tau_y), float(phys_tau_z))
        self.engine.step(inputs, step_dt)

    def get_telemetry(self) -> dict:
        # Read directly from raw voyager::sim::State (strictly noise-free)
        s = self.engine.getState()
        roll, pitch, yaw = quat2euler([s.qw, s.qx, s.qy, s.qz])
        return {
            "x": float(s.x),
            "y": float(s.y),
            "z": float(s.z),
            "vx": float(s.vx),
            "vy": float(s.vy),
            "vz": float(s.vz),
            "roll_deg": float(np.degrees(roll)),
            "pitch_deg": float(np.degrees(pitch)),
            "yaw_deg": float(np.degrees(yaw)),
            "angvel_x": float(s.p),
            "angvel_y": float(s.q),
            "angvel_z": float(s.r),
        }


# ==============================================================================
# Cascaded 6-DOF Controller
# ==============================================================================

class Hexacopter6DOFController:
    """
    Cascaded 6-DOF controller for the 37.291kg Voyager Hexacopter.
    - Outer Loop: Position & Velocity (calculates target vertical acceleration & desired tilt angles)
    - Inner Loop: Attitude (Roll, Pitch, Yaw angle & rate control)
    - Backend-Agnostic: Dispatches control to either MujocoBackend or VoyagerSimBackend.
    """
    def __init__(
        self,
        model_or_backend: "SimulationBackend | mujoco.MjModel | None" = None,
        data: "mujoco.MjData | None" = None,
        backend: "SimulationBackend | None" = None,
    ):
        if backend is not None:
            self.backend = backend
        elif isinstance(model_or_backend, SimulationBackend):
            self.backend = model_or_backend
        elif model_or_backend is not None and data is not None:
            self.backend = MujocoBackend(model=model_or_backend, data=data)
        elif model_or_backend is not None and hasattr(model_or_backend, "opt"):
            self.backend = MujocoBackend(model=model_or_backend, data=data)
        else:
            self.backend = MujocoBackend()

        # For backwards compatibility with callers accessing controller.m and controller.d
        if isinstance(self.backend, MujocoBackend):
            self.m = self.backend.m
            self.d = self.backend.d
        else:
            self.m = None
            self.d = None

        # Target state [x, y, z, yaw_rad]
        self.target_pos = np.array(DEFAULT_INITIAL_POS, dtype=float)
        self.target_yaw = np.radians(DEFAULT_INITIAL_YAW)
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

    def compute_control_inputs(self) -> tuple[float, float, float, float]:
        """
        Compute vehicle-level control commands: (total_thrust, tau_x, tau_y, tau_z).
        Reads telemetry from self.backend.get_telemetry().
        """
        telem = self.backend.get_telemetry()
        pos = np.array([telem["x"], telem["y"], telem["z"]])
        vel = np.array([telem["vx"], telem["vy"], telem["vz"]])
        roll = np.radians(telem["roll_deg"])
        pitch = np.radians(telem["pitch_deg"])
        yaw = np.radians(telem["yaw_deg"])
        angvel = np.array([telem["angvel_x"], telem["angvel_y"], telem["angvel_z"]])

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

        # Desired moments (tau_x, tau_y, tau_z)
        u_roll = self.kp_roll * err_roll - self.kd_roll * angvel[0]
        u_pitch = self.kp_pitch * err_pitch - self.kd_pitch * angvel[1]
        u_yaw = self.kp_yaw * err_yaw - self.kd_yaw * angvel[2]

        return total_thrust_cmd, u_roll, u_pitch, u_yaw

    def compute_rotor_thrusts(self) -> np.ndarray:
        """
        Maintains backward compatibility with callers expecting an array of 6 rotor thrusts.
        """
        total_thrust_cmd, u_roll, u_pitch, u_yaw = self.compute_control_inputs()
        base_rotor_thrust = total_thrust_cmd / N_ROTORS

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

    def step(self, dt: float | None = None) -> None:
        """
        Compute control inputs and advance the simulation backend by dt.
        """
        total_thrust, tau_x, tau_y, tau_z = self.compute_control_inputs()
        self.backend.step(total_thrust, tau_x, tau_y, tau_z, dt=dt)
