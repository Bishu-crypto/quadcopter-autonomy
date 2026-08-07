# Design Lock — Voyager NL-Drone-Agent Sub-Project

This document captures the frozen parameters, tool-calling schemas, safety boundaries, LLM provider architecture, 6-DOF physical control equations, and forward multi-agent research extension specifications for the natural-language drone agent in MuJoCo.

---

## 1. Fixed Tool-Calling Schemas (Single-Agent Baseline)

The LLM tool-calling layer (`llm_client.py`) is constrained strictly to the following 6 tool functions. Direct code generation or raw MuJoCo `ctrl` manipulation by the LLM is prohibited.

| Tool Name | Parameters | Description |
|---|---|---|
| `takeoff` | `altitude_m: float` | Command takeoff to specified target altitude (m). |
| `goto` | `x: float, y: float, z: float, yaw_deg: float = 0.0` | Fly to absolute 3D coordinate $(x,y,z)$ with optional yaw heading. |
| `set_velocity` | `vx: float, vy: float, vz: float` | Maintain 3D target velocity vector (m/s). |
| `hold` | None | Maintain current position and hover. |
| `land` | None | Initiate automated landing sequence to ground clearance. |
| `get_status` | None | Query real MuJoCo sensor telemetry (`framepos`, `framelinvel`, `framequat`). |

---

## 2. Deterministic Safety Bounds

All proposed tool calls pass through `safety.py` BEFORE dispatching to the control engine. Out-of-bound calls raise `SafetyViolation(reason)` and generate explicit feedback to the dialogue node.

- **Maximum Altitude ($Z_{max}$)**: $50.0 \text{ m}$
- **Minimum Altitude / Clearance ($Z_{min}$)**: $0.15 \text{ m}$
- **Maximum Velocity ($V_{max}$)**: $8.0 \text{ m/s}$
- **Geofence Radius ($R_{geofence}$)**: $100.0 \text{ m}$

---

## 3. Converged Hexacopter Airframe Parameters

Pushed directly from `projects/heavy-lift-uav/design_calculations/mass_budget.py` (520 Wh/kg energy density tier):

- **Take-Off Weight ($TOW$)**: $37.291 \text{ kg}$
- **Center of Gravity ($CG$)**: $[0.0000, 0.0000, -0.0521] \text{ m}$
- **Inertia Matrix ($I_{xx}, I_{yy}, I_{zz}$)**: $[5.8965, 5.8815, 11.1390] \text{ kg}\cdot\text{m}^2$
- **Rotors ($N_{rotors}$)**: 6 rotors at arm length $L = 1.12 \text{ m}$, arranged at $60^\circ$ increments.
- **Hover Thrust per Rotor**: $60.97 \text{ N}$ ($365.82 \text{ N}$ total hover thrust balancing $m \cdot g$).
- **Max Rotor Thrust**: $134.14 \text{ N}$ per rotor.

---

## 4. Cascaded 6-DOF Control Architecture

Translates spatial targets into differential rotor thrusts across the 6 rotor sites:

### Outer Loop (Position & Velocity)
$$\mathbf{a}_{world, cmd} = K_{p,pos} (\mathbf{p}_{target} - \mathbf{p}) - K_{d,pos} \mathbf{v}$$

Rotated into body frame by yaw $\psi$:
$$a_{x,body} = a_{x,cmd}\cos\psi + a_{y,cmd}\sin\psi$$
$$a_{y,body} = -a_{x,cmd}\sin\psi + a_{y,cmd}\cos\psi$$

Target tilt angles:
$$\theta_{target} = \text{clip}\left(\frac{a_{x,body}}{g}, -\theta_{max}, \theta_{max}\right)$$
$$\phi_{target} = \text{clip}\left(\frac{-a_{y,body}}{g}, -\phi_{max}, \phi_{max}\right)$$

### Inner Loop (Attitude & Rate)
$$M_{roll} = K_{p,roll} (\phi_{target} - \phi) - K_{d,roll} \omega_x$$
$$M_{pitch} = K_{p,pitch} (\theta_{target} - \theta) - K_{d,pitch} \omega_y$$
$$M_{yaw} = K_{p,yaw} (\psi_{target} - \psi) - K_{d,yaw} \omega_z$$

### Differential Thrust Allocation
For rotor $i$ at position $(x_i, y_i)$:
$$T_i = \text{clip}\left(T_{hover} + \Delta T_{z,i} - M_{pitch}\frac{x_i}{L} + M_{roll}\frac{y_i}{L} + s_i M_{yaw}, 0, T_{max\_rotor}\right)$$

---

## 5. Priority Path: Local Air-Gapped Offline LLM Engine

To satisfy defence research requirements (e.g. Indian Army field deployments and CoDRAS robotics environments), the system prioritizes **local, zero-cloud execution**:
- The offline rule/regex engine in `llm_client.py` serves as the baseline fallback requiring no external internet connection or API keys.
- **Next-Step Hardening**: Integration of lightweight local Small Language Models (SLMs) such as quantized Llama-3-8B-Instruct or Phi-3-Mini running via ONNX Runtime / `llama.cpp` directly onboard the ground station or drone edge compute node.

---

## 6. Multi-Drone / Multi-Agent Research Extension (Forward Scoping)

Designed for multi-robot swarm research (CoDRAS alignment), extending single-drone tool schemas to multi-agent coordinate systems:

### Proposed Multi-Agent Tool Schema Extension

| Tool Name | Extended Parameters | Description / Multi-Agent Behavior |
|---|---|---|
| `swarm_takeoff` | `agent_ids: list[str] \| "all"`, `altitude_m: float` | Synchronized or staggered takeoff for designated drone agents. |
| `swarm_goto` | `agent_ids: list[str] \| "all"`, `waypoints: list[dict]` | Assign specific spatial targets $(x_i, y_i, z_i)$ per agent ID. |
| `set_formation` | `leader_id: str`, `shape: "wedge" \| "grid" \| "column"`, `spacing_m: float` | Maintain rigid or adaptive formation geometry centered on a leader node. |
| `assign_task` | `agent_id: str`, `task_type: "land_target" \| "geo_track" \| "patrol"`, `target_coords: dict` | Autonomous task distribution across heterogeneous swarm members. |
| `swarm_status` | `agent_ids: list[str] \| "all"` | Returns consolidated multi-vehicle state vector $\mathbf{X} = [\mathbf{x}_1, \dots, \mathbf{x}_N]^T$. |

### Multi-Agent Safety Extensions (`safety.py`)
- **Inter-Agent Collision Avoidance**: Hard pairwise minimum separation $d_{min} = 2.0\text{ m}$.
  $$\|\mathbf{p}_i - \mathbf{p}_j\| \ge d_{min} \quad \forall i \neq j$$
- **Swarm Geofence Enforcement**: Spatial bounding box bounding the entire formation geometry within $R_{geofence}$.
