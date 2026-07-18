# Contributing to Voyager

Welcome to Voyager! As a contributor, you are expected to treat the project like a professional-grade aerospace software repository. Please review the guidelines below before making changes.

---

## 1. Documentation-First Workflow

Before writing any new feature or rewriting existing logic:
1. Ensure the relevant theoretical notes in `docs/Theory/` are updated or created.
2. Update `docs/Architecture.md` if the module boundaries, topic names, or interface structures are affected.
3. For major design selections, write an **Architecture Decision Record (ADR)** under `docs/ADR/` (using standard lightweight ADR format).
4. Review the overall objectives in `docs/Vision.md` and `docs/Roadmap.md`.

---

## 2. Coding Standards

All submissions must follow the rules set in **[CodingStandards.md](./CodingStandards.md)**. Key rules:
- **C++ Subsystems**: Strict formatting using `clang-format`. Zero dynamic allocations in the real-time flight loops. Check denominators to prevent division-by-zero.
- **Python Subsystems**: Format code with `black`. Maximum line length of 88 characters.
- **Variable Units**: Always suffix physical variables with their unit of measurement (e.g., `rate_pitch_rad_s`, `accel_z_m_s2`).

---

## 3. Pull Request & Commit Guidelines

- **Commit Messages**: Write clear, descriptive, imperative commit messages (e.g., `feat(sim): add aerodynamic blade element force integration`, `fix(fc): clamp derivative term in attitude rate PID`).
- **Branch Naming**: Use a prefix indicating branch type followed by a short description:
  - `feat/feature-name`
  - `fix/bug-description`
  - `docs/doc-update`
  - `refactor/subsystem-name`
- **Testing**: A PR will not be merged unless it includes:
  - Appropriate unit tests (e.g., via `pytest` or `gtest`).
  - Validation passing in `modules/voyager-sim/` (SITL).
  - Clean linting/formatting checks.
