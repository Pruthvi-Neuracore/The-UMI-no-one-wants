# Notice

`hardware/` and `bom/` are copied from [murobotics-ai/handumi-hw](https://github.com/murobotics-ai/handumi-hw)
at commit `fc7462a`, licensed under Apache-2.0 (see `hardware/LICENSE`).

Changes in this repository:

- **Added** `STEP/d405/d405_camera_mount.step` and `STL/d405/d405_camera_mount.stl`: a mount for the Intel RealSense D405 that
  replaces `camera_mount` (left and right). The hinge knuckles are cut unchanged from HandUMI's `camera_mount.step`; the
  camera plate is new. Source: `d405_mount/d405_camera_mount.py`.

Every other file in `hardware/` and `bom/` is unmodified.
