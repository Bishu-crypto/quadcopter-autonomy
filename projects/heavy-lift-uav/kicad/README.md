# KiCad Power & Signal Schematic Verification Guide

This directory contains the formal electrical schematic for the **Heavy-Lift Gas-Electric Hybrid Hexacopter** (`power_and_signal_schematic.kicad_sch`) conforming strictly to `DESIGN_LOCK.md`.

---

## 1. Schematic Overview & Electrical Architecture

### Application to Use
Open `power_and_signal_schematic.kicad_sch` in **KiCad** (v6.0, v7.0, or v8.0 Eeschema).

### Subsystems Included

1. **Power Path**:
   - **Hybrid Generator System:** 3.6 kW 2-stroke generator feeding a 3-phase rectifier and 48V DC buck-boost regulator (`48V_BUS, MAX 75A`).
   - **Buffer Battery Coupling:** 12S LiPo buffer battery (44.4V - 50.4V) tied in parallel via an Ideal Diode / BMS Failsafe Controller (`BAT_BUS, MAX 100A PEAK`).
   - **Power Distribution Board (PDB):** 48V main DC bus supplying 6 ESC branch outputs.
   - **6x ESC & Motor Branches:** T-Motor Flame 120A ESCs driving T-Motor U15 II KV100 motors.
   - **Auxiliary Regulators:** 48V-to-12V (10A) and 48V-to-5V (10A) DC-DC converters for flight avionics and payload.

2. **Signal & Control Path**:
   - **Flight Controller (Pixhawk 6X):** Outputs 6x PWM/DShot signals (`PWM_1` to `PWM_6`) to ESCs.
   - **Avionics Interfaces:** Dual Neo-3 GPS/RTK modules, 915 MHz RF Telemetry Radio (1W output), FPV Camera/Gimbal control, and Ethernet MAVLink link to Jetson Orin Nano companion computer.
   - **Generator Telemetry:** CAN Bus connection (`CAN1_H/L`) between Generator ECU, BMS, and Pixhawk.

---

## 2. Wire Current Rating Calculations (Cross-Checked against DESIGN_LOCK.md)

- **Total Hover Electrical Power:** $P_{\text{hover}} = \mathbf{3,361.1\text{ W}}$
- **Nominal System Bus Voltage:** $V_{\text{bus}} = \mathbf{48.0\text{ V}}$ (12S nominal configuration)

### Wire Current Ratings
1. **Main 48V DC Bus (Generator Output to PDB):**
   $$I_{\text{hover, total}} = \frac{3,361.1\text{ W}}{48.0\text{ V}} = \mathbf{70.03\text{ A}}$$
   *Max Generator Output Rating:* $3,600\text{ W} / 48.0\text{ V} = \mathbf{75.0\text{ A}}$ max continuous (Wire gauge: 8 AWG / 6 AWG).

2. **ESC / Motor Branch Wires (PDB to 6x ESCs):**
   $$I_{\text{hover, per branch}} = \frac{70.03\text{ A}}{6} = \mathbf{11.67\text{ A hover}}$$
   *Peak Emergency Rating per ESC:* $\approx 60.0\text{ A}$ maneuver peak ($120\text{ A}$ rated ESC, Wire gauge: 12 AWG per ESC).

3. **Buffer Battery Failsafe Connection:**
   *Peak Emergency Discharge Rating:* $\mathbf{100.0\text{ A}}$ peak for 5-minute emergency land buffer (Wire gauge: 8 AWG).

---

## 3. What You Will See in KiCad Eeschema

Upon opening `power_and_signal_schematic.kicad_sch` in KiCad:
1. **Title Block:** Displays title, date, revision, and comment blocks citing `DESIGN_LOCK.md` metrics (3,361.1W hover power, 70.0A total current, 11.67A per ESC branch).
2. **Main Power Section:** Clear visual layout of the 3.6 kW Hybrid Generator -> Rectifier -> PDB -> 6x ESC branch lines labeled with exact hover and peak current ratings.
3. **Signal Section:** Complete wiring hierarchy connecting Pixhawk 6X, GPS/RTK, Telemetry, Jetson Orin Nano, and CAN bus telemetry.
