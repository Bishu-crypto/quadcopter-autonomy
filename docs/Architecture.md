# Voyager — System Architecture

This document defines the high-level architecture of the Voyager UAV Ecosystem, describing the responsibilities of each module, the boundaries of their interfaces, and how they interact in different deployment configurations.

---

## 1. System Components

Voyager consists of 9 independent modules. Each module is housed in its own directory, compiled independently, and communicates through strict interface boundaries.

```
                             ┌──────────────────┐
                             │ Voyager Messages │
                             └────────┬─────────┘
                                      │ (Defines Shared Types)
                                      ▼
  ┌─────────────────┐       ┌──────────────────┐       ┌──────────────────┐
  │   Voyager Sim   │ ◄───► │    Voyager FC    │ ◄───► │   Voyager GCS    │
  └────────┬────────┘       └────────┬─────────┘       └────────┬─────────┘
           │ (Digital Twin)          │ (Firmware Target)        │ (Operator API)
           ▼                         ▼                          ▼
  ┌─────────────────┐       ┌──────────────────┐       ┌──────────────────┐
  │   Plugin Sys    │       │ Voyager Hardware │       │   Voyager SDK    │
  └─────────────────┘       └──────────────────┘       └──────────────────┘
                                     ▲
                                     │ (Governs Comm Links)
                            ┌────────┴─────────┐
                            │ Voyager Protocol │
                            └──────────────────┘
```

### I. Voyager Sim (Simulation Engine)
* **Core Role**: High-fidelity 6-DOF physics and environment simulation.
* **Key Features**:
  * Rigid-body multirotor equations of motion (Euler or RK4 integration).
  * Aerodynamic forces and moments (drag, lift, ground effect, thrust, torque).
  * Sensor models with realistic noise, bias, and latency (IMU, Barometer, GPS, Magnetometer).
  * Extensible C++ plugin architecture for adding new sensors, vehicles, or environmental factors (e.g., wind).

### II. Voyager FC (Flight Controller)
* **Core Role**: Real-time state estimation and flight control loop.
* **Key Features**:
  * State Estimation: Complementary/Madgwick filter and Extended Kalman Filter (EKF) for attitude and position fusion.
  * Flight Control: Cascaded PID loops (Position -> Velocity -> Attitude -> Attitude Rate).
  * Navigation: Mission execution engine, waypoint tracking, and trajectory generation.
  * Actuation: Motor mixer converting throttle, roll, pitch, and yaw commands into individual ESC signals.
  * Safety: Failsafe state machine (low battery, signal loss, geofence breach).

### III. Voyager GCS (Ground Control Station)
* **Core Role**: User interface for vehicle monitoring, configuration, and mission planning.
* **Key Features**:
  * Cross-platform desktop application built using Python and Qt (PySide6).
  * Real-time 3D artificial horizon and telemetry dashboards.
  * Interactive 2D map for waypoint placement, mission editing, and live flight tracking.
  * Parameter editor to read and write controller configurations.
  * Offline log viewer for post-flight analysis.

### IV. Voyager SDK (Software Development Kit)
* **Core Role**: Developer API for high-level autonomous mission control.
* **Key Features**:
  * Available in Python and C++.
  * Hides communication implementation details, exposing clean methods like `takeoff()`, `go_to_waypoint()`, and `get_telemetry()`.
  * Integrates with ROS 2 and external scripting tools.

### V. Voyager Protocol (Communication Protocol)
* **Core Role**: Binary serialization, packet framing, and messaging.
* **Key Features**:
  * Custom low-overhead binary framing (Start/End bytes, Message ID, Payload Length, CRC-16 checksum).
  * Standardized message structures (Heartbeats, State Estimates, Control Overrides, Waypoint Lists, Parameters).
  * Strict packet-loss mitigation and validation rules.

### VI. Voyager Messages (Shared Interface Definitions)
* **Core Role**: Language-agnostic message definitions.
* **Key Features**:
  * Schema-based message IDL (Interface Definition Language) like Protobuf or a custom generator.
  * Compiles definitions directly into Python, C++, and ROS 2 message formats.
  * Acts as the single source of truth for both Voyager Protocol and internal ROS 2 nodes.

### VII. Voyager Hardware (Physical Platform)
* **Core Role**: Physical implementation and PCB schematics.
* **Key Features**:
  * Flight Controller Board: STM32-based processor, dual IMUs, magnetometer, barometer, and flash storage.
  * Telemetry Module: RF transceiver schematics.
  * Support for ESC, RC receiver, and Power Distribution Board (PDB) design.

### VIII. Voyager Documentation
* **Core Role**: Mathematical theory, design rationale, API references, and user guides.

---

## 2. Interaction Topologies

To fulfill the core philosophy of complete replaceability, Voyager supports three runtime topologies:

### Topology A: Software-in-the-Loop (SITL)
Used for pure software testing. All modules run on a single developer PC.

```
┌────────────────────────────────────────────────────────────────────────┐
│                              Developer PC                              │
│                                                                        │
│  ┌───────────────┐     UDP / IPC      ┌──────────────┐                 │
│  │  Voyager Sim  │ ◄────────────────► │  Voyager FC  │                 │
│  │  (Simulation) │  (Sensors/Motors)  │  (Firmware)  │                 │
│  └───────────────┘                    └──────┬───────┘                 │
│                                              │                         │
│                                              │ Voyager Protocol (UDP)  │
│                                              ▼                         │
│                                       ┌──────────────┐                 │
│                                       │ Voyager GCS  │                 │
│                                       │  (Operator)  │                 │
│                                       └──────────────┘                 │
└────────────────────────────────────────────────────────────────────────┘
```

### Topology B: Hardware-in-the-Loop (HITL)
Used to validate the flight controller firmware on the target micro-controller.

```
┌───────────────────────────────────┐               ┌────────────────────┐
│           Developer PC            │               │  Voyager HW Board  │
│                                   │  Serial/USB   │                    │
│  ┌───────────────┐  Sensor Data   │ ────────────► │ ┌────────────────┐ │
│  │  Voyager Sim  │ ───────────────┼───────────────┼─► State Estimation│ │
│  │ (Physics/Sens)│ ◄──────────────┼───────────────┼─┤ & Flight Control│ │
│  └───────────────┘   Motor PWMs   │ ◄─────────────┼─┼─ Motor Mixer   │ │
│                                   │               │ └──────┬─────────┘ │
│  ┌───────────────┐                │               │        │           │
│  │  Voyager GCS  │ ◄──────────────┼───────────────┼────────┘           │
│  │  (Operator)   │   RF Telemetry │  RF/Telemetry │                    │
│  └───────────────┘                │  (Protocol)   │                    │
└───────────────────────────────────┘               └────────────────────┘
```

### Topology C: Real Flight Deployment
Used for physical flight operations.

```
┌───────────────────────────────────┐               ┌────────────────────┐
│           Ground Station          │               │      UAV Body      │
│                                   │               │                    │
│  ┌───────────────┐                │  RF Link      │ ┌────────────────┐ │
│  │  Voyager GCS  │ ◄──────────────┼───────────────┼─►  Voyager FC    │ │
│  │  (Operator)   │  Voyager Proto │ (Telemetry)   │ └──────┬─────────┘ │
│  └──────┬────────┘                │               │        │ SPI/I2C   │
│         │                         │               │        ▼           │
│         │ SDK API (IPC)           │               │ ┌────────────────┐ │
│         ▼                         │               │ │Physical Sensors│ │
│  ┌───────────────┐                │               │ └────────────────┘ │
│  │  Voyager SDK  │                │               │        │ PWM/DShot │
│  │ (Autonomy App)│                │               │        ▼           │
│  └────────────────┘               │               │ ┌────────────────┐ │
│                                   │               │ │  ESCs & Motors │ │
│                                   │               │ └────────────────┘ │
└───────────────────────────────────┘               └────────────────────┘
```

---

## 3. Module Boundaries & Protocols

### Sensor-Actuator Interface (Sim ↔ FC)
In SITL/HITL mode, state data is passed using high-speed JSON or binary payloads containing:
- **Sensor Outputs (Sim -> FC)**: IMU (`accel_x,y,z`, `gyro_x,y,z`), Magnetometer (`mag_x,y,z`), Barometer (`pressure`, `temperature`), GPS (`lat`, `lon`, `alt`, `vel_n,e,d`).
- **Actuator Commands (FC -> Sim)**: Motor speeds or PWM values (`motor_0,1,2,3`).

### Telemetry Interface (FC ↔ GCS/SDK)
Communications must conform to the **Voyager Protocol** framing:
- **Payload Structure**: `[START_BYTE_1 (0xAA)][START_BYTE_2 (0x55)][MSG_ID (1 byte)][PAYLOAD_LEN (1 byte)][PAYLOAD (N bytes)][CRC_16 (2 bytes)]`
- **Serialization**: Little-endian packing of primitive types.
