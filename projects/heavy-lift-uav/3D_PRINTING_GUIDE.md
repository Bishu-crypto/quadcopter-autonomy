# 3D Printing & Manufacturing Guide: Heavy-Lift Hexacopter Components

This document outlines the recommended slicing, material, and assembly parameters for the 3D-printable components of the heavy-lift hexacopter.

## 1. Exported 3D-Printable Components

All printable components are generated automatically by the FreeCAD pipeline in `projects/heavy-lift-uav/freecad/3d_printable/`. To facilitate slicing, all components have been:
1. **Centered at the origin `(0, 0)`** in the XY plane.
2. **Shifted in Z** so that the bottom-most flat face rests exactly on the build plate plane (`z = 0`).
3. **Verified as watertight manifold solids** with no self-intersections.

| STL File Name | Component | Primary Material Recommendation | Key Manufacturing Feature |
| :--- | :--- | :--- | :--- |
| `center_plate.stl` | Hexagonal Frame Center Plate | 3.0mm Carbon Fiber CNC Plate (or PA-CF/PETG for prototyping) | 1.0mm CNC-style outer edge chamfer, weight-reduction pockets, center pass-through |
| `arm_clamp.stl` | Sleeve Arm Clamp | Nylon-CF (PA-CF) or PETG | 30.0mm tight arm bore, twin vertical M5 fastener holes, 2.0mm outer corner fillets |
| `motor_mount_plate.stl` | Motor Mount Plate | Nylon-CF (PA-CF) or Polycarbonate (PC) | M4 PCD 40mm motor bolt pattern, 15mm center wiring passage, 8.0mm corner fillets |
| `skid_foot_pad.stl` | Landing Gear Skid Pad | PETG, TPU (for shock absorption), or PA-CF | 20mm blind strut insertion socket, 15.0mm corner fillets |

---

## 2. Slicing & Printing Parameters

### Recommended Materials
1. **Nylon-Carbon Fiber (PA-CF)**: *Highly Recommended for structural parts.* Offers high stiffness, thermal stability, excellent layer adhesion, and exceptional impact resistance. Perfect for **arm clamps** and **motor mount plates**.
2. **PETG**: Excellent budget alternative. More ductile than PLA, good UV/weather resistance, and strong layer adhesion. Good for **skid foot pads** or prototyping clamps.
3. **TPU (95A-98A)**: Optional for **skid foot pads** to provide landing impact shock absorption.

### Slicer Profiles (OrcaSlicer / PrusaSlicer / Bambu Studio)

| Parameter | Structural Parts (Clamps, Mounts) | Non-Structural / Skid Pads |
| :--- | :--- | :--- |
| **Nozzle Temperature** | 280°C - 300°C (PA-CF) / 250°C (PETG) | 250°C (PETG) / 230°C (TPU) |
| **Bed Temperature** | 80°C - 100°C (PA-CF) / 75°C (PETG) | 75°C (PETG) / 50°C (TPU) |
| **Layer Height** | 0.20 mm | 0.20 mm - 0.28 mm |
| **Wall Loops (Perimeters)**| **6 Walls** (critical for fastener hole shear strength) | 3 - 4 Walls |
| **Top/Bottom Shell Layers**| 5 Layers | 4 Layers |
| **Infill Density** | **45% - 50%** | 20% - 30% |
| **Infill Pattern** | **Gyroid** (isotropic strength, no crossing lines) | Gyroid or Grid |
| **Cooling Fan** | 10% - 20% (low cooling increases layer bonding) | 40% - 60% |
| **Support Material** | Tree/Organic Support (if needed; socket bottom) | None |

---

## 3. Post-Processing & Assembly Instructions

1. **Strut Insertion (Skid Foot Pad)**:
   - Ensure the 20mm blind leg socket is clean and free of support remnants.
   - Insert the 20mm OD carbon fiber landing gear strut into the socket. Secure using high-strength epoxy (e.g., DP420) or a retaining M3 cross-bolt.
2. **Fastener Hole Preparation (Arm Clamps & Motor Mounts)**:
   - Bolt holes are printed at nominal dimensions. It is highly recommended to clean them using a drill bit or a hand reamer (5.0mm for M5 clamps, 4.2mm for M4 motor mounts) to ensure clean clearance fits.
   - Use high-strength steel washers under all bolt heads to distribute clamp loads across the carbon fiber and plastic surfaces.
3. **Layer Orientation Warning**:
   - Always print the **Arm Clamps** flat on the bed (X-axis aligned horizontally). This ensures that the clamping shear stresses from tightening the bolts run parallel to the layers, preventing splitting along print lines.
