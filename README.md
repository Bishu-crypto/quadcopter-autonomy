# Quadcopter Autonomy Project

**Author:** Vaibhav | IIT Madras — BS Electronic Systems (2023–2027)  
**Stack:** PX4 v1.14 · ROS 2 Humble · Gazebo Harmonic · Pixhawk 1 (rev 2.4.8)  
**Repo:** [github.com/Bishu-crypto/quadcopter-autonomy](https://github.com/Bishu-crypto/quadcopter-autonomy)

> From simulation to autonomous real-world flight — fully documented.

---

## Project Phases

| Phase | Title | Status |
|-------|-------|--------|
| [00 — SITL Setup](./00-sitl-setup/) | PX4 SITL + Gazebo + ROS 2 Bridge | 🔄 In Progress |
| [01 — Build Log](./01-build-log/) | Hardware Assembly + Calibration | ⏳ Pending |
| [02 — Flight Logs](./02-flight-logs/) | Manual Flight Validation | ⏳ Pending |
| [03 — Offboard Control](./03-offboard-control/) | ROS 2 Autonomous Control | ⏳ Pending |
| [04 — Advanced](./04-advanced/) | Precision Landing / Avoidance | ⏳ Pending |

---

## Hardware Stack

| Component | Specification |
|-----------|---------------|
| Flight Controller | Pixhawk 1 rev 2.4.8 (STM32F405RGT6) |
| Motors | BLDC, quadcopter spec |
| ESCs | PWM compatible |
| GPS | u-blox compatible module |
| RC System | Standard 6+ channel TX/RX |
| Battery | LiPo |
| Companion (Phase 4) | ESP32 — MAVLink WiFi bridge |

## Software Stack

| Software | Version | Purpose |
|----------|---------|---------|
| Ubuntu | 22.04 LTS | Host OS |
| PX4 Autopilot | v1.14 | Flight firmware + SITL |
| ROS 2 | Humble | Offboard control framework |
| Gazebo | Harmonic 8.11 | 3D physics simulation |
| QGroundControl | Latest | Ground station + log analysis |
| uXRCE-DDS | micro-ROS | PX4 ↔ ROS 2 bridge |

---

## Progress Log

| Date | Phase | Milestone |
|------|-------|-----------|
| Mar 29, 2026 | — | Repository initialized, project structure created |

---

## Repository Structure
```
quadcopter-autonomy/
├── 00-sitl-setup/          # PX4 SITL, Gazebo, uXRCE-DDS, ROS 2 bridge
│   ├── launch/             # ROS 2 launch files
│   ├── configs/            # PX4 params, world files
│   └── README.md
├── 01-build-log/           # Hardware assembly documentation
│   ├── wiring/             # Wiring diagrams
│   ├── photos/             # Build progress photos
│   ├── calibration/        # QGC calibration screenshots
│   └── README.md
├── 02-flight-logs/         # Flight data
│   ├── raw/                # .ulg log files
│   ├── analysis/           # Flight Review exports
│   └── README.md
├── 03-offboard-control/    # ROS 2 offboard control package
│   ├── src/                # Node source code
│   ├── launch/             # Launch files
│   ├── config/             # Parameters
│   └── README.md
├── 04-advanced/            # Advanced autonomy feature
│   ├── src/
│   └── README.md
└── docs/                   # Reports, architecture diagrams
```

---

*Part of a broader embedded systems + UAV portfolio → [github.com/Bishu-crypto](https://github.com/Bishu-crypto)*
