import sys,json,pathlib,numpy as np
import trimesh
r=pathlib.Path(__file__).resolve().parent
m=trimesh.load_mesh(r/'stl/lid.stl')
def box(pos,size):
 b=trimesh.creation.box(extents=size);b.apply_translation(np.array(pos)+np.array(size)/2);return b
def overlap(part,shape):return float(trimesh.boolean.intersection([part,shape],engine='manifold').volume)
partial=trimesh.boolean.intersection([m,box([-1,-7,-.1],[160,70,4.15])],engine='manifold')
for y in [18.35,41.65]:
 # Four 0.15 mm layers close the outer face. Sample just inside both boundaries.
 b=box([4.05,y-.2,.01],[.4,.4,.58]);assert overlap(m,b)/b.volume>.999
 b=box([4.05,y-.2,.61],[.4,.4,.35]);assert overlap(m,b)<.0001
 # Insert has an annular seat at print Z=1.05, not an open hole in the outer face.
 b=box([6.02,y-.1,.65],[.1,.2,.35]);assert overlap(m,b)/b.volume>.999
 # Pilot opening remains accessible from above at the 4.05 mm pause plane.
 cylinder=trimesh.creation.cylinder(radius=1.89,height=3.25,sections=96);cylinder.apply_translation([4.25,y,2.725]);assert overlap(partial,cylinder)<.0001
 # Finished top section captures the insert: bore narrows to screw clearance.
 b=box([6.02,y-.1,4.15],[.1,.2,.15]);assert overlap(m,b)/b.volume>.999
report={'outer_skin_mm':.6,'separate_cover_required':False,'pause_print_z_mm':4.05,'next_layer_z_mm':4.2,'uniform_layer_height_mm':.15,'pause_after_layer_count':27,'insert_pocket_print_z_mm':[1.05,4.05],'insert_top_when_seated_mm':3.95,'M3x8_with_05_washer_nominal_tip_to_cover_clearance_mm':.9,'both_holes_closed':True,'both_insert_pockets_accessible_at_pause':True,'limits':'Pause workflow and thermal insertion not physically tested.'}
(r/'integrated_cover_validation.json').write_text(json.dumps(report,indent=2));print(report)
