# Heavy-Lift UAV Design Calculation Walkthrough

This document serves as a step-by-step teaching guide for the analytical sizing, propulsion, energy, and structural calculations of the heavy-lift hybrid hexacopter project. It is structured to help you understand the physical principles, governing equations, and exact numbers used to establish the converged design baseline.

---

## 1. Configuration Selection Trade-offs

### The Physical Question
Why is a standard single-motor hexacopter (6 arms) selected over a quadcopter (4 arms) or an octocopter/X8 (8 arms)?

### The Engineering Trade-off Logic
1. **Quadcopter vs. Hexacopter**:
   - *Quadcopter*: While a quadcopter is simpler and lighter, it lacks motor redundancy. If any single motor, electronic speed controller (ESC), or propeller fails, a quadcopter loses control instantly and crashes. For a commercial UAV carrying a costly 10 kg payload and high-end sensors, this risk is unacceptable.
   - *Hexacopter*: A hexacopter has 6 rotors. Under a single-rotor failure, the flight control system can dynamically adjust the thrust of the remaining 5 active rotors to balance pitch, roll, and yaw moments, enabling a controlled emergency recovery landing.
2. **Octocopter/X8 vs. Hexacopter**:
   - *Octocopter/X8*: While an octocopter provides even greater lift and redundancy, it requires 8 propulsion sets. This significantly increases:
     - **Dry Weight**: Higher motor, ESC, wiring, and structural arm mass.
     - **Power Cabling Losses**: Extra wiring complexity increases resistive heat losses.
     - **Coaxial Efficiency Penalty**: X8 layouts mount rotors coaxially (top/bottom pairs). The lower rotor operates in the high-velocity downwash of the upper rotor, losing 10% to 15% of its aerodynamic efficiency.
   - *Hexacopter*: By using a single-motor-per-arm layout, the hexacopter avoids coaxial flow interference, maximizing rotor efficiency. It represents the optimal engineering "sweet spot"—achieving true motor-out failsafe safety with the lowest possible dry mass and complexity.

---

## 2. Mass Budget Summation

### The Physical Question
What is the total mass of the aircraft, and how is it distributed among the various subsystems?

### Governing Equation & Theory
The Total Takeoff Weight ($TOW$) is the simple arithmetic sum of the masses ($m_i$) of all individual onboard components:

$$TOW = \sum_{i} m_i$$

For design organization, the component masses are grouped into five primary subsystems:
1. **Payload ($m_{\text{payload}}$)**: The cargo package and camera gimbal.
2. **Power System ($m_{\text{power}}$)**: The hybrid generator, dry fuel tank, buffer battery, and gasoline.
3. **Frame ($m_{\text{frame}}$)**: The center core plates, landing gear struts, and 6 carbon arms.
4. **Propulsion ($m_{\text{propulsion}}$)**: The 6 motor-ESC-propeller groups and wiring harness.
5. **Avionics ($m_{\text{avionics}}$)**: The flight controller, companion computer, telemetry, and FPV links.

### Actual Numbers Plugged In
Summing the individual component masses:
* **Payload**:
  * Payload Package = $10.000\text{ kg}$
  * *Subtotal* = $10.000\text{ kg}$
* **Power System**:
  * Hybrid Generator (Dry) = $4.500\text{ kg}$
  * Fuel Tank (Dry) = $0.500\text{ kg}$
  * Buffer Battery (12S LiPo) = $1.500\text{ kg}$
  * Gasoline Fuel (Carried) = $2.323\text{ kg}$
  * *Subtotal* = $8.823\text{ kg}$
* **Frame**:
  * Center Plates & Core Frame = $2.200\text{ kg}$
  * Landing Gear Assembly = $1.200\text{ kg}$
  * Carbon Arms = $6 \times 0.392\text{ kg/arm} = 2.352\text{ kg}$ *(each arm is a 1.12m carbon tube)*
  * *Subtotal* = $5.752\text{ kg}$
* **Propulsion**:
  * Rotor Groups = $6 \times 1.450\text{ kg/group} = 8.700\text{ kg}$ *(each group is 1.050kg Motor + 0.150kg ESC + 0.250kg Propeller)*
  * Wiring Loom = $0.500\text{ kg}$
  * *Subtotal* = $9.200\text{ kg}$
* **Avionics & Comms**:
  * Flight Controller & GPS = $0.150\text{ kg}$
  * RF Telemetry & Antennas = $0.250\text{ kg}$
  * FPV Camera = $0.100\text{ kg}$
  * Companion Computer = $0.300\text{ kg}$
  * *Subtotal* = $0.800\text{ kg}$

$$TOW = 10.000 + (4.500 + 0.500 + 1.500 + 2.323) + (2.200 + 1.200 + 2.352) + (8.700 + 0.500) + (0.150 + 0.250 + 0.100 + 0.300)$$

$$TOW = 10.000 + 8.823 + 5.752 + 9.200 + 0.800$$

$$TOW = 34.575\text{ kg}$$

### Final Result & Downstream Impact
The total Takeoff Weight is **34.575 kg** (corresponding to a dry vehicle mass of **22.252 kg** when excluding the 10 kg payload and 2.323 kg fuel). This total mass determines the downward gravitational force that the rotors must overcome to hover, which directly drives the required motor thrust calculations.

---

## 3. Thrust-to-Weight Sizing & Redundancy Check

### The Physical Question
How much thrust must the propulsion system produce to meet the maneuverability target under normal operation, and what thrust is required per motor to maintain hover during an emergency motor failure?

### Governing Equation & Theory
1. **Total Peak Thrust Target**:
   To ensure the aircraft can climb rapidly and resist heavy wind gusts, the propulsion system is sized for a Thrust-to-Weight ratio ($T/W$) of **2.6**:
   
   $$T_{\text{peak}} = TOW \times g \times (T/W)$$
   
   where $g = 9.81\text{ m/s}^2$ is the acceleration due to gravity.
   
2. **Peak Thrust per Motor (Normal)**:
   Under normal operation, all 6 rotors share the peak thrust demand equally:
   
   $$T_{\text{motor, normal}} = \frac{T_{\text{peak}}}{6}$$

3. **Required Thrust per Motor (Motor-Out emergency hover)**:
   When one motor fails on a hexacopter, the flight controller must reduce the thrust of the opposite motor to maintain pitch and roll moment equilibrium. This leaves effectively $N_{\text{active, eff}} = 3.0$ load-bearing arms to carry the vertical weight. For a safe emergency recovery at $1.5\text{G}$ load factor, the required thrust per active motor is:
   
   $$T_{\text{motor, emergency}} = \frac{TOW \times g \times 1.5}{3.0}$$

### Actual Numbers Plugged In
* **Gravitational Weight ($W$)**:
  $$W = 34.575\text{ kg} \times 9.81\text{ m/s}^2 = 339.181\text{ N}$$
* **Total Peak Thrust Target ($T_{\text{peak}}$)**:
  $$T_{\text{peak}} = 339.181\text{ N} \times 2.6 = 881.870\text{ N}$$
* **Peak Thrust per Motor (Normal)**:
  $$T_{\text{motor, normal}} = \frac{881.870\text{ N}}{6} = 146.978\text{ N}$$
* **Emergency Thrust per Motor (Motor-Out recovery)**:
  $$T_{\text{motor, emergency}} = \frac{339.181\text{ N} \times 1.5}{3.0} = 169.590\text{ N}$$

### Final Result & Downstream Impact
The peak normal thrust per motor is **146.978 N** (~15.0 kg), while the emergency motor-out thrust is **169.590 N** (~17.3 kg). Because the emergency motor-out condition requires a higher thrust per motor than the peak normal hover condition, the selected motor (T-Motor U15 II KV100) must be rated to supply at least **169.6 N** of thrust.

---

## 4. Hover Power Derivation

### The Physical Question
How much electrical power must the power plant supply to keep the 34.575 kg hexacopter hovering?

### Governing Equation & Theory
1. **Propeller Disk Area ($A$)**:
   The swept disk area of a single propeller with diameter $D_{\text{prop}}$ (in meters) is:
   
   $$A = \pi \left(\frac{D_{\text{prop}}}{2}\right)^2$$

2. **Ideal Induced Velocity ($v_i$)**:
   From Actuator Disk / Momentum Theory, the ideal velocity at which air is accelerated through the rotor disk in hover is:
   
   $$v_i = \sqrt{\frac{T_{\text{hover, rotor}}}{2 \rho A}}$$
   
   where $\rho = 1.225\text{ kg/m}^3$ is air density at sea level, and $T_{\text{hover, rotor}} = \frac{TOW \times g}{6}$ is the hover thrust per motor.

3. **Ideal Aerodynamic Power ($P_{\text{ideal}}$)**:
   $$P_{\text{ideal}} = T_{\text{hover, rotor}} \times v_i$$

4. **Actual Aerodynamic Mechanical Power ($P_{\text{mech, aero}}$)**:
   Corrected for aerodynamic losses using the propeller's Figure of Merit ($FoM$):
   
   $$P_{\text{mech, aero}} = \frac{P_{\text{ideal}}}{FoM}$$

5. **Total Rotor Mechanical Power ($P_{\text{mech, rotor}}$)**:
   Includes profile power losses (blade skin friction) modeled as an additional 15% override:
   
   $$P_{\text{mech, rotor}} = 1.15 \times P_{\text{mech, aero}}$$

6. **Motor Electrical Power ($P_{\text{elec}}$)**:
   Solves the electrical voltage and current of the T-Motor U15 II KV100 using its internal resistance ($R_m$), idle current ($I_0$), and torque constant ($K_t = \frac{60}{2\pi \times KV}$):
   - Angular Velocity: $\omega = \text{RPM} \times \frac{2\pi}{60}$
   - Torque: $Q = \frac{P_{\text{mech, rotor}}}{\omega}$
   - Motor Current: $I = \frac{Q}{K_t} + I_0$
   - Back EMF Voltage: $E_{\text{EMF}} = \frac{\text{RPM}}{KV}$
   - Terminal Voltage: $V = I \times R_m + E_{\text{EMF}}$
   - Electrical Power: $P_{\text{elec}} = V \times I$

7. **Total Aircraft Electrical Power ($P_{\text{elec, total}}$)**:
   $$P_{\text{elec, total}} = 6 \times P_{\text{elec}} + P_{\text{avionics}}$$
   
   where $P_{\text{avionics}} = 150.0\text{ W}$ is the constant draw for flight avionics and the onboard computer.

### Actual Numbers Plugged In
* **Propeller Disk Area ($A$)**:
  $$D_{\text{prop}} = 40\text{ inches} = 1.016\text{ m}$$
  $$A = \pi \left(\frac{1.016}{2}\right)^2 = 0.81073\text{ m}^2$$
* **Hover Thrust per Rotor ($T_{\text{hover, rotor}}$)**:
  $$T_{\text{hover, rotor}} = \frac{34.575\text{ kg} \times 9.81\text{ m/s}^2}{6} = 56.530\text{ N}$$
* **Induced Velocity ($v_i$)**:
  $$v_i = \sqrt{\frac{56.530\text{ N}}{2 \times 1.225\text{ kg/m}^3 \times 0.81073\text{ m}^2}} = \sqrt{28.4601} = 5.3348\text{ m/s}$$
* **Ideal Aerodynamic Power ($P_{\text{ideal}}$)**:
  $$P_{\text{ideal}} = 56.530\text{ N} \times 5.3348\text{ m/s} = 301.577\text{ W}$$
* **Mechanical Aerodynamic Power ($P_{\text{mech, aero}}$)**:
  *Using $FoM = 0.70$ (representing the default baseline used in the convergence loop)*:
  $$P_{\text{mech, aero}} = \frac{301.577\text{ W}}{0.70} = 430.824\text{ W}$$
* **Total Rotor Mechanical Power ($P_{\text{mech, rotor}}$)**:
  $$P_{\text{mech, rotor}} = 430.824\text{ W} \times 1.15 = 495.448\text{ W}$$
* **Motor State Solve (T-Motor U15 II KV100)**:
  - $KV = 100\text{ RPM/V}$, $R_m = 0.017\ \Omega$, $I_0 = 2.0\text{ A}$.
  - Torque constant: $K_t = \frac{60}{2\pi \times 100} = 0.09549\text{ N-m/A}$.
  - Hover RPM = $2363\text{ RPM}$.
  - Angular Velocity: $\omega = 2363 \times \frac{2\pi}{60} = 247.453\text{ rad/s}$.
  - Torque: $Q = \frac{495.448\text{ W}}{247.453\text{ rad/s}} = 2.0022\text{ N-m}$.
  - Current: $I = \frac{2.0022}{0.09549} + 2.0 = 22.967\text{ A}$.
  - Back EMF: $E_{\text{EMF}} = \frac{2363}{100} = 23.630\text{ V}$.
  - Terminal Voltage: $V = 22.967 \times 0.017 + 23.630 = 24.020\text{ V}$.
  - Electrical Power per motor: $P_{\text{elec}} = 24.020\text{ V} \times 22.967\text{ A} = 551.675\text{ W}$ *(Motor Efficiency $\eta_{\text{motor}} = 89.81\%$)*
* **Total Aircraft Electrical Power ($P_{\text{elec, total}}$)**:
  $$P_{\text{elec, total}} = 6 \times 551.675\text{ W} + 150.0\text{ W} = 3310.05\text{ W} + 150.0\text{ W} = 3460.05\text{ W}$$

### Final Result & Downstream Impact
The hover electrical power is **3,460.1 W**. This sets the minimum continuous power rating that the hybrid power plant must deliver to support steady flight.

---

## 5. Battery Sizing vs. Hybrid Decision

### The Physical Question
Why is a pure battery system unfeasible, and why does a gasoline-hybrid system make this mission possible?

### Governing Equation & Theory
1. **Total Mission Energy Required ($E_{\text{required}}$)**:
   $$E_{\text{required}} = P_{\text{avg}} \times t_{\text{mission}}$$
   
   where $P_{\text{avg}} \approx 3260\text{ W}$ is the average power draw, and $t_{\text{mission}} = 104\text{ min} = 1.733\text{ hours}$ is the mission duration.

2. **Carried Energy (with 20% Reserve Margin)**:
   $$E_{\text{carried}} = \frac{E_{\text{required}}}{0.8}$$

3. **Required Battery Mass ($m_{\text{battery}}$)**:
   $$m_{\text{battery}} = \frac{E_{\text{carried}}}{e_{\text{battery}}}$$
   
   where $e_{\text{battery}} = 250\text{ Wh/kg}$ is the usable energy density at the battery pack level.

### Actual Numbers Plugged In
* **Total Energy**:
  $$E_{\text{required}} = 3260\text{ W} \times 1.733\text{ hours} = 5650.7\text{ Wh} = 5.651\text{ kWh}$$
* **Carried Energy**:
  $$E_{\text{carried}} = \frac{5650.7\text{ Wh}}{0.8} = 7063.4\text{ Wh}$$
* **Required Battery Mass**:
  $$m_{\text{battery}} = \frac{7063.4\text{ Wh}}{250\text{ Wh/kg}} = 28.254\text{ kg}$$

### Final Result & Downstream Impact
If powered purely by batteries, the battery pack alone would weigh **28.254 kg**. Adding this to the dry vehicle mass ($22.252\text{ kg}$) and payload ($10.0\text{ kg}$) would result in a takeoff weight of **60.5 kg**. This increased weight would require double the hover power, forcing a massive, non-converging weight spiral. 

By using gasoline fuel (which has a combustion energy density of $12,000\text{ Wh/kg}$), even at $20\%$ generator thermal efficiency, the net system specific energy is $2,400\text{ Wh/kg}$. The power system (dry generator + fuel + buffer battery) weighs only **8.823 kg**, making the mission highly feasible.

---

## 6. Cruise Power & Mission Energy Budget

### The Physical Question
How much power does the aircraft draw in forward cruise, and what is the breakdown of fuel consumption across the four phases of the 30 km out-and-back mission?

### Governing Equation & Theory
1. **Cruise Aerodynamic Drag ($D$)**:
   $$D = \frac{1}{2} \rho V^2 C_d A_{\text{front}}$$
   
   where cruise speed $V = 12.0\text{ m/s}$, drag coefficient $C_d = 1.2$, and frontal area $A_{\text{front}} = 0.35\text{ m}^2$.
2. **Required Flight Thrust ($T_{\text{cruise}}$)**:
   $$T_{\text{cruise}} = \sqrt{W^2 + D^2}$$
3. **Mechanical and Electrical Cruise Power**:
   Calculated using forward flight momentum theory to account for:
   - Induced power: $T_{\text{cruise}} \times v_{i,\text{cruise}}$
   - Profile power: $15\%$ of static hover aerodynamic power.
   - Parasitic drag power: $D \times V$
4. **Fuel Consumption Rate ($\dot{m}_{\text{fuel}}$)**:
   $$\dot{m}_{\text{fuel}} = SFC \times P_{\text{elec}}$$
   
   where $SFC = 0.42\text{ kg/kWh} = 1.16667 \times 10^{-7}\text{ kg/J}$ is the generator's Specific Fuel Consumption.

### Actual Numbers Plugged In
* **Aerodynamic Drag at 12 m/s**:
  $$D = 0.5 \times 1.225\text{ kg/m}^3 \times (12.0\text{ m/s})^2 \times 1.2 \times 0.35\text{ m}^2 = 37.044\text{ N}$$
* **Required Cruise Thrust**:
  $$T_{\text{cruise}} = \sqrt{339.181^2 + 37.044^2} = 341.198\text{ N}$$
* **Cruise Electrical Power**:
  Solving forward flight momentum equations yields a total cruise electrical power of **2,433.8 W**.
* **Phase Fuel Consumptions**:
  * **Phase 1: Vertical Climb** (100 m rise at 2.5 m/s):
    - Duration = $40\text{ s}$
    - Power = $3580\text{ W}$
    - Fuel Burned = $1.16667 \times 10^{-7}\text{ kg/J} \times 3580\text{ W} \times 40\text{ s} = 0.01941\text{ kg}$
  * **Phase 2: Cruise Out** (30 km at 12 m/s):
    - Duration = $2500\text{ s}$ ($41.7\text{ min}$)
    - Average Power = $2402\text{ W}$ *(decreases slightly as fuel burns off)*
    - Fuel Burned = $1.16667 \times 10^{-7}\text{ kg/J} \times 2402\text{ W} \times 2500\text{ s} = 0.70057\text{ kg}$
  * **Phase 3: On-Station Loiter** (20 min hover):
    - Duration = $1200\text{ s}$
    - Average Power = $3331\text{ W}$
    - Fuel Burned = $1.16667 \times 10^{-7}\text{ kg/J} \times 3331\text{ W} \times 1200\text{ s} = 0.46638\text{ kg}$
  * **Phase 4: Cruise Back** (30 km at 12 m/s):
    - Duration = $2500\text{ s}$ ($41.7\text{ min}$)
    - Average Power = $2305\text{ W}$ *(aircraft is lighter due to burned fuel)*
    - Fuel Burned = $1.16667 \times 10^{-7}\text{ kg/J} \times 2305\text{ W} \times 2500\text{ s} = 0.67222\text{ kg}$
* **Total Mission Fuel Consumed**:
  $$m_{\text{consumed}} = 0.01941 + 0.70057 + 0.46638 + 0.67222 = 1.859\text{ kg}$$
* **Fuel Capacity Sized with 20% Reserve Margin**:
  $$m_{\text{carried}} = \frac{1.859\text{ kg}}{0.8} = 2.323\text{ kg}$$

### Final Result & Downstream Impact
The total mission fuel consumption is **1.859 kg**, requiring a fuel tank capacity of at least **2.323 kg**. This carried fuel weight is added to the takeoff mass, closing the design loop.

---

## 7. Hybrid Genset and Buffer Battery Sizing

### The Physical Question
How are the continuous output power of the generator and the capacity of the buffer battery chosen?

### Governing Equation & Theory
1. **Generator Continuous Power**:
   Must exceed the steady hover electrical power:
   
   $$P_{\text{generator}} \ge P_{\text{hover}}$$
   
2. **Generator Mass Sizing**:
   Determined by its specific power density $p_{\text{generator}} = 800\text{ W/kg}$:
   
   $$m_{\text{generator}} = \frac{P_{\text{generator}}}{p_{\text{generator}}}$$

3. **Buffer Battery Capacity Sizing**:
   The battery acts as a safety buffer. It must store enough energy to sustain hover for $t_{\text{emergency}} = 5\text{ minutes}$ ($0.0833\text{ hours}$) in the event of a generator engine failure:
   
   $$E_{\text{buffer}} = P_{\text{hover}} \times t_{\text{emergency}}$$

### Actual Numbers Plugged In
* **Generator Power Sizing**:
  Hover power is $3460\text{ W}$. A **3.6 kW** ($3600\text{ W}$) continuous output generator is selected to provide a safety margin.
* **Generator Dry Mass**:
  $$m_{\text{generator}} = \frac{3600\text{ W}}{800\text{ W/kg}} = 4.50\text{ kg}$$
* **Buffer Battery Energy Capacity**:
  $$E_{\text{buffer}} = 3460\text{ W} \times \left(\frac{5}{60}\text{ hours}\right) = 288.33\text{ Wh}$$
  Using high-discharge LiPo battery cells with a pack specific energy of $200\text{ Wh/kg}$, the required battery weight is:
  $$m_{\text{battery}} = \frac{288.33\text{ Wh}}{200\text{ Wh/kg}} = 1.44\text{ kg} \approx 1.50\text{ kg}$$

### Final Result & Downstream Impact
The power plant is sized with a **3.6 kW generator (dry mass 4.50 kg)** and a **300 Wh buffer battery (mass 1.50 kg)**. This ensures continuous cruise capability and provides a 5-minute emergency glide/landing buffer.

---

## 8. TOW Convergence Loop Iteration

### The Physical Question
Why is an iterative loop needed to find the takeoff weight, and how do the values converge?

### The Iteration Logic
Takeoff weight dictates the required motor thrust, which determines power draw, which dictates the rate of fuel consumption, which determines the fuel weight needed for the mission, which increases the takeoff weight. Because of this circular dependency, the mass budget must be solved iteratively until the Takeoff Weight (TOW) value stabilizes.

### Convergence Table (5 passes)
Starting from an initial guess of $4.200\text{ kg}$ of fuel:

| Iteration | TOW ($kg$) | Hover Power ($W$) | Mission Fuel Burn ($kg$) | Req. Fuel w/ Reserve ($kg$) | Delta TOW ($kg$) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 36.452 | 3,718.4 | 1.985 | 2.482 | 36.452 |
| **2** | 34.734 | 3,481.7 | 1.869 | 2.336 | 1.718 |
| **3** | 34.588 | 3,461.9 | 1.859 | 2.324 | 0.145 |
| **4** | 34.576 | 3,460.2 | 1.859 | 2.323 | 0.012 |
| **5** | **34.575** | **3,460.1** | **1.859** | **2.323** | **0.001** |

### Final Result & Downstream Impact
The mass budget converges in 5 iterations to a stable Takeoff Weight of **34.575 kg** carrying **2.323 kg of fuel**. This converged weight is the mathematical baseline for all downstream structural stress calculations.

---

## 9. Structural Bending Moments and Stress Calculations

### The Physical Question
What are the bending moments and stresses on the carbon fiber arms under vertical acceleration and motor failure, and which load case dictates the arm thickness?

### Governing Equation & Theory
1. **Area Moment of Inertia of the Hollow Arm Tube ($I$)**:
   $$I = \frac{\pi}{64} \left(D_o^4 - D_i^4\right)$$
   
   where outer diameter $D_o = 30\text{ mm} = 0.03\text{ m}$, and inner diameter $D_i = D_o - 2t = 26\text{ mm} = 0.026\text{ m}$ (for wall thickness $t = 2\text{ mm}$).
2. **Root Bending Moment ($M$)**:
   $$\text{Bending Moment } M = F_{\text{arm}} \times L$$
   
   where $F_{\text{arm}}$ is the vertical force at the arm tip, and $L = 1.12\text{ m}$ is the arm length.
3. **Peak Bending Stress ($\sigma$)**:
   $$\sigma = \frac{M \times y}{I} = \frac{M \times \left(D_o / 2\right)}{I}$$
4. **Safety Factor ($SF$)**:
   $$SF = \frac{\text{UTS}}{\sigma}$$
   
   where $\text{UTS} = 800\text{ MPa}$ is the Ultimate Tensile Strength of the carbon fiber tube.

### Load Cases Sizing & Numbers Plugged In
* **Area Moment of Inertia ($I$)**:
  $$I = \frac{\pi}{64} \left(0.030^4 - 0.026^4\right) = 1.7329 \times 10^{-8}\text{ m}^4$$

* **Load Case 1 (Symmetric 2.5G Limit Maneuver)**:
  All 6 arms share the 2.5G vertical lift force:
  $$F_{\text{arm}} = \frac{34.575\text{ kg} \times 9.81\text{ m/s}^2 \times 2.5}{6} = 141.325\text{ N}$$
  $$M = 141.325\text{ N} \times 1.12\text{ m} = 158.284\text{ N-m}$$
  $$\sigma = \frac{158.284\text{ N-m} \times 0.015\text{ m}}{1.7329 \times 10^{-8}\text{ m}^4} = 137.01\text{ MPa}$$
  $$SF = \frac{800\text{ MPa}}{137.01\text{ MPa}} = 5.84$$

* **Load Case 2 (Asymmetric Motor-Out 1.5G Recovery)**:
  Under motor failure, moment balance concentrates the 1.5G vertical recovery lift force on effectively only 3 active arms:
  $$F_{\text{arm}} = \frac{34.575\text{ kg} \times 9.81\text{ m/s}^2 \times 1.5}{3.0} = 169.590\text{ N}$$
  $$M = 169.590\text{ N} \times 1.12\text{ m} = 189.941\text{ N-m}$$
  $$\sigma = \frac{189.941\text{ N-m} \times 0.015\text{ m}}{1.7329 \times 10^{-8}\text{ m}^4} = 164.41\text{ MPa}$$
  $$SF = \frac{800\text{ MPa}}{164.41\text{ MPa}} = 4.87$$

### Final Result & Downstream Impact
The asymmetric motor-out case produces a higher bending stress (**164.4 MPa**) than the symmetric 2.5G limit load case (**137.0 MPa**). Consequently, **Case 2 governs the design**. The resulting safety factor is **4.87**, which exceeds the minimum required aerospace safety margin of **1.5**.

---

## 10. Propeller/Arm Length Geometry

### The Physical Question
Why is the arm length chosen to be exactly 1.12 m, and how does this guarantee clearance between adjacent propeller blades?

### Governing Geometry & Theory
On a standard hexacopter, there are 6 arms spaced at $60^\circ$ radial increments. Connecting the tips of two adjacent arms of length $L$ to the center of the frame forms a triangle. Because the angle at the center vertex is exactly $60^\circ$, and the two arm lengths are equal ($L$), the other two angles must also be:

$$\frac{180^\circ - 60^\circ}{2} = 60^\circ$$

This makes it an **equilateral triangle**. Consequently, the linear tip-to-tip distance ($d$) between adjacent motor shafts is exactly equal to the arm length:

$$d = L$$

To prevent the blades of adjacent propellers from colliding, the distance between the motor shafts must exceed the propeller diameter ($D_{\text{prop}}$). The tip-to-tip blade clearance ($C$) is:

$$C = L - D_{\text{prop}}$$

### Actual Numbers Plugged In
* Propeller Diameter: $40\text{ inches} = 1.016\text{ m}$
* Arm Length: $L = 1.120\text{ m}$
* Blade Clearance ($C$):
  $$C = 1.120\text{ m} - 1.016\text{ m} = 0.104\text{ m} = 104\text{ mm}$$
* Clearance Margin:
  $$\text{Margin} = \frac{0.104\text{ m}}{1.016\text{ m}} \times 100\% = 10.2\%$$

### Final Result & Downstream Impact
Sizing the arms to **1.12 m** provides a blade tip-to-tip clearance of **104 mm** (a 10.2% clearance margin). This guarantees that there is zero physical propeller overlap, preventing aerodynamic interference, high vibration, and physical blade strikes.
