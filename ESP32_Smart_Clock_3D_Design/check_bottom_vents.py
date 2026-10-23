import sys,json,pathlib
import trimesh,numpy as np
r=pathlib.Path(__file__).resolve().parent
m=trimesh.load_mesh(r/'stl/body.stl')
# Each check ray passes through the center of a restored slanted slot.
centers=[[69.40066, 24.46312], [81.41096, 24.2609], [75.5758, 25.80881], [63.61153, 25.84505], [117.72256, 27.17664], [111.50189, 24.22918], [99.42001, 25.01853], [93.72423, 27.3604], [105.61275, 26.45737], [87.61529, 25.75758]]
tri=m.triangles;a=tri[:,0,[0,2]];v=tri[:,1,[0,2]]-a;w=tri[:,2,[0,2]]-a;det=v[:,0]*w[:,1]-v[:,1]*w[:,0];ok=abs(det)>1e-8
results=[]
for old_x,old_z in centers:
 x,z=old_x-13.5,old_z*.53
 q=np.array([x,z])-a;u=np.zeros(len(tri));h=u.copy();u[ok]=(q[ok,0]*w[ok,1]-q[ok,1]*w[ok,0])/det[ok];h[ok]=(v[ok,0]*q[ok,1]-v[ok,1]*q[ok,0])/det[ok]
 k=ok&(u>=-1e-8)&(h>=-1e-8)&(u+h<=1+1e-8)
 y=tri[:,0,1]+u*(tri[:,1,1]-tri[:,0,1])+h*(tri[:,2,1]-tri[:,0,1]);crossings=np.unique(np.round(y[k],4));blocked=bool(np.any((crossings>=57.75)&(crossings<=60)))
 results.append({'x':x,'z':z,'clear_through_bottom_wall':not blocked})
(r/'bottom_vents_validation.json').write_text(json.dumps(results,indent=2))
print('Bottom vents verified:',sum(x['clear_through_bottom_wall'] for x in results),'/',len(results))
assert len(results)==10 and all(x['clear_through_bottom_wall'] for x in results)
