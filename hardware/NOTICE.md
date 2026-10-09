# Notice

`hardware/` and `bom/` are copied from [murobotics-ai/handumi-hw](https://github.com/murobotics-ai/handumi-hw)
at commit `fc7462a`, licensed under Apache-2.0 (see `hardware/LICENSE`).

Changes in this repository:

- **Added** `STEP/d405/d405_camera_mount.step` and `STL/d405/d405_camera_mount.stl`: a mount for the Intel RealSense D405 that
  replaces `camera_mount` (left and right). The hinge knuckles are cut unchanged from HandUMI's `camera_mount.step`; the
  camera plate is new. Source: `d405_mount/d405_camera_mount.py`.
- **Added** `STEP/d405/wrist_d405_mount_handumi.step` and `STL/d405/wrist_d405_mount_handumi.stl`: the supplied D405 wrist
  mount with its tab replaced by HandUMI's camera hinge (cut unchanged from `camera_mount.step`). Source:
  `d405_mount/wrist_mount_to_handumi.py`.
- **Added** `STEP/redesign/` and `STL/redesign/`: `main_support`, `end_cover` and `controller_lid`, restyled versions of
  `fisheye_camera_main_support`, `main_support_cover_plate` and `servo_controller_cover`. Mating features are unchanged.
  Source: `redesign/restyle.py`.

Every other file in `hardware/` and `bom/` is unmodified.
