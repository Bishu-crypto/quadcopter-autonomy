# 🛩️ Propeller Aerodynamics: XFLR5 & QBlade Sizing Rebuild

This directory contains the aerodynamic geometry definitions and simulation inputs for the heavy-lift hexacopter's **40" × 13" Carbon Fiber Propeller**. These files are reconstructed from first principles to validate thrust-to-power curves and hover efficiency matching the converged design baseline in [`DESIGN_LOCK.md`](../DESIGN_LOCK.md).

---

## 📂 Directory Contents

| File | Type | Description |
| :--- | :--- | :--- |
| [`naca4412.dat`](naca4412.dat) | Airfoil Coordinates | 2D coordinate points defining the NACA 4412 profile. |
| [`propeller_40x13_blade.txt`](propeller_40x13_blade.txt) | Blade Geometry | 10 radial stations detailing radius, chord, and twist distribution. |
| [`propeller_40x13_qblade.bld`](propeller_40x13_qblade.bld) | QBlade Blade File | Native QBlade blade description format. |
| [`propeller_40x13_aerodyn.dat`](propeller_40x13_aerodyn.dat) | AeroDyn Input File | AeroDyn v13 compatible blade definition for BEM solver. |
| [`propeller_40x13_geometry.xfl`](propeller_40x13_geometry.xfl) | XFLR5 Project | Pre-loaded NACA 4412 airfoil geometry and polar analysis workspace. |

---

## 🔬 Tool Capabilities & Limitations: XFLR5 vs. QBlade

To understand the aerodynamics of multirotor propellers, we must apply the correct tools within their physical and mathematical boundaries:

### 1. XFLR5 (Static Airfoil & Fixed-Wing Analysis)
* **What it is:** XFLR5 is a tool designed for 2D airfoil analysis (using XFOIL) and 3D analysis of static wings and full aircraft configurations (using Vortex Lattice Method, Lifting Line Theory, and 3D Panel Methods).
* **Limitations:** **XFLR5 does not support rotating rotors or propellers.** It cannot simulate rotational velocity fields, centrifugal forces, or blade-element momentum theory for rotating blades. The project file `propeller_40x13_geometry.xfl` is therefore used **strictly to run 2D airfoil polar sweeps (NACA 4412)** at appropriate Reynolds numbers ($100\text{k} - 500\text{k}$) to generate lift ($C_l$) and drag ($C_d$) data.
* **Role in Project:** Generates the input drag polars for the blade elements.

### 2. QBlade (Rotational BEM & Wind Turbine/Rotor Solver)
* **What it is:** QBlade is a wind turbine and rotor simulation suite that integrates Blade Element Momentum (BEM) and Lifting Line Theory (LLT) solvers with rotational frames of reference.
* **Role in Project:** Imports the NACA 4412 lift/drag polars and uses the 10 radial blade stations to simulate the rotating propeller in static hover ($0\text{ m/s}$ freestream) and forward flight. It outputs the final thrust ($T$) and mechanical power ($P$) vs. RPM curves.

---

## 🛠️ Step-by-Step Simulation Workflow

Follow these instructions to run the aerodynamic verification in the graphical user interfaces of both tools:

### Part 1: Airfoil Polar Generation in XFLR5
1. Open **XFLR5** (v6.61 or later).
2. Go to **File ➔ Open** and select `xflr5/propeller_40x13_geometry.xfl` (or go to **File ➔ Load Airfoil File** and select `naca4412.dat`).
3. Select the **Direct Foil Design** module.
4. Set up an XFOIL Direct Analysis:
   - Click **Foil ➔ Define an Analysis**.
   - Select **Type 1 (Fixed Reynolds number)**.
   - Run analyses for Reynolds numbers corresponding to the blade span:
     - **Root:** $Re = 100,000$
     - **Mid-span:** $Re = 200,000$
     - **Tip:** $Re = 500,000$
   - Set the angle of attack range: $\alpha = -5^\circ$ to $15^\circ$ with a step of $0.5^\circ$.
5. Click **Analyze** to generate the polars.
6. Export the polar data: Right-click the polar plots and export as text files for import into QBlade.

### Part 2: Rotor BEM Simulation in QBlade
1. Open **QBlade** (v0.96 or later).
2. **Import Airfoil Polars:**
   - Go to **Airfoil ➔ Import Foil** and load the NACA 4412 coordinates (`naca4412.dat`).
   - Import the polar files generated from XFLR5 (or run a built-in XFOIL analysis in QBlade for $Re = 100\text{k}, 200\text{k}, 300\text{k}, 500\text{k}$).
3. **Define the Rotor Blade:**
   - Go to **Rotor ➔ Blade Design ➔ New Blade**.
   - Click **Import** and load `xflr5/propeller_40x13_qblade.bld` (or select **AeroDyn Import** and load `xflr5/propeller_40x13_aerodyn.dat`).
   - Verify the hub radius is set to $0.0762\text{ m}$ and total blade length is $0.508\text{ m}$ (40" propeller diameter).
4. **Run Rotor Simulation (BEM):**
   - Select **Rotor ➔ Rotor Simulation**.
   - Define a new simulation:
     - **Freestream speed:** $V_\infty = 0\text{ m/s}$ (Static Hover Condition).
     - **Air density:** $\rho = 1.225\text{ kg/m}^3$ (Standard Sea Level).
     - **RPM Range:** $1000$ to $2600\text{ RPM}$ with a step of $50\text{ RPM}$.
   - Click **Start Simulation**.
5. **Verify Design Baseline:**
   - Plot **Thrust vs. RPM** and **Mechanical Power vs. RPM**.
   - Check the nominal hover operating point (supporting the **34.575 kg TOW**):
     - Required total thrust: $339.2\text{ N}$ (or **56.5 N per rotor** for the 6-rotor system).
     - Verify that this hover thrust is achieved at **1,850 RPM**.
     - Verify that the mechanical power required per rotor at 1,850 RPM is **547.2 W** (yielding a total mechanical power of **3,283 W** and a hover efficiency of **8.1 g/W**).
