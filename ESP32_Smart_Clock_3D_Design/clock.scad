// rev18: smooth symmetric shell, centered ESP, right-side longitudinal power port, compact layout. Units mm.
part="body";$fn=72;
L=158;W=60;D=49.7;lid_t=1.5;wall=2.25;floor_t=1.956;front_skin=.6;
insert_d=3.9;screw_d=3.4;
lid_pts=[[24,6],[134,6],[39.5,60],[118.5,60]];
feet_x=[39.5,118.5];
esp_x=1.8;esp_y=15.9;esp_h=5;esp_pcb_t=2.5;
esp_holes=[[4.25,18.35],[50.95,18.35],[4.25,41.65],[50.95,41.65]];
amp_h=2.5;amp_holes=[[74.75,26.25],[58.65,26.25]];
spk_h=2.5;spk_holes=[[146.75,50.95],[83.05,26.35]];
sensor_screws=[[53.5,D-15],[84.5,D-15]];
power_y=19;power_z=D-8.15;
module box(p,s){translate(p)cube(s);}
module rr(w,h,r){hull()for(x=[r,w-r],y=[r,h-r])translate([x,y])circle(r=r,$fn=(r>=6?192:72));}
module slab(p,s,r=2){translate(p)linear_extrude(s[2])rr(s[0],s[1],r);}
module hole_z(p,d,h){translate(p)cylinder(d=d,h=h);}
module hole_y(p,d,h){translate(p)rotate([-90,0,0])cylinder(d=d,h=h);}
module outside(){hull(){
 for(i=[0:12])let(a=90*i/12,t=3-3*sin(a),z=3-3*cos(a))slab([t,t,z],[L-2*t,W-2*t,.015],16-t);
 slab([0,0,D-.015],[L,W,.015],16);
}}
module rear_profile(inset=0){translate([inset,inset])rr(L-2*inset,W-2*inset,16-inset);}
module rear_outline(){hull(){
 for(i=[0:12])let(a=90*i/12,t=lid_t*(1-cos(a)),z=D+lid_t*sin(a))
 translate([0,0,min(z,D+lid_t-.015)])linear_extrude(.015)rear_profile(t);
}}
// Same oblong aperture rotated: 5.5 along height Y, 13.1 along depth Z.
module right_oblong(y,z,w=13.1,h=5.5){
 multmatrix([[0,0,1,L-8],[0,1,0,y-h/2],[1,0,0,z-w/2],[0,0,0,1]])linear_extrude(9)rr(w,h,h/2);
}
module feet(){for(x=feet_x)slab([x-5.5,W-5,0],[11,11,D],3);}
module display_corner_stops(){for(x=[12.45,145.55],y=[13.45,46.55]){
 let(left=x<L/2,top=y<W/2){
 box([left?x-1.5:x,top?y-1.5:y-6,floor_t-.1],[1.5,7.5,8.1]);
 box([left?x-1.5:x-6,top?y-1.5:y,floor_t-.1],[7.5,1.5,8.1]);
 }}}
module bottom_vents_raw(){
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[75.778, 71.748], [73.609, 71.748], [69.04181, 32.0799], [67.292, 16.882], [67.23705, 15.70062], [67.21655, 15.09564], [67.24204, 14.7976], [67.31, 13.622], [67.35764, 13.3439], [67.46872, 12.99708], [67.77094, 11.63062], [68.02273, 11.28382], [68.50714, 10.35838], [68.792, 10.114], [68.98812, 10.08242], [69.5, 10.0], [71.4692, 27.10422], [76.609, 71.748]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[88.609, 71.748], [83.4692, 27.10422], [81.5, 10.0], [81.30388, 10.03158], [80.792, 10.114], [80.68286, 10.20762], [80.398, 10.452], [79.91359, 11.37744], [79.728, 11.732], [79.61221, 12.25554], [79.31, 13.622], [79.24204, 14.7976], [79.21655, 15.09564], [79.23705, 15.70062], [79.292, 16.882], [81.04181, 32.0799], [85.609, 71.748], [86.44, 71.748]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[82.609, 71.748], [80.44, 71.748], [79.609, 71.748], [75.04181, 32.0799], [73.292, 16.882], [73.23705, 15.70062], [73.21655, 15.09564], [73.24204, 14.7976], [73.31, 13.622], [73.42579, 13.09846], [73.728, 11.732], [74.21241, 10.80656], [74.398, 10.452], [74.68286, 10.20762], [74.792, 10.114], [74.98812, 10.08242], [75.5, 10.0], [80.6398, 54.64378]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[69.778, 71.748], [67.609, 71.748], [63.04181, 32.0799], [61.292, 16.882], [61.27095, 16.42938], [61.216, 15.248], [61.28396, 14.0724], [61.31, 13.622], [61.61221, 12.25554], [61.728, 11.732], [61.95213, 11.20276], [62.13772, 10.8482], [62.24686, 10.75458], [62.792, 10.114], [62.98812, 10.08242], [63.5, 10.0], [68.6398, 54.64378], [70.609, 71.748]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[115.292, 16.882], [119.85919, 56.5501], [121.609, 71.748], [122.44, 71.748], [124.609, 71.748], [122.6398, 54.64378], [117.5, 10.0], [116.98812, 10.08242], [116.792, 10.114], [116.50714, 10.35838], [116.398, 10.452], [116.21241, 10.80656], [115.728, 11.732], [115.42579, 13.09846], [115.31, 13.622], [115.24204, 14.7976], [115.21655, 15.09564], [115.23705, 15.70062]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[109.31, 13.622], [109.24204, 14.7976], [109.21655, 15.09564], [109.23705, 15.70062], [109.292, 16.882], [111.04181, 32.0799], [115.609, 71.748], [117.778, 71.748], [118.609, 71.748], [113.4692, 27.10422], [111.5, 10.0], [111.30388, 10.03158], [110.792, 10.114], [110.68286, 10.20762], [110.398, 10.452], [110.21241, 10.80656], [109.728, 11.732], [109.61221, 12.25554]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[98.98812, 10.08242], [98.792, 10.114], [98.50714, 10.35838], [98.398, 10.452], [97.91359, 11.37744], [97.77094, 11.63062], [97.46872, 12.99708], [97.35764, 13.3439], [97.31, 13.622], [97.24204, 14.7976], [97.21655, 15.09564], [97.23705, 15.70062], [97.292, 16.882], [101.85919, 56.5501], [103.609, 71.748], [104.44, 71.748], [106.609, 71.748], [101.4692, 27.10422], [99.5, 10.0]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[91.24204, 14.7976], [91.21655, 15.09564], [91.23705, 15.70062], [91.292, 16.882], [95.85919, 56.5501], [97.609, 71.748], [99.778, 71.748], [100.609, 71.748], [98.6398, 54.64378], [93.5, 10.0], [92.98812, 10.08242], [92.73743, 10.1611], [92.45257, 10.40546], [91.96816, 11.3309], [91.77094, 11.63062], [91.46872, 12.99708], [91.35764, 13.3439], [91.31, 13.622]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[103.292, 16.882], [103.23705, 15.70062], [103.21655, 15.09564], [103.24204, 14.7976], [103.31, 13.622], [103.35764, 13.3439], [103.46872, 12.99708], [103.77093, 11.63062], [103.91359, 11.37744], [104.398, 10.452], [104.68286, 10.20762], [104.792, 10.114], [105.30388, 10.03158], [105.5, 10.0], [110.6398, 54.64378], [112.609, 71.748], [110.44, 71.748], [109.609, 71.748], [107.85919, 56.5501]]);
multmatrix([[1,0,0,0],[0,0,1,60.8],[0,1,0,0],[0,0,0,1]])linear_extrude(4.2)polygon([[94.609, 71.748], [92.44, 71.748], [91.609, 71.748], [87.04181, 32.0799], [85.292, 16.882], [85.23705, 15.70062], [85.216, 15.248], [85.28396, 14.0724], [85.31, 13.622], [85.61221, 12.25554], [85.728, 11.732], [85.91359, 11.37744], [86.398, 10.452], [86.62154, 10.3268], [87.205, 10.0], [87.41828, 10.0], [87.5, 10.0], [92.6398, 54.64378]]);
}


module bottom_vents(){translate([-13.5,-4,0])scale([1,1,.53])bottom_vents_raw();}
module sensor_guides(){
 for(x=[65.3,71.9]){box([x,0,D-2.5],[1.8,.8,2.5]);box([x,2.6,D-2.5],[1.8,1,2.5]);}
 box([65.3,0,D-2.5],[.7,3.6,2.5]);box([73,0,D-2.5],[.7,3.6,2.5]);
}
module body(){difference(){union(){
 difference(){outside();
 slab([wall,wall,floor_t],[L-2*wall,W-2*wall,D+1],16-wall);
 slab([12.45,13.45,front_skin],[133.1,33.1,floor_t+1],.5);
 // Internal local recess only; outer profile remains the same rounded rectangle at every rear slice.
 box([1,esp_y-1,D-7.9],[6,30.2,8.9]);
 box([-1,W/2-5.95,D-7.7],[8,11.9,10]);
 right_oblong(power_y,power_z);
 box([L-8,power_y-2.75,power_z],[9,5.5,D-power_z+1]);
 box([66,-1,D-8],[7,5,10]);
 }
 feet();display_corner_stops();sensor_guides();
 for(p=lid_pts)hole_z([p[0],p[1],0],8,D);
 for(p=sensor_screws)hole_y([p[0],0,p[1]],8,6);
 }
 for(p=lid_pts)hole_z([p[0],p[1],D-3.5],insert_d,3.6);
 for(p=sensor_screws)hole_y([p[0],-.01,p[1]],insert_d,3.51);
 bottom_vents();
}}
module esp_post(p){difference(){
 intersection(){hole_z([p[0],p[1],D-esp_h],6.4,esp_h+.1);linear_extrude(D+1)rear_profile(1.3);}
 // D-shaped seating section. Flat removes 1 mm on the switch-facing side.
 // Insert is recessed 2.5 mm, below the 2.3 mm-deep switch relief.
 if(p[0]<10){
  if(p[1]<W/2)box([p[0]-4,p[1]+2.2,D-esp_h-.1],[8,5,2.4]);
  else box([p[0]-4,p[1]-7.2,D-esp_h-.1],[8,5,2.4]);
 }
}}
module lid(){difference(){union(){
 rear_outline();for(x=feet_x)slab([x-5.5,W-5,D],[11,11,lid_t],3);
 for(p=esp_holes)esp_post(p);
 for(p=amp_holes)hole_z([p[0],p[1],D-amp_h],8,amp_h+.1);
 for(p=spk_holes)hole_z([p[0],p[1],D-spk_h],8,spk_h+.1);
 box([66.35,.35,D-3],[6.3,2.3,3.1]);
 difference(){
 box([0,W/2-5.75,D-7.5],[1.2,11.5,7.6]);
 multmatrix([[0,0,1,-.1],[1,0,0,W/2-4.6],[0,1,0,D-5.2],[0,0,0,1]])linear_extrude(1.4)rr(9.2,3.4,.6);
 }
 difference(){box([L-wall,power_y-2.6,power_z],[wall,5.2,D-power_z+.1]);right_oblong(power_y,power_z);}
 }
 for(x=[66,71.7]){box([x,-1,D-3.2],[1.3,2.2,3.2]);box([x,2.2,D-3.2],[1.3,2.8,3.2]);}
 for(p=lid_pts)hole_z([p[0],p[1],D-.1],screw_d,lid_t+.2);
 for(p=esp_holes){
  if(p[0]<10){hole_z([p[0],p[1],D-esp_h-.1],3.4,2.7);// Closed outer skin: 0.6 mm. Integral rear closure.
   // Insert pocket print Z=1.05..4.05; nominal 2.9 mm insert pocket.
   hole_z([p[0],p[1],D+lid_t-4.05],insert_d,3.0);
   // Smaller screw-tip cavity leaves a supporting annular seat and closed outer skin.
   hole_z([p[0],p[1],D+lid_t-1.1],3.4,.5);}
  else hole_z([p[0],p[1],D-esp_h-.1],insert_d,3.3);
 }
 for(p=amp_holes)hole_z([p[0],p[1],D-amp_h-.1],insert_d,3.3);
 for(p=spk_holes)hole_z([p[0],p[1],D-spk_h-.1],insert_d,3.3);
 intersection(){translate([114.85,38.6,D-.1])scale([38.7/2,26.9/2,1])cylinder(r=1,h=lid_t+.3,$fn=192);
 union(){for(x=[95:4:135])slab([x,23.6,D-.1],[2,30,lid_t+.3],.95);}}
 for(dx=[-12:6:12])slab([esp_x+25.8+dx-1.2,W/2-10,D-.1],[2.4,20,lid_t+.3],1.1);
}}
module sensor_cage(){difference(){union(){
 difference(){
  multmatrix([[1,0,0,57.5],[0,0,-1,0],[0,1,0,D-28],[0,0,0,1]])linear_extrude(11.5)rr(23,27.5,3);
  box([59.5,-9.5,D-26],[19,10.5,24]);
 }
 for(p=sensor_screws)hull(){hole_y([p[0],-3,p[1]],8,3);box([p[0]<60?57:78,-3,p[1]-4],[3,3,8]);}
 }
 for(p=sensor_screws)hole_y([p[0],-3.1,p[1]],screw_d,3.3);
 for(x=[61:4:77])box([x,-12,D-24],[2,4,18]);
 for(z=[D-23,D-17,D-11]){box([57,-8.5,z],[4,5.5,2]);box([77,-8.5,z],[4,5.5,2]);}
 for(x=[61:4:73])box([x,-8.5,D-29],[2,5.5,4]);
}}
module power_gauge(){difference(){cube([22,15,wall]);translate([4.45,4.75,-.1])linear_extrude(wall+.2)rr(13.1,5.5,2.75);}}
module esp_gauge(){intersection(){lid();box([0,esp_y-2,D-6],[10,32.2,8]);}}
if(part=="body")body();
else if(part=="lid")translate([0,W,D+lid_t])rotate([180,0,0])lid();
else if(part=="sensor_cage")multmatrix([[1,0,0,-49.5],[0,0,-1,D-.5],[0,1,0,11.5],[0,0,0,1]])sensor_cage();
else if(part=="power_gauge")power_gauge();
else if(part=="esp_gauge")translate([0,W,D+lid_t])rotate([180,0,0])esp_gauge();
else if(part=="closed"){body();lid();sensor_cage();}
