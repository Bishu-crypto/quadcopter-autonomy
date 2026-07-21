# Heavy-Lift Gas-Electric Hybrid Hexacopter UAV Engineering Suite

![Heavy-Lift UAV 360 Turntable](reports/figures/cad_360_turntable.gif)

This directory contains the high-fidelity engineering design, parametric 3D CAD modeling, aerodynamic BEM simulation, structural FEA, and KiCad electrical schematic for a heavy-lift multirotor Unmanned Aerial Vehicle (UAV).

---

## 🎯 Target Specifications & Locked Baseline (`DESIGN_LOCK.md`)

- **Payload Capacity:** 10.0 kg (Safety Orange Cargo Bay Box $300 \times 200 \times 150\text{ mm}$ + EO Camera 2-Axis Gimbal)
- **Configuration:** Single-Motor Hexacopter (6 arms @ $60^\circ$ radial spacing, 1 motor + 1 ESC + 1 prop per arm)
- **Arm Tube Length ($L$):** **1.120 m** (30mm OD $\times$ 2mm wall carbon tube) $\rightarrow$ **104 mm tip-to-tip clearance** (Zero Propeller Overlap)
- **Propellers:** **40" $\times$ 13" Carbon Fiber** ($R = 0.508\text{ m}$, NACA 4412 airfoil section)
- **Total Takeoff Weight (TOW):** **34.575 kg** (Converged via 5-iteration mass-power-fuel loop)
- **Power Plant:** **3.6 kW Gas-Electric Hybrid Generator** (48V DC bus, $3,460.1\text{ W}$ hover electrical power, $72.1\text{ A}$ current draw)
- **Mission Profile:** 30 km out-and-back + 20 min hover loiter ($1.859\text{ kg}$ mission fuel burn, **2.323 kg carried fuel** with 20% reserve margin)
- **Governing Structural Load Case:** Asymmetric Motor-Out Emergency Recovery ($\sigma_{\max} = 164.4\text{ MPa}$, **Safety Factor = 4.87** $\ge 1.5$)

---

## 🎬 How to Present & Show Your 3D CAD Model

When presenting this CAD model to recruiters, professors, or engineering reviewers, use these **4 Key Angles & Technical Nuances**:

| View / Angle | Recommended Image | Key Nuances & Talking Points to Highlight |
| :--- | :--- | :--- |
| **1. Isometric Hero View** ($25^\circ$ elev, $-45^\circ$ azim) | ![Isometric Hero](reports/figures/uav_cad_annotated.png) | **Overall 3D Balance:** Highlights the center plate layout, carbon arms, 10kg cargo bay, camera gimbal, antenna, and skid feet. Explains how payload box centered at $[0, 0, -0.15]\text{ m}$ balances CG. |
| **2. Top-Down Orthographic** ($90^\circ$ top-down) | ![Top View](reports/figures/uav_cad_topview.png) | **Zero Propeller Overlap Proof:** Show that adjacent 40" props ($1.016\text{ m}$ diameter) on $1.12\text{ m}$ arms have **104 mm tip clearance**. Explain why $0.8\text{ m}$ arm length failed ($216\text{ mm}$ overlap) and why $1.12\text{ m}$ solves aerodynamic interference. |
| **3. Side Elevation** ($0^\circ$ elevation) | ![Side View](reports/figures/uav_cad_sideview.png) | **Ground Clearance & Landing Safety:** Shows $450\text{ mm}$ landing gear height and $220\text{ mm}$ payload ground clearance to protect camera and cargo during hard landings (3--5G load case). |
| **4. Subsystem Zoom Details** | ![Motor Detail](reports/figures/uav_cad_motor_detail.png) | **Manufacturing Details:** Points out the 4x M4 bolt pattern (PCD 40mm), two-tier motor housing (stator base vs rotor bell), and tapered propeller blade root interface. |

---

## 📁 Native Engineering File Deliverables

- 📄 **Final 9-Page PDF Engineering Report:** [`reports/heavy_lift_uav_report.pdf`](reports/heavy_lift_uav_report.pdf)
- 📝 **LaTeX Source Code File:** [`reports/heavy_lift_uav_report.tex`](reports/heavy_lift_uav_report.tex)
- 🔒 **Locked Baseline Source of Truth:** [`DESIGN_LOCK.md`](DESIGN_LOCK.md)
- 📐 **Parametric FreeCAD Python Macro:** [`freecad/hexacopter_assembly.py`](freecad/hexacopter_assembly.py)
- 📦 **ISO STEP AP214 3D CAD Assembly:** [`freecad/hexacopter_assembly.step`](freecad/hexacopter_assembly.step)
- 🛩️ **XFLR5 Propeller Aerodynamics Project:** [`xflr5/propeller_40x13_geometry.xfl`](xflr5/propeller_40x13_geometry.xfl)
- ⚡ **KiCad 48V Electrical Distribution Schematic:** [`kicad/power_and_signal_schematic.kicad_sch`](kicad/power_and_signal_schematic.kicad_sch)

---

## 💻 Quick Start & Commands

```bash
# 1. Regenerate 3D CAD images, XFLR5 polars, and KiCad schematic diagrams:
python3 simulation/generate_cad_model.py

# 2. Render 360-degree turntable GIF:
python3 simulation/generate_cad_animation.py

# 3. Compile final LaTeX PDF report:
pdflatex -output-directory=reports reports/heavy_lift_uav_report.tex
```
