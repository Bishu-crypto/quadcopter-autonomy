# Voyager — Coding Standards & Guidelines

This document details the coding, formatting, testing, and safety guidelines for the Voyager UAV Ecosystem. All contributions must adhere to these rules.

---

## 1. Naming Conventions

### Python Subsystems (GCS, SDK, Prototyping)
Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines:
- **Classes**: `PascalCase` (e.g., `class HoverController:`)
- **Functions & Methods**: `snake_case` (e.g., `def update_pid_gains(...)`)
- **Variables & Attributes**: `snake_case` (e.g., `current_altitude_m`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ROLL_LIMIT_DEG = 30.0`)
- **Units in Variable Names**: Always append physical units to variables representing physical quantities (e.g., `_rad`, `_deg`, `_m_s`, `_m_s2`, `_kg`, `_sec`).

### C++ Subsystems (Flight Controller, Sim Engine)
Follow standard ROS 2 / C++ conventions:
- **Classes & Types**: `PascalCase` (e.g., `class ComplementaryFilter;`)
- **Functions & Methods**: `camelCase` (e.g., `void resetIntegrator();`)
- **Local Variables**: `snake_case` (e.g., `double accel_magnitude;`)
- **Member Variables**: `snake_case` prefixed with `m_` (e.g., `double m_kp;`)
- **Constants & Enums**: `UPPER_SNAKE_CASE` (e.g., `const double GRAVITY_M_S2 = 9.80665;`)

### ROS 2 Interface Topics & Services
- Topics must be structured hierachically and written in `snake_case`:
  - `/voyager/sim/sensor/imu` (raw simulator output)
  - `/voyager/fc/state/attitude` (fusion output)
  - `/voyager/fc/command/motors` (mixer output)

---

## 2. Code Formatting

### Python
- Use **`black`** formatter.
- Maximum line length: **88 characters** (Black default) or **100 characters** for configuration files.
- Indentation: **4 spaces**.

### C++
- Use **`clang-format`** with the configuration base rules matching the ROS 2 coding style guidelines (derived from Google C++ style).
- Indentation: **4 spaces** (never use hard tabs).
- Bracing: All control statements (`if`, `for`, `while`) must use braces even for single-line blocks.

---

## 3. Safety-Critical Firmware Constraints (Voyager FC)

Flight controller software is real-time and safety-critical. The following constraints apply to all C++ code in `voyager-fc`:

### I. Zero Dynamic Memory Allocation (RT Loops)
- No calls to `malloc()`, `free()`, `new`, or `delete` are allowed inside the main flight execution loop (state estimation, control loops, motor mixing).
- Avoid standard library containers that dynamically allocate (e.g., `std::vector`, `std::string`, `std::map`) in real-time loops.
- Use static allocations, fixed-size arrays (`std::array`), or pre-allocated object pools initialized at startup.

### II. Numerical Stability & Safeguards
- **Zero-Division Check**: Always check denominators before executing divisions. If a divisor is close to zero (e.g., $|dt| < 10^{-6}$), bypass the operation, log an error, and use a safe fallback.
- **Saturation Limits**: All PID outputs, actuator commands, and integrator states must have hard saturation limits (clamps) to prevent runaway accumulation or actuator overloading.
- **Finite Value Checks**: Ensure sensor values and controller states are valid numbers (`std::isfinite`). If `NaN` or `Inf` is detected, trigger the flight failsafe immediately.

### III. Execution Determinism
- Code inside the real-time thread must run at a fixed rate (e.g., 400Hz or 1000Hz).
- Blocking operations (such as disk I/O, network sockets, console logging, or locks) are strictly prohibited in the real-time flight thread. Offload these tasks to asynchronous low-priority threads.

---

## 4. Testing Frameworks & Coverage

All Voyager repositories must maintain high test coverage:

### Python Testing
- Framework: **`pytest`**
- Command: `pytest tests/`
- Every utility function, mathematical transformation, and parser must have comprehensive unit tests.

### C++ Testing
- Framework: **`Google Test (gtest)`** & **`Google Mock (gmock)`**
- Unit tests must mock peripheral hardware registers to test low-level drivers.

### Simulation-in-the-Loop Tests
- Integration tests must run automatically in `Voyager Sim` using a script.
- A typical test script must command a takeoff, track a box-pattern waypoint path, and verify that the drone lands safely within 0.5 meters of the landing target without crashing.

---

## 5. Documentation Standards

### API Documentation
- **Python**: Write Google-style docstrings for all modules, classes, and public functions:
  ```python
  def update(self, error: float, dt: float) -> float:
      """Calculates the control output based on error and time delta.

      Args:
          error: The current error value (desired - actual).
          dt: The elapsed time in seconds since the last update.

      Returns:
          The saturated control output.
      """
  ```
- **C++**: Write Doxygen-compatible comments:
  ```cpp
  /**
   * @brief Updates the complementary filter state.
   * @param accel Accel vector in m/s^2.
   * @param gyro Gyro vector in rad/s.
   * @param dt Time delta in seconds.
   */
  void updateFilter(const Vector3d& accel, const Vector3d& gyro, double dt);
  ```

### Algorithm Explanations
- Implementations of mathematical models (like quaternions, RK4 integration, Kalman filters) must reference the corresponding section in the `Theory/` documentation directory. Include markdown links in headers or inline comments.
