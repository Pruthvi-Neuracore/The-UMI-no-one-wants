# Requirements

## Open decisions

| # | Decision | Options | Status |
|---|---|---|---|
| D1 | CAD authoring | build123d (code CAD) | v0.1 |
| D2 | Actuation | Collector: finger pinch + AS5600. Robot: STS3215 on the same pinion | decided |
| D3 | Camera | IMX335 or D405 on a swappable dock; Insta360 later | decided |
| D4 | Target robot mount | OpenArm via YUBI flange + attachment | decided |
| D5 | Finger type | Parallel jaw, HandUMI tips | decided |

## Functional requirements (draft)

- Handheld, one-hand operation with a trigger to open/close the fingers.
- Wrist-mounted camera with fingertips visible in frame.
- Measure finger width (or opening) for each frame.
- The same finger geometry must also mount on the robot so demos transfer.

## Targets (to fill in)

| Parameter | Target |
|---|---|
| Max stroke (finger opening) | TBD mm |
| Mass (handheld) | TBD g |
| Grip force | TBD N |
| Width sensing resolution | TBD mm |
| Camera FOV | TBD ° |
