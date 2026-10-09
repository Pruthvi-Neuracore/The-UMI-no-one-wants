# Requirements

## Open decisions

| # | Decision | Options | Status |
|---|---|---|---|
| D1 | CAD authoring | Code CAD (build123d / CadQuery), Onshape, other | open |
| D2 | Actuation | Passive trigger + width sensor; servo driven by trigger input; other | open |
| D3 | Camera | GoPro, ELP fisheye USB, other | open |
| D4 | Target robot mount | OpenArm flange, other | open |
| D5 | Finger type | Fin-ray soft fingers, rigid parallel jaw + pads | open |

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
