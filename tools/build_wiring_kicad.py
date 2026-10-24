"""Generate an editable module-level KiCad schematic; pins are module labels."""
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/hardware/clock-wiring.kicad_sch'
OUT.parent.mkdir(parents=True, exist_ok=True)
def uid(s): return str(uuid5(NAMESPACE_URL, 'esp32-clock-wiring/' + s))
def q(s): return json.dumps(str(s))
def effects(size=2): return f'(effects (font (size {size} {size})))'
lib, items = [], []
rootid = uid('root')

def text(x, y, s, size=2.2):
    items.append(f'(text {q(s)} (at {x} {y} 0) {effects(size)} (uuid {uid(s)}))')

def wire(a, b):
    items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {uid(str(a)+str(b))}))')

def label(x, y, s):
    items.append(f'(label {q(s)} (at {x} {y} 0) (effects (font (size 1.8 1.8)) (justify left bottom)) (uuid {uid(s+str(x)+str(y))}))')

def module(ref, name, x, y, w, h, pins):
    # Pin tuple: logical terminal name, side, offset down from top.
    sym = ref + '_module'
    body = f'(symbol "{sym}_0_1" (rectangle (start 0 0) (end {w} {-h}) (stroke (width 0.3) (type default)) (fill (type background))))'
    pin_defs, locs = [], {}
    for i, (name_, side, offset) in enumerate(pins, 1):
        px, angle = (-5, 0) if side == 'L' else (w+5, 180)
        pin_defs.append(f'(pin passive line (at {px} {-offset} {angle}) (length 5) (name {q(name_)} {effects(2.5)}) (number "{i}" {effects(0.7)}))')
        locs[name_] = (x+px, y+offset)
    lib.append(f'(symbol "Clock:{sym}" (pin_names (offset 1)) (pin_numbers hide) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 5 0) {effects()}) (property "Value" {q(name)} (at 0 2 0) {effects()}) {body} (symbol "{sym}_1_1" {"".join(pin_defs)}))')
    instance = f'(symbol (lib_id "Clock:{sym}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {uid(ref)}) (property "Reference" {q(ref)} (at {x+w/2} {y-7} 0) {effects(1.8)}) (property "Value" {q(name)} (at {x+w/2} {y-3} 0) {effects(2.3)})'
    for i in range(1, len(pins)+1): instance += f'(pin "{i}" (uuid {uid(ref+str(i))}))'
    instance += f'(instances (project "clock-wiring" (path "/{rootid}" (reference {q(ref)}) (unit 1)))))'
    items.append(instance)
    return locs

def net(pin, name, left=True):
    end = (pin[0]-9 if left else pin[0]+9, pin[1])
    wire(pin, end)
    label(end[0], end[1], name)

text(132, 10, 'ESP32 SMART CLOCK | MODULE WIRING', 4)
text(132, 17, 'Connect by printed terminal labels. GPIO numbers are not header positions.', 2.1)

esp = module('U1','ESP32 USB-C',24,40,43,132,[
    ('GPIO23','R',10),('GPIO18','R',20),('GPIO5','R',30),
    ('GPIO21','R',60),('GPIO22','R',70),
    ('GPIO25','R',100),('GPIO26','R',110),('GPIO27','R',120),
    ('5V / VIN','L',100),('GND','L',110),('3V3','L',120)])
module('J2','Onboard USB-C',29,80,33,13,[])
text(45.5,86,'PC: data + power',1.7)
power = module('J1','USB-C power socket',24,183,43,15,[
    ('+5V','R',4),('GND','R',12)])
net(power['+5V'],'+5V',False)
net(power['GND'],'GND',False)
buf = module('U2','5 V logic buffer*',100,40,40,38,[
    ('1A','L',10),('2A','L',20),('3A','L',30),
    ('1Y','R',10),('2Y','R',20),('3Y','R',30)])
display = module('U3','MAX7219 / INPUT',190,40,48,45,[
    ('DIN','L',10),('CLK','L',20),('CS / LOAD','L',30),
    ('VCC','R',30),('GND','R',40)])
sensor = module('U4','AHT20 + BMP280',190,96,48,30,[
    ('SDA','L',4),('SCL','L',14),('VCC','R',4),('GND','R',14)])
amp = module('U5','NS4168 amplifier',190,136,48,50,[
    ('DIN','L',4),('BCL / BCLK','L',14),('LRC / WS','L',24),
    ('V','L',34),('G','L',44),('SPK+','R',4),('SPK-','R',14)])
for gpio,a,b,d in [('GPIO23','1A','1Y','DIN'),('GPIO18','2A','2Y','CLK'),('GPIO5','3A','3Y','CS / LOAD')]:
    wire(esp[gpio],buf[a]); wire(buf[b],display[d])
for gpio,d in [('GPIO21','SDA'),('GPIO22','SCL')]: wire(esp[gpio],sensor[d])
for gpio,d in [('GPIO25','DIN'),('GPIO26','BCL / BCLK'),('GPIO27','LRC / WS')]: wire(esp[gpio],amp[d])
for pin,n in [('5V / VIN','+5V'),('GND','GND'),('3V3','3V3')]: net(esp[pin],n)
for part,pin,n in [(display,'VCC','+5V'),(display,'GND','GND'),(sensor,'VCC','3V3'),(sensor,'GND','GND')]: net(part[pin],n,False)
net(amp['V'],'+5V'); net(amp['G'],'GND')
net(amp['SPK+'],'SPK+',False); net(amp['SPK-'],'SPK-',False)
speaker = module('LS1','Speaker',110,178,38,20,[('+','L',5),('-','L',15)])
net(speaker['+'],'SPK+');net(speaker['-'],'SPK-')
text(130, 131, 'I2S AUDIO', 2)
text(125, 120, 'I2C / 3.3 V', 2)
text(126, 86, '*74AHCT125: see buffer sheet', 1.8)
text(130, 203, 'SPK- is an amplifier output. NEVER connect it to GND.', 2.3)
text(132, 214, 'J1: external regulated 5 V supply. J2: ESP32 programming USB-C.', 2.3)
text(132, 221, 'All identical net labels connect together. Sensor VCC uses 3V3 only.', 2.1)
text(132, 228, 'Disconnect external VIN power before powering ESP32 from PC USB.', 2.1)
text(132, 237, 'Module-level schematic | firmware: esphome-smart-clock.yaml | NirBY', 1.7)

OUT.write_text(f'(kicad_sch (version 20250114) (generator "clock_wiring_builder") (uuid {rootid}) (paper "User" 270 245) (lib_symbols {"".join(lib)}) {"".join(items)} (sheet_instances (path "/" (page "1"))))',encoding='utf-8')
print(OUT)

# Explicit supply distribution: each load is wired directly to the USB supply.
lib.clear(); items.clear()
rootid = uid('power-root')
text(132,10,'USB-C POWER | DIRECT SUPPLY DISTRIBUTION',3.8)
text(132,18,'All 5 V loads connect in parallel to J1. ESP32 3V3 powers only the sensor.',2.1)
source=module('J1','USB-C power socket',20,40,48,35,[('+5V','R',10),('GND','R',20)])
loads=[]
for ref,name,y in [('U1','ESP32',40),('U3','MAX7219 display',85),('U5','NS4168 amplifier',130)]:
 pins=[('VIN/5V' if ref=='U1' else 'VCC/5V','L',10),('GND','L',20)]
 if ref=='U1':pins.append(('3V3','R',25))
 loads.append(module(ref,name,150,y,48,32,pins))
sens=module('U4','AHT20 + BMP280',150,180,48,32,[('GND','L',20),('VCC/3V3','R',10)])
wire(source['+5V'],(90,50));wire(source['GND'],(100,60))
for x,ys in [(90,[50,95,140]),(100,[60,105,150,200])]:
 for a,b in zip(ys,ys[1:]):wire((x,a),(x,b))
 for y in ys:
  items.append(f'(junction (at {x} {y}) (diameter 1) (color 0 0 0 0) (uuid {uid("junction"+str(x)+str(y))}))')
for load,y in zip(loads,[40,85,130]):
 pin=load.get('VIN/5V',load.get('VCC/5V'))
 wire((90,y+10),pin);wire((100,y+20),load['GND'])
wire((100,200),sens['GND'])
wire(loads[0]['3V3'],(235,65));wire((235,65),(235,190));wire((235,190),sens['VCC/3V3'])
label(90,35,'+5V');wire((90,35),(90,50))
label(100,42,'GND');wire((100,42),(100,60))
label(235,90,'3V3 ONLY')
text(48,88,'Regulated 5 V input',2)
text(132,223,'Dots mark connected branches. Crossings without dots are NOT connected.',2)
text(132,231,'Never join +5V and 3V3. Disconnect external VIN before PC USB power.',2)
OUT=OUT.with_name('power-distribution.kicad_sch')
OUT.write_text(f'(kicad_sch (version 20250114) (generator "clock_wiring_builder") (uuid {rootid}) (paper "User" 270 245) (lib_symbols {"".join(lib)}) {"".join(items)} (sheet_instances (path "/" (page "1"))))',encoding='utf-8')

# Companion sheet expands the functional buffer shown on the main overview.
lib.clear(); items.clear()
rootid = uid('buffer-root')
text(105, 10, 'DISPLAY BUFFER | 74AHCT125', 3.8)
text(105, 18, 'Recommended for guaranteed 3.3 V to 5 V logic levels', 2)
buffer = module('U2','74AHCT125',85,40,55,130,[
    ('1A','L',10),('2A','L',25),('3A','L',40),
    ('1Y','R',10),('2Y','R',25),('3Y','R',40),
    ('VCC','L',60),('GND','L',75),
    ('/1OE','R',60),('/2OE','R',75),('/3OE','R',90),
    ('4A','L',105),('/4OE','L',120),('4Y','R',120)])
for terminal,name in [('1A','GPIO23'),('2A','GPIO18'),('3A','GPIO5'),('VCC','+5V'),('GND','GND'),('4A','GND'),('/4OE','+5V')]: net(buffer[terminal],name)
for terminal,name in [('1Y','DISPLAY_DIN'),('2Y','DISPLAY_CLK'),('3Y','DISPLAY_CS'),('/1OE','GND'),('/2OE','GND'),('/3OE','GND')]: net(buffer[terminal],name,False)
x,y=buffer['4Y']; items.append(f'(no_connect (at {x} {y}) (uuid {uid("unused-buffer-output")}))')
cap=module('C1','100 nF bypass',30,180,45,25,[('1','L',7),('2','L',18)])
net(cap['1'],'+5V');net(cap['2'],'GND')
text(137,190,'Place C1 close to U2 VCC/GND.',2)
text(105,217,'Terminal names shown; use your IC package datasheet for pin numbers.',1.9)
text(105,225,'/OE means active LOW. Tie unused input 4A LOW and /4OE HIGH.',1.9)
text(105,233,'The direct-wired prototype does not include this extra buffer.',1.9)
OUT=OUT.with_name('display-buffer.kicad_sch')
OUT.write_text(f'(kicad_sch (version 20250114) (generator "clock_wiring_builder") (uuid {rootid}) (paper "User" 210 245) (lib_symbols {"".join(lib)}) {"".join(items)} (sheet_instances (path "/" (page "1"))))',encoding='utf-8')
print(OUT)
