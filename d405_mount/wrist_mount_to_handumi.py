"""Adapt the user's D405 wrist-camera cup to HandUMI's camera hinge.

Input:  a mesh of the wrist camera mount (D405 cup + 4x M3 flat tab), in metres or mm.
Output: the same cup with the tab removed and HandUMI's camera_mount hinge (two Ø8
        knuckles, M3 pivot) fused to the edge of the cup that the tab used to be on.

The cup is re-oriented into HandUMI's camera_mount frame: cup floor outer face at z=0,
D405 centred on (0, 0), camera looking +Z, hinge axis along X at y=-28.25, z=1.5.
The tilt now comes from the HandUMI hinge instead of being built into the part.

    python wrist_mount_to_handumi.py <input.stl>
"""
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import Box, Mesher, Pos, export_step, import_step

ROOT = Path(__file__).resolve().parents[1]
HANDUMI_MOUNT = ROOT / "hardware/STEP/right_handumi/camera_mount.step"
OUT = ROOT / "hardware"

# measured on the supplied mesh (mm, its own frame)
N_IN = np.array([0.0, 0.598, 0.802])       # cup floor normal, pointing into the cup = view direction
FLOOR_OUTER = -39.27                       # N_IN . p on the floor's outer face
U = np.array([0.0, -0.802, 0.598])         # in-plane direction across the cup (toward the far wall)
U_CENTRE = (53.85 + 95.95) / 2             # midway between the inner wall faces
WALL_OUTER = 21.05 + 1.5                   # inner half-width + wall


def to_handumi_frame(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    x = np.array([-1.0, 0.0, 0.0])         # chosen so (x, U, N_IN) is right-handed
    R = np.vstack([x, U, N_IN])
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = [0.0, -U_CENTRE, -FLOOR_OUTER]
    m = mesh.copy()
    m.apply_transform(T)
    return m


def hinge_mesh() -> trimesh.Trimesh:
    original = import_step(str(HANDUMI_MOUNT))
    keep = Pos(0, -40.75, 0) * Box(20, 40, 20)           # |x| < 10, y < -20.75: knuckles + necks only
    hinge = original & keep
    v, t = hinge.tessellate(0.02, 0.1)
    return trimesh.Trimesh(np.array([(q.X, q.Y, q.Z) for q in v]), np.array(t))


def main(src):
    m = trimesh.load(src, force="mesh")
    if m.extents.max() < 1.0:              # exported in metres
        m.apply_scale(1000.0)
    cup = to_handumi_frame(m)

    # drop the tab: keep only what is inside the cup's outer footprint (plus the far side)
    cutter = trimesh.creation.box(extents=[80, 200, 200])
    cutter.apply_translation([0, -WALL_OUTER - 0.01 + 100, 50])
    cup = trimesh.boolean.intersection([cup, cutter], engine="manifold")

    # bridge between the knuckle necks and the cup wall/floor (same thickness as HandUMI's plate)
    bridge = trimesh.creation.box(extents=[20.0, 3.0, 3.0])        # spans the knuckle necks only
    bridge.apply_translation([0, -WALL_OUTER + 0.5, 1.5])

    part = trimesh.boolean.union([cup, bridge, hinge_mesh()], engine="manifold")
    parts = part.split(only_watertight=False)
    print(f"watertight={part.is_watertight} bodies={len(parts)} volume={part.volume:.0f} mm3 "
          f"extents={part.extents.round(1)} bounds_min={part.bounds[0].round(1)}")

    for sub in ("STL", "STEP"):
        (OUT / sub / "d405").mkdir(parents=True, exist_ok=True)
    part.export(OUT / "STL/d405/wrist_d405_mount_handumi.stl")
    stl = OUT / "STL/d405/wrist_d405_mount_handumi.stl"
    solid = Mesher().read(str(stl))[0]                     # faceted B-rep, imports into Onshape as a part
    export_step(solid, str(OUT / "STEP/d405/wrist_d405_mount_handumi.step"))
    return part


if __name__ == "__main__":
    main(sys.argv[1])
