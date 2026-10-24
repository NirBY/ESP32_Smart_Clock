# Daily Package Update Verification

- Verified at: 2026-10-24 08:17:02 UTC
- Commit: dd0e2c75f7986af9caa4a09fbf98999af3a7d896
- ESPHome: Version: 2026.10.0
- PlatformIO (ESPHome): PlatformIO Core, version 6.2.0
- PlatformIO (Arduino): PlatformIO Core, version 6.2.0

Builds completed with current pip ESPHome and the pinned Arduino dependencies below:

- ESPHome smart clock firmware
- PlatformIO hardware test firmware
- PlatformIO Bluetooth speaker firmware

Resolving esp32dev dependencies...
Platform espressif32 @ 55.3.312 (required: https://github.com/pioarduino/platform-espressif32/releases/download/55.03.312-1/platform-espressif32.zip)
├── contrib-piohome @ 3.4.4 (required: /home/runner/.platformio/packages/contrib-piohome)
├── framework-arduinoespressif32 @ 3.3.12 (required: https://github.com/espressif/arduino-esp32/releases/download/3.3.12/esp32-core-3.3.12.tar.xz)
├── framework-arduinoespressif32-libs @ 5.5.5+sha.b774170ff46 (required: https://github.com/espressif/arduino-esp32/releases/download/3.3.12/esp32-core-3.3.12-libs.tar.xz)
├── tool-esptoolpy @ 5.4.0 (required: /home/runner/.platformio/packages/tool-esptoolpy)
├── tool-xtensa-esp-elf-gdb @ 17.1.0+20260402 (required: /home/runner/.platformio/packages/tool-xtensa-esp-elf-gdb)
└── toolchain-xtensa-esp-elf @ 14.2.0+20260121 (required: /home/runner/.platformio/packages/toolchain-xtensa-esp-elf)

Libraries
├── Adafruit AHTX0 @ 2.0.6 (required: adafruit/Adafruit AHTX0 @ 2.0.6)
│   ├── Adafruit BusIO @ 1.17.4 (required: Adafruit BusIO)
│   ├── Adafruit SH110X @ 2.1.15 (required: Adafruit SH110X)
│   │   └── Adafruit GFX Library @ 1.13.0 (required: Adafruit GFX Library)
│   └── Adafruit Unified Sensor @ 1.1.15 (required: Adafruit Unified Sensor)
├── Adafruit BMP280 Library @ 3.0.0 (required: adafruit/Adafruit BMP280 Library @ 3.0.0)
└── MD_MAX72XX @ 3.5.1 (required: majicdesigns/MD_MAX72XX @ 3.5.1)

Resolving bluetooth_speaker dependencies...
Platform espressif32 @ 55.3.312 (required: https://github.com/pioarduino/platform-espressif32/releases/download/55.03.312-1/platform-espressif32.zip)
├── contrib-piohome @ 3.4.4 (required: /home/runner/.platformio/packages/contrib-piohome)
├── framework-arduinoespressif32 @ 3.3.12 (required: https://github.com/espressif/arduino-esp32/releases/download/3.3.12/esp32-core-3.3.12.tar.xz)
├── framework-arduinoespressif32-libs @ 5.5.5+sha.b774170ff46 (required: https://github.com/espressif/arduino-esp32/releases/download/3.3.12/esp32-core-3.3.12-libs.tar.xz)
├── tool-esptoolpy @ 5.4.0 (required: /home/runner/.platformio/packages/tool-esptoolpy)
├── tool-xtensa-esp-elf-gdb @ 17.1.0+20260402 (required: /home/runner/.platformio/packages/tool-xtensa-esp-elf-gdb)
└── toolchain-xtensa-esp-elf @ 14.2.0+20260121 (required: /home/runner/.platformio/packages/toolchain-xtensa-esp-elf)

Libraries
└── ESP32-A2DP @ 1.8.11+sha.b6da474 (required: git+https://github.com/pschatzmann/ESP32-A2DP#v1.8.11)


Review the automation branch before creating a new release.
