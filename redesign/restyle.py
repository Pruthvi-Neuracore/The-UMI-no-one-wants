"""Clean restyle of HandUMI parts. Every mating feature is kept (holes, bores, pockets, rod walls,
servo boss, hinge tab, arm end); only non-functional geometry changes.

  fisheye_camera_main_support -> main_support (T-plate)
      * large blended fillets where the arm meets the bar (material added in the plate plane, z 0..8)
      * racetrack lightening slots through the two open bar spans
      * rounded arm-end corners
      * smooth blends where the bar meets the round servo boss
      * 45° chamfers on the top corners of the rod end wall and on the outer corners of both bar ends
      * engraved name on the outside of the end wall
  main_support_cover_plate -> end_cover: matching 45° top and corner chamfers
  servo_controller_cover -> controller_lid: vent slots

    python restyle.py      # -> ../hardware/{STEP,STL}/redesign/*
"""
from pathlib import Path

from build123d import (Align, Box, Circle, Cylinder, Polygon, Pos, Rot, SlotCenterToCenter, Text,
                       export_step, export_stl, extrude, import_step)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hardware/STEP/right_handumi"            # left and right versions of these parts are identical
OUT = ROOT / "hardware"

PLATE_Z = (0.0, 8.0)          # T-plate thickness in its own frame
BLEND_R = 18.0                # arm-to-bar blend radius
ARM_END_R = 8.0
WALL_CHAMFER = 6.0
END_CHAMFER = 4.0
NAME = "THE UMI NO ONE WANTS"


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def plate_prism(face2d, z0=PLATE_Z[0], z1=PLATE_Z[1]):
    return Pos(0, 0, z0) * extrude(face2d, z1 - z0, dir=(0, 0, 1))


def corner_fill(cx, cy, sx, sy, r):
    """Concave blend filling the inside corner at (cx, cy); (sx, sy) point into the empty quadrant."""
    square = Polygon((cx, cy), (cx + sx * r, cy), (cx + sx * r, cy + sy * r), (cx, cy + sy * r), align=None)
    return plate_prism(square) - plate_prism(Pos(cx + sx * r, cy + sy * r) * Circle(r))


def corner_round(cx, cy, sx, sy, r):
    """Material to remove to round the outside corner at (cx, cy); (sx, sy) point outward."""
    square = Polygon((cx, cy), (cx - sx * r, cy), (cx - sx * r, cy - sy * r), (cx, cy - sy * r), align=None)
    return Pos(0, 0, -1) * extrude(square, 10, dir=(0, 0, 1)) - Pos(cx - sx * r, cy - sy * r, -1) * Cylinder(r, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))


def wall_chamfers(x0, x1, y0, y1, ztop, c):
    """Prisms removing 45° chamfers on the two top corners of a wall spanning x0..x1 (along Y y0..y1)."""
    cut = None
    for xc, s in ((x0, 1), (x1, -1)):
        tri = Polygon((xc, ztop), (xc + s * c, ztop), (xc, ztop - c), align=None)       # in XZ via rotation below
        prism = Pos(0, y1 + 1, 0) * Rot(90, 0, 0) * extrude(tri, y1 - y0 + 2)
        cut = prism if cut is None else cut + prism
    return cut


def vertical_chamfer(x, y, sx, sy, c, z0, z1):
    """Prism removing a 45° chamfer of size c on the vertical edge at (x, y); (sx, sy) point outward."""
    tri = Polygon((x, y), (x - sx * c, y), (x, y - sy * c), align=None)
    return Pos(0, 0, z0) * extrude(tri, z1 - z0, dir=(0, 0, 1))


def boss_blend(sy, r=10.0):
    """Fillet between the bar's outer edge (x = -36) and the Ø45 servo boss (centre (-18, 72.5))."""
    cx, cy, R, xe = -18.0, 72.5, 22.5, -36.0
    d = ((R + r) ** 2 - (cx - (xe - r)) ** 2) ** 0.5
    fc = (xe - r, cy - sy * d)                                          # fillet circle centre
    a = (xe, fc[1])                                                     # tangent point on the edge
    i = (xe, cy - sy * (R**2 - (cx - xe) ** 2) ** 0.5)                  # edge / boss intersection
    k = R / (R + r)
    b = (cx + (fc[0] - cx) * k, cy + (fc[1] - cy) * k)                  # tangent point on the boss
    return plate_prism(Polygon(a, i, b, align=None)) - plate_prism(Pos(*fc) * Circle(r))


def main_support():
    s = import_step(str(SRC / "fisheye_camera_main_support.step"))
    s += corner_fill(0.0, 54.5, 1, -1, BLEND_R)
    s += corner_fill(0.0, 90.5, 1, 1, BLEND_R)
    s += boss_blend(1) + boss_blend(-1)
    for x, sx in ((-36.0, -1), (0.0, 1)):                              # faceted bar ends
        s -= vertical_chamfer(x, 0.0, sx, -1, END_CHAMFER, -1, 35)
        s -= vertical_chamfer(x, 140.0, sx, 1, END_CHAMFER, -1, 9)
    for cy, length in ((32.0, 30.0), (110.0, 24.0)):                # racetrack slots in the open bar spans
        s -= Pos(-18.0, cy, -1) * extrude(Rot(0, 0, 90) * SlotCenterToCenter(length - 14.0, 14.0), 10)
    s -= corner_round(74.0, 54.5, 1, -1, ARM_END_R)
    s -= corner_round(74.0, 90.5, 1, 1, ARM_END_R)
    s -= wall_chamfers(-36.0, 0.0, 0.0, 10.7, 34.0, WALL_CHAMFER)
    txt = Text(NAME, font_size=3.2)
    s -= Pos(-18.0, 0.6, 17.0) * Rot(90, 0, 180) * extrude(txt, 0.6)  # engraved on the outer (-Y) face
    return s


def end_cover():
    s = import_step(str(SRC / "main_support_cover_plate.step"))
    s -= wall_chamfers(-36.0, 0.0, -10.0, 0.0, 34.0, WALL_CHAMFER)
    for x, sx in ((-36.0, -1), (0.0, 1)):                              # matches the bar's faceted ends
        s -= vertical_chamfer(x, 0.0, sx, 1, END_CHAMFER, -1, 35)
    return s


def controller_lid():
    s = import_step(str(SRC / "servo_controller_cover.step"))
    for i in range(5):                                  # clear of the existing cable window (x 2..16, y 9.5..17.5)
        x = -12.0 + i * 6.0
        s -= Pos(x, -4.0, -1) * extrude(Rot(0, 0, 90) * SlotCenterToCenter(17.0, 3.0), 10)
    return s


PARTS = {"main_support": main_support, "end_cover": end_cover, "controller_lid": controller_lid}


def main():
    for sub in ("STEP", "STL"):
        (OUT / sub / "redesign").mkdir(parents=True, exist_ok=True)
    for name, fn in PARTS.items():
        p = fn()
        print(f"{name:16s} valid={p.is_valid} solids={len(p.solids())} vol={p.volume:.0f}")
        export_step(p, str(OUT / "STEP/redesign" / f"{name}.step"))
        export_stl(p, str(OUT / "STL/redesign" / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.15)


if __name__ == "__main__":
    main()
