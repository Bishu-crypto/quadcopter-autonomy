"""
Voyager NL-Drone-Agent — Dialogue Interface Node

Provides an interactive CLI and scriptable entry point for typed natural-language commands.
Maintains multi-turn conversation context and physical telemetry state across backends.
"""
import os
import sys
import argparse
import numpy as np

from safety import validate_tool_call, SafetyViolation, MIN_ALTITUDE
from llm_client import LLMToolAgent
from controller import Hexacopter6DOFController, SimulationBackend
from dialogue_control import MODEL_PATH, get_sensor_telemetry, create_backend


class VoyagerDialogueNode:
    """
    Text-Input Dialogue Node maintaining turn-by-turn context across natural language queries.
    """
    def __init__(self, provider: str = "mock", backend: "str | SimulationBackend | None" = None):
        if isinstance(backend, SimulationBackend):
            self.backend = backend
        else:
            self.backend = create_backend(backend)

        self.controller = Hexacopter6DOFController(backend=self.backend)
        self.agent = LLMToolAgent(provider=provider)
        self.dt = self.backend.dt
        self.turn_count = 0
        self.history = []

        # Backward compatibility with callers accessing node.model / node.data
        if hasattr(self.backend, "m"):
            self.model = self.backend.m
            self.data = self.backend.d
        else:
            self.model = None
            self.data = None

    def step_sim(self, seconds: float):
        n_steps = int(seconds / self.dt)
        for _ in range(n_steps):
            self.controller.step(self.dt)

    def process_user_input(self, user_text: str) -> str:
        self.turn_count += 1
        telemetry = self.backend.get_telemetry()
        
        # 1. LLM Tool-Calling Layer
        tool_call = self.agent.generate_tool_call(user_text, telemetry_context=telemetry)
        tool_name = tool_call.get("tool", "unknown")
        kwargs = tool_call.get("kwargs", {})

        # 2. Safety Validation Layer & Controller Execution
        try:
            val_kwargs = validate_tool_call(tool_name, kwargs)

            if tool_name == "takeoff":
                alt = val_kwargs["altitude_m"]
                self.controller.set_target_position(telemetry["x"], telemetry["y"], alt)
                self.step_sim(5.0)
                curr = self.backend.get_telemetry()
                response = f"[agent] Taking off to {alt:.1f}m. Current position: ({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."

            elif tool_name == "goto":
                x, y, z, yaw = val_kwargs["x"], val_kwargs["y"], val_kwargs["z"], val_kwargs["yaw_deg"]
                self.controller.set_target_position(x, y, z, yaw)
                self.step_sim(6.0)
                curr = self.backend.get_telemetry()
                response = f"[agent] Navigated to waypoint ({x:.1f}, {y:.1f}, {z:.1f})m. Current position: ({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."

            elif tool_name == "set_velocity":
                vx, vy, vz = val_kwargs["vx"], val_kwargs["vy"], val_kwargs["vz"]
                self.controller.set_target_velocity(vx, vy, vz)
                self.step_sim(4.0)
                curr = self.backend.get_telemetry()
                response = f"[agent] Speed set to ({vx:.1f}, {vy:.1f}, {vz:.1f}) m/s. Current velocity: ({curr['vx']:.2f}, {curr['vy']:.2f}, {curr['vz']:.2f}) m/s."

            elif tool_name == "hold":
                curr = self.backend.get_telemetry()
                self.controller.set_target_position(curr["x"], curr["y"], curr["z"])
                self.step_sim(3.0)
                curr = self.backend.get_telemetry()
                response = f"[agent] Holding hover position at ({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m."

            elif tool_name == "land":
                curr = self.backend.get_telemetry()
                self.controller.set_target_position(curr["x"], curr["y"], MIN_ALTITUDE)
                self.step_sim(6.0)
                curr = self.backend.get_telemetry()
                response = f"[agent] Landing completed. Touchdown altitude: {curr['z']:.2f} m."

            elif tool_name == "get_status":
                curr = self.backend.get_telemetry()
                response = (
                    f"[agent] Real telemetry: Position ({curr['x']:.2f}, {curr['y']:.2f}, {curr['z']:.2f}) m | "
                    f"Velocity ({curr['vx']:.2f}, {curr['vy']:.2f}, {curr['vz']:.2f}) m/s | "
                    f"Attitude (r:{curr['roll_deg']:.1f}°, p:{curr['pitch_deg']:.1f}°, y:{curr['yaw_deg']:.1f}°)"
                )
            else:
                response = f"[agent] Command not recognized: '{user_text}'"

        except SafetyViolation as e:
            response = f"[agent] REJECTED — {e}"

        self.history.append({"turn": self.turn_count, "input": user_text, "response": response})
        return response

    def run_interactive(self):
        print("=== Voyager NL-Drone-Agent Interactive CLI ===")
        print("Type natural language commands for the heavy-lift hexacopter. Type 'exit' to quit.\n")
        while True:
            try:
                user_input = input("voyager-agent> ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit"):
                    print("Exiting dialogue node.")
                    break
                resp = self.process_user_input(user_input)
                print(f"{resp}\n")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting dialogue node.")
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voyager NL-Drone-Agent Dialogue Node")
    parser.add_argument("--interactive", action="store_true", help="Run interactive CLI loop")
    parser.add_argument("--provider", type=str, default="mock", help="LLM provider (mock, gemini, openai)")
    parser.add_argument(
        "--backend",
        type=str,
        default=os.environ.get("VOYAGER_BACKEND", "mujoco"),
        choices=["mujoco", "voyager_sim", "voyager"],
        help="Simulation backend (default: mujoco or $VOYAGER_BACKEND)",
    )
    parser.add_argument("commands", nargs="*", help="Optional batch commands to execute")

    args = parser.parse_args()
    node = VoyagerDialogueNode(provider=args.provider, backend=args.backend)

    if args.interactive:
        node.run_interactive()
    elif args.commands:
        for cmd in args.commands:
            print(f"> {cmd}")
            print(node.process_user_input(cmd))
    else:
        # Default quick verification batch
        sample_batch = ["takeoff to 3m", "goto 2, 2, 4", "hold", "land"]
        for cmd in sample_batch:
            print(f"> {cmd}")
            print(node.process_user_input(cmd))
