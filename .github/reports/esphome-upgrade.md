# ESPHome Upgrade Verification

- Verified at: 2026-11-07T11:56:53+00:00
- Verified ESPHome: 2026.10.1 (upgrade from PR #10)
- Combined software source tested: `80e9208a0cf5f27c521c3ec8e414d9a6d745b54f`
- Release: [v0.1.0](https://github.com/NirBY/ESP32_Smart_Clock/releases/tag/v0.1.0), stable and latest
- [Complete release workflow](https://github.com/NirBY/ESP32_Smart_Clock/actions/runs/42369040549): all six jobs passed

## Results

- C++ timer/alarm/brightness/version tests, Home Assistant update/version tests,
  JavaScript brightness editor checks and desktop regressions passed.
- Windows: isolated runtime, current source and ESPHome pin, native downloader
  fault cases, cold EXE setup, GUI/configuration, full firmware compilation,
  cached offline launch and safe offline failure passed.
- macOS: the same universal DMG mounted and installed on Apple Silicon and
  Intel; GUI/configuration, current source and pin, full compilation and cached
  relaunch passed on both.
- ESPHome factory/OTA, PlatformIO hardware-test and Bluetooth firmware built.
- Published downloads were fetched independently. All 12 provenance asset
  hashes, installer SHA files, Windows runtime URL/hash, 16 app/firmware source
  files per platform, Mac disk-image integrity, stable tag and OTA channel were
  verified. Text comparisons account for Windows Git line endings.
- Node 20 deprecation annotations: zero across all release jobs.
- PR #10's version pin was incorporated manually to preserve the cleaned main
  history; all remaining older upgrade PRs were reviewed and closed as superseded.

Later README/gallery-only changes leave the validated software inputs unchanged.
Physical display flicker remains subject to the creator's charger/cable test;
a ten-minute COM4 observation captured no reset/brownout/watchdog reports.
