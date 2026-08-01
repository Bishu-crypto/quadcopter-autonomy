#mass_budeget.py
import numpy as np

class Component:
    def __init__(self, name, category, mass_kg, pos_xyz, desc=""):
        self.name = name
        self.category = category
        self.mass = mass_kg
        self.pos = np.array(pos_xyz, dtype=float) # position relative to frame center [x, y, z] in meters
        self.desc = desc

class MassBudget:
    def __init__(self):
        self.components = []

    def add_component(self, name, category, mass_kg, pos_xyz, desc=""):
        self.components.append(Component(name, category, mass_kg, pos_xyz, desc))

    def get_total_mass(self):
        return sum(c.mass for c in self.components)

    def calculate_cg(self):
        """
        Calculates the Center of Gravity (CG) location [x, y, z] relative to the origin.
        """
        total_mass = self.get_total_mass()
        if total_mass == 0:
            return np.zeros(3)
        weighted_pos = sum(c.mass * c.pos for c in self.components)
        return weighted_pos / total_mass

    def calculate_inertia_tensor(self, cg_pos=None):
        """
        Calculates the 3x3 Moment of Inertia (MOI) tensor (kg-m^2) relative to the CG
        using the parallel axis theorem, treating components as point masses.
        """
        if cg_pos is None:
            cg_pos = self.calculate_cg()
        
        I = np.zeros((3, 3))
        for c in self.components:
            # Position relative to CG
            r = c.pos - cg_pos
            rx, ry, rz = r
            
            # Point mass inertia contribution
            I[0, 0] += c.mass * (ry**2 + rz**2) # Ixx
            I[1, 1] += c.mass * (rx**2 + rz**2) # Iyy
            I[2, 2] += c.mass * (rx**2 + ry**2) # Izz
            
            # Products of inertia
            I[0, 1] -= c.mass * rx * ry # Ixy
            I[1, 0] = I[0, 1]
            I[0, 2] -= c.mass * rx * rz # Ixz
            I[2, 0] = I[0, 2]
            I[1, 2] -= c.mass * ry * rz # Iyz
            I[2, 1] = I[1, 2]
        return I

    def get_category_breakdown(self):
        breakdown = {}
        for c in self.components:
            breakdown[c.category] = breakdown.get(c.category, 0.0) + c.mass
        return breakdown

def build_default_uav_mass_budget(payload_mass=10.0, fuel_mass=12.127, prop_diameter=36, energy_density_wh_kg=520.0):
    mb = MassBudget()
    
    # 1. Payload (centered at the bottom, say z = -0.15m)
    mb.add_component("Payload Package", "Payload", payload_mass, [0.0, 0.0, -0.15], "Camera / Cargo box")
    
    # 2. Power System (Battery-Electric only)
    mb.add_component(f"Main Propulsion Battery Pack ({energy_density_wh_kg:.0f} Wh/kg)", "Power System", fuel_mass, [0.0, 0.0, 0.0], "Main Propulsion Battery")
    
    # 3. Frame & Structural (6 arms configuration, length 0.8m)
    mb.add_component("Center Plates & Core Frame", "Frame", 2.2, [0.0, 0.0, 0.0], "Carbon fiber plates")
    mb.add_component("Landing Gear Assembly", "Frame", 1.2, [0.0, 0.0, -0.4], "Carbon tubes + skids")
    
    arm_mass = 0.392 # per arm (OD 30mm, 2mm wall, 1.12m carbon tube: 0.35 kg/m * 1.12m)
    arm_length = 1.12 # 1.12m arm length provides 104mm clearance for 40" props (1.016m diameter)
    arm_cg_dist = arm_length / 2.0
    
    # 6 arms at 60-degree increments
    angles_deg = [0, 60, 120, 180, 240, 300]
    arm_names = ["Right", "Front-Right", "Front-Left", "Left", "Rear-Left", "Rear-Right"]
    
    for angle_deg, name in zip(angles_deg, arm_names):
        rad = np.radians(angle_deg)
        x_cg = arm_cg_dist * np.cos(rad)
        y_cg = arm_cg_dist * np.sin(rad)
        mb.add_component(f"Carbon Arm {name}", "Frame", arm_mass, [x_cg, y_cg, 0.0], "OD 30mm Tube")
    
    # 4. Propulsion System (6 single motors, 6 ESCs, 6 props at the end of the arms)
    motor_mass = 1.05 # T-Motor U15 II KV100
    esc_mass = 0.08 # Bharath Components 12S ESC
    prop_mass = 0.20 if prop_diameter == 36 else 0.25 # prop weight (0.20kg for 36", 0.25kg for 40")
    rotor_group_mass = motor_mass + esc_mass + prop_mass # Single rotor group
    
    for angle_deg, name in zip(angles_deg, arm_names):
        rad = np.radians(angle_deg)
        x_end = arm_length * np.cos(rad)
        y_end = arm_length * np.sin(rad)
        mb.add_component(f"Rotor Group {name}", "Propulsion", rotor_group_mass, [x_end, y_end, 0.0], "Motor + ESC + Prop")
        
    mb.add_component("Wiring Loom", "Propulsion", 0.5, [0.0, 0.0, 0.0], "Power and signal wires")

    # 5. Avionics & Comms
    mb.add_component("Flight Controller & GPS", "Avionics", 0.08, [0.0, 0.0, 0.08], "Darkmatter BRAHMA F7 / Elena NDNU GPS")
    mb.add_component("RF Telemetry & Antennas", "Avionics", 0.15, [0.0, -0.2, 0.1], "ZeroDrag Nexus1 ELRS + 915MHz Link")
    mb.add_component("First Person View (FPV) Camera", "Avionics", 0.10, [0.0, 0.3, -0.05], "Camera + VTX")
    mb.add_component("Companion Computer", "Avionics", 0.30, [0.0, 0.0, 0.07], "Nvidia Jetson Orin Nano")

    return mb

def run_tow_convergence(payload_mass=10.0, initial_fuel_guess=15.0, prop_diameter=40, max_iter=20, tol=0.005, energy_density_wh_kg=520.0):
    """
    Iterates TOW -> Hover Power -> Mission Energy Consumed -> Battery Mass + 20% Reserve -> TOW
    until Total Takeoff Weight converges within tolerance.
    """
    from power_endurance import PowerEndurance
    from propulsion import Propeller, Motor
    
    prop = Propeller(diameter_inches=prop_diameter, pitch_inches=13)
    motor = Motor(kv=100, resistance=0.017, idle_current=2.0, weight_kg=1.05)
    pe = PowerEndurance(prop, motor)
    
    current_battery = initial_fuel_guess
    prev_tow = 0.0
    iteration_history = []
    
    for iteration in range(1, max_iter + 1):
        mb = build_default_uav_mass_budget(payload_mass=payload_mass, fuel_mass=current_battery, prop_diameter=prop_diameter, energy_density_wh_kg=energy_density_wh_kg)
        tow = mb.get_total_mass()
        
        # Calculate hover power
        hover_power = pe.calculate_total_power(tow, speed_mps=0.0)
        
        # Run operational mission simulation (30 km out + 20 min loiter + 30 km back)
        res = pe.simulate_operational_mission(tow, battery_mass_kg=current_battery, energy_density_wh_kg=energy_density_wh_kg)
        
        energy_consumed_wh = res["total_energy_consumed_wh"]
        required_battery_with_reserve = res["required_battery_mass_kg"]
        
        delta_tow = abs(tow - prev_tow)
        
        iteration_history.append({
            "iteration": iteration,
            "tow_kg": tow,
            "hover_power_w": hover_power,
            "energy_consumed_wh": energy_consumed_wh,
            "battery_required_20_reserve_kg": required_battery_with_reserve,
            "battery_carried_kg": current_battery,
            "delta_tow_kg": delta_tow
        })
        
        if delta_tow < tol:
            print(f"TOW Converged in {iteration} iterations!")
            break
            
        prev_tow = tow
        current_battery = required_battery_with_reserve
        
    final_mb = build_default_uav_mass_budget(payload_mass=payload_mass, fuel_mass=current_battery, prop_diameter=prop_diameter, energy_density_wh_kg=energy_density_wh_kg)
    
    return {
        "final_mb": final_mb,
        "converged_tow_kg": final_mb.get_total_mass(),
        "converged_fuel_kg": current_battery, # kept for legacy API compatibility
        "converged_battery_kg": current_battery,
        "hover_power_w": iteration_history[-1]["hover_power_w"] if iteration_history else 0.0,
        "energy_consumed_wh": iteration_history[-1]["energy_consumed_wh"] if iteration_history else 0.0,
        "iteration_history": iteration_history
    }

if __name__ == "__main__":
    print("Running TOW Mass-Power-Battery Convergence Loop...")
    conv = run_tow_convergence(prop_diameter=40)
    
    print("\nConvergence History Table:")
    print(f"{'Iter':<5} | {'TOW (kg)':<10} | {'Hover Power (W)':<16} | {'Energy Cons (Wh)':<16} | {'Req Batt w/ Reserve (kg)':<25} | {'Delta TOW (kg)':<15}")
    print("-" * 95)
    for h in conv["iteration_history"]:
        print(f"{h['iteration']:<5} | {h['tow_kg']:<10.3f} | {h['hover_power_w']:<16.1f} | {h['energy_consumed_wh']:<16.1f} | {h['battery_required_20_reserve_kg']:<25.3f} | {h['delta_tow_kg']:<15.3f}")
        
    mb = conv["final_mb"]
    total_mass = mb.get_total_mass()
    cg = mb.calculate_cg()
    I = mb.calculate_inertia_tensor(cg)
    
    print(f"\nFinal Converged TOW: {total_mass:.3f} kg")
    print(f"Final Converged Battery Mass: {conv['converged_battery_kg']:.3f} kg")
    print(f"Center of Gravity: [{cg[0]:.4f}, {cg[1]:.4f}, {cg[2]:.4f}] m")
    print("Inertia Tensor (kg-m^2):")
    print(f"  Ixx = {I[0,0]:.4f}, Iyy = {I[1,1]:.4f}, Izz = {I[2,2]:.4f}")

