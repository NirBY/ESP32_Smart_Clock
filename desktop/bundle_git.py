"""Bundle the checksum-pinned official MinGit distribution for applications."""
from pathlib import Path
import hashlib
import json
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def get_mingit():
    pin = json.loads((ROOT / 'desktop/mingit.json').read_text(encoding='utf-8'))
    cache = ROOT / 'outputs/mingit' / pin['version']
    marker = cache / '.mingit-complete'
    if marker.exists() and marker.read_text(encoding='utf-8') == pin['sha256'] and (cache / 'cmd/git.exe').is_file():
        return cache
    archive = ROOT / 'outputs/mingit' / (pin['version'] + '.zip')
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest() != pin['sha256']:
        print('Downloading official MinGit (build machine only)...', flush=True)
        request = urllib.request.Request(pin['url'], headers={'User-Agent': 'SmartClock-Builder'})
        with urllib.request.urlopen(request, timeout=120) as response:
            archive.write_bytes(response.read())
    if hashlib.sha256(archive.read_bytes()).hexdigest() != pin['sha256']:
        raise RuntimeError('MinGit download checksum mismatch')
    with zipfile.ZipFile(archive) as contents:
        for member in contents.infolist():
            target = (cache / member.filename).resolve()
            if not target.is_relative_to(cache.resolve()):
                raise RuntimeError('Invalid MinGit archive path')
            if not member.is_dir():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(contents.read(member))
    if not (cache / 'cmd/git.exe').is_file():
        raise RuntimeError('MinGit archive does not contain git.exe')
    marker.write_text(pin['sha256'], encoding='ascii')
    return cache


def bundle_git(destination):
    source = get_mingit()
    destination = destination.resolve()
    if not destination.is_relative_to((ROOT / 'outputs').resolve()) or destination.name != 'git':
        raise RuntimeError('Refusing to replace Git outside the build output')
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns('.mingit-complete'))


if __name__ == '__main__':
    bundle_git(ROOT / 'outputs/SmartClock-Windows/git')
