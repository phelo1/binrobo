def mir(pl): return [(x, -y, z) for x, y, z in pl]
def uloop(xa, xb, y, zl, n=9):
    """hanging U-shaped loop of cable in the plane y: down at xa, round the bottom at height zl, up at xb"""
    r = abs(xa - xb) / 2; xc = (xa + xb) / 2; sg = 1 if xa > xb else -1
    return [(xc + sg * r * math.cos(math.pi * k / n), y, zl + r - r * math.sin(math.pi * k / n)) for k in range(n + 1)]
def lift_pts(st, pl):
    R, p = POSE[st]['lift']; return [tuple(R @ np.array(q, float) + p) for q in pl]
pz = (G['nib_h'] - G['pad_dz'])   # pad centre height in the lift frame (m)
def uloop_y(ya, yb, x, zl, n=9):
    """hanging U-shaped loop in the plane x: down at ya, round the bottom at height zl, up at yb"""
    r = abs(ya - yb) / 2; yc = (ya + yb) / 2; sg = 1 if ya > yb else -1
    return [(x, yc + sg * r * math.cos(math.pi * k / n), zl + r - r * math.sin(math.pi * k / n)) for k in range(n + 1)]
def looms(st):
    R, p = POSE[st]['lift']; Mv = R @ np.array([0.060, 0.07, 0.10]) + p; A = (0.475, 0.172, 1.10); zl = min(A[2], float(Mv[2])) - 0.22   # A: chain anchor on the mast, Mv: moving end on the carriage
    drvL = [(0.585, 0.125, 0.25), (0.585, 0.36, 0.25), (0.56, 0.36, 0.25), (0.56, 0.36, 0.425), (0.53, 0.398, 0.425), (-0.05, 0.398, 0.425), (-0.05, 0.42, 0.452)]
    encL = [(0.065, 0.398, 0.425), (0.065, 0.458, 0.425), (0.065, 0.458, 0.186)]   # over the rail and down the OUTER face of the motor plate, clear of the wheel
    rearL = [(0.572, 0.125, 0.232), (0.572, 0.346, 0.232), (0.546, 0.346, 0.232), (0.546, 0.346, 0.432), (0.53, 0.398, 0.432), (0.44, 0.398, 0.432), (0.42, 0.398, 0.385), (-0.33, 0.398, 0.385), (-0.372, 0.43, 0.40)]   # along the inner face of the rail, under the gearmotor
    rearL2 = [(-0.33, 0.398, 0.385), (-0.33, 0.398, 0.36), (-0.362, 0.40, 0.215)]
    return [
     ('L1', 'Battery power trunk', 'battery positive through the main fuse to the isolator key and the contactors in the power box; switched feed on to the pod', '2 x 10 mm2', (0.80, 0.10, 0.10), 0.008,
      [[(0.76, -0.022, 0.290), (0.76, 0.13, 0.290), (0.74, 0.20, 0.262), (0.74, 0.20, 0.25)], [(0.66, 0.17, 0.19), (0.66, 0.122, 0.19)]]),
     ('L2', 'Left drive loom', 'pod to left gearmotor and brake; sensor drop over the rail and down the outside of the motor plate', 'motor pair 6 mm2, brake pair, 2 signal cables', (1.00, 0.55, 0.00), 0.006, [drvL, encL]),
     ('L3', 'Right drive loom', 'as L2, mirrored', 'as L2', (1.00, 0.55, 0.00), 0.006, [mir(drvL), mir(encL)]),
     ('L4', 'Rear loom, left and right', 'pod along the inner face of each side rail, under the gearmotor, to rear bumper switches, leg-tip gap sensors, rear markers', 'stop-loop pair, sensor cable, lamp pair each side', (0.95, 0.82, 0.10), 0.006,
      [rearL, rearL2, mir(rearL), mir(rearL2)]),
     ('L5', 'Lift actuator loom', 'lift driver in the power box, up through the rear cover, to the actuator motor', 'motor pair 2.5 mm2', (0.55, 0.35, 0.20), 0.007,
      [[(0.66, 0.17, 0.24), (0.66, 0.145, 0.27), (0.66, 0.145, 0.325), (0.64, 0.03, 0.36)]]),
     ('L6', 'Mast-top loom', 'pod up the front of the right upright to rear camera, beacon, work lamp, marker, rear radar, microphone', 'USB cable, 4 lamp pairs, radar cable', (0.10, 0.70, 0.85), 0.007,
      [[(0.58, -0.06, 0.29), (0.58, -0.06, 0.325), (0.573, -0.185, 0.325), (0.573, -0.185, 1.385), (0.529, -0.17, 1.395), (0.529, 0.15, 1.395), (0.50, 0.15, 1.427)], [(0.529, 0.0, 1.395), (0.50, 0.0, 1.428), (0.46, 0.0, 1.437)],
       [(0.529, -0.11, 1.395), (0.529, -0.11, 1.428), (0.47, -0.11, 1.428), (0.458, -0.11, 1.41)], [(0.529, -0.15, 1.395), (0.50, -0.15, 1.427)], [(0.529, 0.082, 1.395), (0.529, 0.082, 1.428), (0.474, 0.082, 1.428), (0.462, 0.082, 1.418)]]),
     ('L7', 'Carriage loom', 'pod up the front of the left upright to a cable chain anchored on the mast; one hand-off on the carriage, then to the 2 comb distance sensors, comb, nib and pad switches. Also the lift top limit switch', '3 sensor cables, 4 switch pairs', (0.15, 0.35, 0.90), 0.006,
      [[(0.58, 0.06, 0.29), (0.58, 0.06, 0.325), (0.573, 0.185, 0.325), (0.573, 0.185, 1.10), (0.573, 0.172, 1.10), A], [(0.573, 0.185, 1.10), (0.573, 0.185, 1.313), (0.573, 0.231, 1.313), (0.482, 0.231, 1.313)],
       [A] + uloop_y(A[1], 0.07, A[0], zl) + [tuple(Mv)],
       lift_pts(st, [(0.060, 0.07, 0.10), (0.047, 0.07, 0.10), (0.047, 0.07, -0.08), (-0.006, 0.07, -0.08), (-0.006, 0.18, -0.08), (-0.006, 0.18, -0.022)]), lift_pts(st, [(-0.006, 0.07, -0.08), (-0.006, -0.18, -0.08), (-0.006, -0.18, -0.022)]),
       lift_pts(st, [(0.047, 0.07, 0.10), (0.047, 0.115, 0.025), (0.002, 0.115, 0.025)]), lift_pts(st, [(-0.006, 0.07, -0.08), (-0.06, 0.06, -0.04), (-0.122, 0.06, -0.04), (-0.122, 0.02, -0.018)]),
       lift_pts(st, [(-0.006, 0.13, -0.08), (-0.006, 0.13, pz + 0.05), (-0.10, 0.16, pz + 0.05), (-0.115, 0.16, pz + 0.02)])]),
     ('L8', 'Sensor-post loom', 'pod along the bay floor and up the post to lidar, front camera, GNSS, LTE antenna, front radar, horn', 'lidar cable, USB cable, 2 coax, radar cable, speaker pair', (0.60, 0.25, 0.80), 0.007,
      [[(0.72, 0.10, 0.24), (0.905, 0.10, 0.24), (0.905, 0.10, 0.425), (0.955, 0.06, 0.425), (1.0, 0.028, 0.45), (1.0, 0.028, 1.05)], [(1.0, 0.028, 0.815), (1.03, 0.02, 0.815)], [(1.0, 0.028, 0.725), (1.02, 0.03, 0.725)],
       [(1.0, 0.028, 0.58), (1.02, 0.02, 0.58)], [(1.0, 0.028, 0.47), (1.025, 0.024, 0.47)]]),
     ('L9', 'Nose loom', 'pod up behind the castor beam, along the nose cross-member to the headlights, down between the castors and under the bumper to its switches and the charge contacts. The charge pair runs back to the 10 A fuse in the power box', 'stop-loop pair, 2 lamp pairs, charge pair 2.5 mm2', (0.10, 0.62, 0.28), 0.007,
      [[(0.72, -0.10, 0.24), (0.905, -0.10, 0.24), (0.905, -0.10, 0.425), (0.955, -0.10, 0.425), (1.003, -0.10, 0.385)], [(1.003, -0.30, 0.385), (1.003, 0.30, 0.385)],
       [(1.003, 0.12, 0.385), (1.105, 0.12, 0.30), (1.105, 0.12, 0.118), (1.158, 0.12, 0.118), (1.158, 0.12, 0.142)], [(1.003, -0.12, 0.385), (1.105, -0.12, 0.30), (1.105, -0.12, 0.118), (1.158, -0.12, 0.118), (1.158, -0.12, 0.142)]]),
     ('L10', 'Operator-controls loom', 'pod to E-stop and reset button', '2 stop-loop pairs, lamp and button pairs', (0.90, 0.20, 0.60), 0.006,
      [[(0.64, -0.12, 0.275), (0.64, -0.30, 0.275), (0.64, -0.30, 0.302)], [(0.60, -0.12, 0.275), (0.60, -0.23, 0.275), (0.60, -0.23, 0.302)]]),
     ('L11', 'Safety and control loom', 'pod to power box: the two contactor coils from the safety relay, the contactor feedback contacts, switched-feed voltage sense, lift up and down commands', '2 coil pairs, feedback pair, sense pair, 2 command pairs', (0.95, 0.40, 0.70), 0.006,
      [[(0.70, 0.122, 0.215), (0.70, 0.17, 0.215)]]),
    ]
