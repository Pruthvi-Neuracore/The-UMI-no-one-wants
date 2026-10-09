"""Clean restyle of HandUMI parts. Every mating feature is kept (holes, bores, pockets, rod walls,
servo boss, hinge tab, arm end); only non-functional geometry changes.

  fisheye_camera_main_support -> main_support (T-plate)
      * plate rebuilt from one outline (blends and rounded corners built in) with uniform edge rounding;
        every pocket, hole and nut slot carried over from the original
      * large blended fillets where the arm meets the bar
      * racetrack lightening slots through the two open bar spans
      * rounded arm-end corners
      * smooth blends where the bar meets the round servo boss
      * 45° chamfers on the top corners of the rod end wall and on the outer corners of both bar ends
      * PG logo engraved (0.4 mm) on the outside of the end wall
      * a stiff tapered camera post with a 60 mm keel and a Ø12 / M4 hinge knuckle (see hinge.py)
      * two counterbored M3 holes in the arm for the electronics box
  main_support_cover_plate -> end_cover: matching 45° top and corner chamfers
  electronics_box / electronics_lid: Pico 2 + IMU + USB 3 hub enclosure (electronics_box.py)
  *_thumb_link / *_index_middle_finger_link: universal tip flange (finger_link.py)

    python restyle.py      # -> ../hardware/{STEP,STL}/{right,left}/*
"""
from pathlib import Path

from build123d import (Axis, Box, GeomType, Circle, Cylinder, Face, Location, Plane, Polygon, Pos, Rectangle, Rot,
                       SlotCenterToCenter, export_step, export_stl, extrude, fillet, import_step, loft)

import electronics_box as EB
import hinge as H
from finger_link import finger_link
from logo import logo_face

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent / "source"   # original parts these edits start from (same for both hands)
OUT = ROOT / "hardware"

PLATE_Z = (0.0, 8.0)          # T-plate thickness in its own frame
BLEND_R = 18.0                # arm-to-bar blend radius
ARM_END_R = 8.0
WALL_CHAMFER = 6.0
END_CHAMFER = 4.0
KEEL_LEN = 60.0               # length of the camera-post keel along the bar
EDGE_R = 1.0                  # edge rounding on the plate outline
LOGO_W, LOGO_DEPTH = 16.0, 0.4


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def plate_prism(face2d, z0=PLATE_Z[0], z1=PLATE_Z[1]):
    return Pos(0, 0, z0) * extrude(face2d, z1 - z0, dir=(0, 0, 1))


def wall_chamfers(x0, x1, y0, y1, ztop, c):
    """Prisms removing 45° chamfers on the two top corners of a wall spanning x0..x1 (along Y y0..y1)."""
    cut = None
    for xc, s in ((x0, 1), (x1, -1)):
        tri = Polygon((xc, ztop), (xc + s * c, ztop), (xc, ztop - c), align=None)       # in XZ via rotation below
        prism = Pos(0, y1 + 1, 0) * Rot(90, 0, 0) * extrude(tri, y1 - y0 + 2)
        cut = prism if cut is None else cut + prism
    return cut


def vertical_chamfer(x, y, sx, sy, c, z0, z1):
    """Prism removing a 45° chamfer of size c on the vertical edge at (x, y); (sx, sy) point outward."""
    tri = Polygon((x, y), (x - sx * c, y), (x, y - sy * c), align=None)
    return Pos(0, 0, z0) * extrude(tri, z1 - z0, dir=(0, 0, 1))


def camera_post():
    """Braced post from the plate underside to a Ø12 x 10 hinge knuckle. Each section is lofted smoothly through
    a flare just under the plate, so the post blends into it. The servo's outer face is at x = -28.2, so the
    post grows outward (-X) and along the bar (Y)."""
    ax, az = H.AXIS_M
    yc, w = H.Y_CENTRE, H.CENTRE_W
    zt = az + 7.0                                                        # top of the knuckle web

    def rect(z, x0, x1, ylen):
        return Plane.XY.offset(z) * Pos((x0 + x1) / 2, yc) * Rectangle(x1 - x0, ylen)

    core = loft([rect(0.0, -40.5, -28.2, 30.0), rect(-3.0, -39.0, -28.2, 25.0), rect(zt, -35.7, -28.2, w)], ruled=False)
    keel = loft([rect(0.0, -36.0, -28.2, KEEL_LEN), rect(-3.0, -35.8, -28.2, KEEL_LEN - 14.0), rect(zt, -35.7, -28.2, w)],
                ruled=False)
    knuckle = Pos(ax, yc, az) * Rot(90, 0, 0) * Cylinder(H.KNUCKLE_OD / 2, w)
    web = box(ax - H.KNUCKLE_OD / 2, ax + H.KNUCKLE_OD / 2, yc - w / 2, yc + w / 2, az, zt + 0.5)
    post = core + keel + knuckle + web
    return post - Pos(ax, yc, az) * Rot(90, 0, 0) * Cylinder(H.BOLT_D / 2, w + 2)


def outline_2d(shape, z=4.0):
    """Outer outline of the plate at height z, as a face without interior holes."""
    sl = shape & box(-200, 200, -200, 300, z - 0.05, z + 0.05)
    top = max((f for f in sl.faces() if f.geom_type == GeomType.PLANE and f.normal_at().Z > 0.99), key=lambda f: f.area)
    return Face(top.outer_wire()).moved(Location((0, 0, -top.center().Z)))


def blend_faces():
    """2D additions: arm-to-bar blends and bar-to-boss blends."""
    faces = []
    for cy, sy in ((54.5, -1), (90.5, 1)):
        sq = Polygon((0, cy), (BLEND_R, cy), (BLEND_R, cy + sy * BLEND_R), (0, cy + sy * BLEND_R), align=None)
        faces.append(sq - Pos(BLEND_R, cy + sy * BLEND_R) * Circle(BLEND_R))
    cx, cy, R, xe, r = -18.0, 72.5, 22.5, -36.0, 10.0
    for sy in (1, -1):
        d = ((R + r) ** 2 - (cx - (xe - r)) ** 2) ** 0.5
        fc = (xe - r, cy - sy * d)
        i = (xe, cy - sy * (R**2 - (cx - xe) ** 2) ** 0.5)
        k = R / (R + r)
        b = (cx + (fc[0] - cx) * k, cy + (fc[1] - cy) * k)
        faces.append(Polygon((xe, fc[1]), i, b, align=None) - Pos(*fc) * Circle(r))
    return faces


def cut_faces():
    """2D removals: rounded arm end, faceted bar-end corners."""
    faces = []
    for cy, sy in ((54.5, -1), (90.5, 1)):
        sq = Polygon((74.0, cy), (74.0 - ARM_END_R, cy), (74.0 - ARM_END_R, cy - sy * ARM_END_R), (74.0, cy - sy * ARM_END_R), align=None)
        faces.append(sq - Pos(74.0 - ARM_END_R, cy - sy * ARM_END_R) * Circle(ARM_END_R))
    c = END_CHAMFER
    for x, sx in ((-36.0, -1), (0.0, 1)):
        for y, sy in ((0.0, -1), (140.0, 1)):
            faces.append(Polygon((x, y), (x - sx * c, y), (x, y - sy * c), align=None))
    return faces


def logo_cut(width, depth, at, normal_rot):
    """Engraving prism for the PG logo: `at` = position on the face, `normal_rot` turns +Z into the face normal."""
    return Pos(*at) * normal_rot * Pos(0, 0, -depth) * extrude(logo_face(width), depth + 0.5)


def main_support():
    orig = import_step(str(SRC / "fisheye_camera_main_support.step"))
    z0, z1 = PLATE_Z
    # outline = envelope of sections at three heights, so holes and recesses that open sideways (end-cover screws,
    # nut slots, the Ø45 recess) don't show up as notches in the outline; they are carried over below as voids
    old = None
    for z in (1.5, 4.0, 6.8):
        e = extrude(outline_2d(orig, z), z1 - z0)
        old = e if old is None else old + e
    old = old.clean()
    plate = old
    for f in blend_faces():
        plate = plate + extrude(f, z1 - z0, dir=(0, 0, 1))
    for f in cut_faces():
        plate = plate - Pos(0, 0, -1) * extrude(f, z1 - z0 + 2, dir=(0, 0, 1))
    plate = plate.clean()
    # round the outline edges like the rest of the part, except where the end wall rises off the top face
    bottom = [e for e in plate.edges() if e.bounding_box().max.Z < z0 + 0.01]
    top = [e for e in plate.edges() if e.bounding_box().min.Z > z1 - 0.01 and e.center().Y > 11.5]
    plate = fillet(bottom + top, EDGE_R)

    # carry over every pocket, hole and nut slot inside the plate (thin edge-rounding slivers are dropped)
    voids = old - orig
    keep = [v for v in voids.solids() if v.bounding_box().size.Z > 1.4]
    for v in keep:
        plate -= v
    s = plate + (orig & box(-200, 200, -200, 300, z1 - 0.01, 100))     # end wall above the plate
    s += camera_post()

    # racetrack slots in the open bar spans; the one next to the rod end wall is smaller (FEA: rod loads peak there)
    for cy, length, width in ((33.0, 24.0, 10.0), (110.0, 24.0, 14.0)):
        s -= Pos(-18.0, cy, -1) * extrude(Rot(0, 0, 90) * SlotCenterToCenter(length - width, width), 10)
    for lx, ly in EB.ARM_SCREWS:                                      # electronics box: M3 up through the arm
        x, y = EB.to_m(lx, ly)
        s -= Pos(x, y, 4.0) * Cylinder(1.7, 10)
        s -= Pos(x, y, 8.0 - 1.75) * Cylinder(3.25, 3.6)             # counterbore: head flush with the hand side
    s -= wall_chamfers(-36.0, 0.0, 0.0, 10.7, 34.0, WALL_CHAMFER)
    for x, sx in ((-36.0, -1), (0.0, 1)):                              # facets continue up the end wall
        s -= vertical_chamfer(x, 0.0, sx, -1, END_CHAMFER, z1 - 0.01, 35)
    s -= logo_cut(LOGO_W, LOGO_DEPTH, (-18.0, 0.0, 17.0), Rot(90, 0, 0))   # outer face of the end wall (-Y)
    return s


def end_cover():
    s = import_step(str(SRC / "main_support_cover_plate.step"))
    s -= wall_chamfers(-36.0, 0.0, -10.0, 0.0, 34.0, WALL_CHAMFER)
    for x, sx in ((-36.0, -1), (0.0, 1)):                              # matches the bar's faceted ends
        s -= vertical_chamfer(x, 0.0, sx, 1, END_CHAMFER, -1, 35)
    return s


PARTS = {"main_support": main_support, "end_cover": end_cover,
         "electronics_box": EB.shell, "electronics_lid": EB.lid}


def main():
    for side in ("right", "left"):                                      # finger links differ per hand
        for n in (f"{side}_thumb_link", f"{side}_index_middle_finger_link"):
            p = finger_link(SRC / f"{n}.step")
            print(f"{n:32s} valid={p.is_valid} solids={len(p.solids())} vol={p.volume:.0f}")
            export_step(p, str(OUT / "STEP" / side / f"{n}.step"))
            export_stl(p, str(OUT / "STL" / side / f"{n}.stl"), tolerance=0.02, angular_tolerance=0.15)
    for name, fn in PARTS.items():
        p = fn()
        print(f"{name:16s} valid={p.is_valid} solids={len(p.solids())} vol={p.volume:.0f}")
        for side in ("right", "left"):                                  # identical for both hands
            export_step(p, str(OUT / "STEP" / side / f"{name}.step"))
            export_stl(p, str(OUT / "STL" / side / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.15)


if __name__ == "__main__":
    main()
