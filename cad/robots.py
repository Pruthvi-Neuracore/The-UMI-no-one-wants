"""Render the dual-arm robots the Hand-E tips reproduce (for the README): ABB GoFa CRB 15000, FANUC CRX-5iA and UR5,
each with Robotiq Hand-E grippers. Robot descriptions come from the Neuracore robots repository (not vendored here):

    python robots.py /path/to/Neuracore_Robots [abb fanuc ur]
"""
import re
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
import trimesh
import yourdfpy

pv.OFF_SCREEN = True
IMG = Path(__file__).resolve().parents[1] / "docs/img"
BG = "#e6eaef"
BLUE = "#1d4f9c"

ROBOTS = {
    # name: (urdf, Hand-E mesh folder (to add at {side}_tool0) or None if the URDF has one, pose {joint regex: value}, view)
    "abb_gofa": ("example_abb/descriptions/crb15000_dual_description/robot.urdf",
                 "example_fanuc/fanuc_decription/crx5ia/meshes/hand_e",
                 {r"joint_2$": 0.35, r"joint_3$": 0.25, r"joint_5$": 0.95}, (1.6, -0.9, 0.8)),
    "fanuc_crx5ia": ("example_fanuc/fanuc_decription/crx5ia/dual_hand_e.urdf", None,
                     {r"J2$": 0.35, r"J3$": -0.25, r"J5$": -0.95}, (1.6, -0.9, 0.8)),
    "ur5": ("example_ur/descriptions/ur5_dual_description/robot.urdf", None,
            {r"left_shoulder_pan": np.pi, r"shoulder_lift": -1.3, r"elbow": 1.6, r"wrist_1": -1.87,
             r"wrist_2": -1.57}, (1.6, -0.9, 0.8)),
}
DROP = re.compile(r"2f140|arg2f")        # the ABB description ships a 2F-140; it is swapped for the Hand-E


def hande_meshes(folder):
    """Hand-E on a Z-out tool flange, as in the Robotiq Hand-E description: coupler, body +11 mm, fingers +99 mm."""
    def load(n):
        m = trimesh.load(folder / n, force="mesh")
        return m
    Tz = lambda z, rz=0.0: trimesh.transformations.translation_matrix([0, 0, z]) @ \
        trimesh.transformations.rotation_matrix(rz, [0, 0, 1])
    return [(load("io_coupler.dae"), Tz(0.0)), (load("hande.dae"), Tz(0.011)),
            (load("finger.dae"), Tz(0.110)), (load("finger.dae"), Tz(0.110, np.pi))]


def render(root, name):
    rel, hande, pose, view = ROBOTS[name]
    path = root / rel
    robot = yourdfpy.URDF.load(str(path), load_meshes=True, build_collision_scene_graph=False)
    cfg = {}
    for j in robot.actuated_joint_names:
        for pat, v in pose.items():
            if re.search(pat, j):
                cfg[j] = v
    robot.update_cfg(cfg)
    meshes = []
    for link in robot.link_map.values():
        for vis in link.visuals:
            g = vis.geometry.mesh
            if g is None or DROP.search(g.filename):
                continue
            m = trimesh.load(path.parent / g.filename, force="mesh")
            if g.scale is not None:
                m.apply_scale(g.scale)
            Tv = vis.origin if vis.origin is not None else np.eye(4)
            m.apply_transform(robot.get_transform(link.name) @ Tv)
            meshes.append((m, "finger" in link.name or "hande" in link.name))
    if hande:
        for side in ("left", "right"):
            for m, T in hande_meshes(root / hande):
                m = m.copy()
                m.apply_transform(robot.get_transform(f"{side}_tool0") @ T)
                meshes.append((m, True))
    pl = pv.Plotter(off_screen=True, window_size=(1300, 1000))
    pl.enable_anti_aliasing("ssaa")
    pl.set_background(BG)
    for m, grip in meshes:
        col = "#2b2d31" if grip else (0.9, 0.91, 0.93)
        pl.add_mesh(pv.wrap(m), color=col, smooth_shading=True, split_sharp_edges=True, specular=0.3)
    pl.view_vector(view, viewup=(0, 0, 1))
    pl.reset_camera()
    pl.camera.zoom(1.15)
    out = IMG / f"robot_{name}.png"
    pl.screenshot(str(out))
    print(out, "parts:", len(meshes))


if __name__ == "__main__":
    root = Path(sys.argv[1])
    for n in (sys.argv[2:] or ROBOTS):
        render(root, n)
