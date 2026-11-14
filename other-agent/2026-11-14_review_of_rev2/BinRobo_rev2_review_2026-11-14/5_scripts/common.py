exec(open('/workspace/work/coldeye_rev2/clash_r2.py').read().split("R={}")[0].replace("mode=sys.argv[1]","mode='imp'"))
exec(open('/workspace/work/coldeye_imp/env.py').read().split("tug=[it")[0].split("out={}")[1])  # rprof, envelope
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
def dist(a,b):
    d=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped); d.Perform(); return d.Value()
def bbox(s):
    b=s.BoundingBox(); return [round(x,1) for x in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)]
def roll(sh,deg): return sh.rotate(cq.Vector(0,0,200),cq.Vector(1,0,200),deg)
