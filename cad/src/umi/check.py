"""Interference checks for the jaw module over the full stroke."""
import sys
from math import degrees

from build123d import Rot

from .jaw_module import carriage_pose, frame, pinion
from .params import CLOSED_XC, PITCH_R, TRAVEL


def overlap(a, b):
    try:
        return (a & b).volume
    except Exception:
        return 0.0


def main(steps=5, tol=1.0):
    fr, pn = frame(), pinion()
    bad = 0
    for i in range(steps + 1):
        d = TRAVEL * i / steps
        xc = CLOSED_XC + d
        left, right = carriage_pose(-xc, True), carriage_pose(xc, False)
        theta = d / PITCH_R
        # best pinion phase: search a tooth pitch for minimal overlap with both racks
        def mesh(ph):
            p = Rot(0, degrees(-theta) + ph, 0) * pn
            return overlap(p, left) + overlap(p, right)
        coarse = min((mesh(k * 1.5), k * 1.5) for k in range(15))        # one tooth pitch = 22.5°
        best = min((mesh(coarse[1] + k * 0.25), 0) for k in range(-6, 7))
        rows = {"frame-left": overlap(fr, left), "frame-right": overlap(fr, right),
                "left-right": overlap(left, right), "pinion-racks": best[0]}
        flag = [k for k, v in rows.items() if v > tol]
        bad += bool(flag)
        print(f"open={2 * d:5.1f}mm  " + "  ".join(f"{k}={v:6.1f}" for k, v in rows.items())
              + (f"  <-- {flag}" if flag else ""))
    return bad


if __name__ == "__main__":
    sys.exit(main())
