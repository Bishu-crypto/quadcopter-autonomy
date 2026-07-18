# Voyager — Product Vision & Core Philosophy

## 1. Why Voyager Exists

Modern autonomous unmanned aerial vehicles (UAVs) are complex systems that typically sit on top of massive, pre-existing frameworks like PX4, ArduPilot, or Gazebo. While these frameworks are highly capable, they often function as complex black boxes for developers and researchers. 

**Voyager** is an engineering initiative to design and build a complete, modular UAV ecosystem from scratch. By systematically replacing each major subsystem (physics engine, flight controller, communication protocols, SDK, and Ground Control Station) with custom implementations, Voyager aims to:
- Achieve complete, bottom-up visibility into flight physics, control systems, and state estimation.
- Provide a modular testbed where any single component can be swapped out for a commercial equivalent (e.g., swapping a custom flight controller for PX4, or swapping a custom simulator for Gazebo).
- Serve as an open, educational, and research-grade platform for autonomy, swarm robotics, and control theory.

---

## 2. Core Philosophy

The design of Voyager is governed by four fundamental architectural principles:

### I. Single Responsibility (Decoupling)
Every module within Voyager is dedicated to a single, well-defined task. The flight controller only computes control outputs; the simulator only updates vehicle states and sensor models; the Ground Control Station only handles telemetry visualization and operator commands.

### II. Interface-Driven Design
No module directly depends on the implementation details of another. Subsystems communicate exclusively through clearly specified, versioned protocols and APIs. For example:
- **Voyager Sim** exposes a standard sensor/actuator API, making it compatible with any flight controller implementation.
- **Voyager GCS** receives generic telemetry packets, remaining agnostic to whether the source is a simulation node or physical hardware.
- **Voyager SDK** defines a high-level vehicle interface that hides the underlying transport layer (UDP, Serial, MAVLink, or custom telemetry).

### III. System Replaceability
The entire ecosystem acts as a puzzle where any piece can be swapped.
```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Voyager Sim   │ ◄───► │   Voyager FC    │ ◄───► │   Voyager GCS   │
└─────────────────┘       └─────────────────┘       └─────────────────┘
         ▲                         ▲                         ▲
         ▼ (Replaceable)           ▼ (Replaceable)           ▼ (Replaceable)
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  PX4 / Gazebo   │       │  PX4 Autopilot  │       │ QGroundControl  │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

### IV. Clean-Sheet Implementation
Every layer is built from first principles (unless explicitly interfacing with external standards) to avoid legacy technical debt and maximize educational value.

---

## 3. Development Strategy

To bridge the gap between simulation and real-world deployment safely and efficiently, Voyager adheres to a strict development pipeline:

```
┌──────────────┐      ┌─────────────────────────┐      ┌─────────────────┐
│  Pure Sim    │ ───► │  Hardware-in-the-Loop  │ ───► │ Real Hardware   │
│  (SITL)      │      │  (HITL)                 │      │ Flight (Twin)   │
└──────────────┘      └─────────────────────────┘      └─────────────────┘
```

1. **Simulation-First Validation**: All algorithms (estimation, control, path planning) must be developed, tested, and verified within the simulator. No code is run on hardware before passing simulation benchmarks.
2. **Digital Twin Alignment**: The physics engine and sensor simulation models are calibrated continuously using real-world flight log data to ensure the simulator acts as an accurate digital twin of the vehicle.
3. **Seamless Transition**: Moving from simulation to hardware must only involve changing compilation targets or interface configs, without changing the core control loops or architecture.

---

## 4. Long-Term Objectives

Over its lifecycle, the Voyager ecosystem is targetted to support:
- **Simulation**: High-fidelity 6-DOF physics, aerodynamics (ground effect, drag, wind), and multi-vehicle dynamics.
- **Software-in-the-Loop (SITL) & Hardware-in-the-Loop (HITL)**: Direct simulation feedback using virtualized or physical flight controller boards.
- **Industry Standard Compatibility**: Full compliance with MAVLink and ROS 2 ecosystems to allow hybrid stacks (e.g., custom Sim + PX4 FC + custom GCS).
- **Advanced Autonomy**: Computer vision, obstacle avoidance, mapping, and AI-driven trajectory generation.
- **Swarm Robotics**: Multi-vehicle coordination, distributed control, and mesh-network communication.
