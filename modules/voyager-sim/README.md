# Voyager Sim (Simulation Engine)

> [!NOTE]
> This module is the next active development target in the Voyager roadmap.

## Responsibilities

Voyager Sim is a high-fidelity 6-DOF simulation engine built to model the flight physics, aerodynamics, sensor signals, and actuators of multirotors. It is completely isolated from flight controller logic.

Key components to be developed here:
1. **Physics Engine**: Rigid body dynamics solvers integrating translation and rotation equations of motion (Euler and Runge-Kutta 4th Order solvers).
2. **Aerodynamics Module**: Models static thrust, rotor torque coefficients, wind resistance, and blade element lift/drag.
3. **Sensor Simulation**: Recreates IMU, GPS, Magnetometer, and Barometer readings, injecting white noise and random walk drifts.
4. **Plugin System**: Allows dynamic loading of different vehicle configurations (X-quad, H-quad, hexacopter) and environmental profiles.

---

## Directory Structure (Target)

```
voyager-sim/
├── include/            # C++ Header files
│   └── voyager/sim/    # Core headers (physics, sensors, plugins)
├── src/                # Implementation source code
├── tests/              # Unit and integration tests (pytest/gtest)
├── CMakeLists.txt      # Build configuration
└── README.md           # Module overview
```

---

## Development Entry Point

Development will begin by establishing the rigid-body kinematic state integration and verifying translational/rotational states under test force inputs.
