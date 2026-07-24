import uuid
import re
import os
import subprocess

def gen_uuid():
    return str(uuid.uuid4())

def extract_symbol(lib_path, symbol_name):
    with open(lib_path, "r") as f:
        content = f.read()
    
    target = f'(symbol "{symbol_name}"'
    idx = content.find(target)
    if idx == -1:
        target = f'(symbol {symbol_name}'
        idx = content.find(target)
        if idx == -1:
            raise ValueError(f"Symbol {symbol_name} not found in {lib_path}")
            
    paren_count = 0
    start_idx = idx
    for i in range(start_idx, len(content)):
        char = content[i]
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
            if paren_count == 0:
                return content[start_idx:i+1]
                
    raise ValueError(f"Unmatched parenthesis for symbol {symbol_name}")

# Standard local pin definitions for Connector_Generic symbols
# format: {symbol_name: {pin_num: (x_local, y_local)}}
PIN_LAYOUTS = {
    "Conn_01x02": {
        1: (-5.08, 0.0),
        2: (-5.08, -2.54)
    },
    "Conn_01x03": {
        1: (-5.08, 2.54),
        2: (-5.08, 0.0),
        3: (-5.08, -2.54)
    },
    "Conn_01x04": {
        1: (-5.08, 2.54),
        2: (-5.08, 0.0),
        3: (-5.08, -2.54),
        4: (-5.08, -5.08)
    },
    "Conn_01x06": {
        1: (-5.08, 5.08),
        2: (-5.08, 2.54),
        3: (-5.08, 0.0),
        4: (-5.08, -2.54),
        5: (-5.08, -5.08),
        6: (-5.08, -7.62)
    },
    "Conn_01x07": {
        1: (-5.08, 7.62),
        2: (-5.08, 5.08),
        3: (-5.08, 2.54),
        4: (-5.08, 0.0),
        5: (-5.08, -2.54),
        6: (-5.08, -5.08),
        7: (-5.08, -7.62)
    },
    "Conn_01x16": {
        1: (-5.08, 17.78),
        2: (-5.08, 15.24),
        3: (-5.08, 12.7),
        4: (-5.08, 10.16),
        5: (-5.08, 7.62),
        6: (-5.08, 5.08),
        7: (-5.08, 2.54),
        8: (-5.08, 0.0),
        9: (-5.08, -2.54),
        10: (-5.08, -5.08),
        11: (-5.08, -7.62),
        12: (-5.08, -10.16),
        13: (-5.08, -12.7),
        14: (-5.08, -15.24),
        15: (-5.08, -17.78),
        16: (-5.08, -20.32)
    },
    "Conn_01x18": {
        1: (-5.08, 20.32),
        2: (-5.08, 17.78),
        3: (-5.08, 15.24),
        4: (-5.08, 12.7),
        5: (-5.08, 10.16),
        6: (-5.08, 7.62),
        7: (-5.08, 5.08),
        8: (-5.08, 2.54),
        9: (-5.08, 0.0),
        10: (-5.08, -2.54),
        11: (-5.08, -5.08),
        12: (-5.08, -7.62),
        13: (-5.08, -10.16),
        14: (-5.08, -12.7),
        15: (-5.08, -15.24),
        16: (-5.08, -17.78),
        17: (-5.08, -20.32),
        18: (-5.08, -22.86)
    }
}

class Component:
    def __init__(self, name, lib_id, value, x, y, angle, num_pins):
        self.name = name
        self.lib_id = lib_id  # e.g. "Connector_Generic:Conn_01x04"
        self.value = value
        self.x = x
        self.y = y
        self.angle = angle
        self.num_pins = num_pins
        
    def get_pin_abs(self, pin_num):
        symbol_name = self.lib_id.split(":")[1]
        x_local, y_local = PIN_LAYOUTS[symbol_name][pin_num]
        
        if self.angle == 0:
            return (self.x + x_local, self.y - y_local)
        elif self.angle == 90:
            return (self.x - y_local, self.y - x_local)
        elif self.angle == 180:
            return (self.x - x_local, self.y + y_local)
        elif self.angle == 270:
            return (self.x + y_local, self.y + x_local)
        else:
            raise ValueError(f"Unsupported angle: {self.angle}")

def format_wire(p1, p2):
    return f"  (wire (pts (xy {round(p1[0], 2)} {round(p1[1], 2)}) (xy {round(p2[0], 2)} {round(p2[1], 2)})) (stroke (width 0) (type solid)) (uuid \"{gen_uuid()}\"))"

def split_and_find_junctions(raw_wires):
    # Normalize segments so x1 <= x2 and y1 <= y2
    segments = []
    for p1, p2 in raw_wires:
        x1, y1 = p1
        x2, y2 = p2
        x1, y1 = round(x1, 2), round(y1, 2)
        x2, y2 = round(x2, 2), round(y2, 2)
        if x1 > x2 or (x1 == x2 and y1 > y2):
            segments.append(((x2, y2), (x1, y1)))
        else:
            segments.append(((x1, y1), (x2, y2)))
            
    # Keep splitting segments until no more splits occur
    while True:
        split_occurred = False
        new_segments = []
        endpoints = set()
        for p1, p2 in segments:
            endpoints.add(p1)
            endpoints.add(p2)
            
        for seg in segments:
            p1, p2 = seg
            x1, y1 = p1
            x2, y2 = p2
            
            split_pt = None
            for ep in endpoints:
                ex, ey = ep
                if ep == p1 or ep == p2:
                    continue
                # If segment is horizontal
                if abs(y1 - y2) < 0.01 and abs(ey - y1) < 0.01:
                    if x1 < ex < x2:
                        split_pt = ep
                        break
                # If segment is vertical
                elif abs(x1 - x2) < 0.01 and abs(ex - x1) < 0.01:
                    if y1 < ey < y2:
                        split_pt = ep
                        break
            
            if split_pt:
                new_segments.append((p1, split_pt))
                new_segments.append((split_pt, p2))
                split_occurred = True
            else:
                new_segments.append(seg)
                
        segments = list(set(new_segments))  # Remove duplicates
        if not split_occurred:
            break
            
    # Count occurrences of each endpoint
    endpoint_counts = {}
    for p1, p2 in segments:
        endpoint_counts[p1] = endpoint_counts.get(p1, 0) + 1
        endpoint_counts[p2] = endpoint_counts.get(p2, 0) + 1
        
    junctions = []
    for pt, count in endpoint_counts.items():
        if count >= 3:
            junctions.append(pt)
            
    return segments, junctions

def main():
    target_path = "/home/bishu/quadcopter-autonomy/projects/heavy-lift-uav/kicad/power_and_signal_schematic.kicad_sch"
    
    # 1. Define component list
    components = {}
    
    # Left column: Generator & Jetson Orin Nano
    components["GEN1"] = Component("GEN1", "Connector_Generic:Conn_01x04", "3.6kW Hybrid Generator", 50.8, 76.2, 0, 4)
    components["COMP1"] = Component("COMP1", "Connector_Generic:Conn_01x06", "Jetson Orin Nano", 50.8, 215.9, 0, 6)
    
    # Middle column: Battery & BMS & Pixhawk 6X
    components["BAT1"] = Component("BAT1", "Connector_Generic:Conn_01x02", "12S LiPo Battery", 88.9, 139.7, 0, 2)
    components["BMS1"] = Component("BMS1", "Connector_Generic:Conn_01x06", "BMS Ideal Diode", 127.0, 76.2, 0, 6)
    components["FC1"] = Component("FC1", "Connector_Generic:Conn_01x18", "Pixhawk 6X", 127.0, 215.9, 0, 18)
    
    # Right-middle column: PDB & Regulators & Peripherals
    components["PDB1"] = Component("PDB1", "Connector_Generic:Conn_01x16", "Power Distribution Board", 190.5, 76.2, 180, 16)
    components["REG1"] = Component("REG1", "Connector_Generic:Conn_01x04", "DC-DC 12V 10A", 190.5, 165.1, 0, 4)
    
    # Move REG2 to Y = 187.96 to completely resolve all 5V power and signal collisions!
    components["REG2"] = Component("REG2", "Connector_Generic:Conn_01x04", "DC-DC 5V 10A", 190.5, 187.96, 0, 4)
    
    components["GPS1"] = Component("GPS1", "Connector_Generic:Conn_01x04", "Here3 GPS RTK 1", 254.0, 215.9, 0, 4)
    components["GPS2"] = Component("GPS2", "Connector_Generic:Conn_01x04", "Here3 GPS RTK 2", 254.0, 234.95, 0, 4)
    components["TEL1"] = Component("TEL1", "Connector_Generic:Conn_01x04", "RFD900 Telemetry", 254.0, 260.35, 0, 4)
    
    # 12V Payload Connector
    components["J_PAYLOAD"] = Component("J_PAYLOAD", "Connector_Generic:Conn_01x02", "12V Payload", 254.0, 170.18, 180, 2)
    
    # Right column: ESCs & Motors (6 channels)
    y_levels = [38.1, 76.2, 114.3, 152.4, 190.5, 228.6]
    for i, y_val in enumerate(y_levels):
        idx = i + 1
        components[f"ESC{idx}"] = Component(f"ESC{idx}", "Connector_Generic:Conn_01x07", f"Flame120A ESC {idx}", 292.1, y_val, 0, 7)
        components[f"M{idx}"] = Component(f"M{idx}", "Connector_Generic:Conn_01x03", f"T-Motor U15 II {idx}", 355.6, y_val, 0, 3)
        
    # 2. Extract S-expression symbol definitions from standard library
    lib_path = "/usr/share/kicad/symbols/Connector_Generic.kicad_sym"
    symbol_defs = []
    symbol_names = ["Conn_01x02", "Conn_01x03", "Conn_01x04", "Conn_01x06", "Conn_01x07", "Conn_01x16", "Conn_01x18"]
    for name in symbol_names:
        raw_def = extract_symbol(lib_path, name)
        renamed_def = raw_def.replace(f'(symbol "{name}"', f'(symbol "Connector_Generic:{name}"')
        symbol_defs.append(renamed_def)
        
    # 3. Build the schematic content
    lines = []
    lines.append(f'(kicad_sch (version 20241209) (generator "eeschema") (generator_version "9.0")')
    lines.append(f'  (uuid "{gen_uuid()}")')
    lines.append(f'  (paper "A3")')
    
    # Title Block
    lines.append(f'  (title_block')
    lines.append(f'    (title "Heavy-Lift Gas-Electric Hybrid Hexacopter - Power & Signal Schematic")')
    lines.append(f'    (date "2026-07-22")')
    lines.append(f'    (rev "1.8")')
    lines.append(f'    (company "Flight Systems Division")')
    lines.append(f'    (comment 1 "Locked Baseline (DESIGN_LOCK.md): 6 Arms @ 60 deg (L=1.12m), 40in Props, 3460.1W Hover Power, TOW 34.575kg")')
    lines.append(f'    (comment 2 "Power Distribution: 48V Bus, 72.1A Total Hover Current (12.02A/Branch), 75A Gen Max Output")')
    lines.append(f'    (comment 3 "Safety Factor & Peak Rating: 120A Flame ESCs, 100A BMS Battery Failsafe Coupling")')
    lines.append(f'  )')
    
    # Library symbols block
    lines.append(f'  (lib_symbols')
    for sym_def in symbol_defs:
        lines.append(sym_def)
    lines.append(f'  )')
    
    # Place all component instances
    for comp in components.values():
        lines.append(make_symbol_instance(comp.lib_id, comp.name, comp.value, comp.x, comp.y, comp.angle, comp.num_pins))
        
    # Collect all wires as raw segments
    raw_wires = []
    labels = []
    no_connects = []
    
    # Helper to route Orthogonal paths
    def route_ortho(p1, p2, x_mid):
        pts = [p1, (x_mid, p1[1]), (x_mid, p2[1]), p2]
        filtered_pts = []
        for pt in pts:
            if not filtered_pts or filtered_pts[-1] != pt:
                filtered_pts.append(pt)
        for i in range(len(filtered_pts) - 1):
            raw_wires.append((filtered_pts[i], filtered_pts[i+1]))
            
    # Connect GEN1 DC+ (Pin 1) to PDB1 VIN+ (Pin 1)
    p_gen_pos = components["GEN1"].get_pin_abs(1)
    p_pdb_pos = components["PDB1"].get_pin_abs(1)
    route_pts = [p_gen_pos, (38.1, p_gen_pos[1]), (38.1, 53.34), (205.74, 53.34), (205.74, p_pdb_pos[1]), p_pdb_pos]
    for i in range(len(route_pts)-1):
        raw_wires.append((route_pts[i], route_pts[i+1]))
    labels.append(f'  (label "48V_BUS" (at 114.3 53.34 0) (effects (font (size 1.27 1.27))))')
    
    # Connect GEN1 DC- (Pin 2) to PDB1 VIN- (Pin 2)
    p_gen_neg = components["GEN1"].get_pin_abs(2)
    p_pdb_neg = components["PDB1"].get_pin_abs(2)
    route_pts = [p_gen_neg, (35.56, p_gen_neg[1]), (35.56, 50.8), (208.28, 50.8), (208.28, p_pdb_neg[1]), p_pdb_neg]
    for i in range(len(route_pts)-1):
        raw_wires.append((route_pts[i], route_pts[i+1]))
    labels.append(f'  (label "GND_BUS" (at 111.76 50.8 0) (effects (font (size 1.27 1.27))))')
    
    # Connect BAT1 to BMS1 IN (Pins 3, 4)
    # BAT1 Pin 1 to BMS1 Pin 3 (IN_BAT+), middle X = 96.52
    p_bat_pos = components["BAT1"].get_pin_abs(1)
    p_bms_in_pos = components["BMS1"].get_pin_abs(3)
    route_ortho(p_bat_pos, p_bms_in_pos, 96.52)
    labels.append(f'  (label "BAT_V+" (at 96.52 139.7 0) (effects (font (size 1.27 1.27))))')
    
    # BAT1 Pin 2 to BMS1 Pin 4 (IN_BAT-), middle X = 101.6
    p_bat_neg = components["BAT1"].get_pin_abs(2)
    p_bms_in_neg = components["BMS1"].get_pin_abs(4)
    route_ortho(p_bat_neg, p_bms_in_neg, 101.6)
    labels.append(f'  (label "BAT_V-" (at 101.6 142.24 0) (effects (font (size 1.27 1.27))))')
    
    # Connect BMS1 OUT+ (Pin 1) to the positive DC bus wire
    p_bms_out_pos = components["BMS1"].get_pin_abs(1)
    route_pts = [p_bms_out_pos, (114.3, p_bms_out_pos[1]), (114.3, 53.34)]
    for i in range(len(route_pts)-1):
        raw_wires.append((route_pts[i], route_pts[i+1]))
        
    # Connect BMS1 OUT- (Pin 2) to the negative DC bus wire
    p_bms_out_neg = components["BMS1"].get_pin_abs(2)
    route_pts = [p_bms_out_neg, (111.76, p_bms_out_neg[1]), (111.76, 50.8)]
    for i in range(len(route_pts)-1):
        raw_wires.append((route_pts[i], route_pts[i+1]))
        
    # Connect PDB1 ESC outputs to local labels (short 7.62 mm wires)
    # This completely eliminates vertical crossing wires in the center area!
    for i in range(6):
        idx = i + 1
        p_pdb_esc_pos = components["PDB1"].get_pin_abs(3 + i*2)
        p_pdb_esc_neg = components["PDB1"].get_pin_abs(4 + i*2)
        
        raw_wires.append((p_pdb_esc_pos, (p_pdb_esc_pos[0] + 7.62, p_pdb_esc_pos[1])))
        labels.append(f'  (label "ESC{idx}_V+" (at {round(p_pdb_esc_pos[0] + 7.62, 2)} {p_pdb_esc_pos[1]} 0) (effects (font (size 1.27 1.27))))')
        
        raw_wires.append((p_pdb_esc_neg, (p_pdb_esc_neg[0] + 7.62, p_pdb_esc_neg[1])))
        labels.append(f'  (label "ESC{idx}_V-" (at {round(p_pdb_esc_neg[0] + 7.62, 2)} {p_pdb_esc_neg[1]} 0) (effects (font (size 1.27 1.27))))')
        
    # Connect ESC power inputs to local labels (short 7.62 mm wires)
    for idx in range(1, 7):
        esc_key = f"ESC{idx}"
        p_esc_pos = components[esc_key].get_pin_abs(1)
        p_esc_neg = components[esc_key].get_pin_abs(2)
        
        raw_wires.append((p_esc_pos, (p_esc_pos[0] - 7.62, p_esc_pos[1])))
        labels.append(f'  (label "ESC{idx}_V+" (at {round(p_esc_pos[0] - 7.62, 2)} {p_esc_pos[1]} 180) (effects (font (size 1.27 1.27))))')
        
        raw_wires.append((p_esc_neg, (p_esc_neg[0] - 7.62, p_esc_neg[1])))
        labels.append(f'  (label "ESC{idx}_V-" (at {round(p_esc_neg[0] - 7.62, 2)} {p_esc_neg[1]} 180) (effects (font (size 1.27 1.27))))')
        
    # Connect ESC outputs to Motors (spaced x_mid to prevent overlaps)
    for i in range(6):
        idx = i + 1
        esc_key = f"ESC{idx}"
        m_key = f"M{idx}"
        for p in [5, 6, 7]:
            p_esc_out = components[esc_key].get_pin_abs(p)
            p_m_in = components[m_key].get_pin_abs(p - 4)
            x_mid = 323.85 + (p - 6) * 2.54
            route_ortho(p_esc_out, p_m_in, x_mid)
            
            phase_char = ["A", "B", "C"][p - 5]
            labels.append(f'  (label "M{idx}_{phase_char}" (at {round((287.02 + x_mid)/2, 2)} {p_esc_out[1]} 0) (effects (font (size 1.27 1.27))))')
            
    # Connect PDB1 AUX outputs to REG1 and REG2 inputs
    p_pdb_aux_pos = components["PDB1"].get_pin_abs(15)
    p_pdb_aux_neg = components["PDB1"].get_pin_abs(16)
    
    p_reg1_in_pos = components["REG1"].get_pin_abs(1)
    p_reg1_in_neg = components["REG1"].get_pin_abs(2)
    p_reg2_in_pos = components["REG2"].get_pin_abs(1)
    p_reg2_in_neg = components["REG2"].get_pin_abs(2)
    
    route_ortho(p_pdb_aux_pos, p_reg1_in_pos, 177.8)
    route_ortho(p_pdb_aux_pos, p_reg2_in_pos, 177.8)
    labels.append(f'  (label "AUX_V+" (at 177.8 58.42 0) (effects (font (size 1.27 1.27))))')
    
    route_ortho(p_pdb_aux_neg, p_reg1_in_neg, 175.26)
    route_ortho(p_pdb_aux_neg, p_reg2_in_neg, 175.26)
    labels.append(f'  (label "AUX_V-" (at 175.26 55.88 0) (effects (font (size 1.27 1.27))))')
    
    # Connect REG1 VOUT+ (Pin 3) and VOUT- (Pin 4) to J_PAYLOAD Pin 2 & Pin 1
    p_reg1_out_pos = components["REG1"].get_pin_abs(3)
    p_reg1_out_neg = components["REG1"].get_pin_abs(4)
    p_payload_pos = components["J_PAYLOAD"].get_pin_abs(1)
    p_payload_neg = components["J_PAYLOAD"].get_pin_abs(2)
    
    raw_wires.append((p_reg1_out_pos, p_payload_neg))
    labels.append(f'  (label "VCC_12V" (at 198.12 167.64 0) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_reg1_out_neg, p_payload_pos))
    labels.append(f'  (label "GND_12V" (at 198.12 170.18 0) (effects (font (size 1.27 1.27))))')
    
    # Connect REG2 VOUT+ (Pin 3) and VOUT- (Pin 4) to FC1 (Pins 1, 2) and COMP1 (Pins 1, 2) via local labels
    p_reg2_out_pos = components["REG2"].get_pin_abs(3)
    p_reg2_out_neg = components["REG2"].get_pin_abs(4)
    p_fc_pow = components["FC1"].get_pin_abs(1)
    p_fc_gnd = components["FC1"].get_pin_abs(2)
    p_comp_pow = components["COMP1"].get_pin_abs(1)
    p_comp_gnd = components["COMP1"].get_pin_abs(2)
    
    # REG2 outputs
    raw_wires.append((p_reg2_out_pos, (p_reg2_out_pos[0] - 7.62, p_reg2_out_pos[1])))
    labels.append(f'  (label "VCC_5V" (at {round(p_reg2_out_pos[0] - 7.62, 2)} {p_reg2_out_pos[1]} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_reg2_out_neg, (p_reg2_out_neg[0] - 7.62, p_reg2_out_neg[1])))
    labels.append(f'  (label "GND_5V" (at {round(p_reg2_out_neg[0] - 7.62, 2)} {p_reg2_out_neg[1]} 180) (effects (font (size 1.27 1.27))))')
    
    # FC1 power inputs
    raw_wires.append((p_fc_pow, (p_fc_pow[0] - 7.62, p_fc_pow[1])))
    labels.append(f'  (label "VCC_5V" (at {round(p_fc_pow[0] - 7.62, 2)} {p_fc_pow[1]} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_fc_gnd, (p_fc_gnd[0] - 7.62, p_fc_gnd[1])))
    labels.append(f'  (label "GND_5V" (at {round(p_fc_gnd[0] - 7.62, 2)} {p_fc_gnd[1]} 180) (effects (font (size 1.27 1.27))))')
    
    # COMP1 power inputs
    raw_wires.append((p_comp_pow, (p_comp_pow[0] - 7.62, p_comp_pow[1])))
    labels.append(f'  (label "VCC_5V" (at {round(p_comp_pow[0] - 7.62, 2)} {p_comp_pow[1]} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_comp_gnd, (p_comp_gnd[0] - 7.62, p_comp_gnd[1])))
    labels.append(f'  (label "GND_5V" (at {round(p_comp_gnd[0] - 7.62, 2)} {p_comp_gnd[1]} 180) (effects (font (size 1.27 1.27))))')
    
    # GPS1 power (Pins 1, 2) to VCC_5V / GND_5V (7.62 mm wires)
    p_gps1_vcc = components["GPS1"].get_pin_abs(1)
    p_gps1_gnd = components["GPS1"].get_pin_abs(2)
    raw_wires.append((p_gps1_vcc, (p_gps1_vcc[0] - 7.62, p_gps1_vcc[1])))
    labels.append(f'  (label "VCC_5V" (at {round(p_gps1_vcc[0] - 7.62, 2)} {round(p_gps1_vcc[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_gps1_gnd, (p_gps1_gnd[0] - 7.62, p_gps1_gnd[1])))
    labels.append(f'  (label "GND_5V" (at {round(p_gps1_gnd[0] - 7.62, 2)} {round(p_gps1_gnd[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # GPS2 power and CAN (Pins 1-4) (7.62 mm wires)
    p_gps2_vcc = components["GPS2"].get_pin_abs(1)
    p_gps2_gnd = components["GPS2"].get_pin_abs(2)
    p_gps2_can_h = components["GPS2"].get_pin_abs(3)
    p_gps2_can_l = components["GPS2"].get_pin_abs(4)
    raw_wires.append((p_gps2_vcc, (p_gps2_vcc[0] - 7.62, p_gps2_vcc[1])))
    labels.append(f'  (label "VCC_5V" (at {round(p_gps2_vcc[0] - 7.62, 2)} {round(p_gps2_vcc[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_gps2_gnd, (p_gps2_gnd[0] - 7.62, p_gps2_gnd[1])))
    labels.append(f'  (label "GND_5V" (at {round(p_gps2_gnd[0] - 7.62, 2)} {round(p_gps2_gnd[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_gps2_can_h, (p_gps2_can_h[0] - 7.62, p_gps2_can_h[1])))
    labels.append(f'  (label "CAN_H" (at {round(p_gps2_can_h[0] - 7.62, 2)} {round(p_gps2_can_h[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_gps2_can_l, (p_gps2_can_l[0] - 7.62, p_gps2_can_l[1])))
    labels.append(f'  (label "CAN_L" (at {round(p_gps2_can_l[0] - 7.62, 2)} {round(p_gps2_can_l[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # TEL1 power (Pins 1, 2) (7.62 mm wires)
    p_tel1_vcc = components["TEL1"].get_pin_abs(1)
    p_tel1_gnd = components["TEL1"].get_pin_abs(2)
    raw_wires.append((p_tel1_vcc, (p_tel1_vcc[0] - 7.62, p_tel1_vcc[1])))
    labels.append(f'  (label "VCC_5V" (at {round(p_tel1_vcc[0] - 7.62, 2)} {round(p_tel1_vcc[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_tel1_gnd, (p_tel1_gnd[0] - 7.62, p_tel1_gnd[1])))
    labels.append(f'  (label "GND_5V" (at {round(p_tel1_gnd[0] - 7.62, 2)} {round(p_tel1_gnd[1], 2)} 180) (effects (font (size 1.27 1.27))))')

    # FC1 PWM 1 to 6 to labels (7.62 mm wires)
    for idx in range(1, 7):
        p_fc_pwm = components["FC1"].get_pin_abs(8 + idx) # Pin 9 is PWM1
        raw_wires.append((p_fc_pwm, (p_fc_pwm[0] + 7.62, p_fc_pwm[1])))
        labels.append(f'  (label "PWM_{idx}" (at {round(p_fc_pwm[0] + 7.62, 2)} {round(p_fc_pwm[1], 2)} 0) (effects (font (size 1.27 1.27))))')
        
    # ESC1 to ESC6 PWM input to labels (7.62 mm wires)
    for idx in range(1, 7):
        p_esc_pwm = components[f"ESC{idx}"].get_pin_abs(3) # Pin 3 is PWM
        raw_wires.append((p_esc_pwm, (p_esc_pwm[0] - 7.62, p_esc_pwm[1])))
        labels.append(f'  (label "PWM_{idx}" (at {round(p_esc_pwm[0] - 7.62, 2)} {round(p_esc_pwm[1], 2)} 180) (effects (font (size 1.27 1.27))))')
        
    # FC1 CAN1 (Pins 3, 4) to labels (7.62 mm wires)
    p_fc_can_h = components["FC1"].get_pin_abs(3)
    p_fc_can_l = components["FC1"].get_pin_abs(4)
    raw_wires.append((p_fc_can_h, (p_fc_can_h[0] - 7.62, p_fc_can_h[1])))
    labels.append(f'  (label "CAN_H" (at {round(p_fc_can_h[0] - 7.62, 2)} {round(p_fc_can_h[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_fc_can_l, (p_fc_can_l[0] - 7.62, p_fc_can_l[1])))
    labels.append(f'  (label "CAN_L" (at {round(p_fc_can_l[0] - 7.62, 2)} {round(p_fc_can_l[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # GEN1 CAN (Pins 3, 4) to labels (7.62 mm wires)
    p_gen_can_h = components["GEN1"].get_pin_abs(3)
    p_gen_can_l = components["GEN1"].get_pin_abs(4)
    raw_wires.append((p_gen_can_h, (p_gen_can_h[0] - 7.62, p_gen_can_h[1])))
    labels.append(f'  (label "CAN_H" (at {round(p_gen_can_h[0] - 7.62, 2)} {round(p_gen_can_h[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_gen_can_l, (p_gen_can_l[0] - 7.62, p_gen_can_l[1])))
    labels.append(f'  (label "CAN_L" (at {round(p_gen_can_l[0] - 7.62, 2)} {round(p_gen_can_l[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # BMS1 CAN (Pins 5, 6) to labels (7.62 mm wires)
    p_bms_can_h = components["BMS1"].get_pin_abs(5)
    p_bms_can_l = components["BMS1"].get_pin_abs(6)
    raw_wires.append((p_bms_can_h, (p_bms_can_h[0] - 7.62, p_bms_can_h[1])))
    labels.append(f'  (label "CAN_H" (at {round(p_bms_can_h[0] - 7.62, 2)} {round(p_bms_can_h[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_bms_can_l, (p_bms_can_l[0] - 7.62, p_bms_can_l[1])))
    labels.append(f'  (label "CAN_L" (at {round(p_bms_can_l[0] - 7.62, 2)} {round(p_bms_can_l[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # Ethernet link between FC1 (Pins 15-18) and COMP1 (Pins 3-6) (7.62 mm wires)
    eth_pins = [("ETH_TX_P", 15, 5), ("ETH_TX_N", 16, 6), ("ETH_RX_P", 17, 3), ("ETH_RX_N", 18, 4)]
    for label_val, fc_pin, comp_pin in eth_pins:
        p_fc = components["FC1"].get_pin_abs(fc_pin)
        p_comp = components["COMP1"].get_pin_abs(comp_pin)
        
        # Place label on FC1 side (pointing left)
        raw_wires.append((p_fc, (p_fc[0] - 7.62, p_fc[1])))
        labels.append(f'  (label "{label_val}" (at {round(p_fc[0] - 7.62, 2)} {round(p_fc[1], 2)} 180) (effects (font (size 1.27 1.27))))')
        
        # Place label on COMP1 side (pointing left)
        raw_wires.append((p_comp, (p_comp[0] - 7.62, p_comp[1])))
        labels.append(f'  (label "{label_val}" (at {round(p_comp[0] - 7.62, 2)} {round(p_comp[1], 2)} 180) (effects (font (size 1.27 1.27))))')
        
    # FC1 GPS (Pins 5, 6) to labels (7.62 mm wires)
    p_fc_gps_tx = components["FC1"].get_pin_abs(5)
    p_fc_gps_rx = components["FC1"].get_pin_abs(6)
    raw_wires.append((p_fc_gps_tx, (p_fc_gps_tx[0] - 7.62, p_fc_gps_tx[1])))
    labels.append(f'  (label "GPS_TXD" (at {round(p_fc_gps_tx[0] - 7.62, 2)} {round(p_fc_gps_tx[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_fc_gps_rx, (p_fc_gps_rx[0] - 7.62, p_fc_gps_rx[1])))
    labels.append(f'  (label "GPS_RXD" (at {round(p_fc_gps_rx[0] - 7.62, 2)} {round(p_fc_gps_rx[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # GPS1 RX/TX (Pins 4, 3) to labels (7.62 mm wires)
    p_gps1_rx = components["GPS1"].get_pin_abs(4)
    p_gps1_tx = components["GPS1"].get_pin_abs(3)
    raw_wires.append((p_gps1_rx, (p_gps1_rx[0] - 7.62, p_gps1_rx[1])))
    labels.append(f'  (label "GPS_TXD" (at {round(p_gps1_rx[0] - 7.62, 2)} {round(p_gps1_rx[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_gps1_tx, (p_gps1_tx[0] - 7.62, p_gps1_tx[1])))
    labels.append(f'  (label "GPS_RXD" (at {round(p_gps1_tx[0] - 7.62, 2)} {round(p_gps1_tx[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # FC1 Telemetry (Pins 7, 8) to labels (7.62 mm wires)
    p_fc_tel_tx = components["FC1"].get_pin_abs(7)
    p_fc_tel_rx = components["FC1"].get_pin_abs(8)
    raw_wires.append((p_fc_tel_tx, (p_fc_tel_tx[0] - 7.62, p_fc_tel_tx[1])))
    labels.append(f'  (label "TEL_TXD" (at {round(p_fc_tel_tx[0] - 7.62, 2)} {round(p_fc_tel_tx[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_fc_tel_rx, (p_fc_tel_rx[0] - 7.62, p_fc_tel_rx[1])))
    labels.append(f'  (label "TEL_RXD" (at {round(p_fc_tel_rx[0] - 7.62, 2)} {round(p_fc_tel_rx[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # TEL1 RX/TX (Pins 4, 3) to labels (7.62 mm wires)
    p_tel1_rx = components["TEL1"].get_pin_abs(4)
    p_tel1_tx = components["TEL1"].get_pin_abs(3)
    raw_wires.append((p_tel1_rx, (p_tel1_rx[0] - 7.62, p_tel1_rx[1])))
    labels.append(f'  (label "TEL_TXD" (at {round(p_tel1_rx[0] - 7.62, 2)} {round(p_tel1_rx[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    raw_wires.append((p_tel1_tx, (p_tel1_tx[0] - 7.62, p_tel1_tx[1])))
    labels.append(f'  (label "TEL_RXD" (at {round(p_tel1_tx[0] - 7.62, 2)} {round(p_tel1_tx[1], 2)} 180) (effects (font (size 1.27 1.27))))')
    
    # Unconnected pins list for no_connects
    for idx in range(1, 7):
        p_esc_nc = components[f"ESC{idx}"].get_pin_abs(4) # Pin 4 is unconnected telemetry
        no_connects.append(p_esc_nc)
        
    # Split wires and calculate junctions
    split_wires, junctions = split_and_find_junctions(raw_wires)
    
    # Write wires to lines
    for p1, p2 in split_wires:
        lines.append(format_wire(p1, p2))
        
    # Write junctions to lines
    for j in junctions:
        lines.append(f'  (junction (at {round(j[0], 2)} {round(j[1], 2)}) (diameter 1.016) (color 0 0 0 0) (uuid "{gen_uuid()}"))')
        
    # Write no_connects to lines
    for nc in no_connects:
        lines.append(f'  (no_connect (at {round(nc[0], 2)} {round(nc[1], 2)}) (uuid "{gen_uuid()}"))')
        
    # Write labels to lines
    for lbl in labels:
        lines.append(lbl)
        
    # Graphical text annotations
    lines.append(f'  (text "HEAVY-LIFT UAV MAIN POWER PATH (48V HYBRID DC BUS)" (at 40 40 0) (effects (font (size 2.5 2.5) bold)))')
    lines.append(f'  (text "1. HYBRID GENERATOR & RECTIFIER SYSTEM\\n- Output: 3.6 kW Continuous (48V DC, 75A Max)\\n- Fuel: Gasoline 2-Stroke Gen\\n- Cable Rating: 48V_BUS, MAX 75A" (at 40 55 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "2. BUFFER BATTERY & BMS FAILSAFE\\n- Battery: 12S LiPo (44.4V - 50.4V, 4500mAh 45C)\\n- Failsafe BMS Parallel Coupling (Ideal Diode)\\n- Cable Rating: BAT_BUS, MAX 100A PEAK" (at 85 115 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "3. MAIN POWER DISTRIBUTION BOARD (PDB)\\n- Input: 48V DC Bus (Total Hover Power: 3,460.1 W @ 72.1A Total)\\n- 6x ESC Branch Outputs: 48V DC, 12.02A Hover / 60A Peak per Branch" (at 175 30 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "AVIONICS & CONTROL SIGNAL ARCHITECTURE" (at 40 198 0) (effects (font (size 2.5 2.5) bold)))')
    lines.append(f'  (text "1. FLIGHT CONTROLLER (Pixhawk 6X)\\n- PWM Outputs [PWM_1 .. PWM_6] -> 6x ESC Signal Inputs\\n- Telemetry 1 -> 915 MHz RF Telemetry Radio (1W Output)\\n- GPS / RTK -> Dual Neo-3 GPS/RTK Receivers (Serial GPS1 + CAN GPS2)\\n- CAN Bus [CAN1_H/L] -> Hybrid Generator ECU Telemetry, BMS, and GPS2\\n- Companion Computer -> Ethernet MAVLink to Nvidia Jetson Orin Nano" (at 110 268 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "2. COMPANION COMPUTER\\n- Model: Nvidia Jetson Orin Nano\\n- High-level autonomy and payload interface\\n- Powered by DC-DC 5V Regulator" (at 30 258 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "3. REGULATED RAIL OUTPUTS\\n- REG1: 12V 10A Rail for Video Tx / Camera Gimbal\\n- REG2: 5V 10A Rail for Flight Controller & Jetson Orin" (at 175 125 0) (effects (font (size 1.8 1.8))))')
    
    # Close schematic
    lines.append(f')')
    
    # Write output
    with open(target_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Successfully generated v9 schematic at {target_path}")

def make_symbol_instance(lib_id, ref, val, x, y, angle, num_pins):
    inst_uuid = gen_uuid()
    prop_ref_y = y - 7.62
    prop_val_y = y + 7.62
    if num_pins > 4:
        prop_ref_y = y - (num_pins * 1.27 + 2.54)
        prop_val_y = y + (num_pins * 1.27 + 2.54)
        
    lines = []
    lines.append(f'  (symbol (lib_id "{lib_id}") (at {x} {y} {angle}) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{inst_uuid}")')
    lines.append(f'    (property "Reference" "{ref}" (at {x} {prop_ref_y} 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'    (property "Value" "{val}" (at {x} {prop_val_y} 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'    (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append(f'    (property "Datasheet" "~" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    for p in range(1, num_pins + 1):
        lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')
    return "\n".join(lines)

if __name__ == "__main__":
    main()
