"""Reconstruct the HandUMI (right hand) assembly from the part files, check it, and render it.

HandUMI publishes parts only, each in its own frame. Every placement here comes from matching
mating features (hole patterns, bores, pins), noted on each part. Frame "M" is the
fisheye_camera_main_support STEP frame: rods along Y, tips toward -X, hand toward +Z, so in use
-Z is up. All parts are loaded from STEP because some HandUMI STLs use a different frame.

    python tools/assembly.py [--opening 0..1] [--camera wrist|plate|stock] [--support STEP] [--check]
"""
import argparse
import itertools
from functools import lru_cache
from pathlib import Path

import numpy as np
from build123d import Axis, Box, Cylinder, Pos, fillet, import_step

from occ import overlap, place

ROOT = Path(__file__).resolve().parents[1]
HW = ROOT / "hardware"
R = HW / "STEP/right_handumi"

CRANK_C = np.array([-18.0, 72.5])        # servo axis (Ø20.4 hole) in M
CRANK_R, ROD_LEN = 21.5, 36.0            # crank pin radius, connecting-link centre distance
LINK_PIN_X = {"thumb": -30.5, "index": -5.5}
CRANK_Z, CONN_Z = 10.0, 15.0             # crank centre plane / connecting-link plane (from --solve)
BLACK, RED, METAL, GREY = "#1f2126", "#b8322a", "#c9ccd1", "#4a4f58"


def T(R3, t):
    m = np.eye(4)
    m[:3, :3] = np.array(R3, float)
    m[:3, 3] = t
    return m


@lru_cache(None)
def step(path):
    return import_step(str(path))


def link_positions(opening):
    """Crank angle 0 = closed, 90 deg = fully open. Crossed linkage: each crank pin drives the far link."""
    th = np.radians(90 * opening)
    u = np.array([np.cos(th), np.sin(th)])
    p1, p2 = CRANK_C + CRANK_R * u, CRANK_C - CRANK_R * u
    yt = p1[1] + np.sqrt(ROD_LEN**2 - (LINK_PIN_X["thumb"] - p1[0]) ** 2)
    yi = p2[1] - np.sqrt(ROD_LEN**2 - (LINK_PIN_X["index"] - p2[0]) ** 2)
    return th, p1, p2, yt, yi


def d405_dummy(floor):
    b = fillet((Pos(0, 0, floor + 11.5) * Box(42, 42, 23)).edges().filter_by(Axis.Z), 7)
    for x in (-9, 9):
        b -= Pos(x, 0, floor + 23) * Cylinder(5, 1.2)
    return b


def assemble(opening=0.6, camera="wrist", tilt_deg=35.0, support=None, crank_z=CRANK_Z, conn_z=CONN_Z):
    parts = {}

    def add(name, shape, mat, colour):
        parts[name] = (place(shape, mat), colour)

    I3 = np.eye(3)
    add("main_support", step(support or R / "fisheye_camera_main_support.step"), np.eye(4), BLACK)
    # cover plate: rod Ø4.1 (x -28/-8, z 29) and M3 (z 4) line up with the bar; nuts in the bar's slots, y 140..150
    add("main_support_cover_plate", step(R / "main_support_cover_plate.step"), T(I3, [0, 150, 0]), BLACK)
    for x in (-28.0, -8.0):                                   # Ø4 x 135 rods
        add(f"rod_{x:+.0f}", Cylinder(2.0, 135.0), T([[1, 0, 0], [0, 0, 1], [0, -1, 0]], [x, 75.0, 29.0]), METAL)

    th, p1, p2, yt, yi = link_positions(opening)
    # finger links: Ø8.2 LM4UU bores (link y -40.5/-20.5, z 1.5) on the rods; flipped so the pin faces the bar
    RL = [[0, -1, 0], [-1, 0, 0], [0, 0, -1]]
    add("thumb_link", step(R / "right_thumb_link.step"), T(RL, [-48.5, yt, 30.5]), RED)
    add("index_link", step(R / "right_index_middle_finger_link.step"), T(RL, [-48.5, yi, 30.5]), RED)
    for nm, yc in (("thumb", yt), ("index", yi)):
        for x in (-28.0, -8.0):
            add(f"lm4uu_{nm}_{x:+.0f}", Cylinder(4.0, 12.0) - Cylinder(2.0, 13.0),
                T([[1, 0, 0], [0, 0, 1], [0, -1, 0]], [x, yc, 29.0]), METAL)

    # STS3215 (SO-ARM100 model): holes (4.2,±10.2)/(-16.5,±10.2) -> M (-9.7/11, 72.5±10.3); top face z 17 -> 5.2 (pocket ceiling)
    add("servo_sts3215", step(HW / "reference/STS3215_03a.step"), T([[-1, 0, 0], [0, -1, 0], [0, 0, 1]], [-5.5, 72.5, -11.8]), BLACK)
    c, s = np.cos(th), np.sin(th)
    add("crank_mechanism_plate", step(R / "crank_mechanism_plate.step"),
        T([[c, 0, -s], [s, 0, c], [0, -1, 0]], [CRANK_C[0], CRANK_C[1], crank_z]), RED)
    for nm, pc, key, yl in (("1", p1, "thumb", yt), ("2", p2, "index", yi)):
        pl = np.array([LINK_PIN_X[key], yl])
        u = (pc - pl) / np.linalg.norm(pc - pl)
        mid = (pc + pl) / 2
        add(f"connecting_link_{nm}", step(R / f"connecting_link_{nm}.step"),
            T([[u[0], 0, -u[1]], [u[1], 0, u[0]], [0, -1, 0]], [mid[0], mid[1], conn_z]), BLACK)

    # arm end stack on the two M3 holes (69, 64.5/80.5): controller support channel | arm | hand support base
    add("hand_support_base", step(R / "hand_support_base.step"), T(I3, [31.0, 54.5, 8.0]), RED)
    add("controller_support", step(R / "right_controller_support.step"),
        T([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], [53.0, 95.4, 0.0]), BLACK)

    # camera on the hinge tab (Ø3.2 axis Y at x -29.7, z -45, centred y 72.5)
    cams = {"wrist": (HW / "STEP/d405/wrist_d405_mount_handumi.step", 2.0),
            "plate": (HW / "STEP/d405/d405_camera_mount.step", 4.0),
            "stock": (R / "camera_mount.step", None)}
    path, floor = cams[camera]
    a = np.radians(tilt_deg)
    base = np.array([[0, 0, -1], [1, 0, 0], [0, -1, 0]], float)   # cam x->+Y (hinge), y->-Z (up), z->-X (view)
    tilt = np.array([[np.cos(a), 0, -np.sin(a)], [0, 1, 0], [np.sin(a), 0, np.cos(a)]])
    Rc = tilt @ base
    tc = np.array([-29.7, 72.5, -45.0]) - Rc @ np.array([0.0, -28.25, 1.5])
    add("camera_mount", step(path), T(Rc, tc), RED)
    if floor is not None:
        add("d405", d405_dummy(floor), T(Rc, tc), GREY)

    # Piper tips on the HandUMI 4x M2 interface (link y=0 face); tip mounting face at tip x=10.8
    Rt = np.array(RL) @ np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    for nm, fn, hc, yc in (("thumb", "Piper-RIGHT-Gripper-Jaw.step", (10.8, 172.7, -56.9), yt),
                           ("index", "Piper-LEFT-Gripper-Jaw.step", (10.8, 238.5, -56.9), yi)):
        add(f"tip_{nm}", step(HW / "STEP/gripper_tips/AgileX-Piper" / fn), T(Rt, np.array([-48.5, yc, 30.5]) - Rt @ np.array(hc)), BLACK)
    return parts


ALLOWED = [{"rod", "lm4uu"}, {"lm4uu", "thumb_link"}, {"lm4uu", "index_link"}, {"rod", "thumb_link"},
           {"rod", "index_link"}, {"rod", "main_support"}, {"rod", "main_support_cover_plate"},
           # pin joints: Ø3 pins run through MR63 bearings in the connecting links (bearings not modelled)
           {"crank_mechanism_plate", "connecting_link_1"}, {"crank_mechanism_plate", "connecting_link_2"},
           {"connecting_link_1", "thumb_link"}, {"connecting_link_2", "index_link"},
           {"camera_mount", "d405"}]          # the D405 is a visual stand-in (body only, no fillet at the floor)


def interferences(parts, tol=1.0):
    hits = []
    for (a, (sa, _)), (b, (sb, _)) in itertools.combinations(parts.items(), 2):
        ka, kb = a.split("_")[0] if a.startswith(("rod", "lm4uu")) else a, b.split("_")[0] if b.startswith(("rod", "lm4uu")) else b
        if {ka, kb} in ALLOWED or ka == kb:
            continue
        v = overlap(sa, sb)
        if v > tol:
            hits.append((a, b, round(v, 1)))
    return hits


def render(parts, out, views=((-0.9, -1.0, -0.75), (-0.2, 1.0, -0.6)), size=(1900, 1000), zoom=1.25):
    import pyvista as pv
    pv.OFF_SCREEN = True
    meshes = []
    for sh, col in parts.values():
        v, f = sh.tessellate(0.08, 0.25)
        meshes.append((pv.PolyData(np.array([(q.X, q.Y, q.Z) for q in v]),
                                   np.hstack([np.full((len(f), 1), 3), np.array(f)]).ravel()), col))
    pl = pv.Plotter(off_screen=True, shape=(1, len(views)), window_size=size)
    for i, v in enumerate(views):
        pl.subplot(0, i)
        pl.set_background("white")
        for m, col in meshes:
            pl.add_mesh(m, color=col, specular=0.35)
        pl.view_vector(v, viewup=(0, 0, -1))      # in use, -Z is up
        pl.reset_camera()
        pl.camera.zoom(zoom)
    pl.screenshot(str(out))
    return out


def solve_heights(opening=0.0):
    """Find crank / connecting-link planes with no interference (closed position is the tightest)."""
    best = None
    for cz in np.arange(9.0, 13.01, 0.5):
        for lz in np.arange(13.0, 18.01, 0.5):
            p = assemble(opening, crank_z=cz, conn_z=lz)
            keys = ["crank_mechanism_plate", "connecting_link_1", "connecting_link_2", "thumb_link",
                    "index_link", "main_support", "servo_sts3215"]
            tot = sum(overlap(p[a][0], p[b][0]) for a, b in itertools.combinations(keys, 2)
                      if not {a, b} <= {"thumb_link", "index_link", "main_support"})
            if best is None or tot < best[0]:
                best = (tot, cz, lz)
    return best


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--opening", type=float, default=0.6)
    ap.add_argument("--camera", default="wrist")
    ap.add_argument("--support", default=None)
    ap.add_argument("--out", default=str(ROOT / "docs/img/assembly.png"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--solve", action="store_true")
    a = ap.parse_args()
    if a.solve:
        print("best (overlap, crank_z, conn_z):", solve_heights())
    else:
        parts = assemble(a.opening, a.camera, support=a.support)
        print(render(parts, a.out))
        if a.check:
            print("interferences:", interferences(parts) or "none")
