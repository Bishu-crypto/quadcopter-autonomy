"""
===============================================================================
FREECAD PARAMETRIC ASSEMBLY MACRO - HEAVY-LIFT UAV (HIGH-FIDELITY DETAILED)
===============================================================================
Locked Baseline (DESIGN_LOCK.md):
  - Configuration: 6 Arms at 60-degree increments (0, 60, 120, 180, 240, 300 deg)
  - Arm Tubes: OD 30mm, Wall Thickness 2mm (ID 26mm), Length 1.12m (1120mm)
  - Propellers: 40" x 13" 2-Blade Carbon Fiber (Radius 508mm, 104mm Tip-to-Tip Clearance)
  - Motor Housings: Two-tier brushless motors (Stator Base 40mm + Rotor Bell 50mm)
  - Motor Mounts: 80x80x4mm plates with 4x M4 PCD 40mm bolt pattern
  - Center Hex Frame: Diameter 400mm, Carbon Fiber Plates (3mm thickness)
  - Payload Bay: 300mm x 200mm x 150mm Cargo Box (10 kg Capacity)
  - Camera Assembly: EO Camera + 2-Axis Gimbal with forward lens barrel
  - Telemetry Antenna: Top-mounted omni antenna
  - Landing Gear: 4 legs with skid pads (450mm height, 220mm ground clearance)
===============================================================================
How to run in FreeCAD:
  1. Open FreeCAD (v0.19, v0.20, v0.21 or v1.0).
  2. Macro -> Macros... -> Select 'hexacopter_assembly.py' -> Execute.
  3. The high-detail assembly builds automatically and exports:
     'projects/heavy-lift-uav/freecad/hexacopter_assembly.step'
===============================================================================
"""

import os
import math

try:
    import FreeCAD as App
    import Part
    from FreeCAD import Base
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False
    print("Notice: Running outside FreeCAD environment. Script generated for standalone execution.")

try:
    import FreeCADGui as Gui
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

def build_hexacopter_freecad_assembly(output_step_path=None):
    if not FREECAD_AVAILABLE:
        print("FreeCAD module not loaded in current Python interpreter.")
        return False

    doc_name = "Hexacopter_UAV_Assembly"
    if App.ActiveDocument and App.ActiveDocument.Name == doc_name:
        doc = App.ActiveDocument
        doc.clearDocument()
    else:
        doc = App.newDocument(doc_name)

    print(f"Building high-detail Hexacopter Assembly in FreeCAD (Doc: {doc_name})...")

    # Primary Dimensions (mm)
    ARM_LENGTH = 1120.0          # 1.12 m
    ARM_OD = 30.0                # 30 mm
    ARM_WALL = 2.0               # 2 mm
    ARM_ID = ARM_OD - 2*ARM_WALL # 26 mm
    
    CENTER_HEX_RADIUS = 200.0    # 200 mm (400 mm Diameter)
    PLATE_THICKNESS = 3.0        # 3 mm
    STANDOFF_HEIGHT = 80.0       # 80 mm spacing
    
    MOTOR_PLATE_SIZE = 80.0      # 80x80 mm
    MOTOR_PLATE_THICK = 4.0      # 4 mm
    PCD_BOLT_RADIUS = 20.0       # PCD 40 mm (R=20mm)
    
    LANDING_GEAR_OD = 20.0       # 20 mm
    LANDING_GEAR_HEIGHT = 450.0  # 450 mm
    SKID_FOOT_LENGTH = 140.0     # 140 mm foot pad
    SKID_FOOT_WIDTH = 40.0       # 40 mm foot pad width
    
    PROP_RADIUS = 508.0          # 40" prop radius = 508 mm
    PROP_HUB_RADIUS = 30.0       # Hub radius 30 mm

    # Color Tokens
    COLOR_CARBON = (0.15, 0.15, 0.15)      # Dark Carbon Slate
    COLOR_MOTOR_BELL = (0.75, 0.75, 0.78)  # Metallic Silver / Aluminum
    COLOR_MOTOR_STATOR = (0.25, 0.25, 0.28)# Dark Anodized Steel
    COLOR_PROP = (0.10, 0.30, 0.60)        # Translucent Dark Blue
    COLOR_PAYLOAD = (0.95, 0.50, 0.10)     # High-Vis Safety Orange
    COLOR_CAMERA = (0.05, 0.05, 0.05)      # Matte Black
    COLOR_LENS = (0.20, 0.60, 0.90)        # Optical Glass Blue
    COLOR_GEN = (0.50, 0.55, 0.60)         # Steel Gray
    COLOR_TANK = (0.85, 0.85, 0.90)        # Semi-Translucent Tank
    COLOR_BOLT = (0.85, 0.85, 0.85)        # Stainless Steel Bolts
    COLOR_ANTENNA = (0.90, 0.20, 0.20)     # Radio Antenna Red/Black

    angles_deg = [0, 60, 120, 180, 240, 300]

    def set_obj_appearance(obj, color, transparency=0):
        try:
            if hasattr(obj, "ViewObject") and obj.ViewObject is not None:
                obj.ViewObject.ShapeColor = (float(color[0]), float(color[1]), float(color[2]))
                if transparency > 0:
                    obj.ViewObject.Transparency = int(transparency)
                if hasattr(obj.ViewObject, "DisplayMode"):
                    obj.ViewObject.DisplayMode = "Flat Lines"
        except Exception as e:
            pass

    # 1. CENTER HEX FRAME PLATES & CLAMPS
    def make_hex_plate(z_offset, label):
        points = []
        for i in range(6):
            rad = math.radians(angles_deg[i])
            points.append(Base.Vector(CENTER_HEX_RADIUS * math.cos(rad), CENTER_HEX_RADIUS * math.sin(rad), z_offset))
        points.append(points[0])
        polygon = Part.makePolygon(points)
        face = Part.Face(polygon)
        plate = face.extrude(Base.Vector(0, 0, PLATE_THICKNESS if z_offset >= 0 else -PLATE_THICKNESS))
        obj = doc.addObject("Part::Feature", label)
        obj.Shape = plate
        set_obj_appearance(obj, COLOR_CARBON)
        return obj

    make_hex_plate(STANDOFF_HEIGHT / 2.0, "Center_Plate_Top")
    make_hex_plate(-STANDOFF_HEIGHT / 2.0, "Center_Plate_Bottom")

    # Arm Clamps & Fasteners at Center Plate
    for idx, angle in enumerate(angles_deg):
        rad = math.radians(angle)
        c_x = 100.0 * math.cos(rad)
        c_y = 100.0 * math.sin(rad)
        clamp_box = Part.makeBox(40, 36, 20, Base.Vector(c_x - 20, c_y - 18, -10))
        clamp_obj = doc.addObject("Part::Feature", f"Arm_Clamp_{idx+1}")
        clamp_obj.Shape = clamp_box
        set_obj_appearance(clamp_obj, COLOR_CARBON)
        
        # 2 Fastener Bolts per clamp
        b1 = Part.makeCylinder(2.5, 30, Base.Vector(c_x - 10, c_y + 12, -15), Base.Vector(0, 0, 1))
        b2 = Part.makeCylinder(2.5, 30, Base.Vector(c_x + 10, c_y - 12, -15), Base.Vector(0, 0, 1))
        bolt_obj = doc.addObject("Part::Feature", f"Clamp_Fasteners_{idx+1}")
        bolt_obj.Shape = b1.fuse(b2)
        set_obj_appearance(bolt_obj, COLOR_BOLT)

    # 2. GENERATOR, FUEL TANK, & AVIONICS ANTENNA
    gen_box = Part.makeBox(160, 160, 120, Base.Vector(-80, -80, -60))
    gen_obj = doc.addObject("Part::Feature", "Hybrid_Generator_3.6kW")
    gen_obj.Shape = gen_box
    set_obj_appearance(gen_obj, COLOR_GEN)

    fuel_tank = Part.makeCylinder(100, 150, Base.Vector(0, 0, -210), Base.Vector(0, 0, 1))
    tank_obj = doc.addObject("Part::Feature", "Fuel_Tank_5L")
    tank_obj.Shape = fuel_tank
    set_obj_appearance(tank_obj, COLOR_TANK, transparency=10)

    # Telemetry Antenna on Top Plate
    ant_base = Part.makeCylinder(8, 12, Base.Vector(0, 80, STANDOFF_HEIGHT/2.0 + PLATE_THICKNESS), Base.Vector(0, 0, 1))
    ant_whip = Part.makeCylinder(2, 120, Base.Vector(0, 80, STANDOFF_HEIGHT/2.0 + PLATE_THICKNESS + 12), Base.Vector(0, 0, 1))
    ant_obj = doc.addObject("Part::Feature", "Telemetry_Omni_Antenna")
    ant_obj.Shape = ant_base.fuse(ant_whip)
    set_obj_appearance(ant_obj, COLOR_ANTENNA)

    # 3. PAYLOAD CARGO BAY (300mm x 200mm x 150mm - 10kg Capacity)
    payload_box = Part.makeBox(300, 200, 150, Base.Vector(-150, -100, -230))
    payload_obj = doc.addObject("Part::Feature", "Payload_Cargo_Bay_10kg")
    payload_obj.Shape = payload_box
    set_obj_appearance(payload_obj, COLOR_PAYLOAD)

    # 4. EO CAMERA & 2-AXIS GIMBAL WITH FORWARD LENS BARREL
    gimbal_yoke = Part.makeBox(60, 70, 40, Base.Vector(150, -35, -110))
    camera_body = Part.makeSphere(32, Base.Vector(180, 0, -125))
    lens_barrel = Part.makeCylinder(14, 25, Base.Vector(180, 0, -125), Base.Vector(1, 0, 0))
    lens_glass = Part.makeCylinder(12, 2, Base.Vector(204, 0, -125), Base.Vector(1, 0, 0))
    
    gimbal_obj = doc.addObject("Part::Feature", "EO_Camera_Gimbal_Assembly")
    gimbal_obj.Shape = gimbal_yoke.fuse(camera_body).fuse(lens_barrel)
    set_obj_appearance(gimbal_obj, COLOR_CAMERA)

    glass_obj = doc.addObject("Part::Feature", "EO_Camera_Optical_Lens")
    glass_obj.Shape = lens_glass
    set_obj_appearance(glass_obj, COLOR_LENS)

    # 5. 6 HOLLOW CARBON ARMS, DETAILED MOTORS, MOUNT BOLTS, & 2-BLADE PROPELLERS
    for idx, angle in enumerate(angles_deg):
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Hollow Carbon Arm Tube (OD 30mm, ID 26mm)
        outer_cyl = Part.makeCylinder(ARM_OD / 2.0, ARM_LENGTH, Base.Vector(0, 0, 0), Base.Vector(1, 0, 0))
        inner_cyl = Part.makeCylinder(ARM_ID / 2.0, ARM_LENGTH + 20, Base.Vector(-10, 0, 0), Base.Vector(1, 0, 0))
        tube = outer_cyl.cut(inner_cyl)
        tube.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), angle)
        
        arm_obj = doc.addObject("Part::Feature", f"Carbon_Arm_{idx+1}_{angle}deg")
        arm_obj.Shape = tube
        set_obj_appearance(arm_obj, COLOR_CARBON)

        tip_x = ARM_LENGTH * cos_a
        tip_y = ARM_LENGTH * sin_a

        # Motor Mount Plate (80x80x4mm with 4x M4 PCD 40mm bolt holes)
        mount_solid = Part.makeBox(MOTOR_PLATE_SIZE, MOTOR_PLATE_SIZE, MOTOR_PLATE_THICK, 
                                   Base.Vector(tip_x - MOTOR_PLATE_SIZE/2.0, tip_y - MOTOR_PLATE_SIZE/2.0, ARM_OD/2.0))
        # Cut 4x M4 bolt holes at PCD 40mm (R=20mm)
        for bh_angle in [45, 135, 225, 315]:
            bh_rad = math.radians(bh_angle)
            bx = tip_x + PCD_BOLT_RADIUS * math.cos(bh_rad)
            by = tip_y + PCD_BOLT_RADIUS * math.sin(bh_rad)
            b_hole = Part.makeCylinder(2.2, MOTOR_PLATE_THICK + 4, Base.Vector(bx, by, ARM_OD/2.0 - 2), Base.Vector(0, 0, 1))
            mount_solid = mount_solid.cut(b_hole)
            
            # Add visible M4 Bolt Heads
            b_head = Part.makeCylinder(3.5, 3.0, Base.Vector(bx, by, ARM_OD/2.0 - 3.0), Base.Vector(0, 0, 1))
            b_obj = doc.addObject("Part::Feature", f"Motor_Bolt_{idx+1}_{bh_angle}deg")
            b_obj.Shape = b_head
            set_obj_appearance(b_obj, COLOR_BOLT)

        mount_obj = doc.addObject("Part::Feature", f"Motor_Mount_Plate_{idx+1}")
        mount_obj.Shape = mount_solid
        set_obj_appearance(mount_obj, COLOR_CARBON)

        # Two-Tier Brushless Motor (Stator Base 40mm dia + Rotor Bell 50mm dia)
        stator_base = Part.makeCylinder(20.0, 15.0, Base.Vector(tip_x, tip_y, ARM_OD/2.0 + MOTOR_PLATE_THICK), Base.Vector(0, 0, 1))
        rotor_bell = Part.makeCylinder(25.0, 35.0, Base.Vector(tip_x, tip_y, ARM_OD/2.0 + MOTOR_PLATE_THICK + 15.0), Base.Vector(0, 0, 1))
        
        stator_obj = doc.addObject("Part::Feature", f"TMotor_Stator_{idx+1}")
        stator_obj.Shape = stator_base
        set_obj_appearance(stator_obj, COLOR_MOTOR_STATOR)

        bell_obj = doc.addObject("Part::Feature", f"TMotor_RotorBell_{idx+1}")
        bell_obj.Shape = rotor_bell
        set_obj_appearance(bell_obj, COLOR_MOTOR_BELL)

        # 2-Blade Tapered Propeller Assembly (40" Diameter = 508mm Radius)
        prop_z = ARM_OD/2.0 + MOTOR_PLATE_THICK + 52.0
        prop_hub = Part.makeCylinder(PROP_HUB_RADIUS, 12.0, Base.Vector(tip_x, tip_y, prop_z), Base.Vector(0, 0, 1))
        
        # Blade 1 and Blade 2 (Tapered wedge shapes from 35mm root to 12mm tip)
        p1 = Base.Vector(tip_x + PROP_HUB_RADIUS, tip_y - 17.5, prop_z + 2)
        p2 = Base.Vector(tip_x + PROP_RADIUS, tip_y - 6.0, prop_z + 5)
        p3 = Base.Vector(tip_x + PROP_RADIUS, tip_y + 6.0, prop_z + 5)
        p4 = Base.Vector(tip_x + PROP_HUB_RADIUS, tip_y + 17.5, prop_z + 2)
        
        blade1_poly = Part.makePolygon([p1, p2, p3, p4, p1])
        blade1_face = Part.Face(blade1_poly)
        blade1 = blade1_face.extrude(Base.Vector(0, 0, 6))

        p1_b = Base.Vector(tip_x - PROP_HUB_RADIUS, tip_y + 17.5, prop_z + 2)
        p2_b = Base.Vector(tip_x - PROP_RADIUS, tip_y + 6.0, prop_z + 5)
        p3_b = Base.Vector(tip_x - PROP_RADIUS, tip_y - 6.0, prop_z + 5)
        p4_b = Base.Vector(tip_x - PROP_HUB_RADIUS, tip_y - 17.5, prop_z + 2)
        
        blade2_poly = Part.makePolygon([p1_b, p2_b, p3_b, p4_b, p1_b])
        blade2_face = Part.Face(blade2_poly)
        blade2 = blade2_face.extrude(Base.Vector(0, 0, 6))

        full_prop = prop_hub.fuse(blade1).fuse(blade2)
        # Rotate prop to match arm angle + 90 deg tangent alignment
        full_prop.rotate(Base.Vector(tip_x, tip_y, prop_z), Base.Vector(0, 0, 1), angle + 90)

        prop_obj = doc.addObject("Part::Feature", f"Propeller_40in_2Blade_{idx+1}")
        prop_obj.Shape = full_prop
        set_obj_appearance(prop_obj, COLOR_PROP, transparency=25)

    # 6. LANDING GEAR STRUTS WITH SKID PADS
    lg_angles = [45, 135, 225, 315]
    for idx, angle in enumerate(lg_angles):
        rad = math.radians(angle)
        x_base = (CENTER_HEX_RADIUS - 30) * math.cos(rad)
        y_base = (CENTER_HEX_RADIUS - 30) * math.sin(rad)
        z_bottom = -STANDOFF_HEIGHT/2.0 - LANDING_GEAR_HEIGHT
        
        # Strut tube
        leg = Part.makeCylinder(LANDING_GEAR_OD / 2.0, LANDING_GEAR_HEIGHT, 
                                Base.Vector(x_base, y_base, z_bottom), Base.Vector(0, 0, 1))
        leg_obj = doc.addObject("Part::Feature", f"Landing_Leg_{idx+1}")
        leg_obj.Shape = leg
        set_obj_appearance(leg_obj, COLOR_CARBON)

        # Skid Foot Pad (140mm x 40mm x 12mm box base with rounded ends)
        skid_pad = Part.makeBox(SKID_FOOT_LENGTH, SKID_FOOT_WIDTH, 12, 
                                Base.Vector(x_base - SKID_FOOT_LENGTH/2.0, y_base - SKID_FOOT_WIDTH/2.0, z_bottom - 12))
        skid_obj = doc.addObject("Part::Feature", f"Skid_Foot_Pad_{idx+1}")
        skid_obj.Shape = skid_pad
        set_obj_appearance(skid_obj, COLOR_CARBON)

    # Recompute document and refresh GUI viewports
    doc.recompute()
    
    if GUI_AVAILABLE:
        try:
            Gui.SendMsgToActiveView("ViewFit")
            Gui.updateGui()
        except Exception:
            pass

    # PRINT COMPLETE OBJECT TREE SUMMARY
    doc_objs = doc.Objects
    print("\n=======================================================================")
    print(f" FREECAD HIGH-FIDELITY DOCUMENT TREE INVENTORY (Total Objects: {len(doc_objs)})")
    print("=======================================================================")
    for i, o in enumerate(doc_objs, 1):
        print(f" {i:02d}. [{o.TypeId.split('::')[-1]}] {o.Label}")
    print("=======================================================================\n")

    # Export STEP file if path provided
    if output_step_path:
        os.makedirs(os.path.dirname(output_step_path), exist_ok=True)
        Part.export([obj.Shape for obj in doc.Objects], output_step_path)
        print(f"STEP assembly successfully exported to: {output_step_path}")
        
    return True

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    step_out = os.path.join(script_dir, "hexacopter_assembly.step")
    build_hexacopter_freecad_assembly(step_out)
