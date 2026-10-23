import sys,json,pathlib
import trimesh,numpy as np
r=pathlib.Path(__file__).resolve().parent
body=trimesh.load_mesh(r/'stl/body.stl');lid=trimesh.load_mesh(r/'stl/lid.stl');cage=trimesh.load_mesh(r/'stl/sensor_cage.stl')
lid.apply_transform([[1,0,0,0],[0,-1,0,60],[0,0,-1,51.2],[0,0,0,1]])
cage.apply_transform([[1,0,0,49.5],[0,0,1,-11.5],[0,-1,0,49.2],[0,0,0,1]])
def box(p,s):
 m=trimesh.creation.box(extents=s);m.apply_translation(np.array(p)+np.array(s)/2);return m
sensor=box([61.5,-7.6,25.7],[15,7.6,15])
wire=trimesh.boolean.union([box([67,-5.8,40.7],[5,5,6]),box([67,-5.8,41.7],[5,11.8,5])],engine='manifold')
def volume(a,b):
 if np.any(np.minimum(a.bounds[1],b.bounds[1])-np.maximum(a.bounds[0],b.bounds[0])<=.001):return 0.
 return float(trimesh.boolean.intersection([a,b],engine='manifold').volume)
collisions=[]
for name,part in [('body',body),('lid',lid),('cage',cage)]:
 v=volume(part,wire)
 if v>.03:collisions.append({'part':name,'against':'5x5 wire route gauge','volume_mm3':v})
steps=[0,1,2,4,8,12,20]
for step in steps:
 moved=cage.copy();moved.apply_translation([0,-step,0])
 for name,other in [('body',body),('lid',lid),('sensor',sensor),('wire route',wire)]:
  v=volume(moved,other)
  if v>.03:collisions.append({'lift_mm':step,'against':name,'volume_mm3':v})
# Lid must remain removable with cage fixed to the body.
for step in [0,2,5,10,20,40]:
 moved=lid.copy();moved.apply_translation([0,0,step]);v=volume(moved,cage)
 if v>.03:collisions.append({'lid_rear_offset_mm':step,'against':'installed cage','volume_mm3':v})
report={'cage_vertical_lift_samples_mm':steps,'wire_route_gauge_cross_section_mm':[5,5],'collisions':collisions,'limits':'Discrete rigid-envelope checks. The 5x5 route gauge is a design clearance, not a measured cable bundle. Physical assembly and flexibility not verified.'}
(r/'sensor_installation_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert not collisions
