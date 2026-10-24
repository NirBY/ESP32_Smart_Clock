# Ender-3 V3 KE print configuration

Open `ESP32_Clock_Ender3V3KE_PLA_015mm.3mf` as a project in OrcaSlicer 2.4.2 or a compatible slicer. It contains all three final parts, arranged on one 220 x 220 mm plate, and editable printer, filament and process settings. Slice before printing; this project intentionally does not supply executable G-code.

| Setting | Value |
|---|---|
| Printer / nozzle | Creality Ender-3 V3 KE / 0.4 mm |
| Material | White PLA, 1.75 mm |
| Plate | Textured PEI |
| First and subsequent layers | 0.15 mm, fixed |
| Walls | 3 |
| Top / bottom solid layers | 4 / 4 |
| Infill | 20% gyroid |
| Nozzle / bed | 210 / 60 degrees C |
| Supports | Disabled |
| Scale | 100%, millimetres |
| Print sequence | By layer |

The 0.6 mm front diffuser consists of four solid layers with these settings.

The creator has successfully printed and assembled the clock in one continuous print.
The profiles contain the three final parts and editable settings; slice for your printer
before printing. Temperature settings are starting values for white PLA.

Printer defaults derive from OrcaSlicer's bundled Creality Ender-3 V3 KE presets.
Rebuild with `tools/build_print_profile.py`; install official OrcaSlicer separately.
Design license: CC BY-NC-SA 4.0, NirBY.

## Creality Cloud variant

`ESP32_Clock_Ender3V3KE_Creality.3mf` preserves the same plate geometry in the
Creality project schema. Use the Orca-named project for OrcaSlicer, or this variant
for the Creality listing. Neither file contains executable G-code.
