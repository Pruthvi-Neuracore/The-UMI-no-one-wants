"""Camera hinge shared by the redesigned main support (centre knuckle) and the D405 wrist mount (outer lugs).

Main-support frame (M): hinge axis along Y at (x, z) = AXIS_M, centred at y = 72.5.
Camera-mount frame: hinge axis along X at (y, z) = AXIS_CAM, centred at x = 0.
"""
AXIS_M = (-29.7, -45.0)        # same pivot location as HandUMI, so the camera pose is unchanged
AXIS_CAM = (-29.5, 1.5)        # 1.25 mm further from the cup than HandUMI, to clear the Ø12 knuckles
Y_CENTRE = 72.5
KNUCKLE_OD = 12.0              # HandUMI: Ø8
CENTRE_W = 10.0                # main-support knuckle width (HandUMI: 5.8)
LUG_W = 6.0                    # each camera lug (HandUMI: 4.5)
GAP = 0.2                      # axial clearance per side
BOLT_D = 4.4                   # M4 clearance (HandUMI: M3); use an M4 x 30 bolt + nyloc nut
