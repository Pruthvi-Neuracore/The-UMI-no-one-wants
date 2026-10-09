"""Robotiq Hand-E finger as a tip for the universal finger-link flange.

Source: the Hand-E finger visual mesh (robotiq_hande_description, as used in Neuracore_Robots), copied to
source/hand_e/finger.dae. The jaw carriage below the finger is cropped off, the finger is remeshed into a watertight
solid, and set on a 4 mm plate with the flange's M3 pattern (6 mm along the closing axis, 24 mm across), with the screw
holes just outside the finger so the heads stay reachable. Both jaws use the same part (one turned 180°), like the
Hand-E itself.

    python hande_tip.py      # -> ../hardware/STL/gripper_tips/Robotiq-Hand-E/ (mesh-derived, so STL only)
"""
from pathlib import Path

import numpy as np
import trimesh
from build123d import Axis, Box, Cylinder, Mesher, Pos, export_step, fillet

SRC = Path(__file__).resolve().parent / "source/hand_e/finger.dae"
OUT = Path(__file__).resolve().parents[1] / "hardware"
CROP_X, CROP_Z = -0.5, 6.0                    # keep the finger only (the carriage sits at x < 0, z < 6)
PLATE = (-4.0, 15.0, -15.0, 15.0, 2.0, 6.5)   # x0, x1, y0, y1, z0, z1 (overlaps the finger base by 0.5 mm)
CX = 5.5                                       # centre of the finger thickness (closing axis)
HOLES = [(CX + dx, dy) for dx in (-6.0, 0.0, 6.0) for dy in (-12.0, 12.0)]


def to_mesh(shape):
    v, t = shape.tessellate(0.02, 0.1)
    return trimesh.Trimesh(np.array([(q.X, q.Y, q.Z) for q in v]), np.array(t))


def build():
    m = trimesh.load(SRC, force="mesh")
    m.apply_scale(1000.0)
    for origin, normal in (((CROP_X, 0, 0), (1, 0, 0)), ((0, 0, CROP_Z), (0, 0, 1))):
        m = m.slice_plane(origin, normal, cap=False)
    vox = m.voxelized(pitch=0.25).fill()                                  # watertight solid from the visual mesh
    finger = vox.marching_cubes
    finger.apply_transform(vox.transform)
    trimesh.smoothing.filter_taubin(finger, iterations=10)
    x0, x1, y0, y1, z0, z1 = PLATE
    plate = Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)
    plate = fillet(plate.edges().filter_by(Axis.Z), 2.5)
    for x, y in HOLES:
        plate -= Pos(x, y, (z0 + z1) / 2) * Cylinder(1.7, z1 - z0 + 1)
    tip = trimesh.boolean.union([finger, to_mesh(plate)], engine="manifold")
    for x, y in HOLES:                                                    # keep the holes clear of the finger
        h = Pos(x, y, z0 + 10) * Cylinder(1.7, 20)
        tip = trimesh.boolean.difference([tip, to_mesh(h)], engine="manifold")
    return tip


def main():
    tip = build()
    import manifold3d                                                     # simplify but stay watertight
    mf = manifold3d.Manifold(manifold3d.Mesh(tip.vertices.astype(np.float32), tip.faces.astype(np.uint32))).simplify(0.06)
    out = mf.to_mesh()
    tip = trimesh.Trimesh(np.asarray(out.vert_properties)[:, :3], np.asarray(out.tri_verts))
    stl = OUT / "STL/gripper_tips/Robotiq-Hand-E/Hand-E-Finger.stl"           # mesh-derived: STL only
    tip.export(stl)
    print(stl.name, "watertight", tip.is_watertight, "bounds", tip.bounds.round(1).tolist())


if __name__ == "__main__":
    main()
