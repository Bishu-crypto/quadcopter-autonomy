#power endurance.py
import numpy as np
from propulsion import Propeller, Motor

class PowerEndurance:
    def __init__(self, propeller, motor, drag_coefficient=1.2, frontal_area=0.35, sfc_kg_kwh=0.42):
        self.prop = propeller
        self.motor = motor
        self.Cd = drag_coefficient # Drag coefficient of fuselage
        self.A_front = frontal_area # Frontal projected area in m^2
        self.sfc = sfc_kg_kwh / 3.6e6 # convert kg/kWh to kg/J (Specific Fuel Consumption)
        
    def solve_induced_velocity_forward(self, thrust, speed, air_density=1.225):
        """
        Solves for the induced velocity (v_i) in forward flight using Newton-Raphson.
        Equation: v_i = T / (2 * rho * A * sqrt(V^2 + v_i^2))
        """
        if thrust <= 0:
            return 0.0
        A = self.prop.area
        const = thrust / (2.0 * air_density * A)
        
        # Initial guess (hover value)
        vi = np.sqrt(thrust / (2.0 * air_density * A))
        
        # Newton-Raphson loop
        for _ in range(20):
            denom = np.sqrt(speed**2 + vi**2)
            f = vi * denom - const
            f_prime = denom + (vi**2 / denom)
            vi_new = vi - f / f_prime
            if abs(vi_new - vi) < 1e-5:
                return vi_new
            vi = vi_new
        return vi

    def solve_induced_velocity_climb(self, thrust, V_climb, air_density=1.225):
        """
        Solves for the induced velocity (v_i) in vertical climb.
        Equation: v_i * (V_climb + v_i) = T / (2 * rho * A)
        Has a closed-form quadratic solution.
        """
        if thrust <= 0:
            return 0.0
        A = self.prop.area
        const = thrust / (2.0 * air_density * A)
        vi = (-V_climb + np.sqrt(V_climb**2 + 4.0 * const)) / 2.0
        return vi

    def calculate_total_power(self, mass_kg, speed_mps, V_climb=0.0, air_density=1.225):
        """
        Calculates total electrical power required to fly at a given speed/climb rate for a 6-rotor hexacopter.
        """
        weight = mass_kg * 9.81
        
        if V_climb > 0.0 and speed_mps == 0.0:
            # Vertical climb case
            thrust_total = weight
            thrust_per_rotor = thrust_total / 6.0
            v_i = self.solve_induced_velocity_climb(thrust_per_rotor, V_climb, air_density)
            p_mech_rotor = thrust_per_rotor * (V_climb + v_i) / self.prop.fom
            p_mech_total = p_mech_rotor * 6.0
            
            # Profile power
            p_profile = 0.15 * self.prop.thrust_power_model(weight / 6.0, air_density) * 6.0
            p_mech_total += p_profile
            
            # Parasitic power in climb is negligible
        else:
            # Forward flight case
            # 1. Aerodynamic drag force
            drag = 0.5 * air_density * (speed_mps**2) * self.Cd * self.A_front
            
            # 2. Required thrust
            thrust_total = np.sqrt(weight**2 + drag**2)
            thrust_per_rotor = thrust_total / 6.0
            
            # 3. Mechanical power (single rotor momentum theory)
            v_i = self.solve_induced_velocity_forward(thrust_per_rotor, speed_mps, air_density)
            p_mech_rotor = thrust_per_rotor * v_i / self.prop.fom
            p_mech_total = p_mech_rotor * 6.0
            
            # Add profile power
            p_profile = 0.15 * self.prop.thrust_power_model(weight / 6.0, air_density) * 6.0
            p_mech_total += p_profile
            
            # Add parasitic power from forward flight drag
            p_drag = drag * speed_mps
            p_mech_total += p_drag
        
        # 4. Electrical power using motor model
        # Estimate RPM based on thrust.
        if V_climb > 0.0 and speed_mps == 0.0:
            rpm = 2200.0 * np.sqrt(weight / (6.0 * 49.0))
        else:
            rpm = 2200.0 * np.sqrt(thrust_total / (6.0 * 49.0))
            
        if rpm < 500:
            rpm = 500 # minimum idle RPM
            
        torque_per_motor = p_mech_total / 6.0 / (rpm * 2 * np.pi / 60.0) if rpm > 0 else 0.0
        
        # Solve motor electrical performance
        state = self.motor.solve_motor_state(torque_per_motor, rpm)
        p_elec_propulsion = state["p_elec"] * 6.0
        
        # Avionics and payload power (constant draw, say 150 W)
        p_elec_avionics = 150.0
        
        return p_elec_propulsion + p_elec_avionics

    def simulate_flight(self, initial_mass_kg, battery_mass_kg=0.0, speed_mps=12.0, energy_density_wh_kg=520.0, dt=60.0, fuel_mass_kg=None):
        """
        Simulates the flight until battery is depleted, integrating energy draw.
        For battery-electric, total mass is constant throughout flight.
        """
        if fuel_mass_kg is not None and battery_mass_kg == 0.0:
            battery_mass_kg = fuel_mass_kg
            
        time = 0.0
        current_energy_wh = battery_mass_kg * energy_density_wh_kg
        current_mass = initial_mass_kg
        
        history = {
            "time_min": [],
            "mass_kg": [],
            "power_w": [],
            "battery_wh": [],
            "distance_km": []
        }
        
        while current_energy_wh > 0:
            power = self.calculate_total_power(current_mass, speed_mps)
            consumed_wh = (power * dt) / 3600.0
            
            if consumed_wh > current_energy_wh:
                dt_actual = (current_energy_wh / (power / 3600.0))
                current_energy_wh = 0.0
                time += dt_actual
            else:
                current_energy_wh -= consumed_wh
                time += dt
                
            distance = speed_mps * time / 1000.0
            
            history["time_min"].append(time / 60.0)
            history["mass_kg"].append(current_mass)
            history["power_w"].append(power)
            history["battery_wh"].append(current_energy_wh)
            history["distance_km"].append(distance)
            
        endurance_min = time / 60.0
        total_distance = speed_mps * time / 1000.0
        
        return endurance_min, total_distance, history

    def simulate_operational_mission(self, initial_mass_kg, battery_mass_kg=0.0, cruise_speed_mps=12.0, climb_rate_mps=2.5, climb_alt_m=100.0, loiter_time_s=1200.0, target_range_km=30.0, energy_density_wh_kg=520.0, dt=1.0, fuel_mass_kg=None):
        """
        Simulates the 30 km operational mission profile:
        1. Vertical Climb to altitude (climb_alt_m)
        2. Cruise Out (target_range_km)
        3. Loiter / Hover on station (loiter_time_s)
        4. Cruise Back (target_range_km)
        Integrates cumulative energy consumption at constant takeoff mass.
        """
        if fuel_mass_kg is not None and battery_mass_kg == 0.0:
            battery_mass_kg = fuel_mass_kg
            
        current_mass = initial_mass_kg
        total_time_s = 0.0
        
        energy_climb_j = 0.0
        energy_cruise_out_j = 0.0
        energy_loiter_j = 0.0
        energy_cruise_back_j = 0.0
        
        # Phase 1: Climb
        climb_duration = climb_alt_m / climb_rate_mps
        t = 0.0
        while t < climb_duration:
            step = min(dt, climb_duration - t)
            power = self.calculate_total_power(current_mass, speed_mps=0.0, V_climb=climb_rate_mps)
            energy_climb_j += power * step
            t += step
            total_time_s += step
            
        # Phase 2: Cruise Out (30 km)
        target_dist_m = target_range_km * 1000.0
        dist_out = 0.0
        while dist_out < target_dist_m:
            step = dt
            power = self.calculate_total_power(current_mass, speed_mps=cruise_speed_mps, V_climb=0.0)
            energy_cruise_out_j += power * step
            dist_out += cruise_speed_mps * step
            total_time_s += step
            
        # Phase 3: Loiter / Hover (20 min)
        t = 0.0
        while t < loiter_time_s:
            step = min(dt, loiter_time_s - t)
            power = self.calculate_total_power(current_mass, speed_mps=0.0, V_climb=0.0)
            energy_loiter_j += power * step
            t += step
            total_time_s += step
            
        # Phase 4: Cruise Back (30 km)
        dist_back = 0.0
        while dist_back < target_dist_m:
            step = dt
            power = self.calculate_total_power(current_mass, speed_mps=cruise_speed_mps, V_climb=0.0)
            energy_cruise_back_j += power * step
            dist_back += cruise_speed_mps * step
            total_time_s += step
            
        total_energy_consumed_j = energy_climb_j + energy_cruise_out_j + energy_loiter_j + energy_cruise_back_j
        total_energy_consumed_wh = total_energy_consumed_j / 3600.0
        
        # 20% Reserve Margin requirement:
        # Total battery energy capacity required = total_energy_consumed_wh / 0.8
        required_capacity_with_reserve_wh = total_energy_consumed_wh / 0.8
        required_battery_mass_kg = required_capacity_with_reserve_wh / energy_density_wh_kg
        
        is_sufficient = battery_mass_kg >= required_battery_mass_kg
        
        res = {
            "total_time_min": total_time_s / 60.0,
            
            "energy_climb_wh": energy_climb_j / 3600.0,
            "energy_cruise_out_wh": energy_cruise_out_j / 3600.0,
            "energy_loiter_wh": energy_loiter_j / 3600.0,
            "energy_cruise_back_wh": energy_cruise_back_j / 3600.0,
            "total_energy_consumed_wh": total_energy_consumed_wh,
            "required_capacity_with_reserve_wh": required_capacity_with_reserve_wh,
            "required_battery_mass_kg": required_battery_mass_kg,
            "carried_battery_mass_kg": battery_mass_kg,
            
            # Legacy fuel aliases for safety
            "fuel_climb_kg": (energy_climb_j / 3600.0) / energy_density_wh_kg,
            "fuel_cruise_out_kg": (energy_cruise_out_j / 3600.0) / energy_density_wh_kg,
            "fuel_loiter_kg": (energy_loiter_j / 3600.0) / energy_density_wh_kg,
            "fuel_cruise_back_kg": (energy_cruise_back_j / 3600.0) / energy_density_wh_kg,
            "total_fuel_consumed_kg": total_energy_consumed_wh / energy_density_wh_kg,
            "required_fuel_with_reserve_kg": required_battery_mass_kg,
            "carried_fuel_kg": battery_mass_kg,
            
            "reserve_margin_actual_percent": ((battery_mass_kg - required_battery_mass_kg) / battery_mass_kg) * 100.0 if battery_mass_kg > 0 else 0.0,
            "is_sufficient": is_sufficient
        }
        return res

if __name__ == "__main__":
    from mass_budget import build_default_uav_mass_budget
    
    prop = Propeller(diameter_inches=40, pitch_inches=13)
    motor = Motor(kv=100, resistance=0.017, idle_current=2.0, weight_kg=1.05)
    
    pe = PowerEndurance(prop, motor)
    
    mb = build_default_uav_mass_budget(payload_mass=10.0, fuel_mass=4.2, prop_diameter=40)
    tow = mb.get_total_mass()
    
    print(f"Initial Takeoff Weight (40\" Prop): {tow:.2f} kg")
    
    # Hover power (speed = 0)
    hover_power = pe.calculate_total_power(tow, 0.0)
    print(f"Hover Power: {hover_power:.2f} W")
    
    # Run operational mission simulation
    res = pe.simulate_operational_mission(tow, fuel_mass_kg=4.2)
    print("\nOperational Mission Simulation (30 km Out + 20 min Loiter + 30 km Back):")
    print(f"  Total Duration: {res['total_time_min']:.1f} min")
    print(f"  Climb Fuel: {res['fuel_climb_kg']:.3f} kg")
    print(f"  Cruise Out Fuel: {res['fuel_cruise_out_kg']:.3f} kg")
    print(f"  Loiter Fuel: {res['fuel_loiter_kg']:.3f} kg")
    print(f"  Cruise Back Fuel: {res['fuel_cruise_back_kg']:.3f} kg")
    print(f"  Total Fuel Consumed: {res['total_fuel_consumed_kg']:.3f} kg")
    print(f"  Fuel Required (with 20% Reserve Margin): {res['required_fuel_with_reserve_kg']:.3f} kg")
    print(f"  Fuel Carried: {res['carried_fuel_kg']:.3f} kg")
    print(f"  Reserve Margin Carried: {res['reserve_margin_actual_percent']:.1f}%")
    print(f"  Sufficient? {res['is_sufficient']}")
