"""Build every part, export STEP + STL, and check assemblies for interference.

    python -m umi.build            # from cad/src
"""
import itertools
import sys
from pathlib import Path

from build123d import Compound, Pos, Rot, export_step, export_stl

from . import cameras, collector, jaw_module as jm, robot
from .params import CLOSED_XC, OPEN_XC, STROKE_DEG, TRAVEL

OUT = Path(__file__).resolve().parents[2]

# name -> (builder, qty, group)
PARTS = {
    "frame": (jm.frame, 1, "jaw_module"),
    "carriage": (jm.carriage, 2, "jaw_module"),
    "pinion": (jm.pinion, 1, "jaw_module"),
    "finger_ring_thumb": (lambda: collector.finger_ring(False), 1, "collector"),
    "finger_ring_index": (lambda: collector.finger_ring(True), 1, "collector"),
    "pod": (collector.pod, 1, "collector"),
    "pod_lid": (collector.pod_lid, 1, "collector"),
    "magnet_cap": (collector.magnet_cap, 1, "collector"),
    "servo_cradle": (robot.cradle, 1, "openarm_unit"),
    "servo_cradle_lid": (robot.cradle_lid, 1, "openarm_unit"),
    "horn_coupler": (robot.coupler, 1, "openarm_unit"),
    "cam_imx335_mount": (cameras.imx335_mount, 1, "cameras"),
    "cam_d405_cradle": (cameras.d405_cradle, 1, "cameras"),
}


def assembly(kind: str, opening: float, parts: dict) -> dict:
    xc = CLOSED_XC + opening / 2
    a = {"frame": parts["frame"], "pinion": parts["pinion"],
         "carriage_L": jm.carriage_pose(-xc, True), "carriage_R": jm.carriage_pose(xc, False)}
    ring_l = parts["finger_ring_thumb"]
    ring_r = parts["finger_ring_index"]
    if kind == "collector":
        a["ring_thumb"] = Pos(-xc, 0, 0) * ring_l
        a["ring_index"] = Pos(xc, 0, 0) * ring_r
        a |= {k: parts[k] for k in ("pod", "pod_lid", "magnet_cap", "cam_imx335_mount")}
    else:
        a |= {k: parts[k] for k in ("servo_cradle", "servo_cradle_lid", "horn_coupler", "cam_d405_cradle")}
        a["servo(envelope)"] = robot.servo_envelope()
    return a


def interferences(a: dict, tol=0.5):
    hits = []
    for (n1, p1), (n2, p2) in itertools.combinations(a.items(), 2):
        if {n1, n2} == {"pinion", "carriage_L"} or {n1, n2} == {"pinion", "carriage_R"}:
            continue  # mesh checked separately in umi.check
        try:
            v = (p1 & p2).volume
        except Exception:
            v = 0.0
        if v > tol:
            hits.append((n1, n2, round(v, 1)))
    return hits


def main(export=True):
    parts = {}
    for name, (fn, qty, group) in PARTS.items():
        p = fn()
        parts[name] = p
        bb = p.bounding_box()
        print(f"{name:20s} valid={p.is_valid} solids={len(p.solids())} vol={p.volume:8.0f} "
              f"size=({bb.size.X:.0f},{bb.size.Y:.0f},{bb.size.Z:.0f}) qty={qty}")
        if export:
            for sub in ("STEP", "STL"):
                (OUT / sub / group).mkdir(parents=True, exist_ok=True)
            export_step(p, str(OUT / "STEP" / group / f"{name}.step"))
            export_stl(p, str(OUT / "STL" / group / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.2)
    print(f"\nstroke {2 * TRAVEL:.0f} mm over {STROKE_DEG:.0f} deg of pinion rotation")
    bad = 0
    for kind in ("collector", "openarm_unit"):
        for opening in (0.0, 2 * TRAVEL):
            a = assembly(kind, opening, parts)
            hits = interferences(a)
            bad += len(hits)
            print(f"{kind:13s} open={opening:4.0f}mm  interferences: {hits or 'none'}")
            if export and opening == 2 * TRAVEL:
                (OUT / "STEP" / "assemblies").mkdir(parents=True, exist_ok=True)
                comp = Compound(children=[p for p in a.values()])
                export_step(comp, str(OUT / "STEP" / "assemblies" / f"{kind}_open.step"))
                (OUT / "STL" / "assemblies").mkdir(parents=True, exist_ok=True)
                export_stl(comp, str(OUT / "STL" / "assemblies" / f"{kind}_open.stl"), tolerance=0.05)
    return bad


if __name__ == "__main__":
    sys.exit(main(export="--no-export" not in sys.argv))
