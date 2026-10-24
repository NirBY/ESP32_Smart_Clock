"""Use local sources for pre-release validation, before the tag exists."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
out = root / 'outputs/package-check'
out.mkdir(parents=True, exist_ok=True)
text = (root / 'packages/smart-clock.yaml').read_text()
text = text.replace('type: git\n      url: https://github.com/${github_repo}.git\n      ref: v${firmware_version}',
                    'type: local\n      path: ../../components')
for name in ('timer-finished', 'volume-beep'):
    text = text.replace(f'https://raw.githubusercontent.com/${{github_repo}}/v${{firmware_version}}/media/{name}.wav', f'../../media/{name}.wav')
(out / 'package.yaml').write_text(text)
shutil.copyfile(root / 'secrets.example.yaml', out / 'secrets.yaml')
(out / 'check.yaml').write_text('''packages:
  clock: !include package.yaml
substitutions:
  api_encryption_key: !secret api_encryption_key
  wifi_ssid: !secret wifi_ssid
  wifi_password: !secret wifi_password
  fallback_ap_password: !secret fallback_ap_password
''')
