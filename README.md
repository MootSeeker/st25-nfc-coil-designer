# NFC PCB Antenna Generator for KiCad

This Python script calculates and generates custom 13.56 MHz NFC/RFID planar antennas for Printed Circuit Boards (PCBs). It directly outputs a ready-to-use KiCad footprint (`.kicad_mod`) and calculates the specific 3-capacitor tuning network required for STMicroelectronics ST25 tags (like the ST25DV64KC).

## Features

* **Precision Calculation:** Uses the Mohan equation for planar, circular spiral inductors to hit your target inductance (e.g., 4.83 µH).
* **Hardware-Optimized Routing:** Forces whole integer turns so the inner and outer connection pads perfectly align on the same axis. This prevents unwanted loop areas during PCB routing and improves EMI.
* **Direct KiCad Export:** Generates a `.kicad_mod` file that can be instantly imported into KiCad or Altium Designer.
* **ST25DV Tuning Network:** Automatically calculates the required external capacitance for a differential 3-capacitor adjustment network ($C_{p}$, $C_{s1}$, $C_{s2}$) based on the IC's internal tuning capacity ($C_{tune}$ = 28.5 pF).
* **Input Validation:** Catches invalid geometry parameters early with clear error messages.

## Requirements

* Python 3.6 or later (no external dependencies — uses only the standard library)

## Installation

```bash
git clone https://github.com/<your-user>/CoilDesigner.git
cd CoilDesigner
```

No additional packages need to be installed.

## Usage

Run the script with default parameters (4.83 µH target, 50 mm diameter, 0.3 mm track):

```bash
python3 nfc_antenna.py
```

Or customise any parameter via command-line flags:

```bash
python3 nfc_antenna.py --target-l 2.5 --d-out 35.0 --width 0.2 --spacing 0.2 --thickness 18.0
```

To write output files into a specific directory:

```bash
python3 nfc_antenna.py --out-dir build/
```

### Parameters

| Flag | Type | Default | Description |
|---|---|---|---|
| `--target-l` | float | `4.83` | Target inductance in µH |
| `--d-out` | float | `50.0` | Outer coil diameter in mm |
| `--width` | float | `0.3` | PCB track width in mm |
| `--spacing` | float | `0.3` | Spacing between tracks in mm |
| `--thickness` | float | `35.0` | Copper layer thickness in µm (35 µm = 1 oz) |
| `--out-dir` | string | `.` | Output directory for generated files |

Run `python3 nfc_antenna.py --help` to see all options.

### Output Files

| File | Description |
|---|---|
| `NFC_Tag_Antenna_<d_out>mm_Integer.kicad_mod` | KiCad footprint — import directly into your PCB project |
| `ST25DV_Custom_Matching.txt` | ASCII schematic with calculated capacitor tuning values for the ST25DV64KC |

### Using as a Library

The module can also be imported without side effects:

```python
from nfc_antenna import calculate_inductance, find_best_integer_turns

turns, L = find_best_integer_turns(4.83, 0.05, 0.0003, 0.0003)
print(f"{turns} turns → {L:.3f} µH")
```

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
