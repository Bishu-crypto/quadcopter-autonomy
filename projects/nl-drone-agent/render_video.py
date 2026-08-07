"""
Offscreen Off-Line MuJoCo Video & Telemetry Rendering Engine for Voyager NL-Drone-Agent.

Simulates and renders offscreen video flight_demo.mp4 and flight telemetry plot flight_demo_plot.png
showcasing full 6-DOF multi-axis takeoff, XY spatial navigation, hovering hold, and landing.
"""
import os
os.environ.setdefault("MUJOCO_GL", "egl")
import json
import mujoco
import numpy as np
import imageio

from safety import validate_tool_call, MIN_ALTITUDE
from llm_client import LLMToolAgent
from controller import Hexacopter6DOFController
from dialogue_control import MODEL_PATH, get_sensor_telemetry
from plot_telemetry import generate_flight_plot


def render_flight_demo(out_mp4="flight_demo.mp4", out_json="flight_log.json"):
    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data = mujoco.MjData(model)
    controller = Hexacopter6DOFController(model, data)
    agent = LLMToolAgent(provider="mock")

    renderer = mujoco.Renderer(model, height=540, width=960)
    cam = mujoco.MjvCamera()
    cam.lookat = [2.0, 1.5, 2.5]
    cam.distance = 9.0
    cam.azimuth = 135
    cam.elevation = -22

    frames = []
    fps = 30
    dt = model.opt.timestep
    steps_per_frame = int(round(1.0 / fps / dt))

    log = {
        "t": [], "x": [], "y": [], "z": [],
        "vx": [], "vy": [], "vz": [],
        "roll": [], "pitch": [], "yaw": []
    }
    t = 0.0
    transcript = []

    def step_and_capture(seconds: float):
        nonlocal t
        n_steps = int(seconds / dt)
        for i in range(n_steps):
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

            if i % steps_per_frame == 0:
                renderer.update_scene(data, camera=cam)
                frames.append(renderer.render().copy())

    commands = [
        "takeoff to 3m",
        "hold",
        "goto 4, 3, 5",
        "hold",
        "land"
    ]

    for cmd_text in commands:
        transcript.append(f"> {cmd_text}")
        telemetry = get_sensor_telemetry(data)
        tool_call = agent.generate_tool_call(cmd_text, telemetry_context=telemetry)
        tool_name = tool_call.get("tool", "unknown")
        kwargs = tool_call.get("kwargs", {})
        val_kwargs = validate_tool_call(tool_name, kwargs)

        if tool_name == "takeoff":
            controller.set_target_position(telemetry["x"], telemetry["y"], val_kwargs["altitude_m"])
            step_and_capture(5.0)
        elif tool_name == "goto":
            controller.set_target_position(val_kwargs["x"], val_kwargs["y"], val_kwargs["z"], val_kwargs["yaw_deg"])
            step_and_capture(6.0)
        elif tool_name == "hold":
            curr = get_sensor_telemetry(data)
            controller.set_target_position(curr["x"], curr["y"], curr["z"])
            step_and_capture(3.0)
        elif tool_name == "land":
            curr = get_sensor_telemetry(data)
            controller.set_target_position(curr["x"], curr["y"], MIN_ALTITUDE)
            step_and_capture(6.0)

    # Save outputs
    out_dir = os.path.dirname(__file__)
    mp4_path = os.path.join(out_dir, out_mp4)
    json_path = os.path.join(out_dir, out_json)

    imageio.mimsave(mp4_path, frames, fps=fps)
    print(f"Saved offscreen flight video to {mp4_path} ({len(frames)} frames)")

    with open(json_path, "w") as f:
        json.dump(log, f)
    
    generate_flight_plot(log_path=json_path, out_path=os.path.join(out_dir, "flight_demo_plot.png"))


if __name__ == "__main__":
    render_flight_demo()
