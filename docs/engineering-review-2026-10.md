# Engineering review — 2026-10-11

The paused project is a useful sensor experiment, but its written completion
claims were ahead of the saved design. The starting PCB contained 121 footprints
and no tracks/vias, while STATUS described a partially routed board. No components
have been purchased and none of the physical performance claims have been tested.

## Corrections made

| Finding | Revision | Verification / remaining limit |
|---|---|---|
| MCP73831 STAT can be driven near its 5V supply; the MCU input is on 3V3. | U7 → MCP73832T-2ACI/OT open-drain variant. R17 → 10 kΩ, approximately 100 mA. | Manufacturer STAT table; still measure charge termination and temperatures. |
| Charger lacked dedicated input/battery bypass parts. | C24/C25 10 µF / 16 V X7R 1206 (TDK C3216X7R1C106K160AC) on VBUS/VBAT; retain ≥4.7 µF effective under bias. | Netlist topology; final routing/MLCC effective capacitance review required. |
| Boost EN could float during reset/bootloader. | R33 100 kΩ pulldown plus safe firmware output initialization. | Netlist and successful build; scope reset behavior on hardware. |
| EC mid-rail permanently biases the wet electrodes relative to exposed dock ground. | R20 feed moved to EC_BIAS_EN / P0.30; low/Hi-Z at idle. | Netlist and variant contract; wet DC/leakage and settling remain physical tests. |
| Dock row had 4.5 mm pitch and wrong mating-part recommendation. | 2.54 mm pitch; top-coordinate order GND, D+, D−, +5V; mate 5358. | Manufacturer drawing. Physical mating/continuity gate remains open. |
| Generic optical LED footprints were not tied to actual devices. | D1/D2 use correct Everlight non-ST PLCC2 lands; D3 uses Vishay VLMU1610 footprint. | Rendered manufacturer package drawings and polarity review. Assembly rotation still needs review. |
| Pressure bypass was placed in the charger area. | C10 moved beside U5 on F.Cu. | Placement check; shortest practical supply/return routing still required. |
| Expansion pins on the PCB did not match the schematic. | Pad nets synchronized from a fresh schematic netlist. | Full board/netlist check, not just net labels. |
| REGOUT0 startup protection was described but absent. | Erased-field-only 3V3 guard in initVariant; preserve other UICR bits and reset. | Carrier/XIAO builds pass; voltage and post-erase behavior need hardware. |
| NFC tuning values were arbitrary. | C12/C13 DNP until the coil/mechanical stack is measured. | DNP flags in schematic and PCB. |
| Boot/charge/EC idle behavior was unspecified in the placeholder application. | Commissioning idle image keeps loads off and reports VBUS detection. | No sensing application or measured low-power/charge-state implementation yet. |
| USB D− was interrupted at U11 by a crossing VBUS trace; U1's battery connection was also open. | Connected D− and VBAT; rerouted the local VBUS crossing. | October 12 refill DRC and schematic parity; USB and power-up still need hardware tests. |
| The routing grid falsely joined two 3V3 pour islands across a 0.0347 mm gap. | Added a short 3V3 bridge; routing tools now determine connectivity from polygons before rasterization. | The corresponding KiCad open is cleared. Overall CAD gate still fails on the 21 remaining opens listed in STATUS.md. |

## Real-life limitations retained as explicit gates

- EC readings need reference standards, source-impedance checks, balanced excitation
  and fouling/leakage trials. Gold ENIG electrodes and four-wire topology alone do
  not establish long-term accuracy.
- Pressure changes are not proof of ingestion. Concentric FDC pads are not two
  water-level probes. Thermal sugar/flow detection has not been demonstrated.
- Clear epoxy can change optical crosstalk/fluorescence. Port masking does not
  establish waterproofness, and an acoustic membrane needs a validated seal.
- A dry air cavity, battery foil and ballast location materially affect submerged
  BLE. The final mechanical stack needs packet-loss and data-transfer tests.
- Burying SWD/reset would make recovery depend on the bootloader. An app that
  crashes before BLE starts must remain recoverable. Keep debug access during
  development; permanent sealing is gated on this test.
- The $300 budget is a ceiling, not a proven BOM cost. Two-sided assembly setup,
  sensor parts and shipping require an itemized quote before purchase.

See [validation-plan.md](validation-plan.md) for measurable release gates.
Current CAD check results belong in `../STATUS.md`; this review is not fabrication
approval. Previous narrative/specification versions are preserved in
`history/2026-09-paused-baseline/`.

## Primary references used

- [Microchip MCP73831/2 datasheet](https://www.microchip.com/content/dam/mchp/documents/APID/ProductDocuments/DataSheets/MCP73831-Family-Data-Sheet-DS20001984H.pdf): STAT states, charge programming and bypass requirements.
- [Adafruit 5412 drawing](https://cdn-shop.adafruit.com/product-files/5412/5412_C17238_4P.pdf) and [5358 mate](https://www.adafruit.com/product/5358): contact geometry and mating component.
- [Vishay VLMU1610-365-135](https://www.vishay.com/docs/84374/vlmu1610-365-135.pdf), page 5: UV package and polarity.
- [Everlight HIR67-21C/L11/TR8](https://en.everlight.com/wp-content/plugins/ItemRelationship/product_files/pdf/HIR67-21C-L11-TR8_datasheet_v4.pdf), page 2, and [Everlight catalogue](https://en.everlight.com/wp-content/uploads/2022/01/2022-2023_Catalogue_s.pdf), printed page 86: PLCC2 lands and white LED selection.
- [Sunlord SWPA series](https://www.sunlordinc.com/uploads/files/20221122/SWPA%20series%20of%20SMD%20Power%20Inductor.pdf): SWPA4030S1R0NT selection.
- [Nordic nRF52840 POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html): regulator configuration and USB supply detection. Project-local component datasheets are in `docs/datasheets/`.
