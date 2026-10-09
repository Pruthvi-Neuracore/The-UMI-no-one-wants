"""Render the README images.  python tools/render_docs.py"""
import numpy as np
import pyvista as pv
from build123d import import_step

from assembly import BLUE, DARK, HW, ORANGE, ROOT, assemble, d405_dummy
from occ import place

pv.OFF_SCREEN = True
IMG = ROOT / "docs/img"


def poly(shape, tol=0.06):
    v, f = shape.tessellate(tol, 0.2)
    return pv.PolyData(np.array([(q.X, q.Y, q.Z) for q in v]), np.hstack([np.full((len(f), 1), 3), np.array(f)]).ravel())


def plotter(shape, size):
    pl = pv.Plotter(off_screen=True, shape=shape, window_size=size, border=False)
    pl.enable_anti_aliasing("ssaa")
    return pl


def show(pl, items, view, up, title=None, zoom=1.2):
    pl.set_background("white")
    for m, c in items:
        pl.add_mesh(m, color=c, specular=0.4, specular_power=20, smooth_shading=True, split_sharp_edges=True)
    if title:
        pl.add_text(title, font_size=11, color="black")
    pl.view_vector(view, viewup=up)
    pl.reset_camera()
    pl.camera.zoom(zoom)


def hero(opening=0.55):
    meshes = [(poly(s), c) for s, c in assemble(opening).values()]
    pl = plotter((1, 2), (2400, 1150))
    for i, v in enumerate(((-0.9, -1.0, -0.8), (-0.25, 1.0, -0.65))):
        pl.subplot(0, i)
        show(pl, meshes, v, (0, 0, -1), zoom=1.3)
    pl.screenshot(str(IMG / "hero.png"))


def parts():
    rd = HW / "STEP/redesign"
    ms, ec, lid = (import_step(str(rd / f)) for f in ("main_support.step", "end_cover.step", "controller_lid.step"))
    cup = import_step(str(HW / "STEP/d405/wrist_d405_mount_handumi.step"))
    up = (0, 0, -1)
    panels = [([(poly(ms, 0.04), BLUE)], "main support", (0.8, -0.6, -0.9), up),
              ([(poly(ms, 0.04), BLUE)], "main support: camera post (M4 hinge)", (-0.9, -0.5, 0.6), up),
              ([(poly(ec, 0.04), BLUE)], "end cover", (0.6, -1.0, -0.5), up),
              ([(poly(lid, 0.04), BLUE)], "controller lid", (0.4, -0.5, 1.0), (0, 1, 0)),
              ([(poly(cup, 0.04), ORANGE)], "D405 wrist mount", (1, -1.3, 0.9), (0, 0, 1)),
              ([(poly(cup, 0.04), ORANGE), (poly(d405_dummy(2.0), 0.04), DARK)], "D405 wrist mount with camera", (1, -1.3, 0.9), (0, 0, 1))]
    pl = plotter((2, 3), (2100, 1300))
    for i, (items, title, v, u) in enumerate(panels):
        pl.subplot(i // 3, i % 3)
        show(pl, items, v, u, title, zoom=1.15)
    pl.screenshot(str(IMG / "parts.png"))


if __name__ == "__main__":
    hero()
    parts()
    print("ok")
