# Heavy-Lift UAV Design Lock & Baseline Reference

> **CRITICAL ARCHITECTURAL DIRECTIVE**  
> This file records the official, locked design baseline for the heavy-lift UAV project as of July 2026.  
> It serves as the single source of truth for the codebase. **Before making ANY future change to the codebase, check this file first and confirm the proposed change is consistent with it.**  
> If a future request contradicts this baseline, flag it explicitly to the user before making modifications.

---

## 1. Aircraft Topology & Configuration

- **Configuration:** Standard Single-Motor Hexacopter
- **Arm Layout:** 6 arms at 60-degree radial increments ($0^\circ, 60^\circ, 120^\circ, 180^\circ, 240^\circ, 300^\circ$)
- **Arm Length ($L$):** **1.12 m** ($1120\text{ mm}$)
  - *Geometric Clearance:* Distance between adjacent arm tips equals arm length ($d = L = 1.120\text{ m}$). With 40" props ($D_{\text{prop}} = 1.016\text{ m}$), adjacent blade tip-to-tip clearance is $1.120 - 1.016 = \mathbf{0.104\text{ m}} = 104\text{ mm}$ (10.2% clearance margin, **ZERO OVERLAP**).
  - *Motor-to-Motor Diagonal Diameter:* **2.24 m** ($2240\text{ mm}$)
- **Propulsion Allocation:** Exactly 1 motor + 1 ESC + 1 propeller per arm (**6 motors total**)
- **Payload Cargo Bay Geometry (CAD Baseline):**
  - Dimensions: $300\text{ mm} \times 200\text{ mm} \times 150\text{ mm}$ (placeholder cargo box representing 10 kg payload capacity).
  - Mounting Position: Centered below bottom plate at $[0.0, 0.0, -0.150]\text{ m}$.
- **Camera & Gimbal Geometry (CAD Baseline):**
  - Assembly: Electro-Optical (EO) Camera + 2-Axis Gimbal housing ($70 \times 70 \times 70\text{ mm}$ housing with lens sphere).
  - Mounting Position: Front underside of center frame at $[0.180, 0.0, -0.125]\text{ m}$.
  - *Ground & Component Clearance:* $450\text{ mm}$ landing gear struts provide $220\text{ mm}$ vertical ground clearance below the payload bay and camera. **ZERO COMPONENT COLLISION**.
- **Explicit Exclusions:** NOT coaxial, NOT X8, NOT quadcopter, NOT octocopter. No robotic arm or manipulator geometry; static cargo housing and camera gimbal only.

---

## 2. Rotor & Propeller Specifications

- **Propeller Sizing:** 40" x 13" Carbon Fiber ($R = 0.508\text{ m} = 508\text{ mm}$)
- **Disk Area per Rotor:** $0.8107\text{ m}^2$ (Total Disk Area = $4.864\text{ m}^2$)
- **Hover Figure of Merit (FoM):** $0.72$ ($8.1\text{ g/W}$ hover efficiency at nominal operating point)

---

## 3. Converged System Baseline (5-Iteration TOW Loop)

*Verified via dynamic mass-power-fuel convergence loop (`run_tow_convergence` in `mass_budget.py`)*

- **Total Takeoff Weight (TOW):** `34.575 kg`
- **Hover Electrical Power Draw:** `3,460.1 W`
- **Payload Capacity:** `10.000 kg`
- **Dry Vehicle Mass (excl. fuel & payload):** `22.252 kg` (Arm tube mass = 0.392 kg/arm for 1.12m carbon tube)
- **Operational Mission Profile:** Climb (100m) + Cruise Out (30 km @ 12 m/s) + On-Station Loiter (20 min hover) + Cruise Back (30 km @ 12 m/s)
- **Mission Fuel Consumed:** `1.859 kg`
- **Carried Fuel Mass (with 20% Reserve Margin):** `2.323 kg`
- **Center of Gravity (CG):** `[-0.0000, -0.0006, -0.0533] m` (relative to central frame reference)
- **Inertia Tensor ($I_{CG}$):**
  - $I_{xx} = 6.187\text{ kg-m}^2$
  - $I_{yy} = 6.168\text{ kg-m}^2$
  - $I_{zz} = 11.670\text{ kg-m}^2$

---

## 4. Structural & FEA Load Case Baseline

- **Arm Specifications:** Carbon Fiber Tube, 30 mm Outer Diameter, 2 mm Wall Thickness, **1.12 m Length** ($\text{UTS} = 800\text{ MPa}$, $E = 120\text{ GPa}$)
- **Governing Load Case:** **ASYMMETRIC MOTOR-OUT (1.5G Emergency Recovery)**
  - *Rationale:* Moment balance under motor failure concentrates higher force ($169.6\text{ N}$) on active arms adjacent to the failed rotor compared to symmetric distribution.
  - **Governing Root Bending Moment:** $189.9\text{ N-m}$ ($M = F \times L = 169.6\text{ N} \times 1.12\text{ m}$)
  - **Governing Peak Bending Stress:** $164.4\text{ MPa}$
  - **Governing Safety Factor:** **SF = 4.87** (PASSED $\ge 1.5$ requirement)
- **Secondary Non-Governing Load Case:** **Symmetric 2.5G Limit Load**
  - Peak Force per Arm: $141.3\text{ N}$
  - Root Bending Moment: $158.3\text{ N-m}$
  - Peak Bending Stress: $137.0\text{ MPa}$
  - Safety Factor: $\text{SF} = 5.84$

---

## 5. Verified Codebase Artifacts

The following scripts and modules are confirmed 100% consistent with this locked baseline:

1. `projects/heavy-lift-uav/design_calculations/mass_budget.py`
2. `projects/heavy-lift-uav/design_calculations/propulsion.py`
3. `projects/heavy-lift-uav/design_calculations/power_endurance.py`
4. `projects/heavy-lift-uav/design_calculations/structural_analysis.py`
5. `projects/heavy-lift-uav/simulation/rotor_bem.py`
6. `projects/heavy-lift-uav/simulation/generate_cad_model.py`
7. `projects/heavy-lift-uav/generate_report.py`

---

## 6. Maintenance & Enforcement Rules

- **Do NOT** recalculate, revert, or regenerate baseline values unless explicitly instructed by the user to perform a design trade study.
- **Do NOT** re-introduce coaxial, X8, or 4-arm logic into any calculation script or visualization pipeline.
- If a future prompt requests changes that contradict any parameter in this document, cross-check against `DESIGN_LOCK.md` first and flag the conflict explicitly to the user before taking action.
