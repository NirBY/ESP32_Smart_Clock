# Full wiring — ESPHome clock

![Direct USB-C supply wiring](../images/power-distribution.png)

USB-C supplies all 5 V loads directly in parallel. The sensor VCC connects only to ESP32 3V3; all grounds share the USB-C return.

![Complete wiring diagram](../images/wiring.png)

[High-resolution PNG](../images/wiring.png) · [Vector diagram](../images/wiring.svg) · [Two-sheet PDF](../hardware/clock-wiring.pdf) · [Editable KiCad schematic](../hardware/clock-wiring.kicad_sch). Signal assignments are taken from
`esphome-smart-clock.yaml`. Connections below are to **module labels**, not to
universal physical header positions. The photo wire colors are not a pin map.

**J1** is the separate USB-C power socket: its two wires feed the shared +5V and GND nets. **J2** is the USB-C port already on the ESP32 board, used for programming and USB power. Matching net labels are electrically connected.

| Source | Destination | Connection |
|---|---|---|
| Regulated USB-C input +5 V | ESP32 5V/VIN, MAX7219 VCC, NS4168 V | Parallel 5 V supply bus |
| Input GND | ESP32 GND, MAX7219 GND, NS4168 G, sensor GND | Common ground bus |
| ESP32 3V3 | Sensor VCC | 3.3 V only |
| ESP32 GPIO21 | Sensor SDA | I2C data |
| ESP32 GPIO22 | Sensor SCL | I2C clock |
| ESP32 GPIO23 | MAX7219 DIN | Direct wire |
| ESP32 GPIO18 | MAX7219 CLK | Direct wire |
| ESP32 GPIO5 | MAX7219 CS / LOAD | Direct wire; GPIO5 is a boot strapping pin |
| ESP32 GPIO25 | NS4168 DIN | I2S audio data |
| ESP32 GPIO26 | NS4168 BCL / BCLK | I2S bit clock |
| ESP32 GPIO27 | NS4168 LRC / WS | I2S word clock |
| NS4168 speaker + | Speaker + | Amplified output |
| NS4168 speaker − | Speaker − | Amplified output, **not GND** |

The four display tiles are already chained on the matrix PCB. Connect to its
**DIN input** end; leave the final DOUT unconnected. The sensor board combines
AHT20 (0x38) and BMP280 (configured 0x77) on the same SDA/SCL pair. Its I2C
pull-ups must go to 3.3 V, never 5 V.

The ESP32 connects directly to MAX7219 DIN, CLK and CS in this working build.
The NS4168 is a single I2S DAC/amplifier board.

Use only regulated 5 V input; this socket is not a battery charger. Verify its
wire polarity and voltage before connection. Do not connect 5 V to ESP32 3V3
or sensor VCC. Never connect either amplified speaker terminal to ground.
Keep the sensor outside the enclosure in its vented cage.

Disconnect external 5 V from ESP32 VIN before powering the ESP32 from PC USB,
unless the exact board has verified power-path isolation. For normal operation
use the common external 5 V supply and OTA. See [Hardware and Power](Hardware-And-Power.md)
for optional bulk capacitance and power troubleshooting. The supplied photos
are build references, not evidence that every hidden electrical connection is
correct. Follow the explicit pin map above.

The two sheets were exported with KiCad. These are logical module connections, not PCB layouts; symbol terminal numbers are internal identifiers, not physical package pin numbers.

To regenerate images, install KiCad and PyMuPDF, then run `python tools/draw_wiring.py --kicad-cli PATH_TO_KICAD_CLI` from the repository root. To regenerate the editable sheets, run `python tools/build_wiring_kicad.py`.
