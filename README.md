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

## Firmware Updates

For a personalized clock, update from your local ESPHome YAML. This preserves
your private `secrets.yaml` and any local config edits:

```powershell
esphome upload esphome-smart-clock.yaml --device 192.168.1.99
```

Replace `192.168.1.99` with the clock IP address.

The GitHub release update entity checks public release binaries. Those binaries
are built in GitHub Actions with `secrets.example.yaml`, so they are useful as
reference/recovery artifacts but are not the normal update path for a device
that needs your local Wi-Fi/API secrets.

[![Import ESP32 Smart Clock update automation](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FNirBY%2FESP32_Smart_Clock%2Fblob%2Fmain%2Fdocs%2Fblueprints%2Fautomation%2Fesp32_smart_clock_auto_update.yaml)

The button imports a safe check/notify blueprint. It does not install public
GitHub firmware unless you explicitly enable that option.

## Calendar Agenda Announcements

Home Assistant can read today's events from a calendar, print a compact agenda
on the LED matrix, and optionally speak the same agenda through the clock
speaker. The automation can run every day at a selected time, from an
`input_button` helper, or both.

[![Import ESP32 Smart Clock calendar agenda automation](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FNirBY%2FESP32_Smart_Clock%2Fblob%2Fmain%2Fdocs%2Fblueprints%2Fautomation%2Fesp32_smart_clock_calendar_agenda.yaml)

Create an `input_button` helper if you want a dashboard button, then import the
blueprint and select your calendar, clock speaker, and ESPHome display action.

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
- [Home Assistant Dashboard](docs/wiki/Home-Assistant-Dashboard.md)
- [Calendar And Announcements](docs/wiki/Calendar-And-Announcements.md)
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

Upload over Wi-Fi by IP address:

```powershell
esphome upload esphome-smart-clock.yaml --device 192.168.1.99
```

Upload over Wi-Fi by IP address and keep logs open:

```powershell
esphome run esphome-smart-clock.yaml --device 192.168.1.99
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
- Hebrew MAX7219 font glyphs can be designed with [md_max72xx-font-designer](https://github.com/vasco65/md_max72xx-font-designer/tree/master).
- For audio noise or playback issues, see [Logs And Troubleshooting](docs/wiki/Logs-And-Troubleshooting.md) and [Audio And Music](docs/wiki/Audio-And-Music.md).
