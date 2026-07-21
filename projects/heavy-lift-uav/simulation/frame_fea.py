import numpy as np
import os
import matplotlib.pyplot as plt

class BeamElement:
    def __init__(self, node_i, node_j, L, E, I_area, density, cross_area):
        self.node_i = node_i
        self.node_j = node_j
        self.L = L
        self.E = E
        self.I = I_area
        self.rho = density
        self.A = cross_area
        
        # Local stiffness matrix (Euler-Bernoulli beam)
        # Nodal DOFs: [v_i, theta_i, v_j, theta_j]
        # v is vertical displacement, theta is rotation
        EI = E * I_area
        L3 = L**3
        L2 = L**2
        self.k_local = (EI / L3) * np.array([
            [12.0,   6.0*L,  -12.0,  6.0*L],
            [6.0*L,  4.0*L2, -6.0*L, 2.0*L2],
            [-12.0,  -6.0*L, 12.0,   -6.0*L],
            [6.0*L,  2.0*L2, -6.0*L, 4.0*L2]
        ])
        
        # Consistent mass matrix (for self-weight distributed load)
        # Nodal force vector = mass_density_per_length * g * L/2 * [1, L/6, 1, -L/6]
        # (Assuming uniform vertical distributed load)
        self.w_self = density * cross_area * 9.81

class BeamFEA:
    def __init__(self, length_m, num_elements, E_gpa, UTS_mpa, Do_mm, t_mm, density_kg_m3=1600.0):
        self.L = length_m
        self.num_elements = num_elements
        self.n_nodes = num_elements + 1
        self.E = E_gpa * 1e9
        self.uts = UTS_mpa * 1e6
        self.do = Do_mm / 1000.0
        self.t = t_mm / 1000.0
        self.di = self.do - 2.0 * self.t
        self.rho = density_kg_m3
        
        self.A = (np.pi / 4.0) * (self.do**2 - self.di**2)
        self.I = (np.pi / 64.0) * (self.do**4 - self.di**4)
        
        self.node_coords = np.linspace(0.0, self.L, self.n_nodes)
        self.elements = []
        
        L_el = self.L / num_elements
        for i in range(num_elements):
            el = BeamElement(i, i+1, L_el, self.E, self.I, self.rho, self.A)
            self.elements.append(el)
            
    def solve(self, tip_force_n, motor_mass_kg, load_factor_g=2.5):
        """
        Solves the global stiffness system: K_global * U = F_global
        """
        # Global system size: 2 DOFs per node (vertical displacement, rotation)
        # N_dof = 2 * n_nodes
        n_dof = 2 * self.n_nodes
        K_glob = np.zeros((n_dof, n_dof))
        F_glob = np.zeros(n_dof)
        
        # Assembly
        for el in self.elements:
            # DOFs indices
            dofs = [2 * el.node_i, 2 * el.node_i + 1, 2 * el.node_j, 2 * el.node_j + 1]
            
            # Stiffness matrix assembly
            for i_idx, i_dof in enumerate(dofs):
                for j_idx, j_dof in enumerate(dofs):
                    K_glob[i_dof, j_dof] += el.k_local[i_idx, j_idx]
            
            # Distributed self-weight load (under G-load)
            w_load = el.w_self * load_factor_g
            L_e = el.L
            # Consistent nodal force for element
            f_dist = w_load * L_e * np.array([0.5, L_e/12.0, 0.5, -L_e/12.0])
            
            for idx, dof in enumerate(dofs):
                F_glob[dof] += f_dist[idx]
                
        # Point load at the tip (vertical force = motor thrust - motor mass under G-load)
        # Motor thrust acts upwards (+y), motor weight acts downwards (-y)
        # Under peak maneuver, thrust dominates and acts upwards.
        # F_tip = Tip Force (thrust) - Motor weight * G
        net_tip_force = tip_force_n - (motor_mass_kg * 9.81 * load_factor_g)
        tip_node_disp_dof = 2 * (self.n_nodes - 1)
        F_glob[tip_node_disp_dof] += net_tip_force
        
        # Boundary Conditions: Clamped at Node 0 (x=0)
        # v_0 = 0, theta_0 = 0
        # We partition the matrix or zero out row/col and set diagonal to 1.0
        active_dofs = list(range(2, n_dof))
        
        K_active = K_glob[np.ix_(active_dofs, active_dofs)]
        F_active = F_glob[active_dofs]
        
        # Solve for displacements
        U_active = np.linalg.solve(K_active, F_active)
        
        U_full = np.zeros(n_dof)
        U_full[active_dofs] = U_active
        
        # Extract nodal displacements and rotations
        v_nodal = U_full[0::2]
        theta_nodal = U_full[1::2]
        
        # Calculate bending stress along the beam
        # For each element, M(x) = E * I * v''(x)
        # For Euler-Bernoulli beam, displacement is cubic, so curvature v''(x) is linear.
        # Bending stress: sigma = M * (Do/2) / I = E * (Do/2) * v''
        stresses_mpa = []
        for el in self.elements:
            dofs = [2 * el.node_i, 2 * el.node_i + 1, 2 * el.node_j, 2 * el.node_j + 1]
            u_el = U_full[dofs]
            
            # Curvature at node i (x_local = 0)
            # v''(0) = (-6/L^2)*v_i + (-4/L)*theta_i + (6/L^2)*v_j + (-2/L)*theta_j
            L_e = el.L
            d2v_dx2_i = (-6.0/L_e**2)*u_el[0] + (-4.0/L_e)*u_el[1] + (6.0/L_e**2)*u_el[2] + (-2.0/L_e)*u_el[3]
            
            stress_pa_i = self.E * (self.do / 2.0) * d2v_dx2_i
            stresses_mpa.append(abs(stress_pa_i) / 1e6)
            
        # Append tip stress (ideally 0 for free end)
        stresses_mpa.append(0.0)
        
        return v_nodal, theta_nodal, stresses_mpa

def run_fea_simulation(output_dir="reports/figures"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Define our arm
    # 30mm OD, 2mm wall thickness, 0.8m length
    # Carbon fiber: E = 120 GPa, UTS = 800 MPa, density = 1600 kg/m^3
    fea = BeamFEA(length_m=0.8, num_elements=10, E_gpa=120.0, UTS_mpa=800.0, Do_mm=30.0, t_mm=2.0)
    
    # 2.5G Peak Load
    # TOW = 33 kg. Total thrust required at 2.5G = 33 * 9.81 * 2.5 = 809 N.
    # 4 arms. Thrust per arm = 202 N.
    # Motor/Prop/ESC mass at tip = 1.6 kg.
    thrust_per_arm = 202.0
    motor_mass = 1.6
    
    v_nodal, theta_nodal, stresses_mpa = fea.solve(thrust_per_arm, motor_mass, load_factor_g=2.5)
    
    # Plot Deflection
    plt.figure(figsize=(8, 4))
    plt.plot(fea.node_coords, v_nodal * 1000.0, 'b-o', linewidth=2)
    plt.xlabel('Position along arm (m)')
    plt.ylabel('Deflection (mm)')
    plt.title('Beam Deflection Profile under 2.5G Limit Load (FEM Simulation)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "arm_deflection_fea.png"), dpi=200)
    plt.close()
    
    # Plot Stress
    plt.figure(figsize=(8, 4))
    plt.plot(fea.node_coords, stresses_mpa, 'r-s', linewidth=2)
    plt.axhline(y=800.0 / 1.5, color='g', linestyle='--', label='Allowable Stress (SF=1.5)')
    plt.xlabel('Position along arm (m)')
    plt.ylabel('Bending Stress (MPa)')
    plt.title('Bending Stress Distribution under 2.5G Limit Load')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "arm_stress_fea.png"), dpi=200)
    plt.close()
    
    print(f"FEA Simulation completed. Max Deflection: {np.max(np.abs(v_nodal))*1000.0:.2f} mm")
    print(f"Max Stress: {np.max(stresses_mpa):.2f} MPa (UTS = 800 MPa)")
    print("FEA plots generated in reports/figures/")

if __name__ == "__main__":
    fea = BeamFEA(length_m=0.8, num_elements=5, E_gpa=120.0, UTS_mpa=800.0, Do_mm=30.0, t_mm=2.0)
    v, theta, stress = fea.solve(202.0, 1.6, 2.5)
    print(f"FEA Check - Tip Deflection: {v[-1]*1000.0:.2f} mm, Root Stress: {stress[0]:.2f} MPa")
    
    # Generate curves
    run_fea_simulation("projects/heavy-lift-uav/reports/figures")
