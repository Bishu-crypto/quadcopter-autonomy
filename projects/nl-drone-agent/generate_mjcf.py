"""
Generates hexacopter.xml (MJCF) for the Voyager heavy-lift hexacopter,
using real converged mass/inertia values from
projects/heavy-lift-uav/design_calculations/mass_budget.py
"""
import os
import numpy as np

# ---- Real converged values (from mass_budget.py run_tow_convergence, prop_diameter=40) ----
TOW = 37.291          # kg
CG = [0.0000, 0.0000, -0.0521]   # m, relative to frame origin
IXX, IYY, IZZ = 5.8965, 5.8815, 11.1390   # kg-m^2
ARM_LENGTH = 1.12      # m
N_ROTORS = 6
G = 9.81
HOVER_THRUST_PER_ROTOR = (TOW * G) / N_ROTORS   # N
ROTOR_Z = 0.04          # m, rotor plane above frame origin
YAW_TORQUE_COEFF = 0.02  # N*m per N of thrust (reaction torque coupling)
MESH_SCALE = 10.0        # STL is a 1:10 scale reference model

rotor_sites = []
rotor_actuators = []
for i in range(N_ROTORS):
    angle_deg = i * 60.0
    angle_rad = np.radians(angle_deg)
    x = ARM_LENGTH * np.cos(angle_rad)
    y = ARM_LENGTH * np.sin(angle_rad)
    spin = 1 if i % 2 == 0 else -1  # alternating CW/CCW
    rotor_sites.append(
        f'      <site name="rotor{i}" pos="{x:.4f} {y:.4f} {ROTOR_Z}" size="0.02" rgba="1 0 0 1"/>'
    )
    rotor_actuators.append(
        f'    <motor name="rotor{i}_thrust" site="rotor{i}" gear="0 0 1 0 0 {spin * YAW_TORQUE_COEFF:.4f}" '
        f'ctrlrange="0 {HOVER_THRUST_PER_ROTOR * 2.2:.2f}"/>'
    )

xml = f"""<mujoco model="voyager_heavy_lift_hexacopter">
  <compiler angle="radian" meshdir="assets"/>
  <option timestep="0.002" gravity="0 0 -9.81" integrator="RK4"/>
  <visual>
    <global offwidth="960" offheight="540"/>
  </visual>

  <asset>
    <mesh name="hex_body_mesh" file="hexacopter_body.stl" scale="{MESH_SCALE} {MESH_SCALE} {MESH_SCALE}"/>
    <texture type="skybox" builtin="gradient" rgb1="0.5 0.7 0.9" rgb2="0.05 0.05 0.1" width="128" height="128"/>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.2 0.3 0.2" rgb2="0.3 0.4 0.3" width="300" height="300"/>
    <material name="grid_mat" texture="grid" texrepeat="8 8" reflectance="0.1"/>
  </asset>

  <worldbody>
    <light directional="true" pos="0 0 10" dir="0 0 -1" diffuse="0.9 0.9 0.9"/>
    <geom name="ground" type="plane" size="50 50 0.1" material="grid_mat"/>

    <body name="hexacopter" pos="0 0 2.0">
      <freejoint name="hex_free"/>
      <inertial pos="{CG[0]} {CG[1]} {CG[2]}" mass="{TOW}" diaginertia="{IXX} {IYY} {IZZ}"/>
      <geom name="hex_visual" type="mesh" mesh="hex_body_mesh" rgba="0.85 0.85 0.9 1" contype="0" conaffinity="0"/>
      <geom name="hex_collision" type="box" size="0.15 0.15 0.05" rgba="1 1 1 0" group="3"/>
{chr(10).join(rotor_sites)}
    </body>
  </worldbody>

  <actuator>
{chr(10).join(rotor_actuators)}
  </actuator>

  <sensor>
    <framepos name="hex_pos" objtype="body" objname="hexacopter"/>
    <framequat name="hex_quat" objtype="body" objname="hexacopter"/>
    <framelinvel name="hex_linvel" objtype="body" objname="hexacopter"/>
    <frameangvel name="hex_angvel" objtype="body" objname="hexacopter"/>
  </sensor>
</mujoco>
"""

output_path = os.path.join(os.path.dirname(__file__), "hexacopter.xml")
with open(output_path, "w") as f:
    f.write(xml)

print(f"Generated hexacopter.xml at {output_path}")
print(f"TOW: {TOW} kg | Hover thrust/rotor: {HOVER_THRUST_PER_ROTOR:.2f} N | Total hover thrust: {HOVER_THRUST_PER_ROTOR*N_ROTORS:.2f} N")
