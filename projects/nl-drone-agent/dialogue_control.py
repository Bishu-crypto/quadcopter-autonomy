"""
Voyager NL-Drone-Agent — Dialogue Control & Safety-Validated Execution Pipeline

Integrates:
  1. Natural Language Input (via swappable LLM tool caller in llm_client.py)
  2. Deterministic Safety Validation (in safety.py — rejects unsafe commands with explanation)
  3. Cascaded 6-DOF Hexacopter Control (in controller.py — handles Z altitude + XY horizontal tracking)
  4. Swappable Physics Simulation Backend (MujocoBackend or VoyagerSimBackend)
"""
import os
import sys
import json
import argparse
import numpy as np

from safety import validate_tool_call, SafetyViolation, MIN_ALTITUDE
from llm_client import LLMToolAgent
from controller import (
    Hexacopter6DOFController,
    SimulationBackend,
    MujocoBackend,
    VoyagerSimBackend,
    quat2euler,
    TOW,
    G,
    N_ROTORS
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "hexacopter.xml")


def create_backend(backend_name: str | None = None) -> SimulationBackend:
    """Factory creating the requested SimulationBackend (default: MujocoBackend)."""
    name = (backend_name or os.environ.get("VOYAGER_BACKEND", "mujoco")).lower()
    if name in ("voyager", "voyager_sim", "voyager-sim"):
        return VoyagerSimBackend()
    return MujocoBackend(model_path=MODEL_PATH)


def get_sensor_telemetry(sim_source) -> dict:
    """Extract telemetry dictionary from SimulationBackend or legacy MjData."""
    if hasattr(sim_source, "get_telemetry"):
        return sim_source.get_telemetry()
    pos = sim_source.qpos[0:3].copy()
    quat = sim_source.qpos[3:7].copy()
    vel = sim_source.qvel[0:3].copy()
    angvel = sim_source.qvel[3:6].copy()
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


def run_demo(
    commands: list[str],
    llm_provider: str = "mock",
    backend: "str | SimulationBackend | None" = None
) -> tuple[dict, list[str]]:
    """
    Executes a sequence of natural language typed commands through:
    LLM -> Safety Layer -> 6-DOF Controller -> Simulation Backend -> Telemetry Transcript & Log
    """
    if isinstance(backend, SimulationBackend):
        sim_backend = backend
    else:
        sim_backend = create_backend(backend)

    controller = Hexacopter6DOFController(backend=sim_backend)
    agent = LLMToolAgent(provider=llm_provider)

    log = {
        "t": [], "x": [], "y": [], "z": [],
        "vx": [], "vy": [], "vz": [],
        "roll": [], "pitch": [], "yaw": []
    }
    t = 0.0
    dt = sim_backend.dt
    transcript = []

    def step_for(seconds: float):
        nonlocal t
        n_steps = int(seconds / dt)
        for _ in range(n_steps):
            controller.step(dt)
            t += dt
            
            telemetry = sim_backend.get_telemetry()
            log["t"].append(t)
            log["x"].append(telemetry["x"])
            log["y"].append(telemetry["y"])
            log["z"].append(telemetry["z"])
            log["vx"].append(telemetry["vx"])
            log["vy"].append(telemetry["vy"])
            log["vz"].append(telemetry["vz"])
            log["roll"].append(telemetry["roll_deg"])
            log["pitch"].append(telemetry["pitch_deg"])
            log["yaw"].append(telemetry["yaw_deg"])

    for cmd_text in commands:
        transcript.append(f"> {cmd_text}")
        telemetry = sim_backend.get_telemetry()

        # 1. LLM Tool-Calling Layer
        tool_call = agent.generate_tool_call(cmd_text, telemetry_context=telemetry)
        tool_name = tool_call.get("tool", "unknown")
        kwargs = tool_call.get("kwargs", {})

        # 2. Safety Validation Layer & Dispatch
        try:
            val_kwargs = validate_tool_call(tool_name, kwargs)

            if tool_name == "takeoff":
                alt = val_kwargs["altitude_m"]
                controller.set_target_position(telemetry["x"], telemetry["y"], alt)
                step_for(5.0)
                curr = sim_backend.get_telemetry()
                transcript.append(
                    f"[agent] Taking off to {alt:.1f} m. "
                    f"Current status: pos=({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."
                )

            elif tool_name == "goto":
                x, y, z, yaw = val_kwargs["x"], val_kwargs["y"], val_kwargs["z"], val_kwargs["yaw_deg"]
                controller.set_target_position(x, y, z, yaw)
                step_for(6.0)
                curr = sim_backend.get_telemetry()
                transcript.append(
                    f"[agent] Waypoint reached. Target=({x:.1f}, {y:.1f}, {z:.1f}) m | "
                    f"Current=({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."
                )

            elif tool_name == "set_velocity":
                vx, vy, vz = val_kwargs["vx"], val_kwargs["vy"], val_kwargs["vz"]
                controller.set_target_velocity(vx, vy, vz)
                step_for(4.0)
                curr = sim_backend.get_telemetry()
                transcript.append(
                    f"[agent] Velocity set to ({vx:.1f}, {vy:.1f}, {vz:.1f}) m/s. "
                    f"Current speed: ({curr['vx']:.2f}, {curr['vy']:.2f}, {curr['vz']:.2f}) m/s."
                )

            elif tool_name == "hold":
                curr = sim_backend.get_telemetry()
                controller.set_target_position(curr["x"], curr["y"], curr["z"])
                step_for(3.0)
                curr = sim_backend.get_telemetry()
                transcript.append(
                    f"[agent] Holding position at ({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."
                )

            elif tool_name == "land":
                curr = sim_backend.get_telemetry()
                controller.set_target_position(curr["x"], curr["y"], MIN_ALTITUDE)
                step_for(6.0)
                curr = sim_backend.get_telemetry()
                transcript.append(
                    f"[agent] Landing sequence complete. Final altitude {curr['z']:.2f} m."
                )

            elif tool_name == "get_status":
                curr = sim_backend.get_telemetry()
                transcript.append(
                    f"[agent] Status: pos=({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m | "
                    f"vel=({curr['vx']:.2f}, {curr['vy']:.2f}, {curr['vz']:.2f}) m/s | "
                    f"attitude=(roll {curr['roll_deg']:.1f}°, pitch {curr['pitch_deg']:.1f}°, yaw {curr['yaw_deg']:.1f}°)"
                )

            else:
                transcript.append(f"[agent] Unrecognized command: '{cmd_text}'")

        except SafetyViolation as e:
            transcript.append(f"[agent] REJECTED — {e}")

    return log, transcript


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voyager NL-Drone-Agent Dialogue Control")
    parser.add_argument(
        "--backend",
        type=str,
        default=os.environ.get("VOYAGER_BACKEND", "mujoco"),
        choices=["mujoco", "voyager_sim", "voyager"],
        help="Simulation backend (default: mujoco or $VOYAGER_BACKEND)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="mock",
        help="LLM provider (default: mock)",
    )
    args = parser.parse_args()

    test_commands = [
        "takeoff to 3m",
        "hold",
        "status",
        "goto 4, 3, 5",
        "hold",
        "go up 2m higher",
        "takeoff to 100m",  # Deliberately unsafe -> rejected by safety layer
        "land",
        "status"
    ]
    log, transcript = run_demo(test_commands, llm_provider=args.provider, backend=args.backend)
    print("\n".join(transcript))

    out_dir = os.path.dirname(__file__)
    with open(os.path.join(out_dir, "flight_transcript.txt"), "w") as f:
        f.write("\n".join(transcript))
    with open(os.path.join(out_dir, "flight_log.json"), "w") as f:
        json.dump(log, f)
