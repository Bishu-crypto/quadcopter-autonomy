"""
Live 3D Graphical Viewer Demo for Voyager NL-Drone-Agent in MuJoCo.

Launches a real-time 3D MuJoCo graphical window showing the heavy-lift hexacopter
tilting, flying through 3D waypoints, hovering, and landing in real time.
"""
import time
import mujoco
import mujoco.viewer

from safety import validate_tool_call, SafetyViolation, MIN_ALTITUDE
from llm_client import LLMToolAgent
from controller import Hexacopter6DOFController
from dialogue_control import MODEL_PATH, get_sensor_telemetry


def run_gui_demo():
    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data = mujoco.MjData(model)
    controller = Hexacopter6DOFController(model, data)
    agent = LLMToolAgent(provider="mock")

    dt = model.opt.timestep

    mission = [
        "takeoff to 3m",
        "hold",
        "goto 4, 3, 5",
        "hold",
        "go up 2m higher",
        "takeoff to 100m", # Unsafe -> rejected
        "land"
    ]

    print("Launching MuJoCo 3D Graphical Viewer...")
    with mujoco.viewer.launch_passive(model, data) as viewer:
        viewer.cam.lookat = [2.0, 1.5, 2.5]
        viewer.cam.distance = 9.0
        viewer.cam.azimuth = 135
        viewer.cam.elevation = -22

        for cmd_text in mission:
            print(f"\n> {cmd_text}")
            telemetry = get_sensor_telemetry(data)
            tool_call = agent.generate_tool_call(cmd_text, telemetry_context=telemetry)
            tool_name = tool_call.get("tool", "unknown")
            kwargs = tool_call.get("kwargs", {})

            try:
                val_kwargs = validate_tool_call(tool_name, kwargs)

                if tool_name == "takeoff":
                    controller.set_target_position(telemetry["x"], telemetry["y"], val_kwargs["altitude_m"])
                    duration = 5.0
                elif tool_name == "goto":
                    controller.set_target_position(val_kwargs["x"], val_kwargs["y"], val_kwargs["z"], val_kwargs["yaw_deg"])
                    duration = 6.0
                elif tool_name == "hold":
                    curr = get_sensor_telemetry(data)
                    controller.set_target_position(curr["x"], curr["y"], curr["z"])
                    duration = 3.0
                elif tool_name == "land":
                    curr = get_sensor_telemetry(data)
                    controller.set_target_position(curr["x"], curr["y"], MIN_ALTITUDE)
                    duration = 6.0
                else:
                    duration = 1.0

                n_steps = int(duration / dt)
                for _ in range(n_steps):
                    step_start = time.time()
                    data.ctrl[:] = controller.compute_rotor_thrusts()
                    mujoco.mj_step(model, data)
                    viewer.sync()

                    # Real-time sync sleep
                    time_until_next = dt - (time.time() - step_start)
                    if time_until_next > 0:
                        time.sleep(time_until_next)

                curr = get_sensor_telemetry(data)
                print(f"[agent] Executed: pos=({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m.")

            except SafetyViolation as e:
                print(f"[agent] REJECTED — {e}")

    print("\n3D Graphical Simulation Finished.")


if __name__ == "__main__":
    run_gui_demo()
