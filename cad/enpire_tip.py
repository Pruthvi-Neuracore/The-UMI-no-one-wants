"""Open-ENPIRE (UCG) finger as a tip for the universal finger-link flange.

Source: pgeedh/Open-ENPIRE-Gripper, grippers-stl/enpire_i2rt_yam_stl (the original ENPIRE finger: rigid jaw +
soft insert, Apache-2.0, copied to source/enpire/). The robot-specific mount tab at the base is cut off and replaced
by a 5 mm plate with the flange's M3 pattern (12 x 24 mm + centre pair); the screws run through the base block and go in
from the lattice side. The second jaw is the mirror image.

    python enpire_tip.py      # -> ../hardware/STL/gripper_tips/Open-ENPIRE/ (mesh-derived, so STL only)
"""
from pathlib import Path

import numpy as np
import trimesh
from build123d import Axis, Box, Cylinder, Mesher, Pos, Rot, export_step, fillet

SRC = Path(__file__).resolve().parent / "source/enpire"
OUT = Path(__file__).resolve().parents[1] / "hardware"
CUT_Y, PLATE_Y = -8.0, -3.0                  # remove y > CUT_Y (the mount tab), add a plate from CUT_Y to PLATE_Y
X0, X1, Z0, Z1 = -24.7, 6.9, -4.3, 28.3      # base block outline
CX, CZ = (X0 + X1) / 2, (Z0 + Z1) / 2        # hole-pattern centre
# the fingers close along native z (soft inserts face each other), which maps to the flange's x (6 mm pitch);
# native x maps to the flange's z (24 mm pitch)
HOLES = [(CX + dx, CZ + dz) for dx in (-12.0, 12.0) for dz in (-6.0, 0.0, 6.0)]
HOLE_DEPTH = 32.0


def to_mesh(shape):
    v, t = shape.tessellate(0.02, 0.1)
    return trimesh.Trimesh(np.array([(q.X, q.Y, q.Z) for q in v]), np.array(t))


def build():
    hard = trimesh.load(SRC / "i2rt_UCG_Hard.stl")
    soft = trimesh.load(SRC / "I2RT_UCG_Soft.stl")
    keep = trimesh.creation.box(extents=[200, 200, 200])
    keep.apply_translation([0, CUT_Y - 100, 0])
    hard = trimesh.boolean.intersection([hard, keep], engine="manifold")
    plate = Pos(CX, (CUT_Y + PLATE_Y) / 2 - 0.25, CZ) * Box(X1 - X0, PLATE_Y - CUT_Y + 0.5, Z1 - Z0)
    plate = fillet(plate.edges().filter_by(Axis.Y), 3.0)
    hard = trimesh.boolean.union([hard, to_mesh(plate)], engine="manifold")
    for x, z in HOLES:
        h = Pos(x, PLATE_Y - HOLE_DEPTH / 2 + 0.01, z) * Rot(90, 0, 0) * Cylinder(1.7, HOLE_DEPTH)
        hard = trimesh.boolean.difference([hard, to_mesh(h)], engine="manifold")
    return hard, soft


def main():
    hard, soft = build()
    mirror = np.eye(4)
    mirror[2, 2], mirror[2, 3] = -1.0, 2 * CZ                         # mirror across the closing axis (z = CZ)
    for t in ("STL", "STEP"):
        (OUT / t / "gripper_tips/Open-ENPIRE").mkdir(parents=True, exist_ok=True)
    for side, M in (("RIGHT", np.eye(4)), ("LEFT", mirror)):
        for name, mesh in (("Jaw", hard), ("Soft-Insert", soft)):
            m = mesh.copy()
            m.apply_transform(M)
            stl = OUT / "STL/gripper_tips/Open-ENPIRE" / f"ENPIRE-{side}-{name}.stl"
            m.export(stl)                                                    # mesh-derived: STL only
            print(stl.name, "watertight", m.is_watertight, "volume", round(m.volume))


if __name__ == "__main__":
    main()
