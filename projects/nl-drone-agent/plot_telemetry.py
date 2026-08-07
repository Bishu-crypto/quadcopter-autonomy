"""
Generates flight_demo_plot.png containing multi-axis 3D position trajectories,
linear velocities, and pitch/roll attitude dynamics for the Voyager hexacopter flight.
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np

LOG_PATH = os.path.join(os.path.dirname(__file__), "flight_log.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "flight_demo_plot.png")


def generate_flight_plot(log_path=LOG_PATH, out_path=OUT_PATH):
    if not os.path.exists(log_path):
        print(f"Log file {log_path} not found.")
        return

    with open(log_path, "r") as f:
        log = json.load(f)

    t = np.array(log["t"])
    x, y, z = np.array(log["x"]), np.array(log["y"]), np.array(log["z"])
    vx, vy, vz = np.array(log["vx"]), np.array(log["vy"]), np.array(log["vz"])
    roll, pitch, yaw = np.array(log["roll"]), np.array(log["pitch"]), np.array(log["yaw"])

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("Voyager NL-Drone-Agent 6-DOF Flight Telemetry", fontsize=14, fontweight="bold")

    # Subplot 1: 3D Position Trajectory (X, Y, Z)
    axes[0].plot(t, x, label="X Position (m)", color="#1f77b4", linewidth=2)
    axes[0].plot(t, y, label="Y Position (m)", color="#ff7f0e", linewidth=2)
    axes[0].plot(t, z, label="Z Altitude (m)", color="#2ca02c", linewidth=2)
    axes[0].set_ylabel("Position [m]")
    axes[0].grid(True, linestyle="--", alpha=0.6)
    axes[0].legend(loc="upper right")
    axes[0].set_title("3D Waypoint Tracking Dynamics")

    # Subplot 2: Linear Velocities (Vx, Vy, Vz)
    axes[1].plot(t, vx, label="Vx (m/s)", color="#1f77b4", linestyle="--")
    axes[1].plot(t, vy, label="Vy (m/s)", color="#ff7f0e", linestyle="--")
    axes[1].plot(t, vz, label="Vz (m/s)", color="#2ca02c", linestyle="--")
    axes[1].set_ylabel("Velocity [m/s]")
    axes[1].grid(True, linestyle="--", alpha=0.6)
    axes[1].legend(loc="upper right")
    axes[1].set_title("Linear Velocity Profile")

    # Subplot 3: Attitude Dynamics (Roll, Pitch Tilt Angles)
    axes[2].plot(t, pitch, label="Pitch Angle (°)", color="#d62728", linewidth=1.8)
    axes[2].plot(t, roll, label="Roll Angle (°)", color="#9467bd", linewidth=1.8)
    axes[2].plot(t, yaw, label="Yaw Angle (°)", color="#8c564b", linestyle=":", linewidth=1.5)
    axes[2].set_ylabel("Attitude [deg]")
    axes[2].set_xlabel("Time [seconds]")
    axes[2].grid(True, linestyle="--", alpha=0.6)
    axes[2].legend(loc="upper right")
    axes[2].set_title("Body Tilt Dynamics (Attitude Control)")

    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved flight telemetry plot to {out_path}")


if __name__ == "__main__":
    generate_flight_plot()
