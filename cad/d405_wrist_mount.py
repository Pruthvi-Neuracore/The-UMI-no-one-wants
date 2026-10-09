"""Adapt the user's D405 wrist-camera cup to HandUMI's camera hinge.

Input:  a mesh of the wrist camera mount (D405 cup + 4x M3 flat tab), in metres or mm.
Output: the same cup with the tab removed and two Ø12 hinge lugs (M4 pivot, hinge.py)
        on the edge the tab used to be on, plus a cable window in the top wall matching the
        side windows. It mates with the redesigned main support's camera post.

The cup is re-oriented into HandUMI's camera_mount frame: cup floor outer face at z=0,
D405 centred on (0, 0), camera looking +Z, hinge axis along X at (y, z) = hinge.AXIS_CAM.
The tilt now comes from the HandUMI hinge instead of being built into the part.

    python d405_wrist_mount.py [source/wrist_camera_mount.stl]
"""
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import Axis, Box, Cylinder, Mesher, Pos, Rot, export_step, fillet

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hinge as H  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hardware"

# measured on the supplied mesh (mm, its own frame)
N_IN = np.array([0.0, 0.598, 0.802])       # cup floor normal, pointing into the cup = view direction
FLOOR_OUTER = -39.27                       # N_IN . p on the floor's outer face
U = np.array([0.0, -0.802, 0.598])         # in-plane direction across the cup (toward the far wall)
U_CENTRE = (53.85 + 95.95) / 2             # midway between the inner wall faces
WALL_OUTER = 21.05 + 1.5                   # inner half-width + wall


def to_mount_frame(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
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
    """Two Ø12 lugs on an M4 pivot that straddle the main support's 10 mm centre knuckle (hinge.py)."""
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
    # triangulated gussets: from each lug up the back wall of the cup and forward under its floor, one rib per lug
    for sgn in (-1, 1):
        x0, x1 = sorted((sgn * x_in, sgn * (x_in + H.LUG_W)))
        lugs += gusset(x0, x1)
    return to_mesh(lugs)


def gusset(x0, x1):
    """Triangulated rib in the cup's y-z plane between x0 and x1: a strut from the lug up the back wall and a strut
    from the lug along the underside of the floor, filling the corner between them. Rounded edges."""
    from build123d import Plane, Polygon, extrude
    ay, az = H.AXIS_CAM
    w = -WALL_OUTER + 0.15                                       # just inside the back wall's outer face
    pts = [(ay + 1.5, az - 6.0),                                  # bottom of the lug
           (GUSSET_FLOOR_END, 0.15),                              # along the underside of the floor
           (w, 0.15),                                             # the cup's back corner
           (w, GUSSET_WALL_TOP),                                  # up the back wall
           (ay + 2.5, az + 6.0)]                                  # top of the lug
    pl = Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))   # sketch in y-z, extrude along +x
    face = pl * Polygon(*pts, align=None)
    rib = extrude(face, x1 - x0)
    try:
        rib = fillet(rib.edges().filter_by(Axis.X, reverse=True), 1.2)
    except Exception:
        pass
    return rib


# cable window in the top wall (+Y, opposite the hinge), same size as the cup's side windows
GUSSET_FLOOR_END = -6.0                    # gusset runs under the floor to here (clear of the camera screws)
GUSSET_WALL_TOP = 20.0                     # and up the back wall to here
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
    cup = to_mount_frame(m)

    # drop the tab: keep only what is inside the cup's outer footprint (plus the far side)
    cutter = trimesh.creation.box(extents=[80, 200, 200])
    cutter.apply_translation([0, -WALL_OUTER - 0.01 + 100, 50])
    cup = trimesh.boolean.intersection([cup, cutter], engine="manifold")

    part = trimesh.boolean.union([cup, hinge_lugs()], engine="manifold")
    part = trimesh.boolean.difference([part, top_window_cutter()], engine="manifold")
    parts = part.split(only_watertight=False)
    print(f"watertight={part.is_watertight} bodies={len(parts)} volume={part.volume:.0f} mm3 "
          f"extents={part.extents.round(1)} bounds_min={part.bounds[0].round(1)}")

    for side in ("right", "left"):                         # same part for both hands
        stl = OUT / "STL" / side / "d405_wrist_mount.stl"
        part.export(stl)
    solid = Mesher().read(str(stl))[0]                     # faceted B-rep, imports into Onshape as a part
    for side in ("right", "left"):
        export_step(solid, str(OUT / "STEP" / side / "d405_wrist_mount.step"))
    return part


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent / "source/wrist_camera_mount.stl"))
