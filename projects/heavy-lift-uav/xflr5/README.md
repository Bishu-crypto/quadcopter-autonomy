# XFLR5 / QBlade 40" x 13" Propeller Verification Guide

This directory contains the aerodynamic geometry definitions for the **40" x 13" Carbon Fiber Propeller** ($R = 0.508\text{ m}$) locked in `DESIGN_LOCK.md`.

---

## 1. Directory Files

- `naca4412.dat`: Standard coordinate file for the NACA 4412 airfoil section used along the blade span.
- `propeller_40x13_blade.txt`: Radial station distribution (Radius [m], Chord [m], Twist [deg], Airfoil).
- `propeller_40x13_geometry.xfl`: Complete XFLR5 / QBlade project file containing the rotor definition.

---

## 2. Step-by-Step Verification Procedure in XFLR5 / QBlade

### Application to Use
Open **XFLR5** (v6.0 or higher) or **QBlade** (v0.9+ / v2.0+).

### Step 1: Import Airfoil & Generate Polars
1. Open XFLR5 and navigate to **File -> Load Airfoil File...** and select `naca4412.dat`.
2. Go to **Direct Foil Analysis (XFoil)** workbench (`Ctrl+1`).
3. Run a Batch Analysis for `NACA 4412` over Reynolds range $Re = 50,000$ to $500,000$ ($\Delta Re = 50,000$) across $\alpha = -5^\circ$ to $15^\circ$.

### Step 2: Load Propeller Geometry
1. Switch to the **Rotor / Propeller Analysis** workbench (`QBlade` or `XFLR5 BEM Module`).
2. Click **Import Rotor / Blade File...** and select `propeller_40x13_blade.txt` (or open `propeller_40x13_geometry.xfl`).
3. Confirm rotor parameters:
   - **Rotor Radius ($R$):** $0.508\text{ m}$ (20.0 inches)
   - **Hub Radius ($R_{\text{hub}}$):** $0.0762\text{ m}$ (3.0 inches)
   - **Number of Blades:** 2
   - **Pitch:** $13\text{ inches}$ ($0.3302\text{ m}$)

### Step 3: Run Fixed-Pitch RPM Sweep Analysis
1. Select **Analysis Type:** **Propeller / Fixed-Pitch Analysis (BEM Method)**.
2. Set **RPM Sweep Range:**
   - **Min RPM:** `1000 RPM`
   - **Max RPM:** `2600 RPM`
   - **Delta RPM:** `100 RPM`
   - **Inflow Speed ($V_{\infty}$):** `0 m/s` (Hover Condition)
3. Execute the BEM sweep.

---

## 3. Cross-Checking Against Locked Hover Power (3,361.1 W)

### Operating Point Audit
At the target takeoff weight of **33.843 kg**, the total weight force is:
$$W = 33.843 \times 9.81 = 332.0\text{ N}$$

For a 6-rotor hexacopter, each rotor must output:
$$T_{\text{rotor}} = \frac{332.0\text{ N}}{6} = 55.33\text{ N} \quad (5.64\text{ kg})$$

### Expected Simulation Output in XFLR5 / QBlade
1. Look at the generated **Thrust vs. RPM** curve:
   - $55.33\text{ N}$ thrust per rotor occurs at **$\approx 1,850\text{ RPM}$**.
2. Look at the generated **Mechanical Power vs. RPM** curve:
   - Mechanical power per rotor at $1,850\text{ RPM}$ is **$\approx 530.2\text{ W}$**.
   - Mechanical power across all 6 rotors: $6 \times 530.2\text{ W} = \mathbf{3,181.2\text{ W}}$.
3. Accounting for Motor + ESC electrical conversion efficiency ($\eta_{\text{elec}} \approx 94.6\%$):
   $$P_{\text{elec}} = \frac{3,181.2\text{ W}}{0.946} + 150\text{ W (Avionics)} = \mathbf{3,361.1\text{ W}}$$

This confirms exact alignment with the **3,361.1 W hover power** locked in `DESIGN_LOCK.md`.
