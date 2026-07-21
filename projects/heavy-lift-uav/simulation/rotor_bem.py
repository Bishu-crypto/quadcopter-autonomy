import numpy as np
import os
import matplotlib.pyplot as plt

class BEMSolver:
    def __init__(self, radius_m, num_blades=2, chord_root=0.08, chord_tip=0.03, twist_root_deg=25.0, twist_tip_deg=8.0):
        self.R = radius_m
        self.B = num_blades
        self.c_root = chord_root
        self.c_tip = chord_tip
        self.theta_root = np.radians(twist_root_deg)
        self.theta_tip = np.radians(twist_tip_deg)
        
        # Airfoil lift/drag properties (approximate NACA 4412 at low Reynolds numbers)
        self.cl_alpha = 2 * np.pi # lift curve slope (per radian)
        self.alpha_0 = np.radians(-4.0) # zero-lift angle of attack
        self.cd0 = 0.015 # minimum drag coefficient
        self.k_drag = 0.05 # induced drag factor for profile drag: Cd = cd0 + k_drag * Cl^2

    def get_element_geometry(self, r):
        """
        Linearly interpolates chord and twist angle at radial position r.
        """
        fraction = r / self.R
        chord = self.c_root + fraction * (self.c_tip - self.c_root)
        twist = self.theta_root + fraction * (self.theta_tip - self.theta_root)
        return chord, twist

    def solve_element(self, r, omega, V_climb=0.0, air_density=1.225):
        """
        Solves for the induced velocity at radius r using BEM.
        Equates blade element forces to axial momentum change.
        """
        chord, twist = self.get_element_geometry(r)
        
        # Rotational speed (m/s)
        V_theta = omega * r
        if V_theta <= 0:
            return 0.0, 0.0
            
        # Solves for induced velocity vi (axial inflow) using iteration
        # Inflow angle: phi = arctan((V_climb + vi) / V_theta)
        vi = 0.5 # initial guess
        max_iter = 100
        tolerance = 1e-4
        
        for _ in range(max_iter):
            W = np.sqrt((V_climb + vi)**2 + V_theta**2)
            phi = np.arctan2(V_climb + vi, V_theta)
            
            # Angle of attack
            alpha = twist - phi
            
            # Lift and drag coefficients
            cl = self.cl_alpha * (alpha - self.alpha_0)
            # Simple stall model
            cl = np.clip(cl, -1.2, 1.2)
            cd = self.cd0 + self.k_drag * cl**2
            
            # Aerodynamic forces resolved in axial direction
            # dT_element = 0.5 * rho * W^2 * c * B * (Cl * cos(phi) - Cd * sin(phi)) dr
            # Momentum theory: dT_momentum = 4 * pi * rho * r * vi * (V_climb + vi) dr
            # Solve for new vi from equating the two:
            # vi * (V_climb + vi) = (W^2 * c * B / (8 * pi * r)) * (Cl * cos(phi) - Cd * sin(phi))
            rhs = (W**2 * chord * self.B / (8.0 * np.pi * r)) * (cl * np.cos(phi) - cd * np.sin(phi))
            
            # Solve quadratic for vi: vi^2 + V_climb * vi - rhs = 0
            # vi = (-V_climb + sqrt(V_climb^2 + 4 * rhs)) / 2
            if rhs < 0:
                vi_new = 0.0
            else:
                vi_new = (-V_climb + np.sqrt(V_climb**2 + 4.0 * rhs)) / 2.0
                
            if abs(vi_new - vi) < tolerance:
                vi = vi_new
                break
            vi = vi_new
            
        # Recompute forces at convergence
        W = np.sqrt((V_climb + vi)**2 + V_theta**2)
        phi = np.arctan2(V_climb + vi, V_theta)
        alpha = twist - phi
        cl = np.clip(self.cl_alpha * (alpha - self.alpha_0), -1.2, 1.2)
        cd = self.cd0 + self.k_drag * cl**2
        
        # Thrust and Torque per unit length
        dT_dr = 0.5 * air_density * W**2 * chord * self.B * (cl * np.cos(phi) - cd * np.sin(phi))
        dQ_dr = 0.5 * air_density * W**2 * chord * self.B * (cl * np.sin(phi) + cd * np.cos(phi)) * r
        
        return dT_dr, dQ_dr

    def solve_propeller(self, rpm, V_climb=0.0, air_density=1.225, num_elements=30):
        """
        Integrates blade elements radially to find total thrust (N) and torque (N-m).
        """
        omega = rpm * (2.0 * np.pi / 60.0)
        if omega <= 0:
            return 0.0, 0.0
            
        # Exclude root hub (inner 15% of radius)
        r_vals = np.linspace(0.15 * self.R, self.R, num_elements)
        dr = r_vals[1] - r_vals[0]
        
        total_thrust = 0.0
        total_torque = 0.0
        
        for r in r_vals:
            dT_dr, dQ_dr = self.solve_element(r, omega, V_climb, air_density)
            total_thrust += dT_dr * dr
            total_torque += dQ_dr * dr
            
        return total_thrust, total_torque

def generate_bem_curves(output_dir="reports/figures"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 40" propeller (Radius = 20" = 0.508 m)
    solver = BEMSolver(radius_m=0.508)
    
    rpm_range = np.linspace(1000, 2600, 17)
    thrusts = []
    powers = []
    efficiencies_g_w = [] # Hover efficiency in g/W
    
    for rpm in rpm_range:
        thrust_n, torque_nm = solver.solve_propeller(rpm)
        omega = rpm * (2.0 * np.pi / 60.0)
        power_w = torque_nm * omega
        
        thrust_kg = thrust_n / 9.81
        eff = (thrust_kg * 1000.0) / power_w if power_w > 0 else 0.0
        
        thrusts.append(thrust_kg)
        powers.append(power_w)
        efficiencies_g_w.append(eff)
        
    # Plotting
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    color = 'tab:blue'
    ax1.set_xlabel('Propeller Speed (RPM)')
    ax1.set_ylabel('Thrust (kg)', color=color)
    ax1.plot(rpm_range, thrusts, color=color, linewidth=2, label='Thrust (kg)')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('Mechanical Power (W)', color=color)
    ax2.plot(rpm_range, powers, color=color, linewidth=2, linestyle='--', label='Power (W)')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Propeller Aerodynamic Curves (BEM Simulation) — 40" Rotor')
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, "propeller_bem_curves.png"), dpi=200)
    plt.close()
    
    # Hover efficiency plot
    plt.figure(figsize=(8, 5))
    plt.plot(thrusts, efficiencies_g_w, 'g-', linewidth=2)
    plt.xlabel('Thrust per Rotor (kg)')
    plt.ylabel('Hover Efficiency (g/W)')
    plt.title('Hover Efficiency vs. Thrust (BEM Simulation) — 40" Rotor')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "hover_efficiency_curve.png"), dpi=200)
    plt.close()
    
    print("BEM Simulation completed. Plots generated in reports/figures/")

if __name__ == "__main__":
    solver = BEMSolver(radius_m=0.508)
    t, q = solver.solve_propeller(2200)
    p = q * (2200 * 2 * np.pi / 60.0)
    print(f"BEM Propeller Check (2200 RPM): Thrust = {t/9.81:.2f} kg, Torque = {q:.2f} N-m, Mech Power = {p:.1f} W")
    
    # Generate curves
    generate_bem_curves("projects/heavy-lift-uav/reports/figures")
