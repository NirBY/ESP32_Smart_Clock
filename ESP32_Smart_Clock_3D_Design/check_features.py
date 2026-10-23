exec((__import__('pathlib').Path(__file__).with_name('validate_revision.py')).read_text().split('collisions=[]')[0])
def filled(m,pos,size):return volume(m,box(pos,size))/float(np.prod(size))
lid=meshes['lid'];body=meshes['body']
# D relief and recessed insert retention at both USB-side posts.
for x,y in [[4.25,18.35],[4.25,41.65]]:
 yp=y+2.25 if y<30 else y-3.05
 assert filled(lid,[x-.4,yp,44.75],[.8,.8,2.1])<.001
 assert filled(lid,[x-.2,y-.2,50.65],[.4,.4,.5])>.999
 assert filled(lid,[x-.2,y-.2,44.65],[.4,.4,5.7])<.001
 # Material around insert remains full below relief.
 assert filled(lid,[x+2.3,y-.2,47.4],[.5,.4,2])>.999
# Body skin samples; feet screw locations and through holes.
for x in np.linspace(13,145,9):
 for y in np.linspace(14,46,5):
  assert filled(body,[x-.1,y-.1,.05],[.2,.2,.5])>.999
  assert filled(body,[x-.1,y-.1,.61],[.2,.2,.5])<.001
for x,y in c['lid_holes']:
 assert filled(body,[x-.2,y-.2,46.3],[.4,.4,3.3])<.001
 assert filled(lid,[x-.2,y-.2,49.65],[.4,.4,1.6])<.001
# Five rear vents centered on ESP; cut paths on lid.
for x in [15.6,21.6,27.6,33.6,39.6]:assert filled(lid,[x-.4,21,49.6],[.8,18,1.7])<.001
# Constant side/top walls away from ports and bosses.
assert filled(body,[70,.01,15],[5,2.23,5])>.999
assert filled(body,[70,2.26,15],[5,.4,5])<.001
# Four separate corner stops and no continuous rails.
for x in [12.45,145.55]:
 for y in [13.45,46.55]:
  assert filled(body,[x-1.3 if x<79 else x+.2,y+.3 if y<30 else y-5.5,2.1],[1,5,7])>.999
for pos,size in [([10.95,23,3],[1.5,14,6]),([145.55,23,3],[1.5,14,6]),([30,11.95,3],[90,1.5,6]),([30,46.55,3],[90,1.5,6])]:assert filled(body,pos,size)<.001
report={'D_relief_mm':1,'D_relief_depth_mm':2.3,'recessed_insert_mm':2.5,'USB_insert_installation':'during print pause at 4.05 mm','integrated_outer_skin_mm':.6,'ESP_standoff_height_mm':5,'USB_side_screws':'M3x8','other_ESP_screws':'M3x5','four_separate_corner_stops':True,'skin_mm':.6,'walls_mm':2.25,'vents_centered':True}
(r/'feature_validation.json').write_text(json.dumps(report,indent=2));print(report)
