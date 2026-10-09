# The UMI no one wants

<p align="center">
  <img src="docs/img/hero.png" alt="The UMI no one wants: hand-worn gripper with an Intel RealSense D405 wrist camera" width="900">
</p>

A hand-worn gripper for collecting bimanual manipulation data without a robot in the loop. It has an
**Intel RealSense D405** depth camera on the wrist, an on-board **IMU and Raspberry Pi Pico 2**, and a single USB cable to your laptop.

- **Depth wrist camera:** the D405 sits in a cup that tilts on a Ø12 / M4 hinge and looks down at the fingertips. It's set at 65° below horizontal, 9–10 cm from the tips (the D405's minimum range is 7 cm). Cable windows are on the top and both sides.
- **Braced camera post:** a tapered post with a 60 mm keel, flaring smoothly into the frame, carries the hinge.
- **Universal tip flange:** each finger link has a 20 × 30 mm flange with M2 (8 × 12), M3 (12 × 24 + centre pair) and M4 (12 mm pair) hole patterns, so you can bolt on different gripper tips.
- **One cable:** a closed electronics box holds a USB 3 hub, the Pico 2 and the IMU. The camera and the Pico both connect to the hub, and one USB-C cable goes to the laptop. See [docs/electronics.md](docs/electronics.md).
- **Clean frame:** the T-plate is built from one continuous outline with blended corners, uniform edge rounding, lightening slots and faceted ends, plus a matching end cover.
- **Checked in a full assembly:** the gripper is clash-checked closed, half-open and open, across camera tilts from 40° to 80°.

## Parts

<p align="center">
  <img src="docs/img/parts.png" alt="Main support, D405 wrist mount, electronics box and lid, end cover" width="900">
</p>

Print everything in `hardware/STL/right/` for a right hand or `hardware/STL/left/` for a left hand, plus a pair of
tips from `hardware/STL/gripper_tips/`. STEP files for every part are in `hardware/STEP/`.

| Part | File |
|---|---|
| Main support (T-plate with camera post) | `main_support.stl` |
| End cover | `end_cover.stl` |
| D405 wrist mount | `d405_wrist_mount.stl` |
| Electronics box + lid | `electronics_box.stl`, `electronics_lid.stl` |
| Thumb and index/middle finger links (universal tip flange) | `*_thumb_link.stl`, `*_index_middle_finger_link.stl` |
| Crank, connecting links, hand support base, controller support | `crank_mechanism_plate.stl`, `connecting_link_1/2.stl`, `hand_support_base.stl`, `*_controller_support.stl` |

### Tip flange hole patterns

| Screws | Pattern | Fixing |
|---|---|---|
| 4× M2 | 8 × 12 mm | Self-tapping (fits every tip in `gripper_tips/`) |
| 6× M3 | 12 × 24 mm rectangle + centre pair at ±12 mm | M3 heat-set inserts (Ø4.0 × 5) |
| 2× M4 | 12 mm apart, centred | M4 heat-set inserts (Ø5.6 × 7) |

## Hardware

Base mechanics, rods, bearings, servo and fasteners are listed in [bom/README.md](bom/README.md), with these changes:

- **Camera:** Intel RealSense D405 instead of the IMX335 camera. Fix it with 2× M3×5 screws into its rear holes (2× M3×0.5, 20 mm apart, 4 mm max thread depth).
- **Camera hinge:** 1× M4×30 bolt with a nyloc nut.
- **Electronics:** Raspberry Pi Pico 2, a BNO085 IMU, a small USB 3 hub and short cables. This replaces the servo controller board and its power supply. Full list and wiring: [docs/electronics.md](docs/electronics.md).

## Files

| Path | What |
|---|---|
| `hardware/STL`, `hardware/STEP` | Printable parts and CAD |
| `redesign/` | Sources: `restyle.py` (main support, end cover, finger links, box), `electronics_box.py`, `finger_link.py`, `hinge.py`, `logo.py`; the starting parts are in `redesign/source/` |
| `d405_mount/` | Source for the D405 wrist mount and its input mesh |
| `tools/assembly.py` | Builds the full assembly, clash-checks it (`--check`) and renders it |
| `tools/render_docs.py` | Renders the images in this README |
| `tools/fea.py` | Strength analysis of every printed part (results in `docs/fea_results.csv`, stress maps in `docs/img/fea/`) |
| `docs/electronics.md` | Electronics, wiring and power |
| `bom/` | Bill of materials for the base mechanics |

To rebuild everything (Python 3.12 with `build123d`, `trimesh`, `manifold3d`, `pyvista`):

```bash
python redesign/restyle.py
python d405_mount/d405_wrist_mount.py d405_mount/input/wrist_camera_mount.stl
cd tools && python assembly.py --opening 0 --check && python render_docs.py
```

## Strength

Every printed part is analysed in `tools/fea.py`: linear-elastic FEA in PLA (E = 3 GPa), with quadratic tetrahedra
meshed from the STEP files and checked against hand calculations. Load cases are 15 g knocks on the camera, a 30 N
grip with the tip's 70 mm lever, a 40 N finger press, and hand and VR-controller loads. Safety factors are against
30 MPa (along layers) and 15 MPa (across layers). Results so far are in [`docs/fea_results.csv`](docs/fea_results.csv);
**the analysis is still running**, and the table will be completed in the next update.

## License

Third-party sources, licenses and the list of modifications are in [`hardware/NOTICE.md`](hardware/NOTICE.md).
