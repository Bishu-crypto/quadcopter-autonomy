import numpy as np

class CarbonFiberArm:
    def __init__(self, outer_diameter_mm=30.0, wall_thickness_mm=2.0, length_m=1.12, youngs_modulus_gpa=120.0, tensile_strength_mpa=800.0):
        self.do = outer_diameter_mm / 1000.0 # meters
        self.t = wall_thickness_mm / 1000.0 # meters
        self.di = self.do - 2.0 * self.t # meters
        self.L = length_m # meters
        self.E = youngs_modulus_gpa * 1e9 # Pascals
        self.uts = tensile_strength_mpa * 1e6 # Pascals

    def get_cross_sectional_area(self):
        return (np.pi / 4.0) * (self.do**2 - self.di**2)

    def get_area_moment_of_inertia(self):
        """
        Calculates the area moment of inertia (I) for a hollow cylinder:
        I = pi/64 * (Do^4 - Di^4)
        """
        return (np.pi / 64.0) * (self.do**4 - self.di**4)

    def analyze_bending(self, force_n):
        """
        Calculates the max bending stress at the root (Pa) and tip deflection (m)
        for a cantilever beam with a point load at the end.
        """
        I_area = self.get_area_moment_of_inertia()
        
        # Root bending moment: M = F * L
        m_bending = force_n * self.L
        
        # Max stress: sigma = M * y / I_area, where y = Do/2
        stress_pa = (m_bending * (self.do / 2.0)) / I_area
        
        # Deflection: delta = F * L^3 / (3 * E * I_area)
        deflection_m = (force_n * (self.L**3)) / (3.0 * self.E * I_area)
        
        safety_factor = self.uts / stress_pa if stress_pa > 0 else float('inf')
        
        return {
            "root_moment_nm": m_bending,
            "max_stress_mpa": stress_pa / 1e6,
            "deflection_mm": deflection_m * 1000.0,
            "safety_factor": safety_factor
        }

def run_structural_validation(tow_kg, num_arms=6):
    """
    Performs dual structural load case calculations:
      1. Symmetric 2.5G Limit Load Case: All 6 arms carry equal load under 2.5G maneuver.
      2. Asymmetric Motor-Out Load Case: 1 motor fails. Remaining active arms balance moment 
         and carry weight under 1.5G emergency recovery maneuver.
    Returns both results and states which case governs.
    """
    arm = CarbonFiberArm(outer_diameter_mm=30.0, wall_thickness_mm=2.0, length_m=1.12)
    
    # 1. Symmetric 2.5G Load Case
    total_force_sym = tow_kg * 9.81 * 2.5
    force_per_arm_sym = total_force_sym / num_arms
    res_sym = arm.analyze_bending(force_per_arm_sym)
    res_sym["force_per_arm_n"] = force_per_arm_sym
    
    # 2. Asymmetric Motor-Out Load Case (1.5G recovery maneuver)
    # When 1 motor fails, moment equilibrium requires reducing thrust on opposite motor,
    # leaving effectively ~3.0 to 3.5 primary load-bearing arms to carry the 1.5G vertical demand.
    total_force_asym = tow_kg * 9.81 * 1.5
    effective_active_arms = 3.0 # Conservative moment balance factor
    force_per_arm_asym = total_force_asym / effective_active_arms
    res_asym = arm.analyze_bending(force_per_arm_asym)
    res_asym["force_per_arm_n"] = force_per_arm_asym
    
    # Determine governing case
    if res_asym["max_stress_mpa"] > res_sym["max_stress_mpa"]:
        governing_case = "Asymmetric Motor-Out (1.5G Recovery)"
        governing_res = res_asym
    else:
        governing_case = "Symmetric 2.5G Limit Load"
        governing_res = res_sym
        
    print(f"Structural Load Case Analysis (TOW = {tow_kg:.2f} kg):")
    print(f"  Case 1 [Symmetric 2.5G]: Force/Arm = {res_sym['force_per_arm_n']:.1f} N, Stress = {res_sym['max_stress_mpa']:.1f} MPa, SF = {res_sym['safety_factor']:.2f}")
    print(f"  Case 2 [Asymmetric 1.5G Motor-Out]: Force/Arm = {res_asym['force_per_arm_n']:.1f} N, Stress = {res_asym['max_stress_mpa']:.1f} MPa, SF = {res_asym['safety_factor']:.2f}")
    print(f"  GOVERNING LOAD CASE: {governing_case}")
    print(f"  Governing Bending Stress: {governing_res['max_stress_mpa']:.1f} MPa (Allowable SF = {governing_res['safety_factor']:.2f})")
    
    return {
        "symmetric_2_5g": res_sym,
        "asymmetric_motor_out": res_asym,
        "governing_case": governing_case,
        "governing_results": governing_res
    }

if __name__ == "__main__":
    run_structural_validation(34.575)
