# Notice

`hardware/` and `bom/` are copied from [murobotics-ai/handumi-hw](https://github.com/murobotics-ai/handumi-hw)
at commit `fc7462a`, licensed under Apache-2.0 (see `hardware/LICENSE`).

Changes in this repository:

- **Added** `STEP/d405/wrist_d405_mount_handumi.step` and `STL/d405/wrist_d405_mount_handumi.stl`: the supplied D405 wrist
  mount with its tab replaced by Ø12 / M4 hinge lugs that mate with the redesigned main support. Source:
  `d405_mount/wrist_mount_to_handumi.py`.
- **Added** `STEP/redesign/` and `STL/redesign/`: `main_support`, `end_cover` and `controller_lid`, restyled versions of
  `fisheye_camera_main_support`, `main_support_cover_plate` and `servo_controller_cover`. Mating features are unchanged, except the camera post on
  `main_support`, which is rebuilt as a stiffer Ø12 / M4 hinge (so it takes the new D405 wrist mount, not HandUMI's camera mount).
  Source: `redesign/restyle.py`.

Every other file in `hardware/` and `bom/` is unmodified.
