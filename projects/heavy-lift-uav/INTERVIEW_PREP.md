# Technical Interview Preparation Guide: Heavy-Lift Multirotor UAV

This guide contains the key engineering justifications, equations, and trade-offs used in this project. Use this to prepare for technical interviews.

---

## 1. Propulsion & Power Plant Trade-Offs

### Q: Why did you choose a Gas-Electric Hybrid over a battery-only system?
*   **The Physics / Core Math:**
    *   Target mission: Carry a **10 kg payload** for **2 hours** (120 minutes).
    *   Total takeoff weight (TOW) is estimated at **33.02 kg**.
    *   Average hover power required is approx. **2,490 W (2.49 kW)**.
    *   Total energy required: $2.49 \text{ kW} \times 2 \text{ hours} \approx 5.0 \text{ kWh}$.
    *   **Li-Ion battery pack density** at the system level is about **200–250 Wh/kg**.
    *   Required battery weight: $\frac{5000 \text{ Wh}}{250 \text{ Wh/kg}} = 20 \text{ kg}$ (and at least 24 kg if we assume 80% DOD for battery health).
    *   Adding the 10 kg payload brings us to 30–34 kg, leaving **zero weight** for the frame, landing gear, ESCs, cabling, and 8 large motors.
*   **The Hybrid Solution:**
    *   Gasoline has an energy density of **12,000 Wh/kg**.
    *   Even at a low thermal-to-electrical conversion efficiency of **18%**, the effective electrical energy density of the gasoline hybrid system is **2,160 Wh/kg** (nearly **10x** that of lithium batteries).
    *   The hybrid system consists of a 4.5 kg generator, 4.2 kg of gasoline (5.5 Liters), and a 1.5 kg buffer battery (for transient peak current and emergency landing). Total weight is only **10.2 kg**, which easily fits the budget and achieves a 122-minute cruise endurance.

---

## 2. Configuration Selection

### Q: Why Coaxial X8 Octocopter over Flat Hexacopter or Flat Octocopter?
1.  **Redundancy (Safety):** Storing a 10 kg payload requires high reliability. In an X8 configuration, if any single motor or ESC fails, the coaxial twin on that arm immediately increases throttle to compensate. The UAV can survive the loss of up to 2 non-adjacent motors and land safely. Quadcopters have zero redundancy, and flat hexacopters have limited recovery envelopes.
2.  **Frame Size and Transportability:** To hover a 33 kg UAV efficiently, large **36-inch propellers** are required.
    *   A flat hexacopter layout would require a motor-to-motor frame diameter of **over 2.5 meters**.
    *   A coaxial X8 stacks 8 propellers on only 4 arms (X configuration), reducing the frame footprint to **1.6 meters**.
3.  **Structural Mass Savings:** Halving the number of arms from 8 to 4 reduces the carbon fiber structural mass by approximately **1.5 kg**, which directly offsets the coaxial aerodynamic efficiency loss.

---

## 3. Rotor Aerodynamics & Coaxial Loss Model

### Q: How did you model the coaxial rotor aerodynamic penalty?
*   **Momentum Theory Analysis:**
    *   In a coaxial pair, the bottom propeller operates in the high-velocity slipstream of the top propeller.
    *   According to actuator disk theory, the top propeller produces an induced velocity at hover:
        $$v_{i,top} = \sqrt{\frac{T}{2 \rho A}}$$
    *   The slipstream contracts and accelerates, reaching a velocity of $v_w = 2 v_{i,top}$ at the plane of the bottom rotor.
    *   The bottom rotor must produce the same thrust $T$, so its induced velocity $v_{i,bot}$ satisfies:
        $$T = 2 \rho A v_{i,bot} (v_{i,bot} + 2 v_{i,top})$$
    *   Solving the quadratic equation yields:
        $$v_{i,bot} = (\sqrt{2} - 1) v_{i,top} \approx 0.414 v_{i,top}$$
    *   The power required by the bottom rotor is:
        $$P_{bot} = T (v_{i,bot} + 2 v_{i,top}) = 2.414 T v_{i,top} = 2.414 P_{top}$$
    *   Total power of the coaxial pair is $P_{coaxial} = P_{top} + P_{bot} = 3.414 P_{top}$.
    *   Two isolated (flat) rotors would require $2 P_{top}$. The coaxial loss factor is:
        $$\frac{3.414 P_{top}}{2 P_{top}} = 1.707 \quad (\approx 15\% \text{ loss in efficiency})$$
    *   This matches standard experimental data showing a 13–18% coaxial penalty.

### Q: How did you model the blade aerodynamics?
*   We implemented a **Blade Element Momentum (BEM) theory** solver. We discretized the 36" propeller blade into 30 radial segments. At each segment, we solved for the local inflow angle ($\phi$) and angle of attack ($\alpha = \theta - \phi$), then integrated lift and drag forces ($dL, dD$) along the radius to get total thrust and torque.

---

## 4. Forward Flight Power (The Bucket Curve)

### Q: Why is cruise power (2,310 W) lower than hover power (2,490 W)?
*   This is due to **Translational Lift**.
*   In hover, the air is stationary, and the rotor must accelerate it from rest (high induced power).
*   In forward flight (cruise at 12 m/s), a large mass flow rate of fresh air passes through the rotor disk. The induced velocity $v_i$ required to produce the same thrust decreases dramatically, solved numerically via:
    $$v_i = \frac{T}{2 \rho A \sqrt{V_\infty^2 + v_i^2}}$$
*   This reduction in induced power offsets the increase in parasitic drag power (fuselage drag: $P_{drag} = \frac{1}{2} \rho V_\infty^3 C_D A_{front}$) up to the **optimum cruise speed** (12 m/s in our design). Beyond 15 m/s, the cubic increase in parasitic drag dominates, and total power rises rapidly. This forms the classic **"Power Bucket Curve"**.

---

## 5. Structural Validation (FEM)

### Q: How did you validate the carbon fiber arms?
*   **Boundary Conditions & Loading:**
    *   The arm is modeled as a cantilever beam (length $L = 0.8 \text{ m}$), clamped at the center plate.
    *   We designed for a **2.5G Limit Load Factor** (aerospace standard).
    *   Force per arm under 2.5G: $F_{arm} = \frac{33.02 \text{ kg} \times 9.81 \times 2.5}{4 \text{ arms}} \approx 202.4 \text{ N}$.
    *   The cross-section is a hollow carbon fiber tube: $D_o = 30 \text{ mm}$, $t = 2.0 \text{ mm}$.
    *   Area moment of inertia: $I = \frac{\pi}{64}(D_o^4 - D_i^4) = 1.706 \times 10^{-8} \text{ m}^4$.
*   **Finite Element Method (FEM) Solver:**
    *   We wrote a 1D Euler-Bernoulli beam FEA solver from scratch. It discretizes the arm into 10 beam elements, assemblies the global stiffness matrix $K_{global}$ using:
        $$K_e = \frac{E I_e}{L_e^3} \begin{bmatrix} 12 & 6 L_e & -12 & 6 L_e \\ 6 L_e & 4 L_e^2 & -6 L_e & 2 L_e^2 \\ -12 & -6 L_e & 12 & -6 L_e \\ 6 L_e & 2 L_e^2 & -6 L_e & 4 L_e^2 \end{bmatrix}$$
    *   Solving $K U = F$ yields a **6.35 mm tip deflection** and **161.6 MPa max root stress**.
    *   Compared to high-strength carbon fiber UTS (**800 MPa**), the safety factor is **4.95** (well above the required 1.5).
