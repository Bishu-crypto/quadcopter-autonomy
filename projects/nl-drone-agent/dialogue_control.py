"""
Voyager NL-Drone-Agent — Dialogue Control & Safety-Validated Execution Pipeline

Integrates:
  1. Natural Language Input (via swappable LLM tool caller in llm_client.py)
  2. Deterministic Safety Validation (in safety.py — rejects unsafe commands with explanation)
  3. Cascaded 6-DOF Hexacopter Control (in controller.py — handles Z altitude + XY horizontal tracking)
  4. MuJoCo Physics Engine Telemetry Loop
"""
import os
import json
import numpy as np
import mujoco

from safety import validate_tool_call, SafetyViolation, MIN_ALTITUDE
from llm_client import LLMToolAgent
from controller import Hexacopter6DOFController, quat2euler, TOW, G, N_ROTORS

MODEL_PATH = os.path.join(os.path.dirname(__file__), "hexacopter.xml")


def get_sensor_telemetry(data: mujoco.MjData) -> dict:
    """Extract real telemetry from MuJoCo frame sensors and freejoint qpos/qvel."""
    pos = data.qpos[0:3].copy()
    quat = data.qpos[3:7].copy()
    vel = data.qvel[0:3].copy()
    angvel = data.qvel[3:6].copy()
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


def run_demo(commands: list[str], llm_provider: str = "mock") -> tuple[dict, list[str]]:
    """
    Executes a sequence of natural language typed commands through:
    LLM -> Safety Layer -> 6-DOF Controller -> MuJoCo Sim -> Telemetry Transcript & Log
    """
    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data = mujoco.MjData(model)
    controller = Hexacopter6DOFController(model, data)
    agent = LLMToolAgent(provider=llm_provider)

    log = {
        "t": [], "x": [], "y": [], "z": [],
        "vx": [], "vy": [], "vz": [],
        "roll": [], "pitch": [], "yaw": []
    }
    t = 0.0
    dt = model.opt.timestep
    transcript = []

    def step_for(seconds: float):
        nonlocal t
        n_steps = int(seconds / dt)
        for _ in range(n_steps):
            thrusts = controller.compute_rotor_thrusts()
            data.ctrl[:] = thrusts
            mujoco.mj_step(model, data)
            t += dt
            
            telemetry = get_sensor_telemetry(data)
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
        telemetry = get_sensor_telemetry(data)

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
                curr = get_sensor_telemetry(data)
                transcript.append(
                    f"[agent] Taking off to {alt:.1f} m. "
                    f"Current status: pos=({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."
                )

            elif tool_name == "goto":
                x, y, z, yaw = val_kwargs["x"], val_kwargs["y"], val_kwargs["z"], val_kwargs["yaw_deg"]
                controller.set_target_position(x, y, z, yaw)
                step_for(6.0)
                curr = get_sensor_telemetry(data)
                transcript.append(
                    f"[agent] Waypoint reached. Target=({x:.1f}, {y:.1f}, {z:.1f}) m | "
                    f"Current=({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."
                )

            elif tool_name == "set_velocity":
                vx, vy, vz = val_kwargs["vx"], val_kwargs["vy"], val_kwargs["vz"]
                controller.set_target_velocity(vx, vy, vz)
                step_for(4.0)
                curr = get_sensor_telemetry(data)
                transcript.append(
                    f"[agent] Velocity set to ({vx:.1f}, {vy:.1f}, {vz:.1f}) m/s. "
                    f"Current speed: ({curr['vx']:.2f}, {curr['vy']:.2f}, {curr['vz']:.2f}) m/s."
                )

            elif tool_name == "hold":
                curr = get_sensor_telemetry(data)
                controller.set_target_position(curr["x"], curr["y"], curr["z"])
                step_for(3.0)
                curr = get_sensor_telemetry(data)
                transcript.append(
                    f"[agent] Holding position at ({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."
                )

            elif tool_name == "land":
                curr = get_sensor_telemetry(data)
                controller.set_target_position(curr["x"], curr["y"], MIN_ALTITUDE)
                step_for(6.0)
                curr = get_sensor_telemetry(data)
                transcript.append(
                    f"[agent] Landing sequence complete. Final altitude {curr['z']:.2f} m."
                )

            elif tool_name == "get_status":
                curr = get_sensor_telemetry(data)
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
    log, transcript = run_demo(test_commands)
    print("\n".join(transcript))

    out_dir = os.path.dirname(__file__)
    with open(os.path.join(out_dir, "flight_transcript.txt"), "w") as f:
        f.write("\n".join(transcript))
    with open(os.path.join(out_dir, "flight_log.json"), "w") as f:
        json.dump(log, f)
