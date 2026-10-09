# Notice

`hardware/` and `bom/` are derived from [murobotics-ai/handumi-hw](https://github.com/murobotics-ai/handumi-hw)
at commit `fc7462a`, licensed under Apache-2.0 (see `hardware/LICENSE`). `hardware/reference/STS3215_03a.step` is from
[TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) (Apache-2.0).

Changes in this repository:

- Renamed the part folders `right_handumi/` → `right/` and `left_handumi/` → `left/` (STEP and STL); the files inside are unmodified.
- Added `main_support`: restyled `fisheye_camera_main_support` (blends, lightening slots, faceted ends, engraved name),
  with a new braced camera post and Ø12 / M4 hinge and two M3 holes for the electronics box. Source: `redesign/restyle.py`.
- Added `end_cover`: `main_support_cover_plate` with matching chamfers.
- Added `electronics_box` and `electronics_lid`: a new enclosure for a Raspberry Pi Pico 2, an IMU and a USB 3 hub,
  replacing `servo_controller_support` / `servo_controller_cover`. Source: `redesign/electronics_box.py`.
- Replaced the finger links (`*_thumb_link`, `*_index_middle_finger_link`) with versions that have a universal
  tip flange (lofted neck, 20 × 30 mm flange, M2/M3/M4 patterns). Source: `redesign/finger_link.py`.
- Added `d405_wrist_mount`: a D405 cup with Ø12 / M4 hinge lugs, replacing `camera_mount`. Source: `d405_mount/d405_wrist_mount.py`.

The parts these edits replace were removed from `right/` and `left/`; the originals the scripts start from are kept in
`redesign/source/`. Every other file in `hardware/` and `bom/` is unmodified apart from the folder rename (and the
matching paths in `hardware/README.md`).
