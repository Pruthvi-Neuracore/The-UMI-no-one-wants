# The UMI no one wants

[HandUMI](https://github.com/murobotics-ai/handumi-hw) with one change: the wrist camera is an
**Intel RealSense D405** instead of the IMX335 USB camera.

![D405 mount](docs/img/d405_camera_mount.png)

## Build

1. Print everything in `hardware/STL/left_handumi/` and/or `hardware/STL/right_handumi/`, **except `camera_mount.stl`**.
2. Print `hardware/STL/d405/d405_camera_mount.stl` instead (same part for left and right; one per HandUMI).
3. Print the gripper tips for your robot from `hardware/STL/gripper_tips/`.
4. Follow the HandUMI [BOM](bom/README.md), with the camera changes below.

## D405 mount

- **Hinge:** identical to HandUMI's `camera_mount`: two Ø8 knuckles on the same M3 pivot, cut straight from their STEP. It fits the
  existing `fisheye_camera_main_support` with no other changes.
- **Camera:** two **M3×6** screws from the back into the D405's rear holes. Per Intel's datasheet these are 2× M3×0.5, 20 mm apart,
  with 4.0 mm max engagement; M3×6 through the counterbored 4 mm plate gives about 3.5 mm. Top and bottom lips locate the body. The sides are
  open so the USB-C cable can leave either way.
- **Orientation:** the stereo baseline is parallel to the hinge axis, the same as the IMX335 board's horizontal.

| Item | HandUMI | This repo |
|---|---|---|
| Camera | SVPRO IMX335 USB (×1 per unit) | Intel RealSense D405 (×1 per unit) |
| Camera screws | M2 board screws | 2× M3×6 per unit |
| Cable | USB-C (camera) | USB-C to USB-A/C, **USB 3** recommended for depth |

## Check before printing a batch

- **Tilt range:** the D405 is 23 mm deep and weighs 58 g, versus a bare board. Print one mount, assemble it on the support, and check the
  camera clears the support across the tilt you want.
- **Pivot:** with a heavier camera, use a nyloc nut on the M3 pivot so the angle holds.

## Files

| Path | What |
|---|---|
| `hardware/` | HandUMI hardware (STEP + STL), unmodified, plus `d405/` |
| `hardware/STL/d405/d405_camera_mount_with_d405.glb` | Preview of the mount with a D405-sized body |
| `d405_mount/d405_camera_mount.py` | Source for the mount (build123d); run it to regenerate STEP/STL |
| `bom/` | HandUMI BOM, unmodified |
| `tools/inspect_step.py` | Prints holes and bosses of a STEP file |

HandUMI is © its authors, Apache-2.0; see [`hardware/NOTICE.md`](hardware/NOTICE.md).
The earlier rack-and-pinion design is kept on the `v0.1-rack-pinion` branch.
