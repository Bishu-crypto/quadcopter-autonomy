# Changelog

All notable changes to the Voyager project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0-dev] - 2026-07-12
### Added
- Created the core engineering documentation: `Vision.md`, `Architecture.md`, `Roadmap.md`, `CodingStandards.md`.
- Added the `docs/Theory/` directory containing detailed mathematical foundations: `FlightDynamics.md`, `Control.md`, `Estimation.md`, `Communications.md`.
- Initialized placeholders for upcoming theory documents: `Navigation.md`, `Aerodynamics.md`, `Sensors.md`.
- Added the `docs/ENGINEERING_PRINCIPLES.md` (Master Prompt context) as the primary onboarding document.
- Created `docs/CONTRIBUTING.md` and initialized empty `docs/ADR/`, `specs/`, `journal/`, `scripts/`, `tools/`, `assets/`, and `modules/` directories.

### Changed
- Restructured workspace root layout to decouple production modules, prototype code, legacy logs, and assets.
- Relocated the original proof-of-concept ROS 2 workspace from root to `prototype/voyager-prototype-v0.1/quadcopter_ws/` and marked it as a frozen prototype.
- Moved legacy build, flight, and setup logs into `experiments/` and `logs/`.

---

## [0.1.0] - 2026-07-10
### Added
- Completed initial proof-of-concept monolithic workspace (`custom_uav_stack`).
- Developed a 6-DOF multirotor rigid body physics simulator.
- Implemented a flight controller node with cascaded PID loops (attitude and position hold).
- Developed a GCS telemetry bridge communicating with a Python/Qt Ground Control Station application.
- Successfully verified closed-loop autonomous hovering and waypoint tracking in simulation.
- **Note**: This version is now frozen as **Voyager Prototype v0.1** and is kept for historical reference under `prototype/voyager-prototype-v0.1/`.
