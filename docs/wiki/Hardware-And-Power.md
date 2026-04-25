# Hardware And Power

## Hardware

- ESP32 30-pin dev board, CH340C, USB-C, HW-394 style board
- MAX7219 8x32 LED matrix board, usually four chained 8x8 modules
- NS4168 I2S Class-D audio amplifier module with speaker
- AHT20 + BMP280 I2C temperature, humidity, and pressure board
- 5V 3A USB-C power supply

## Pin Map

| Function | Module pin | ESP32 pin | Notes |
|---|---:|---:|---|
| I2C SDA | AHT20/BMP280 SDA | GPIO21 | Sensor board logic must be 3.3V-safe |
| I2C SCL | AHT20/BMP280 SCL | GPIO22 | Sensor board logic must be 3.3V-safe |
| SPI MOSI | MAX7219 DIN | GPIO23 | Use short wires |
| SPI CLK | MAX7219 CLK | GPIO18 | Use short wires |
| SPI CS | MAX7219 CS/LOAD | GPIO5 | Boot strap pin; keep external pull effects low |
| I2S DATA | NS4168 DIN | GPIO25 | Audio data out |
| I2S BCLK | NS4168 BCLK | GPIO26 | Audio bit clock |
| I2S L/R CLK | NS4168 LRC/WS | GPIO27 | Audio word select |

All module grounds must be connected together.

## Power

- Power the ESP32 through USB-C during programming.
- For normal use, use a stable 5V supply sized for the LED matrix and speaker. 5V 3A is a good starting point.
- MAX7219 VCC: 5V.
- NS4168 VCC: 3.0V-5.5V; this project uses 5V.
- AHT20/BMP280 VCC: 3V3, unless your exact sensor module explicitly supports 5V logic.
- Add a 470uF-1000uF electrolytic capacitor near the amplifier and LED matrix between 5V and GND if audio or display flickers.
- If the MAX7219 is unreliable from ESP32 3.3V logic, add a 3.3V-to-5V logic level shifter on DIN, CLK, and CS.

Do not connect an external 5V supply to VIN while the ESP32 is also powered from USB unless the board documentation says that exact board has safe power-path isolation.

## USB + VIN Safety

Do not assume it is safe to connect both USB from the PC and an external 5V supply to VIN at the same time.

Some ESP32 dev boards isolate USB 5V and VIN with a diode or power-path circuit. Many low-cost CH340/USB-C boards do not document this clearly, and back-feeding 5V into the PC USB port can damage the USB port, the ESP32 board, or the power supply.

Safer options:

- During programming: power the ESP32 from USB only, and disconnect external 5V from VIN.
- During full hardware testing: connect PC USB for data, power the LED matrix/amplifier from the external 5V supply, and connect all grounds together. Do not connect that external 5V to ESP32 VIN unless you have verified the board schematic.
- Best permanent setup: power the ESP32 from the same regulated 5V supply through its 5V/VIN pin only, and use OTA updates after the first flash.
- If you must use USB data and external 5V together, use a USB data-only cable or a USB power blocker so the PC 5V line is not connected.

## GPIO5 Note

`GPIO5` is used as MAX7219 CS/LOAD. It is an ESP32 strapping pin, so ESPHome warns about it at boot. The current hardware keeps it as-is. Avoid external pull-up or pull-down circuits on this pin that could affect boot mode.

## PSRAM Note

On PSRAM-enabled modules, `GPIO16` can be connected to internal PSRAM and may not be usable as a normal GPIO. The current HW-394 style board is treated as a normal ESP32 dev board with 4MB flash.

## Audio Amplifier Module

The actual I2S amplifier module used in this build is NS4168-based.

Datasheet:

https://www.chipsourcetek.com/Uploads/file/NS4168.pdf

Relevant module notes:

- I2S serial digital audio input.
- Working voltage: 3.0V-5.5V.
- Output power: 2.5W at 5V with a 4 ohm speaker.
- Automatic sampling-rate detection, advertised for 8kHz-96kHz.
- Built-in high-pass filter and protection features.
- Left/right channel selection may depend on the module `CTRL` pin wiring or board defaults.

If playback sounds like white noise, check I2S wiring first: `DIN`, `BCLK`, and `LRC/WS` must not be swapped. Also check whether the module exposes `CTRL`; if it does, the selected channel level may matter.
