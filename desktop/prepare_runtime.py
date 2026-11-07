"""Unpack the bundled Git tools once, using the bundled Python runtime."""
from pathlib import Path
import sys

import py7zr

root = Path(__file__).resolve().parent
if len(sys.argv) != 2 or Path(sys.argv[1]).resolve() != root:
    raise SystemExit('Invalid runtime directory')
with py7zr.SevenZipFile(root / 'git.7z') as archive:
    for name in archive.getnames():
        if not (root / name).resolve().is_relative_to(root):
            raise SystemExit('Invalid archive path')
    archive.extractall(root)
(root / 'git.7z').unlink()
if not (root / 'git/cmd/git.exe').is_file():
    raise SystemExit('Bundled Git was not extracted')

# Do not mark a runtime as installed until its core libraries can actually load.
import tkinter
import esphome
import esptool
import platformio
import serial
import ssl
tkinter.Tcl().eval('info patchlevel')
