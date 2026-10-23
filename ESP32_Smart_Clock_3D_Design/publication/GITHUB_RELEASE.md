# ESP32 Smart Clock enclosure - revision 18

Three final printable parts: `body.stl`, `lid.stl` and `sensor_cage.stl`. This replaces previous enclosure files with one current design and portable OpenSCAD source.

The rounded enclosure includes a 0.6 mm white-PLA front diffuser, two feet, four separate display stops, D-relieved ESP mounts, side USB access, low speaker/amplifier mounts, and an external sensor cage. The two ESP insert access holes are closed by an integral 0.6 mm lid skin.

**Lid print pause required:** fixed 0.15 mm layers including the first; pause after Z 4.05 mm, before Z 4.20 mm, to install two M3 inserts. Follow the included guide and try the ESP fit sample first.

## Assets

- `ESP32_Smart_Clock_Final_STLs.zip`: the three final STLs, instructions and previews.
- `ESP32_Smart_Clock_Creality_Upload.zip`: models, optional fit samples, square cover images, PDF guide and listing text.
- `ESP32_Smart_Clock_GitHub_Source.zip`: editable source, validation scripts/reports, models and publication materials.
- `SHA256SUMS.txt`: checksums for the main models and ZIPs.

Units: millimetres. Scale: 100%. Assembled envelope: 158 x 77.5 x 51.2 mm. Design license: CC BY-NC-SA 4.0, NirBY.

All main STLs and fit samples are single watertight solids. Six geometry checks passed, covering assembly clearances, insert closures, USB openings, vents and sensor installation. The white-PLA 0.6 mm diffuser was physically tested; the complete latest assembly and insert-pause workflow remain untested. Publish as a prerelease until physical validation is complete.

This is an enclosure release, with no firmware binaries or changes to the firmware update channel.
