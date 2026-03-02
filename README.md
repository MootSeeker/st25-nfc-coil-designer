# NFC PCB Antenna Generator for KiCad

This Python script calculates and generates custom 13.56 MHz NFC/RFID planar antennas for Printed Circuit Boards (PCBs). It directly outputs a ready-to-use KiCad footprint (`.kicad_mod`) and calculates the specific 3-capacitor tuning network required for STMicroelectronics ST25 tags (like the ST25DV64KC).

## Features

* **Precision Calculation:** Uses the Mohan equation for planar, circular spiral inductors to hit your target inductance (e.g., 4.83 µH).
* **Hardware-Optimized Routing:** Forces whole integer turns so the inner and outer connection pads perfectly align on the same axis. This prevents unwanted loop areas during PCB routing and improves EMI.
* **Direct KiCad Export:** Generates a `.kicad_mod` file that can be instantly imported into KiCad or Altium Designer.
* **ST25DV Tuning Network:** Automatically calculates the required external capacitance for a differential 3-capacitor adjustment network ($C_{p}$, $C_{s1}$, $C_{s2}$) based on the IC's internal tuning capacity ($C_{tune}$ = 28.5 pF).

## Usage

1. Open the script and adjust your PCB manufacturing parameters:
   * Target Inductance (e.g., 4.83 µH)
   * Outer Diameter (e.g., 50.0 mm)
   * Track Width and Spacing (e.g., 0.3 mm)
   * Copper Thickness (e.g., 35 µm)
2. Run the script: `python nfc_generator.py`
3. Two files will be generated:
   * `NFC_Tag_Antenna_50.0mm_Integer.kicad_mod` (Your PCB Footprint)
   * `ST25DV_Custom_Matching.txt` (An ASCII schematic with your exact capacitor tuning values)

## Network Topology

The script calculates values for the following differential tuning topology commonly used with ST25 dynamic tags:

```text
 Tag AC0 ───────||─────────┬──────────────┐
              [ C_s1 ]     │              │
                          _│_             │
                          ___ C_p         § L_ant
                           │              § 
 Tag AC1 ───────||─────────┴──────────────┘
              [ C_s2 ]
