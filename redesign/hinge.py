"""Camera pose and mounting shared by the main support, the D405 cradle and the assembly.

The D405 cradle bolts rigidly to the underside of the main support (no hinge). The camera sits in front of the servo
and looks straight at the base of the gripper fingers (~79 mm away).
Main-support frame (M): rods along Y, tips toward -X, hand toward +Z (in use -Z is up).
Camera frame: cup floor outer face at z = 0, D405 centred on (0, 0), looking along +z.
"""
import numpy as np

CENTRE_M = (-60.0, 72.5, -48.0)     # D405 optical centre, in front of the servo and clear of the plate edge
TARGET_M = (-55.0, 72.5, 30.5)      # what the optical axis points at: the base of the gripper fingers (tip flanges)
                                    # (distance ~79 mm; the D405 minimum range is 70 mm)
OPTICAL_CAM = (0.0, 0.0, 23.0)      # D405 optical centre in the camera frame (front face)
MOUNT_BOLTS = [(-34.0, 66.0), (-34.0, 79.0)]   # M3 through the servo boss (counterbored, heads flush on the top face)
INSERT_D, INSERT_DEPTH = 4.0, 6.0               # M3 heat-set inserts in the cradle base


def camera_pose():
    """Rotation and translation taking camera-frame points into the main-support frame."""
    v = np.array(TARGET_M) - np.array(CENTRE_M)
    a = np.arctan2(v[2], -v[0])                               # view angle below horizontal (toward -X)
    base = np.array([[0, 0, -1], [1, 0, 0], [0, -1, 0]], float)   # cam x -> +Y, cam y -> -Z, cam z (view) -> -X
    tilt = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    R = tilt @ base
    t = np.array(CENTRE_M) - R @ np.array(OPTICAL_CAM)
    return R, t
