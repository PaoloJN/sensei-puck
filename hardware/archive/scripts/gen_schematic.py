#!/usr/bin/env python3
# ============================================================================
# RETIRED 2026-08-31 — DO NOT RUN.
# Paolo manually reorganized the schematic (A2 page, custom placement) after
# the final generated version (103 symbols). Running this script would
# OVERWRITE his layout and any wiring. It is kept only as historical record
# of how the placement-only sheet was produced. The .kicad_sch file is now
# the sole source of truth, maintained by hand in the KiCad GUI.
# ============================================================================
"""Generate puck-carrier.kicad_sch — Water Puck INTEGRATED board (spin 1).

"The PCB is the puck": bare MDBT50Q-1MV2 nRF52840 module, sensors mounted
directly on a 50 mm round board, LiPo + MCP73831 charger + USB-C, TPS61023
boost 5 V rail. See ../carrier-board-spec.md. Incorporates the 2026-08-31
design-review fix list (docs/design-review.md §4, items 1-11), plus the
review follow-up batch: 4-electrode EC upgrade (E3/E4 outer force pair,
E1/E2 inner sense -> AIN2/AIN3), second FDC1004 pad (FDC2 on CIN2), and the
DNP v2 UVC organics channel (D7 275 nm LED, PD1 GUVC-T21GH, R25). EC drive
moved P0.28/P0.29 -> P0.22/P0.23 (full-drive pads; the old pair is
low-frequency-only per MDBT50Q datasheet §2.6) — spec pin map is truth.

PLACEMENT-ONLY schematic: all symbols placed, grouped into labeled blocks,
with reference designators / Values / Footprints hardcoded. NO wires, NO
labels, NO junctions, NO no-connect markers — wiring is done by hand in the
GUI afterwards.

Symbol definitions are extracted verbatim from their source .kicad_sym
libraries and embedded in lib_symbols with "Lib:Name" ids. Derived symbols
(2N7002/AO3400A/SS34/DS18B20 extend parents) are flattened against their
parent before embedding, exactly as eeschema does (keeps ERC
lib_symbol_mismatch quiet).

Run:  python3 scripts/gen_schematic.py [output.kicad_sch]
(default output: <project>/puck-carrier.kicad_sch)
"""

import re
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # project dir
STOCK = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
PUCK_EXTRA_LIB = HERE / "lib/symbols/puck-extra.kicad_sym"

PROJECT = "puck-carrier"
G = 2.54  # schematic grid


def new_uuid() -> str:
    return str(uuid.uuid4())


# ----------------------------------------------------------------------------
# s-expression symbol extraction (bracket matching, string-aware)
# ----------------------------------------------------------------------------

def extract_block(text: str, start: int) -> str:
    """Return the balanced (...) block starting at text[start] == '('."""
    depth = 0
    i = start
    in_str = False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        i += 1
    raise ValueError("unbalanced s-expression")


_lib_cache: dict[Path, str] = {}


def extract_symbol(lib_path: Path, name: str) -> str:
    if lib_path not in _lib_cache:
        _lib_cache[lib_path] = lib_path.read_text()
    text = _lib_cache[lib_path]
    needle = f'(symbol "{name}"'
    idx = text.find(needle)
    if idx < 0:
        raise SystemExit(f"symbol {name!r} not found in {lib_path}")
    return extract_block(text, idx)


def reindent(block: str, extra_tabs: int = 1) -> str:
    """Library symbols sit at depth 1; in the schematic they sit at depth 2."""
    pad = "\t" * extra_tabs
    lines = block.split("\n")
    out = [lines[0]] + [pad + ln if ln.strip() else ln for ln in lines[1:]]
    return "\n".join(out)


def property_blocks(block: str) -> dict[str, str]:
    """Map property name -> full '(property ...)' block text."""
    out: dict[str, str] = {}
    for m in re.finditer(r'\(property\s+"([^"]+)"', block):
        out[m.group(1)] = extract_block(block, m.start())
    return out


def flatten(parent_block: str, child_block: str, parent_name: str,
            child_name: str) -> str:
    """Flatten a derived symbol the way eeschema does before embedding:
    parent body + child's property overrides + renamed symbol/unit names."""
    flat = parent_block
    child_props = property_blocks(child_block)
    for name, child_prop in child_props.items():
        m = re.search(r'\(property\s+"%s"' % re.escape(name), flat)
        if m:
            old = extract_block(flat, m.start())
            flat = flat[:m.start()] + child_prop + flat[m.start() + len(old):]
        else:  # child-only property: insert after the last parent property
            last = None
            for pm in re.finditer(r'\(property\s+"[^"]+"', flat):
                last = pm
            old = extract_block(flat, last.start())
            end = last.start() + len(old)
            flat = flat[:end] + "\n\t\t" + child_prop + flat[end:]
    flat = flat.replace(f'(symbol "{parent_name}_', f'(symbol "{child_name}_')
    flat = flat.replace(f'(symbol "{parent_name}"', f'(symbol "{child_name}"', 1)
    return flat


def lib_symbol(libname: str, symname: str, lib_path: Path) -> tuple[str, list[str]]:
    """Return (embedded lib_symbols entry text, pin numbers).

    The entry is renamed Lib:Name. Derived symbols (extends) are flattened
    against their parent, matching what eeschema writes into .kicad_sch.
    """
    block = extract_symbol(lib_path, symname)
    m = re.search(r'\(extends\s+"([^"]+)"\)', block)
    if m:
        parent = extract_symbol(lib_path, m.group(1))
        block = flatten(parent, block, m.group(1), symname)
        pins = re.findall(r'\(number\s+"([^"]+)"', parent)
    else:
        pins = re.findall(r'\(number\s+"([^"]+)"', block)
    renamed = block.replace(f'(symbol "{symname}"', f'(symbol "{libname}:{symname}"', 1)
    return "\t\t" + reindent(renamed), pins


# ----------------------------------------------------------------------------
# emit helpers
# ----------------------------------------------------------------------------

def fmt(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def prop(name: str, value: str, x: float, y: float, angle: int = 0,
         hide: bool = False, justify_left: bool = True) -> str:
    esc = value.replace("\\", "\\\\").replace('"', '\\"')
    lines = [f'\t\t(property "{name}" "{esc}"',
             f"\t\t\t(at {fmt(x)} {fmt(y)} {angle})"]
    if hide:
        lines.append("\t\t\t(hide yes)")
    lines += ["\t\t\t(show_name no)",
              "\t\t\t(do_not_autoplace no)",
              "\t\t\t(effects",
              "\t\t\t\t(font",
              "\t\t\t\t\t(size 1.27 1.27)",
              "\t\t\t\t)"]
    if justify_left and not hide:
        lines.append("\t\t\t\t(justify left)")
    lines += ["\t\t\t)", "\t\t)"]
    return "\n".join(lines)


class Emitter:
    def __init__(self, root_uuid: str, pins: dict[str, list[str]]):
        self.root_uuid = root_uuid
        self.pins = pins
        self.items: list[str] = []
        self.n_symbols = 0

    def place(self, lib_id: str, ref: str, value: str, footprint: str,
              x: float, y: float, rot: int = 0, in_bom: bool = True,
              fields_at: tuple[float, float] | None = None,
              hide_value: bool = False) -> None:
        if fields_at is not None:
            # explicit top-left anchor for Ref/Value (horizontal, left-just.)
            fx, fy = fields_at
            ref_prop = prop("Reference", ref, fx, fy)
            val_prop = prop("Value", value, fx, fy + G, hide=hide_value)
        elif rot in (90, 270):
            # field angle 90 in the rotated frame renders horizontal;
            # centered above/below the body, clear of the graphics.
            ref_prop = prop("Reference", ref, x, y - 2 * G, angle=90,
                            justify_left=False)
            val_prop = prop("Value", value, x, y + 2 * G, angle=90,
                            justify_left=False, hide=hide_value)
        else:
            ref_prop = prop("Reference", ref, x + 2 * G, y - G / 2)
            val_prop = prop("Value", value, x + 2 * G, y + G / 2,
                            hide=hide_value)
        lines = ["\t(symbol",
                 f'\t\t(lib_id "{lib_id}")',
                 f"\t\t(at {fmt(x)} {fmt(y)} {rot})",
                 "\t\t(unit 1)",
                 "\t\t(body_style 1)",
                 "\t\t(exclude_from_sim no)",
                 f"\t\t(in_bom {'yes' if in_bom else 'no'})",
                 "\t\t(on_board yes)",
                 "\t\t(in_pos_files yes)",
                 "\t\t(dnp no)",
                 "\t\t(fields_autoplaced no)",
                 f'\t\t(uuid "{new_uuid()}")',
                 ref_prop,
                 val_prop,
                 prop("Footprint", footprint, x, y, hide=True),
                 prop("Datasheet", "", x, y, hide=True),
                 prop("Description", "", x, y, hide=True)]
        for p in self.pins[lib_id]:
            lines += [f'\t\t(pin "{p}"', f'\t\t\t(uuid "{new_uuid()}")',
                      "\t\t)"]
        lines += ["\t\t(instances",
                  f'\t\t\t(project "{PROJECT}"',
                  f'\t\t\t\t(path "/{self.root_uuid}"',
                  f'\t\t\t\t\t(reference "{ref}")',
                  "\t\t\t\t\t(unit 1)",
                  "\t\t\t\t)",
                  "\t\t\t)",
                  "\t\t)",
                  "\t)"]
        self.items.append("\n".join(lines))
        self.n_symbols += 1

    def title(self, text: str, x: float, y: float) -> None:
        esc = text.replace("\\", "\\\\").replace('"', '\\"')
        self.items.append("\n".join([
            f'\t(text "{esc}"',
            "\t\t(exclude_from_sim no)",
            f"\t\t(at {fmt(x)} {fmt(y)} 0)",
            "\t\t(effects",
            "\t\t\t(font",
            "\t\t\t\t(size 2.54 2.54)",
            "\t\t\t\t(bold yes)",
            "\t\t\t)",
            "\t\t\t(justify left bottom)",
            "\t\t)",
            f'\t\t(uuid "{new_uuid()}")',
            "\t)"]))

    def note(self, text: str, x: float, y: float) -> None:
        """Small design-note text (wiring guidance, review-fix annotations)."""
        esc = text.replace("\\", "\\\\").replace('"', '\\"')
        self.items.append("\n".join([
            f'\t(text "{esc}"',
            "\t\t(exclude_from_sim no)",
            f"\t\t(at {fmt(x)} {fmt(y)} 0)",
            "\t\t(effects",
            "\t\t\t(font",
            "\t\t\t\t(size 1.27 1.27)",
            "\t\t\t)",
            "\t\t\t(justify left bottom)",
            "\t\t)",
            f'\t\t(uuid "{new_uuid()}")',
            "\t)"]))


# ----------------------------------------------------------------------------
# design data — integrated spin 1 (MDBT50Q-1MV2 module, post design review)
# ----------------------------------------------------------------------------

NEEDED = [
    # (libname, symname, source path)
    ("Battery_Management",  "MCP73831-2-OT",       STOCK / "Battery_Management.kicad_sym"),
    ("Connector",           "TestPoint",           STOCK / "Connector.kicad_sym"),
    ("Connector",           "USB_C_Receptacle_USB2.0_16P", STOCK / "Connector.kicad_sym"),
    ("Connector_Generic",   "Conn_01x01",          STOCK / "Connector_Generic.kicad_sym"),
    ("Connector_Generic",   "Conn_01x02",          STOCK / "Connector_Generic.kicad_sym"),
    ("Connector_Generic",   "Conn_01x03",          STOCK / "Connector_Generic.kicad_sym"),
    ("Device",              "Buzzer",              STOCK / "Device.kicad_sym"),
    ("Device",              "C",                   STOCK / "Device.kicad_sym"),
    ("Device",              "L",                   STOCK / "Device.kicad_sym"),
    ("Device",              "LED",                 STOCK / "Device.kicad_sym"),
    ("Device",              "R",                   STOCK / "Device.kicad_sym"),
    ("Diode",               "SS34",                STOCK / "Diode.kicad_sym"),
    ("Mechanical",          "MountingHole",        STOCK / "Mechanical.kicad_sym"),
    ("Regulator_Linear",    "XC6206PxxxMR",        STOCK / "Regulator_Linear.kicad_sym"),
    ("Sensor_Audio",        "IM69D130",            STOCK / "Sensor_Audio.kicad_sym"),
    ("Sensor_Optical",      "AS7341DLG",           STOCK / "Sensor_Optical.kicad_sym"),
    ("Sensor_Temperature",  "DS18B20",             STOCK / "Sensor_Temperature.kicad_sym"),
    ("Transistor_FET",      "AO3400A",             STOCK / "Transistor_FET.kicad_sym"),
    ("power",               "PWR_FLAG",            STOCK / "power.kicad_sym"),
    ("puck-extra",          "MDBT50Q-1MV2",        PUCK_EXTRA_LIB),
    ("puck-extra",          "TPS61023",            PUCK_EXTRA_LIB),
    ("puck-extra",          "FDC1004DGSR",         PUCK_EXTRA_LIB),
    ("puck-extra",          "LSM6DSO",             PUCK_EXTRA_LIB),
    ("puck-extra",          "MS583702BA01-50",     PUCK_EXTRA_LIB),
]

# footprint shorthands
FP_R0603 = "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder"
FP_C0603 = "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
FP_C1210 = "Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder"
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23_Handsoldering"
FP_TP = "TestPoint:TestPoint_Pad_D1.5mm"
FP_ELEC = "puck:EC_Electrode_2x8mm"
FP_LED3528 = "puck:LED_Everlight-SMD3528_3.5x2.8mm_67-21ST"
FP_MIC = "Sensor_Audio:Infineon_PG-LLGA-5-1"     # IM69D130 PG-LLGA-5-1 (stock)
# placeholders to revisit at BOM/layout time (see LIBRARIES.md):
FP_L4X4 = "Inductor_SMD:L_Sunlord_SWPA4030S"


def build(root_uuid: str, pins: dict[str, list[str]]) -> Emitter:
    e = Emitter(root_uuid, pins)

    def u(n: float) -> float:
        return round(n * G, 4)

    def add(lib_id, ref, value, fp, col, row, rot=0, in_bom=True, **kw):
        if "fields_at" in kw:
            kw["fields_at"] = (u(kw["fields_at"][0]), u(kw["fields_at"][1]))
        e.place(lib_id, ref, value, fp, u(col), u(row), rot, in_bom, **kw)

    # --- Block 1: Brain — MDBT50Q module (review fix 1 / C5) ----------------
    e.title("1. BRAIN — MDBT50Q-1MV2 (nRF52840)", u(8), u(10))
    add("puck-extra:MDBT50Q-1MV2", "U1", "MDBT50Q-1MV2",
        "puck:MDBT50Q-1MV2", 26, 27, fields_at=(12, 12.5))
    e.note("USB-C VBUS -> module VBUS pad (52840 USB dead without it) + local decoupling",
           u(8), u(11.5))

    # --- Block 1b: NFC (wake/pairing, etched PCB coil) ----------------------
    e.title("NFC", u(36), u(16))
    add("Device:L", "L2", "NFC PCB coil", "", 38, 20)     # etched at layout
    add("Device:C", "C12", "300pF NFC", FP_C0603, 38, 27)
    add("Device:C", "C13", "300pF NFC", FP_C0603, 38, 33)

    # --- Block 2: Battery + USB-C + charger ---------------------------------
    e.title("2. BATTERY + USB-C + CHARGE", u(48), u(10))
    add("Connector:USB_C_Receptacle_USB2.0_16P", "J2", "USB_C_16P",
        "puck:USB_C_Receptacle_HRO_TYPE-C-31-M-12", 56, 26,
        fields_at=(50, 13.5))
    add("Device:R", "R18", "5.1k", FP_R0603, 68, 20)   # CC1 pulldown
    add("Device:R", "R19", "5.1k", FP_R0603, 74, 20)   # CC2 pulldown
    add("Battery_Management:MCP73831-2-OT", "U7", "MCP73831-2",
        "Package_TO_SOT_SMD:SOT-23-5", 86, 22, fields_at=(81, 16.5))
    add("Device:R", "R17", "4.7k", FP_R0603, 96, 22)   # PROG, ~200 mA
    add("Connector_Generic:Conn_01x02", "J1",
        "LiPo 400-500mAh protected",
        "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", 104, 20)
    add("Device:C", "C3", "100uF", FP_C1210, 122, 21)  # VDD burst buffer
    # magnetic charge pads (5 V in via purchased magnetic pogo cable);
    # FP_ELEC is a placeholder — real pad footprint authored at layout time
    add("Connector_Generic:Conn_01x01", "CP1", "CHG_PAD+ (5V in)", FP_ELEC,
        86, 31)
    add("Connector_Generic:Conn_01x01", "CP2", "CHG_PAD-", FP_ELEC, 86, 35)
    add("Diode:SS34", "D6", "SS14", "Diode_SMD:D_SOD-123", 104, 31,
        fields_at=(101, 26.5))                         # reverse-polarity blk

    # --- Block 3: Boost 5 V rail (review fix 8 / M4: MT3608 -> TPS61023) ----
    # FB divider: VOUT = VREF*(1+R15/R16), VREF = 0.595 V (SLVSF14B §6.5 PWM)
    #   R15=750k / R16=100k -> 0.595*8.5 = 5.06 V (R16 <300k per DS §8.2.2.1)
    # L1: TPS61023 wants 0.37-2.9 uH effective (DS §8.2.2.2) -> 1 uH, not 22 uH
    e.title("3. BOOST 5V (TPS61023)", u(126), u(10))
    add("puck-extra:TPS61023", "U2", "TPS61023",
        "Package_TO_SOT_SMD:SOT-563", 132, 22, fields_at=(127, 15.5))
    add("Device:L", "L1", "1uH >2A sat", FP_L4X4, 142, 20)
    add("Diode:SS34", "D5", "SS34 (DNP - not needed w/ TPS61023)",
        "Diode_SMD:D_SMA", 150, 20, fields_at=(147, 15.5))
    add("Device:R", "R15", "750k", FP_R0603, 132, 30)   # FB top
    add("Device:R", "R16", "100k", FP_R0603, 138, 30)   # FB bottom
    add("Device:C", "C5", "22uF 16V", FP_C0805, 144, 30)
    add("Device:C", "C6", "22uF 16V", FP_C0805, 150, 30)
    e.note("EN VIH 1.2V min -> drivable from 1.8V (pre-UICR) and 3.3V GPIO;"
           " true load disconnect when EN low", u(126), u(35))

    # --- Block 4: on-board I2C sensors --------------------------------------
    e.title("4. I2C SENSORS (ON-BOARD)", u(8), u(44))
    add("Sensor_Optical:AS7341DLG", "U3", "AS7341",
        "puck:AMS_OLGA-8_2x3.1mm_P0.8mm", 16, 52, fields_at=(10, 46.5))
    add("Device:C", "C7", "100nF", FP_C0603, 30, 52)
    add("puck-extra:FDC1004DGSR", "U4", "FDC1004",
        "puck:SOP50P490X110-10N", 44, 52, fields_at=(37, 44.5))
    add("Device:C", "C8", "100nF", FP_C0603, 58, 52)
    e.note("U4: SHLD1 = guard net; SHLD2 NC; CIN2 -> FDC2 pad; CIN3/4 NC (no stubs)",
           u(36), u(58.5))
    add("puck-extra:MS583702BA01-50", "U5", "MS5837-02BA",
        "puck:XDCR_MS583702BA01-50", 16, 66, fields_at=(10, 61))
    add("Device:C", "C9", "100nF", FP_C0603, 30, 66)
    add("puck-extra:LSM6DSO", "U8", "LSM6DSO",
        "Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y", 44, 66,
        fields_at=(38, 60.5))
    add("Device:C", "C10", "100nF", FP_C0603, 58, 66)
    e.note("U8: I2C addr 0x6A (SDO/SA0 -> GND), CS -> VDDIO (I2C mode)",
           u(38), u(73))
    add("Device:R", "R1", "4.7k", FP_R0603, 66, 50)    # SDA pull-up
    add("Device:R", "R2", "4.7k", FP_R0603, 72, 50)    # SCL pull-up
    # 1.8 V LDO for AS7341 VDD only (review fix 2 / C1: abs max 2.2 V)
    add("Regulator_Linear:XC6206PxxxMR", "U10",
        "XC6206P182MR 1.8V->AS7341 only", FP_SOT23, 68, 60,
        fields_at=(63, 55.5))
    add("Device:C", "C14", "1uF", FP_C0603, 66, 66)    # LDO in
    add("Device:C", "C15", "1uF", FP_C0603, 72, 66)    # LDO out

    # --- Block 5: PDM microphone (review fix 10 / M7: -> IM69D130) ----------
    e.title("5. PDM MIC", u(80), u(44))
    add("Sensor_Audio:IM69D130", "U9", "IM69D130", FP_MIC,
        86, 52, fields_at=(81, 46.5))
    add("Device:C", "C11", "100nF", FP_C0603, 96, 52)
    add("Device:C", "C17", "1uF", FP_C0603, 96, 58)    # bulk beside 100n
    e.note("U9: PDM clk 0.4-3.3 MHz (nRF default 1.032 MHz OK);"
           " SELECT -> GND (mono)", u(80), u(63))

    # --- Block 6: 1-wire ----------------------------------------------------
    e.title("6. 1-WIRE (DS18B20)", u(102), u(44))
    add("Sensor_Temperature:DS18B20", "U6", "DS18B20",
        "Package_TO_SOT_THT:TO-92_Inline", 108, 53, fields_at=(103, 46.5))
    add("Device:R", "R14", "4.7k", FP_R0603, 118, 51)

    # --- Block 7: EC front end (review fixes 3 / C3+C4; 4-electrode upgrade)
    e.title("7. EC FRONT END (4-WIRE)", u(126), u(44))
    add("Device:R", "R3", "1k", FP_R0603, 130, 50, rot=90)     # EC_DRV_LO
    add("Device:R", "R4", "100k", FP_R0603, 130, 56, rot=90)   # EC_DRV_HI
    add("Device:C", "C1", "4.7uF X7R", FP_C0805, 140, 50, rot=90)  # ->force A
    add("Connector_Generic:Conn_01x01", "E3", "EC_FORCE_A", FP_ELEC, 150, 46)
    add("Connector_Generic:Conn_01x01", "E1", "ELECTRODE_A", FP_ELEC, 150, 50)
    add("Device:C", "C2", "4.7uF X7R", FP_C0805, 140, 62, rot=90)  # force B->GND
    add("Connector_Generic:Conn_01x01", "E2", "ELECTRODE_B", FP_ELEC, 150, 62)
    add("Connector_Generic:Conn_01x01", "E4", "EC_FORCE_B", FP_ELEC, 150, 66)
    # mid-rail bias network (fix C3): R20/R21 divider + C16 tap,
    # R22/R23 legs to each electrode/AIN node
    add("Device:R", "R20", "1M", FP_R0603, 157, 48)    # VDD -> tap
    add("Device:R", "R21", "1M", FP_R0603, 157, 52)    # tap -> GND
    add("Device:C", "C16", "100nF", FP_C0603, 157, 56)  # tap decoupling
    add("Device:R", "R22", "1M", FP_R0603, 157, 60)    # tap -> force A node
    add("Device:R", "R23", "1M", FP_R0603, 157, 64)    # tap -> force B node
    add("Device:R", "R26", "1M", FP_R0603, 157, 68)    # tap -> sense A node
    add("Device:R", "R27", "1M", FP_R0603, 157, 72)    # tap -> sense B node
    e.note("Bias: R20/R21 mid-rail divider, C16 at tap; R22/R23 tap->each AIN"
           " node. SAADC RESP/RESN = Bypass.", u(126), u(70))
    e.note("4-wire: E3/E4 = outer FORCE (EC_DRV via R3/R4 + C1/C2, monitored"
           " on AIN0/1); E1/E2 = inner SENSE", u(126), u(74))
    e.note("-> AIN2/AIN3 (P0.04/P0.05), no current, fouling-immune; R26/R27"
           " bias the sense nodes from the tap.", u(126), u(76))
    e.note("2-electrode firmware fallback = drive+sense on the force pair.",
           u(126), u(78))
    e.note("R26/R27: bias legs for 4-wire sense nodes (AIN2/AIN3) — review C3",
           u(126), u(80))

    # --- Block 8: LED drivers x3 (loads on 5 V rail) ------------------------
    # review fix 6 / M5: 2N7002 -> AO3400A (full enhancement at 3.3 V gate;
    # all four FETs now identical -> one BOM line); 100k pulldowns keep LEDs
    # off while GPIOs are Hi-Z during boot/DFU.
    e.title("8. LED DRIVERS x3 (5V)", u(8), u(76))
    for x, rr, rv, dr, dv, qr, rpd in [
        (14, "R5", "220R", "D1", "WHITE", "Q1", "R8"),
        (26, "R6", "360R", "D2", "IR850", "Q2", "R9"),
        (38, "R7", "150R", "D3", "UV365", "Q3", "R10"),
    ]:
        add("Device:R", rr, rv, FP_R0603, x, 82)               # from 5V
        add("Device:LED", dr, dv, FP_LED3528, x, 89, rot=270)
        add("Transistor_FET:AO3400A", qr, "AO3400A", FP_SOT23, x - 2, 96)
        add("Device:R", rpd, "100k", FP_R0603, x - 8, 98)      # gate pulldown

    # --- Block 9: Heater ----------------------------------------------------
    e.title("9. HEATER", u(50), u(76))
    add("Device:R", "R11", "100R 1W 2512",
        "Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder", 56, 82)
    add("Transistor_FET:AO3400A", "Q4", "AO3400A", FP_SOT23, 54, 90)
    add("Device:R", "R12", "100k", FP_R0603, 48, 92)           # gate pulldown

    # --- Block 10: Piezo (review fix 7 / M2: low-side FET, off the GPIO) ----
    e.title("10. PIEZO", u(70), u(76))
    add("Device:R", "R13", "220R", FP_R0603, 74, 82, rot=90)   # series, from 5V/VBAT
    add("Device:Buzzer", "PZ1", "PiezoDisc",
        "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm", 82, 82)
    add("Transistor_FET:AO3400A", "Q5", "AO3400A", FP_SOT23, 74, 90)
    add("Device:R", "R24", "1M", FP_R0603, 82, 92)   # bleed across piezo disc
    e.note("Piezo: 5V/VBAT -> R13 -> PZ1 -> Q5 drain; Q5 gate <- PIEZO GPIO;"
           " R24 bleed across disc", u(70), u(97))

    # --- Block 11: Test points / SWD / mechanical ---------------------------
    e.title("11. TEST POINTS / SWD / MECHANICAL", u(92), u(76))
    add("power:PWR_FLAG", "#FLG01", "PWR_FLAG", "", 96, 82)    # for VBAT
    add("power:PWR_FLAG", "#FLG02", "PWR_FLAG", "", 104, 82)   # for VDD
    add("power:PWR_FLAG", "#FLG03", "PWR_FLAG", "", 112, 82)   # for 5V
    add("power:PWR_FLAG", "#FLG04", "PWR_FLAG", "", 120, 82)   # for GND
    tp_row1 = ["VDD", "GND", "GND", "SDA", "SCL",
               "EC_A", "EC_B", "EC_DRV_LO", "EC_DRV_HI"]        # TP1-TP9
    tp_row2 = ["VBAT", "5V", "BOOST_EN",
               "SWDIO", "SWDCLK", "RESET", "VDD", "GND",
               "VBUS"]                                          # TP10-TP18
    for i, net in enumerate(tp_row1):
        add("Connector:TestPoint", f"TP{i + 1}", net, FP_TP, 96 + 6 * i, 90)
    for i, net in enumerate(tp_row2):
        add("Connector:TestPoint", f"TP{i + 10}", net, FP_TP, 96 + 7 * i, 97)
    add("Connector_Generic:Conn_01x01", "FDC1", "FDC_SENSE_PAD",
        "puck:FDC_Sense_Pad_10mm", 76, 104)
    # second capacitive pad at a different board radius = redundant level
    # gradient (CIN2)
    add("Connector_Generic:Conn_01x01", "FDC2", "FDC CIN2 pad",
        "puck:FDC_Sense_Pad_10mm", 84, 104)
    for ref, col in (("H1", 92), ("H2", 98), ("H3", 104)):
        add("Mechanical:MountingHole", ref, "MountingHole",
            "MountingHole:MountingHole_2.2mm_M2", col, 104,
            in_bom=False, hide_value=True)

    # --- Block 12: UVC organics channel (DNP - populate at v2) --------------
    # Grouped with the optical zone. D7: 3535-class 275 nm emitter on a stock
    # Cree-XP 3.45x3.45 mm land pattern (pad 3 = thermal, unconnected at v1;
    # exact emitter footprint re-verified when a part is chosen). PD1:
    # GUVC-T21GH is a TO-5 3-lead can (Vcc/Vout/GND, integrated TI amp,
    # 1.8-5.5 V, Vout = 0.355 V per mW/cm^2) — datasheet on file
    # docs/datasheets/guvc-t21gh.pdf; NOT a 2-pad SMD part.
    e.title("12. UVC ORGANICS (DNP - v2)", u(8), u(102))
    add("Device:R", "R25", "DNP", FP_R0603, 14, 107)     # D7 series (v2 sizes)
    add("Device:LED", "D7", "275nm UVC (DNP - v2)", "LED_SMD:LED_Cree-XP",
        24, 107, rot=270)
    add("Connector_Generic:Conn_01x03", "PD1", "GUVC-T21GH (DNP - v2)",
        "Package_TO_SOT_THT:TO-5-3_Window", 40, 107)
    e.note("UVC organics channel — v2, populate later; needs 10-20mm folded"
           " path at layout", u(8), u(112))
    e.note("D7 <- UVC_EN (P0.11) via R25; PD1 pins Vcc/Vout/GND (TO-5, int."
           " TIA) — Vout -> UVC_PD (P0.31/AIN7)", u(8), u(114))
    e.note("verify PD1 lead-vs-tab numbering against the can before v2"
           " populate", u(8), u(116))

    return e


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "puck-carrier.kicad_sch"
    root_uuid = new_uuid()

    lib_entries: list[str] = []
    pins: dict[str, list[str]] = {}
    for libname, symname, path in NEEDED:
        entry, pin_list = lib_symbol(libname, symname, path)
        lib_entries.append(entry)
        pins[f"{libname}:{symname}"] = pin_list

    e = build(root_uuid, pins)

    doc = "\n".join(
        ["(kicad_sch",
         "\t(version 20260306)",
         '\t(generator "eeschema")',
         '\t(generator_version "10.0")',
         f'\t(uuid "{root_uuid}")',
         '\t(paper "A3")',
         "\t(lib_symbols"]
        + lib_entries
        + ["\t)"]
        + e.items
        + ["\t(sheet_instances",
           '\t\t(path "/"',
           '\t\t\t(page "1")',
           "\t\t)",
           "\t)",
           "\t(embedded_fonts no)",
           ")",
           ""])

    out.write_text(doc)
    print(f"wrote {out} ({len(doc)} bytes, {e.n_symbols} symbol instances, "
          f"{len(lib_entries)} lib symbols)")


if __name__ == "__main__":
    main()
