import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
BG='#e8e8ea'; INK='#1d1d1f'; ACC='#ff4d00'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,(a,b)=plt.subplots(1,2,figsize=(16,8),facecolor=BG,gridspec_kw=dict(width_ratios=[1,1.05]))
for ax in (a,b): ax.set_facecolor(BG); ax.axis('off')
# section through front wall + receiver (illustrative)
P=lambda pts,fc: a.add_patch(plt.Polygon(pts,closed=True,fc=fc,ec=INK,lw=1))
P([(0,0),(6,0),(6,160),(0,160)],'#9aa3a0')          # front wall (thk 6)
P([(6,120),(40,120),(40,128),(6,128)],ACC)          # receiver shelf
P([(32,96),(40,96),(40,128),(32,128)],ACC)          # downturned lip
P([(-20,160),(46,160),(46,172),(-20,172)],'#8a9390') # rim
P([(-25,172),(52,172),(52,184),(-25,184)],'#7d8784') # lid
# comb tooth
a.add_patch(plt.Polygon([(10,60),(28,60),(28,116),(10,116)],closed=True,fc='none',ec='#607868',lw=1.5,ls='--'))
a.text(-2,70,'comb tooth\n(robot)',color='#607868',ha='right',fontsize=10)
def d(p0,p1,t,tx,ty,col=INK):
    a.annotate('',xy=p0,xytext=p1,arrowprops=dict(arrowstyle='<->',color=col,lw=1))
    a.text(tx,ty,t,color=col,fontsize=10,fontweight='bold')
d((6,136),(40,136),'M3a lip projection from wall',44,138,ACC)
d((46,96),(46,128),'M3b lip drop (downturn depth)',50,108,ACC)
d((6,112),(32,112),'',0,0,ACC); a.text(44,82,'M3d seat gap: wall to inside\nof downturn (tooth fits here)',color=ACC,fontsize=10,fontweight='bold')
a.annotate('',xy=(19,112),xytext=(44,90),arrowprops=dict(arrowstyle='-',color=ACC,lw=0.8))
a.annotate('M3e lip / shelf thickness',xy=(40,124),xytext=(60,168),color=ACC,fontsize=10,fontweight='bold',arrowprops=dict(arrowstyle='-|>',color=ACC))
a.annotate('M1 = height of this top\nsurface above the ground',xy=(20,128),xytext=(-75,140),fontsize=10,fontweight='bold',arrowprops=dict(arrowstyle='-|>',color=INK))
a.text(-75,20,'FRONT WALL\n(inside of bin to the left)',fontsize=9,color='#555')
a.set_xlim(-90,130); a.set_ylim(-18,200); a.set_aspect('equal')
a.set_title('Detail: section through the lifting lip (enlarged, typical shape)',fontsize=12,color=INK)
a.text(-88,-12,'Also M3c: rib pitch and rib thickness along the lip (photo it square-on with a tape)',fontsize=9,color=INK)
# checklist + markings
txt=("WHAT TO MEASURE (every bin, mm, tape + straight edge)\n"
"M1  Height of lip top above flat ground\n"
"M2  Lip length, end to end\n"
"M3  Lip profile a-e (detail) + rib pitch c\n"
"M4  Front wall set-back from lip face at 450, 500, 550 mm below lip\n"
"M5  Overall height (lid shut), overall depth\n"
"M6  Handle bar: height, bar diameter, gap behind bar\n"
"M7  Wheel diameter, width, outside track, axle height\n"
"M8  Axle centre to front wall at the base\n"
"M11 Lid overhang beyond the lip (front)\n"
"M12 Body width at lip height and 500 mm up\n"
"Mass: weigh empty (bathroom scale) and a typical full one\n\n"
"PHOTOS: front square-on, side square-on, lip close-up\n"
"with a tape held across it, and the moulded stamp area\n\n"
"MOULDED MARKINGS THAT HELP US (EN 840-1 cl. 9)\n"
"EN 840-1      proves an EN 840 bin = frontal comb receiver\n"
"Nominal vol. 140 / 240 L\n"
"Max total mass e.g. 110 kg for 240 L (our design load)\n"
"Maker / trademark + mould no. -> exact data sheet\n"
"Year / month  date clock: age of the plastic lip\n"
"RAL-GZ 951/1  GGAWB quality mark: lip load-tested\n"
"CE + LWA dB(A)  noise mark, 2000/14/EC\n"
">PE-HD<      material code (EN ISO 11469)")
b.text(0.02,0.98,txt,va='top',ha='left',family='DejaVu Sans Mono',fontsize=11.5,color=INK,transform=b.transAxes,
       bbox=dict(boxstyle='round,pad=0.6',fc='white',ec='#999'))
fig.suptitle('Bin lifting lip detail, measurement checklist and the stamps to look for',fontsize=14,color=INK)
plt.tight_layout(rect=(0,0,1,0.95))
fig.savefig('bin_lip_and_markings.png',dpi=130,facecolor=BG)
