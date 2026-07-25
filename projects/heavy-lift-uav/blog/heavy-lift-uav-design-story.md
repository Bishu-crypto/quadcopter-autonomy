# Sizing a 34kg Hybrid Hexacopter from First Principles: My Design Story for DronIQ Labs

When we think of multirotors, we usually think of consumer photography drones weighing a couple of kilograms, or perhaps racing quads carrying small action cameras. Designing a drone that can carry a 10 kg cargo payload over a 30 km radius (60 km total out-and-back distance) with a 20-minute loiter on station at full payload is a completely different engineering challenge. This represents roughly two hours of total flight endurance under high loading. It is a problem that pushes the limits of battery energy density, requiring a transition to a gas-electric hybrid powerplant. 

As part of the DronIQ Labs technical assessment, I set out to design this heavy-lift hexacopter from first principles. Here is the story of how the design was sized, calculated, and optimized, including a few surprises and bugs along the way.

## Hexacopter Topology and Propeller Trades

The first design decision was topology. While an octocopter provides structural symmetry and motor redundancy, the dry weight penalty of two additional motor mounts, ESCs, and arm extensions would significantly degrade range. A quadcopter, on the other hand, puts too much thrust burden on each motor and has zero control redundancy in the event of a rotor failure. A standard single-motor hexacopter (6 arms spaced at 60-degree increments) was the optimal configuration.

The baseline recommendation was 36-inch propellers. However, I wanted to see if pushing the propeller diameter to the 40-inch limit would yield significant efficiency gains. Using a custom Blade Element Momentum (BEM) solver, I evaluated both options. The BEM analysis showed that the 40-inch propeller (with a 13-inch pitch, radius of 0.508 m) operated with a 19.1% improvement in hover efficiency (8.1 g/W hover efficiency versus 6.8 g/W). 

At the nominal takeoff weight of the aircraft, the 40-inch propeller reduced the hover power requirement by over 400 watts (from 2,477W down to 2,050W). Running at a lower 1,850 RPM also significantly reduces profile drag, drive-train stress, and acoustic noise. The major tradeoff was arm length: to maintain a safe 104 mm tip-to-tip clearance between adjacent 40" propellers without any aerodynamic overlap, the arm length had to stretch to 1.12 m, resulting in a motor-to-motor diagonal diameter of 2.24 m.

## Solving the Sizing Loop

One of the most common pitfalls in conceptual aircraft design is relying on single-pass estimates. In a heavy-lift cargo drone, mass, thrust, power, and fuel are circularly dependent. If the airframe is heavier, it requires more thrust to hover. More thrust demands more electrical power, which increases fuel consumption from the hybrid generator, requiring a larger fuel tank and more fuel mass, which adds weight back onto the takeoff weight.

To solve this circular dependency, I wrote a 5-iteration convergence loop using fixed-point iteration. It started with an initial Take-Off Weight (TOW) guess of 35.78 kg and dynamically calculated hover thrust, power draw, and mission fuel burn across a 4-phase mission profile (climb, cruise out, loiter, cruise back). 

![Take-Off Weight Convergence](../reports/figures/endurance_simulation.png)

By the fifth iteration, the Take-Off Weight converged to exactly 34.575 kg, with the fuel mass converging to 2.323 kg (which includes a 20% safety reserve over the 1.859 kg consumed during the mission). A single-pass calculation would have under-predicted the required takeoff weight by almost 1.9 kg, showing just how critical coupled iteration is for securing structural and energy safety margins.

![Mass Budget Breakdown](../reports/figures/mass_budget_pie.png)

## The Structural Surprise

With 1.12-meter arms, structural rigidity and bending stress are major design drivers. The arms are designed as hollow carbon fiber tubes with a 30 mm outer diameter and a 2 mm wall thickness ($\text{UTS} = 800\text{ MPa}$, $E = 120\text{ GPa}$). My initial assumption was that the symmetric 2.5G limit load case would govern the arm sizing, as it represents the highest total vertical lift force (848.4 N total, or 141.3 N per arm).

However, running the asymmetric motor-out emergency recovery case (under 1.5G maneuver load) revealed a different reality. If one motor fails, the remaining active rotors must spool up to balance the rolling and pitching moments of the aircraft. Because of this moment-compensation logic, the load concentrates onto fewer arms. The active arms adjacent to the failed rotor must carry a peak force of 169.6 N—which is 20% higher than the per-arm load under the symmetric 2.5G case.

![Structural Stress and Deflection](../reports/figures/arm_structural_fea.png)

The failure case governed the design, producing a root bending moment of 189.9 N-m and a peak root bending stress of 164.4 MPa. This resulted in a safety factor of 4.87, easily passing the required aerospace safety margin of 1.5. This structural surprise reinforced a key lesson: in safety-critical systems, emergency failure states, rather than nominal high-G limits, frequently dictate structural sizing.

## The Overlapping Propeller Bug

No engineering project is complete without a debugging story. In an early version of the CAD geometry generator, I noticed that the 3D model rendered with the 40-inch propellers overlapping in the center. 

The bug was simple but honest: the script was placing the newly selected 40-inch propellers on the arm lengths calculated during the 36-inch propeller phase. Since I had hardcoded the arm length baseline in the CAD assembly script rather than linking it dynamically to the propeller sizing trade study, the adjacent propeller tips were physically colliding in the assembly. 

To fix this, I refactored the design configuration parameters so that the arm length was derived directly from the selected propeller radius plus the required 104 mm clearance margin. Checking the tip-to-tip clearance variables after the fix confirmed that the clearance was exactly 10.2% of the propeller diameter, preventing any blade collision.

## Future Improvements

If I had more time to iterate on this design, three areas would be my priority:
1. **Weight Optimization:** A structural safety factor of 4.87 is very conservative. By running an optimization loop on the carbon fiber tube wall thickness (perhaps reducing it to 1.5 mm or optimizing the fiber layup angle), we could trim dry weight and convert that directly into payload capacity or fuel.
2. **Aeroelastic Validation:** The BEM solver is a useful conceptual design tool, but it doesn't capture rotor-rotor wake interactions or blade flexibility. I would validate the propeller aerodynamic polars against QBlade or full CFD.
3. **Rotor-Rotor Interference:** With a diagonal diameter of 2.24 m, aerodynamic interactions between adjacent rotors can create local turbulence and efficiency losses. Modeling this wake interaction would yield a more precise hover power estimate.

***

*Find the complete design files, simulation scripts, and CAD models in the [GitHub Repository](https://github.com/Bishu-crypto/quadcopter-autonomy/tree/main/projects/heavy-lift-uav) and read the full technical document in the [PDF Report](../reports/heavy_lift_uav_design_report.pdf).*
