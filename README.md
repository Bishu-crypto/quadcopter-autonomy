# Voyager — A Modular Autonomous UAV Ecosystem

**Author:** Vaibhav | IIT Madras — BS Electronic Systems (2023–2027)  
**Repo:** [github.com/Bishu-crypto/quadcopter-autonomy](https://github.com/Bishu-crypto/quadcopter-autonomy)

> Re-architecting the entire UAV stack from scratch to understand, model, and build every layer of an autonomous aerial vehicle system — from physics simulation to embedded flight controller firmware.

---

## 🚀 Getting Started (Onboarding)

> [!IMPORTANT]
> If you are a new developer or starting a new programming agent session, you **MUST** read and understand our **[ENGINEERING_PRINCIPLES.md](./docs/ENGINEERING_PRINCIPLES.md)** first. It governs our system philosophy, modular boundaries, simulation-first workflow, and coding guidelines.

---

## 🧭 Repository Structure

```
quadcopter-autonomy/ (Voyager Root)
├── README.md               # Main repository directory index
├── .gitignore              # Repository file exclusion rules
├── docs/                   # General documentation
│   ├── Vision.md           # Why Voyager exists & core philosophies
│   ├── Architecture.md     # Module boundaries, data flow, & topologies
│   ├── Roadmap.md          # 1-2 Year Milestones
│   ├── CodingStandards.md  # Naming, formatting, and safety-critical rules
│   ├── ENGINEERING_PRINCIPLES.md # Core master prompt and onboarding philosophy
│   ├── CONTRIBUTING.md     # Pull request guidelines & contribution flow
│   ├── CHANGELOG.md        # Record of project version releases
│   ├── ADR/                # Architecture Decision Records directory
│   └── Theory/             # Mathematical & physical foundations of Voyager
│       ├── FlightDynamics.md  # 6-DOF kinematics and dynamics
│       ├── Control.md         # Cascaded PID control & mixer math
│       ├── Estimation.md      # Sensor modeling & complementary/EKF filters
│       ├── Communications.md  # Telemetry packet framing & serialization
│       ├── Navigation.md      # Path planning & geofencing guidelines
│       ├── Aerodynamics.md    # Rotor aerodynamics & wind modeling
│       └── Sensors.md         # Detailed sensor physics
├── modules/                # Production software modules
│   └── voyager-sim/        # High-fidelity 6-DOF physics and environment simulator
├── prototype/              # Historical prototypes
│   └── voyager-prototype-v0.1/ # Voyager Prototype v0.1
│       └── quadcopter_ws/  # Original ROS 2 simulation and GCS bridge workspace
├── experiments/            # Legacy flight control and simulation experiments
├── logs/                   # Raw and analyzed flight telemetry data
├── specs/                  # Interface specifications and protocol schemas
├── journal/                # Daily engineering logs and developer design diaries
├── scripts/                # Build and test automation scripts
├── tools/                  # Log parsers and sensor calibration helpers
└── assets/                 # Images, reports, and CAD model files
```

---

*Part of a broader embedded systems + UAV portfolio → [github.com/Bishu-crypto](https://github.com/Bishu-crypto)*
