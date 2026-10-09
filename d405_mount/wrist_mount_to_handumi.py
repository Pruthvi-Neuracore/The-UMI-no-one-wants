"""Adapt the user's D405 wrist-camera cup to HandUMI's camera hinge.

Input:  a mesh of the wrist camera mount (D405 cup + 4x M3 flat tab), in metres or mm.
Output: the same cup with the tab removed and two Ø12 hinge lugs (M4 pivot, redesign/hinge.py)
        on the edge the tab used to be on, plus a cable window in the top wall matching the
        side windows. It mates with the redesigned main support's camera post.

The cup is re-oriented into HandUMI's camera_mount frame: cup floor outer face at z=0,
D405 centred on (0, 0), camera looking +Z, hinge axis along X at (y, z) = hinge.AXIS_CAM.
The tilt now comes from the HandUMI hinge instead of being built into the part.

    python wrist_mount_to_handumi.py <input.stl>
"""
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import Axis, Box, Cylinder, Mesher, Pos, Rot, export_step, fillet

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "redesign"))
import hinge as H  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
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


def to_mesh(shape) -> trimesh.Trimesh:
    v, t = shape.tessellate(0.02, 0.1)
    return trimesh.Trimesh(np.array([(q.X, q.Y, q.Z) for q in v]), np.array(t))


def hinge_lugs() -> trimesh.Trimesh:
    """Two Ø12 lugs on an M4 pivot that straddle the main support's 10 mm centre knuckle (redesign/hinge.py)."""
    ay, az = H.AXIS_CAM
    r = H.KNUCKLE_OD / 2
    x_in = H.CENTRE_W / 2 + H.GAP
    lugs = None
    for s in (-1, 1):
        x0, x1 = sorted((s * x_in, s * (x_in + H.LUG_W)))
        w = x1 - x0
        lug = Pos((x0 + x1) / 2, ay, az) * Rot(0, 90, 0) * Cylinder(r, w)
        lug += Pos((x0 + x1) / 2, (ay - WALL_OUTER + 1.0) / 2, az) * Box(w, abs(ay + WALL_OUTER - 1.0), 2 * r)
        lug -= Pos((x0 + x1) / 2, ay, az) * Rot(0, 90, 0) * Cylinder(H.BOLT_D / 2, w + 2)
        lugs = lug if lugs is None else lugs + lug
    return to_mesh(lugs)


# cable window in the top wall (+Y, opposite the hinge), same size as the cup's side windows
TOP_WINDOW = dict(x=(-13.0, 13.0), z=(2.04, 15.75), corner_r=3.0)


def top_window_cutter() -> trimesh.Trimesh:
    (x0, x1), (z0, z1) = TOP_WINDOW["x"], TOP_WINDOW["z"]
    w = Pos((x0 + x1) / 2, WALL_OUTER, (z0 + z1) / 2) * Box(x1 - x0, 8.0, z1 - z0)
    w = fillet(w.edges().filter_by(Axis.Y), TOP_WINDOW["corner_r"])
    v, t = w.tessellate(0.02, 0.1)
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

    part = trimesh.boolean.union([cup, hinge_lugs()], engine="manifold")
    part = trimesh.boolean.difference([part, top_window_cutter()], engine="manifold")
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
