"""OpenArm unit: STS3215 cradle (same rear-module interface as the collector pod) + horn coupler.

The cradle's back face carries the YUBI_ATTACHMENT gripper-side pattern, so the stock
yubi-hw OPENARM_FLANGE + YUBI_ATTACHMENT bolt on unchanged.
"""
from math import cos, radians, sin

from build123d import Part

from .jaw_module import BOSS_Y0, box, cyl_y, cyl_z
from .params import *

SHAFT_END = BOSS_Y0 - 8.0             # pinion shaft protrudes 8 mm behind the boss
COUPLER = (SHAFT_END - 4.0, BOSS_Y0 - 1.0)   # y-range of the coupler
HORN_FACE = COUPLER[0]
HORN_T = 3.0                          # horn disc thickness -> VERIFY
SERVO_TOP = HORN_FACE - HORN_T - 4.6  # 4.6 = spline boss height above the case (measured)
SERVO_BACK = SERVO_TOP - STS_BODY[2]
CR_X0, CR_X1 = -46.0, 38.0
CR_Z = 22.0
CR_Y0 = SERVO_BACK - 8.0              # back plate (OpenArm side)


def coupler() -> Part:
    c = cyl_y(10.0, COUPLER[0] + 3, COUPLER[1], 0, 0) + cyl_y(HORN_PCD + 6, COUPLER[0], COUPLER[0] + 3, 0, 0)
    flat = box(SHAFT_D / 2 - 0.5, SHAFT_D, -10, 10, -10, 10)
    c -= cyl_y(SHAFT_D + 0.1, SHAFT_END - 0.5, COUPLER[1] + 1, 0, 0) - flat
    for i in range(HORN_N):
        a = radians(45 + i * 360 / HORN_N)
        c -= cyl_y(HORN_HOLE, COUPLER[0] - 1, COUPLER[0] + 4, HORN_PCD / 2 * cos(a), HORN_PCD / 2 * sin(a))
    return c


def servo_envelope() -> Part:
    """STS3215 body, output axis on the pinion axis (+Y), body offset along -X."""
    bx = -STS_SHAFT_OFFSET
    return box(bx - STS_BODY[0] / 2, bx + STS_BODY[0] / 2, SERVO_BACK, SERVO_TOP,
               -STS_BODY[1] / 2, STS_BODY[1] / 2) + cyl_y(9.0, SERVO_TOP - 0.01, HORN_FACE - HORN_T, 0, 0)


LID_POSTS = [(x, y) for x in (CR_X0 + 4, CR_X1 - 4) for y in (CR_Y0 + 12, FRAME_Y0 - 8)]


def cradle() -> Part:
    bx = -STS_SHAFT_OFFSET
    c = box(CR_X0, CR_X1, CR_Y0, FRAME_Y0, -CR_Z, CR_Z)
    c -= box(CR_X0 + 3, CR_X1 - 3, SERVO_BACK, FRAME_Y0 - 4, -CR_Z + 3, CR_Z + 1)   # open-top cavity
    c -= cyl_y(18.0, BOSS_Y0 - 1, FRAME_Y0 + 1, 0, 0)                                 # bearing boss
    # servo seat: a saddle under the body + the back wall locate it; the lid clamps it down
    c += box(bx - STS_BODY[0] / 2 - 3, bx + STS_BODY[0] / 2 + 3, SERVO_BACK, SERVO_TOP,
             -CR_Z + 3 - 0.01, -STS_BODY[1] / 2)
    c -= box(bx - STS_BODY[0] / 2 - CLR, bx + STS_BODY[0] / 2 + CLR, SERVO_BACK - CLR, SERVO_TOP,
             -STS_BODY[1] / 2 - CLR, CR_Z + 1)
    for x, y in LID_POSTS:
        c += box(x - 4, x + 4, y - 4, y + 4, -CR_Z + 1, CR_Z) - cyl_z(M3_INSERT_D, CR_Z - 6, CR_Z + 1, x, y)
    for x, z in REAR_MOUNTS:
        c -= cyl_y(M3_CLR, FRAME_Y0 - 5, FRAME_Y0 + 1, x, z)
    c -= box(CR_X1 - 4, CR_X1 + 1, SERVO_BACK + 4, SERVO_BACK + 14, -6, 6)             # servo cable
    # OpenArm side: YUBI_ATTACHMENT pattern; attachment (x, y) -> cradle (z, x)
    for ax, ay in YUBI_M3:
        c -= cyl_y(M3_INSERT_D, CR_Y0 - 1, CR_Y0 + 6, ay, ax)
    for ax, ay in YUBI_PINS:
        c -= cyl_y(3.0 + PRESS, CR_Y0 - 1, CR_Y0 + 4, ay, ax)
    return c


def cradle_lid() -> Part:
    bx = -STS_SHAFT_OFFSET
    lid = box(CR_X0, CR_X1, CR_Y0, FRAME_Y0 - 4, CR_Z, CR_Z + 3)
    lid += box(bx - STS_BODY[0] / 2 + 4, bx + STS_BODY[0] / 2 - 2, SERVO_BACK + 4, SERVO_TOP - 4,
               STS_BODY[1] / 2 + CLR, CR_Z + 0.01)                                     # clamps the servo
    for x, y in LID_POSTS:
        lid -= cyl_z(M3_CLR, CR_Z - 1, CR_Z + 4, x, y)
    return lid
