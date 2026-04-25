# Audio And Music

## Current Audio Design

Audio playback is configured for low-memory stability on a normal ESP32 without PSRAM: mono, 16 kHz, smaller speaker buffers, and a smaller media-player buffer. This is best for TTS/announcements and simple Home Assistant audio. High-bitrate music streaming can still stress RAM; for direct music playback from phones/PCs, use the separate Bluetooth speaker firmware.

The ESPHome firmware uses:

- NS4168 I2S Class-D amplifier module
- `i2s_audio` speaker output
- `speaker` media player platform
- local `media/volume-beep.wav` for volume feedback

## Music Casting Options

There are two supported music paths:

| Mode | Firmware | Works from | Notes |
|---|---|---|---|
| Wi-Fi via Home Assistant | `esphome-smart-clock.yaml` | Home Assistant media browser, automations, TTS, Music Assistant, local/online media URLs | Best option if this is mainly a Home Assistant clock |
| Bluetooth A2DP speaker | PlatformIO env `bluetooth_speaker` | Android, iPhone, Windows, macOS, Linux | Direct pairing like a Bluetooth speaker, but this firmware does not expose the HA sensors/display controls |

Direct Wi-Fi casting from every phone/PC app is not the same protocol:

- Android/PC "Cast" usually means Chromecast, which this ESP32 firmware does not implement.
- iPhone Wi-Fi speaker casting usually means AirPlay, which this ESP32 firmware does not implement.
- Spotify Connect also requires a different receiver stack.

For universal phone/PC playback, use the Bluetooth firmware. For Home Assistant-controlled playback, use the ESPHome firmware.

## Play Music Over Wi-Fi From Home Assistant

After flashing `esphome-smart-clock.yaml`, the device appears as a Home Assistant media player. You can play TTS, audio URLs, or media from Home Assistant-supported integrations.

Example using a direct MP3 URL:

```yaml
action: media_player.play_media
target:
  entity_id: media_player.esp32_smart_clock_speaker
data:
  media_content_id: "https://example.com/song.mp3"
  media_content_type: music
```

The exact `media_player` entity ID may be different in your Home Assistant. Use Developer Tools > States to confirm it.

## Volume Beep

Changing the `Speaker` media-player volume plays a short local beep so you can hear the effective level immediately.

The beep file is `media/volume-beep.wav`. It is embedded into the ESPHome firmware at compile time, so if you change it, compile and upload again.

The current beep format is:

- mono
- 16-bit PCM WAV
- 16 kHz
- short fade-in/fade-out
- silence at the beginning and end to reduce pop/noise

The firmware ignores volume-change beep requests during the first 15 seconds after boot. This avoids a boot-time beep when Home Assistant restores the media-player volume.

## Speaker Wiring

| NS4168 module | ESP32 |
|---|---:|
| DIN | GPIO25 |
| BCLK | GPIO26 |
| LRC / WS | GPIO27 |
| VCC | 5V |
| GND | GND |

Speaker wires must connect only to the amplifier speaker output, not to the ESP32.

## Install Bluetooth Speaker Firmware

This turns the ESP32 into a direct Bluetooth music speaker named `ESP32 Smart Clock`.

This is an alternate firmware. It replaces ESPHome, so Home Assistant, Wi-Fi sensors, screen messages, and OTA updates will not work while this firmware is installed.

1. Install VS Code or Cursor.
2. Install the PlatformIO extension.
3. Open this folder.
4. Connect the ESP32 with a USB data cable.
5. In PlatformIO, choose environment `bluetooth_speaker`.
6. Click PlatformIO: Build.
7. Click PlatformIO: Upload.
8. Pair from Android, iPhone, Windows, macOS, or Linux with `ESP32 Smart Clock`.
9. Select it as the audio output device and play music.

Equivalent terminal commands:

```powershell
cd Z:\workspace\esp32_smart_clock
pio run -e bluetooth_speaker
pio run -e bluetooth_speaker -t upload
```

To go back to Home Assistant mode, flash `esphome-smart-clock.yaml` again from ESPHome.

## Audio Troubleshooting

If there is no sound:

- If logs show `Not enough memory` or `ESP_ERR_NO_MEM`, flash the latest ESPHome YAML.
- Check logs while playing audio.
- Confirm the amplifier has 5V power.
- Confirm all grounds are common.
- Try a lower volume first.
- Add a 470uF-1000uF capacitor near the amplifier between 5V and GND.
- Some NS4168-style boards expose a `CTRL`, `SD`, or channel-select pin. If your board exposes it, check the board specs and pull it to the required level.

If audio is noisy:

- Keep I2S wires short.
- Add bulk capacitance near the amplifier.
- Check that `DIN`, `BCLK`, and `LRCLK/WS` are not swapped.
- Capture audio logs as described in [Logs And Troubleshooting](Logs-And-Troubleshooting.md).
- Confirm what format Home Assistant is sending. The current ESPHome speaker pipeline is tuned for low-memory 16 kHz mono playback.

## Actual Amplifier Module

The module used in this build is an NS4168-based I2S Class-D amplifier board.

Datasheet:

https://www.chipsourcetek.com/Uploads/file/NS4168.pdf

The datasheet / module information describes:

- NS4168 I2S digital audio amplifier
- I2S digital input
- 3.0V-5.5V working voltage
- 2.5W output power at 5V and 4 ohm load
- 8kHz-96kHz automatic sampling-rate detection
- built-in high-pass filter and protection mechanisms
- optional left/right channel behavior through `CTRL`

Because the module supports automatic 8kHz-96kHz sampling-rate detection, the current `16000 Hz` firmware output should be inside the supported range. If decoded audio logs show valid PCM, but the speaker output is still white noise, the next suspects are I2S format, channel selection, or wiring rather than only bitrate.

Useful log line from a known-good decode path should look like:

```text
Decoded audio has 1 channels, 16000 Hz sample rate, and 16 bits per sample
```

If you hear white noise while logs show valid decoded audio, test these next:

- verify `DIN`, `BCLK`, and `LRC/WS` wiring again
- try very short wires between ESP32 and the amplifier
- check whether `CTRL` is floating and whether it needs GND/VCC for the selected channel
- test `channel: left` and `channel: right` in `esphome-smart-clock.yaml`
- test a different I2S communication format only one change at a time
