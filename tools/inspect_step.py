"""Print bounding box, volume and cylindrical features (holes/bosses) of STEP files."""
import sys
from collections import Counter

from OCP.BRepAdaptor import BRepAdaptor_Surface
from build123d import GeomType, import_step


def describe(path, max_cyl=40):
    shape = import_step(path)
    bb = shape.bounding_box()
    print(f"\n### {path}")
    print(f"bbox min=({bb.min.X:.1f},{bb.min.Y:.1f},{bb.min.Z:.1f}) "
          f"size=({bb.size.X:.1f},{bb.size.Y:.1f},{bb.size.Z:.1f}) vol={shape.volume:.0f}mm3 solids={len(shape.solids())}")
    cyls = Counter()
    for f in shape.faces():
        if f.geom_type != GeomType.CYLINDER:
            continue
        s = BRepAdaptor_Surface(f.wrapped).Cylinder()
        loc, ax = s.Location(), s.Axis().Direction()
        axis = tuple(round(abs(v), 2) for v in (ax.X(), ax.Y(), ax.Z()))
        key = (round(s.Radius() * 2, 2), axis, round(loc.X(), 1), round(loc.Y(), 1), round(loc.Z(), 1))
        cyls[key] += 1
    print(f"cylinders (dia, axis, point-on-axis) x{len(cyls)}:")
    for k in sorted(cyls)[:max_cyl]:
        print("  ", k)


for p in sys.argv[1:]:
    describe(p)
