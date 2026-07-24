# Voyager — UAV Autonomy Ecosystem & Heavy-Lift UAV Showcase

**Author:** Vaibhav | IIT Madras — BS Electronic Systems (2023–2027)  
**Repository:** [github.com/Bishu-crypto/quadcopter-autonomy](https://github.com/Bishu-crypto/quadcopter-autonomy)

---

## 🚁 Project Showcase: Heavy-Lift Gas-Electric Hybrid Hexacopter

![Heavy-Lift UAV 360 Turntable](projects/heavy-lift-uav/reports/figures/cad_360_turntable.gif)

### Summary
This repository contains the comprehensive, multi-disciplinary engineering design, simulation, and validation suite for the **Voyager Heavy-Lift Gas-Electric Hybrid Hexacopter UAV**. The vehicle is engineered to carry a **10.0 kg payload** over a **30 km operational mission radius** (60 km total out-and-back range) with a **20-minute hover loiter** on-station, and is powered by a **3.6 kW gas-electric hybrid generator** coupled to a 48V DC bus. Through first-principles calculations, Blade Element Momentum (BEM) rotor aerodynamic simulations, 3D parametric CAD modeling (FreeCAD), finite element structural analysis (FEA), and KiCad electrical schematic design, the entire UAV architecture has been verified against a locked design baseline. The primary structural load path is governed by an **asymmetric motor-out emergency recovery (1.5G)** case, which maintains a safety factor of **4.87** on the 1.12m carbon fiber arms, ensuring robust system reliability.

### Headline Specifications & Performance Baseline

| Parameter | Locked Baseline Value | Engineering Basis / Status |
| :--- | :--- | :--- |
| **Total Takeoff Weight (TOW)** | `34.575 kg` | Mathematically converged via 5-iteration mass-power-fuel loop |
| **Hover Electrical Power** | `3,460.1 W` | Total DC electrical draw (48V nominal, 6 arms @ $60^\circ$) |
| **Operational Mission Range** | `60.0 km` | 30 km out-and-back mission radius |
| **Mission Endurance** | `104.0 minutes` | 30 km out @ 12 m/s + 20 min loiter + 30 km back @ 12 m/s |
| **Governing Safety Factor** | `4.87` | Asymmetric motor-out emergency recovery (Peak bending stress = 164.4 MPa vs UTS = 800 MPa) |

---

## Design Notes

See /docs/design_notes.md - handwritten derivations and reasoning for every major design decision, written by the author during development.

---

## 🧭 Repository Folder Structure

```
quadcopter-autonomy/ (Voyager Root)
├── README.md                          # Main repository landing page and project showcase
├── .gitignore                         # Git exclusion rules (excluding caches, locks, and backups)
├── docs/                              # General & theoretical documentation
│   ├── Vision.md                      # Core philosophy and vision of Voyager
│   ├── Architecture.md                # System module boundaries and architecture layout
│   ├── design_notes.md                # [New] Handwritten derivations and reasoning for major design decisions
│   ├── ENGINEERING_PRINCIPLES.md      # Development philosophy and engineering principles
│   └── Theory/                        # Mathematical & physical foundations of flight control
│       ├── FlightDynamics.md          # 6-DOF kinematics and dynamics
│       ├── Control.md                 # PID control and rotor mixing mathematics
│       └── Aerodynamics.md            # Rotor aerodynamics and BEM theory
├── projects/
│   └── heavy-lift-uav/                # Showcase: Heavy-Lift Gas-Electric Hybrid Hexacopter Suite
│       ├── DESIGN_LOCK.md             # Locked system parameters & target baseline (source of truth)
│       ├── design_calculations/       # First-principles calculations (mass, power, structural, propulsion)
│       ├── simulation/                # Aerodynamic BEM & 3D CAD visualization generation scripts
│       ├── freecad/                   # Parametric 3D CAD python macro & exported STEP assembly
│       ├── kicad/                     # 48V electrical schematic & generated PDF schematic
│       ├── reports/                   # Compiled LaTeX 9-page report, figures, and turntable GIF
│       └── xflr5/                     # Rotor geometry & NACA 4412 aerodynamic polar files
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
