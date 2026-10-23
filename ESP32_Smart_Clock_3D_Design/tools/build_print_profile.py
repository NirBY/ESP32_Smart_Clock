from pathlib import Path
import json
import argparse
import subprocess
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Build the editable OrcaSlicer clock project.')
parser.add_argument('--orca',type=Path,required=True,help='Official OrcaSlicer executable; resources must be beside it')
parser.add_argument('--output',type=Path,required=True,help='Output directory for intermediate presets and native project')
args=parser.parse_args()
presets=args.orca.resolve().parent/'resources/profiles/Creality'
out=args.output.resolve()
out.mkdir(parents=True,exist_ok=True)
def resolve(kind,name):
 d=json.loads((presets/kind/(name+'.json')).read_text())
 base=resolve(kind,d['inherits']) if d.get('inherits') else {}
 base.update(d);base.pop('inherits',None)
 return base
machine=resolve('machine','Creality Ender-3 V3 KE 0.4 nozzle')
machine['before_layer_change_gcode']=';BEFORE_LAYER_CHANGE\n;[layer_z]\n{if layer_z > 4.19 and layer_z < 4.21}\n;INSTALL TWO LID INSERTS AFTER 4.05 MM - TOPS BELOW SURFACE\nPAUSE\n{endif}\nG92 E0\n'
process=resolve('process','0.16mm Optimal @Creality Ender3V3KE')
process.update(curr_bed_type='Textured PEI Plate',name='Clock - 0.15 mm PLA - insert pause',print_settings_id='Clock - 0.15 mm PLA - insert pause',layer_height='0.15',initial_layer_print_height='0.15',adaptive_layer_height='0',wall_loops='3',bottom_shell_layers='4',top_shell_layers='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',initial_layer_speed='25',initial_layer_infill_speed='35',outer_wall_speed='60',inner_wall_speed='90',top_surface_speed='50',sparse_infill_speed='100',internal_solid_infill_speed='80',bridge_speed='25',enable_prime_tower='0',infill_combination='0',xy_hole_compensation='0',print_sequence='by layer')
filament=resolve('filament','Creality Generic PLA @Ender-3V3-all')
filament.update(filament_colour=['#FFFFFF'],filament_max_volumetric_speed=['8'],nozzle_temperature=['210'],nozzle_temperature_initial_layer=['210'])
for key in ['hot_plate_temp','hot_plate_temp_initial_layer','textured_plate_temp','textured_plate_temp_initial_layer']: filament[key]=['60']
for name,d in [('printer',machine),('process',process),('filament',filament)]:
 (out/(name+'.json')).write_text(json.dumps(d,indent=2))
print('Prepared flattened Ender-3 V3 KE / white PLA configuration; fixed 0.15 mm layers and conditional pause before 4.20 mm.')

subprocess.run([str(args.orca.resolve()), '--load-settings', str(out/'printer.json')+';'+str(out/'process.json'), '--load-filaments', str(out/'filament.json'), '--arrange', '1', '--outputdir', str(out), '--export-3mf', 'ESP32_Clock_Ender3V3KE_PLA_015mm.3mf', 'body.stl', 'lid.stl', 'sensor_cage.stl'], cwd=root/'stl', check=True)
