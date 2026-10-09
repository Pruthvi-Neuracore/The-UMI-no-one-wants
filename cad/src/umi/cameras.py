"""Swappable camera adapters on the 20x20 M3 dock. Every adapter puts the optical centre at
CAM_CENTER pitched down CAM_TILT, so swapping cameras keeps the viewpoint (Insta360 later)."""
from build123d import Part, Pos, Rot

from .jaw_module import box, cyl_x, cyl_y, cyl_z
from .params import *

DOCK_TOP = FRAME_Z + TOP_T


def dock_base() -> Part:
    b = box(-DOCK_PITCH / 2 - 6, DOCK_PITCH / 2 + 6, DOCK_Y - DOCK_PITCH / 2 - 6, DOCK_Y + DOCK_PITCH / 2 + 6,
            DOCK_TOP, DOCK_TOP + 5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * DOCK_PITCH / 2, DOCK_Y + sy * DOCK_PITCH / 2
            b -= cyl_z(M3_CLR, DOCK_TOP - 1, DOCK_TOP + 6, x, y)
            b -= cyl_z(6.2, DOCK_TOP + 3, DOCK_TOP + 6, x, y)
    return b


def _at_camera(p: Part) -> Part:
    """Place a part modelled at the optical centre (looking +Y) into the camera pose."""
    cx, cy, cz = CAM_CENTER
    return Pos(cx, cy, cz) * Rot(-CAM_TILT, 0, 0) * p


def _mast(x_in: float, plate_front: float, plate_bottom: float, plate_top: float) -> Part:
    """Two vertical fins at |x| in [x_in, x_in+4], from the dock up to the camera plate, trimmed
    flush with the plate's front face and top edge so they stay out of the field of view."""
    fins = Part()
    for x0 in (-x_in - 4, x_in):
        fins += box(x0, x0 + 4, DOCK_Y - DOCK_PITCH / 2 - 20, DOCK_Y + DOCK_PITCH / 2 + 6,
                    DOCK_TOP + 4.99, CAM_CENTER[2] + 60)
    fins -= _at_camera(box(-80, 80, plate_front, 200, plate_bottom, 200))
    fins -= _at_camera(box(-80, 80, -200, 200, plate_top, 200))
    for sx in (-1, 1):                     # feet: widen the dock base out to the fins
        x0, x1 = sorted((sx * (DOCK_PITCH / 2 + 5.99), sx * (x_in + 4)))
        fins += box(x0, x1, DOCK_Y - DOCK_PITCH / 2 - 6, DOCK_Y + DOCK_PITCH / 2 + 6, DOCK_TOP, DOCK_TOP + 5)
    return fins


def imx335_mount() -> Part:
    s = IMX335_BOARD + 4
    plate = box(-s / 2 - 6, s / 2 + 6, -14, -11, -s / 2, s / 2)  # board sits behind, lens through
    plate -= cyl_y(IMX335_LENS, -15, -10, 0, 0)
    for sx in (-1, 1):
        for sz in (-1, 1):
            plate -= cyl_y(2.2, -15, -10, sx * IMX335_HOLES / 2, sz * IMX335_HOLES / 2)
    return dock_base() + _mast(s / 2 + 2, -11, -s / 2, s / 2) + _at_camera(plate)


def d405_cradle() -> Part:
    w, d, h = D405
    tray = box(-w / 2 - 3, w / 2 + 3, -d - 3, 1.5, -h / 2 - 3, -h / 2)        # floor
    tray += box(-w / 2 - 3, -w / 2, -d - 3, 1.5, -h / 2 - 0.01, -h / 2 + 8)   # side lips
    tray += box(w / 2, w / 2 + 3, -d - 3, 1.5, -h / 2 - 0.01, -h / 2 + 8)
    tray += box(-w / 2 - 3, w / 2 + 3, -d - 3, -d, -h / 2 - 0.01, -h / 2 + 8)  # back lip
    tray -= cyl_z(6.6, -h / 2 - 4, -h / 2 + 1, 0, -d / 2)                     # 1/4-20 (centre: VERIFY)
    tray += box(-w / 2 - 7, w / 2 + 7, -d - 3, 1.5, -h / 2 - 3, -h / 2)    # wings for the fins
    return dock_base() + _mast(w / 2 + 3, 1.5, -h / 2 - 3, -h / 2) + _at_camera(tray)
