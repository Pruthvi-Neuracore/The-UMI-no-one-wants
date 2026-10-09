"""Dump the real cylindrical features (holes/bosses/bores) of STEP parts, merged per axis line.

    python tools/features.py part.step [...]
"""
import sys
from collections import defaultdict

from build123d import GeomType, import_step
from OCP.BRepAdaptor import BRepAdaptor_Surface


def features(path, min_span=1.2):
    s = import_step(path)
    bb = s.bounding_box()
    groups = defaultdict(list)
    for f in s.faces():
        if f.geom_type != GeomType.CYLINDER:
            continue
        c = BRepAdaptor_Surface(f.wrapped).Cylinder()
        d = c.Axis().Direction()
        ax = [round(abs(v), 2) for v in (d.X(), d.Y(), d.Z())]
        fb = f.bounding_box()
        if max(ax) < 0.99:
            continue
        k = ax.index(max(ax))
        loc = c.Location()
        p = [loc.X(), loc.Y(), loc.Z()]
        other = [round(p[i], 1) for i in range(3) if i != k]
        lo, hi = [(fb.min.X, fb.min.Y, fb.min.Z)[k], (fb.max.X, fb.max.Y, fb.max.Z)[k]]
        groups[(round(c.Radius() * 2, 2), "XYZ"[k], tuple(other))].append((lo, hi))
    print(f"\n## {path.split('/')[-1]}  bbox x[{bb.min.X:.1f},{bb.max.X:.1f}] y[{bb.min.Y:.1f},{bb.max.Y:.1f}] z[{bb.min.Z:.1f},{bb.max.Z:.1f}]")
    for (d, ax, other), spans in sorted(groups.items()):
        lo, hi = min(s[0] for s in spans), max(s[1] for s in spans)
        # a full bore has angular coverage: approximate by span along the axis
        if hi - lo < min_span and d < 5:
            continue
        print(f"  Ø{d:<6} axis {ax} at {other}  span [{lo:.1f},{hi:.1f}]")


for p in sys.argv[1:]:
    features(p)
