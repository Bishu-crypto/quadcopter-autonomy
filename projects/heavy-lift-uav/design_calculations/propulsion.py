#propulsion.py
import numpy as np

class Propeller:
    def __init__(self, diameter_inches, pitch_inches, figure_of_merit=0.70):
        self.diameter = diameter_inches * 0.0254 # meters
        self.pitch = pitch_inches * 0.0254 # meters
        self.area = np.pi * (self.diameter / 2)**2
        self.fom = figure_of_merit # Figure of Merit (aerodynamic efficiency)

    def thrust_power_model(self, thrust_n, air_density=1.225):
        """
        Calculates the required mechanical power (W) for a given thrust (N) in hover
        using Actuator Disk / Momentum Theory.
        """
        if thrust_n <= 0:
            return 0.0
        # Ideal induced velocity (m/s)
        v_i = np.sqrt(thrust_n / (2.0 * air_density * self.area))
        # Ideal power (W)
        p_ideal = thrust_n * v_i
        # Actual mechanical power including losses
        p_mech = p_ideal / self.fom
        return p_mech

    def get_torque(self, thrust_n, rpm, air_density=1.225):
        """
        Calculates torque (N-m) from mechanical power and angular velocity.
        """
        p_mech = self.thrust_power_model(thrust_n, air_density)
        omega = rpm * (2.0 * np.pi / 60.0)
        if omega <= 0:
            return 0.0
        return p_mech / omega

class Motor:
    def __init__(self, kv, resistance, idle_current, weight_kg):
        self.kv = kv # RPM/V
        self.r_m = resistance # Ohms
        self.i_0 = idle_current # Amps
        self.weight = weight_kg # kg
        # Torque constant Kt (N-m/A)
        self.k_t = 60.0 / (2.0 * np.pi * self.kv)

    def solve_motor_state(self, torque_nm, rpm):
        """
        Calculates current, voltage, electrical power, and efficiency for a given load.
        """
        # Torque = Kt * (I - I_0) => I = Torque / Kt + I_0
        current = (torque_nm / self.k_t) + self.i_0
        
        # Back EMF voltage
        e_emf = rpm / self.kv
        
        # Terminal voltage
        voltage = current * self.r_m + e_emf
        
        p_elec = voltage * current
        omega = rpm * (2.0 * np.pi / 60.0)
        p_mech = torque_nm * omega
        
        efficiency = p_mech / p_elec if p_elec > 0 else 0.0
        
        return {
            "current": current,
            "voltage": voltage,
            "p_elec": p_elec,
            "p_mech": p_mech,
            "efficiency": efficiency
        }
if __name__ == "__main__":
    # Quick verification
    prop = Propeller(diameter_inches=36, pitch_inches=12)
    # Define T-Motor U15 II KV100 equivalent
    motor = Motor(kv=100, resistance=0.017, idle_current=2.0, weight_kg=1.05)
    
    thrust_n = 5.0 * 9.81 # 5 kg hover thrust per motor
    rpm = 2200
    
    torque = prop.get_torque(thrust_n, rpm)
    state = motor.solve_motor_state(torque, rpm)
    
    print(f"Propeller Mech Power: {prop.thrust_power_model(thrust_n):.2f} W")
    print(f"Motor Voltage: {state['voltage']:.2f} V, Current: {state['current']:.2f} A")
    print(f"Motor Elec Power: {state['p_elec']:.2f} W, Efficiency: {state['efficiency']*100:.1f}%")
