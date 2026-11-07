# Install and update with the desktop app

The desktop app guides you through preparing your clock without terminal
commands or a separate Python, Java, Git or ESPHome installation. The application
automatically downloads its Python runtime, ESPHome, USB/OTA uploader and Git.
Compiler tools are downloaded automatically during the first firmware build.

Release packages pass Windows installation/recovery checks and native Apple
Silicon/Intel macOS installation and compilation checks before publication.
Installers are unsigned; operating-system approval may be needed.

## Download and open

Download the matching asset from
[GitHub Releases](https://github.com/NirBY/ESP32_Smart_Clock/releases):

| Computer | Download | Open |
| --- | --- | --- |
| Windows 10/11, Intel or AMD 64-bit | `SmartClock-Windows-x64.exe` | Double-click the single EXE; no manual extraction or companion folder |
| Mac, Apple Silicon or Intel, macOS 12+ | `SmartClock-macOS.dmg` | Open the DMG, then double-click `Smart Clock Setup` |

Windows is distributed as **one small online setup EXE** (about 23 KB). You can
copy that file alone to another folder or computer. On first launch it downloads
the matching runtime (about 81 MB) from its official GitHub release, checks its
exact size and SHA-256, then prepares it under
`%LOCALAPPDATA%\SmartClock\application`; later launches reuse it. No Python,
Java, Git, archive utility or other package needs to be installed manually.
The preparation dialog may remain visible for a while during the first launch.
This is one distributed file, not an application that runs without writing any
working files to disk. Your private settings remain in their separate data folder.

The Mac installer is one universal **DMG file**, about 210 KB. Double-click it,
then double-click **Smart Clock Setup** in the window that opens. No ZIP extraction
or separate Apple Silicon/Intel download is needed. Keep the image mounted until
setup finishes; once the clock GUI is open, you can eject it.
First-time setup opens Terminal automatically, downloads
verified setup tools, and prepares Python/Git/ESPHome in a private environment.
**No commands need to be typed**, and Python, Java, Homebrew and Xcode do not need
to be installed beforehand. Keep that window open until the clock GUI appears.
Later launches open the GUI directly using the cached environment.
If setup is interrupted, reopen the same app to retry. Other installed versions
and your private clock settings are preserved. Setup logs are in
`~/Library/Logs/SmartClock/setup.log`. Runtime packages live under
`~/.local/share/smartclock`; clock settings remain in the separate folder below.

The setup icon detects the Mac hardware automatically and uses the matching
Apple Silicon or Intel runtime, including when Terminal was configured for Rosetta.

The preview is unsigned; macOS
notarization and Windows signing are not configured. A `.sha256` file accompanies
each release download for integrity checking. These packages are platform
specific; Windows ARM and older operating systems are not validated targets.
If macOS blocks this unsigned preview, use **System Settings → Privacy & Security
→ Open Anyway** for this app, then reopen it. Native Mac execution has not been
verified in the local Windows development session; the release workflow includes
separate Apple Silicon and Intel installation/compilation tests.

For the local Windows preview, open
`outputs/web-preview/SmartClock-Local-Setup.exe` while the local preview server is
running. This test-only build downloads from this computer's loopback server.
The production EXE in `outputs/desktop-release` uses the official HTTPS release
URL, which becomes available only after an approved release publishes its runtime.

## Interrupted downloads and setup errors

- Setup shows download progress and offers **Cancel**. It keeps completed bytes
  and resumes on the next run when the server supports it. If the server cannot
  resume, setup restarts the transfer safely.
- Temporary failures retry automatically, up to three attempts. Missing releases,
  blocked proxies, and authentication errors show an actionable message.
- Incomplete files, HTML login pages, invalid ranges, wrong sizes and wrong
  SHA-256 hashes never become an installed runtime. Invalid data is discarded;
  a replacement is downloaded before installation can continue.
- Setup prepares a separate staging directory and activates it only after the
  runtime has unpacked and its core libraries can load. Failed or cancelled setup
  preserves existing runtime versions and private clock settings.
- If Internet is unavailable on first use, reconnect and choose **Retry**, or
  run setup again. An already installed version can launch without downloading
  again; firmware updates/build tools may still need Internet.
- If disk access is blocked or space runs out, correct the reported problem and
  retry. Technical startup details are in `%LOCALAPPDATA%\SmartClock\startup-error.log`.

During firmware compilation, ESPHome manages and validates compiler packages.
The app distinguishes package/network failures from USB upload errors and keeps
your saved settings available for a retry. It does not start uploading firmware
when compilation fails.

## First installation

1. Connect the ESP32 using a **USB data cable**. A charging-only cable cannot
   install firmware. Keep the computer connected to the Internet.
2. The app scans for supported USB bridges automatically and shows their port
   and description. If several are connected, select the clock's port. A detected
   USB bridge is a candidate; it does not by itself identify the clock firmware.
   After unplugging or moving the cable, **Find USB** refreshes the list and
   replaces a disconnected COM/device-path selection automatically when one
   recognized clock bridge is present. You do not need to clear the field first.
   Connected selections and network addresses are preserved; ambiguous device
   lists require you to choose. An active build/upload is never silently retargeted.
3. On Windows, if no port appears, click **Set up USB drivers**. The app asks
   Windows Update for a driver matching the connected bridge and requests
   administrator approval. Wait for completion and reconnect the cable.
   Windows Update must be enabled and offer a compatible driver; driver binaries
   are not bundled. If no compatible driver is offered, vendor-specific driver
   setup is still required. macOS driver installation is not automated in this
   preview; a board requiring a vendor driver needs that driver first.
4. Fill in **Wi-Fi name (2.4 GHz)** and **Wi-Fi password**. The clock cannot use
   a 5 GHz-only network. Leave the password empty only for an open network.
5. Keep or choose a **Recovery hotspot password**. Save it somewhere safe; it
   lets you reconnect the clock after a router change.
6. For a new clock, use the generated **Home Assistant encryption key**.
   For an existing clock, enter its existing key to preserve the HA connection.
   **Show passwords and key** reveals these values when needed.
7. Click **1. Save & validate**. Correct any reported settings errors.
8. Optionally click **2. Check for updates** to select a newer published firmware
   version. This includes beta releases and downloads source, preserving the
   personal settings in your form. It does not flash the clock.
9. Click **3. Build & install**, check the target port, and confirm installation.
   The first build can take 10–30 minutes or longer and require several GB of
   disk space and downloads. One overall percentage bar covers the complete
   build-and-install operation, without resetting between stages. It is a weighted
   work estimate, not an exact time forecast: preparation/downloads occupy the
   first 15%, compilation runs through 85%, build finalization reaches 90%, transfer
   reaches 98%, and verification/restart stays below 100% until upload succeeds.
   Retries and nested build counters cannot make the bar move backwards. The
   current stage is shown next to the overall percentage. Failed operations keep
   their last percentage and never show successful completion.
   Full technical details remain available below the bar.
10. Wait for **Firmware uploaded successfully**. The clock restarts and connects
    to Wi-Fi. Add the discovered ESPHome device in Home Assistant and supply the
    encryption key from the form.

If USB connection fails, check the selected port and cable. Some boards require
holding **BOOT** as upload connects, then releasing it when writing starts.
Do not disconnect power during flashing. An upload success message confirms
transfer; check the physical display and Home Assistant connection afterward.

## Change settings or update firmware later

Open the app on the same computer. It reloads your saved form settings. Change
the required fields, validate, then build and install again.

For wireless updates, replace the USB port with the clock's IP address or hostname
(for example, `esp32-smart-clock.local`). The computer must be able to reach the
clock on the local network. If you change the router/Wi-Fi credentials and the
clock is no longer reachable, connect USB or use the clock's recovery hotspot.

**Check for updates** downloads and selects newer firmware; **Build & install**
applies it with your own credentials. Public example-credential firmware is never
used for this personalized installation. The version shown is the selected
source version, not a version read back from the device. Updating the desktop
application itself currently means downloading the newer EXE (Windows) or DMG
(macOS). Replacing the EXE preserves settings. Each EXE version manages its own
runtime cache automatically.

Brightness, timer, alarm, sound and other runtime controls remain in Home
Assistant. The desktop form configures connectivity and firmware installation.

## Where settings are stored

| System | Folder |
| --- | --- |
| Windows | `%LOCALAPPDATA%\SmartClock\device` |
| macOS | `~/Library/Application Support/SmartClock/device` |

`secrets.yaml` contains your Wi-Fi passwords and API key. Keep this folder private
and back it up before moving to another computer. Replacing the app folder
preserves this separate settings folder. The app does not upload these settings
to GitHub or include them in release packages. ESPHome downloads dependencies and
source code online; private credentials are used for the local build and clock.

## Automatic release packaging

The existing **Build and Release Firmware** workflow now builds desktop packages
on Windows, Apple Silicon macOS and Intel macOS. Tag pushes (`v*`/`V*`), publishing
a GitHub release, and the existing manual release action run this pipeline.

Each desktop job installs the pinned `ESPHOME_VERSION` into an isolated runtime,
matches the bundled firmware version to the release tag, checks dependencies,
tests the form, and compiles firmware using the packaged runtime with development
tools removed from `PATH`. All three jobs must pass before the firmware release
job publishes. Windows additionally runs the actual standalone EXE from an empty
folder against a local HTTP server, checks download recovery with injected faults,
and checks an offline cached second launch. The release contains the small Windows
EXE, its immutable runtime ZIP, one universal macOS DMG and their SHA-256 files in
addition to the existing firmware assets. A manual run without a release tag
produces workflow artifacts without publishing a release.

The workflow builds the DMG once, then verifies and mounts the exact same image
on Apple Silicon and Intel before running the native installation/compilation
checks. The workflow remains unexecuted until these changes are uploaded.
Local checks verified the real UDIF/HFS image, checksums, file contents and execute
permissions; mounting/execution on a Mac still needs confirmation.
Code signing/notarization credentials are not
configured. For developer build instructions, see [desktop/README.md](../../desktop/README.md).
