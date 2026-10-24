# Local setup — Windows, macOS and Linux

Install Git and Python 3.12 or newer. Choose any folder you own, open a terminal
there and run these commands once on any operating system:

```sh
git clone https://github.com/NirBY/ESP32_Smart_Clock.git
cd ESP32_Smart_Clock
```

Already downloaded or cloned the project? Open a terminal in that folder instead.
All subsequent commands run from the repository root (the folder containing
`esphome-smart-clock.yaml`); no specific drive or absolute path is required.

## ESPHome environment

Create and activate a dedicated environment. Repeat only the activation command
when opening a new terminal.

**Windows PowerShell:**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux (bash or zsh):**

```sh
python3 -m venv .venv
source .venv/bin/activate
```

On Linux, install your distribution's Python venv package if environment creation
reports that venv or ensurepip is missing.

**Then, on every OS:**

```sh
python -m pip install --upgrade pip
python -m pip install "esphome==2026.10.0"
python -m esphome version
```

Create `secrets.yaml` only if it does not exist (existing credentials are kept):

```sh
python -c "from pathlib import Path; p=Path('secrets.yaml'); p.exists() or p.write_bytes(Path('secrets.example.yaml').read_bytes())"
```

Edit that file in your preferred editor. Continue with
[firmware installation](Install-And-Home-Assistant.md#2-configure-wi-fi).

## USB and network device selection

Leave `--device` out to let ESPHome offer available devices:

```sh
esphome upload esphome-smart-clock.yaml
esphome logs esphome-smart-clock.yaml
```

For an explicit device, replace `CLOCK_DEVICE` in the guides with the actual
serial port or clock hostname/IP. It is a placeholder, not a literal address.

| OS / connection | Typical device identifier (example only) |
|---|---|
| Windows USB | `COM5` — check Device Manager |
| macOS USB | `/dev/cu.usbserial-…` — use the actual detected name |
| Linux USB | `/dev/ttyUSB0` or `/dev/ttyACM0` |
| Network, any OS | `esp32-smart-clock.local` or the address shown by HA |

Linux serial permissions depend on the distribution; grant your user access to
the serial device's group if access is denied, then sign out and back in.

## Separate PlatformIO environment

Use this only for the Arduino hardware-test or Bluetooth firmware, which replaces
ESPHome on the clock. In a **new terminal**, open the repository root and create
a separate environment:

**Windows PowerShell:**

```powershell
py -3 -m venv .pio/core
.\.pio\core\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bat
py -3 -m venv .pio/core
.pio\core\Scripts\activate.bat
```

**macOS / Linux:**

```sh
python3 -m venv .pio/core
source .pio/core/bin/activate
```

**Then, on every OS:**

```sh
python -m pip install "platformio==6.2.0"
pio run -e esp32dev
```

For Bluetooth use `pio run -e bluetooth_speaker`. Add `-t upload` to upload.
Run `deactivate` before switching environments.
