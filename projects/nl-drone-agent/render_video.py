"""
Offscreen Video & Telemetry Rendering Engine for Voyager NL-Drone-Agent.

Simulates and renders offscreen video flight_demo.mp4 and flight telemetry plot flight_demo_plot.png
showcasing full 6-DOF multi-axis takeoff, XY spatial navigation, hovering hold, and landing.
Supports both MujocoBackend and VoyagerSimBackend (via kinematic-sync rendering).
"""
import os
os.environ.setdefault("MUJOCO_GL", "egl")
import json
import argparse
import numpy as np
import imageio

from safety import validate_tool_call, MIN_ALTITUDE
from llm_client import LLMToolAgent
from controller import Hexacopter6DOFController, SimulationBackend, VoyagerSimBackend
from dialogue_control import MODEL_PATH, create_backend
from plot_telemetry import generate_flight_plot


def render_flight_demo(
    out_mp4: str = "flight_demo.mp4",
    out_json: str = "flight_log.json",
    out_plot: str = "flight_demo_plot.png",
    backend: "str | SimulationBackend | None" = None,
    no_video: bool = False,
) -> dict:
    if isinstance(backend, SimulationBackend):
        sim_backend = backend
    else:
        sim_backend = create_backend(backend)

    controller = Hexacopter6DOFController(backend=sim_backend)
    agent = LLMToolAgent(provider="mock")
    is_voyager = isinstance(sim_backend, VoyagerSimBackend)

    frames = []
    fps = 30
    dt = sim_backend.dt
    steps_per_frame = int(round(1.0 / fps / dt))

    # Initialize offscreen renderer if video is requested
    renderer = None
    cam = None
    vis_model = None
    vis_data = None

    if not no_video:
        import mujoco
        if is_voyager:
            vis_model = mujoco.MjModel.from_xml_path(MODEL_PATH)
            vis_data = mujoco.MjData(vis_model)
            renderer = mujoco.Renderer(vis_model, height=540, width=960)
        else:
            vis_model = sim_backend.m
            vis_data = sim_backend.d
            renderer = mujoco.Renderer(vis_model, height=540, width=960)

        cam = mujoco.MjvCamera()
        cam.lookat = [2.0, 1.5, 2.5]
        cam.distance = 9.0
        cam.azimuth = 135
        cam.elevation = -22

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
            controller.step(dt)
            t += dt

            # Same telemetry sample reused for both plot log and video frame
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

            if not no_video and (i % steps_per_frame == 0):
                if is_voyager:
                    # Kinematic forwarding into MuJoCo visual model
                    vis_data.qpos[0] = telemetry["x"]
                    vis_data.qpos[1] = telemetry["y"]
                    vis_data.qpos[2] = telemetry["z"]
                    s = sim_backend.engine.getState()
                    vis_data.qpos[3] = s.qw
                    vis_data.qpos[4] = s.qx
                    vis_data.qpos[5] = s.qy
                    vis_data.qpos[6] = s.qz
                    mujoco.mj_forward(vis_model, vis_data)
                    renderer.update_scene(vis_data, camera=cam)
                else:
                    renderer.update_scene(vis_data, camera=cam)

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
        telemetry = sim_backend.get_telemetry()
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
            curr = sim_backend.get_telemetry()
            controller.set_target_position(curr["x"], curr["y"], curr["z"])
            step_and_capture(3.0)
        elif tool_name == "land":
            curr = sim_backend.get_telemetry()
            controller.set_target_position(curr["x"], curr["y"], MIN_ALTITUDE)
            step_and_capture(6.0)

    # Save outputs
    out_dir = os.path.dirname(__file__)
    mp4_path = os.path.join(out_dir, out_mp4)
    json_path = os.path.join(out_dir, out_json)
    plot_path = os.path.join(out_dir, out_plot)

    if not no_video and len(frames) > 0:
        imageio.mimsave(mp4_path, frames, fps=fps)
        print(f"Saved offscreen flight video to {mp4_path} ({len(frames)} frames)")
    elif no_video:
        print("Skipped video rendering (--no-video selected).")

    with open(json_path, "w") as f:
        json.dump(log, f)
    print(f"Saved flight telemetry log to {json_path}")

    generate_flight_plot(log_path=json_path, out_path=plot_path)
    print(f"Saved flight plot to {plot_path}")

    return log


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voyager NL-Drone-Agent Video & Telemetry Renderer")
    parser.add_argument(
        "--backend",
        type=str,
        default=os.environ.get("VOYAGER_BACKEND", "mujoco"),
        choices=["mujoco", "voyager_sim", "voyager"],
        help="Simulation backend (default: mujoco or $VOYAGER_BACKEND)",
    )
    parser.add_argument("--no-video", "--plot-only", dest="no_video", action="store_true", help="Skip video frame rendering and only generate telemetry log and plot")
    parser.add_argument("--out-mp4", type=str, default="flight_demo.mp4", help="Output MP4 file name")
    parser.add_argument("--out-json", type=str, default="flight_log.json", help="Output telemetry JSON file name")
    parser.add_argument("--out-plot", type=str, default="flight_demo_plot.png", help="Output telemetry PNG plot name")

    args = parser.parse_args()
    render_flight_demo(
        out_mp4=args.out_mp4,
        out_json=args.out_json,
        out_plot=args.out_plot,
        backend=args.backend,
        no_video=args.no_video,
    )
