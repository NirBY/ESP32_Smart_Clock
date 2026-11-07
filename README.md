# ESP32 Smart Clock

An ESP32 clock with an 8x32 LED matrix, environmental sensors, alarms, countdown timers, audio and Home Assistant controls. Build the hardware, print the enclosure, then configure and install your personalized firmware with the guided Windows or macOS app.

## Presentation

[![Clock, countdown, sensors, messages, alarms, audio, Home Assistant and printable enclosure](docs/images/clock-showcase.gif)](docs/wiki/Gallery.md)

*Eight rotating feature slides in the original gallery style. Product illustrations are based on the real printed clock and enclosure geometry; display examples are illustrative. [Actual build photos](docs/wiki/Gallery.md#actual-printed-clock) · [All eight slides](docs/images/showcase-storyboard.png).*

[Wiring guide](docs/wiki/Wiring.md) · [Parts list](docs/wiki/Shopping-List.md) · [Build gallery](docs/wiki/Gallery.md)

### Printable enclosure

The [current three-part enclosure](ESP32_Smart_Clock_3D_Design/README.md) includes the final [body](ESP32_Smart_Clock_3D_Design/stl/body.stl), [lid](ESP32_Smart_Clock_3D_Design/stl/lid.stl) and [sensor cage](ESP32_Smart_Clock_3D_Design/stl/sensor_cage.stl), editable source, fit samples and an [illustrated assembly guide](ESP32_Smart_Clock_3D_Design/PRINT_GUIDE.pdf). Only the latest design is retained in the working tree.

**The enclosure opens from the back.** The front diffuser is part of the body;
remove the vented rear lid to access the electronics.

| Assembled enclosure | Rear lid removed |
| --- | --- |
| ![Actual STL geometry: assembled clock](ESP32_Smart_Clock_3D_Design/previews/cover.png) | ![Actual STL geometry: exploded rear-opening enclosure](ESP32_Smart_Clock_3D_Design/previews/exploded.png) |

*CAD views rendered directly from the supplied STL meshes. Open the
[body](ESP32_Smart_Clock_3D_Design/stl/body.stl),
[rear lid](ESP32_Smart_Clock_3D_Design/stl/lid.stl), or
[sensor cage](ESP32_Smart_Clock_3D_Design/stl/sensor_cage.stl) on GitHub to rotate
the actual 3D model.*

Print the body in white PLA for the tested 0.6 mm diffuser. The creator has printed and assembled the working clock in one continuous print. The enclosure files are licensed **CC BY-NC-SA 4.0** by NirBY; see the [design license scope](ESP32_Smart_Clock_3D_Design/ATTRIBUTION.md).

[Find the enclosure on Creality Cloud](https://www.crealitycloud.com/model-detail/6adbce3bd4b1f991f82d5813).

## Quick Start

1. Download **[Windows setup EXE](https://github.com/NirBY/ESP32_Smart_Clock/releases/latest/download/SmartClock-Windows-x64.exe)** or **[macOS setup DMG](https://github.com/NirBY/ESP32_Smart_Clock/releases/latest/download/SmartClock-macOS.dmg)**. The Mac DMG supports Apple Silicon and Intel.
2. Open the EXE, or open the DMG and then **Smart Clock Setup**. The installer downloads and verifies its own software. No separate Python, Java, Git, Homebrew or Xcode setup is required; Internet is needed for first setup and firmware tools.
3. Connect the clock with a USB data cable. Enter your 2.4 GHz Wi-Fi details. For a new clock, keep the generated API encryption key and copy it for Home Assistant setup; for an existing clock, use its current key.
4. Click **Find USB**, **Save & validate**, then **Build & install**. Moving the cable to another port refreshes a disconnected COM/device path automatically. Windows also offers signed driver setup through Windows Update.
5. Follow the [Home Assistant integration steps](#home-assistant-integration) below. Later updates can use USB or the clock's network address.

![Smart Clock setup window](docs/images/desktop-setup.png)

The app shows estimated progress for the complete build/install process and reaches 100% only after success. Setup retries/resumes interrupted downloads, verifies checksums, and preserves your settings and working installation on failure. Installers are unsigned; Windows or macOS may ask you to approve opening them.

See the [full installation guide](docs/wiki/Desktop-App.md), [driver help](docs/wiki/Desktop-App.md#first-installation), or [manual CLI setup](docs/wiki/Local-Setup.md).

## Hardware Summary and Complete Wiring

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

### Complete wiring

**Power distribution:** USB-C directly supplies every 5 V load and common ground. Only the sensor VCC uses ESP32 3V3.

![Direct USB-C power distribution](docs/images/power-distribution.png)

**Signal connections:**

[![Complete ESP32 clock wiring diagram](docs/images/wiring.png)](docs/images/wiring.png)

[High-resolution PNG](docs/images/wiring.png) · [Scalable SVG](docs/images/wiring.svg) · [Two-sheet PDF](docs/hardware/clock-wiring.pdf) · [Editable KiCad source](docs/hardware/clock-wiring.kicad_sch) · [Pin mapping and assembly notes](docs/wiki/Wiring.md)

Connections use module labels and firmware GPIO numbers, not physical header positions. The diagram includes the display, external sensor, amplifier, speaker, USB-C power and shared ground.

## Home Assistant integration

### What to install

| Component | Needed? | Purpose |
|---|---|---|
| Home Assistant | Yes | Runs your clock controls and automations |
| ESPHome integration | Yes; built into Home Assistant | Connects the flashed clock over the local network |
| ESPHome Device Builder app/add-on | Optional | Edit and compile firmware inside Home Assistant; the desktop installer already handles local builds |
| HACS | Optional | The clock integration and included brightness card do not require it |
| Brightness editor card | Optional; included in this repository | Adds a time-range editor to the dashboard; copy the supplied JavaScript file manually |
| Music Assistant / MCP scripts | Optional | Music search or AI control; each needs separate setup |

### Connect the clock

1. Install the ESPHome clock firmware with the desktop app in Quick Start, then let the clock join your home Wi-Fi. Home Assistant must be able to reach the clock on the local network.
2. In Home Assistant, open **Settings > Devices & services**. Configure the discovered **ESPHome** clock. If it is absent, choose **Add integration > ESPHome** and enter the clock's IP address (default API port **6053**).
3. When asked for the encryption key, paste the same **Home Assistant encryption key** used in the desktop setup form (`api_encryption_key` in a manual build). It is different from the Wi-Fi and recovery-hotspot passwords.
4. Assign an area and open the device. The clock exposes display, timer, alarm, audio, sensor and system controls, organized as logical devices for the same physical clock.
5. Test a brightness change, check temperature/humidity, then send a short screen message. For clock actions that call Home Assistant, enable **Allow the device to perform Home Assistant actions** in the integration's device options if prompted.

The [official ESPHome integration guide](https://www.home-assistant.io/integrations/esphome/) covers discovery, manual setup and encryption. [ESPHome Device Builder setup](https://esphome.io/install/getting-started/) is available if you prefer to build from Home Assistant.

### Add the dashboard

Use the [dashboard YAML](docs/home-assistant-dashboard.yaml) and check entity IDs against your clock. To enable the included brightness range editor:

1. Copy [smart-clock-brightness-card.js](docs/home-assistant/smart-clock-brightness-card.js) to Home Assistant's `/config/www/` directory.
2. Add `/local/smart-clock-brightness-card.js?v=1` under **Settings > Dashboards > Resources** as a **JavaScript module** (Advanced mode may need enabling in your profile), then reload the browser.
3. Add the supplied dashboard/card, set your time ranges, and enable **Day / night automatic brightness**. HACS is not required for this manual installation.

See the [dashboard guide](docs/wiki/Home-Assistant-Dashboard.md) for entity names and a standalone card example.

### Alarm schedules

Configure one alarm in Home Assistant: every day, selected weekdays, a day of
each month, or a specific date. Optionally limit it to an inclusive start/end
date range. The schedule summary shows your choices in readable text.

[![Weekly, monthly and specific-date alarm examples with an optional date range](docs/images/alarm-schedules.png)](docs/wiki/Alarm.md)

*Illustrated examples of the scheduling controls, not a live Home Assistant
screenshot. Choose one schedule at a time. The
[example dashboard](docs/home-assistant-dashboard.yaml) shows the relevant
weekday switches, day-of-month control, or date picker for your selection.*

See the [alarm setup and scheduling rules](docs/wiki/Alarm.md). The clock displays
`ALARM`, plays the selected local Alarm Sound, and sends an event to Home
Assistant for additional automations.

### Firmware Updates

Use **Check for updates** in the desktop app, then **Build & install** to apply the new firmware with your own settings.

For a personalized clock, update from your local ESPHome YAML. This preserves
your private `secrets.yaml` and any local config edits:

```sh
esphome run esphome-smart-clock.yaml --device CLOCK_DEVICE
```

Replace `CLOCK_DEVICE` with the clock IP address.

The GitHub release update entity checks public release binaries. Those binaries
are built in GitHub Actions with `secrets.example.yaml`, so they are useful as
reference/recovery artifacts but are not the normal update path for a device
that needs your local Wi-Fi/API secrets.

[![Import ESP32 Smart Clock update automation](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FNirBY%2FESP32_Smart_Clock%2Fblob%2Fmain%2Fdocs%2Fblueprints%2Fautomation%2Fesp32_smart_clock_auto_update.yaml)

The button imports a safe check/notify blueprint. It does not install public
GitHub firmware unless you explicitly enable that option.

Each update notification includes **Open firmware update panel**, which opens
the selected clock's update details in your own Home Assistant instance.
Opening the link does not install firmware. Re-import the blueprint to add
the link to an existing automation. The panel uses the entity's reported
status; older development builds may still show **Up-to-date** despite the
notification. Personalized clocks still need firmware built with their own
configuration and credentials.

### Calendar Agenda Announcements

Home Assistant can read today's events from a calendar, print a compact agenda
on the LED matrix, and optionally speak the same agenda through the clock
speaker. The automation can run every day at a selected time, from an
`input_button` helper, or both.

[![Import ESP32 Smart Clock calendar agenda automation](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FNirBY%2FESP32_Smart_Clock%2Fblob%2Fmain%2Fdocs%2Fblueprints%2Fautomation%2Fesp32_smart_clock_calendar_agenda.yaml)

Create an `input_button` helper if you want a dashboard button, then import the
blueprint and select your calendar, clock speaker, and ESPHome display action.

### AI control with Home Assistant MCP

**MCP runs in Home Assistant, not on the ESP32.** An authenticated AI client calls
Home Assistant tools; HA sends commands to the clock through the ESPHome API.
The optional [MCP package](docs/home-assistant-mcp/README.md) is included in this
repository and adds six tools:

| Tool | What you can do |
|---|---|
| Status | Read temperature, humidity, pressure, timer, alarm and settings |
| Timer | Start a countdown, pause, resume or cancel it |
| Alarm | Daily, weekly, monthly or specific-date schedules, with optional date limits; [alarm guide](docs/wiki/Alarm.md) |
| Message | Display custom text (up to 100 characters) or clear it |
| Setting | Change brightness, display intervals, switches and time format |
| Music | Search/play through Music Assistant; control playback and volume |

#### Set up MCP

1. Add the clock to Home Assistant through the **ESPHome integration** first.
2. Review the entity IDs in [package.yaml](docs/home-assistant-mcp/package.yaml)
   against your installation. Copy it to `/config/packages/esp32_clock_mcp.yaml`.
   Enable packages under your existing `homeassistant:` configuration, check
   configuration and restart HA. The [installation guide](docs/home-assistant-mcp/README.md#install)
   includes the YAML and an alternative using six individual scripts.
3. In each of the six scripts, open **Settings → Voice assistants** and expose
   it to **Assist**.
4. Add/configure the **Model Context Protocol Server** integration. Select the
   **Assist** LLM API and keep authentication enabled. Review other entities
   already exposed to Assist, since they may also be available to the client.
5. In **Settings → System → AI**, enable the appropriate MCP server and copy
   its URL into your MCP-compatible AI client. Sign in with Home Assistant using
   supported authentication. A remotely hosted client needs a reachable HA URL.
   See the [official HA MCP setup](https://www.home-assistant.io/integrations/mcp_server/).
6. Reconnect the client, check that the clock tools appear, then ask for status,
   display a test message and run a short timer. Check HA script traces and the
   physical clock to confirm execution.

Try: “Show HELLO on the clock”, “Start a seven-minute timer”, “Show the countdown
for 10 seconds and the time for 2 seconds”, “Set the daily alarm to 07:30”, or
“What are the room temperature and humidity?”

Music search requires **Music Assistant** and configured music providers. MCP
does not automatically mirror Google Home timers or add a microphone to the
clock. This package is supplied for setup and testing; **end-to-end control
through a live MCP client has not yet been verified**.

## Troubleshooting

- **USB missing or stale:** use a data cable, reconnect, then click **Find USB**. A disconnected COM/device selection refreshes automatically. On Windows use **Set up USB drivers** if needed; Mac bridge-driver guidance is in the [desktop guide](docs/wiki/Desktop-App.md).
- **Upload cannot connect:** close other serial monitors. Hold **BOOT** as upload starts and release it when writing begins.
- **Brief display flicker:** compare the specified 5 V / 3 A supply and a short cable against the computer USB port or hub; temporarily lower brightness. A supply/cable problem is a possibility, not a confirmed diagnosis for every flicker. Reset/brownout logs and a charger comparison help distinguish causes.
- **Hourly text:** the default is weekday/date, for example `SAT 07/11`, for 3 seconds. Adjust **Date Message Seconds**. The date uses compact pixel text; unsupported custom characters may use a font fallback.
- **Home Assistant cannot connect:** check the clock IP, local network reachability and matching API encryption key. Reinstalling with a different key requires updating the integration's key too.
- **Download or build failed:** keep Internet connected and retry. Existing settings are preserved. See [logs and troubleshooting](docs/wiki/Logs-And-Troubleshooting.md) and [audio troubleshooting](docs/wiki/Audio-And-Music.md).

### Recover Wi-Fi from your phone

The clock already includes **ESP32 Smart Clock Fallback**, a password-protected
Wi-Fi hotspot and setup page. No Bluetooth, app, Home Assistant connection, or
USB cable is needed to change the router name/password.

**Default password for public release firmware:** `CHANGE_ME_FALLBACK_AP_PASSWORD`
(type it exactly, including underscores). This is an example placeholder, not a
password generated for each clock. For your own build, replace
`fallback_ap_password` in your private `secrets.yaml` before flashing. If you
already flashed a personalized build, use the password you configured there.

1. Power the clock normally. If its configured Wi-Fi network cannot be reached
   (for example, after changing the router password), wait **90 seconds**.
   The fallback hotspot starts automatically; there is no button to press.
2. On your phone, open **Settings > Wi-Fi** and join
   **ESP32 Smart Clock Fallback**.
3. Enter the hotspot password: the value of `fallback_ap_password` in your
   private `secrets.yaml`. This is separate from your home Wi-Fi password.
   Public release builds use the example value `CHANGE_ME_FALLBACK_AP_PASSWORD`.
4. Accept **Stay connected / Use without Internet** if prompted. If the setup
   page does not open automatically, open **http://192.168.4.1/** in your browser
   (HTTP, not HTTPS). Temporarily turn off mobile data or a VPN if your phone
   keeps routing away from the clock.
5. Select your home **2.4 GHz** Wi-Fi network, or enter its name manually, enter
   its password, and press **Save**. The ESP32 board used here cannot join 5 GHz.
6. Allow the clock to connect, then reconnect your phone to your normal network.
   The fallback hotspot shuts down after connection. If the password is wrong,
   reconnect to the fallback hotspot and try again.

![ESPHome fallback Wi-Fi setup page](docs/images/wifi-fallback-portal.png)

*Screenshot of the original ESPHome 2026.9.0 portal rendered locally with
example network data. Your available networks will differ.*

The portal saves the new credentials on the clock across restarts. Also update
`wifi_ssid` and `wifi_password` in your local `secrets.yaml` before the next USB
build/upload, so a future firmware installation does not restore stale values.
Changing Wi-Fi here does not change the Home Assistant API encryption key.

To test recovery without changing your router, temporarily flash a local build
with a nonexistent Wi-Fi SSID, wait 90 seconds, then follow the steps above.
Keep a copy of your correct local settings. Do not reset or erase the device.

Reference: [ESPHome captive portal documentation](https://esphome.io/components/captive_portal/).

## Firmware Options

| Firmware | Use for | Home Assistant | Wi-Fi | Bluetooth music |
|---|---|---:|---:|---:|
| ESPHome smart clock | Clock, sensors, screen messages, alarm, Home Assistant speaker | Yes | Yes | No |
| Bluetooth speaker | Direct Bluetooth music from phone/PC | No | No | Yes |
| PlatformIO hardware test | Checking wiring and modules | No | No | No |

The ESP32 runs one firmware at a time. Flashing the Bluetooth speaker firmware replaces ESPHome. Flashing ESPHome again replaces the Bluetooth speaker firmware.

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

```sh
esphome logs esphome-smart-clock.yaml --device CLOCK_DEVICE
```

Upload and keep logs open:

```sh
esphome run esphome-smart-clock.yaml --device CLOCK_DEVICE
```

Upload an already compiled firmware over Wi-Fi by IP address:

```sh
esphome upload esphome-smart-clock.yaml --device CLOCK_DEVICE
```

Upload over Wi-Fi by IP address and keep logs open:

```sh
esphome run esphome-smart-clock.yaml --device CLOCK_DEVICE
```

For the separate Arduino builds, activate the [PlatformIO environment](docs/wiki/Local-Setup.md#separate-platformio-environment), then run:

```sh
python -m pip install "platformio==6.2.0"
```

Build the PlatformIO hardware test:

```sh
pio run -e esp32dev
```

Build the Bluetooth speaker firmware:

```sh
pio run -e bluetooth_speaker
```

## Notes

- Do not commit `secrets.yaml`; it is ignored by git.
- `GPIO5` is an ESP32 strapping pin. It is currently used for MAX7219 CS/LOAD, so avoid external pull-up/down effects on that pin.
- Hebrew MAX7219 font glyphs can be designed with [md_max72xx-font-designer](https://github.com/vasco65/md_max72xx-font-designer/tree/master).
- For audio noise or playback issues, see [Logs And Troubleshooting](docs/wiki/Logs-And-Troubleshooting.md) and [Audio And Music](docs/wiki/Audio-And-Music.md).
