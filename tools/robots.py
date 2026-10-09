"""Render the robot arms whose grippers the tip sets reproduce (for the README).

Robot models come from the murobotics-ai/handumi-sw repository (assets/), which is not vendored here:

    python tools/robots.py /path/to/handumi-sw/assets
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

ROBOTS = {
    # name: (urdf relative to assets, package-root map, joint pose {joint-name regex: value}, view)
    "piper": ("piper/piper.urdf", {"piper_description": "piper"},
              {r"joint2$": 1.2, r"joint3$": -1.1, r"joint5$": 0.8, r"joint7$": 0.03, r"joint8$": -0.03}, (1.0, -1.2, 0.7)),
    "trlc-dk1": ("trlc-dk1/TRLC-DK1-Follower.urdf", {}, {r"joint_?2$": 0.9, r"joint_?3$": -1.0, r"joint_?5$": 0.7},
                 (1.0, -1.2, 0.7)),
    "openarm": ("openarm/urdf/openarm_v1.urdf", {"openarm_description": "openarm/openarm_description"},
                {r"joint2$": 0.4, r"joint4$": 1.4, r"joint6$": 0.5}, (1.0, -1.2, 0.6)),
}


def handler(assets, root, pkgs):
    def fn(fname):
        m = re.match(r"package://([^/]+)/(.*)", fname)
        if m:
            base = assets / pkgs.get(m.group(1), m.group(1))
            return str(base / m.group(2))
        return str((root / fname).resolve())
    return fn


ENPIRE_OPENARM = Path(__file__).resolve().parents[1] / "redesign/source/enpire/open-arm_enpire_left-jaw.stl"


def enpire_fingers(robot):
    """Open-ENPIRE OpenArm jaws in place of the stock OpenArm fingers (world-frame meshes).
    Jaw frame (mm): length +x from the mount, height y, thickness z (gripping side at low z). Stock finger mesh frame
    (mm): x across, y thickness (gripping side at low y), z along the finger; mount section starts near z = 670."""
    jaw = trimesh.load(ENPIRE_OPENARM)
    jaw.apply_scale(1000.0)
    M = np.array([[0, 1, 0, 0.0], [0, 0, 1, 17.3], [1, 0, 0, 676.0], [0, 0, 0, 1]], float)
    out = []
    for link in robot.link_map:
        if not link.endswith("_finger"):
            continue
        sy = -1.0 if link.endswith("right_finger") else 1.0           # the URDF mirrors the right finger mesh in y
        S = np.diag([0.001, 0.001 * sy, 0.001, 1.0])
        S[:3, 3] = [0.0, -0.05 * sy, -0.673001]                        # the URDF visual origin of the finger (mirrored for the right)
        m = jaw.copy()
        m.apply_transform(robot.get_transform(link) @ S @ M)
        if sy < 0:
            m.invert()
        out.append(m)
    return out


def render(assets, name, enpire=False):
    rel, pkgs, pose, view = ROBOTS[name]
    path = assets / rel
    robot = yourdfpy.URDF.load(str(path), filename_handler=handler(assets, path.parent, pkgs), load_meshes=True)
    cfg = {}
    for j in robot.actuated_joint_names:
        for pat, v in pose.items():
            if re.search(pat, j):
                lim = robot.joint_map[j].limit
                cfg[j] = float(np.clip(v, lim.lower, lim.upper)) if lim is not None and lim.lower is not None else v
    robot.update_cfg(cfg)
    scene = robot.scene
    pl = pv.Plotter(off_screen=True, window_size=(1100, 1000))
    pl.enable_anti_aliasing("ssaa")
    pl.set_background(BG)
    for node in scene.graph.nodes_geometry:
        T, gname = scene.graph[node]
        g = scene.geometry[gname]
        if not isinstance(g, trimesh.Trimesh) or (enpire and "finger" in str(gname).lower()):
            continue
        g = g.copy()
        g.apply_transform(T)
        col = g.visual.main_color[:3] / 255.0 if hasattr(g.visual, "main_color") else (0.75, 0.77, 0.8)
        if np.allclose(col, 0) or np.allclose(col, 1):
            col = (0.72, 0.74, 0.78)
        pl.add_mesh(pv.wrap(g), color=col, smooth_shading=True, split_sharp_edges=True, specular=0.3)
    if enpire:
        for m in enpire_fingers(robot):
            pl.add_mesh(pv.wrap(m), color="#1d4f9c", smooth_shading=True, specular=0.3)
    pl.view_vector(view, viewup=(0, 0, 1))
    pl.reset_camera()
    pl.camera.zoom(1.2)
    out = IMG / f"robot_{name}{'_enpire' if enpire else ''}.png"
    pl.screenshot(str(out))
    print(out, "joints posed:", len(cfg))


if __name__ == "__main__":
    assets = Path(sys.argv[1])
    for n in (sys.argv[2:] or ["piper", "openarm", "openarm+enpire"]):
        try:
            render(assets, n.split("+")[0], enpire=n.endswith("+enpire"))
        except Exception as e:
            print(n, "FAILED", repr(e)[:200])
