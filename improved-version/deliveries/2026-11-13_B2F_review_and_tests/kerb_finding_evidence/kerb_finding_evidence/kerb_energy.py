#!/usr/bin/env python3
"""Hand check: energy barrier for two rigid drive wheels (r 165 mm) to roll over a sharp edge about its corner, with friction mu at the corner and a torque cap.
Wheel centre moves on an arc of radius r about the corner; along the arc the driving friction is min(mu*N, 2*Tcap/r) with N ~ W cos(theta); gravity resists with W sin(theta)."""
import numpy as np, math, json
def barrier(W, r, h, mu, tcap):
    th0 = math.acos((r - h) / r); th = np.linspace(th0, 0, 4000); F = np.minimum(mu * W * np.cos(th), 2 * tcap / r); net = W * np.sin(th) - F   # resisting minus driving
    work = np.cumsum(net[:-1] * r * (-(np.diff(th))))                    # energy the robot must supply from momentum, cumulative
    return math.degrees(th0), float(max(work.max(), 0.0)), math.tan(th0)
out = []
for h in (0.040, 0.050, 0.060):
    for W, lab in ((1536.0, 'full 240 L, drive axle 1,536 N'), (455.0, 'empty robot, drive axle 455 N')):
        a, b, mu_static = barrier(W, 0.165, h, 0.6, 60.0); m = 202.3 if W > 1000 else 92.3
        ke = 0.5 * m * 0.5 ** 2; ke_after = ke * math.cos(math.radians(a)) ** 2
        out.append(dict(edge_mm=round(h * 1000), load=lab, contact_angle_deg=round(a, 1), friction_needed_from_rest=round(mu_static, 2), barrier_J=round(b, 1), kinetic_J_at_0p5=round(ke, 1), kinetic_J_after_impact_est=round(ke_after, 1), passes_on_energy=ke_after > b))
for o in out: print(o)
json.dump(out, open('kerb_energy.json', 'w'), indent=1)
