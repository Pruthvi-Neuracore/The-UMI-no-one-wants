"""All driving dimensions (mm). Frame: X = jaw travel, Y = approach (+Y toward tips), Z = up.

Origin is the pinion axis in the jaw-module mid-plane. Anything marked VERIFY was not taken
from a datasheet or measured CAD and must be test-fitted before a print run.
"""
from math import pi

# --- printing ---
CLR = 0.25          # sliding / slip clearance per side
PRESS = -0.05       # press-fit allowance on diameter

# --- guide rods + linear bearings (Ø6 rod, LM6UU: 6 x 12 x 19) ---
ROD_D = 6.0
ROD_Z = 18.0        # rods at z = ±ROD_Z, y = 0
LMU_OD, LMU_L = 12.0, 19.0

# --- rack & pinion (synchronises the jaws; width is linear in pinion angle) ---
GEAR_M = 1.25
PINION_Z = 16
PITCH_R = GEAR_M * PINION_Z / 2          # 10 mm -> 20 mm of total width per radian
GEAR_FACE = 8.0
GEAR_BACKLASH = 0.3                       # removed from rack tooth thickness (printing)
GEAR_Y = -16.0                            # pinion / rack mid-plane (behind the carriages)
RACK_BODY = 5.0                           # rack backbone thickness behind tooth roots

# --- carriages ---
CAR_W = 24.0                              # along X
CAR_Y0, CAR_Y1 = -8.0, 10.0               # back face, tip face
CAR_Z = 26.0                              # carriage spans z = ±CAR_Z (2 mm wall over LM6UU)
CLOSED_XC = CAR_W / 2 + 2.0               # carriage centre at fully closed (2 mm gap/side)
TRAVEL = 40.0                             # per jaw -> 80 mm total stroke
OPEN_XC = CLOSED_XC + TRAVEL
RACK_LEN = TRAVEL + CAR_W + 2 * PITCH_R   # keeps the mesh engaged over the full stroke

# --- HandUMI-compatible tip interface (4x M2, 8 along X x 12 along Z, axis = +Y) ---
TIP_DX, TIP_DZ, TIP_HOLE = 8.0, 12.0, 2.2
M2_NUT_AF, M2_NUT_T = 4.0, 1.6

# --- frame ---
WALL = 4.0
END_T = 8.0
FRAME_X = OPEN_XC + CAR_W / 2 + 2.0       # inner face of the end blocks
FRAME_Y0, FRAME_Y1 = GEAR_Y - GEAR_FACE / 2 - 2.0 - WALL, CAR_Y1   # back-plate rear face, front
FRAME_Z = CAR_Z + 2.0
TOP_T = 4.0

# --- pinion shaft (Ø5 dowel in a 685ZZ 5x11x5 bearing) ---
SHAFT_D = 5.0
BRG_OD, BRG_W = 11.0, 5.0

# --- camera dock: 4x M3 heat-set inserts on a 20 x 20 square, top of frame ---
DOCK_PITCH = 20.0
DOCK_Y = (FRAME_Y0 + FRAME_Y1) / 2
M3_INSERT_D = 4.0     # VERIFY against your insert brand
M3_CLR = 3.4

# --- electronics (collector pod) ---
PICO_L, PICO_W = 51.0, 21.0               # Raspberry Pi Pico / Pico 2 outline
PICO_HOLES = (47.0, 11.4)                 # 4x Ø2.1 mounting holes
IMU_POCKET = (28.0, 23.0, 5.0)            # BNO085 breakout; sellers disagree on outline -> VERIFY
ENC_POCKET = (24.0, 24.0, 4.0)            # AS5600 breakout -> VERIFY
MAGNET_D, MAGNET_T = 6.0, 2.5             # diametric magnet on the pinion shaft

# --- Feetech STS3215 (envelope measured from SO-ARM100 STS3215_03a.step) ---
STS_BODY = (45.4, 24.8, 35.0)             # x, y, z with output axis along +z
STS_SHAFT_OFFSET = 12.5                   # output axis offset from body centre along x

# --- finger cradles (collector) ---
THUMB_ID = 24.0
INDEX_ID = (22.0, 40.0)                   # index + middle, oval
RING_W = 14.0
RING_T = 3.0
THUMB_RING_Y, INDEX_RING_Y = -7.0, 9.5   # ring centres in Y, staggered so they pass at full close

# --- YUBI_ATTACHMENT gripper-side interface (measured from yubi-hw STEP) -> VERIFY face ---
YUBI_M3 = [(-13.5, 28.8), (-13.5, -28.8), (10.0, 22.0), (10.0, -22.0)]
YUBI_PINS = [(-9.5, 16.5), (-9.5, -16.5)]   # Ø3 locating pins

# --- Intel RealSense D405: 42 x 42 x 23, 1/4-20 tripod thread on the base ---
D405 = (42.0, 23.0, 42.0)                  # width (x), depth (y), height (z)


def width_from_angle(theta_rad: float) -> float:
    """Jaw opening (carriage-centre spacing change) for a pinion rotation from closed."""
    return 2 * PITCH_R * theta_rad


STROKE_DEG = TRAVEL / PITCH_R * 180 / pi

# --- rear module interface (pod on the collector, servo cradle on the robot): 4x M3 on back plate ---
REAR_MOUNTS = [(sx * 30.0, sz * 16.0) for sx in (-1, 1) for sz in (-1, 1)]   # (x, z)

# --- camera pose: both adapters put the optical centre here, looking +Y pitched down ---
CAM_CENTER = (0.0, -8.0, 76.0)
CAM_TILT = 40.0                     # deg below horizontal; aims at the fingertips
IMX335_BOARD, IMX335_HOLES, IMX335_LENS = 38.0, 34.0, 16.0   # LENS Ø -> VERIFY

# --- robot unit: STS3215 horn coupling ---
HORN_PCD, HORN_HOLE, HORN_N = 14.0, 2.6, 4   # VERIFY against the horn shipped with your servo
