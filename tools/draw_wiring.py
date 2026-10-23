"""Draw the firmware-derived module wiring diagram (requires matplotlib)."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

root = Path(__file__).resolve().parents[1]
fig, ax = plt.subplots(figsize=(16,12))
fig.patch.set_facecolor('#f7f9fc')
ax.set(xlim=(0,160), ylim=(120,0)); ax.axis('off')
def text(x,y,t,size=11,**kw): ax.text(x,y,t,fontsize=size,fontfamily='DejaVu Sans',va='center',color='#172b45',**kw)
def box(x,y,w,h,title):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.6,rounding_size=1.6',facecolor='white',edgecolor='#9aaec5',lw=1.4))
 text(x+2,y+3,title,13,weight='bold')
def line(x1,x2,y,label,color='#187c96'):
 ax.plot([x1,x2],[y,y],color=color,lw=2)
 ax.plot([x1,x2],[y,y],'o',color=color,ms=3)
 text((x1+x2)/2,y-1.7,label,9,ha='center')
text(5,5,'ESP32 SMART CLOCK  /  COMPLETE MODULE WIRING',21,weight='bold')
text(5,9,'Firmware GPIO labels • not physical header positions • all GND labels join the same net',11)
box(5,16,36,76,'ESP32 USB-C dev board')
box(91,16,63,24,'MAX7219 8 × 32 — INPUT side')
for y,gpio,pin in [(25,'GPIO23','DIN'),(31,'GPIO18','CLK'),(37,'GPIO5','CS / LOAD')]:
 text(23,y,gpio,11); line(41,91,y,'3.3 V → 5 V buffer*'); text(93,y,pin,11)
box(91,45,63,18,'AHT20 + BMP280 — external cage')
for y,gpio,pin in [(54,'GPIO21','SDA'),(60,'GPIO22','SCL')]:
 text(23,y,gpio); line(41,91,y,'I2C / 3.3 V'); text(93,y,pin)
box(91,68,36,24,'NS4168 I2S amplifier')
for y,gpio,pin in [(77,'GPIO25','DIN'),(83,'GPIO26','BCL / BCLK'),(89,'GPIO27','LRC / WS')]:
 text(23,y,gpio); line(41,91,y,'I2S / 3.3 V'); text(93,y,pin,10)
box(136,68,18,24,'Speaker')
ax.plot([127,136],[80,80],color='#b74752',lw=2); text(131.5,77,'+',12,ha='center')
ax.plot([127,136],[86,86],color='#485566',lw=2); text(131.5,89,'−',12,ha='center')
text(6,94,'POWER NETS — join every terminal on each row',12,weight='bold')
for y,label,targets,color in [
 (99,'+5 V','USB-C input +  →  ESP32 5V/VIN • MAX7219 VCC • NS4168 V • buffer VCC','#bf394d'),
 (104,'3V3','ESP32 3V3  →  sensor VCC (and its I2C pull-ups)','#c17a10'),
 (109,'GND','USB-C input −  →  ESP32 GND • MAX7219 GND • NS4168 G • sensor GND • buffer GND','#485566')]:
 text(6,y,label,12,weight='bold'); ax.plot([17,22],[y,y],color=color,lw=3); text(24,y,targets,10)
text(5,114,'*Use 74AHCT125 or equivalent TTL-input buffer; direct 3.3 V signals are not guaranteed by MAX7219 specifications.',9)
text(5,118,'Disconnect external VIN power before PC USB. Speaker − is NOT ground. Full notes and buffer connections: docs/wiki/Wiring.md',9)
fig.subplots_adjust(left=.015,right=.99,top=.99,bottom=.015)
for ext in ('png','svg'): fig.savefig(root/'docs/images'/('wiring.'+ext),dpi=150)
print('Wiring PNG and SVG generated')
