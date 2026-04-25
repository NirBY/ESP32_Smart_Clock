# Development And Releases

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

## Install The PlatformIO Hardware Test

This is only for checking the hardware wiring. It replaces the ESPHome firmware until you flash ESPHome again.

1. Install VS Code or Cursor.
2. Install the PlatformIO extension.
3. Open this folder.
4. Connect the ESP32 with a USB data cable.
5. Click PlatformIO: Build.
6. Click PlatformIO: Upload.
7. Open Serial Monitor at 115200 baud.
8. If upload fails, hold BOOT while upload starts, then release when writing begins.

Equivalent terminal commands:

```powershell
cd Z:\workspace\esp32_smart_clock
pio run -e esp32dev
pio run -e esp32dev -t upload
pio device monitor -b 115200
```

## Current Firmware

`src/main.cpp` is a PlatformIO hardware test:

- scans I2C
- reads AHT20 humidity/temperature
- reads BMP280 temperature/pressure
- scrolls readings on the MAX7219 matrix
- plays a short I2S tone through the NS4168 amplifier/speaker

This test firmware does not connect to Wi-Fi or Home Assistant.

## PlatformIO Environments

`platformio.ini` includes:

- `esp32dev` - hardware test firmware from `src/main.cpp`
- `bluetooth_speaker` - Bluetooth A2DP speaker firmware from `src/bt_a2dp_sink.cpp`

Both environments use ESP32 HW-394 / WR-32 style board settings:

```ini
board_build.mcu = esp32
board_build.f_cpu = 240000000L
board_build.flash_size = 4MB
board_build.flash_mode = dio
board_upload.flash_size = 4MB
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

## Verify Latest Packages Workflow

The `Verify latest packages` workflow checks current ESPHome and PlatformIO packages, builds the firmware, and opens a manual-review PR with the verification report.

The workflow is intentionally not a release workflow. It verifies package updates and asks for manual review before anything is merged.

If GitHub Actions cannot create the PR, enable this repository setting:

`Settings` > `Actions` > `General` > `Workflow permissions`

Enable:

- `Read and write permissions`
- `Allow GitHub Actions to create and approve pull requests`
