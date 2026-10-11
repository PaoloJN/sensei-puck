# Water Puck

A college proof of concept: a Ø46 mm sensor PCB intended to sit in a glass or
plastic jug and record changes in its contents. It combines pressure, optical,
conductivity, capacitive and temperature measurements with an nRF52840 BLE module.
It does not assess drinking-water safety.

**No parts have been purchased or hardware tested.** The project is being revised
from its paused design. Read [STATUS.md](STATUS.md) for the current PCB checks and
release blockers; do not order from older renders or fabrication files.

The current electronics use an MCP73832 charger set to approximately 100 mA,
a protected LiPo, a four-contact magnetic USB dock, and a switched 5 V boost rail.
The firmware builds as a commissioning idle image; sensor logging, BLE sync and
the custom bootloader remain to be implemented.

The budget ceiling is about $300 with at most two PCB spins. A real assembled-board
quote and a measured bench prototype must precede permanent sealing.

- [Board specification](hardware/carrier-board-spec.md)
- [Engineering review](docs/engineering-review-2026-10.md)
- [Validation plan](docs/validation-plan.md)
- [Firmware](firmware/README.md)
- [Demonstration scope](docs/product-story.md)
- [Purchasing plan](docs/shopping-list.md)

The editable design is in `hardware/hardware-puck-carrier/`. Historical concepts
and reviews in `planning/` and `docs/history/` are background, not release evidence.
