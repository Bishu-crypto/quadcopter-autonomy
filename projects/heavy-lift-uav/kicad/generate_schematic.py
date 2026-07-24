import uuid

def gen_uuid():
    return str(uuid.uuid4())

def main():
    target_path = "/home/bishu/quadcopter-autonomy/projects/heavy-lift-uav/kicad/power_and_signal_schematic.kicad_sch"
    
    # Generate unique UUIDs for all elements
    sheet_uuid = gen_uuid()
    
    # Create the schematic content
    lines = []
    lines.append(f'(kicad_sch (version 20230121) (generator eeschema)')
    lines.append(f'  (uuid "{sheet_uuid}")')
    lines.append(f'  (paper "A3")')
    
    lines.append(f'  (title_block')
    lines.append(f'    (title "Heavy-Lift Gas-Electric Hybrid Hexacopter - Power & Signal Schematic")')
    lines.append(f'    (date "2026-07-22")')
    lines.append(f'    (rev "1.2")')
    lines.append(f'    (company "Flight Systems Division")')
    lines.append(f'    (comment 1 "Locked Baseline (DESIGN_LOCK.md): 6 Arms @ 60 deg (L=1.12m), 40in Props, 3460.1W Hover Power, TOW 34.575kg")')
    lines.append(f'    (comment 2 "Power Distribution: 48V Bus, 72.1A Total Hover Current (12.02A/Branch), 75A Gen Max Output")')
    lines.append(f'    (comment 3 "Safety Factor & Peak Rating: 120A Flame ESCs, 100A BMS Battery Failsafe Coupling")')
    lines.append(f'  )')
    
    # Define Library Symbols
    lines.append(f'  (lib_symbols')
    
    # UAV_Parts:Generator
    lines.append(f'    (symbol "UAV_Parts:Generator" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "GEN" (at -15.24 12.7 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "Generator_3.6kW" (at 0 12.7 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "Generator_0_1"')
    lines.append(f'        (rectangle (start -15.24 10.16) (end 15.24 -15.24) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "Generator_1_1"')
    lines.append(f'        (pin power_out line (at 20.32 5.08 180) (length 5.08) (name "DC+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 20.32 -5.08 180) (length 5.08) (name "DC-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 20.32 -10.16 180) (length 5.08) (name "CAN_H" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 20.32 -15.24 180) (length 5.08) (name "CAN_L" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')
    
    # UAV_Parts:Battery_12S
    lines.append(f'    (symbol "UAV_Parts:Battery_12S" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "BAT" (at -10.16 7.62 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "Battery_12S_4.5Ah" (at 0 7.62 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "Battery_12S_0_1"')
    lines.append(f'        (rectangle (start -10.16 5.08) (end 10.16 -7.62) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "Battery_12S_1_1"')
    lines.append(f'        (pin power_out line (at 15.24 2.54 180) (length 5.08) (name "BAT+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 15.24 -2.54 180) (length 5.08) (name "BAT-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:BMS_Failsafe
    lines.append(f'    (symbol "UAV_Parts:BMS_Failsafe" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "U" (at -15.24 17.78 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "BMS_Ideal_Diode" (at 0 17.78 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "BMS_Failsafe_0_1"')
    lines.append(f'        (rectangle (start -15.24 15.24) (end 15.24 -15.24) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "BMS_Failsafe_1_1"')
    lines.append(f'        (pin power_in line (at -20.32 10.16 0) (length 5.08) (name "IN_BAT+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -20.32 -10.16 0) (length 5.08) (name "IN_BAT-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 20.32 10.16 180) (length 5.08) (name "OUT+" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 20.32 -10.16 180) (length 5.08) (name "OUT-" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin bidirectional line (at 20.32 0 180) (length 5.08) (name "CAN_H" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin bidirectional line (at 20.32 -5.08 180) (length 5.08) (name "CAN_L" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:PDB
    lines.append(f'    (symbol "UAV_Parts:PDB" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "PDB" (at -20.32 40.64 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "Power_Distribution_Board" (at 0 40.64 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "PDB_0_1"')
    lines.append(f'        (rectangle (start -20.32 38.1) (end 20.32 -38.1) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "PDB_1_1"')
    lines.append(f'        (pin power_in line (at -25.4 25.4 0) (length 5.08) (name "VIN+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -25.4 -25.4 0) (length 5.08) (name "VIN-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 30.48 180) (length 5.08) (name "ESC1+" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 25.4 180) (length 5.08) (name "ESC1-" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 20.32 180) (length 5.08) (name "ESC2+" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 15.24 180) (length 5.08) (name "ESC2-" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 10.16 180) (length 5.08) (name "ESC3+" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 5.08 180) (length 5.08) (name "ESC3-" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 0 180) (length 5.08) (name "ESC4+" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 -5.08 180) (length 5.08) (name "ESC4-" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 -10.16 180) (length 5.08) (name "ESC5+" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 -15.24 180) (length 5.08) (name "ESC5-" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 -20.32 180) (length 5.08) (name "ESC6+" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 -25.4 180) (length 5.08) (name "ESC6-" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 -30.48 180) (length 5.08) (name "AUX+" (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 25.4 -35.56 180) (length 5.08) (name "AUX-" (effects (font (size 1.27 1.27)))) (number "16" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:ESC_Flame120A
    lines.append(f'    (symbol "UAV_Parts:ESC_Flame120A" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "ESC" (at -12.7 15.24 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "Flame120A_ESC" (at 0 15.24 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "ESC_Flame120A_0_1"')
    lines.append(f'        (rectangle (start -12.7 12.7) (end 12.7 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "ESC_Flame120A_1_1"')
    lines.append(f'        (pin power_in line (at -17.78 7.62 0) (length 5.08) (name "V+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -17.78 -7.62 0) (length 5.08) (name "V-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at -17.78 2.54 0) (length 5.08) (name "PWM" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at -17.78 -2.54 0) (length 5.08) (name "GND" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 17.78 5.08 180) (length 5.08) (name "MA" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 17.78 0 180) (length 5.08) (name "MB" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 17.78 -5.08 180) (length 5.08) (name "MC" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:Motor_U15II
    lines.append(f'    (symbol "UAV_Parts:Motor_U15II" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "M" (at -7.62 10.16 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "U15II_KV100" (at 0 10.16 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "Motor_U15II_0_1"')
    lines.append(f'        (circle (center 0 0) (radius 7.62) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "Motor_U15II_1_1"')
    lines.append(f'        (pin power_in line (at -12.7 5.08 0) (length 5.08) (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -12.7 0 0) (length 5.08) (name "B" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -12.7 -5.08 0) (length 5.08) (name "C" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:Pixhawk6X
    lines.append(f'    (symbol "UAV_Parts:Pixhawk6X" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "FC" (at -25.4 33.02 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "Pixhawk_6X" (at 0 33.02 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "Pixhawk6X_0_1"')
    lines.append(f'        (rectangle (start -25.4 30.48) (end 25.4 -30.48) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "Pixhawk6X_1_1"')
    lines.append(f'        (pin power_in line (at -30.48 25.4 0) (length 5.08) (name "5V_IN" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -30.48 -25.4 0) (length 5.08) (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin bidirectional line (at -30.48 15.24 0) (length 5.08) (name "CAN1_H" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin bidirectional line (at -30.48 10.16 0) (length 5.08) (name "CAN1_L" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at -30.48 0 0) (length 5.08) (name "GPS_TX" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at -30.48 -5.08 0) (length 5.08) (name "GPS_RX" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at -30.48 -12.7 0) (length 5.08) (name "TEL_TX" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at -30.48 -17.78 0) (length 5.08) (name "TEL_RX" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 30.48 25.4 180) (length 5.08) (name "PWM1" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 30.48 20.32 180) (length 5.08) (name "PWM2" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 30.48 15.24 180) (length 5.08) (name "PWM3" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 30.48 10.16 180) (length 5.08) (name "PWM4" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 30.48 5.08 180) (length 5.08) (name "PWM5" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 30.48 0 180) (length 5.08) (name "PWM6" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 30.48 -10.16 180) (length 5.08) (name "ETH_TX+" (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 30.48 -15.24 180) (length 5.08) (name "ETH_TX-" (effects (font (size 1.27 1.27)))) (number "16" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at 30.48 -20.32 180) (length 5.08) (name "ETH_RX+" (effects (font (size 1.27 1.27)))) (number "17" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at 30.48 -25.4 180) (length 5.08) (name "ETH_RX-" (effects (font (size 1.27 1.27)))) (number "18" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:JetsonOrin
    lines.append(f'    (symbol "UAV_Parts:JetsonOrin" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "COMP" (at -15.24 22.86 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "Jetson_Orin_Nano" (at 0 22.86 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "JetsonOrin_0_1"')
    lines.append(f'        (rectangle (start -15.24 20.32) (end 15.24 -20.32) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "JetsonOrin_1_1"')
    lines.append(f'        (pin power_in line (at -20.32 15.24 0) (length 5.08) (name "5V_IN" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -20.32 -15.24 0) (length 5.08) (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at 20.32 10.16 180) (length 5.08) (name "ETH_RX+" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at 20.32 5.08 180) (length 5.08) (name "ETH_RX-" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 20.32 -5.08 180) (length 5.08) (name "ETH_TX+" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at 20.32 -10.16 180) (length 5.08) (name "ETH_TX-" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:DCDC_Converter
    lines.append(f'    (symbol "UAV_Parts:DCDC_Converter" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "REG" (at -10.16 12.7 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "DC-DC_Regulator" (at 0 12.7 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "DCDC_Converter_0_1"')
    lines.append(f'        (rectangle (start -10.16 10.16) (end 10.16 -10.16) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "DCDC_Converter_1_1"')
    lines.append(f'        (pin power_in line (at -15.24 5.08 0) (length 5.08) (name "VIN+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -15.24 -5.08 0) (length 5.08) (name "VIN-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 15.24 5.08 180) (length 5.08) (name "VOUT+" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_out line (at 15.24 -5.08 180) (length 5.08) (name "VOUT-" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:TelemetryRadio
    lines.append(f'    (symbol "UAV_Parts:TelemetryRadio" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "TEL" (at -10.16 12.7 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "RFD900_Telemetry" (at 0 12.7 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "TelemetryRadio_0_1"')
    lines.append(f'        (rectangle (start -10.16 10.16) (end 10.16 -10.16) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "TelemetryRadio_1_1"')
    lines.append(f'        (pin power_in line (at -15.24 6.35 0) (length 5.08) (name "VCC" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -15.24 -6.35 0) (length 5.08) (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at -15.24 2.12 0) (length 5.08) (name "RX" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at -15.24 -2.12 0) (length 5.08) (name "TX" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')

    # UAV_Parts:GPS_RTK
    lines.append(f'    (symbol "UAV_Parts:GPS_RTK" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "GPS" (at -10.16 12.7 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "Here3_GPS_RTK" (at 0 12.7 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "GPS_RTK_0_1"')
    lines.append(f'        (rectangle (start -10.16 10.16) (end 10.16 -10.16) (stroke (width 0.254) (type default)) (fill (type background)))')
    lines.append(f'      )')
    lines.append(f'      (symbol "GPS_RTK_1_1"')
    lines.append(f'        (pin power_in line (at -15.24 6.35 0) (length 5.08) (name "VCC" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin power_in line (at -15.24 -6.35 0) (length 5.08) (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin output line (at -15.24 2.12 0) (length 5.08) (name "TX" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    lines.append(f'        (pin input line (at -15.24 -2.12 0) (length 5.08) (name "RX" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    lines.append(f'      )')
    lines.append(f'    )')
    
    lines.append(f'  )') # End of lib_symbols
    
    # Helper to generate properties
    def add_instance_properties(ref, val, x, y):
        inst_lines = []
        inst_lines.append(f'    (property "Reference" "{ref}" (at {x + 5} {y - 12} 0) (effects (font (size 1.27 1.27))))')
        inst_lines.append(f'    (property "Value" "{val}" (at {x} {y + 12} 0) (effects (font (size 1.27 1.27))))')
        inst_lines.append(f'    (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))')
        inst_lines.append(f'    (property "Datasheet" "~" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))')
        return inst_lines

    # ------------------ Placed Symbol Instances ------------------
    # GEN1 at (45, 80)
    lines.append(f'  (symbol (lib_id "UAV_Parts:Generator") (at 45 80 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("GEN1", "Generator_3.6kW", 45, 80))
    lines.append(f'    (pin "1" (uuid "{gen_uuid()}")) (pin "2" (uuid "{gen_uuid()}"))')
    lines.append(f'    (pin "3" (uuid "{gen_uuid()}")) (pin "4" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')
    
    # BAT1 at (80, 140)
    lines.append(f'  (symbol (lib_id "UAV_Parts:Battery_12S") (at 80 140 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("BAT1", "Battery_12S_4.5Ah", 80, 140))
    lines.append(f'    (pin "1" (uuid "{gen_uuid()}")) (pin "2" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')
    
    # BMS1 at (130, 80)
    lines.append(f'  (symbol (lib_id "UAV_Parts:BMS_Failsafe") (at 130 80 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("U1", "BMS_Ideal_Diode", 130, 80))
    lines.append(f'    (pin "1" (uuid "{gen_uuid()}")) (pin "2" (uuid "{gen_uuid()}"))')
    lines.append(f'    (pin "3" (uuid "{gen_uuid()}")) (pin "4" (uuid "{gen_uuid()}"))')
    lines.append(f'    (pin "5" (uuid "{gen_uuid()}")) (pin "6" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')
    
    # PDB1 at (195, 80)
    lines.append(f'  (symbol (lib_id "UAV_Parts:PDB") (at 195 80 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("PDB1", "Power_Distribution_Board", 195, 80))
    for p in range(1, 17):
        lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')
    
    # REG1 (12V) at (200, 145)
    lines.append(f'  (symbol (lib_id "UAV_Parts:DCDC_Converter") (at 200 145 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("REG1", "DC-DC_12V_10A", 200, 145))
    lines.append(f'    (pin "1" (uuid "{gen_uuid()}")) (pin "2" (uuid "{gen_uuid()}"))')
    lines.append(f'    (pin "3" (uuid "{gen_uuid()}")) (pin "4" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')

    # REG2 (5V) at (200, 175)
    lines.append(f'  (symbol (lib_id "UAV_Parts:DCDC_Converter") (at 200 175 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("REG2", "DC-DC_5V_10A", 200, 175))
    lines.append(f'    (pin "1" (uuid "{gen_uuid()}")) (pin "2" (uuid "{gen_uuid()}"))')
    lines.append(f'    (pin "3" (uuid "{gen_uuid()}")) (pin "4" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')

    # ESC1 to ESC6 at (295, y_esc)
    # Motors M1 to M6 at (355, y_esc)
    y_esc_list = [50, 80, 110, 140, 170, 200]
    for i, y_esc in enumerate(y_esc_list):
        idx = i + 1
        lines.append(f'  (symbol (lib_id "UAV_Parts:ESC_Flame120A") (at 295 {y_esc} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
        lines.append(f'    (uuid "{gen_uuid()}")')
        lines.extend(add_instance_properties(f"ESC{idx}", f"Flame120A_ESC_{idx}", 295, y_esc))
        for p in range(1, 8):
            lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
        lines.append(f'  )')
        
        lines.append(f'  (symbol (lib_id "UAV_Parts:Motor_U15II") (at 355 {y_esc} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
        lines.append(f'    (uuid "{gen_uuid()}")')
        lines.extend(add_instance_properties(f"M{idx}", f"Motor_{idx}_U15II", 355, y_esc))
        for p in range(1, 4):
            lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
        lines.append(f'  )')

    # FC1 (Pixhawk6X) at (130, 230)
    lines.append(f'  (symbol (lib_id "UAV_Parts:Pixhawk6X") (at 130 230 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("FC1", "Pixhawk_6X", 130, 230))
    for p in range(1, 19):
        lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')

    # COMP1 (JetsonOrin) at (50, 230)
    lines.append(f'  (symbol (lib_id "UAV_Parts:JetsonOrin") (at 50 230 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("COMP1", "Jetson_Orin_Nano", 50, 230))
    for p in range(1, 7):
        lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')

    # GPS1 at (200, 215)
    lines.append(f'  (symbol (lib_id "UAV_Parts:GPS_RTK") (at 200 215 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("GPS1", "GPS1_Neo3_RTK", 200, 215))
    for p in range(1, 5):
        lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')

    # GPS2 at (200, 235)
    lines.append(f'  (symbol (lib_id "UAV_Parts:GPS_RTK") (at 200 235 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("GPS2", "GPS2_Neo3_RTK", 200, 235))
    for p in range(1, 5):
        lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')

    # TEL1 at (200, 260)
    lines.append(f'  (symbol (lib_id "UAV_Parts:TelemetryRadio") (at 200 260 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
    lines.append(f'    (uuid "{gen_uuid()}")')
    lines.extend(add_instance_properties("TEL1", "Telemetry_RFD900", 200, 260))
    for p in range(1, 5):
        lines.append(f'    (pin "{p}" (uuid "{gen_uuid()}"))')
    lines.append(f'  )')


    # ------------------ Wires (Connections) ------------------
    # Connect GEN1 DC+ (65.32, 75) to PDB1 VIN+ (169.6, 54.6)
    lines.append(f'  (wire (pts (xy 65.32 75) (xy 165 75)) (stroke (width 0.5) (type default)))')
    lines.append(f'  (wire (pts (xy 165 75) (xy 165 54.6)) (stroke (width 0.5) (type default)))')
    lines.append(f'  (wire (pts (xy 165 54.6) (xy 169.6 54.6)) (stroke (width 0.5) (type default)))')

    # GEN1 DC- (65.32, 85) to PDB1 VIN- (169.6, 105.4)
    lines.append(f'  (wire (pts (xy 65.32 85) (xy 165 85)) (stroke (width 0.5) (type default)))')
    lines.append(f'  (wire (pts (xy 165 85) (xy 165 105.4)) (stroke (width 0.5) (type default)))')
    lines.append(f'  (wire (pts (xy 165 105.4) (xy 169.6 105.4)) (stroke (width 0.5) (type default)))')

    # BMS1 OUT+ (150.32, 70) to the wire above at (165, 70) -> intersects at (165, 70).
    lines.append(f'  (wire (pts (xy 150.32 70) (xy 165 70)) (stroke (width 0.5) (type default)))')
    
    # BMS1 OUT- (150.32, 90) to the wire above at (165, 90).
    lines.append(f'  (wire (pts (xy 150.32 90) (xy 165 90)) (stroke (width 0.5) (type default)))')

    # Connect BAT1 to BMS1:
    # BAT1 BAT+ (95.24, 137.46) to BMS1 IN_BAT+ (109.68, 70)
    lines.append(f'  (wire (pts (xy 95.24 137.46) (xy 105 137.46)) (stroke (width 0.5) (type default)))')
    lines.append(f'  (wire (pts (xy 105 137.46) (xy 105 69.84)) (stroke (width 0.5) (type default)))')
    lines.append(f'  (wire (pts (xy 105 69.84) (xy 109.68 69.84)) (stroke (width 0.5) (type default)))')

    # BAT1 BAT- (95.24, 142.54) to BMS1 IN_BAT- (109.68, 90.16)
    lines.append(f'  (wire (pts (xy 95.24 142.54) (xy 100 142.54)) (stroke (width 0.5) (type default)))')
    lines.append(f'  (wire (pts (xy 100 142.54) (xy 100 90.16)) (stroke (width 0.5) (type default)))')
    lines.append(f'  (wire (pts (xy 100 90.16) (xy 109.68 90.16)) (stroke (width 0.5) (type default)))')

    # Connect PDB1 ESC outputs to ESC inputs:
    # ESC1: PDB1 ESC1+ (220.4, 49.52) to ESC1 V+ (277.22, 42.38)
    lines.append(f'  (wire (pts (xy 220.4 49.52) (xy 265 49.52)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 265 49.52) (xy 265 42.38)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 265 42.38) (xy 277.22 42.38)) (stroke (width 0.4) (type default)))')
    
    # ESC1: PDB1 ESC1- (220.4, 54.6) to ESC1 V- (277.22, 57.62)
    lines.append(f'  (wire (pts (xy 220.4 54.6) (xy 260 54.6)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 260 54.6) (xy 260 57.62)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 260 57.62) (xy 277.22 57.62)) (stroke (width 0.4) (type default)))')

    # Connect ESC outputs to Motors:
    for i, y_esc in enumerate(y_esc_list):
        idx = i + 1
        lines.append(f'  (wire (pts (xy 312.78 {y_esc - 5.08}) (xy 342.3 {y_esc - 5.08})) (stroke (width 0.3) (type default)))')
        lines.append(f'  (wire (pts (xy 312.78 {y_esc}) (xy 342.3 {y_esc})) (stroke (width 0.3) (type default)))')
        lines.append(f'  (wire (pts (xy 312.78 {y_esc + 5.08}) (xy 342.3 {y_esc + 5.08})) (stroke (width 0.3) (type default)))')

    # ESC2: PDB1 ESC2+ (220.4, 59.68) to ESC2 V+ (277.22, 72.38)
    lines.append(f'  (wire (pts (xy 220.4 59.68) (xy 255 59.68)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 255 59.68) (xy 255 72.38)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 255 72.38) (xy 277.22 72.38)) (stroke (width 0.4) (type default)))')
    # ESC2: PDB1 ESC2- (220.4, 64.76) to ESC2 V- (277.22, 87.62)
    lines.append(f'  (wire (pts (xy 220.4 64.76) (xy 250 64.76)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 250 64.76) (xy 250 87.62)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 250 87.62) (xy 277.22 87.62)) (stroke (width 0.4) (type default)))')

    # ESC3: PDB1 ESC3+ (220.4, 69.84) to ESC3 V+ (277.22, 102.38)
    lines.append(f'  (wire (pts (xy 220.4 69.84) (xy 245 69.84)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 245 69.84) (xy 245 102.38)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 245 102.38) (xy 277.22 102.38)) (stroke (width 0.4) (type default)))')
    # ESC3: PDB1 ESC3- (220.4, 74.92) to ESC3 V- (277.22, 117.62)
    lines.append(f'  (wire (pts (xy 220.4 74.92) (xy 240 74.92)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 240 74.92) (xy 240 117.62)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 240 117.62) (xy 277.22 117.62)) (stroke (width 0.4) (type default)))')

    # ESC4: PDB1 ESC4+ (220.4, 80) to ESC4 V+ (277.22, 132.38)
    lines.append(f'  (wire (pts (xy 220.4 80) (xy 235 80)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 235 80) (xy 235 132.38)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 235 132.38) (xy 277.22 132.38)) (stroke (width 0.4) (type default)))')
    # ESC4: PDB1 ESC4- (220.4, 85.08) to ESC4 V- (277.22, 147.62)
    lines.append(f'  (wire (pts (xy 220.4 85.08) (xy 230 85.08)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 230 85.08) (xy 230 147.62)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 230 147.62) (xy 277.22 147.62)) (stroke (width 0.4) (type default)))')

    # ESC5: PDB1 ESC5+ (220.4, 90.16) to ESC5 V+ (277.22, 162.38)
    lines.append(f'  (wire (pts (xy 220.4 90.16) (xy 225 90.16)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 225 90.16) (xy 225 162.38)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 225 162.38) (xy 277.22 162.38)) (stroke (width 0.4) (type default)))')
    # ESC5: PDB1 ESC5- (220.4, 95.24) to ESC5 V- (277.22, 177.62)
    lines.append(f'  (wire (pts (xy 220.4 95.24) (xy 220.4 177.62)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 220.4 177.62) (xy 277.22 177.62)) (stroke (width 0.4) (type default)))')

    # ESC6: PDB1 ESC6+ (220.4, 100.32) to ESC6 V+ (277.22, 192.38)
    lines.append(f'  (wire (pts (xy 220.4 100.32) (xy 220.4 192.38)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 220.4 192.38) (xy 277.22 192.38)) (stroke (width 0.4) (type default)))')
    # ESC6: PDB1 ESC6- (220.4, 105.4) to ESC6 V- (277.22, 207.62)
    lines.append(f'  (wire (pts (xy 220.4 105.4) (xy 220.4 207.62)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 220.4 207.62) (xy 277.22 207.62)) (stroke (width 0.4) (type default)))')

    # Connect PDB1 AUX outputs to REG1 and REG2 inputs:
    # PDB1 AUX+ (220.4, 110.48) to REG1 VIN+ (184.76, 139.92) and REG2 VIN+ (184.76, 169.92)
    lines.append(f'  (wire (pts (xy 220.4 110.48) (xy 220.4 139.92)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 220.4 139.92) (xy 184.76 139.92)) (stroke (width 0.4) (type default)))')
    # Connect REG2 VIN+ to same wire at (220.4, 169.92)
    lines.append(f'  (wire (pts (xy 220.4 139.92) (xy 220.4 169.92)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 220.4 169.92) (xy 184.76 169.92)) (stroke (width 0.4) (type default)))')

    # PDB1 AUX- (220.4, 115.56) to REG1 VIN- (184.76, 150.08) and REG2 VIN- (184.76, 180.08)
    lines.append(f'  (wire (pts (xy 220.4 115.56) (xy 220.4 150.08)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 220.4 150.08) (xy 184.76 150.08)) (stroke (width 0.4) (type default)))')
    # Connect REG2 VIN- to same wire
    lines.append(f'  (wire (pts (xy 220.4 150.08) (xy 220.4 180.08)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (wire (pts (xy 220.4 180.08) (xy 184.76 180.08)) (stroke (width 0.4) (type default)))')

    # Connect REG2 VOUT+ (215.24, 169.92) to FC1 5V_IN (99.52, 204.6) and COMP1 5V_IN (29.68, 214.76)
    lines.append(f'  (wire (pts (xy 215.24 169.92) (xy 215.24 185)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (wire (pts (xy 215.24 185) (xy 99.52 185)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (wire (pts (xy 99.52 185) (xy 99.52 204.6)) (stroke (width 0.3) (type default)))')
    # Connect COMP1 5V_IN to the same 5V line
    lines.append(f'  (wire (pts (xy 99.52 185) (xy 29.68 185)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (wire (pts (xy 29.68 185) (xy 29.68 214.76)) (stroke (width 0.3) (type default)))')

    # Connect REG2 VOUT- (215.24, 180.08) to FC1 GND (99.52, 255.4) and COMP1 GND (29.68, 245.24)
    lines.append(f'  (wire (pts (xy 215.24 180.08) (xy 215.24 190)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (wire (pts (xy 215.24 190) (xy 95 190)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (wire (pts (xy 95 190) (xy 95 255.4)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (wire (pts (xy 95 255.4) (xy 99.52 255.4)) (stroke (width 0.3) (type default)))')
    # COMP1 GND
    lines.append(f'  (wire (pts (xy 95 190) (xy 25 190)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (wire (pts (xy 25 190) (xy 25 245.24)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (wire (pts (xy 25 245.24) (xy 29.68 245.24)) (stroke (width 0.3) (type default)))')

    # Connect REG1 VOUT+ (215.24, 139.92) to a local label for 12V Payload Power
    lines.append(f'  (wire (pts (xy 215.24 139.92) (xy 225 139.92)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (label "VCC_12V" (at 225 139.92 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 215.24 150.08) (xy 225 150.08)) (stroke (width 0.4) (type default)))')
    lines.append(f'  (label "GND_12V" (at 225 150.08 0) (effects (font (size 1.27 1.27))))')

    # Pixhawk PWM Outputs to labels
    for idx in range(1, 7):
        y_fc_pwm = 230 - (25.4 - 5.08 * (idx - 1))
        lines.append(f'  (wire (pts (xy 160.48 {y_fc_pwm}) (xy 165.48 {y_fc_pwm})) (stroke (width 0.3) (type default)))')
        lines.append(f'  (label "PWM_{idx}" (at 165.48 {y_fc_pwm} 0) (effects (font (size 1.27 1.27))))')

    # ESC PWM Inputs to labels
    for idx, y_esc in enumerate(y_esc_list):
        y_esc_pwm = y_esc - 2.54
        lines.append(f'  (wire (pts (xy 277.22 {y_esc_pwm}) (xy 272.22 {y_esc_pwm})) (stroke (width 0.3) (type default)))')
        lines.append(f'  (label "PWM_{idx+1}" (at 272.22 {y_esc_pwm} 180) (effects (font (size 1.27 1.27))))')

    # Pixhawk CAN Bus
    lines.append(f'  (wire (pts (xy 104.6 214.76) (xy 99.6 214.76)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "CAN_H" (at 99.6 214.76 180) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 104.6 219.84) (xy 99.6 219.84)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "CAN_L" (at 99.6 219.84 180) (effects (font (size 1.27 1.27))))')

    # Connect GEN1 CAN Bus
    lines.append(f'  (wire (pts (xy 65.32 90.16) (xy 70.32 90.16)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "CAN_H" (at 70.32 90.16 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 65.32 95.24) (xy 70.32 95.24)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "CAN_L" (at 70.32 95.24 0) (effects (font (size 1.27 1.27))))')

    # Connect BMS1 CAN Bus
    lines.append(f'  (wire (pts (xy 150.32 80) (xy 155.32 80)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "CAN_H" (at 155.32 80 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 150.32 85.08) (xy 155.32 85.08)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "CAN_L" (at 155.32 85.08 0) (effects (font (size 1.27 1.27))))')

    # Connect Ethernet link between FC1 and COMP1
    lines.append(f'  (wire (pts (xy 155.4 240.16) (xy 165 240.16)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "ETH_TX_P" (at 165 240.16 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 155.4 245.24) (xy 165 245.24)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "ETH_TX_N" (at 165 245.24 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 155.4 250.32) (xy 165 250.32)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "ETH_RX_P" (at 165 250.32 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 155.4 255.4) (xy 165 255.4)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "ETH_RX_N" (at 165 255.4 0) (effects (font (size 1.27 1.27))))')

    # COMP1 Ethernet side:
    lines.append(f'  (wire (pts (xy 70.32 220) (xy 75 220)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "ETH_TX_P" (at 75 220 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 70.32 225) (xy 75 225)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "ETH_TX_N" (at 75 225 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 70.32 240) (xy 75 240)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "ETH_RX_P" (at 75 240 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 70.32 245) (xy 75 245)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "ETH_RX_N" (at 75 245 0) (effects (font (size 1.27 1.27))))')

    # Connect Peripherals: GPS1, GPS2, TEL1
    # FC1 GPS port
    lines.append(f'  (wire (pts (xy 104.6 230) (xy 99.6 230)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "GPS_TXD" (at 99.6 230 180) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 104.6 235.08) (xy 99.6 235.08)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "GPS_RXD" (at 99.6 235.08 180) (effects (font (size 1.27 1.27))))')

    # GPS1
    lines.append(f'  (wire (pts (xy 184.76 212.88) (xy 179.76 212.88)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "GPS_RXD" (at 179.76 212.88 180) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 184.76 217.12) (xy 179.76 217.12)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "GPS_TXD" (at 179.76 217.12 180) (effects (font (size 1.27 1.27))))')

    # GPS2
    lines.append(f'  (wire (pts (xy 184.76 232.88) (xy 179.76 232.88)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "GPS_RXD" (at 179.76 232.88 180) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 184.76 237.12) (xy 179.76 237.12)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "GPS_TXD" (at 179.76 237.12 180) (effects (font (size 1.27 1.27))))')

    # FC1 Telemetry port
    lines.append(f'  (wire (pts (xy 104.6 242.7) (xy 99.6 242.7)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "TEL_TXD" (at 99.6 242.7 180) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 104.6 247.78) (xy 99.6 247.78)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "TEL_RXD" (at 99.6 247.78 180) (effects (font (size 1.27 1.27))))')

    # TEL1
    lines.append(f'  (wire (pts (xy 184.76 257.88) (xy 179.76 257.88)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "TEL_TXD" (at 179.76 257.88 180) (effects (font (size 1.27 1.27))))')
    lines.append(f'  (wire (pts (xy 184.76 262.12) (xy 179.76 262.12)) (stroke (width 0.3) (type default)))')
    lines.append(f'  (label "TEL_RXD" (at 179.76 262.12 180) (effects (font (size 1.27 1.27))))')

    # ------------------ Graphical Text Annotations ------------------
    lines.append(f'  (text "HEAVY-LIFT UAV MAIN POWER PATH (48V HYBRID DC BUS)" (at 40 40 0) (effects (font (size 2.5 2.5) bold)))')
    lines.append(f'  (text "1. HYBRID GENERATOR & RECTIFIER SYSTEM\\n- Output: 3.6 kW Continuous (48V DC, 75A Max)\\n- Fuel: Gasoline 2-Stroke Gen\\n- Cable Rating: 48V_BUS, MAX 75A" (at 40 55 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "2. BUFFER BATTERY & BMS FAILSAFE\\n- Battery: 12S LiPo (44.4V - 50.4V, 4500mAh 45C)\\n- Failsafe BMS Parallel Coupling (Ideal Diode)\\n- Cable Rating: BAT_BUS, MAX 100A PEAK" (at 85 115 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "3. MAIN POWER DISTRIBUTION BOARD (PDB)\\n- Input: 48V DC Bus (Total Hover Power: 3,460.1 W @ 72.1A Total)\\n- 6x ESC Branch Outputs: 48V DC, 12.02A Hover / 60A Peak per Branch" (at 175 30 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "AVIONICS & CONTROL SIGNAL ARCHITECTURE" (at 40 198 0) (effects (font (size 2.5 2.5) bold)))')
    lines.append(f'  (text "1. FLIGHT CONTROLLER (Pixhawk 6X)\\n- PWM Outputs [PWM_1 .. PWM_6] -> 6x ESC Signal Inputs\\n- Telemetry 1 -> 915 MHz RF Telemetry Radio (1W Output)\\n- GPS / RTK -> Dual Neo-3 GPS/RTK Receivers\\n- CAN Bus [CAN1_H/L] -> Hybrid Generator ECU Telemetry & BMS Status\\n- Companion Computer -> Ethernet MAVLink to Nvidia Jetson Orin Nano" (at 110 268 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "2. COMPANION COMPUTER\\n- Model: Nvidia Jetson Orin Nano\\n- High-level autonomy and payload interface\\n- Powered by DC-DC 5V Regulator" (at 30 258 0) (effects (font (size 1.8 1.8))))')
    lines.append(f'  (text "3. REGULATED RAIL OUTPUTS\\n- REG1: 12V 10A Rail for Video Tx / Camera Gimbal\\n- REG2: 5V 10A Rail for Flight Controller & Jetson Orin" (at 175 125 0) (effects (font (size 1.8 1.8))))')

    # Close S-expression
    lines.append(f')')
    
    # Write to target file
    with open(target_path, "w") as f:
        f.write("\n".join(lines))
        
    print(f"Generated KiCad schematic: {target_path}")

if __name__ == "__main__":
    main()
