"""Shared parallel-jaw module: frame, carriages (one part, used twice), pinion.

The two carriages are the same part; the second is rotated 180° about Y, which puts its
rack on the opposite side of the pinion so the jaws move symmetrically.
"""
from math import cos, radians, tan

from bd_warehouse.gear import SpurGear
from build123d import (Axis, Box, Cylinder, Part, Polyline, Pos, RegularPolygon, Rot, chamfer,
                       extrude, make_face)

from .params import *

def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl_x(d, x0, x1, y, z):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, x1 - x0)


def cyl_y(d, y0, y1, x, z):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(d / 2, y1 - y0)


def cyl_z(d, z0, z1, x, y):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(d / 2, z1 - z0)


# ---------------------------------------------------------------- rack
HA, HF = GEAR_M, 1.25 * GEAR_M
PITCH = 3.141592653589793 * GEAR_M
T20 = tan(radians(20))


def rack(length: float) -> Part:
    """Rack in the XZ plane: teeth point -Z, pitch line at z=0, runs x=0..length, extruded in Y."""
    pts = [(0, HF + RACK_BODY), (length, HF + RACK_BODY), (length, HF)]
    c = length - PITCH / 2
    while c - PITCH / 2 >= -1e-6:
        q = PITCH / 4 - GEAR_BACKLASH / 2      # half tooth thickness at the pitch line
        pts += [(c + q + HF * T20, HF), (c + q - HA * T20, -HA),
                (c - q + HA * T20, -HA), (c - q - HF * T20, HF)]
        c -= PITCH
    pts += [(0, HF)]
    face = make_face(Polyline(*[(x, 0, z) for x, z in pts], close=True))
    return Pos(0, GEAR_FACE / 2, 0) * extrude(face, GEAR_FACE, dir=(0, -1, 0))


# ---------------------------------------------------------------- carriage
def carriage() -> Part:
    """Carriage centred on x=0 with its rack above the pinion (left jaw pose, x<0)."""
    hw = CAR_W / 2
    body = box(-hw, hw, CAR_Y0, CAR_Y1, -CAR_Z, CAR_Z)
    body = chamfer(body.edges().filter_by(Axis.Y), 2.0)

    # rack: pitch line at z=+PITCH_R, teeth down, extends toward +x (across the pinion)
    rk = Pos(-hw, GEAR_Y, PITCH_R) * rack(RACK_LEN)
    z_back0 = PITCH_R + HF
    neck = box(-hw, hw, GEAR_Y - GEAR_FACE / 2, CAR_Y0 + 0.01, z_back0, z_back0 + RACK_BODY)
    body = body + rk + neck

    for z in (ROD_Z, -ROD_Z):   # LM6UU pocket from -x, retaining lip at +x
        body -= cyl_x(LMU_OD + PRESS, -hw - 1, -hw + LMU_L, 0, z)
        body -= cyl_x(ROD_D + 1.5, -hw, hw + 1, 0, z)

    for sx in (-1, 1):          # HandUMI tip interface + M2 nut traps on the back face
        for sz in (-1, 1):
            x, z = sx * TIP_DX / 2, sz * TIP_DZ / 2
            body -= cyl_y(TIP_HOLE, CAR_Y0 - 1, CAR_Y1 + 1, x, z)
            nut = RegularPolygon(M2_NUT_AF / 2 / cos(radians(30)) + 0.15, 6)
            body -= Pos(x, CAR_Y0 + 2.0, z) * Rot(90, 0, 0) * extrude(nut, 2.5)

    for z_face in (-CAR_Z, CAR_Z):   # finger-ring mounts, both faces (carriage is used rotated)
        for x in (-6, 6):
            z0, z1 = (z_face - 0.1, z_face + 6) if z_face < 0 else (z_face - 6, z_face + 0.1)
            body -= cyl_z(M3_INSERT_D, z0, z1, x, 1.0)
    return body


def carriage_pose(xc: float, left: bool) -> Part:
    c = carriage()
    return Pos(xc, 0, 0) * c if left else Pos(xc, 0, 0) * Rot(0, 180, 0) * c


# ---------------------------------------------------------------- pinion
def pinion() -> Part:
    g = SpurGear(module=GEAR_M, tooth_count=PINION_Z, pressure_angle=20, thickness=GEAR_FACE)
    g = Pos(0, 0, -GEAR_FACE / 2) * g if abs(g.bounding_box().min.Z) < 1e-6 else g
    hub = cyl_z(8.0, GEAR_FACE / 2, GEAR_FACE / 2 + 2.0, 0, 0)   # spacer against the bearing race
    p = g + hub
    flat = Pos(4.5 - SHAFT_D / 2 + SHAFT_D / 2, 0, 0) * Box(SHAFT_D, 10, 31)   # flat 4.5 from far side
    p -= Cylinder(SHAFT_D / 2 + 0.05, 30) - flat                   # Ø5 D-shaft bore
    # gear axis +z -> world -y (hub faces the back plate)
    return Pos(0, GEAR_Y, 0) * Rot(90, 0, 0) * p


# ---------------------------------------------------------------- frame
BOSS_D, BOSS_Y0 = 17.0, FRAME_Y0 - 2 * BRG_W - 2


def frame() -> Part:
    xo = FRAME_X + END_T
    zt = FRAME_Z + TOP_T
    f = box(FRAME_X, xo, FRAME_Y0, FRAME_Y1, -FRAME_Z, zt)                # +x end block
    f += box(-xo, -FRAME_X, FRAME_Y0, FRAME_Y1, -FRAME_Z, zt)             # -x end block
    f += box(-xo, xo, FRAME_Y0, FRAME_Y0 + WALL, -FRAME_Z, zt)             # back plate
    f += box(-xo, xo, FRAME_Y0, FRAME_Y1, FRAME_Z, zt)                     # top plate / camera dock
    f += cyl_y(BOSS_D, BOSS_Y0, FRAME_Y0 + 0.01, 0, 0)                     # bearing boss

    gz0 = PITCH_R + HF + RACK_BODY + CLR + 0.2                              # rack back-up guides
    for s in (1, -1):
        z0, z1 = sorted((s * gz0, s * (gz0 + 3)))
        f += box(-FRAME_X, FRAME_X, FRAME_Y0 + WALL - 0.01, GEAR_Y + GEAR_FACE / 2, z0, z1)

    # styling: faceted outer edges of the end blocks
    f = chamfer(f.edges().filter_by(Axis.Y).group_by(Axis.X)[0] + f.edges().filter_by(Axis.Y).group_by(Axis.X)[-1], 5.0)

    for z in (ROD_Z, -ROD_Z):                                                # rods, press fit
        f -= cyl_x(ROD_D + PRESS, -xo - 1, xo + 1, 0, z)
    f -= cyl_y(BRG_OD + PRESS, BOSS_Y0 - 1, BOSS_Y0 + 2 * BRG_W, 0, 0)       # 2x 685ZZ from the rear
    f -= cyl_y(SHAFT_D + 2, BOSS_Y0, FRAME_Y0 + WALL + 1, 0, 0)

    for sx in (-1, 1):                                                       # camera dock inserts
        for sy in (-1, 1):
            f -= cyl_z(M3_INSERT_D, zt - 6, zt + 1, sx * DOCK_PITCH / 2, DOCK_Y + sy * DOCK_PITCH / 2)
    for sx in (-1, 1):                                                       # rear module mounts
        for sz in (-1, 1):
            f -= cyl_y(M3_INSERT_D, FRAME_Y0 - 1, FRAME_Y0 + 6, sx * 30, sz * 16)
    return f
