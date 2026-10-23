import sys,json,pathlib,itertools,numpy as np
import trimesh
r=pathlib.Path(__file__).resolve().parent
c=json.loads((r/'design.json').read_text());L,W,D=c['L'],c['W'],c['D'];meshes={};report={}
for name in ['body','lid','sensor_cage']:
 m=trimesh.load_mesh(r/'stl'/f'{name}.stl');report[name]={'watertight':bool(m.is_watertight),'winding':bool(m.is_winding_consistent),'components':len(m.split(only_watertight=False)),'volume_mm3':float(m.volume),'bounds_mm':m.bounds.tolist()}
 assert m.is_volume and report[name]['components']==1,name
 if name=='lid':m.apply_transform([[1,0,0,0],[0,-1,0,W],[0,0,-1,D+1.5],[0,0,0,1]])
 if name=='sensor_cage':m.apply_transform([[1,0,0,49.5],[0,0,1,-11.5],[0,-1,0,D-.5],[0,0,0,1]])
 meshes[name]=m
proxies={
 'display':([12.95,13.95,.6],[132.1,32.1,17.8]),
 'esp_pcb':([1.8,15.9,42.2],[51.6,28.2,2.5]),
 'esp_headers':([7.8,15.9,23.5],[39.6,28.2,18.7]),
 'esp_usb':([-.1,25.6,44.7],[7,8.8,3]),
 'esp_plug':([-12,24.55,42.9],[11.9,10.9,6.6]),
 'amp':([55.5,8.8,37.1],[22.4,42.4,10.1]),
 'speaker':([80,23,30.6],[69.7,31.2,16.6]),
 'sensor':([61.5,-7.6,25.7],[15,7.6,15])}
def box(pos,size):
 m=trimesh.creation.box(extents=size);m.apply_translation(np.array(pos)+np.array(size)/2);return m
hardware={k:box(*v) for k,v in proxies.items()}
verts=[]
for z in [37.75,45.35]:
 m=trimesh.creation.cylinder(radius=2.6,height=12.7,sections=96)
 m.apply_transform([[0,0,1,151.65],[1,0,0,19],[0,1,0,z],[0,0,0,1]]);verts.extend(m.vertices)
hardware['power']=trimesh.convex.convex_hull(np.array(verts))
def volume(a,b):
 if np.any(np.minimum(a.bounds[1],b.bounds[1])-np.maximum(a.bounds[0],b.bounds[0])<.0001):return 0.
 return float(trimesh.boolean.intersection([a,b],engine='manifold').volume)
collisions=[]
for (a,ma),(b,mb) in itertools.combinations(meshes.items(),2):
 v=volume(ma,mb)
 if v>.03:collisions.append([a,b,v])
for a,ma in hardware.items():
 for b,mb in meshes.items():
  v=volume(ma,mb)
  if v>.03:collisions.append([a,b,v])
for (a,ma),(b,mb) in itertools.combinations(hardware.items(),2):
 v=volume(ma,mb)
 if v>.03:collisions.append([a,b,v])
# Rear insertion of the lid-mounted assembly and display into body.
insertion=[]
for step in [0,2,5,10,20,40,60]:
 for name in ['lid','display','esp_pcb','esp_headers','esp_usb','amp','speaker']:
  m=(meshes if name=='lid' else hardware)[name].copy();m.apply_translation([0,0,step]);v=volume(meshes['body'],m)
  if v>.03:insertion.append([name,step,v])
# Constant rounded outer contour, excluding the two intentional feet below Y=W.
v=meshes['body'].vertices;v=v[(v[:,1]>=0)&(v[:,1]<=W)&(v[:,2]>=3)]
q=np.abs(v[:,:2]-[L/2,W/2])-[L/2-16,W/2-16]
sdf=np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(np.max(q,axis=1),0)-16
assert np.max(sdf)<.002,float(np.max(sdf))
result={'parts':report,'collisions':collisions,'insertion_collisions':insertion,'no_ESP_outer_bulge':True,'side_wall_mm':2.25,'front_skin_mm':.6,'display_to_esp_wire_gap_mm':5.1,'total_bounds_mm':[158,77.5,51.2],'limits':'Rigid hardware envelopes from user measurements; switches not measured; flexible cables and print tolerances require physical fit check.'}
(r/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert not collisions and not insertion
