exec((__import__('pathlib').Path(__file__).with_name('validate_revision.py')).read_text().split('collisions=[]')[0])
body=meshes['body'];lid=meshes['lid']
def filled(pos,size):return sum(volume(m,box(pos,size)) for m in [body,lid])/float(np.prod(size))
# Aperture on right side; 5.5 height x 13.1 depth, old top aperture now solid.
for y,z in [[19,41.55],[19,35.2],[19,47.9],[16.5,41.55],[21.5,41.55]]:
 assert filled([155.9,y-.03,z-.03],[2,.06,.06])<.001,(y,z)
# Solid curved corners of the oblong, demonstrating that it is not a rectangle.
for y,z in [[16.5,35.5],[21.5,35.5],[16.5,47.6],[21.5,47.6]]:
 assert filled([155.9,y-.03,z-.03],[2,.06,.06])>.999,(y,z)
assert filled([110,.1,43],[8,2,3])>.999
# Connected wire route runs into the case, beside speaker, using a 5x5 design gauge.
wire=box([138,16.5,39.05],[7.3,5,5])
for name,m in {**meshes,**{k:v for k,v in hardware.items() if k!='power'}}.items():assert volume(m,wire)<.001,name
# Outside plug clearance.
plug=box([158.1,15.7,36.1],[12,6.6,10.9])
for m in meshes.values():assert volume(m,plug)<.001
report={'wall':'right, opposite ESP','aperture_yz_mm':[5.5,13.1],'aperture_center_yz_mm':[19,41.55],'flange_rear_edge_z_mm':49.35,'lid_plane_z_mm':49.7,'flange_to_lid_nominal_gap_mm':.35,'neck_to_speaker_nominal_gap_mm':1.4,'old_top_opening_closed':True,'wire_route_gauge_mm':[5,5],'speaker_extra_downward_shift_mm':1,'limits':'Rounded neck inferred from photo, spring motion not simulated; physical seating depends on print tolerance.'}
(r/'power_position_validation.json').write_text(json.dumps(report,indent=2));print(report)
