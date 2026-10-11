# Router pipeline (2026-10-11)

Freerouting 2.5.0 driven from scripts, with KiCad 10 Python for board edits.
Set `ROUTE_WORK` (scratch dir with a `drc/` subdir holding a copy of
`puck-carrier.kicad_pro`, `fp-lib-table` and a `lib` symlink) and
`FREEROUTING_JAR` before use. Close KiCad first.

Order that worked best (see docs/changelog.md 2026-10-11 routing entry):

1. `fanout_planes.py` — one via per 3V3 pad into the In2 plane (and listed GND pads).
2. `route_manual.py` — hand routes under the FDC pads (no foreign via allowed there).
3. `router_export.py` — DSN "router view": no copper fills, outer-layer rule
   areas only, existing wiring protected, complete nets hidden, widths capped
   at 0.25 mm, In2 optionally routable (`--route-inner PWR`).
4. `freeroute.sh` — fan-out off, neck-down off, planes not obstacles.
5. `import.sh` — session import + DRC with the project file beside the board.
6. `round.sh` — stitch GND pads the pours lost, strip neck-downs, re-export
   with the still-open nets, route, import, DRC. Repeat while it improves.
7. `bridge.sh` / `net_islands.py` — expose one pin per GND/3V3 island so the
   router only bridges islands.

Freerouting ignores `class_class` clearance rules and does not count protected
wiring as connectivity, so the tool reports ~40 more opens than KiCad does.
