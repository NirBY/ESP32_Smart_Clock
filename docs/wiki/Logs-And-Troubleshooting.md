# Logs And Troubleshooting

Start with logs. They will tell you if Wi-Fi, I2C sensors, display, or audio are failing.

## Log Levels

ESPHome log levels, from quiet to noisy:

- `NONE` disables logs for that tag.
- `ERROR` shows only errors.
- `WARN` shows warnings and errors.
- `INFO` shows normal boot, Wi-Fi, API, and status messages.
- `DEBUG` shows detailed component behavior and is useful while debugging.
- `VERBOSE` and `VERY_VERBOSE` are very noisy and should only be used briefly.

Log levels are compiled into the firmware from `esphome-smart-clock.yaml`. If you change them, compile and upload again.

Global level:

```yaml
logger:
  level: INFO
```

Per-module levels:

```yaml
logger:
  level: DEBUG
  logs:
    wifi: INFO
    api: INFO
    sensor: INFO
    audio: DEBUG
    i2s_audio.speaker: DEBUG
    speaker: DEBUG
    speaker_media_player: DEBUG
    media_player: DEBUG
    ring_buffer: DEBUG
```

Important rule: a module cannot be more detailed than the global level. For example, if `logger.level` is `INFO`, ESPHome will reject `audio: DEBUG`. Set the global level to `DEBUG`, then keep noisy modules such as `wifi`, `api`, and `sensor` at `INFO`.

## View Logs Over USB

Connect the ESP32 by USB and run:

```powershell
cd Z:\workspace\esp32_smart_clock
esphome logs esphome-smart-clock.yaml
```

If ESPHome asks for a port, choose the ESP32 COM port.

You can also force a specific COM port:

```powershell
esphome logs esphome-smart-clock.yaml --device COM5
```

Replace `COM5` with your real port from Windows Device Manager.

To upload and immediately keep the log open:

```powershell
esphome run esphome-smart-clock.yaml --device COM5
```

Use this when you need boot logs from the first seconds after flashing.

## View Logs Over Wi-Fi

After the device is already online:

```powershell
cd Z:\workspace\esp32_smart_clock
esphome logs esphome-smart-clock.yaml --device OTA
```

In Home Assistant, you can also open the ESPHome device and use **Logs**.

If OTA logs do not connect, use USB logs first. OTA logs only work after Wi-Fi and the ESPHome API are already connected.

## Useful Module Tags

For audio noise or playback problems, enable:

```yaml
logger:
  level: DEBUG
  logs:
    audio: DEBUG
    i2s_audio.speaker: DEBUG
    speaker: DEBUG
    speaker_media_player: DEBUG
    media_player: DEBUG
    ring_buffer: DEBUG
    wifi: INFO
    api: INFO
```

Then start playback and copy the log lines from a few seconds before playback starts until a few seconds after the noise starts. Useful lines include tags like `[audio]`, `[i2s_audio.speaker]`, `[speaker_media_player]`, and `[ring_buffer]`.

For Wi-Fi problems, use:

```yaml
logger:
  level: DEBUG
  logs:
    wifi: DEBUG
    api: INFO
```

For sensor problems, use:

```yaml
logger:
  level: DEBUG
  logs:
    i2c: DEBUG
    sensor: DEBUG
    aht10: DEBUG
    bmp280: DEBUG
```

For normal daily use, prefer `INFO` or reduce the audio modules back to `INFO` after debugging. DEBUG logging adds more serial output and can slightly increase CPU and flash usage.

## Sensors Show No Data

Look for I2C scan lines in the logs at boot.

Expected addresses:

```text
AHT20: 0x38
BMP280: 0x76 or 0x77
```

If no I2C devices are found:

- Check sensor VCC is connected to ESP32 `3V3`.
- Check GND is common with the ESP32.
- Check SDA is GPIO21.
- Check SCL is GPIO22.
- Keep I2C wires short.

If AHT20 works but BMP280 does not, change the BMP280 address near the top of `esphome-smart-clock.yaml`:

```yaml
substitutions:
  bmp280_address: "0x76"
```

Then compile and upload again.

## Common Existing Notes

- If MAX7219 text is mirrored or broken in the PlatformIO test, change `HARDWARE_TYPE` in `src/main.cpp`:
  - `MD_MAX72XX::FC16_HW`
  - `MD_MAX72XX::PAROLA_HW`
  - `MD_MAX72XX::GENERIC_HW`
- If you have only one 8x8 MAX7219 module, change `MAX_DEVICES` from `4` to `1` in `src/main.cpp`, and `num_chips` from `4` to `1` in `esphome-smart-clock.yaml`.
- If BMP280 is not found, check whether the board address is `0x76` or `0x77`. The PlatformIO firmware tries both. The ESPHome YAML uses `bmp280_address` near the top of the file; change it to the address shown by the I2C scan if needed.
- If AHT20 logs communication errors in ESPHome, keep `variant: AHT20` and check that the module is powered from 3V3 with SDA/SCL on GPIO21/GPIO22.
- If audio is noisy, keep I2S wires short and add bulk capacitance near the amplifier.
