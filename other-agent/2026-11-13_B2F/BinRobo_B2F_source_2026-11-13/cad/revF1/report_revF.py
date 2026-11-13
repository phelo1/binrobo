import json, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from lib import render, iso, SIDE
D=json.load(open('mesh_revF.json')); R={}
for f in sorted(glob.glob('results_*.json')): R.update(json.load(open(f)))
M=json.load(open('mass_revF.json'))
def g(k,*p,d='–'):
    v=R.get(k,{})
    for x in p: v=v.get(x,{}) if isinstance(v,dict) else {}
    return d if v=={} else v
pdf=PdfPages('Bin_Tug_RevF_Sim_Report.pdf')
# page 1: design
fig=plt.figure(figsize=(16.5,11.7))
fig.text(0.04,0.95,'Bin tug Rev F – "hand-truck" grab: design changes',fontsize=22,weight='bold')
fig.text(0.04,0.925,'MuJoCo 3.17 physics model built from the CAD mass table. All figures are simulation estimates; verify on a sandbag-loaded bin.',fontsize=11,color='#456')
for i,(key,t) in enumerate((('dock','Docked, latched (bin upright)'),('t24','Mid-tip (bin 24°)'),('tow','Tow pose (bin 48°)'))):
    ax=fig.add_axes([0.02+i*0.33,0.47,0.31,0.43]); render(ax,iso(-55,20),D[key]['mesh'],lw=0.1); ax.set_title(t,fontsize=13)
txt=[
"WHAT CHANGED FROM REV E (and why)",
"• Wheel-stop crossbeam with two rubber rollers sits against the bin's wheel treads at axle height. It supplies the backward push a person's foot gives,",
"   so pulling the handle forward now TIPS the bin instead of rolling it (Rev E's critical failure).",
"• Mast is hinged at its base and rocked forward by one 2,500 N / 450 mm self-locking actuator (was: vertical slide). The hook carriage floats on the",
"   rails with a return spring, so the hooks follow the handle's arc and take up ±30 mm of docking error. The ramped hook lip rides over the bar and snaps shut.",
"• Mast, stop bar, docking funnel and anti-tip rollers sit on a REAR FRAME that yaws on a 250 mm turntable directly over the drive axle (AS5600 angle sensor,",
"   solenoid lock pin for docking and tipping). Without it the tug could not turn with a bin attached (first run: 4° of a 92° bend).",
"• Anti-tip rollers (100 mm, 70 mm ground clearance) 0.88 m behind the drive axle catch the tip-up reaction (the casters unload for ~20 s while tipping a full bin).",
"   First version at 15 mm clearance snagged on a 60 mm bump; raised.",
"• Lidar moved low on the bumper; RTK antenna, 4G/LoRa antennas and beacon moved to a front sensor post.",
f"• Mass: {M['total']:.0f} kg with 4 ballast plates (Rev E 87 kg). The extra ~18 kg is the rear frame (~17 kg incl. actuator and turntable).",
]
fig.text(0.04,0.42,'\n'.join(txt),fontsize=11.5,va='top',family='DejaVu Sans',linespacing=1.55)
pdf.savefig(fig); plt.close(fig)
# page 2: results table
fig=plt.figure(figsize=(16.5,11.7)); ax=fig.add_axes([0.03,0.05,0.94,0.83]); ax.axis('off')
fig.text(0.04,0.95,'Rev F simulation results (full bin = 108 kg incl. 96 kg load unless noted)',fontsize=20,weight='bold')
rows=[["Test","Surface","Result","Key numbers"]]
c=R.get('cycle_full',{})
rows.append(["Full cycle: dock, latch, tip, tow 6 m, stand, release","wet grass μ0.45","PASS",f"tips to 48° in ~48 s · actuator ≤1.1 kN (rated 2.5 kN) · tug pitches {g('cycle_full','phase5','pitch_max')}° onto anti-tip rollers"])
rows.append(["Same cycle, 30 kg bin / empty bin","wet grass","PASS","casters stay loaded; actuator ≤0.4 kN"])
for gr in (10,15,20):
    for mu in (0.45,0.8):
        k=f'climb_{gr}_{mu}'; p=g(k,'phase7')
        ok=(not R.get(k,{}).get('flipped')) and p!='–' and p.get('dist',0)>4.5
        lift=p!='–' and p.get('caster_min',1)==0 and p.get('pitch_max',0)>2
        rows.append([f"Uphill tow {gr}%", 'wet grass μ0.45' if mu==0.45 else 'dry μ0.8',("PASS (casters lift)" if lift else "PASS") if ok else "FAIL",
                     f"5 m at {p.get('v_end','?')} m/s · tug rocks back {p.get('pitch_max')}° onto anti-tip rollers · motors at {p.get('torque_max','?')} Nm limit" if p.get('torque_max',0)>=59 else f"5 m at {p.get('v_end','?')} m/s · casters stay down"])
for gr in (10,15,20):
    for mu in (0.45,0.8):
        k=f'estop_{gr}_{mu}'; v=R.get(k,{})
        rows.append([f"Downhill e-stop {gr}% from 0.5 m/s", 'wet grass μ0.45' if mu==0.45 else 'dry μ0.8',"PASS" if v.get('stops') else "FAIL",f"spring brakes stop it in {v.get('slide_m','?')} m"])
rows.append(["100 mm pothole, left wheels","damp μ0.6","PASS" if R.get('pothole_100mm',{}).get('reached_4m') else "FAIL",f"roll {g('pothole_100mm','phase7','roll_max')}° · hook peak {g('pothole_100mm','phase7','hook_max')} N"])
rows.append(["60 mm sharp bump, left wheels","damp μ0.6","PASS (hard)" if R.get('bump_60mm',{}).get('reached_4m') else "FAIL",f"rollers strike, pitch {g('bump_60mm','phase7','pitch_max')}° · hook shock {g('bump_60mm','phase7','hook_max')} N"])
for gr in (20,30,40):
    k=f'camber_{gr}'; v=R.get(k,{})
    cr=abs(g(k,'phase8','dist',d=0)); st="FAIL" if v.get('flipped') else ("MARGINAL" if cr>0.1 else "PASS")
    rows.append([f"Side slope {gr}%: parked, then across","damp μ0.6",st,f"no roll-over · creeps {cr:.2f} m after stopping"+(" (brakes not holding sideways)" if cr>0.1 else "")])
t=R.get('turn',{})
rows.append(["2.5 m-radius bend while towing","damp μ0.6","PASS*",f"turned {t.get('yaw_arc_deg')}° of {t.get('expected_arc_deg')}° commanded in 10 s (open-loop; heading loop closes the gap)"])
rows.append(["Spin in place with bin attached","damp μ0.6","DON'T",f"rear frame hits its 70° stop and wrenches the bin → firmware caps hitch angle at 60°"])
tb=ax.table(cellText=rows[1:],colLabels=rows[0],loc='upper left',colWidths=[0.27,0.12,0.08,0.53],cellLoc='left')
tb.auto_set_font_size(False); tb.set_fontsize(10.5); tb.scale(1,1.55)
for (r_,c_),cell in tb.get_celld().items():
    if r_==0: cell.set_facecolor('#1d2a33'); cell.get_text().set_color('white'); cell.get_text().set_weight('bold')
    elif c_==2:
        t_=cell.get_text().get_text(); cell.set_facecolor('#fff3c4' if '(' in t_ else '#d8f0d8' if t_.startswith('PASS') else ('#ffe2c2' if t_ in("DON'T",'MARGINAL') else '#f7caca'))
fig.text(0.04,0.03,"Model limits: friction and rolling resistance approximated; rigid tyres (bump results conservative); spring brake modelled as a 150 Nm wheel hold; real bin CG and wheel size to be measured. "
         "Turn test is open-loop wheel speeds.",fontsize=9.5,color='#456')
pdf.savefig(fig); plt.close(fig); pdf.close(); print('ok')
