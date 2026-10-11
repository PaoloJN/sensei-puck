# Purchasing plan — nothing ordered

Budget ceiling: **$300 total**, at most two PCB spins. Prices below are budget
allocations, not supplier quotes. Do not use the old $220 total: it counted a
$25 PCB while the same list estimated $60–90 for assembly, and omitted several
board-mounted parts and setup charges.

| Allocation | Maximum target |
|---|---:|
| First assembled PCB batch, components, shipping and tax | $170 |
| Protected battery, dock, bench supplies and reference standards | $45 |
| Mechanical prototypes and sealing trials | $25 |
| Contingency / second-spin reserve | $60 |
| Total ceiling | **$300** |

Get an itemized two-sided assembly quote before committing. If the first batch
cannot fit, revise scope or obtain lab support before buying; a second assembled
spin may not fit the reserve. Borrow SWD, bench supply, scope, hot air, analytical
balance and calibrated EC/temperature instruments from campus.

## Verify before purchasing

- Battery: protected 1-cell LiPo, roughly 400–500 mAh, explicitly rated for at
  least 100 mA charging. Check JST polarity and actual dimensions; connector
  appearance does not establish polarity. Keep the cell replaceable during tests.
- Dock cable: [Adafruit 5412](https://www.adafruit.com/product/5412), four contacts
  at 2.54 mm pitch. Matching connector is
  [5358](https://www.adafruit.com/product/5358), **not the five-pin 5413**.
  Check mating orientation, contact travel and continuity against a printed PCB
  before fabrication. The cable drawing shows 14.2 mm magnet-center spacing;
  magnet selection and mechanical retention remain to be finalized from the mate.
- Module: MDBT50Q-1MV2. Verify assembly service support; do not budget it twice
  in both an assembly quote and a loose-parts cart.
- Pressure: MS5837-02BA01-50. A -30BA breakout is not an equivalent resolution
  validation of this design. Protect the gel port during assembly and coating.
- U6: **DS18B20U+ (8-pin µSOP)**, not the TO-92 DS18B20+.
- U7: **MCP73832T-2ACI/OT**, not MCP73831. R17 = 10 kΩ (about 100 mA).
- D3: **VLMU1610-365-135**, matched to the project footprint. A generic 3528
  “365 nm” LED is not a pin/land-pattern substitute.
- C12/C13 are DNP until the actual NFC antenna is chosen and tuned. Defer NFC
  purchases until core sensing, charging and recovery work.
- Use certified EC solutions or lab-prepared standards checked against a
  calibrated meter. A cheap TDS pen alone is not an independent accuracy reference.

## Purchase sequence

1. Finish CAD checks and component/footprint verification; obtain an assembly quote.
2. Obtain/borrow the exact dock mate and module for a 1:1 mechanical check, and
   the reference equipment needed to evaluate EC. No whole-project cart yet.
3. Assemble the first carrier and test it unsealed with accessible SWD and reset.
4. Buy sealing materials only after a mechanically defined, leak-tested dummy
   enclosure passes. Preserve budget for corrections found on the first board.

The historical list is in
[the paused baseline](history/2026-09-paused-baseline/shopping-list.md).
