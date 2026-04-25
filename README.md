# ESP32 Smart Clock

ESP32 smart clock project with an 8x32 MAX7219 LED matrix, AHT20/BMP280 indoor sensors, an NS4168 I2S audio amplifier module, and Home Assistant control through ESPHome.

For normal use, install the **ESPHome smart clock firmware** from `esphome-smart-clock.yaml`.

## Quick Start

1. Copy `secrets.example.yaml` to `secrets.yaml`.
2. Put your Wi-Fi and ESPHome API key in `secrets.yaml`.
3. Connect the ESP32 with a USB data cable.
4. Compile and upload:

   ```powershell
   cd Z:\workspace\esp32_smart_clock
   esphome compile esphome-smart-clock.yaml
   esphome upload esphome-smart-clock.yaml
   ```

5. Add the discovered ESPHome device in Home Assistant.

If upload fails, hold **BOOT** while upload starts, then release **BOOT** when writing begins.

## Firmware Options

| Firmware | Use for | Home Assistant | Wi-Fi | Bluetooth music |
|---|---|---:|---:|---:|
| ESPHome smart clock | Clock, sensors, screen messages, alarm, Home Assistant speaker | Yes | Yes | No |
| Bluetooth speaker | Direct Bluetooth music from phone/PC | No | No | Yes |
| PlatformIO hardware test | Checking wiring and modules | No | No | No |

The ESP32 runs one firmware at a time. Flashing the Bluetooth speaker firmware replaces ESPHome. Flashing ESPHome again replaces the Bluetooth speaker firmware.

## Hardware Summary

- ESP32 30-pin dev board, CH340C, USB-C, HW-394 style board
- MAX7219 8x32 LED matrix
- NS4168 I2S Class-D audio amplifier module with speaker
- AHT20 + BMP280 I2C temperature, humidity, and pressure board
- 5V 3A USB-C power supply

Main pins:

| Function | ESP32 pin |
|---|---:|
| I2C SDA | GPIO21 |
| I2C SCL | GPIO22 |
| MAX7219 DIN | GPIO23 |
| MAX7219 CLK | GPIO18 |
| MAX7219 CS/LOAD | GPIO5 |
| I2S DATA | GPIO25 |
| I2S BCLK | GPIO26 |
| I2S LRCLK/WS | GPIO27 |

All module grounds must be connected together.

## Wiki

Detailed documentation was moved out of the README:

- [Wiki Home](docs/wiki/Home.md)
- [Hardware And Power](docs/wiki/Hardware-And-Power.md)
- [Install And Home Assistant](docs/wiki/Install-And-Home-Assistant.md)
- [Display Behavior](docs/wiki/Display-Behavior.md)
- [Audio And Music](docs/wiki/Audio-And-Music.md)
- [Logs And Troubleshooting](docs/wiki/Logs-And-Troubleshooting.md)
- [Development And Releases](docs/wiki/Development-And-Releases.md)

## Common Commands

Open logs over USB:

```powershell
esphome logs esphome-smart-clock.yaml --device COM5
```

Upload and keep logs open:

```powershell
esphome run esphome-smart-clock.yaml --device COM5
```

Build the PlatformIO hardware test:

```powershell
pio run -e esp32dev
```

Build the Bluetooth speaker firmware:

```powershell
pio run -e bluetooth_speaker
```

## Notes

- Do not commit `secrets.yaml`; it is ignored by git.
- `GPIO5` is an ESP32 strapping pin. It is currently used for MAX7219 CS/LOAD, so avoid external pull-up/down effects on that pin.
- For audio noise or playback issues, see [Logs And Troubleshooting](docs/wiki/Logs-And-Troubleshooting.md) and [Audio And Music](docs/wiki/Audio-And-Music.md).
