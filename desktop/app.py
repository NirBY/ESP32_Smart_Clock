"""Local, personalized ESPHome installer. No credentials leave this computer."""
import base64
import json
import os
from pathlib import Path
import queue
import re
import secrets
import shutil
import subprocess
import sys
import threading
import urllib.request
import zipfile
import io
import importlib.metadata
import http.client
import time
import urllib.error
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = Path(__file__).resolve().parent
DATA = Path(os.getenv('LOCALAPPDATA', str(Path.home() / 'Library/Application Support'))) / 'SmartClock'
REPO = 'NirBY/ESP32_Smart_Clock'
USB_BRIDGE_VIDS = (0x10C4, 0x1A86, 0x0403, 0x303A)


def select_usb_target(current, detected):
    """Replace disconnected serial targets; preserve deliberate live/network targets."""
    current = current.strip()
    canonical = current[4:] if current.startswith('\\\\.\\') else current
    present = {port.device.casefold(): port.device for port in detected}
    if canonical.casefold() in present:
        return present[canonical.casefold()]
    serial_target = bool(re.fullmatch(r'COM\d+', canonical, re.I)) or canonical.startswith('/dev/')
    if current and not serial_target:
        return current
    supported = [port.device for port in detected if port.vid in USB_BRIDGE_VIDS]
    return supported[0] if len(supported) == 1 else ''


def version(source):
    return re.search(r'firmware_version:\s*"([^"]+)"', source).group(1)


def release_order(value):
    match = re.fullmatch(r'[vV]?(\d+)\.(\d+)\.(\d+)(?:-beta\.(\d+))?', value)
    if not match:
        raise ValueError('Unsupported release version')
    parts = match.groups()
    return tuple(int(p) for p in parts[:3]) + (int(parts[3]) if parts[3] else float('inf'),)


def cache_is_current(candidate, bundled):
    try:
        return release_order(version(candidate.read_text(encoding='utf-8'))) >= release_order(version(bundled.read_text(encoding='utf-8')))
    except (OSError, ValueError, AttributeError):
        return False


def release_config(config, tag):
    """Release CI takes the tag as authoritative even if source YAML is older."""
    value = tag.lstrip('vV')
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-beta\.\d+)?', value):
        raise ValueError('Unsupported release version')
    updated, count = re.subn(r'(?m)^(  firmware_version:)\s*"[^"]+"',
                             lambda m: m[1] + ' "' + value + '"', config, count=1)
    if count != 1:
        raise ValueError('Firmware version is missing from the release source')
    return updated


def validate(values):
    if not values['wifi_ssid'] or len(values['wifi_ssid'].encode()) > 32:
        raise ValueError('Wi-Fi name must contain 1–32 bytes.')
    if values['wifi_password'] and not 8 <= len(values['wifi_password']) <= 63:
        raise ValueError('Wi-Fi password must contain 8–63 characters (or be empty for an open network).')
    if not 8 <= len(values['fallback_ap_password']) <= 63:
        raise ValueError('Recovery hotspot password must contain 8–63 characters.')
    try:
        decoded = base64.b64decode(values['api_encryption_key'], validate=True)
        valid = len(decoded) == 32 and any(decoded)
    except Exception:
        valid = False
    if not valid:
        raise ValueError('Home Assistant key must be a Base64 encoded 32-byte key.')


def prepare(source, target, values):
    validate(values)
    target.mkdir(parents=True, exist_ok=True)
    for folder in ('src', 'media', 'components'):
        if (source / folder).exists():
            shutil.copytree(source / folder, target / folder, dirs_exist_ok=True)
    config = (source / 'esphome-smart-clock.yaml').read_text(encoding='utf-8')
    config = re.sub(r'(?m)^  build_path:.*$', '  build_path: build/${device_name}', config)
    (target / 'esphome-smart-clock.yaml').write_text(config, encoding='utf-8')
    # JSON quoted strings are valid YAML scalars, including Unicode and punctuation.
    secret_file = target / 'secrets.yaml'
    secret_file.write_text(''.join(f'{k}: {json.dumps(v)}\n' for k, v in values.items()), encoding='utf-8')
    secret_file.chmod(0o600)


def fetch(url):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'SmartClock-Desktop/0.1'})
            with urllib.request.urlopen(request, timeout=30) as response:
                if 'text/html' in response.headers.get('Content-Type', '').lower():
                    raise ValueError('A Wi-Fi login or proxy page was returned instead of update data. Connect to the Internet and retry. Your settings were kept.')
                data = response.read()
                length = response.headers.get('Content-Length')
                if length and len(data) != int(length):
                    raise http.client.IncompleteRead(data)
                return data
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 404, 407):
                raise RuntimeError(f'Update download unavailable (HTTP {exc.code}). Check network/proxy access or try again later. Your current firmware and settings were kept.') from exc
            if attempt == 2:
                raise RuntimeError('Update server unavailable after 3 attempts. Check the Internet connection and retry. Your settings were kept.') from exc
        except (urllib.error.URLError, TimeoutError, OSError, http.client.IncompleteRead) as exc:
            if attempt == 2:
                raise RuntimeError('Update download interrupted after 3 attempts. Reconnect to the Internet and click Check for updates again. Your settings were kept.') from exc
        time.sleep(attempt + 1)


def command_failure(action, details):
    if action == 'upload':
        return 'Upload did not finish. Keep the clock powered, check the USB cable/port or Wi-Fi address, and retry installation. See the details below.'
    text = '\n'.join(details).lower()
    if any(marker in text for marker in ('checksum mismatch', 'hash mismatch', 'sha256 mismatch', 'invalid crc', 'badzipfile', 'not a zip file')):
        return 'A downloaded build package failed validation. No firmware upload was started. Retry Build & install to download/validate the tools again; see details below if it persists.'
    if any(marker in text for marker in ('failed to download', 'could not download', 'connectionerror', 'nameresolutionerror', 'name resolution', 'timed out', 'certificate_verify_failed', 'proxyerror', 'network is unreachable', 'no such host', 'failed to establish a new connection')):
        return 'Build tools could not be downloaded. Check Internet access, proxy/firewall settings and the computer date, then retry Build & install. No firmware upload was started; your settings were kept.'
    return 'Configuration/build failed before any firmware upload. Check the details below, correct the reported issue and retry.'


def clean_log_line(line):
    # ESPHome dashboard output may encode ESC as literal \\033; rich/esptool
    # also emits cursor/erase commands, not just color (m) sequences.
    return re.sub(r'(?:\x1b|\\033|\\x1[bB]|\\u001[bB])\[[0-?]*[ -/]*[@-~]', '', line).rstrip()


def parse_progress(action, line):
    """Only interpret work counters, never memory/flash-usage percentages."""
    line = clean_log_line(line)
    if action == 'compile':
        match = re.match(r'^\s*\[(\d+)/(\d+)\]', line)
        if match:
            done, total = map(int, match.groups())
            if total > 0 and 0 <= done <= total:
                percent = done * 100 / total
                return dict(stage='compile', done=done, total=total, percent=percent, label=f'Compiling firmware — {percent:.0f}% ({done}/{total} tasks)')
        if any(text in line.lower() for text in ('creating factory.bin', 'generating binary image', 'successfully compiled program')):
            return dict(stage='finalize', percent=None, label='Finalizing firmware…')
    if action in ('compile', 'config') and re.search(r'\bdownload(?:ing)?\b', line, re.I):
        match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
        if match and 0 <= float(match[1]) <= 100:
            percent = float(match[1])
            return dict(stage='download', percent=percent, label=f'Downloading tools — {percent:.0f}%')
    if action == 'upload':
        if re.search(r'^\s*(?:Writing at\s+0x[0-9a-f]+|Uploading:)', line, re.I):
            match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
            if match and 0 <= float(match[1]) <= 100:
                percent = float(match[1])
                return dict(stage='transfer', percent=percent, label=f'Transferring firmware — {percent:.1f}%')
        if 'verifying written data' in line.lower():
            return dict(stage='verify', percent=None, label='Verifying written firmware…')
        if any(text in line.lower() for text in ('hash of data verified', 'hard resetting', 'waiting for result')):
            return dict(stage='restart', percent=None, label='Finishing upload / restarting clock…')
    return None


class OverallProgress:
    """A monotonic work estimate; only successful operation completion reaches 100."""
    def __init__(self):
        self.value = 0.0
        self.primary_tasks = 0

    def update(self, event):
        stage = event.get('stage', 'prepare')
        fraction = max(0, min(100, event.get('percent') or 0)) / 100
        names = {'prepare': 'Preparing build tools', 'download': 'Downloading build tools',
                 'compile': 'Compiling firmware', 'finalize': 'Finalizing firmware',
                 'compiled': 'Build complete', 'connect': 'Connecting to clock',
                 'transfer': 'Transferring firmware', 'verify': 'Verifying firmware',
                 'restart': 'Restarting clock', 'uploaded': 'Finishing installation'}
        candidate = self.value
        if stage == 'download':
            candidate = 15 * fraction
        elif stage == 'compile':
            candidate = 15
            total = event.get('total', 0)
            # Small CMake probes and nested bootloader builds aren't the whole graph.
            if total >= 16 and total >= self.primary_tasks:
                self.primary_tasks = total
                candidate = 15 + 70 * fraction
        elif stage == 'finalize':
            candidate = 88
        elif stage in ('compiled', 'connect'):
            candidate = 90
        elif stage == 'transfer':
            candidate = 90 + 8 * fraction
        elif stage == 'verify':
            candidate = 98.5
        elif stage in ('restart', 'uploaded'):
            candidate = 99
        self.value = min(99, max(self.value, candidate))
        return self.value, f'Overall — {self.value:.0f}% (estimated) · {names.get(stage, event.get("label", "Working"))}'

    def complete(self):
        self.value = 100


class App:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.busy = False
        self.overall_progress = None
        self.source = ROOT / 'firmware'
        self.latest = None
        DATA.mkdir(parents=True, exist_ok=True)
        selection = DATA / 'selected-release.txt'
        if selection.exists():
            tag = selection.read_text(encoding='utf-8').strip()
            if re.fullmatch(r'[vV]?\d+\.\d+\.\d+(?:-beta\.\d+)?', tag):
                candidate = DATA / 'downloads' / tag
                pin = candidate / 'ESPHOME_VERSION'
                if pin.exists() and pin.read_text(encoding='utf-8').strip() == importlib.metadata.version('esphome') and cache_is_current(candidate / 'esphome-smart-clock.yaml', self.source / 'esphome-smart-clock.yaml'):
                    self.source = candidate
        self.profile = DATA / 'device'
        saved = {}
        if (self.profile / 'secrets.yaml').exists():
            import yaml
            saved = yaml.safe_load((self.profile / 'secrets.yaml').read_text(encoding='utf-8')) or {}
        root.title('Smart Clock • Setup & Update')
        root.geometry('850x760')
        root.minsize(760, 690)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=8)
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Smart Clock', font=('Segoe UI', 25, 'bold')).pack(anchor='w')
        ttk.Label(frame, text='Connect • Configure • Install', font=('Segoe UI', 12)).pack(anchor='w', pady=(0, 12))
        ttk.Label(frame, text='First installation: connect a USB data cable. Later updates can use the clock’s network address.\nInternet is required. The first build can take 10–30 minutes. Keep the clock connected.').pack(anchor='w')
        form = ttk.Frame(frame)
        form.pack(fill='x', pady=12)
        form.columnconfigure(1, weight=1)
        self.values = {}
        fields = [('wifi_ssid', 'Wi-Fi name (2.4 GHz)', False, ''),
                  ('wifi_password', 'Wi-Fi password', True, ''),
                  ('fallback_ap_password', 'Recovery hotspot password', True, secrets.token_urlsafe(12)),
                  ('api_encryption_key', 'Home Assistant encryption key', True, base64.b64encode(secrets.token_bytes(32)).decode())]
        self.entries = []
        for row, (key, label, private, default) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky='w', padx=(0, 14), pady=6)
            var = tk.StringVar(value=saved.get(key, default))
            self.values[key] = var
            entry = ttk.Entry(form, textvariable=var, show='•' if private else '')
            entry.grid(row=row, column=1, sticky='ew')
            if private:
                self.entries.append(entry)
        self.show = tk.BooleanVar()
        ttk.Checkbutton(form, text='Show passwords and key', variable=self.show, command=lambda: [e.configure(show='' if self.show.get() else '•') for e in self.entries]).grid(row=4, column=1, sticky='w')
        ttk.Label(form, text='USB port / clock IP or hostname').grid(row=5, column=0, sticky='w', pady=10)
        self.device = tk.StringVar()
        self.ports = ttk.Combobox(form, textvariable=self.device)
        self.ports.grid(row=5, column=1, sticky='ew')
        ttk.Button(form, text='Find USB', command=self.scan).grid(row=5, column=2, padx=5)
        self.usb_info = tk.StringVar()
        ttk.Label(form, textvariable=self.usb_info, wraplength=550).grid(row=6, column=1, sticky='w')
        if sys.platform == 'win32':
            ttk.Button(form, text='Set up USB drivers', command=self.drivers).grid(row=6, column=2)
        ttk.Label(frame, text='Existing clock? Use its existing Home Assistant key to keep the connection.\nSettings are stored locally on this computer. Runtime controls remain available in Home Assistant.').pack(anchor='w')
        self.status = tk.StringVar(value=f'Bundled firmware: {version((self.source / "esphome-smart-clock.yaml").read_text(encoding="utf-8"))}')
        ttk.Label(frame, textvariable=self.status, wraplength=770).pack(anchor='w', pady=10)
        buttons = ttk.Frame(frame)
        buttons.pack(fill='x')
        self.actions = []
        for label, action in [('1. Save & validate', self.check), ('2. Check for updates', self.updates), ('3. Build & install', self.install)]:
            b = ttk.Button(buttons, text=label, command=action)
            b.pack(side='left', padx=(0, 8))
            self.actions.append(b)
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=10)
        self.progress_text = tk.StringVar(value='Ready')
        ttk.Label(frame, textvariable=self.progress_text).pack(anchor='w', pady=(0, 6))
        self._progress_mode = 'indeterminate'
        self.log = tk.Text(frame, height=12, wrap='word', state='disabled', font=('Consolas', 9))
        self.log.pack(fill='both', expand=True)
        self.scan()
        root.after(2500, self.watch_usb)
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.poll)

    def scan(self):
        from serial.tools.list_ports import comports
        detected = list(comports())
        supported = [p for p in detected if p.vid in USB_BRIDGE_VIDS]
        ports = [p.device for p in supported + [p for p in detected if p not in supported]]
        self.ports['values'] = ports
        self.usb_info.set(' • '.join(f'{p.device}: {p.description}' for p in supported) or 'No recognized ESP USB bridge. Check cable or set up drivers.')
        # The uploader captures its target before starting. Never switch that
        # visible selection underneath an active build/upload.
        if not self.busy:
            current = self.device.get()
            selected = select_usb_target(current, detected)
            if selected != current:
                self.device.set(selected)
            if not selected and len(supported) > 1:
                self.usb_info.set('Multiple ESP USB bridges found. Select your clock’s port from the list. ' + self.usb_info.get())

    def watch_usb(self):
        self.scan()
        self.root.after(2500, self.watch_usb)

    def drivers(self):
        if self.busy:
            return
        if not messagebox.askokcancel('USB driver setup', 'Check Windows Update for a signed driver matching the connected ESP USB bridge?\nInternet and administrator approval are required. Reconnect USB afterward.'):
            return
        script = ROOT / 'install_drivers.ps1'
        def task():
            args = subprocess.list2cmdline(['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(script)])
            code = "$ErrorActionPreference='Stop'; $p=Start-Process powershell.exe -Verb RunAs -WindowStyle Hidden -Wait -PassThru -ArgumentList '" + args.replace("'", "''") + "'; exit $p.ExitCode"
            result = subprocess.run(['powershell.exe', '-NoProfile', '-Command', code],
                                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            report = DATA / 'driver-result.txt'
            text = report.read_text(encoding='utf-8-sig') if report.exists() else 'Driver setup was cancelled or could not start.'
            if result.returncode:
                raise RuntimeError(text)
            return text
        self.start(task)

    def close(self):
        if self.busy:
            messagebox.showinfo('Operation in progress', 'Wait for the build or installation to finish before closing.')
        else:
            self.root.destroy()

    def poll(self):
        while not self.events.empty():
            kind, text = self.events.get()
            if kind == 'progress':
                if self.overall_progress is not None:
                    percent, label = self.overall_progress.update(text)
                    self.show_progress(label, percent)
                else:
                    self.show_progress(text['label'], text['percent'])
            elif kind in ('done', 'failed'):
                self.busy = False
                self.progress.stop()
                if kind == 'done':
                    if self.overall_progress is not None:
                        self.overall_progress.complete()
                    self.show_progress('Completed — 100%', 100)
                else:
                    prefix = f'Stopped at about {self.overall_progress.value:.0f}%' if self.overall_progress else 'Stopped'
                    self.progress_text.set(prefix + ' — see details below and retry')
                for b in self.actions:
                    b.configure(state='normal')
                self.status.set(text)
            else:
                self.log.configure(state='normal')
                self.log.insert('end', text + '\n')
                self.log.see('end')
                self.log.configure(state='disabled')
        self.root.after(100, self.poll)

    def show_progress(self, label, percent=None):
        mode = 'indeterminate' if percent is None else 'determinate'
        if mode != self._progress_mode:
            self.progress.stop()
            self.progress.configure(mode=mode, maximum=100, value=0)
            self._progress_mode = mode
            if mode == 'indeterminate':
                self.progress.start()
        if percent is not None:
            self.progress['value'] = max(0, min(100, percent))
        self.progress_text.set(label)

    def start(self, task, overall_install=False):
        if self.busy:
            return
        self.busy = True
        self.overall_progress = OverallProgress() if overall_install else None
        for b in self.actions:
            b.configure(state='disabled')
        self.progress.stop()
        self._progress_mode = None
        self.show_progress('Overall — 0% (estimated) · Preparing…' if overall_install else 'Preparing…', 0 if overall_install else None)
        def work():
            try:
                result = task()
                self.events.put(('done', result))
            except Exception as exc:
                self.events.put(('log', str(exc)))
                self.events.put(('failed', str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def save(self):
        values = {k: v.get() for k, v in self.values.items()}
        prepare(self.source, self.profile, values)
        return values

    def command(self, *args):
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        env['PYTHONUNBUFFERED'] = '1'
        env.pop('PYTHONHOME', None)
        env.pop('PYTHONPATH', None)
        env['PYTHONNOUSERSITE'] = '1'
        scripts = Path(sys.executable).parent / 'Scripts' if sys.platform == 'win32' else Path(sys.executable).parent
        paths = [str(scripts), str(ROOT / ('git/cmd' if sys.platform == 'win32' else 'git/bin')), str(ROOT / 'git/usr/bin')]
        env['PATH'] = os.pathsep.join(paths + [env.get('PATH', '')])
        if sys.platform == 'darwin' and (ROOT / 'git/libexec/git-core').exists():
            env['GIT_EXEC_PATH'] = str(ROOT / 'git/libexec/git-core')
            env['GIT_TEMPLATE_DIR'] = str(ROOT / 'git/share/git-core/templates')
        elif sys.platform == 'darwin':
            env.pop('GIT_EXEC_PATH', None)
            env.pop('GIT_TEMPLATE_DIR', None)
            env['DYLD_FALLBACK_LIBRARY_PATH'] = str(Path(sys.prefix) / 'lib') + ':' + env.get('DYLD_FALLBACK_LIBRARY_PATH', '/usr/local/lib:/usr/lib')
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        values = __import__('yaml').safe_load((self.profile / 'secrets.yaml').read_text(encoding='utf-8'))
        executable = str(Path(sys.executable).with_name('python.exe')) if sys.platform == 'win32' else sys.executable
        details = deque(maxlen=100)
        phase = {'compile': 'Preparing build / downloading tools…', 'upload': 'Connecting to clock…', 'config': 'Validating settings…'}.get(args[0], 'Working…')
        self.events.put(('progress', dict(stage={'compile': 'prepare', 'upload': 'connect', 'config': 'validate'}.get(args[0], 'prepare'), label=phase, percent=None)))
        # Dashboard mode keeps OTA progress frames enabled when stdout is a pipe.
        # -I ignores PYTHONUTF8; force UTF-8 explicitly for Windows tool output.
        with subprocess.Popen([executable, '-I', '-X', 'utf8', '-m', 'esphome', '--dashboard', *args], cwd=self.profile, env=env,
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding='utf-8', errors='replace', creationflags=flags) as process:
            for line in process.stdout:
                for secret in values.values():
                    if secret:
                        line = line.replace(secret, '[private]')
                clean = clean_log_line(line)
                details.append(clean)
                self.events.put(('log', clean))
                progress = parse_progress(args[0], clean)
                if progress:
                    self.events.put(('progress', progress))
            if process.wait():
                raise RuntimeError(command_failure(args[0], details))
        self.events.put(('progress', dict(stage={'compile': 'compiled', 'upload': 'uploaded', 'config': 'validated'}.get(args[0], 'complete'), label={'compile': 'Build complete — 100%', 'upload': 'Upload completed — 100%', 'config': 'Settings validated — 100%'}.get(args[0], 'Completed — 100%'), percent=100)))

    def check(self):
        try:
            self.save()
        except Exception as exc:
            messagebox.showerror('Check settings', str(exc))
            return
        self.start(lambda: (self.command('config', 'esphome-smart-clock.yaml'), 'Settings saved and configuration validated.')[1])

    def updates(self):
        def task():
            releases = json.loads(fetch(f'https://api.github.com/repos/{REPO}/releases?per_page=100'))
            release = next((r for r in releases if not r['draft']), None)
            if not release:
                return 'No published releases found. Bundled firmware remains selected.'
            tag = release['tag_name']
            if not re.fullmatch(r'[vV]?\d+\.\d+\.\d+(?:-beta\.\d+)?', tag):
                raise ValueError('Unsupported release version; bundled firmware remains selected.')
            current = version((self.source / 'esphome-smart-clock.yaml').read_text(encoding='utf-8'))
            if release_order(tag) <= release_order(current):
                return f'Firmware {current} is up to date (including beta releases).'
            archive = zipfile.ZipFile(io.BytesIO(fetch(f'https://api.github.com/repos/{REPO}/zipball/{tag}')))
            target = DATA / 'downloads' / tag
            prefix = archive.namelist()[0].split('/')[0] + '/'
            required = archive.read(prefix + 'ESPHOME_VERSION').decode().strip()
            if required != importlib.metadata.version('esphome'):
                raise ValueError(f'This firmware requires ESPHome {required}. Download the matching newer desktop app first.')
            # Extract only firmware inputs; no archive paths may escape the target.
            for member in archive.infolist():
                name = member.filename.removeprefix(prefix)
                if name == 'esphome-smart-clock.yaml' or name.startswith(('src/', 'media/', 'components/')):
                    dest = (target / name).resolve()
                    if not dest.is_relative_to(target.resolve()):
                        raise ValueError('Unsafe archive path')
                    if not member.is_dir():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_bytes(archive.read(member))
            yaml_file = target / 'esphome-smart-clock.yaml'
            yaml_file.write_text(release_config(yaml_file.read_text(encoding='utf-8'), tag), encoding='utf-8')
            (target / 'ESPHOME_VERSION').write_text(required, encoding='utf-8')
            (DATA / 'selected-release.txt').write_text(tag, encoding='utf-8')
            self.source = target
            return f'Update {tag} downloaded and selected. Click Build & install to apply your personal settings.'
        self.start(task)

    def install(self):
        self.scan()
        device = self.device.get().strip()
        if not device or device.startswith('-'):
            messagebox.showerror('Choose a clock', 'Select a USB port or enter the clock’s IP address.')
            return
        try:
            self.save()
        except Exception as exc:
            messagebox.showerror('Check settings', str(exc))
            return
        if not messagebox.askokcancel('Install firmware', f'Build personalized firmware and install it on {device}?\nKeep power connected until installation finishes.'):
            return
        def task():
            config = 'esphome-smart-clock.yaml'
            self.command('compile', config)
            self.command('upload', config, '--device', device)
            return 'Firmware uploaded successfully. The clock is restarting. Add it to Home Assistant using the saved key.'
        self.start(task, overall_install=True)


if __name__ == '__main__':
    App(tk.Tk()).root.mainloop()
