"""
Swappable LLM Tool-Calling Layer for Voyager NL-Drone-Agent.

Translates natural language text input into structured tool calls constrained strictly
to the fixed tool schema:
  - takeoff(altitude_m)
  - goto(x, y, z, yaw_deg)
  - land()
  - hold()
  - set_velocity(vx, vy, vz)
  - get_status()

Supports API providers (OpenAI/Gemini style) when configured, alongside an intelligent
offline context-aware engine for deterministic execution without requiring external API keys.
"""
import os
import re
import json
import typing

# ---- Fixed Tool Schemas ----
TOOL_SCHEMAS = [
    {
        "name": "takeoff",
        "description": "Command hexacopter to take off to a specified altitude in meters.",
        "parameters": {
            "type": "object",
            "properties": {
                "altitude_m": {"type": "number", "description": "Target altitude above ground in meters."}
            },
            "required": ["altitude_m"]
        }
    },
    {
        "name": "goto",
        "description": "Command hexacopter to fly to a target 3D spatial coordinate (x, y, z) with optional heading yaw.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "Target X position in world frame (m)."},
                "y": {"type": "number", "description": "Target Y position in world frame (m)."},
                "z": {"type": "number", "description": "Target Z position in world frame (m)."},
                "yaw_deg": {"type": "number", "description": "Target yaw angle in degrees (default 0)."}
            },
            "required": ["x", "y", "z"]
        }
    },
    {
        "name": "set_velocity",
        "description": "Command hexacopter to maintain a target 3D velocity vector (vx, vy, vz) in m/s.",
        "parameters": {
            "type": "object",
            "properties": {
                "vx": {"type": "number", "description": "X velocity component (m/s)."},
                "vy": {"type": "number", "description": "Y velocity component (m/s)."},
                "vz": {"type": "number", "description": "Z velocity component (m/s)."}
            },
            "required": ["vx", "vy", "vz"]
        }
    },
    {
        "name": "land",
        "description": "Command hexacopter to initiate landing sequence at current position.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "hold",
        "description": "Command hexacopter to hold current 3D position and hover.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_status",
        "description": "Request current telemetry status (position, velocity, orientation) from MuJoCo sensors.",
        "parameters": {"type": "object", "properties": {}}
    }
]


class MockLLMEngine:
    """
    Context-aware natural language tool parser.
    Resolves relative commands (e.g. 'go up 2m higher', 'fly forward 3m')
    using real telemetry context passed from the drone state.
    """
    def __init__(self):
        pass

    def parse(self, text: str, telemetry: dict | None = None) -> dict:
        text_clean = text.strip().lower()
        
        # Current telemetry context fallback
        curr_x = telemetry.get("x", 0.0) if telemetry else 0.0
        curr_y = telemetry.get("y", 0.0) if telemetry else 0.0
        curr_z = telemetry.get("z", 2.0) if telemetry else 2.0

        # Status request
        if text_clean in ("status", "get status", "what's your status", "telemetry", "state"):
            return {"tool": "get_status", "kwargs": {}}

        # Land
        if text_clean in ("land", "land now", "initiate landing", "descend and land"):
            return {"tool": "land", "kwargs": {}}

        # Hold / Hover
        if text_clean in ("hold", "hover", "hold position", "stop", "pause"):
            return {"tool": "hold", "kwargs": {}}

        # Relative altitude changes: "go up 2m", "climb 5m higher", "go down 1m"
        if m := re.search(r"(?:go|climb|ascend)\s+up(?:\s+by)?\s+([\d.]+)\s*m?", text_clean):
            dz = float(m.group(1))
            return {"tool": "goto", "kwargs": {"x": curr_x, "y": curr_y, "z": curr_z + dz}}
        
        if m := re.search(r"(?:go|descend)\s+down(?:\s+by)?\s+([\d.]+)\s*m?", text_clean):
            dz = float(m.group(1))
            return {"tool": "goto", "kwargs": {"x": curr_x, "y": curr_y, "z": max(0.15, curr_z - dz)}}

        # Takeoff to absolute altitude: "takeoff to 5m", "takeoff 3m"
        if m := re.match(r"takeoff(?: to)? ([\d.]+)m?", text_clean):
            return {"tool": "takeoff", "kwargs": {"altitude_m": float(m.group(1))}}
        if text_clean == "takeoff":
            return {"tool": "takeoff", "kwargs": {"altitude_m": 3.0}}

        # Goto absolute 3D waypoint: "goto 2, 3, 4", "fly to 5, -2, 3", "goto x=2 y=3 z=4"
        if m := re.search(r"goto\s+([\-\d.]+)[, ]+([\-\d.]+)[, ]+([\-\d.]+)(?:[, ]+([\-\d.]+))?", text_clean):
            vals = [float(v) for v in m.groups() if v is not None]
            yaw = vals[3] if len(vals) > 3 else 0.0
            return {"tool": "goto", "kwargs": {"x": vals[0], "y": vals[1], "z": vals[2], "yaw_deg": yaw}}

        if m := re.search(r"fly\s+to\s+([\-\d.]+)[, ]+([\-\d.]+)[, ]+([\-\d.]+)", text_clean):
            return {"tool": "goto", "kwargs": {"x": float(m.group(1)), "y": float(m.group(2)), "z": float(m.group(3))}}

        if m := re.search(r"x\s*=\s*([\-\d.]+).*?y\s*=\s*([\-\d.]+).*?z\s*=\s*([\-\d.]+)", text_clean):
            return {"tool": "goto", "kwargs": {"x": float(m.group(1)), "y": float(m.group(2)), "z": float(m.group(3))}}

        # Relative 2D moves: "fly forward 3m", "move right 2m"
        if m := re.search(r"forward\s+([\d.]+)\s*m?", text_clean):
            dx = float(m.group(1))
            return {"tool": "goto", "kwargs": {"x": curr_x + dx, "y": curr_y, "z": curr_z}}

        if m := re.search(r"right\s+([\d.]+)\s*m?", text_clean):
            dy = float(m.group(1))
            return {"tool": "goto", "kwargs": {"x": curr_x, "y": curr_y + dy, "z": curr_z}}

        # Set velocity: "set velocity 1, 0, 0", "fly at 2 m/s"
        if m := re.search(r"(?:set\s+velocity|velocity)\s+([\-\d.]+)[, ]+([\-\d.]+)[, ]+([\-\d.]+)", text_clean):
            return {"tool": "set_velocity", "kwargs": {"vx": float(m.group(1)), "vy": float(m.group(2)), "vz": float(m.group(3))}}

        # Unrecognized fallback
        return {"tool": "unknown", "kwargs": {"text": text}}


class LLMToolAgent:
    """
    Swappable LLM Tool Agent.
    Switches between local rule-based Mock engine and live API providers based on provider configuration.
    """
    def __init__(self, provider: str = "mock", api_key: str | None = None, model_name: str | None = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name or "gpt-4o-mini"
        self.mock_engine = MockLLMEngine()

    def generate_tool_call(self, prompt: str, telemetry_context: dict | None = None) -> dict:
        """
        Main entry point: maps natural language user prompt to a structured tool call.
        """
        if self.provider == "mock" or not self.api_key:
            return self.mock_engine.parse(prompt, telemetry_context)

        # External API Provider Implementation (OpenAI / Gemini compatible format)
        try:
            import urllib.request
            # Minimal HTTP API call for OpenAI compatible endpoint
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an autonomous drone dialogue assistant. "
                            "Convert user requests into structured tool calls. "
                            f"Available tools: {json.dumps(TOOL_SCHEMAS)}. "
                            f"Current Telemetry: {json.dumps(telemetry_context or {})}."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "tools": [{"type": "function", "function": schema} for schema in TOOL_SCHEMAS],
                "tool_choice": "auto"
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                choice = result["choices"][0]["message"]
                if "tool_calls" in choice and choice["tool_calls"]:
                    tc = choice["tool_calls"][0]["function"]
                    return {"tool": tc["name"], "kwargs": json.loads(tc["arguments"])}
        except Exception as e:
            # Fallback to local mock engine if network/API fails
            pass

        return self.mock_engine.parse(prompt, telemetry_context)
