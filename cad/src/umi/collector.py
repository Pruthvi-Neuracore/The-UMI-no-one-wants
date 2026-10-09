"""Hand-worn collector parts: finger rings, electronics pod (AS5600 + Pico + IMU), lid, magnet cap."""
from build123d import Ellipse, Part, Pos, Rot, extrude

from .jaw_module import BOSS_Y0, box, cyl_x, cyl_y, cyl_z
from .params import *

TAB_T = 4.0


def finger_ring(oval: bool) -> Part:
    """Ring under a carriage. oval=True -> index+middle, else thumb. Finger axis = +Y.

    The rings are staggered in Y (thumb further back) so they pass each other when closed.
    """
    w_in, h_in = (INDEX_ID[1], INDEX_ID[0]) if oval else (THUMB_ID, THUMB_ID)
    zc = -CAR_Z - TAB_T - 2 - RING_T - h_in / 2
    yc = INDEX_RING_Y if oval else THUMB_RING_Y
    outer = Pos(0, yc + RING_W / 2, zc) * Rot(90, 0, 0) * extrude(Ellipse(w_in / 2 + RING_T, h_in / 2 + RING_T), RING_W)
    inner = Pos(0, yc + RING_W / 2 + 1, zc) * Rot(90, 0, 0) * extrude(Ellipse(w_in / 2, h_in / 2), RING_W + 2)
    tab = box(-CAR_W / 2, CAR_W / 2, CAR_Y0, CAR_Y1, -CAR_Z - TAB_T, -CAR_Z)
    neck = box(-12, 12, yc - RING_W / 2, yc + RING_W / 2, zc + h_in / 2, -CAR_Z - TAB_T + 0.01)
    r = tab + neck + outer - inner
    for x in (-6, 6):                         # M3 into carriage inserts; driver goes through the ring
        r -= cyl_z(M3_CLR, -CAR_Z - TAB_T - 1, -CAR_Z + 1, x, 1.0)
        r -= cyl_z(6.5, zc - h_in / 2 - RING_T - 1, -CAR_Z - TAB_T, x, 1.0)
    return r


# ---- electronics pod (bolts to the frame's rear-module interface) ----
POD_X, POD_Y0, POD_Y1, POD_Z0, POD_Z1 = 36.0, -80.0, FRAME_Y0, -22.0, 20.0
SENSOR_WALL = (-49.0, -45.0)


def pod() -> Part:
    p = box(-POD_X, POD_X, POD_Y0, POD_Y1, POD_Z0, POD_Z1)
    p -= box(-POD_X + 3, POD_X - 3, POD_Y0 + 3, POD_Y1 - 4, POD_Z0 + 3, POD_Z1 + 1)   # cavity
    p -= cyl_y(BOSS_D_CLR, BOSS_Y0 - 1, POD_Y1 + 1, 0, 0)                           # boss
    p += box(-16, 16, *SENSOR_WALL, POD_Z0 + 1, POD_Z1) - box(-12.2, 12.2, SENSOR_WALL[1] - 1.6, SENSOR_WALL[1] + 0.1, -12.2, 12.2)
    p -= box(-4, 4, SENSOR_WALL[0] - 1, SENSOR_WALL[1] - 1.5, -10, 10)              # sensor wires
    for x, z in REAR_MOUNTS:                                                         # M3 to frame
        p -= cyl_y(M3_CLR, POD_Y1 - 5, POD_Y1 + 1, x, z)
    # IMU pocket in the floor, Pico on 4 standoffs above it (behind the sensor wall)
    py = (POD_Y0 + 3 + SENSOR_WALL[0]) / 2
    p -= box(-IMU_POCKET[0] / 2, IMU_POCKET[0] / 2, py - IMU_POCKET[1] / 2, py + IMU_POCKET[1] / 2,
             POD_Z0 + 1.5, POD_Z0 + 3.1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * PICO_HOLES[0] / 2, py + sy * PICO_HOLES[1] / 2
            p += cyl_z(5.0, POD_Z0 + 2.9, POD_Z0 + 3 + 9, x, y) - cyl_z(1.8, POD_Z0 + 4, POD_Z0 + 13, x, y)
    p -= box(-POD_X - 1, -POD_X + 4, py - 6, py + 6, POD_Z0 + 9, POD_Z0 + 19)      # Pico USB
    p -= box(POD_X - 4, POD_X + 1, POD_Y0 + 8, POD_Y0 + 20, POD_Z0 + 6, POD_Z0 + 16)  # camera/cable pass
    for x in (-POD_X, POD_X):                                                        # strap slots
        p -= box(x - 6, x + 6, py - 11, py + 11, POD_Z0 + 4, POD_Z0 + 7)
    for x in (-8.0, 8.0):                                                            # VR-controller support
        p -= cyl_y(M3_INSERT_D, POD_Y0 - 1, POD_Y0 + 6, x, 0)
    for sx in (-1, 1):                                                               # lid inserts
        for sy in (POD_Y0 + 6, POD_Y1 - 16):
            p += cyl_z(8, POD_Z0 + 2, POD_Z1, sx * (POD_X - 5), sy) - cyl_z(M3_INSERT_D, POD_Z1 - 6, POD_Z1 + 1, sx * (POD_X - 5), sy)
    return p


BOSS_D_CLR = 18.0


def pod_lid() -> Part:
    lid = box(-POD_X, POD_X, POD_Y0, POD_Y1, POD_Z1, POD_Z1 + 2.5)
    for sx in (-1, 1):
        for sy in (POD_Y0 + 6, POD_Y1 - 16):
            lid -= cyl_z(M3_CLR, POD_Z1 - 1, POD_Z1 + 4, sx * (POD_X - 5), sy)
    for i in range(5):                                                               # vent / styling slots
        x = -24 + i * 12
        lid -= box(x - 2, x + 2, POD_Y0 + 14, POD_Y1 - 18, POD_Z1 - 1, POD_Z1 + 4)
    return lid


def magnet_cap() -> Part:
    """Pressed on the rear end of the pinion shaft; holds a 6x2.5 diametric magnet facing the AS5600."""
    y1 = BOSS_Y0 - 0.5
    y0 = SENSOR_WALL[1] + 2.0
    c = cyl_y(10.0, y0, y1, 0, 0)
    c -= cyl_y(SHAFT_D + PRESS, y0 + 2.6, y1 + 1, 0, 0)
    c -= cyl_y(MAGNET_D + 0.1, y0 - 1, y0 + MAGNET_T, 0, 0)
    return c
