"""Add download guidance to GitHub asset labels without renaming any files."""
import argparse
import json
import os
import subprocess

LABELS = {
    'SmartClock-Windows-x64.exe': 'Windows setup EXE - start here',
    'SmartClock-macOS.dmg': 'macOS setup DMG - Apple Silicon and Intel',
    'SmartClock-Windows-x64.sha256': 'Windows setup - SHA-256 checksum',
    'SmartClock-macOS.sha256': 'macOS setup - SHA-256 checksum',
    'esphome-smart-clock.factory.bin': 'ESPHome factory firmware - USB recovery, example credentials',
    'esphome-smart-clock.ota.bin': 'ESPHome OTA firmware - network update, example credentials',
    'esphome-smart-clock.ota.md5': 'ESPHome OTA firmware - MD5 checksum',
    'platformio-hardware-test.bin': 'Hardware-test firmware - wiring and module diagnostics',
    'bluetooth-speaker.bin': 'Bluetooth speaker firmware - replaces the ESPHome clock',
    'firmware-manifest.json': 'Home Assistant firmware-update manifest',
    'release-provenance.json': 'Build provenance - source commit and asset SHA-256 hashes',
}


def label(name):
    if name.startswith('SmartClock-runtime-Windows-x64-'):
        return ('Windows runtime - SHA-256 checksum' if name.endswith('.sha256')
                else 'Windows runtime ZIP - downloaded automatically by setup')
    return LABELS.get(name)


def api(endpoint, payload=None):
    command = ['gh', 'api', endpoint]
    if payload is not None:
        command += ['--method', 'PATCH', '--input', '-']
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            text=True, encoding='utf-8', capture_output=True, check=True)
    return json.loads(result.stdout)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tag')
    args = parser.parse_args()
    repo = os.environ.get('GITHUB_REPOSITORY', 'NirBY/ESP32_Smart_Clock')
    base = f'repos/{repo}/releases'
    release = api(f'{base}/tags/{args.tag}')
    count = 0
    for asset in release['assets']:
        description = label(asset['name'])
        if description and asset.get('label') != description:
            updated = api(f"{base}/assets/{asset['id']}", {'label': description})
            assert updated['name'] == asset['name'] and updated['label'] == description
            count += 1
    print(f'Added descriptions to {count} release assets; filenames and URLs preserved')
