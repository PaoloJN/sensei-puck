# Component and footprint provenance

The schematic and exported engineering BOM define the current population.
The former table mixed retired UVC parts, TO-92 packaging, hand-solder footprints
and obsolete coil geometry; it is preserved in
`../../docs/history/2026-09-paused-baseline/LIBRARIES.md` for provenance only.

## October footprint corrections

- `puck:LED_Everlight_67-21_PLCC2`: D1 67-21/T2C-ZV1W2E/2T and D2
  HIR67-21C/L11/TR8, manufacturer-recommended 1.5 × 2.6 mm lands and 1.5 mm
  gap. Cathode left, chamfer upper-left: body is rotated 180° from vendor top
  view. KiCad Device:LED uses pad 1=K / 2=A, opposite the vendor's numeric labels.
- `puck:LED_Vishay_VLMU1610`: D3 VLMU1610-365-135, Vishay drawing 84374,
  page 5. 1.6 × 1.6 mm body, two 1.6 × 0.65 lands, 0.3 mm gap; pad 1=K north.
- U7 uses stock Battery_Management:MCP73832-2-OT and the existing SOT-23-5
  footprint; selected MPN MCP73832T-2ACI/OT. MCP73831 is not an alternative.
- CP pads: Ø2 mm, 2.54 mm pitch, courtyard radius 1.2 mm. Actual mate check
  remains required; there is no invented generic connector pitch.
- L1 is SWPA4030S1R0NT in stock Sunlord SWPA4030S footprint.
- C12/C13 are DNP tuning positions; L2 is off-board coil wire pads.

The project-local module/sensor/copper footprints are in `lib/footprints/` and
symbols in `lib/symbols/`. The original verification notes for the 61-pad module,
TPS61023, LSM6DSO and other imported parts are retained in the historical file.
Recheck pad numbering and the exact purchased package during release review.
3D models are visual aids and do not establish a correct land pattern.

Sources and physical validation limits: `../../docs/engineering-review-2026-10.md`.
