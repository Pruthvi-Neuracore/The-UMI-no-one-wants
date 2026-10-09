"""Render preview PNGs of both assemblies (offscreen VTK via pyvista).

    python -m umi.render          # writes docs/img/*.png
"""
from pathlib import Path

import numpy as np
import pyvista as pv

from build123d import Pos, import_step

from .build import PARTS, assembly
from .jaw_module import cyl_x
from .params import CAR_W, CAR_Y1, CLOSED_XC, END_T, FRAME_X, LMU_L, LMU_OD, ROD_D, ROD_Z, TRAVEL

TIPS = Path(__file__).resolve().parents[2] / "third_party" / "handumi_gripper_tips" / "STEP" / "UMI-Gripper"
HOLDER_HOLE_CENTRE = (50.0, 71.2, -2.4)   # right holder's 4x M2 pattern centre in HandUMI's frame

pv.OFF_SCREEN = True
IMG = Path(__file__).resolve().parents[3] / "docs" / "img"
# first match wins
PALETTE = [("servo(", "#2d6cdf"), ("rod", "#c9ccd1"), ("lm6uu", "#9aa0a8"), ("tip", "#f2f2f2"), ("carriage", "#e4572e"), ("ring", "#e4572e"), ("pinion", "#f3a712"),
           ("coupler", "#f3a712"), ("magnet", "#f3a712"), ("lid", "#5a6170"), ("cam", "#5a6170"),
           ("", "#23262d")]
VIEWS = {"iso": (1.0, -1.2, 0.8), "front": (0.5, 1.0, 0.35), "side": (1.0, 0.0, 0.1)}


def to_mesh(part):
    verts, tris = part.tessellate(0.15, 0.2)
    v = np.array([(q.X, q.Y, q.Z) for q in verts])
    f = np.hstack([np.full((len(tris), 1), 3), np.array(tris)]).ravel()
    return pv.PolyData(v, f)


def colour(name):
    return next(c for k, c in PALETTE if k in name)


def vitamins(opening):
    """Rods, bearings and the HandUMI UMI-Gripper finger holders (render only)."""
    xc = CLOSED_XC + opening / 2
    xo = FRAME_X + END_T
    v = {f"rod{z}": cyl_x(ROD_D, -xo, xo, 0, z) for z in (ROD_Z, -ROD_Z)}
    for s in (-1, 1):
        for z in (ROD_Z, -ROD_Z):
            x0 = s * xc - CAR_W / 2 if s < 0 else s * xc + CAR_W / 2 - LMU_L
            v[f"lm6uu{s}{z}"] = cyl_x(LMU_OD, x0, x0 + LMU_L, 0, z) - cyl_x(ROD_D, x0 - 1, x0 + LMU_L + 1, 0, z)
    hx, hy, hz = HOLDER_HOLE_CENTRE
    v["tip_R"] = Pos(xc - hx, CAR_Y1 - hy, -hz) * import_step(str(TIPS / "UMI-RIGHT-Finger-Holder.step"))
    v["tip_L"] = Pos(-xc + hx, CAR_Y1 - hy, -hz) * import_step(str(TIPS / "UMI-LEFT-Finger-Holder.step"))
    return v


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    parts = {k: fn() for k, (fn, _, _) in PARTS.items()}
    for kind in ("collector", "openarm_unit"):
        for opening, tag in ((2 * TRAVEL, "open"), (10.0, "closed")):
            a = assembly(kind, opening, parts) | vitamins(opening)
            meshes = {n: to_mesh(p) for n, p in a.items()}
            for view, cam in VIEWS.items():
                if tag == "closed" and view != "iso":
                    continue
                pl = pv.Plotter(off_screen=True, window_size=(1400, 1000))
                pl.set_background("white")
                for n, m in meshes.items():
                    pl.add_mesh(m, color=colour(n), smooth_shading=False, specular=0.3,
                                show_edges=False, opacity=0.35 if n.startswith("servo(") else 1.0)
                pl.camera_position = [tuple(500 * np.array(cam)), (0, -10, 10), (0, 0, 1)]
                pl.reset_camera()
                pl.camera.zoom(1.15)
                out = IMG / f"{kind}_{tag}_{view}.png"
                pl.screenshot(str(out))
                pl.close()
                print(out)


if __name__ == "__main__":
    main()
