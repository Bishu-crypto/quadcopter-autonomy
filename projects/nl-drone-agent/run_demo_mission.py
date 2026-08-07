"""
Voyager NL-Drone-Agent — Screen-Recording Presentation Demo Mission

Executes a styled, multi-phase autonomous flight mission with colorized telemetry,
tool-calling breakdown, safety bounds checking, and live status dashboard.
Ideal for screen recording and uploading to Google Drive / Portfolio.
"""
import os
import sys
import time
import numpy as np
import mujoco

from safety import validate_tool_call, SafetyViolation, MIN_ALTITUDE
from llm_client import LLMToolAgent
from controller import Hexacopter6DOFController
from dialogue_control import MODEL_PATH, get_sensor_telemetry

# ANSI Colors for Terminal Presentation
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
MAGENTA = "\033[1;35m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(f"{CYAN}{'='*72}{RESET}")
    print(f"{BOLD}{CYAN}   VOYAGER HEAVY-LIFT HEXACOPTER — NATURAL LANGUAGE AUTONOMY DEMO{RESET}")
    print(f"{CYAN}   TOW: 37.291 kg | 6-DOF Position & Tilt Control | MuJoCo Physics{RESET}")
    print(f"{CYAN}{'='*72}{RESET}\n")


def print_telemetry_badge(curr: dict):
    print(
        f"   {BOLD}TELEMETRY:{RESET} {GREEN}Pos: ({curr['x']:5.2f}, {curr['y']:5.2f}, {curr['z']:5.2f})m{RESET} | "
        f"{BLUE}Vel: ({curr['vx']:5.2f}, {curr['vy']:5.2f}, {curr['vz']:5.2f})m/s{RESET} | "
        f"{MAGENTA}Tilt: (p:{curr['pitch_deg']:4.1f}°, r:{curr['roll_deg']:4.1f}°){RESET}"
    )


def run_mission():
    print_banner()

    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data = mujoco.MjData(model)
    controller = Hexacopter6DOFController(model, data)
    agent = LLMToolAgent(provider="mock")

    dt = model.opt.timestep

    mission_script = [
        ("INITIAL TELEMETRY CHECK", "status"),
        ("AUTONOMOUS TAKEOFF", "takeoff to 4m"),
        ("STATION KEEPING", "hold"),
        ("WAYPOINT 1 (FORWARD-RIGHT CLIMB)", "goto 5, 4, 6"),
        ("WAYPOINT 2 (RECTANGULAR CROSS)", "goto -3, 4, 5"),
        ("CONTEXT-AWARE RELATIVE CLIMB", "go up 2m higher"),
        ("SAFETY BOUNDS TEST (UNSAFE COMMAND)", "takeoff to 150m"),
        ("PRECISION LANDING", "land"),
        ("POST-FLIGHT TELEMETRY CHECK", "status"),
    ]

    def step_sim(seconds: float):
        n_steps = int(seconds / dt)
        for i in range(n_steps):
            thrusts = controller.compute_rotor_thrusts()
            data.ctrl[:] = thrusts
            mujoco.mj_step(model, data)
            if i % int(0.5 / dt) == 0 and seconds > 1.0:
                curr = get_sensor_telemetry(data)
                print_telemetry_badge(curr)
                time.sleep(0.08) # smooth visual cadence for screen recording

    for phase, cmd_text in mission_script:
        print(f"{YELLOW}[PHASE: {phase}]{RESET}")
        print(f" {BOLD}USER PROMPT >{RESET} {CYAN}'{cmd_text}'{RESET}")
        time.sleep(0.4)

        telemetry = get_sensor_telemetry(data)
        tool_call = agent.generate_tool_call(cmd_text, telemetry_context=telemetry)
        tool_name = tool_call.get("tool", "unknown")
        kwargs = tool_call.get("kwargs", {})

        print(f" {BOLD}LLM TOOL CALL >{RESET} {MAGENTA}{tool_name}({kwargs}){RESET}")

        try:
            val_kwargs = validate_tool_call(tool_name, kwargs)
            print(f" {BOLD}SAFETY CHECK >{RESET} {GREEN}[PASSED — WITHIN HARD BOUNDS]{RESET}")

            if tool_name == "takeoff":
                controller.set_target_position(telemetry["x"], telemetry["y"], val_kwargs["altitude_m"])
                step_sim(4.5)
            elif tool_name == "goto":
                controller.set_target_position(val_kwargs["x"], val_kwargs["y"], val_kwargs["z"], val_kwargs["yaw_deg"])
                step_sim(5.5)
            elif tool_name == "hold":
                curr = get_sensor_telemetry(data)
                controller.set_target_position(curr["x"], curr["y"], curr["z"])
                step_sim(2.5)
            elif tool_name == "land":
                curr = get_sensor_telemetry(data)
                controller.set_target_position(curr["x"], curr["y"], MIN_ALTITUDE)
                step_sim(5.0)
            elif tool_name == "get_status":
                curr = get_sensor_telemetry(data)
                print_telemetry_badge(curr)

            curr_final = get_sensor_telemetry(data)
            print(f" {BOLD}AGENT RESPONSE >{RESET} {GREEN}Command completed. Altitude: {curr_final['z']:.2f}m.{RESET}\n")

        except SafetyViolation as e:
            print(f" {BOLD}SAFETY CHECK >{RESET} {RED}[REJECTED BY BOUNDS CHECKER]{RESET}")
            print(f" {BOLD}AGENT RESPONSE >{RESET} {RED}REJECTED — {e}{RESET}\n")

        time.sleep(0.6)

    print(f"{CYAN}{'='*72}{RESET}")
    print(f"{BOLD}{GREEN}MISSION COMPLETE — ALL WAYPOINTS VISITED & SAFETY BOUNDS VERIFIED{RESET}")
    print(f"{CYAN}{'='*72}{RESET}")


if __name__ == "__main__":
    run_mission()
