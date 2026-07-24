import subprocess
import os

TEMPLATE_START = """(kicad_sch (version 20230121) (generator eeschema)
  (uuid "d0a4c211-1234-4321-ba90-faecde112233")
  (paper "A3")
  (title_block
    (title "Test")
  )
"""

def test_schematic(content):
    test_file = "projects/heavy-lift-uav/kicad/test_temp.kicad_sch"
    with open(test_file, "w") as f:
        f.write(content)
        
    cmd = ["kicad-cli", "sch", "export", "pdf", "-o", "projects/heavy-lift-uav/kicad/test_temp.pdf", test_file]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists("projects/heavy-lift-uav/kicad/test_temp.pdf"):
        os.remove("projects/heavy-lift-uav/kicad/test_temp.pdf")
        
    return res.returncode == 0, res.stderr + "\n" + res.stdout

def main():
    # 1. Working resistor case
    working_content = TEMPLATE_START + """  (lib_symbols
    (symbol "Device:R" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at -1.778 0 90) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_0_1"
        (rectangle (start -1.016 3.81) (end 1.016 -3.81) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "R_1_1"
        (pin passive line (at 0 5.08 270) (length 1.27)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at 0 -5.08 90) (length 1.27)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
      )
    )
  )
  (symbol (lib_id "Device:R") (at 150 100 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "e6c40a5a-8b8b-4b4b-8b8b-e6c40a5a8b8b")
    (property "Reference" "R1" (at 152.032 100 90) (effects (font (size 1.27 1.27))))
    (property "Value" "10k" (at 150 100 90) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 148.222 100 90) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at 150 100 0) (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "e6c40a5a-8b8b-4b4b-8b8b-e6c40a5a8b81"))
    (pin "2" (uuid "e6c40a5a-8b8b-4b4b-8b8b-e6c40a5a8b82"))
  )
)
"""
    r, m = test_schematic(working_content)
    print("Working resistor schematic loads:", r)
    
    # 2. Generator case
    gen_content = TEMPLATE_START + """  (lib_symbols
    (symbol "UAV_Parts:Generator" (in_bom yes) (on_board yes)
      (property "Reference" "GEN" (at -15.24 12.7 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Generator_3.6kW" (at 0 12.7 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Generator_0_1"
        (rectangle (start -15.24 10.16) (end 15.24 -15.24) (stroke (width 0.254) (type default)) (fill (type background)))
      )
      (symbol "Generator_1_1"
        (pin power_out line (at 20.32 5.08 180) (length 5.08) (name "DC+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin power_out line (at 20.32 -5.08 180) (length 5.08) (name "DC-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin output line (at 20.32 -10.16 180) (length 5.08) (name "CAN_H" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin output line (at 20.32 -15.24 180) (length 5.08) (name "CAN_L" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
      )
    )
  )
  (symbol (lib_id "UAV_Parts:Generator") (at 45 80 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "5b3a3233-1a2b-3c4d-5e6f-7a8b9c0d1e2f")
    (property "Reference" "GEN1" (at 50 68 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Generator_3.6kW" (at 45 92 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 45 80 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at 45 80 0) (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "5b3a3233-1a2b-3c4d-5e6f-7a8b9c0d1e21"))
    (pin "2" (uuid "5b3a3233-1a2b-3c4d-5e6f-7a8b9c0d1e22"))
    (pin "3" (uuid "5b3a3233-1a2b-3c4d-5e6f-7a8b9c0d1e23"))
    (pin "4" (uuid "5b3a3233-1a2b-3c4d-5e6f-7a8b9c0d1e24"))
  )
)
"""
    r, m = test_schematic(gen_content)
    print("Generator schematic loads:", r)
    if not r:
        print("Generator error:", m)

if __name__ == "__main__":
    main()
