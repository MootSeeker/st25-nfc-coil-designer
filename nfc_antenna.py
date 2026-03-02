import math

def calculate_inductance(d_out, w, s, n):
    mu0 = 4 * math.pi * 10**-7
    d_in = d_out - 2 * n * (w + s)
    if d_in <= 0: return 0.0
    d_avg = (d_out + d_in) / 2.0
    rho = (d_out - d_in) / (d_out + d_in)
    c1, c2, c3, c4 = 1.00, 2.46, 0.00, 0.20
    L = 0.5 * mu0 * (n**2) * d_avg * c1 * (math.log(c2 / rho) + c3 * rho + c4 * rho**2)
    return L * 1e6

def calculate_resistance(d_out, w, s, n, thickness):
    d_in = d_out - 2 * n * (w + s)
    d_avg = (d_out + d_in) / 2.0
    length = n * math.pi * d_avg
    rho_cu = 1.68e-8
    cross_section_area = w * thickness
    return rho_cu * (length / cross_section_area)

def find_best_integer_turns(target_L, d_out, w, s):
    n = 1.0
    step = 0.01
    while True:
        L = calculate_inductance(d_out, w, s, n)
        if L >= target_L or L == 0: break
        n += step
    
    n_floor = math.floor(n)
    n_ceil = math.ceil(n)
    
    L_floor = calculate_inductance(d_out, w, s, n_floor)
    L_ceil = calculate_inductance(d_out, w, s, n_ceil)
    
    if abs(target_L - L_floor) < abs(target_L - L_ceil):
        return n_floor, L_floor
    else:
        return n_ceil, L_ceil

def generate_kicad_footprint(filename, d_out_mm, w_mm, s_mm, n):
    r_out = (d_out_mm - w_mm) / 2.0
    pitch = w_mm + s_mm
    b = pitch / (2 * math.pi)
    segments = 100
    total_steps = int(n * segments)
    
    lines = []
    lines.append(f"(footprint \"NFC_Antenna_{d_out_mm}mm_IntegerTurns\"")
    lines.append(f"  (layer \"F.Cu\")")
    lines.append(f"  (attr smd)")
    
    prev_x, prev_y = None, None
    for i in range(total_steps + 1):
        theta = (i / segments) * 2 * math.pi
        r = r_out - b * theta
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        if prev_x is not None:
            lines.append(f"  (fp_line (start {prev_x:.4f} {prev_y:.4f}) (end {x:.4f} {y:.4f}) (layer \"F.Cu\") (width {w_mm:.3f}))")
        prev_x, prev_y = x, y

    start_r = r_out
    end_r = r_out - b * (n * 2 * math.pi)
    end_theta = n * 2 * math.pi
    end_x = end_r * math.cos(end_theta)
    end_y = end_r * math.sin(end_theta)

    lines.append(f"  (pad \"1\" smd circle (at {start_r:.4f} 0.0000) (size {w_mm*1.5:.3f} {w_mm*1.5:.3f}) (layers \"F.Cu\" \"F.Mask\"))")
    lines.append(f"  (pad \"2\" smd circle (at {end_x:.4f} {end_y:.4f}) (size {w_mm*1.5:.3f} {w_mm*1.5:.3f}) (layers \"F.Cu\" \"F.Mask\"))")
    lines.append(")")
    
    with open(filename, 'w', encoding='utf-8') as f: 
        f.write("\n".join(lines))

def generate_custom_schematic_file(filename, L_uh, R_dc):
    f = 13.56e6 # 13.56 MHz
    L = L_uh * 1e-6
    omega = 2 * math.pi * f
    
    # ST25DV64KC internal capacitance
    c_tune_internal_pF = 28.5 
    
    # Required physical resonance capacitance for the actual inductance
    c_res_total_F = 1 / ((omega**2) * L)
    c_res_total_pF = c_res_total_F * 1e12
    
    # External difference that the network (C401, C402, C403) must provide
    c_diff = c_res_total_pF - c_tune_internal_pF
    c_diff_clamped = max(0, c_diff) # Negative values cannot be populated
    
    ascii_art = f"""ST25DV64KC CUSTOM ANTENNA TUNING
================================
Frequency:          13.56 MHz
Actual inductance:  {L_uh:.3f} µH
DC resistance:      {R_dc:.2f} Ohm

Internal IC capacitance (C_tune):     {c_tune_internal_pF:.1f} pF
Required system capacitance (C_res):  {c_res_total_pF:.1f} pF
Externally required (C_ext):          {c_diff:.1f} pF

YOUR SCHEMATIC (Antenna Adjustment)
-----------------------------------

X400                                           IC400
(Antenna)       Antenna Adjustment            (ST25DV)
┌─────┐
│    1├───┬────────┬─────────────[ R404 ]──────┤5  AC1
│     │   │        │               0E
│     │  _│_      _│_ C402
│     │  ___ C401 ___
│     │   │        │
│     │  GND       │
│    2├───┬────────┴─────────────[ R405 ]──────┤4  AC0
└─────┘   │                        0E
         _│_
         ___ C403
          │
         GND


NETWORK MATH:
Because C401 and C403 are connected via GND, they act for the AC signal
as a differential series combination in parallel with C402.
The external capacitance seen by the antenna (C_ext) is:

    C_ext = C402 + (C401 * C403) / (C401 + C403)


POPULATION RECOMMENDATION FOR YOUR BOARD:

1. Initial test (your current DNP state):
   -> C401 = DNP
   -> C402 = DNP
   -> C403 = DNP
    If your printed coil is exactly {L_uh:.3f} µH, then C_ext = 0 pF is ideal,
    because the chip's internal {c_tune_internal_pF:.1f} pF is sufficient for resonance.

2. Tuning if the frequency is too high (etched inductance became too small):
    -> You need {c_diff_clamped:.1f} pF (C_ext).
    -> Option A (parallel only): populate C402 = {c_diff_clamped:.1f} pF. Leave C401/C403 = DNP.
    -> Option B (with symmetry/EMI path to GND):
        Select equal values for C401 and C403 (e.g. {c_diff_clamped * 2:.1f} pF).
        This gives (C*C)/(2C) = {c_diff_clamped:.1f} pF.
        C402 remains DNP.
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ascii_art)
    print(f"✅ Tuning data saved to: {filename}")

# --- Your parameters ---
TARGET_L_UH = 4.83
D_OUT_MM = 50.0
W_MM = 0.3
S_MM = 0.3
T_UM = 35.0

d_out_m, w_m, s_m, t_m = D_OUT_MM/1000.0, W_MM/1000.0, S_MM/1000.0, T_UM/1e6

turns, actual_l = find_best_integer_turns(TARGET_L_UH, d_out_m, w_m, s_m)
r_dc = calculate_resistance(d_out_m, w_m, s_m, turns, t_m)

generate_kicad_footprint(f"NFC_Tag_Antenna_{D_OUT_MM}mm_Integer.kicad_mod", D_OUT_MM, W_MM, S_MM, turns)
generate_custom_schematic_file("ST25DV_Custom_Matching.txt", actual_l, r_dc)