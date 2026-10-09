"""Intel RealSense D405 camera mount for HandUMI (drop-in replacement for camera_mount).

Keeps HandUMI's camera_mount hinge exactly: the two Ø8 knuckles and M3 pivot are cut
straight from hardware/STEP/right_handumi/camera_mount.step. Only the plate is replaced.

D405 rear interface, from the Intel D400 datasheet 337029-017, Figure 10-14:
2x M3x0.5 on the back face, 20.00 mm apart, centred, max thread engagement 4.0 mm.
Body 42 x 42 x 23 mm, 58 g. The USB-C port is on a side face, so the locating lips are only
on the top and bottom edges.

Frame (same as HandUMI camera_mount): hinge axis along X at y=-28.25, z=1.5; the camera
looks along +Z; the stereo baseline runs along X (parallel to the hinge / jaw travel).

    python d405_camera_mount.py      # -> ../hardware/{STEP,STL}/d405/d405_camera_mount.*
"""
from pathlib import Path

from build123d import (Box, Cylinder, Pos, export_step, export_stl, import_step)

ROOT = Path(__file__).resolve().parents[1]
HANDUMI_MOUNT = ROOT / "hardware/STEP/right_handumi/camera_mount.step"   # left == right

PLATE_EDGE_Y = -21.25          # where HandUMI's plate starts; everything below is the hinge
D405_W = 42.0                  # width and height of the body
D405_M3_PITCH = 20.0
PLATE_T = 4.0                  # z = 0 .. 4 (HandUMI plate is 3)
PLATE_MARGIN = 2.0             # plate overhang around the body
LIP_T, LIP_H, LIP_CLR = 1.6, 4.0, 0.2
M3_CLR, CBORE_D, CBORE_DEPTH = 3.4, 6.5, 1.5   # M3x6 -> 3.5 mm engagement (max 4.0)


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def build():
    original = import_step(str(HANDUMI_MOUNT))
    hinge = original & box(-50, 50, -60, PLATE_EDGE_Y + 0.5, -10, 10)

    h = D405_W / 2 + PLATE_MARGIN
    plate = box(-h, h, PLATE_EDGE_Y, h, 0, PLATE_T)
    plate += box(-h, h, -h, PLATE_EDGE_Y + 0.01, 0, PLATE_T) - box(-9, 9, -60, PLATE_EDGE_Y, -1, 10)

    inner = D405_W / 2 + LIP_CLR
    for s in (-1, 1):   # top / bottom lips; sides left open for the USB-C cable
        y0, y1 = sorted((s * inner, s * (inner + LIP_T)))
        plate += box(-inner, inner, y0, y1, PLATE_T - 0.01, PLATE_T + LIP_H)

    for x in (-D405_M3_PITCH / 2, D405_M3_PITCH / 2):
        plate -= Pos(x, 0, PLATE_T / 2) * Cylinder(M3_CLR / 2, PLATE_T + 2)
        plate -= Pos(x, 0, CBORE_DEPTH / 2 - 0.01) * Cylinder(CBORE_D / 2, CBORE_DEPTH)
    plate -= box(-6, 6, -12, 12, -1, PLATE_T + 1) - box(-2, 2, -13, 13, -2, PLATE_T + 2)  # weight relief

    part = hinge + plate
    part.label = "d405_camera_mount"
    return part, original


def main():
    part, original = build()
    hinge_box = box(-50, 50, -60, PLATE_EDGE_Y - 0.5, -10, 10)
    a, b = original & hinge_box, part & hinge_box
    diff = (a - b).volume + (b - a).volume
    bb = part.bounding_box()
    print(f"valid={part.is_valid} solids={len(part.solids())} vol={part.volume:.0f} mm3 "
          f"size=({bb.size.X:.1f},{bb.size.Y:.1f},{bb.size.Z:.1f}) hinge_diff_vs_handumi={diff:.3f} mm3")
    for sub, fn in (("STEP", export_step), ("STL", export_stl)):
        out = ROOT / "hardware" / sub / "d405"
        out.mkdir(parents=True, exist_ok=True)
        fn(part, str(out / f"d405_camera_mount.{sub.lower()}"))
    return part


if __name__ == "__main__":
    main()
