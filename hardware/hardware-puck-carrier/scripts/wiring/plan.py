"""Wiring plan: every (ref,pin) -> action. Single source of truth for both
the generator and the verifier.

Action kinds:
  ('G', net [, opts])      stub + global label
  ('L', net [, opts])      stub + local label
  ('NC',)                  no_connect marker
  ('W', ref2, pin2, netid) direct wire to other pin; netid '~xxx' = unnamed
  ('WL', ref2, pin2, net, kind, (lx,ly), ang)  direct wire + label on wire
  ('PIN_L', net, ang)      local label anchored directly at pin (no stub)
opts dict: len (stub length, default 2.54), ang (label angle override)

Constructs (drawn specially, connectivity registered):
  UJOIN: two same-direction stubs joined by a cross wire + one label
  PAIRJOIN: two stubs + joining wire + label mid-join
"""

PLAN = {}
def P(ref, pin, *action):
    PLAN[(ref, str(pin))] = action

# ---------------- Block 1: Brain U1 ----------------
u1 = {
    1:('G','GND'), 9:('G','EC_B'), 11:('G','EC_A'), 12:('G','UVC_PD'),
    16:('G','SCL'), 19:('G','SDA'), 20:('G','EC_SENSE_A'), 21:('G','EC_SENSE_B'),
    22:('G','PDM_DATA'), 24:('G','PDM_CLK'), 27:('G','UVC_EN'),
    28:('G','3V3'), 30:('G','VBAT'), 32:('G','VBUS'),
    34:('G','USB_DM'), 35:('G','USB_DP'), 36:('G','LED_850'), 37:('G','LED_WHITE'),
    38:('G','OW_DQ'), 39:('G','LED_365'), 40:('G','RESET'), 41:('G','HEATER_EN'),
    42:('G','PIEZO'), 43:('G','IMU_INT'), 44:('G','BOOST_EN'),
    45:('G','EC_DRV_HI'), 46:('G','EC_DRV_LO'), 48:('G','UART_TX'),
    49:('G','UART_RX'), 51:('G','SWDIO'), 52:('G','NFC1'), 53:('G','SWCLK'),
    54:('G','NFC2'), 23:('G','CHG_STAT'), 29:('G','LED_STAT'),
    47:('G','RING_DATA'), 25:('G','BTN_DFU'), 26:('G','BTN_FRESET'),
}
NC_U1 = [3,4,5,6,7,8,10,13,14,17,18,31,50,56,57,58,59,60,61]
for n, a in u1.items():
    P('U1', n, *a)
for n in NC_U1:
    P('U1', n, 'NC')
# hidden stacked GND pins 2,15,33,55 connect by position with pin 1's stub

# ---------------- Block 2: Battery + charging ----------------
P('J1', 1, 'G', 'VBAT'); P('J1', 2, 'G', 'GND')
P('U7', 1, 'G', 'CHG_STAT', {'ang': 270})  # STAT -> U1 P0.07 (open-drain)
P('U7', 2, 'G', 'GND')                 # VSS
P('U7', 3, 'G', 'VBAT')                # VBAT out
P('U7', 4, 'G', 'VBUS')                # VDD
P('U7', 5, 'PIN_L', 'PROG', 270)       # PROG - label at pin, text down
P('R17', 1, 'L', 'PROG'); P('R17', 2, 'G', 'GND')
# Dock pad constellation (USB-C REMOVED 2026-08-31): GND / D- / D+ / 5V
P('D6', 1, 'G', 'VBUS')                       # cathode
P('D6', 2, 'L', 'PAD_5V', {'ang': 270})       # anode <- 5V pad
P('CP1', 1, 'G', 'GND', {'ang': 270})         # PAD_GND
P('CP2', 1, 'L', 'PAD_DM')                    # PAD_DM -> R29 -> USB_DM
P('CP3', 1, 'L', 'PAD_DP')                    # PAD_DP -> R30 -> USB_DP
P('CP4', 1, 'L', 'PAD_5V')                    # PAD_5V -> D6 anode
P('R29', 1, 'G', 'USB_DM'); P('R29', 2, 'L', 'PAD_DM')   # 27R series
P('R30', 1, 'G', 'USB_DP'); P('R30', 2, 'L', 'PAD_DP')   # 27R series
# U11 USBLC6-2SC6 ESD array on the pad side (pins 1/6 = I/O1, 3/4 = I/O2)
P('U11', 1, 'L', 'PAD_DM'); P('U11', 6, 'L', 'PAD_DM')
P('U11', 3, 'L', 'PAD_DP'); P('U11', 4, 'L', 'PAD_DP')
P('U11', 5, 'G', 'VBUS');   P('U11', 2, 'G', 'GND')
P('C3', 1, 'G', '3V3'); P('C3', 2, 'G', 'GND')

# ---------------- Block 3: Boost ----------------
P('U2', 1, 'L', 'BOOST_FB')                    # FB
P('U2', 2, 'G', 'BOOST_EN')
P('U2', 3, 'G', 'VBAT')
P('U2', 4, 'G', 'GND')
P('U2', 5, 'L', 'BOOST_SW', {'ang': 90})       # SW, label up to dodge L1/5V
P('U2', 6, 'G', '5V')
P('L1', 1, 'G', 'VBAT'); P('L1', 2, 'L', 'BOOST_SW')
P('C5', 1, 'G', 'VBAT'); P('C5', 2, 'G', 'GND')
P('C6', 1, 'G', '5V');  P('C6', 2, 'G', 'GND')
P('R15', 1, 'G', '5V'); P('R15', 2, 'L', 'BOOST_FB')
P('R16', 1, 'L', 'BOOST_FB'); P('R16', 2, 'G', 'GND')
P('D5', 1, 'G', '5V'); P('D5', 2, 'L', 'BOOST_SW')

# ---------------- Block 4: I2C sensors ----------------
P('R1', 1, 'G', '3V3'); P('R1', 2, 'G', 'SDA')
P('R2', 1, 'G', '3V3'); P('R2', 2, 'G', 'SCL')
P('U10', 1, 'G', 'GND'); P('U10', 2, 'G', '1V8'); P('U10', 3, 'G', '3V3')
P('C14', 1, 'G', '3V3'); P('C14', 2, 'G', 'GND')
P('C15', 1, 'G', '1V8'); P('C15', 2, 'G', 'GND')
P('U3', 1, 'G', '1V8')
P('U3', 2, 'G', 'SCL'); P('U3', 8, 'G', 'SDA')
P('U3', 6, 'G', 'GND')             # GPIO tied low (not 3.6V tolerant)
# U3 pins 3 (GND) + 5 (PGND): UJOIN construct below
P('U3', 7, 'NC'); P('U3', 4, 'NC')  # INT, LDR
P('C7', 1, 'G', '1V8'); P('C7', 2, 'G', 'GND')
P('U4', 1, 'G', 'SHLD1')
P('U4', 2, 'L', 'CIN1'); P('U4', 3, 'L', 'CIN2')
P('U4', 4, 'NC'); P('U4', 5, 'NC'); P('U4', 6, 'NC')   # CIN3, CIN4, SHLD2
P('U4', 9, 'G', 'SCL'); P('U4', 10, 'G', 'SDA')
P('U4', 8, 'G', '3V3'); P('U4', 7, 'G', 'GND')
P('C8', 1, 'G', '3V3'); P('C8', 2, 'G', 'GND')
P('U5', 1, 'G', 'GND'); P('U5', 2, 'G', '3V3')
P('U5', 3, 'G', 'SCL'); P('U5', 4, 'G', 'SDA')
P('C9', 1, 'G', '3V3'); P('C9', 2, 'G', 'GND')
P('U8', 1, 'G', 'GND')             # SDO/SA0 -> addr 0x6A
P('U8', 2, 'NC'); P('U8', 3, 'NC') # SDX, SCX (aux i/f unused)
P('U8', 10, 'NC'); P('U8', 11, 'NC')  # OCS_Aux, SDO_Aux
P('U8', 12, 'G', '3V3')            # CS -> I2C mode
P('U8', 13, 'G', 'SCL'); P('U8', 14, 'G', 'SDA')
P('U8', 4, 'G', 'IMU_INT', {'ang': 270})
P('U8', 9, 'NC')                   # INT2
# U8 pins 5 (VDDIO) + 8 (VDD): UJOIN below (hidden GND pin 7 stacks on 6)
P('U8', 6, 'G', 'GND')
P('C10', 1, 'G', '3V3'); P('C10', 2, 'G', 'GND')

# ---------------- Block 5: Mic ----------------
P('U9', 1, 'G', 'PDM_DATA', {'len': 5.08, 'ang': 270})
P('U9', 3, 'G', 'PDM_CLK', {'ang': 270})
P('U9', 4, 'G', 'GND')             # SELECT -> mono/left
P('U9', 2, 'G', '3V3'); P('U9', 5, 'G', 'GND')
P('C11', 1, 'G', '3V3'); P('C11', 2, 'G', 'GND')
P('C17', 1, 'G', '3V3'); P('C17', 2, 'G', 'GND')

# ---------------- Block 6: 1-wire ----------------
P('U6', 1, 'G', 'GND'); P('U6', 3, 'G', '3V3')
P('U6', 2, 'WL', 'R14', '2', 'OW_DQ', 'G', (342.9, 181.61), 270)
P('R14', 1, 'G', '3V3')

# ---------------- Block 7: EC front end ----------------
P('R3', 1, 'G', 'EC_DRV_LO')
P('R3', 2, 'WL', 'R4', '1', 'EC_NODE_D', 'L', (393.7, 173.99), 270)
P('R4', 2, 'G', 'EC_DRV_HI', {'ang': 90})
P('C1', 1, 'L', 'EC_NODE_D', {'ang': 270})
P('C1', 2, 'G', 'EC_A', {'ang': 270})
P('C2', 1, 'G', 'EC_B', {'ang': 270})
P('C2', 2, 'G', 'GND')
P('E1', 1, 'G', 'EC_SENSE_A')
P('E2', 1, 'G', 'EC_SENSE_B', {'ang': 270})
P('E3', 1, 'G', 'EC_A')
P('E4', 1, 'G', 'EC_B')
P('R20', 1, 'G', '3V3'); P('R20', 2, 'G', 'EC_BIAS')
P('R21', 1, 'G', 'EC_BIAS'); P('R21', 2, 'G', 'GND')
P('R22', 1, 'G', 'EC_BIAS'); P('R22', 2, 'G', 'EC_A')
P('R23', 1, 'G', 'EC_BIAS'); P('R23', 2, 'G', 'EC_B')
P('R26', 1, 'G', 'EC_BIAS'); P('R26', 2, 'G', 'EC_SENSE_A')
P('R27', 1, 'G', 'EC_BIAS'); P('R27', 2, 'G', 'EC_SENSE_B')
P('C16', 1, 'G', 'EC_BIAS'); P('C16', 2, 'G', 'GND')

# ---------------- Block 8: LED drivers ----------------
for row, (rs, d, q, rg, net, k, ya, yk) in enumerate([
        ('R5', 'D1', 'Q1', 'R8', 'LED_WHITE', 1, 280.67, 273.05),
        ('R6', 'D2', 'Q2', 'R9', 'LED_850', 2, 300.99, 293.37),
        ('R7', 'D3', 'Q3', 'R10', 'LED_365', 3, 321.31, 313.69)]):
    P(rs, 1, 'G', '5V')
    # Rseries -> anode, labelled LEDk_A; cathode -> drain, labelled LEDk_K
    P(rs, 2, 'WL', d, '2', 'LED%d_A' % k, 'L', (33.02, ya), 0)
    P(d, 1, 'WL', q, '3', 'LED%d_K' % k, 'L', (49.53, yk), 0)
    P(q, 1, 'G', net, {'ang': 270})          # gate
    P(q, 2, 'G', 'GND')                      # source
    P(rg, 1, 'G', net); P(rg, 2, 'G', 'GND') # gate pulldown

# R8/R9/R10 sit in one column; facing vertical labels in the 12.7 mm gaps
# collide. Use longer stubs + horizontal labels for the facing pins.
P('R8', 2, 'G', 'GND', {'len': 5.08, 'ang': 0})
P('R9', 1, 'G', 'LED_850', {'len': 5.08, 'ang': 0})
P('R9', 2, 'G', 'GND', {'len': 5.08, 'ang': 0})
P('R10', 1, 'G', 'LED_365', {'len': 5.08, 'ang': 0})

# ---------------- Block 9: Heater ----------------
P('R11', 1, 'WL', 'Q4', '3', 'HTR_SW', 'L', (110.49, 273.05), 0)
P('R11', 2, 'G', '5V')
P('Q4', 1, 'G', 'HEATER_EN', {'ang': 270})
P('Q4', 2, 'G', 'GND')
P('R12', 1, 'G', 'HEATER_EN'); P('R12', 2, 'G', 'GND')

# ---------------- Block 10: Piezo ----------------
P('PZ1', 1, 'G', '3V3')
P('PZ1', 2, 'L', 'PZ_SW')
P('R13', 1, 'L', 'PZ_SW')
P('R13', 2, 'WL', 'Q5', '3', 'PZ_DRV', 'L', (186.69, 273.05), 0)
P('Q5', 1, 'G', 'PIEZO', {'ang': 270})
P('Q5', 2, 'G', 'GND')
P('R24', 1, 'G', '3V3'); P('R24', 2, 'L', 'PZ_SW')   # bleed across PZ1
P('R28', 1, 'G', 'PIEZO'); P('R28', 2, 'G', 'GND')   # NEW gate pulldown

# ---------------- Block 10b: Status LED + glow ring (2026-08-31) ----------
P('R31', 1, 'G', 'LED_STAT')                     # top, to P0.12
P('R31', 2, 'WL', 'D8', '2', 'LED_STAT_A', 'L', (321.31, 359.41), 0)
P('D8', 1, 'G', 'GND')                           # cathode up
P('D9', 2, 'G', '5V')                            # anode
P('D9', 1, 'L', '5V_RING')                       # cathode -> ring rail
P('R32', 1, 'G', 'RING_DATA')                    # left, from P1.00
P('R32', 2, 'WL', 'D10', '4', 'RING_D0', 'L', (379.73, 355.6), 90)
RING_X = [389.89, 415.29, 440.69, 466.09, 491.49, 516.89]
for k in range(6):
    d = 'D%d' % (10 + k)
    P(d, 2, 'L', '5V_RING', {'ang': 90})         # VDD up
    P(d, 3, 'G', 'GND')                          # GND down
    if k < 5:                                    # DOUT -> next DIN
        P(d, 1, 'WL', 'D%d' % (11 + k), '4', 'RING_D%d' % (k + 1), 'L',
          (RING_X[k] + 12.7, 355.6), 90)
P('D15', 1, 'NC')                                # end of chain
for k in range(6):                               # ring decouplers
    c = 'C%d' % (18 + k)
    P(c, 1, 'L', '5V_RING', {'ang': 90})
    P(c, 2, 'G', 'GND')
P('#FLG05', 1, 'L', '5V_RING')                   # ring rail is power_in-fed

# ---------------- Block 11: NFC ----------------
P('L2', 1, 'G', 'NFC1'); P('L2', 2, 'G', 'NFC2')
P('C12', 1, 'G', 'NFC1'); P('C12', 2, 'G', 'GND')
P('C13', 1, 'G', 'NFC2'); P('C13', 2, 'G', 'GND')

# ---------------- Block 12: UVC ----------------
P('R25', 1, 'G', '5V')
P('R25', 2, 'WL', 'D7', '2', 'UVC_A', 'L', (33.02, 359.41), 0)
P('D7', 1, 'G', 'UVC_EN')                    # cathode -> GPIO low-side sink
P('PD1', 1, 'G', '3V3')                      # Vcc (lead order Vcc/Vout/GND)
P('PD1', 2, 'G', 'UVC_PD')                   # Vout
P('PD1', 3, 'G', 'GND')

# ---------------- Block 13: TPs + flags ----------------
tps = {1:'3V3', 2:'GND', 3:'GND', 4:'SDA', 5:'SCL', 6:'EC_A', 7:'EC_B',
       8:'EC_DRV_LO', 9:'EC_DRV_HI', 10:'VBAT', 11:'5V', 12:'BOOST_EN',
       13:'SWDIO', 14:'SWCLK', 15:'RESET', 16:'3V3', 17:'GND', 18:'VBUS'}
for n, net in tps.items():
    P('TP%d' % n, 1, 'G', net)
# PWR_FLAG assignment: 3V3/GND/VBUS are the undriven power nets. VBAT is
# already driven by U7 pin 3 (power output) - a flag there is a hard ERC
# pin_to_pin error, so the 4th flag marks CHG_PAD (external power entry,
# passive-only net, conflict-free) instead. Deviation from guide documented.
P('TP19', 1, 'G', 'UART_TX')
P('TP20', 1, 'G', 'UART_RX')
P('TP21', 1, 'G', 'BTN_DFU')     # tweezer-to-GND forces DFU (commissioning item 2)
P('TP22', 1, 'G', 'BTN_FRESET')
P('#FLG01', 1, 'G', '3V3')
P('#FLG02', 1, 'G', 'GND')
P('#FLG03', 1, 'G', 'VBUS')
P('#FLG04', 1, 'L', 'PAD_5V')

# FDC pads
P('FDC1', 1, 'L', 'CIN1')
P('FDC2', 1, 'L', 'CIN2')

# ---------------- Special constructs ----------------
# UJOIN: (refA,pinA), (refB,pinB), drop distance, net, label kind, label angle
UJOINS = [
    (('U3', '3'), ('U3', '5'), 2.54, 'GND', 'G', 270),   # GND + PGND
    (('U8', '5'), ('U8', '8'), 2.54, '3V3', 'G', 90),    # VDDIO + VDD
]
# PAIRJOIN: (refA,pinA), (refB,pinB), stub len, net, kind, label pos, angle
PAIRJOINS = []

# Symbols removed by the 2026-08-31 dock change (USB-C deleted)
REMOVE_REFS = ['J2', 'R18', 'R19',
               'H1', 'H2', 'H3']  # M2 holes dropped 2026-08-31 (Paolo): shell-ledge retention, O40 area

FP_0603 = 'Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder'
# New symbols: ref -> (lib_id, x, y, value, footprint)
NEW_SYMBOLS = {
    'R28': ('Device:R', 226.06, 276.86, '100k', FP_0603),
    'R29': ('Device:R', 273.05, 41.91, '27R', FP_0603),
    'R30': ('Device:R', 288.29, 41.91, '27R', FP_0603),
    'CP3': ('Connector_Generic:Conn_01x01', 292.1, 90.17, 'PAD_DP',
            'puck:CHG_Pad_D2.0mm'),
    'CP4': ('Connector_Generic:Conn_01x01', 312.42, 90.17, 'PAD_5V',
            'puck:CHG_Pad_D2.0mm'),
    'TP19': ('Connector:TestPoint', 411.48, 294.64, 'UART_TX',
             'TestPoint:TestPoint_Pad_D1.5mm'),
    'TP20': ('Connector:TestPoint', 426.72, 294.64, 'UART_RX',
             'TestPoint:TestPoint_Pad_D1.5mm'),
    'TP21': ('Connector:TestPoint', 441.96, 294.64, 'BTN_DFU',
             'TestPoint:TestPoint_Pad_D1.5mm'),
    'TP22': ('Connector:TestPoint', 457.2, 294.64, 'BTN_FRESET',
             'TestPoint:TestPoint_Pad_D1.5mm'),
    'U11': ('puck-extra:USBLC6-2SC6', 210.82, 48.26, 'USBLC6-2SC6',
            'Package_TO_SOT_SMD:SOT-23-6'),
    'R31': ('Device:R', 317.5, 355.6, '1k', FP_0603),
    'R32': ('Device:R', 374.65, 355.6, '220R', FP_0603, 90),
    'D8': ('Device:LED', 332.74, 355.6, 'STATUS 0603',
           'LED_SMD:LED_0603_1608Metric', 270),
    'D9': ('Diode:SS34', 359.41, 349.25, '1N5819WS/SS14 ring supply',
           'Diode_SMD:D_SOD-123'),
    '#FLG05': ('power:PWR_FLAG', 415.29, 311.15, 'PWR_FLAG', ''),
}
for _k in range(6):
    NEW_SYMBOLS['D%d' % (10 + _k)] = (
        'puck-extra:XL-1010RGBC', 389.89 + 25.4 * _k, 355.6,
        'XL-1010RGBC', 'puck:LED_XL-1010RGBC')
    NEW_SYMBOLS['C%d' % (18 + _k)] = (
        'Device:C', 302.26 + 12.7 * _k, 383.54, '100nF',
        'Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder')
# Value/Footprint fixes on existing pad symbols (identity changed by the delta)
PATCH_VALUES = {
    'CP1': ('PAD_GND', 'puck:CHG_Pad_D2.0mm'),
    'CP2': ('PAD_DM', 'puck:CHG_Pad_D2.0mm'),
}
