# CAD Model Validation Report

Generated programmatically using FreeCAD and `trimesh` verification suite.

## 1. Solid Geometry Validity (Per Part)

| Part Name | Category | Valid? | Shape Type | Faces | Solids | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| Arm_Clamp_1 | Arm Clamps | PASS | Compound | 13 | 1 | None |
| Arm_Clamp_2 | Arm Clamps | PASS | Compound | 13 | 1 | None |
| Arm_Clamp_3 | Arm Clamps | PASS | Compound | 13 | 1 | None |
| Arm_Clamp_4 | Arm Clamps | PASS | Compound | 13 | 1 | None |
| Arm_Clamp_5 | Arm Clamps | PASS | Compound | 13 | 1 | None |
| Arm_Clamp_6 | Arm Clamps | PASS | Compound | 13 | 1 | None |
| Battery_Pack_12S_6307_2Wh | Battery Pack | PASS | Solid | 6 | 1 | None |
| Carbon_Arm_1_0deg | Arm Tubes | PASS | Compound | 4 | 1 | None |
| Carbon_Arm_2_60deg | Arm Tubes | PASS | Compound | 4 | 1 | None |
| Carbon_Arm_3_120deg | Arm Tubes | PASS | Compound | 4 | 1 | None |
| Carbon_Arm_4_180deg | Arm Tubes | PASS | Compound | 4 | 1 | None |
| Carbon_Arm_5_240deg | Arm Tubes | PASS | Compound | 4 | 1 | None |
| Carbon_Arm_6_300deg | Arm Tubes | PASS | Compound | 4 | 1 | None |
| Center_Plate_Bottom | Center Plates | PASS | Compound | 37 | 1 | None |
| Center_Plate_Top | Center Plates | PASS | Compound | 37 | 1 | None |
| Landing_Leg_1 | Landing Legs | PASS | Solid | 3 | 1 | None |
| Landing_Leg_2 | Landing Legs | PASS | Solid | 3 | 1 | None |
| Landing_Leg_3 | Landing Legs | PASS | Solid | 3 | 1 | None |
| Landing_Leg_4 | Landing Legs | PASS | Solid | 3 | 1 | None |
| Motor_Mount_Plate_1 | Motor Mount Plates | PASS | Compound | 15 | 1 | None |
| Motor_Mount_Plate_2 | Motor Mount Plates | PASS | Compound | 15 | 1 | None |
| Motor_Mount_Plate_3 | Motor Mount Plates | PASS | Compound | 15 | 1 | None |
| Motor_Mount_Plate_4 | Motor Mount Plates | PASS | Compound | 15 | 1 | None |
| Motor_Mount_Plate_5 | Motor Mount Plates | PASS | Compound | 15 | 1 | None |
| Motor_Mount_Plate_6 | Motor Mount Plates | PASS | Compound | 15 | 1 | None |
| Propeller_40in_2Blade_1 | Propellers | PASS | Compound | 17 | 3 | None |
| Propeller_40in_2Blade_2 | Propellers | PASS | Compound | 17 | 3 | None |
| Propeller_40in_2Blade_3 | Propellers | PASS | Compound | 17 | 3 | None |
| Propeller_40in_2Blade_4 | Propellers | PASS | Compound | 17 | 3 | None |
| Propeller_40in_2Blade_5 | Propellers | PASS | Compound | 17 | 3 | None |
| Propeller_40in_2Blade_6 | Propellers | PASS | Compound | 17 | 3 | None |
| Skid_Foot_Pad_1 | Skid Pads | PASS | Compound | 12 | 1 | None |
| Skid_Foot_Pad_2 | Skid Pads | PASS | Compound | 12 | 1 | None |
| Skid_Foot_Pad_3 | Skid Pads | PASS | Compound | 12 | 1 | None |
| Skid_Foot_Pad_4 | Skid Pads | PASS | Compound | 12 | 1 | None |

## 2. Inter-Part Interference / Collision Check

| Part 1 | Part 2 | Intersection Vol ($mm^3$) | Clearance Distance ($mm$) | Intersects? |
| --- | --- | --- | --- | --- |
| Battery_Pack_12S_6307_2Wh | Arm_Clamp_1 | 0.00000 | 50.00000 | NO |
| Battery_Pack_12S_6307_2Wh | Arm_Clamp_2 | 0.00000 | 18.29612 | NO |
| Battery_Pack_12S_6307_2Wh | Arm_Clamp_3 | 0.00000 | 18.29612 | NO |
| Battery_Pack_12S_6307_2Wh | Arm_Clamp_4 | 0.00000 | 50.00000 | NO |
| Battery_Pack_12S_6307_2Wh | Arm_Clamp_5 | 0.00000 | 18.29612 | NO |
| Battery_Pack_12S_6307_2Wh | Arm_Clamp_6 | 0.00000 | 18.29612 | NO |
| Battery_Pack_12S_6307_2Wh | Carbon_Arm_1_0deg | 0.00000 | 60.00000 | NO |
| Battery_Pack_12S_6307_2Wh | Carbon_Arm_2_60deg | 0.00000 | 29.72432 | NO |
| Battery_Pack_12S_6307_2Wh | Carbon_Arm_3_120deg | 0.00000 | 29.72432 | NO |
| Battery_Pack_12S_6307_2Wh | Carbon_Arm_4_180deg | 0.00000 | 60.00000 | NO |
| Battery_Pack_12S_6307_2Wh | Carbon_Arm_5_240deg | 0.00000 | 29.72432 | NO |
| Battery_Pack_12S_6307_2Wh | Carbon_Arm_6_300deg | 0.00000 | 29.72432 | NO |
| Arm_Clamp_1 | Center_Plate_Top | 0.00000 | 20.00000 | NO |
| Arm_Clamp_1 | Center_Plate_Bottom | 0.00000 | 20.00000 | NO |
| Arm_Clamp_2 | Center_Plate_Top | 0.00000 | 20.00000 | NO |
| Arm_Clamp_2 | Center_Plate_Bottom | 0.00000 | 20.00000 | NO |
| Arm_Clamp_3 | Center_Plate_Top | 0.00000 | 20.00000 | NO |
| Arm_Clamp_3 | Center_Plate_Bottom | 0.00000 | 20.00000 | NO |
| Arm_Clamp_4 | Center_Plate_Top | 0.00000 | 20.00000 | NO |
| Arm_Clamp_4 | Center_Plate_Bottom | 0.00000 | 20.00000 | NO |
| Arm_Clamp_5 | Center_Plate_Top | 0.00000 | 20.00000 | NO |
| Arm_Clamp_5 | Center_Plate_Bottom | 0.00000 | 20.00000 | NO |
| Arm_Clamp_6 | Center_Plate_Top | 0.00000 | 20.00000 | NO |
| Arm_Clamp_6 | Center_Plate_Bottom | 0.00000 | 20.00000 | NO |
| Motor_Mount_Plate_1 | Carbon_Arm_1_0deg | 0.00000 | 0.00000 | NO |
| Motor_Mount_Plate_1 | Carbon_Arm_2_60deg | 0.00000 | 0.00000 | NO |
| Motor_Mount_Plate_1 | Carbon_Arm_3_120deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_1 | Carbon_Arm_4_180deg | 0.00000 | 1250.00000 | NO |
| Motor_Mount_Plate_1 | Carbon_Arm_5_240deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_1 | Carbon_Arm_6_300deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_2 | Carbon_Arm_1_0deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_2 | Carbon_Arm_2_60deg | 0.00000 | 0.00000 | NO |
| Motor_Mount_Plate_2 | Carbon_Arm_3_120deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_2 | Carbon_Arm_4_180deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_2 | Carbon_Arm_5_240deg | 0.00000 | 1250.00000 | NO |
| Motor_Mount_Plate_2 | Carbon_Arm_6_300deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_3 | Carbon_Arm_1_0deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_3 | Carbon_Arm_2_60deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_3 | Carbon_Arm_3_120deg | 0.00000 | 0.00000 | NO |
| Motor_Mount_Plate_3 | Carbon_Arm_4_180deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_3 | Carbon_Arm_5_240deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_3 | Carbon_Arm_6_300deg | 0.00000 | 1250.00000 | NO |
| Motor_Mount_Plate_4 | Carbon_Arm_1_0deg | 0.00000 | 1250.00000 | NO |
| Motor_Mount_Plate_4 | Carbon_Arm_2_60deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_4 | Carbon_Arm_3_120deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_4 | Carbon_Arm_4_180deg | 0.00000 | 0.00000 | NO |
| Motor_Mount_Plate_4 | Carbon_Arm_5_240deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_4 | Carbon_Arm_6_300deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_5 | Carbon_Arm_1_0deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_5 | Carbon_Arm_2_60deg | 0.00000 | 1250.00000 | NO |
| Motor_Mount_Plate_5 | Carbon_Arm_3_120deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_5 | Carbon_Arm_4_180deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_5 | Carbon_Arm_5_240deg | 0.00000 | 0.00000 | NO |
| Motor_Mount_Plate_5 | Carbon_Arm_6_300deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_6 | Carbon_Arm_1_0deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_6 | Carbon_Arm_2_60deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_6 | Carbon_Arm_3_120deg | 0.00000 | 1250.00000 | NO |
| Motor_Mount_Plate_6 | Carbon_Arm_4_180deg | 0.00000 | 1158.57900 | NO |
| Motor_Mount_Plate_6 | Carbon_Arm_5_240deg | 0.00000 | 903.35815 | NO |
| Motor_Mount_Plate_6 | Carbon_Arm_6_300deg | 0.00000 | 0.00000 | NO |
| Landing_Leg_1 | Skid_Foot_Pad_1 | 628.31853 | 0.00000 | YES |
| Landing_Leg_1 | Skid_Foot_Pad_2 | 0.00000 | 160.41631 | NO |
| Landing_Leg_1 | Skid_Foot_Pad_3 | 0.00000 | 274.66655 | NO |
| Landing_Leg_1 | Skid_Foot_Pad_4 | 0.00000 | 210.41631 | NO |
| Landing_Leg_2 | Skid_Foot_Pad_1 | 0.00000 | 160.41631 | NO |
| Landing_Leg_2 | Skid_Foot_Pad_2 | 628.31853 | 0.00000 | YES |
| Landing_Leg_2 | Skid_Foot_Pad_3 | 0.00000 | 210.41631 | NO |
| Landing_Leg_2 | Skid_Foot_Pad_4 | 0.00000 | 274.66655 | NO |
| Landing_Leg_3 | Skid_Foot_Pad_1 | 0.00000 | 274.66655 | NO |
| Landing_Leg_3 | Skid_Foot_Pad_2 | 0.00000 | 210.41631 | NO |
| Landing_Leg_3 | Skid_Foot_Pad_3 | 628.31853 | 0.00000 | YES |
| Landing_Leg_3 | Skid_Foot_Pad_4 | 0.00000 | 160.41631 | NO |
| Landing_Leg_4 | Skid_Foot_Pad_1 | 0.00000 | 210.41631 | NO |
| Landing_Leg_4 | Skid_Foot_Pad_2 | 0.00000 | 274.66655 | NO |
| Landing_Leg_4 | Skid_Foot_Pad_3 | 0.00000 | 160.41631 | NO |
| Landing_Leg_4 | Skid_Foot_Pad_4 | 628.31853 | 0.00000 | YES |

## 3. Unit / Scale Sanity Check

- **Overall Bounding Box Dimensions (mm)**:
  - **X**: 2320.0000 mm (Range: [-1160.0000, 1160.0000])
  - **Y**: 2458.2892 mm (Range: [-1229.1446, 1229.1446])
  - **Z**: 677.0000 mm (Range: [-502.0000, 175.0000])
- **Overall Span (including Propellers)**: 2458.2892 mm (~2.458 m)
- **Motor-to-Motor Span (excluding Propellers)**: 2320.0000 mm (~2.320 m)

## 4. Mesh Validation (Post-STL-Export)

| STL File | Watertight? | Winding Consistent? | Triangles | Vertices | Non-Manifold Edges | Open Boundary Edges | Degenerate Faces |
| --- | --- | --- | --- | --- | --- | --- | --- |
| arm_clamp.stl | YES | YES | 682 | 333 | 0 | 0 | 0 |
| center_plate.stl | YES | YES | 2536 | 1256 | 0 | 0 | 0 |
| motor_mount_plate.stl | YES | YES | 688 | 336 | 0 | 0 | 0 |
| skid_foot_pad.stl | YES | YES | 300 | 152 | 0 | 0 | 0 |
| test_export.stl | NO | YES | 91 | 136 | 0 | 209 | 0 |

## 5. Slicer-Equivalent Check

> [!IMPORTANT]
> No CLI Slicer (like `prusa-slicer` or `slic3r`) is pre-installed in this environment, and passwordless `sudo` is unavailable to install one. Therefore, the **Slicer-Equivalent Check** could not be performed headlessly and must be run manually by the user.

## 6. Summary Table (Print-Ready Status)

| Part Name | Solid Valid? | Interference-Free? | Mesh Watertight? | Triangle Count | Print-Ready? | Issues Found |
| --- | --- | --- | --- | --- | --- | --- |
| center_plate.stl | PASS | PASS | PASS | 2536 | YES | None |
| arm_clamp.stl | PASS | PASS | PASS | 682 | YES | None |
| motor_mount_plate.stl | PASS | PASS | PASS | 688 | YES | None |
| skid_foot_pad.stl | PASS | FAIL | PASS | 300 | NO | Interference: Intersects Landing_Leg_1 |
