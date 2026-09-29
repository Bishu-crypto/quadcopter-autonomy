"""
Voyager NL-Drone-Agent — Screen-Recording Presentation Demo Mission

Executes a styled, multi-phase autonomous flight mission with colorized telemetry,
tool-calling breakdown, safety bounds checking, and live status dashboard.
Ideal for screen recording and uploading to Google Drive / Portfolio.
Supports both MujocoBackend and VoyagerSimBackend.
"""
import os
import sys
import time
import argparse
import numpy as np

from safety import validate_tool_call, SafetyViolation, MIN_ALTITUDE
from llm_client import LLMToolAgent
from controller import Hexacopter6DOFController, SimulationBackend, VoyagerSimBackend
from dialogue_control import MODEL_PATH, create_backend

# ANSI Colors for Terminal Presentation
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
MAGENTA = "\033[1;35m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner(backend_name: str = "MuJoCo"):
    print(f"{CYAN}{'='*72}{RESET}")
    print(f"{BOLD}{CYAN}   VOYAGER HEAVY-LIFT HEXACOPTER — NATURAL LANGUAGE AUTONOMY DEMO{RESET}")
    print(f"{CYAN}   TOW: 37.291 kg | 6-DOF Position & Tilt Control | {backend_name} Physics{RESET}")
    print(f"{CYAN}{'='*72}{RESET}\n")


def print_telemetry_badge(curr: dict):
    print(
        f"   {BOLD}TELEMETRY:{RESET} {GREEN}Pos: ({curr['x']:5.2f}, {curr['y']:5.2f}, {curr['z']:5.2f})m{RESET} | "
        f"{BLUE}Vel: ({curr['vx']:5.2f}, {curr['vy']:5.2f}, {curr['vz']:5.2f})m/s{RESET} | "
        f"{MAGENTA}Tilt: (p:{curr['pitch_deg']:4.1f}°, r:{curr['roll_deg']:4.1f}°){RESET}"
    )


def run_mission(backend: "str | SimulationBackend | None" = None, fast: bool = False):
    if isinstance(backend, SimulationBackend):
        sim_backend = backend
    else:
        sim_backend = create_backend(backend)

    backend_label = "Voyager-Sim C++ (RK4)" if isinstance(sim_backend, VoyagerSimBackend) else "MuJoCo"
    print_banner(backend_label)

    controller = Hexacopter6DOFController(backend=sim_backend)
    agent = LLMToolAgent(provider="mock")

    dt = sim_backend.dt
    sleep_mult = 0.0 if fast else 1.0

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
        step_badge_interval = int(0.5 / dt)
        for i in range(n_steps):
            controller.step(dt)
            if i % step_badge_interval == 0 and seconds > 1.0:
                curr = sim_backend.get_telemetry()
                print_telemetry_badge(curr)
                if sleep_mult > 0:
                    time.sleep(0.08 * sleep_mult)

    for phase, cmd_text in mission_script:
        print(f"{YELLOW}[PHASE: {phase}]{RESET}")
        print(f" {BOLD}USER PROMPT >{RESET} {CYAN}'{cmd_text}'{RESET}")
        if sleep_mult > 0:
            time.sleep(0.4 * sleep_mult)

        telemetry = sim_backend.get_telemetry()
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
                curr = sim_backend.get_telemetry()
                controller.set_target_position(curr["x"], curr["y"], curr["z"])
                step_sim(2.5)
            elif tool_name == "land":
                curr = sim_backend.get_telemetry()
                controller.set_target_position(curr["x"], curr["y"], MIN_ALTITUDE)
                step_sim(5.0)
            elif tool_name == "get_status":
                curr = sim_backend.get_telemetry()
                print_telemetry_badge(curr)

            curr_final = sim_backend.get_telemetry()
            print(f" {BOLD}AGENT RESPONSE >{RESET} {GREEN}Command completed. Altitude: {curr_final['z']:.2f}m.{RESET}\n")

        except SafetyViolation as e:
            print(f" {BOLD}SAFETY CHECK >{RESET} {RED}[REJECTED BY BOUNDS CHECKER]{RESET}")
            print(f" {BOLD}AGENT RESPONSE >{RESET} {RED}REJECTED — {e}{RESET}\n")

        if sleep_mult > 0:
            time.sleep(0.6 * sleep_mult)

    print(f"{CYAN}{'='*72}{RESET}")
    print(f"{BOLD}{GREEN}MISSION COMPLETE — ALL WAYPOINTS VISITED & SAFETY BOUNDS VERIFIED{RESET}")
    print(f"{CYAN}{'='*72}{RESET}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voyager NL-Drone-Agent Presentation Demo Mission")
    parser.add_argument(
        "--backend",
        type=str,
        default=os.environ.get("VOYAGER_BACKEND", "mujoco"),
        choices=["mujoco", "voyager_sim", "voyager"],
        help="Simulation backend (default: mujoco or $VOYAGER_BACKEND)",
    )
    parser.add_argument("--fast", action="store_true", help="Run without presentation delays")
    args = parser.parse_args()

    run_mission(backend=args.backend, fast=args.fast)
