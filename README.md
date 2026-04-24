# ESP32 Smart Clock

ESP32 smart clock project for PlatformIO hardware testing and Home Assistant control.

## Which Firmware Should I Install?

For normal use, install the **ESPHome smart clock firmware** from `esphome-smart-clock.yaml`.

| Firmware | Use for | Home Assistant | Wi-Fi | Bluetooth music |
|---|---|---:|---:|---:|
| ESPHome smart clock | Clock, sensors, screen messages, alarm, Home Assistant speaker | Yes | Yes | No |
| Bluetooth speaker | Direct Bluetooth music from phone/PC | No | No | Yes |
| PlatformIO hardware test | Checking wiring and modules | No | No | No |

The ESP32 runs one firmware at a time. Flashing the Bluetooth speaker firmware replaces ESPHome. Flashing ESPHome again replaces the Bluetooth speaker firmware.

If this is your first install, start with **ESPHome smart clock**.

## Hardware

- ESP32 30-pin dev board, CH340C, USB-C, HW-394 style board
- MAX7219 8x32 LED matrix board, usually four chained 8x8 modules
- NS4168 I2S DAC amplifier with speaker
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
| I2S L/R CLK | NS4168 LRCLK/LRC/WS | GPIO27 | Audio word select |

All module grounds must be connected together.

## Power

- Power the ESP32 through USB-C during programming.
- For normal use, use a stable 5V supply sized for the LED matrix and speaker. 5V 3A is a good starting point.
- MAX7219 VCC: 5V.
- NS4168 VCC: 5V.
- AHT20/BMP280 VCC: 3V3, unless your exact sensor module explicitly supports 5V logic.
- Add a 470uF-1000uF electrolytic capacitor near the amplifier and LED matrix between 5V and GND if audio or display flickers.
- If the MAX7219 is unreliable from ESP32 3.3V logic, add a 3.3V-to-5V logic level shifter on DIN, CLK, and CS.

Do not connect an external 5V supply to VIN while the ESP32 is also powered from USB unless the board documentation says that exact board has safe power-path isolation. See the USB + VIN note below.

## Current Firmware

`src/main.cpp` is a PlatformIO hardware test:

- scans I2C
- reads AHT20 humidity/temperature
- reads BMP280 temperature/pressure
- scrolls readings on the MAX7219 matrix
- plays a short I2S tone through the NS4168 speaker

This test firmware does not connect to Wi-Fi or Home Assistant.

## Home Assistant Control

For Home Assistant, use `esphome-smart-clock.yaml` with ESPHome. It exposes:

- `Temperature`, `Humidity`, and `Pressure` sensors
- `Screen Message` text entity
- `Display Brightness` number entity, range `0`-`15`
- `Speaker` media player entity for Home Assistant TTS/audio
- `Alarm Enabled`, `Alarm Hour`, and `Alarm Minute` entities as alarm controls
- an `esphome.alarm_triggered` Home Assistant event when the alarm time is reached
- API actions:
  - `esphome.esp32_smart_clock_show_message`
  - `esphome.esp32_smart_clock_clear_message`

Important limitations:

- This hardware has a speaker only, not a microphone. It can play voice/TTS sent from Home Assistant, but it cannot listen for voice commands unless you add an I2S microphone.
- Wi-Fi music playback is through Home Assistant/ESPHome as a network media player. It is not a native Chromecast, AirPlay, Spotify Connect, or DLNA speaker.
- The alarm trigger sets the matrix to `ALARM` and fires an `esphome.alarm_triggered` event. Use a Home Assistant automation to play TTS or `media_player.play_media` on the `Speaker` entity.
- To allow the device to fire Home Assistant events, open the ESPHome integration device settings in Home Assistant and enable "Allow the device to perform Home Assistant actions".
- The ESPHome config uses the Google Font `Noto Sans Hebrew`, so first compile needs internet access from the ESPHome builder.

## Display Behavior

The display always returns to the clock when a temporary screen has expired or when required data is missing.

Default screen:

- Shows clock as `HH:MM:SS` using a custom 32x8 pixel layout across the full LED matrix.
- Time is synced with NTP/SNTP.
- NTP refresh interval is `1h`.
- Before valid time is available, the display shows `--:--`.

Temporary screens:

| Trigger | Display | Duration |
|---|---|---:|
| Home Assistant screen message | message text | 10 seconds |
| Temperature/humidity/pressure data | `temp humidity pressure` | 3 seconds every 30 seconds |
| Music playback starts | `MUSIC` | up to 10 seconds |
| TTS/announcement starts | `SPEAKER` | up to 10 seconds |
| Music pauses/stops | returns to clock | immediately |
| Wi-Fi disconnected | `NO WIFI` | 3 seconds every 30 seconds |
| Top of each hour | day/date | 3 seconds |
| Invalid/missing data | clock | immediately |

The ESPHome speaker media player does not expose song-title metadata to the MAX7219 display. If you want a song name shown, send it from Home Assistant as a screen message; it will show for 10 seconds and return to the clock.

Short English/number messages use a custom 3x7 pixel renderer that spreads the text across all 32 columns. Longer supported messages scroll across the full matrix. Hebrew screen messages use the `Noto Sans Hebrew` font; the display helper reverses UTF-8 Hebrew text before drawing it so short right-to-left messages can be read on the left-to-right MAX7219 matrix.

Display brightness can be changed from Home Assistant with the `Display Brightness` number entity. `0` is dimmest, `15` is brightest.

Brightness changes are sent directly to the MAX7219 chips at runtime and are also re-applied after boot when the restored Home Assistant value is available.

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

## First-Time Install With ESPHome

Use this for the normal smart clock firmware.

### 1. Install The ESPHome Tool

On Windows, open PowerShell and run:

```powershell
python -m pip install esphome
```

Verify it installed:

```powershell
esphome version
```

If `esphome` is not found, try:

```powershell
python -m esphome version
```

### 2. Configure Wi-Fi

Create your private `secrets.yaml` from the dummy example, then edit it:

```powershell
cd Z:\workspace\esp32_smart_clock
Copy-Item secrets.example.yaml secrets.yaml
```

Set your real Wi-Fi name and password:

```yaml
wifi_ssid: "YOUR_WIFI_NAME"
wifi_password: "YOUR_WIFI_PASSWORD"
fallback_ap_password: "choose-a-password"
api_encryption_key: "paste-the-key-generated-by-esphome"
```

For `api_encryption_key`, the easiest path is to create a temporary ESPHome device in Home Assistant and copy the generated key, or use any valid ESPHome API encryption key.

Do not commit `secrets.yaml`. It is ignored by git. Only `secrets.example.yaml` should be pushed to GitHub.

### 3. Connect USB

1. Connect the ESP32 to the PC with a USB data cable.
2. Use USB power only while flashing.
3. If the LED matrix and speaker need external 5V during testing, keep grounds connected, but do not connect external 5V to VIN while USB is connected unless your exact ESP32 board safely supports it.

### 4. Compile And Upload

Run:

```powershell
cd Z:\workspace\esp32_smart_clock
esphome compile esphome-smart-clock.yaml
esphome upload esphome-smart-clock.yaml
```

When ESPHome asks, choose the USB serial port.

If upload fails, hold **BOOT** while upload starts, then release **BOOT** when writing begins.

### 5. Add To Home Assistant

1. Wait for the ESP32 to reboot.
2. It should connect to the Wi-Fi from `secrets.yaml`.
3. In Home Assistant, open Settings > Devices & services.
4. Add the discovered `ESP32 Smart Clock` ESPHome device.
5. Enter the API encryption key if Home Assistant asks.
6. Open the ESPHome integration device settings and enable "Allow the device to perform Home Assistant actions" if you want alarm events to trigger Home Assistant automations.

## Future Updates Over Wi-Fi

After the first USB flash, ESPHome OTA updates usually work over Wi-Fi.

From PowerShell:

```powershell
cd Z:\workspace\esp32_smart_clock
esphome upload esphome-smart-clock.yaml
```

ESPHome will upload wirelessly if the device is online. If OTA fails or the device is offline, connect USB and upload again.

From Home Assistant:

1. Install the ESPHome add-on if it is not installed.
2. Open ESPHome.
3. Import or create the `esp32-smart-clock` device.
4. Use the same YAML from `esphome-smart-clock.yaml`.
5. Click Install.
6. Choose Wirelessly for OTA updates, or USB/serial for first install.

## Windows + VS Code + PlatformIO Install

Use this if you want to work from VS Code on Windows.

Important: PlatformIO installs the PlatformIO firmwares in `platformio.ini`. The normal Home Assistant smart clock firmware is ESPHome, so install it from the VS Code terminal with the `esphome` command.

### 1. Install Tools

1. Install Python 3 from https://www.python.org/downloads/windows/.
2. During Python install, enable "Add python.exe to PATH".
3. Install VS Code from https://code.visualstudio.com/.
4. Open VS Code.
5. Open Extensions.
6. Install **PlatformIO IDE**.
7. Open a new VS Code terminal: Terminal > New Terminal.
8. Install ESPHome:

   ```powershell
   python -m pip install esphome
   ```

9. Verify the tools:

   ```powershell
   python --version
   pio --version
   esphome version
   ```

If `esphome` is not found, use:

```powershell
python -m esphome version
```

### 2. Open The Project

1. In VS Code, choose File > Open Folder.
2. Open:

   ```text
   Z:\workspace\esp32_smart_clock
   ```

3. Wait for PlatformIO to load the project.
4. Connect the ESP32 with a USB data cable.
5. Check Windows Device Manager if needed. CH340 boards usually appear as a `USB-SERIAL CH340` COM port.

### 3. Install The Normal ESPHome Smart Clock Firmware

This is the recommended first install.

1. Edit `secrets.yaml` with your Wi-Fi and API key.
2. In the VS Code terminal, run:

   ```powershell
   cd Z:\workspace\esp32_smart_clock
   esphome compile esphome-smart-clock.yaml
   esphome upload esphome-smart-clock.yaml
   ```

3. Choose the ESP32 COM port when ESPHome asks.
4. If upload fails, hold **BOOT** while upload starts, then release **BOOT** when writing begins.
5. After flashing, add `ESP32 Smart Clock` in Home Assistant under Settings > Devices & services.

After the first USB install, future ESPHome uploads can usually happen over Wi-Fi:

```powershell
cd Z:\workspace\esp32_smart_clock
esphome upload esphome-smart-clock.yaml
```

## GitHub Releases

The repository includes a GitHub Actions workflow that builds and verifies firmware when you push a version tag.

The workflow:

- creates CI-only dummy `secrets.yaml` from `secrets.example.yaml`
- validates and compiles `esphome-smart-clock.yaml`
- builds the PlatformIO hardware test firmware
- builds the PlatformIO Bluetooth speaker firmware
- uploads all firmware binaries to a GitHub Release

Create a new release:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

Use a new tag for each release, for example `v1.0.1`, `v1.1.0`, or `v2.0.0`.

### 4. Install The PlatformIO Hardware Test From VS Code

This replaces ESPHome until you flash ESPHome again.

1. Open the PlatformIO sidebar.
2. Under Project Tasks, select environment `esp32dev`.
3. Click Build.
4. Click Upload.
5. Click Monitor to open Serial Monitor at 115200 baud.

Equivalent terminal commands:

```powershell
cd Z:\workspace\esp32_smart_clock
pio run -e esp32dev
pio run -e esp32dev -t upload
pio device monitor -b 115200
```

### 5. Install Bluetooth Speaker Firmware From VS Code

This replaces ESPHome until you flash ESPHome again.

1. Open the PlatformIO sidebar.
2. Under Project Tasks, select environment `bluetooth_speaker`.
3. Click Build.
4. Click Upload.
5. Pair Android, iPhone, or PC with `ESP32 Smart Clock`.

Equivalent terminal commands:

```powershell
cd Z:\workspace\esp32_smart_clock
pio run -e bluetooth_speaker
pio run -e bluetooth_speaker -t upload
```

## Emulator / Simulation

You can use an emulator for partial testing, but not for full hardware verification.

Recommended simulator: **Wokwi**.

What you can reasonably test in Wokwi:

- ESP32 boot and serial logs
- basic Arduino/PlatformIO firmware logic
- GPIO wiring mistakes
- SPI wiring to a MAX7219-style LED matrix
- some I2C sensor behavior, depending on available Wokwi parts or custom simulation examples

What you should not trust an emulator to fully verify:

- NS4168 I2S amplifier audio quality
- real speaker volume/noise
- Bluetooth A2DP pairing/audio
- real Wi-Fi connection to your router
- Home Assistant discovery and OTA on your local network
- 5V/VIN/USB power safety
- level shifting problems between ESP32 3.3V logic and MAX7219 5V logic

Best use of simulation:

1. Simulate the PlatformIO hardware-test firmware first.
2. Confirm the code boots and the display/sensor logic is sane.
3. Build the ESPHome firmware locally with:

   ```powershell
   cd Z:\workspace\esp32_smart_clock
   esphome compile esphome-smart-clock.yaml
   ```

4. Do the final verification on the real ESP32 hardware.

For this project, the emulator is a helpful pre-check, not a replacement for real hardware testing.

### Wokwi Notes

Wokwi supports ESP32 simulation and many common peripherals, including MAX7219 LED matrix modules. ESP32 I2S support is limited/in progress, so do not use Wokwi as proof that the NS4168 speaker wiring or audio playback is correct.

For ESPHome, the better "software-only" check is:

```powershell
esphome config esphome-smart-clock.yaml
esphome compile esphome-smart-clock.yaml
```

ESPHome also has a `host` platform for running some ESPHome configs on a desktop computer, but many real hardware components are unavailable there. This project uses real ESP32 hardware features, so `host` is useful only for limited API/software experiments, not for full clock validation.

## Install The Hardware Test With PlatformIO

This is only for checking the hardware wiring. It replaces the ESPHome firmware until you flash ESPHome again.

1. Install VS Code or Cursor.
2. Install the PlatformIO extension.
3. Open this folder.
4. Connect the ESP32 with a USB data cable.
5. Click PlatformIO: Build.
6. Click PlatformIO: Upload.
7. Open Serial Monitor at 115200 baud.
8. If upload fails, hold BOOT while upload starts, then release when writing begins.

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

To go back to Home Assistant mode, flash `esphome-smart-clock.yaml` again from ESPHome.

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

## Home Assistant Examples

Show a message:

```yaml
action: esphome.esp32_smart_clock_show_message
data:
  message: "GOOD MORNING"
```

Clear the message so the clock/sensors show again:

```yaml
action: esphome.esp32_smart_clock_clear_message
```

Send TTS to the speaker:

```yaml
action: tts.speak
target:
  entity_id: tts.home_assistant_cloud
data:
  media_player_entity_id: media_player.esp32_smart_clock_speaker
  message: "Wake up"
```

Alarm event automation example:

```yaml
alias: ESP32 smart clock alarm voice
triggers:
  - trigger: event
    event_type: esphome.alarm_triggered
actions:
  - action: tts.speak
    target:
      entity_id: tts.home_assistant_cloud
    data:
      media_player_entity_id: media_player.esp32_smart_clock_speaker
      message: "Wake up"
```

## USB + VIN Safety

Do not assume it is safe to connect both USB from the PC and an external 5V supply to VIN at the same time.

Some ESP32 dev boards isolate USB 5V and VIN with a diode or power-path circuit. Many low-cost CH340/USB-C boards do not document this clearly, and back-feeding 5V into the PC USB port can damage the USB port, the ESP32 board, or the power supply.

Safer options:

- During programming: power the ESP32 from USB only, and disconnect external 5V from VIN.
- During full hardware testing: connect PC USB for data, power the LED matrix/amplifier from the external 5V supply, and connect all grounds together. Do not connect that external 5V to ESP32 VIN unless you have verified the board schematic.
- Best permanent setup: power the ESP32 from the same regulated 5V supply through its 5V/VIN pin only, and use OTA updates after the first flash.
- If you must use USB data and external 5V together, use a USB data-only cable or a USB power blocker so the PC 5V line is not connected.

## Logs And Troubleshooting

Start with logs. They will tell you if Wi-Fi, I2C sensors, display, or audio are failing.

### View Logs Over USB

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

### View Logs Over Wi-Fi

After the device is already online:

```powershell
cd Z:\workspace\esp32_smart_clock
esphome logs esphome-smart-clock.yaml --device OTA
```

In Home Assistant, you can also open the ESPHome device and use **Logs**.

### Default Display Behavior

By default, the ESPHome firmware shows the clock from NTP/SNTP:

```text
HH:MM:SS
```

The default clock is drawn directly as pixels across the full 8x32 matrix. Short English/number temporary messages are also drawn as 3x7 pixels across the full width. Hebrew and unsupported symbols use the configured font and may scroll.

If Home Assistant sends a screen message, that message replaces the clock for 10 seconds.

Clear the message from Home Assistant:

```yaml
action: esphome.esp32_smart_clock_clear_message
```

If the display still shows old text after reboot, flash the latest YAML. The current config does not restore old screen messages.

### Hebrew Text

Hebrew is supported for Home Assistant screen messages.

Example:

```yaml
action: esphome.esp32_smart_clock_show_message
data:
  message: "שלום"
```

How it works:

- The display font is `Noto Sans Hebrew`.
- The firmware includes Hebrew glyphs for regular and final Hebrew letters.
- The display lambda detects Hebrew UTF-8 text and reverses codepoints before printing, which makes short right-to-left messages readable on the MAX7219 matrix.

Limitations:

- The MAX7219 matrix is only 8 pixels high, so Hebrew is readable but small.
- Complex Hebrew shaping, nikud, and mixed Hebrew/English sentence layout are not handled.
- For long Hebrew text, keep messages short or let the display scroll.

### Text Does Not Use All LEDs

For the ESPHome firmware, the default clock and supported English/number messages are drawn across the full 8x32 matrix. Hebrew text and unsupported symbols use the font renderer, so they may not occupy every column.

If supported text still appears on only part of the display, check the number of MAX7219 modules:

- Four 8x8 modules: keep `num_chips: 4`.
- One 8x8 module: change `num_chips: 1`.

In `esphome-smart-clock.yaml`:

```yaml
display:
  - platform: max7219digit
    num_chips: 4
```

If the text appears on only part of the display:

- Check DIN, CLK, CS wiring.
- Check that every MAX7219 module has 5V and GND.
- Check module direction. Many 8x32 boards have an input side and output side.
- Try `rotate_chip`, `reverse_enable`, or wiring from the other end if the display is mirrored or shifted.

### Sensors Show No Data

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

If AHT20 works but BMP280 does not, change the BMP280 address in `esphome-smart-clock.yaml`:

```yaml
sensor:
  - platform: bmp280_i2c
    address: 0x77
```

Then compile and upload again.

### Speaker Does Not Work

First check wiring:

| NS4168 | ESP32 |
|---|---:|
| DIN | GPIO25 |
| BCLK | GPIO26 |
| LRCLK / LRC / WS | GPIO27 |
| VCC | 5V |
| GND | GND |

Speaker wires must connect only to the amplifier speaker output, not to the ESP32.

To test from Home Assistant, call TTS or play a WAV/MP3 URL to the `Speaker` media player entity. Confirm the real entity ID in Developer Tools > States.

If there is no sound:

- Check logs while playing audio.
- Confirm the amplifier has 5V power.
- Confirm all grounds are common.
- Try a lower volume first.
- Add a 470uF-1000uF capacitor near the amplifier between 5V and GND.
- Some NS4168 boards have extra enable/shutdown pins. If your board has `EN`, `SD`, or `CTRL`, check the board specs and pull it to the required level.

### Common Existing Notes

- If MAX7219 text is mirrored or broken in the PlatformIO test, change `HARDWARE_TYPE` in `src/main.cpp`:
  - `MD_MAX72XX::FC16_HW`
  - `MD_MAX72XX::PAROLA_HW`
  - `MD_MAX72XX::GENERIC_HW`
- If you have only one 8x8 MAX7219 module, change `MAX_DEVICES` from `4` to `1` in `src/main.cpp`, and `num_chips` from `4` to `1` in `esphome-smart-clock.yaml`.
- If BMP280 is not found, check whether the board address is `0x76` or `0x77`. The PlatformIO firmware tries both. The ESPHome YAML currently uses `0x76`; change it to `0x77` if needed.
- If AHT20 logs communication errors in ESPHome, keep `variant: AHT20` and check that the module is powered from 3V3 with SDA/SCL on GPIO21/GPIO22.
- If audio is noisy, keep I2S wires short and add bulk capacitance near the amplifier.
