# ESP32 Smart Clock Wiki

This wiki contains the detailed project documentation. Keep `README.md` short and link here for the full setup and troubleshooting notes.

## Pages

- [Hardware And Power](Hardware-And-Power.md)
- [Install And Home Assistant](Install-And-Home-Assistant.md)
- [Display Behavior](Display-Behavior.md)
- [Audio And Music](Audio-And-Music.md)
- [Logs And Troubleshooting](Logs-And-Troubleshooting.md)
- [Development And Releases](Development-And-Releases.md)

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

```powershell
cd Z:\workspace\esp32_smart_clock
esphome compile esphome-smart-clock.yaml
```

Upload ESPHome:

```powershell
esphome upload esphome-smart-clock.yaml
```

Open ESPHome logs:

```powershell
esphome logs esphome-smart-clock.yaml --device COM5
```

Build PlatformIO hardware test:

```powershell
pio run -e esp32dev
```

Build Bluetooth speaker firmware:

```powershell
pio run -e bluetooth_speaker
```
