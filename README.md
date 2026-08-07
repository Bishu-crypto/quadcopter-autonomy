# Voyager — UAV Autonomy Ecosystem & Heavy-Lift UAV Showcase

**Author:** Vaibhav | IIT Madras — BS Electronic Systems (2023–2027)  
**Repository:** [github.com/Bishu-crypto/quadcopter-autonomy](https://github.com/Bishu-crypto/quadcopter-autonomy)

---

## 🚁 Project Showcase: Heavy-Lift Battery-Electric Hexacopter

![Heavy-Lift UAV 360 Turntable](projects/heavy-lift-uav/reports/figures/cad_360_turntable.gif)

### Summary
This repository contains the comprehensive, multi-disciplinary engineering design, simulation, and validation suite for the **Voyager Heavy-Lift Battery-Electric Hexacopter UAV**. The vehicle is engineered to carry a **10.0 kg payload** over a **30 km operational mission radius** (60 km total out-and-back range) with a **20-minute hover loiter** on-station. Grounded in a domestic sourcing strategy, the primary selected battery is the Bangalore-manufactured **Leolus Energy Nexfly (350 Wh/kg)** semi-solid-state battery, with the requested **520 Wh/kg** chemistry treated as an aspirational forward-looking upgrade target. 

Through first-principles calculations, Blade Element Momentum (BEM) rotor aerodynamic simulations, 3D parametric CAD modeling (FreeCAD), finite element structural analysis (FEA), and KiCad electrical schematic design, the entire UAV architecture has been verified across three energy density tiers. The primary structural load path is governed by an **asymmetric motor-out emergency recovery (1.5G)** case, which maintains a safety factor of **4.51** (3.01x the 1.5 floor) under the 520 Wh/kg case, and **2.68** (1.79x the 1.5 floor) under the heavier 350 Wh/kg buildable baseline.

### Three-Tier Sourcing & Sizing Baseline

| Parameter | Leolus Nexfly (350 Wh/kg - Primary Indian) | Tattu/GSL (450 Wh/kg - Imported Best) | DronIQ Target (520 Wh/kg - Aspirational) |
| :--- | :--- | :--- | :--- |
| **Converged TOW** | `62.679 kg` | `41.104 kg` | `37.289 kg` |
| **Battery Pack Mass** | `37.517 kg` | `15.942 kg` | `12.127 kg` |
| **Hover Power Draw** | `7,940.5 W` | `4,386.4 W` | `3,835.7 W` |
| **Mission Energy** | `10,504.9 Wh` | `5,739.2 Wh` | `5,044.6 Wh` |
| **Hover Thrust / Rotor** | `10.45 kg` | `6.85 kg` | `6.22 kg` |
| **Peak Motor-Out Thrust** | `31.34 kg` | `20.55 kg` | `18.64 kg` |
| **Motor Thrust Margin** | `11.7% (vs 35.5 kg limit)` | `42.1% (vs 35.5 kg limit)` | `47.5% (vs 35.5 kg limit)` |
| **Governing Struct. SF** | `SF 2.68 (1.79x margin)` | `SF 4.09 (2.73x margin)` | `SF 4.51 (3.01x margin)` |
| **Resonance Margin (1P/2P)**| `1P: 83.4%, 2P: 60.7%` | `1P: 79.5%, 2P: 98.4%` | `1P: 78.5%, 2P: 108.3%` |
| **Center of Gravity (CG Z)** | `-0.0310 m` | `-0.0473 m` | `-0.0521 m` |

---

## Design Notes

See /docs/design_notes.md - handwritten derivations and reasoning for every major design decision, written by the author during development.

---

## 🤖 Sub-Project Showcase: Voyager NL-Drone-Agent (MuJoCo)

![Flight Telemetry Dynamics](projects/nl-drone-agent/flight_demo_plot.png)

### Summary & Architecture
The **Voyager NL-Drone-Agent** (`projects/nl-drone-agent/`) extends the heavy-lift hexacopter with an autonomous **natural-language dialogue agent** operating inside a high-fidelity **MuJoCo physics simulation**. The system features strict separation between AI reasoning and deterministic physical safety:

1. **Swappable LLM Tool-Calling Layer (`llm_client.py`)**: Constrains user text prompts into structured function calls (`takeoff`, `goto`, `land`, `hold`, `set_velocity`, `get_status`) with context maintenance across turns ("go up 2m higher").
2. **Deterministic Safety Validation Layer (`safety.py`)**: Hard physical bounds firewall ($Z_{max}=50\text{m}, Z_{min}=0.15\text{m}, V_{max}=8\text{m/s}, R_{geofence}=100\text{m}$). Out-of-bounds commands are rejected with explicit feedback.
3. **6-DOF Hexacopter Controller (`controller.py`)**: Full 3D position ($XY + Z$) and attitude (pitch/roll tilt) control via 6-rotor differential thrust allocation.
4. **Interactive CLI & Video Output (`dialogue_node.py` / `render_video.py`)**: Turn-by-turn dialogue node, rendered 3D flight video (`flight_demo.mp4`), and telemetry plots (`flight_demo_plot.png`).

---

## 🧭 Repository Folder Structure

```
quadcopter-autonomy/ (Voyager Root)
├── README.md                          # Main repository landing page and project showcase
├── .gitignore                         # Git exclusion rules (excluding caches, locks, and backups)
├── docs/                              # General & theoretical documentation
│   ├── Vision.md                      # Core philosophy and vision of Voyager
│   ├── Architecture.md                # System module boundaries and architecture layout
│   ├── design_notes.md                # Handwritten derivations and reasoning for major design decisions
│   ├── ENGINEERING_PRINCIPLES.md      # Development philosophy and engineering principles
│   └── Theory/                        # Mathematical & physical foundations of flight control
├── projects/
│   ├── heavy-lift-uav/                # Showcase: Heavy-Lift Battery-Electric Hexacopter Suite
│   └── nl-drone-agent/                # Showcase: Natural Language Drone Agent in MuJoCo
│       ├── DESIGN_LOCK.md             # Locked tool schemas, safety bounds & 6-DOF equations
│       ├── generate_mjcf.py           # MJCF XML model generator (37.291kg TOW baseline)
│       ├── safety.py                  # Deterministic safety bounds checker
│       ├── llm_client.py              # Swappable LLM tool-calling layer
│       ├── controller.py              # Cascaded 6-DOF position, velocity & tilt controller
│       ├── dialogue_control.py        # Validated execution pipeline demo
│       ├── dialogue_node.py           # Interactive CLI & batch dialogue node
│       ├── run_demo_mission.py        # Animated presentation mission script
│       ├── render_video.py            # Offscreen video & plot generator
│       ├── flight_demo.mp4            # Rendered 3D flight video
│       └── flight_demo_plot.png       # Flight telemetry visualization plot
├── modules/
│   └── voyager-sim/                   # High-performance C++ 6-DOF physics and simulator engine
├── prototype/
│   └── voyager-prototype-v0.1/        # Historical prototype (ROS 2 & Ground Control Station)
└── run_tests.sh                       # Automation script to build and test C++ simulation engine
```

---

## 💻 Quick Start & Running Scripts

To run the design calculations, aerodynamic simulations, and CAD visualization generation, navigate to the repository root directory and execute the following commands:

### 1. Execute Design Sizing & Calculation Modules
These scripts perform first-principles sizing and output converged metrics verifying the baseline:
* **TOW Convergence Loop:**
  ```bash
  python3 projects/heavy-lift-uav/design_calculations/mass_budget.py
  ```
* **Mission Endurance & Power Simulation:**
  ```bash
  python3 projects/heavy-lift-uav/design_calculations/power_endurance.py
  ```
* **Arm Structural Analysis (FEA Beam):**
  ```bash
  python3 projects/heavy-lift-uav/design_calculations/structural_analysis.py
  ```
* **Propulsion Sizing & Rotor Thrust Sizing:**
  ```bash
  python3 projects/heavy-lift-uav/design_calculations/propulsion.py
  ```

### 2. Run Aerodynamic & CAD Renders
* **Rotor Aerodynamics (BEM Simulation):**
  ```bash
  python3 projects/heavy-lift-uav/simulation/rotor_bem.py
  ```
* **Generate CAD View Figures:**
  ```bash
  python3 projects/heavy-lift-uav/simulation/generate_cad_model.py
  ```
* **Generate 360-Degree CAD Rotation Animation:**
  ```bash
  python3 projects/heavy-lift-uav/simulation/generate_cad_animation.py
  ```

### 3. Build & Run C++ 6-DOF Simulator Engine Tests
To build and test the custom `voyager-sim` physics engine:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

*Part of a broader embedded systems + UAV portfolio → [github.com/Bishu-crypto](https://github.com/Bishu-crypto)*
