"""Relocate Homebrew Git and its non-system Mach-O dependencies into the app."""
from pathlib import Path
import os
import re
import shutil
import subprocess


def bundle_git(destination):
    prefix = Path(subprocess.check_output(['brew', '--prefix', 'git'], text=True).strip())
    shutil.copytree(prefix, destination, dirs_exist_ok=True, symlinks=False,
                    ignore=shutil.ignore_patterns('doc', 'man'))
    libraries = destination / 'bundled-libs'
    libraries.mkdir(exist_ok=True)
    pending = [p for p in destination.rglob('*') if p.is_file()]
    visited = set()
    while pending:
        binary = pending.pop()
        if binary in visited:
            continue
        visited.add(binary)
        with binary.open('rb') as stream:
            magic = stream.read(4)
        if magic not in (b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca'):
            continue
        binary.chmod(binary.stat().st_mode | 0o200)
        if binary.suffix == '.dylib':
            subprocess.run(['install_name_tool', '-id', '@rpath/' + binary.name, str(binary)], check=True)
        lines = subprocess.check_output(['otool', '-L', str(binary)], text=True).splitlines()[1:]
        for line in lines:
            dependency = line.strip().split(' (', 1)[0]
            if not dependency.startswith(('/opt/homebrew/', '/usr/local/')):
                continue
            source = Path(dependency).resolve()
            target = libraries / source.name
            if not target.exists():
                shutil.copy2(source, target)
                pending.append(target)
            relative = os.path.relpath(target, binary.parent)
            subprocess.run(['install_name_tool', '-change', dependency, '@loader_path/' + relative, str(binary)], check=True)
        load_commands = subprocess.check_output(['otool', '-l', str(binary)], text=True)
        for rpath in re.findall(r'\bpath (.*?) \(offset', load_commands):
            if rpath.startswith(('/opt/homebrew/', '/usr/local/')):
                subprocess.run(['install_name_tool', '-delete_rpath', rpath, str(binary)], check=True)
        subprocess.run(['codesign', '--force', '--sign', '-', str(binary)], check=True, capture_output=True)
