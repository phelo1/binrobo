#!/usr/bin/env python3
"""[tester 2026-11-14] MuJoCo version probe: a free-rolling 200 mm castor wheel (cylinder r 0.10, 50 mm wide, axle on x/z slides,
30 kg) pushed at 0.10 m/s by a force-capped velocity servo (cap F) into a sharp 40 mm box step. Rigid-body answer: it climbs when F > W tan(theta),
cos(theta) = (r-h)/r -> tan 1.333 -> 392 N for 30 kg. Same contact settings as the gate (solref 0.008, solimp 0.9 0.99, elliptic, noslip 3, dt 0.5 ms).
Also a drive-wheel case: r 0.165 (330 mm) wheel, 40 mm step -> tan(theta) = 0.86 (cos 0.758)."""
import mujoco, numpy as np, sys, json
def run(F, r=0.10, h=0.040, m=30.0, mu=0.6, geom='cylinder'):
    sz = f'{r} 0.025' if geom=='cylinder' else f'{r}'
    xml=f'''<mujoco><option timestep="0.0005" cone="elliptic" noslip_iterations="3"/>
<default><geom solref="0.008 1" solimp="0.9 0.99 0.001" friction="{mu} 0.005 0.0001"/></default>
<worldbody><geom name="floor" type="plane" size="5 5 0.1"/><geom name="step" type="box" pos="1.5 0 {h/2}" size="1.0 1 {h/2}"/>
<body name="axle" pos="{0.5-r-0.03} 0 {r}"><joint name="x" type="slide" axis="1 0 0"/><joint name="z" type="slide" axis="0 0 1"/><inertial mass="{m}" pos="0 0 0" diaginertia="0.1 0.1 0.1"/>
<body name="w"><joint name="spin" type="hinge" axis="0 1 0" damping="0.0"/><geom type="{geom}" size="{sz}" euler="90 0 0" mass="1"/></body></body></worldbody>
<actuator><velocity name="push" joint="x" kv="20000" forcelimited="true" forcerange="-{F} {F}"/></actuator></mujoco>'''
    M=mujoco.MjModel.from_xml_string(xml); D=mujoco.MjData(M); b=M.body('axle').id
    zmax=0.0; nmax=0.0
    for i in range(int(4.0/M.opt.timestep)):
        D.ctrl[0]=0.10 if D.time>0.2 else 0.0
        mujoco.mj_step(M,D); zmax=max(zmax,D.qpos[1])
        if D.qpos[0]>0.25: break
    # contact normal angle at the step during the push (deg from horizontal), last sample
    return dict(F=F,climbed=bool(D.qpos[1]>h-0.003),z_rise_mm=round(1000*zmax,1),dx=round(float(D.qpos[0]),3))
if __name__=='__main__':
    out=dict(version=mujoco.__version__,castor=[],drive=[])
    for F in (300,360,380,400,420,450,600,1000):
        out['castor'].append(run(F))
    for F in (300,400,420,440,460,500,700,1000):
        out['drive'].append(run(F,r=0.165,m=50.0))
    print(json.dumps(out))
