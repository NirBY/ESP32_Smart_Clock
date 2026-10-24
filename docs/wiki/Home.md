# ESP32 Smart Clock Wiki

Follow [local setup for Windows, macOS or Linux](Local-Setup.md) first. Run commands from your cloned repository root with the appropriate environment active. `CLOCK_DEVICE` means your actual USB port or network hostname/IP.

This wiki contains the detailed project documentation. Keep `README.md` short and link here for the full setup and troubleshooting notes.

## Pages

- [Local setup — Windows, macOS and Linux](Local-Setup.md)
- [Home Assistant MCP](../home-assistant-mcp/README.md)
- [Wiring diagram](Wiring.md)

- [Hardware And Power](Hardware-And-Power.md)
- [Install And Home Assistant](Install-And-Home-Assistant.md)
- [Home Assistant Dashboard](Home-Assistant-Dashboard.md)
- [Calendar And Announcements](Calendar-And-Announcements.md)
- [Display Behavior](Display-Behavior.md)
- [Audio And Music](Audio-And-Music.md)
- [Logs And Troubleshooting](Logs-And-Troubleshooting.md)
- [Development And Releases](Development-And-Releases.md)

- [Timer](Timer.md)
- [Complete Wiring](Wiring.md)
- [Parts and purchase links](Shopping-List.md)
- [Gallery](Gallery.md)
- [Home Assistant MCP](../home-assistant-mcp/README.md)

## Firmware Options

For normal use, install the **ESPHome smart clock firmware** from `esphome-smart-clock.yaml`.

| Firmware | Use for | Home Assistant | Wi-Fi | Bluetooth music |
|---|---|---:|---:|---:|
| ESPHome smart clock | Clock, sensors, screen messages, alarm, Home Assistant speaker | Yes | Yes | No |
| Bluetooth speaker | Direct Bluetooth music from phone/PC | No | No | Yes |
| PlatformIO hardware test | Checking wiring and modules | No | No | No |

The ESP32 runs one firmware at a time. Flashing the Bluetooth speaker firmware replaces ESPHome. Flashing ESPHome again replaces the Bluetooth speaker firmware.

If this is your first install, start with **ESPHome smart clock**.

## Main Files

- `esphome-smart-clock.yaml` - normal Home Assistant smart clock firmware.
- `platformio.ini` - PlatformIO environments for hardware test and Bluetooth speaker firmware.
- `src/main.cpp` - PlatformIO hardware test firmware.
- `src/bt_a2dp_sink.cpp` - Bluetooth speaker firmware.
- `media/volume-beep.wav` - local volume feedback beep used by ESPHome.
- `secrets.example.yaml` - template for private ESPHome secrets.

## Quick Commands

Compile ESPHome:

```sh
esphome compile esphome-smart-clock.yaml
```

Upload ESPHome:

```sh
esphome upload esphome-smart-clock.yaml
```

Upload ESPHome over Wi-Fi by IP address:

```sh
esphome upload esphome-smart-clock.yaml --device CLOCK_DEVICE
```

Open ESPHome logs:

```sh
esphome logs esphome-smart-clock.yaml --device CLOCK_DEVICE
```

Build PlatformIO hardware test:

```sh
pio run -e esp32dev
```

Build Bluetooth speaker firmware:

```sh
pio run -e bluetooth_speaker
```

For the isolated PlatformIO environment setup, see [the README](../../README.md#common-commands).
