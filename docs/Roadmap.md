# Voyager — Development Roadmap

This document outlines the engineering phases and key milestones for the development of the **Voyager** UAV ecosystem over the next 1–2 years.

---

## Roadmap at a Glance

```
           M1-6                      M6-12                      M12-18                     M18-24
┌─────────────────────────┐┌─────────────────────────┐┌─────────────────────────┐┌─────────────────────────┐
│         Phase 1         ││         Phase 2         ││         Phase 3         ││         Phase 4         │
│  Sim & Protocol Foundation  ││  Flight Control & SITL  ││  Hardware Design & HITL ││ Advanced Autonomy/Swarm │
└─────────────────────────┘└─────────────────────────┘└─────────────────────────┘└─────────────────────────┘
```

---

## Phase 1: Simulation & Protocol Foundation (Months 1–6)
*Focus: Setting up the developer sandbox, message definitions, serialization logic, and core simulation.*

### Key Deliverables
- **Voyager Messages**: A schema-driven IDL compiler outputting message definitions in C++, Python, and ROS 2 types.
- **Voyager Protocol**: Low-latency, robust binary serialization protocol spec with reference implementations.
- **Voyager Sim**: A standalone, high-performance C++ simulator implementing 6-DOF multirotor rigid body physics.
- **Voyager SDK**: Initial Python bindings exposing connection handlers, heartbeat monitors, and simple control APIs.

### Milestones
* `M1.1`: Messages IDL compiler fully operational.
* `M1.2`: Physics engine verified in 3D (attitude and translation integration checks).
* `M1.3`: Bi-directional packet transmission between simulation and SDK verified over UDP with < 1ms latency.

---

## Phase 2: Flight Control & SITL (Months 6–12)
*Focus: Writing the core flight algorithms and completing the loop in Software-in-the-Loop simulation.*

### Key Deliverables
- **State Estimation (Voyager FC)**: Sensor fusion filters (complementary attitude filter + EKF for position/velocity tracking).
- **Control Loops (Voyager FC)**: Complete cascaded PID controller architecture.
- **Voyager GCS**: Qt-based UI with interactive map, mission planning tools, parameter editor, and real-time artificial horizon.
- **SITL Integration**: Integrated loop connecting `Voyager Sim` ↔ `Voyager FC` ↔ `Voyager GCS`.

### Milestones
* `M2.1`: State estimation filter accuracy within 1 degree (attitude) and 0.1 meters (position) in simulation.
* `M2.2`: Closed-loop autonomous hover and trajectory waypoint tracking in SITL.
* `M2.3`: Parameter editing and real-time mission uploading from Voyager GCS to Voyager FC.

---

## Phase 3: Hardware Design & HITL (Months 12–18)
*Focus: Designing physical electronics and running code on target microcontrollers.*

### Key Deliverables
- **Flight Controller PCB**: Custom schematic and routing layout utilizing STM32H7 or similar MCU.
- **Firmware Port**: Voyager FC ported to RTOS (Zephyr or FreeRTOS) for deterministic 1kHz loop execution.
- **Hardware-in-the-Loop (HITL)**: Physical board running flight firmware, interacting with Voyager Sim running on PC.
- **Telemetry RF Hardware**: Custom radio transceiver designs for 433MHz/915MHz bands.

### Milestones
* `M3.1`: PCB fabrication, assembly, and bench power/sensor verification.
* `M3.2`: Deterministic 1kHz task execution verified on the target MCU.
* `M3.3`: Successful HITL mission execution (firmware running on physical board controls virtual aircraft in simulator).

---

## Phase 4: Advanced Autonomy & Swarms (Months 18–24)
*Focus: Real-world flights, companion computers, and multi-vehicle orchestration.*

### Key Deliverables
- **Real Flight Validation**: Stable, autonomous hover and waypoint flight using the complete custom hardware stack.
- **Companion Computer Interface**: High-bandwidth interface (SPI/UART/Ethernet) linking Voyager FC to companion computers.
- **ROS 2 Autonomy Stack**: Nodes for mapping, obstacle detection (using depth cameras or LiDAR), and path planning.
- **Swarm Simulation**: Multi-vehicle simulation supporting mesh network routing and distributed control.

### Milestones
* `M4.1`: First successful physical flight (manual take-off and hover validation).
* `M4.2`: Fully autonomous real-world mission completion (take-off, waypoint nav, precision land).
* `M4.3`: Multi-vehicle SITL flight demonstrating cooperative behavior.
