# Rev F.1 report: optimisation study, chosen changes, before/after, recovery decision tree + sim results, cost delta, risks.
import json, glob, os, textwrap, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
S={}
for f in glob.glob('study/*__*.json'):
    d=json.load(open(f)); S[(d['variant'],d['test'])]=d
RC={os.path.basename(f)[9:-5]:json.load(open(f)) for f in glob.glob('study/recovery_*.json')}
def st(v,t,*k,d='–'):
    x=S.get((v,t))
    if x is None: return d
    for kk in k:
        if not isinstance(x,dict) or kk not in x: return d
        x=x[kk]
    return x
W,H=16.5,11.7; NAVY='#1d2a33'; BLUE='#0b5d8f'; GREY='#456'
def page(title,sub=None):
    fig=plt.figure(figsize=(W,H)); fig.text(0.04,0.955,title,fontsize=21,weight='bold',color=NAVY)
    if sub: fig.text(0.04,0.927,sub,fontsize=11,color=GREY)
    fig.text(0.96,0.02,'Bin tug Rev F.1 · MuJoCo sim study · figures are simulation estimates',fontsize=8.5,color='#889',ha='right')
    return fig
def table(ax,rows,colw,fs=10,scale=1.45,head=NAVY,colorcol=None,wrap=None):
    if wrap:
        rows=[[textwrap.fill(str(c),wrap[j]) if wrap[j] else str(c) for j,c in enumerate(r)] for r in rows]
    tb=ax.table(cellText=rows[1:],colLabels=rows[0],loc='upper left',colWidths=colw,cellLoc='left')
    tb.auto_set_font_size(False); tb.set_fontsize(fs); tb.scale(1,scale)
    nl={}
    for (r,c),cell in tb.get_celld().items(): nl[r]=max(nl.get(r,1),cell.get_text().get_text().count('\n')+1)
    for (r,c),cell in tb.get_celld().items():
        cell.set_height(cell.get_height()*(0.45+0.55*nl[r]))
        cell.set_edgecolor('#b8c2c8')
        if r==0: cell.set_facecolor(head); cell.get_text().set_color('white'); cell.get_text().set_weight('bold')
        elif colorcol is not None: colorcol(r,c,cell)
    return tb
def para(fig,x,y,lines,fs=11.5,ls=1.5,width=None,**kw):
    out=[]
    for l in lines:
        if width and len(l)>width:
            ind='   ' if l.startswith('•') else ''
            out+= textwrap.wrap(l,width,subsequent_indent=ind)
        else: out.append(l)
    fig.text(x,y,'\n'.join(out),fontsize=fs,va='top',linespacing=ls,**kw)
pdf=PdfPages('Bin_Tug_RevF1_Report.pdf')
# ---------------- page 1: verdict + chosen changes + cost
fig=page('Bin tug Rev F.1 – optimisation of Rev F and bin-recovery strategy','Brian · Nov 2026 · same MuJoCo model as Rev F (CAD mass table, 0.5 ms step), corrected and extended. All numbers are simulation estimates.')
if os.path.exists('frames/hero.png'):
    ax=fig.add_axes([0.53,0.50,0.44,0.40]); ax.imshow(plt.imread('frames/hero.png')); ax.axis('off'); ax.set_title('Rev F.1 towing (sim frame)',fontsize=11)
c1=st('F1','cycle'); 
verdict=[
"VERDICT",
"• Rev F's architecture is the right one for an unmodified wheelie bin: the optimum is a TUNED Rev F, not a new concept.",
"• It cannot get lighter. On 20% wet grass (μ 0.45) only the ~105 kg versions made the climb; the 101, 97 and 86 kg versions stalled. Traction sets the mass, so the 4 ballast plates stay. Moving them forward is what helps.",
"• Chain 4WD buys nothing on the climb (uphill the casters are off the ground ~90% of the time), so it is not worth the cost.",
"• A 48° tow tilt is best. At 35–40° it stalled on the 20% climb and the e-stop distance grew 1.5–2.3×.",
"• Rev F's '60 mm bump' test was really a 30 mm step. At a true 60 mm Rev F gets stuck (the caster climbs, the rollers ground, the drive wheels lift). F.1 gets over, but roughly, so fixed sharp steps on the lane should get a rubber ramp.",
"",
"REV F.1 CHANGES (all small)",
"1  Ballast plates moved forward from +0.56 m to +0.70 m (same 4 plates, 17.3 kg).",
"2  Anti-tip rollers raised from 70 to 100 mm clearance, so the tug can't high-centre when a caster climbs a 60 mm step.",
"3  Casters moved 100 mm forward (longer outriggers): better pitch stability and shorter e-stops.",
"4  Rubber bush in the hook carriage mount (2–3 mm give): cuts the peak spikes in hook load.",
"5  Firmware: soft stop (ramp down, then brake), closed-loop P control of heading, and a 60° cap on the hitch angle.",
"6  Recovery: AprilTags on the bin's front and back, plus nudge / re-dock / alert logic. Uses the existing bumper and cameras.",
]
para(fig,0.04,0.89,verdict,fs=11.2,ls=1.45,width=84)
cost=[["Change","€ (est.)","Mass"],["Ballast re-position (bracket, holes, bolts)","5–15","0"],["Anti-tip bracket re-made 30 mm higher","0–10","0"],
      ["Caster outriggers +100 mm (5 mm plate)","10–25","+0.6 kg*"],["Rubber–metal hook bushes ×2","8–20","+0.1 kg"],["Firmware: soft stop, heading loop, hitch cap","0","0"],
      ["AprilTags ×2 (outdoor vinyl) + bumper nudge face","5–25","+0.3 kg"],["Total F.1 delta","€30–95","≈ +1 kg"]]
ax=fig.add_axes([0.53,0.17,0.44,0.27]); ax.axis('off')
def cc(r,c,cell):
    if r==7: cell.set_facecolor('#e8f1f7'); cell.get_text().set_weight('bold')
table(ax,cost,[0.66,0.18,0.16],fs=10,scale=1.6,colorcol=cc)
fig.text(0.53,0.135,'Whole tug:  Rev F  €670–1,030 used / €920–1,430 new\n                 Rev F.1  €700–1,125 used / €950–1,525 new',fontsize=10.5,weight='bold',color=NAVY,va='bottom')
fig.text(0.53,0.100,'Optional site work: a rubber kerb ramp at any sharp step of 50 mm or more on the lane, €15–40 each.',fontsize=10,color=NAVY)
fig.text(0.53,0.075,'* extra outrigger steel was not added to the sim mass (≈0.6% of the total). Prices are rough € estimates.',fontsize=8.5,color=GREY)
pdf.savefig(fig); plt.close(fig)
# ---------------- page 2: study table
fig=page('Optimisation study: one change at a time from Rev F, then combined','Each variant: full grab, then the 20% wet climb (5 m in 25 s), a true 60 mm sharp step under the left wheels (μ 0.6), and a 20% downhill e-stop. Full bin, 108 kg.')
order=['F0','Bfwd','B3fwd','B2fwd','Light','D4','Clong','AT100','T40','T35','Hsoft','F1a','F1b','F1']
name={'F0':'Rev F baseline','Bfwd':'Ballast fwd (+0.70 m)','B3fwd':'3 plates fwd (−4.3 kg)','B2fwd':'2 plates fwd (−8.7 kg)','Light':'No ballast + rear −20% (−20 kg)',
      'D4':'Chain 4WD','Clong':'Casters +100 mm fwd','AT100':'Anti-tip rollers 100 mm','T40':'Tow tilt 40°','T35':'Tow tilt 35°','Hsoft':'Soft hook bush (very soft)',
      'F1a':'Combo: Bfwd+AT100+bush+soft stop','F1b':'Combo with 3 plates','F1':'REV F.1 = F1a + casters fwd'}
rows=[['Variant','Tug kg','20% wet climb\n(avg m/s, of 0.5)','Casters off\nground uphill','Tug riding on\nrollers uphill','60 mm step','Hook peak / 99th\npct on step (N)','E-stop 20%\ndown (m)','Actuator peak\nraw / 50 ms (N)','Tow hook\n99th pct (N)']]
for v in order:
    if (v,'cycle') not in S: continue
    cl=S.get((v,'climb20'),{}); b=S.get((v,'bump60'),{}); e=S.get((v,'estop20'),{}); c=S.get((v,'cycle'),{})
    rows.append([name[v],c.get('tug_kg'),(f"{cl.get('avg_v')}" if cl.get('reached_5m') else 'STALLED'),f"{int(100*st(v,'climb20','phase7','caster_unloaded_frac',d=0))}%",
                 f"{st(v,'climb20','phase7','antitip_p90')} N",'PASS' if b.get('reached_4m') else 'STUCK',f"{st(v,'bump60','phase7','hook_max')} / {st(v,'bump60','phase7','hook_p99')}",
                 e.get('slide_m'),f"{c.get('act_peak_raw_N')} / {c.get('act_peak_50ms_N')}",st(v,'cycle','phase7','hook_p99')])
ax=fig.add_axes([0.03,0.33,0.94,0.56]); ax.axis('off')
def cc2(r,c,cell):
    t=cell.get_text().get_text()
    if rows[r][0].startswith('REV F.1'): cell.set_facecolor('#dff0e0'); cell.get_text().set_weight('bold')
    if t in('STALLED','STUCK'): cell.set_facecolor('#f7caca')
    if t=='PASS' and c==5: cell.set_facecolor('#d8f0d8')
table(ax,rows,[0.20,0.05,0.10,0.07,0.08,0.06,0.11,0.07,0.12,0.08],fs=9.6,scale=1.9,colorcol=cc2)
notes=[
"HOW TO READ IT",
"• Climb: every ~105 kg version is traction-limited at 20% wet grass (wheels slip, 0.24–0.32 m/s against 0.5 commanded). The 101 kg, 97 kg and 86 kg versions stall, so the 4 plates are",
"   the minimum. Moving them forward takes the tug off its anti-tip rollers uphill (roller load 135 N → 0) and raises the climb speed by about 20–30%.",
"• 60 mm sharp step: Rev F, the ballast variants and the tilt variants all high-centre (caster up 60 mm → rollers 0.88 m behind the axle drop below their 70 mm clearance).",
"   Raising the rollers, moving the casters forward or 4WD all clear it. 4WD and raised rollers alone gave the worst hook spikes (11.6 kN and 16.3 kN, single-step peaks).",
"• Hook peaks on the step are single-timestep spikes from rigid contact (the 200 mm bin wheel hitting a sharp 60 mm edge). The 99th percentile is the better measure of load.",
"   A soft bush halves them but lets the bin surge: e-stop 0.40 m. A medium bush (used in F.1) is the compromise.",
"• Actuator: Rev F's logged 2,500 N was one 0.5 ms step at the instant the brakes clamped (the actuator force limit was hit briefly); filtered over 50 ms it is about 1.0 kN.",
"   The F.1 soft stop removes it: 1,117 N raw. The real working load is ≤1.0 kN, so the 2.5 kN actuator has 2.5× margin.",
"• Tilt 35–40°: tips faster (34–39 s) and lowers the actuator spike, but it stalled on the 20% climb and the e-stop distance grew to 0.33–0.51 m, so 48° stays.",
]
para(fig,0.04,0.30,notes,fs=10.4,ls=1.45)
pdf.savefig(fig); plt.close(fig)
# ---------------- page 3: before/after + verdict vs alternatives
fig=page('Rev F vs Rev F.1: key tests re-run (same code, same seeds)','Full 108 kg bin unless noted. Wet grass μ 0.45, damp μ 0.6. "Rev F" values come from this re-run, so they can differ slightly from the Rev F report.')
r=lambda x: '–' if x in(None,'–') else x
ba=[['Test','Rev F','Rev F.1','Comment']]
ba.append(['Full cycle (dock→latch→tip→tow→stand→release)',f"PASS · tip {st('F0','cycle','tip_s')} s · act raw {st('F0','cycle','act_peak_raw_N')} N",f"PASS · tip {st('F1','cycle','tip_s')} s · act raw {st('F1','cycle','act_peak_raw_N')} N",'Soft stop removes the 2.5 kN brake-clamp spike'])
ba.append(['Climb 15% wet, 5 m',f"{st('F0','climb15','avg_v')} m/s · casters off {int(100*st('F0','climb15','phase7','caster_unloaded_frac',d=0))}% · on rollers {st('F0','climb15','phase7','antitip_max')} N",
           f"{st('F1','climb15','avg_v')} m/s · casters off {int(100*st('F1','climb15','phase7','caster_unloaded_frac',d=0))}% · rollers 0 N",'F.1 stays on its casters'])
ba.append(['Climb 20% wet, 5 m',f"{st('F0','climb20','avg_v')} m/s (heavy slip)",f"{st('F1','climb20','avg_v')} m/s (slip)",'At the traction limit: treat 20% wet with a full bin as marginal'])
ba.append(['E-stop 20% downhill wet, from 0.5 m/s',f"{st('F0','estop20','slide_m')} m",f"{st('F1','estop20','slide_m')} m",'Spring brakes; both stop'])
ba.append(['True 60 mm sharp step, left wheels, 0.5 m/s',"STUCK (high-centred on rollers)",f"PASS · hook {st('F1','bump60','phase7','hook_max')} N peak / {st('F1','bump60','phase7','hook_p99')} N p99",f"Rough: bin yaws up to {st('F1','bump60','phase7','bin_yaw_max')}°; same at 0.25 m/s. Ramp fixed steps"])
ba.append(['30% side slope, drive 3 m across',f"drift {st('F0','camber30','drift_while_driving_m')} m · creep {st('F0','camber30','creep_after_stop_m')} m",f"drift {st('F1','camber30','drift_while_driving_m')} m · creep {st('F1','camber30','creep_after_stop_m')} m",'No roll-over; RTK heading loop corrects drift'])
ba.append(['2.5 m bend (92°), damp',f"open-loop {st('F0','turn_open','arc_deg')}°",f"closed-loop {st('F1','turn_closed','arc_deg')}° in {st('F1','turn_closed','arc_time_s')} s · hitch ≤{st('F1','turn_closed','hitch_max_arc')}°",'P controller on heading, Kp 1.5 /s'])
ba.append(['Spin-in-place request with bin',f"hitch hits the {st('F0','turn_open','hitch_max_spin')}° stop",f"hitch held to {st('F1','turn_closed','hitch_max_spin')}° (cap 60°)",'Firmware turns a spin into a tight creeping turn'])
ax=fig.add_axes([0.03,0.42,0.94,0.48]); ax.axis('off')
def cc3(r_,c,cell):
    t=cell.get_text().get_text()
    if 'STUCK' in t: cell.set_facecolor('#f7caca')
    elif c==2: cell.set_facecolor('#eef7ee')
table(ax,ba,[0.24,0.25,0.26,0.25],fs=9.8,scale=2.3,colorcol=cc3,wrap=[40,40,42,40])
alt=[
"DESIGN-LEVEL VERDICT VS EARLIER CONCEPTS (judged from each revision's recorded behaviour; Rev A, C and E were not re-simulated here)",
"• Rev A, bin jack (lifts the front lip so the bin rolls on its own wheels): the robot carries a big share of the bin's weight and needs a fork to find the lip of whatever bin model is there.",
"   It needs a stronger lift and has a harder docking tolerance than F. Not better.",
"• Rev C, hitch-pin tug: the cheapest mechanism IF Brian bolts a hitch fitting onto his own bin. It drops the mast float and some docking tolerance (~€60–120 and ~5 kg less).",
"   But the tug mass stays (traction sets it), the bin must be modified, a crew can damage the fitting, and it only works from one face. Worth it only if modifying the bin is acceptable.",
"• Rev E, vertical-slide mast: failed outright (pulling the handle rolled the bin instead of tipping it). Rev F's wheel-stop crossbeam fixed that. Superseded.",
"• Rev F.1: the best fit for an unmodified, crew-handled 240 L bin. The remaining limits are physics (traction on 20% wet, sharp steps for a 200 mm bin wheel), not architecture.",
]
para(fig,0.04,0.37,alt,fs=10.6,ls=1.48)
pdf.savefig(fig); plt.close(fig)
# ---------------- page 4: recovery strategy + decision tree
fig=page('Task 2 – Recovery when the bin cannot be grabbed: detection and decision tree','Empty bin, 12.3 kg. The crew may leave it turned round, sideways, shoved against a hedge, or tipped over.')
det=[
"DETECTION (existing sensors + 2 tags)",
"• LD06 lidar on the bumper (~0.2 m high): fit the bin footprint",
"   (0.58 × 0.73 m) → position + heading (±180° ambiguous).",
"• Handle-side signature in the same scan: two small round returns",
"   (the wheels, 0.54 m apart) at one end; flat feet face at the other.",
"• Camera + AprilTag 36h11 (~150 mm) on the bin's FRONT and BACK:",
"   the tag ID says which face, the 6-DoF pose gives heading ±2° and",
"   tilt → 'upright / tipped' and 'is this our bin'.",
"• Tipped = tag roll >45° or footprint >0.9 m long and <0.7 m tall.",
"• Clearance map from the same lidar scan: handle-side corridor",
"   needed ≈2.1 m × 0.9 m; swing room ≥0.8 m radius round the",
"   wheel axle, plus ~0.6 m drift towards the handle per 90°.",
"",
"WHY NUDGING WORKS ON THE WHEELS (and its catch)",
"• Push the FEET end sideways with the bumper at 0.1 m/s while the",
"   tug follows the arc: the bin swings round its wheel axle.",
"   It needs ~40–60 N of push (feet friction), well within the drive.",
"• Because the wheels roll freely, the bin also ROLLS towards its",
"   handle (0.55 m per 90°, 1.1–1.25 m per 180° in sim). This decides",
"   when nudging is allowed (the room check above).",
]
para(fig,0.03,0.90,det,fs=10.6,ls=1.42)
if os.path.exists('frames/nudge.png'):
    axi=fig.add_axes([0.02,0.05,0.36,0.30]); axi.imshow(plt.imread('frames/nudge.png')); axi.axis('off'); axi.set_title('Sim frame: bumper swinging a sideways bin round its wheels (R2)',fontsize=9.5)
ax=fig.add_axes([0.40,0.04,0.58,0.87]); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis('off')
def box(x,y,w,h,t,fc='#e8f1f7',ec=BLUE,fs=9.2):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.6',fc=fc,ec=ec,lw=1.2)); ax.text(x,y,t,ha='center',va='center',fontsize=fs,wrap=True)
def arr(x0,y0,x1,y1,t=None,tx=0,ty=0):
    ax.annotate('',(x1,y1),(x0,y0),arrowprops=dict(arrowstyle='->',lw=1.1,color='#334'))
    if t: ax.text((x0+x1)/2+tx,(y0+y1)/2+ty,t,fontsize=8.6,color='#a33' if t.startswith('no') else '#262',weight='bold')
RED='#fde2e2'; GRN='#e1f3e1'
box(50,96,46,4.5,'ARRIVE at pickup point (RTK) · stop · 360° lidar + rear-camera scan')
box(50,87,34,4.5,'Bin found within 5 m?'); arr(50,93.5,50,89.5)
box(86,87,24,6,'search spiral 5 m → none:\nALERT "bin missing" + photo\nhome, retry +30 min ×3',fc=RED,ec='#a33',fs=8.4); arr(67,87,74,87,'no',-2,1)
box(50,78,34,4.5,'Upright? (tag roll / footprint)'); arr(50,84.5,50,80.5,'yes',1,0)
box(86,78,24,6,'TIPPED: stop, 4G alert with photo,\nhome, retry next window\n(the tug cannot right a bin)',fc=RED,ec='#a33',fs=8.4); arr(67,78,74,78,'no',-2,1)
box(50,69,40,5,'Handle side reachable? corridor ≥2.1 m × 0.9 m\nand handle within ±25° of a reachable approach'); arr(50,75.5,50,71.8,'yes',1,0)
box(14,60,24,7,'DRIVE ROUND to the pre-dock pose\n(path round the bin, 1.55 m radius)\n→ reverse on tag/lidar line',fc=GRN,ec='#262',fs=8.4); arr(32,69,20,63.8,'yes',-6,1)
box(56,58,40,5,'Pick rotation 90° or 180° (handle → open side)\nSwing room ≥0.8 m + roll-drift room clear?'); arr(52,66.5,55,60.8,'no',1,0)
box(56,47,40,5.5,'ORBIT-NUDGE: bumper pushes the feet end, tug follows the\narc at 0.1 m/s · abort if push >400 N for 2 s or drift >1.8 m',fc=GRN,ec='#262',fs=8.4); arr(56,55.5,56,50.0,'yes',1,0)
box(88,58,22,8,'NO ROOM (hard against a\nhedge, handle facing it):\nalert + photo, home, retry;\nafter 3 tries ask Brian',fc=RED,ec='#a33',fs=8.2); arr(76,58,77,58,'no',-1,1)
box(56,38,34,4.5,'Re-scan: within ±25° of target?'); arr(56,44.2,56,40.4)
arr(73,38,88,53.8); ax.text(80.5,40.2,'no → nudge again once;\nstill no → alert',fontsize=8.4,color='#a33',weight='bold')
box(36,29,40,5,'DOCK: drive round → pre-dock pose → reverse with\nline-following (lateral & heading P-loop) → wheel-stop contact'); arr(56,35.8,44,31.6,'yes',1,0); arr(14,56.3,24,31.6)
box(36,20,30,4.5,'Hook latch switches OK?'); arr(36,26.4,36,22.3)
box(78,20,28,6,'hooks up, pull forward 1 m,\nre-dock (max 2) → else alert',fc='#fff3c4',ec='#a80',fs=8.4); arr(51,20,64,20,'no',-3,1)
box(36,10,36,5,'TIP to 48° → tow home on the RTK route',fc=GRN,ec='#262'); arr(36,17.7,36,12.6,'yes',1,0)
ax.text(2,2,'Anywhere: person/animal in the lidar safety zone, or bin heading for a ditch/lane edge (geofence) → stop + alert.',fontsize=8.6,color='#a33')
pdf.savefig(fig); plt.close(fig)
# ---------------- page 5: recovery sim results + risks
fig=page('Recovery simulations (empty 12.3 kg bin, Rev F.1 geometry) and remaining risks','Perception emulated as true bin pose + noise (σ 15 mm, 1.5°, filtered). The bumper collides with the bin. μ 0.6 unless noted. Times are simulated seconds.')
def R(k,f,d='–'): return RC.get(k,{}).get(f,d)
rr=[['Scenario','Strategy','Result','Key numbers'],
 ['R2: sideways, handle side blocked by a wall',"nudge 90° round its wheels → drive round → dock → grab",'SUCCESS' if R('R2','success') else 'FAIL',
  f"rotated {R('R2','rotated_deg')}° in 13.6 s of pushing · bin rolled 0.56 m · dock error {R('R2','dock_lat_mm')} mm / {R('R2','dock_head_deg')}° · latched at 64 s · {R('R2','sim_time_s')} s incl. 47 s tip"],
 ['R1: backwards, hedge 1.5 m behind the handle',"nudge 180° round its wheels → dock → grab",'SUCCESS' if R('R1','success') else 'FAIL',
  f"rotated {R('R1','rotated_deg')}° in 25 s of pushing · bin rolled {[e[1] for e in R('R1','events',[]) if 'moved' in e[1]][0].split('moved ')[-1]} · dock error {R('R1','dock_lat_mm')} mm · latched at 84 s · bumper peak {R('R1','bumper_peak_N')} N"],
 ['Repeat with another noise seed','R1 and R2','2 / 2 SUCCESS' if R('R1_s3','success') and R('R2_s3','success') else 'mixed','same outcomes, within ±1 s'],
 ['R2 on wet grass μ 0.45','nudge 90° + dock (+ auto re-dock)','SUCCESS (2nd dock)' if R('R2_wet_s3','success') else 'FAIL',
  f"1st reverse ended 182 mm off line → latch missed → pull forward, re-dock OK · {R('R2_wet_s3','sim_time_s')} s"],
 ['R1 on wet grass μ 0.45','nudge 180°','FAIL → alert path','bin rolled 1.47 m, reached the hedge and wedged at 96°: wet ground needs more room'],
 ['R1a: backwards, hedge only 0.8 m behind','nudge round its wheels','FAIL (expected)',f"rotated {R('R1a','rotated_deg')}° then wedged against the hedge (bin rolled towards its handle) → alert path"],
 ['R1b: same, pivot on its feet','push the wheel end sideways','FAIL',f"bin slid sideways instead of pivoting ({R('R1b','rotated_deg')}°, moved 1.8 m) · rejected (may partly be a contact-model artefact)"],
 ['Tipped bin','–','not simulated','detection + alert only; righting a bin is out of scope for this hardware']]
ax=fig.add_axes([0.03,0.47,0.94,0.43]); ax.axis('off')
def cc4(r_,c,cell):
    t=cell.get_text().get_text()
    if c==2: cell.set_facecolor('#d8f0d8' if 'SUCCESS' in t else ('#f7caca' if 'FAIL' in t else '#eeeeee'))
table(ax,rr,[0.22,0.22,0.12,0.44],fs=9.5,scale=2.25,colorcol=cc4,wrap=[34,34,18,72])
risks=[
"REMAINING RISKS AND CAVEATS",
"• Traction: 20% wet grass with a full bin is at the limit (wheels slip, ~0.3 m/s). Measure the steepest part of the lane. If it is over ~15%, fit grippier tyres or accept slow, slipping climbs in the wet.",
"• Sharp steps: a 200 mm bin wheel hitting a sharp 60 mm edge gives multi-kN hook spikes and makes the bin yaw ~50°, even at 0.25 m/s. Ramp known steps; real lane bumps are usually rounded (easier).",
"• Rigid-contact model: tyres, grass and the hook are stiffer than real, so peak loads are pessimistic. Rolling resistance is a fixed axle friction. Bin centre of gravity and wheel size are estimated: measure them.",
"• Recovery: the bin's roll-towards-handle drift is the main hazard (ditches, the lane edge). The room check and geofence must be conservative. The wet-grass R1 failure shows the margin is thin.",
"• Docking on wet ground can miss the latch (R2 wet): the re-dock loop is required, not optional. Both cameras need tag visibility in rain, low sun and at night (IR LED or a retro-reflective tag).",
"• F.1 hardware changes are drawn as offsets of the Rev F CAD in the videos (rollers, ballast, outriggers). They have not been re-modelled in CAD yet.",
"• The 4G alert, photo upload and retry scheduling are logic only (not simulated). The tug cannot right a tipped bin, so a person must.",
]
para(fig,0.04,0.42,risks,fs=10.3,ls=1.5,width=175)
pdf.savefig(fig); plt.close(fig); pdf.close(); print('ok')
