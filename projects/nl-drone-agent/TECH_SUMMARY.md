# Technical Summary: Safety-Constrained Natural-Language Autonomy for Heavy-Lift UAVs

**Sub-Project:** `projects/nl-drone-agent/` | **Repository:** Voyager (`github.com/Bishu-crypto/quadcopter-autonomy`)  
**Target Evaluation:** Academic & Research Audience (Centre of Drones and Autonomous Systems — CoDRAS, IIT Ropar)

---

## 1. Architectural Philosophy: *LLM Proposes, Deterministic Layer Disposes*

Large Language Models (LLMs) provide powerful semantic reasoning and natural-language abstraction, but their stochastic nature makes direct control signal generation or unvalidated trajectory execution fundamentally unsafe for autonomous UAVs. 

To bridge natural-language intent with flight-critical safety, this architecture enforces a strict physical separation:
1. **Semantic Layer (LLM)**: Constrained to output strictly typed, schema-validated tool proposals (`takeoff`, `goto`, `land`, `hold`, `set_velocity`, `get_status`). The LLM has **zero direct access** to low-level motor commands or raw physics states.
2. **Deterministic Safety Layer (Firewall)**: Evaluates every tool proposal against hard kinematic, altitude, and geofence bounds *prior to dispatch*. Proposals violating bounds are explicitly rejected with explanatory telemetry feedback fed back to the dialogue node.
3. **Control & Plant Layer (Physics Engine)**: Deterministic cascaded 6-DOF controller closing the loop on horizontal translation ($XY$) via body tilt angle generation and differential rotor thrust allocation in MuJoCo.

```
┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│   Natural Language Text   │ ───► │  LLM Tool-Calling Layer   │ ───► │ Deterministic Safety      │
│   "takeoff to 4m"         │      │  takeoff(altitude_m=4.0)  │      │ Validation Firewall       │
└───────────────────────────┘      └───────────────────────────┘      └─────────────┬─────────────┘
                                                                                    │ (If Valid)
                                                                                    ▼
┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│ Real Sensor Telemetry     │ ◄─── │ MuJoCo Physics Engine     │ ◄─── │ Cascaded 6-DOF Multirotor │
│ (Position, Velocity, Att) │      │ (37.291 kg Heavy-Lift)    │      │ Position & Tilt Controller│
└───────────────────────────┘      └───────────────────────────┘      └───────────────────────────┘
```

---

## 2. Core Sub-System Implementations

### A. Swappable LLM Tool-Calling Layer (`llm_client.py`)
- **Schema Constraint**: Constrained strictly to 6 tool functions. Raw code generation and direct low-level control manipulation are prohibited.
- **Context-Aware Telemetry Loop**: Maintains turn-by-turn conversation context and merges real MuJoCo sensor telemetry (`framepos`, `framelinvel`, `framequat`). Resolves state-dependent relative requests (e.g., *"go up 2m higher"*) relative to actual simulated altitude ($Z_{current} + 2.0\text{m}$).
- **Air-Gapped Offline Engine**: Includes a deterministic, local offline parsing engine alongside live API adapters (Gemini / OpenAI), prioritizing zero-latency, local execution for air-gapped defence environments.

### B. Deterministic Safety Validation Layer (`safety.py`)
- **Hard Operational Bounds**:
  - Max Altitude ($Z_{max}$): $50.0\text{ m}$
  - Ground Clearance ($Z_{min}$): $0.15\text{ m}$
  - Max Velocity ($V_{max}$): $8.0\text{ m/s}$
  - Geofence Radius ($R_{geofence}$): $100.0\text{ m}$
- **Rejection Logic**: Out-of-bounds proposals raise `SafetyViolation(reason)`, generating human-readable explanation strings returned to the dialogue node rather than silent clamping.

### C. Cascaded 6-DOF Physical Controller (`controller.py` & `hexacopter.xml`)
- **Plant Dynamics**: Real converged heavy-lift hexacopter model from design calculations ($TOW = 37.291\text{ kg}$, $I_{xx}=5.8965, I_{yy}=5.8815, I_{zz}=11.1390\text{ kg}\cdot\text{m}^2$, $L=1.12\text{ m}$ arm length, $60.97\text{ N}$ hover thrust per rotor).
- **Multi-Axis Control Loop**:
  - *Outer Loop*: Position error $\mathbf{e}_p = \mathbf{p}_{target} - \mathbf{p} \implies$ Desired world accelerations $\mathbf{a}_{cmd} \implies$ Body pitch ($\theta$) and roll ($\phi$) tilt commands.
  - *Inner Loop*: Attitude and angular rate error $\implies$ Rotational moments ($M_{pitch}, M_{roll}, M_{yaw}$).
  - *Allocation*: Differential thrust distribution across 6 alternating CW/CCW rotors.

---

## 3. Empirical Verification Trace

Below is an unedited execution transcript from `dialogue_control.py` demonstrating autonomous 3D navigation, relative context resolution, and explicit safety rejection of an out-of-bounds command (`takeoff to 100m`):

```text
> takeoff to 3m
[agent] Taking off to 3.0 m. Current status: pos=(0.00, -0.00, 3.00) m.
> hold
[agent] Holding position at (0.00, -0.00, 3.00) m.
> status
[agent] Status: pos=(0.00, -0.00, 3.00) m | vel=(0.00, -0.00, -0.00) m/s | attitude=(roll -0.0°, pitch -0.0°, yaw -0.0°)
> goto 4, 3, 5
[agent] Waypoint reached. Target=(4.0, 3.0, 5.0) m | Current=(3.98, 2.99, 5.00) m.
> hold
[agent] Holding position at (3.98, 2.99, 5.00) m.
> go up 2m higher
[agent] Waypoint reached. Target=(4.0, 3.0, 7.0) m | Current=(3.98, 2.99, 7.00) m.
> takeoff to 100m
[agent] REJECTED — Requested takeoff altitude 100.00m is outside safe bounds [0.15m, 50.00m].
> land
[agent] Landing sequence complete. Final altitude 0.15 m.
> status
[agent] Status: pos=(3.98, 2.99, 0.15) m | vel=(-0.00, -0.00, -0.00) m/s | attitude=(roll 0.0°, pitch -0.0°, yaw -0.6°)
```

---

## 4. Forward Research Directions for CoDRAS / Multi-Agent Integration

1. **Air-Gapped Offline LLM Hardening**: Extending local SLM (Small Language Model) inference (e.g., Llama-3-8B / Phi-3 quantized) for zero-dependency onboard execution.
2. **Multi-Agent / Swarm Tool Schema**: Extending single-drone schemas to multi-agent target identifiers (`agent_id`), formation geometry (`formation(type, spacing)`), and decentralized collision avoidance.
3. **Reinforcement Learning (RL) Policy Augmentation**: Replacing hand-tuned cascaded PD gains with RL-trained neural tilt/thrust policies under heavy payload variations and atmospheric turbulence.
