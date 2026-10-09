"""Render the README image of the D405 wrist mount (offscreen).  python render_mounts.py <input wrist mount .stl>"""
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
import trimesh
from build123d import Axis, Box, Cylinder, Pos, fillet

pv.OFF_SCREEN = True
ROOT = Path(__file__).resolve().parents[1]
RED, GREY = "#c0392b", "#4a4f58"


def d405_body(floor_z):
    b = fillet((Pos(0, 0, floor_z + 11.5) * Box(42, 42, 23)).edges().filter_by(Axis.Z), 5)
    for x in (-9, 9):
        b -= Pos(x, 0, floor_z + 23) * Cylinder(5, 1.2)
    v, t = b.tessellate(0.05, 0.2)
    return pv.PolyData(np.array([(q.X, q.Y, q.Z) for q in v]), np.hstack([np.full((len(t), 1), 3), np.array(t)]).ravel())


def sheet(panels, out):
    pl = pv.Plotter(off_screen=True, shape=(2, 3), window_size=(1950, 1250))
    for i, (items, title, vv) in enumerate(panels):
        pl.subplot(i // 3, i % 3)
        pl.set_background("white")
        for m, c in items:
            pl.add_mesh(m if isinstance(m, pv.PolyData) else pv.wrap(m), color=c, specular=0.3)
        pl.add_text(title, font_size=11, color="black")
        pl.view_vector(vv, viewup=(0, 0, 1) if abs(vv[2]) < 0.95 else (0, 1, 0))
        pl.reset_camera()
        pl.camera.zoom(1.05)
    pl.screenshot(str(out))
    print(out)


def main(src):
    orig = trimesh.load(src, force="mesh")
    if orig.extents.max() < 1.0:
        orig.apply_scale(1000.0)
    wrist = trimesh.load(ROOT / "hardware/STL/d405/wrist_d405_mount_handumi.stl")
    iso, side, back, front = (1, -1.3, 0.9), (1, 0, 0.05), (0.2, -0.3, -1), (0.15, -0.25, 1)
    sheet([([(orig, RED)], "source wrist mount (input)", (1, -1, 0.8)),
           ([(wrist, RED)], "adapted: HandUMI hinge, tab removed", iso),
           ([(wrist, RED), (d405_body(2), GREY)], "with D405", iso),
           ([(wrist, RED), (d405_body(2), GREY)], "side (hinge axis = X)", side),
           ([(wrist, RED)], "back: 2x M3 for the D405, 20 mm", back),
           ([(wrist, RED), (d405_body(2), GREY)], "front (camera view direction)", front)],
          ROOT / "docs/img/wrist_d405_mount_handumi.png")


if __name__ == "__main__":
    main(sys.argv[1])
