#!/usr/bin/env python3
"""Minimal check of how a MuJoCo version treats a cylinder wheel on a sharp 40 mm box edge (my own model, not the other agent's code).
Same contact settings as their gate: implicitfast, elliptic cone, noslip 3, solref 0.008 1, solimp 0.9 0.99 0.002, friction 0.6, dt 0.0005.
A: contact normal when the wheel rests against the corner (physically it must point from the corner to the wheel centre, 40.7 deg from vertical).
B: one driven wheel carrying 78 kg (half the loaded drive-axle load), speed servo 0.5 m/s, torque cap 60 N m: does it get over?"""
import mujoco, numpy as np, math, json, sys
R, H, MU = 0.165, 0.040, 0.6
XML = f'''<mujoco><option timestep="0.0005" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic" noslip_iterations="3"/>
<default><geom solref="0.008 1" solimp="0.9 0.99 0.002"/></default>
<worldbody><geom name="ground" type="plane" size="20 20 0.1" friction="{MU}" condim="3"/>
<geom name="step" type="box" pos="2.0 0 {H/2}" size="1.0 1.0 {H/2}" friction="{MU}" condim="3"/>
<body name="w" pos="0 0 {R}"><joint name="x" type="slide" axis="1 0 0"/><joint name="z" type="slide" axis="0 0 1"/><joint name="spin" type="hinge" axis="0 1 0"/>
<inertial pos="0 0 0" mass="78" diaginertia="0.6 0.6 0.6"/><geom name="wheel" type="cylinder" size="{R} 0.03" euler="90 0 0" friction="{MU}" condim="3"/></body></worldbody>
<actuator><motor name="m" joint="spin" gear="1" ctrlrange="-60 60" ctrllimited="true"/></actuator></mujoco>'''
m = mujoco.MjModel.from_xml_string(XML); d = mujoco.MjData(m)
gid = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, n)
# A: wheel touching the corner with 1 mm of overlap
xc = 1.0 - math.sqrt(R * R - (R - H) ** 2) + 0.001
d.qpos[:] = [xc, 0.0, 0.0]; mujoco.mj_forward(m, d); normals = []
for i in range(d.ncon):
    c = d.contact[i]
    if {c.geom1, c.geom2} == {gid('wheel'), gid('step')}:
        n = np.array(c.frame[:3]); ang = math.degrees(math.atan2(abs(n[0]), abs(n[2]))); normals.append(round(ang, 1))
# B: drive at it
mujoco.mj_resetData(m, d); d.qpos[:] = [0.3, 0.0, 0.0]; d.qvel[:] = [0.5, 0.0, 0.5 / R]; t_over = None
for k in range(int(8.0 / m.opt.timestep)):
    v_wheel = d.qvel[2] * R; d.ctrl[0] = float(np.clip(150.0 * (0.5 - v_wheel), -60, 60)); mujoco.mj_step(m, d)
    if t_over is None and d.qpos[0] > 1.2 and d.qpos[1] > H - 0.005: t_over = round(d.time, 2)
print(json.dumps(dict(mujoco=mujoco.__version__, expected_normal_deg=round(math.degrees(math.acos((R - H) / R)), 1), contact_normal_deg_from_vertical=normals, wheel_got_over=t_over is not None, t_over_s=t_over, x_end=round(float(d.qpos[0]), 2), z_rise_end_mm=round(float(d.qpos[1]) * 1000, 1))))
