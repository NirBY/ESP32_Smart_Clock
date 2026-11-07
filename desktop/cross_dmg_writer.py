"""Windows build-only bootstrap for a checksum-pinned HFSX/UDIF writer."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'outputs/dmg-tools'


def fetch(url, file, checksum):
    if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest() != checksum:
        print('Downloading DMG build tool:', file.name, flush=True)
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'SmartClock-DMG-Builder'}), timeout=120) as response:
            file.write_bytes(response.read())
    if hashlib.sha256(file.read_bytes()).hexdigest() != checksum:
        raise RuntimeError('DMG build tool checksum mismatch: ' + file.name)


def extract(archive, destination, prefix='', go_sdk=False):
    with zipfile.ZipFile(archive) as source:
        for member in source.infolist():
            name = member.filename.removeprefix(prefix)
            if go_sdk and (not name.startswith(('go/bin/', 'go/pkg/', 'go/src/')) or '/testdata/' in name or name.endswith('_test.go')):
                continue
            target = (destination / name).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise RuntimeError('Invalid tool archive path')
            if not member.is_dir():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read(member))


def ensure_writer():
    TOOLS.mkdir(parents=True, exist_ok=True)
    pins = json.loads((ROOT / 'desktop/dmg_tools.json').read_text())
    output = TOOLS / 'smartclock-dmg-writer.exe'
    fingerprint = hashlib.sha256((json.dumps(pins, sort_keys=True) + (ROOT / 'desktop/dmg_writer_main.go').read_text() + 'windows-posix-modes-v1').encode()).hexdigest()
    marker = TOOLS / 'writer-built.txt'
    if output.exists() and marker.exists() and marker.read_text() == fingerprint:
        return output
    go_zip = TOOLS / 'go-sdk.zip'
    fetch(pins['go_url'], go_zip, pins['go_sha256'])
    goroot = TOOLS / 'go'
    if not (TOOLS / 'go-ready.txt').exists():
        print('Preparing portable Go compiler (build machine only)...', flush=True)
        extract(go_zip, TOOLS, go_sdk=True)
        (TOOLS / 'go-ready.txt').write_text(pins['go_sha256'])
    source_zip = TOOLS / 'writer-source.zip'
    fetch(pins['writer_url'], source_zip, pins['writer_sha256'])
    source_dir = TOOLS / 'writer-source'
    with zipfile.ZipFile(source_zip) as contents:
        prefix = contents.namelist()[0].split('/')[0] + '/'
    extract(source_zip, source_dir, prefix=prefix)
    # Windows has no Unix execute bits. Explicitly record correct Mac modes in
    # the HFS catalog instead of Go's synthetic Windows 0666/0777 values.
    implementation = source_dir / 'dmg.go'
    code = implementation.read_text()
    code = code.replace('"sort"', '"sort"\n "runtime"\n "strings"')
    code = code.replace('return uint16(info.Mode().Perm())', '''if runtime.GOOS == "windows" {
        if info.IsDir() || info.Name() == "SmartClock" || strings.HasSuffix(info.Name(), ".command") { return 0o755 }
        return 0o644
    }
    return uint16(info.Mode().Perm())''')
    implementation.write_text(code)
    main = source_dir / 'examples/smartclock/main.go'
    main.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'desktop/dmg_writer_main.go', main)
    env = os.environ.copy()
    env.update(GOROOT=str(goroot), GOPATH=str(TOOLS / 'modules'), GOCACHE=str(TOOLS / 'go-cache'),
               GOTOOLCHAIN='local', GOENV='off', GOPROXY='https://proxy.golang.org,direct',
               GOSUMDB='sum.golang.org', GONOSUMDB='', GONOPROXY='', GOPRIVATE='',
               GOINSECURE='', GOFLAGS='', GOOS='windows', GOARCH='amd64', CGO_ENABLED='0')
    print('Compiling pinned cross-platform DMG writer...', flush=True)
    subprocess.run([str(goroot / 'bin/go.exe'), 'build', '-trimpath', '-o', str(output), './examples/smartclock'], cwd=source_dir, env=env, check=True)
    marker.write_text(fingerprint)
    return output


if __name__ == '__main__':
    print(ensure_writer())
