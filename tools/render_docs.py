"""Render the README images.  python tools/render_docs.py"""
import numpy as np
import pyvista as pv
from build123d import import_step

from assembly import HW, ROOT, assemble

pv.OFF_SCREEN = True
IMG = ROOT / "docs/img"


def poly(shape, tol=0.06):
    v, f = shape.tessellate(tol, 0.2)
    return pv.PolyData(np.array([(q.X, q.Y, q.Z) for q in v]), np.hstack([np.full((len(f), 1), 3), np.array(f)]).ravel())


def plotter(shape, size):
    pl = pv.Plotter(off_screen=True, shape=shape, window_size=size, border=False)
    pl.enable_anti_aliasing("ssaa")
    return pl


def hero(opening=0.55):
    parts = assemble(opening)
    meshes = [(poly(s), c) for s, c in parts.values()]
    pl = plotter((1, 2), (2400, 1150))
    for i, v in enumerate(((-0.9, -1.0, -0.8), (-0.25, 1.0, -0.65))):
        pl.subplot(0, i)
        pl.set_background("white")
        for m, c in meshes:
            pl.add_mesh(m, color=c, specular=0.4, specular_power=20, smooth_shading=True, split_sharp_edges=True)
        pl.view_vector(v, viewup=(0, 0, -1))
        pl.reset_camera()
        pl.camera.zoom(1.3)
    pl.screenshot(str(IMG / "hero.png"))


def redesign_sheet():
    pairs = [("fisheye_camera_main_support", "main_support", "T-plate (main support)", (0.8, -0.6, -0.9)),
             ("main_support_cover_plate", "end_cover", "end cover", (0.6, -1.0, -0.5)),
             ("servo_controller_cover", "controller_lid", "controller lid", (0.4, -0.5, 1.0))]
    pl = plotter((2, 3), (2100, 1300))
    for col, (old, new, title, v) in enumerate(pairs):
        for row, (path, tag, colour) in enumerate(((HW / f"STEP/right_handumi/{old}.step", "HandUMI", "#6b707a"),
                                                    (HW / f"STEP/redesign/{new}.step", "redesign", "#1f2126" if col < 2 else "#b8322a"))):
            pl.subplot(row, col)
            pl.set_background("white")
            pl.add_mesh(poly(import_step(str(path)), 0.04), color=colour, specular=0.4, smooth_shading=True, split_sharp_edges=True)
            pl.add_text(f"{title}: {tag}", font_size=10, color="black")
            pl.view_vector(v, viewup=(0, 0, -1) if col < 2 else (0, 1, 0))
            pl.reset_camera()
            pl.camera.zoom(1.15)
    pl.screenshot(str(IMG / "redesign_parts.png"))


if __name__ == "__main__":
    hero()
    redesign_sheet()
    print("ok")
