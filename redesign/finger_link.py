"""Finger links with a universal tip flange.

The original links carry tips on a 12 x 16 x 3 mm plate on a 12 x 6 mm neck. Here the plate and neck are
replaced by a lofted neck flaring into a 20 x 30 x 5 mm flange with filleted edges. The front face stays at
y = 0, so tips sit exactly where they did. Hole patterns on the flange (link frame: x across, z along the finger,
holes along Y):

    M2   4x  8 x 12 mm   existing tip library (self-tapping, as before)
    M3   6x  12 x 24 mm rectangle + centre pair at z = ±12 (heat-set inserts, Ø4.0 x 5)
    M4   2x  12 mm apart at z = 0 (heat-set inserts, Ø5.6 x 7); same spacing as Robotiq's M4 accessory holes

Flange width is set so the two flanges keep a 3.6 mm gap at full close.
"""
from build123d import Axis, Box, Cylinder, Face, Polyline, Pos, Rot, Wire, fillet, import_step, loft

FLANGE = (20.0, 5.0, 30.0)          # x, y (thickness), z
NECK_ROOT = (-6.0, 6.0, -9.0, 7.0)  # x0, x1, z0, z1 on the link body at y = NECK_Y
NECK_Y = -12.4
M2 = [(sx * 4.0, sz * 6.0) for sx in (-1, 1) for sz in (-1, 1)]
M3 = [(x, sz * 12.0) for x in (-6.0, 0.0, 6.0) for sz in (-1, 1)]
M4 = [(-6.0, 0.0), (6.0, 0.0)]


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def rect_y(y, x0, x1, z0, z1):
    return Face(Wire(Polyline((x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1), close=True).edges()))


def hole_y(x, z, d, depth):
    return Pos(x, -depth / 2 + 0.01, z) * Rot(90, 0, 0) * Cylinder(d / 2, depth + 0.02)


def finger_link(src):
    s = import_step(str(src))
    s -= box(-6.6, 6.6, NECK_Y + 0.2, 0.6, -8.6, 8.6)                   # old 12 x 16 plate and 12 x 6 neck
    fx, fy, fz = FLANGE
    flange = box(-fx / 2, fx / 2, -fy, 0.0, -fz / 2, fz / 2)
    flange = fillet(flange.edges().filter_by(Axis.Y), 3.0)
    flange = fillet(flange.edges().group_by(Axis.Y)[-1], 1.0)          # soften the front edges
    x0, x1, z0, z1 = NECK_ROOT
    neck = loft([rect_y(NECK_Y - 1.0, x0, x1, z0, z1), rect_y(NECK_Y + 2.5, x0 - 0.5, x1 + 0.5, z0 - 1.5, z1 + 1.5),
                 rect_y(-fy + 0.01, -fx / 2 + 1, fx / 2 - 1, -fz / 2 + 3, fz / 2 - 3)], ruled=False)
    s = s + neck + flange
    for x, z in M2:
        s -= hole_y(x, z, 2.1, 6.0)
    for x, z in M3:
        s -= hole_y(x, z, 4.0, 5.0)
    for x, z in M4:
        s -= hole_y(x, z, 5.6, 7.0)
    return s
