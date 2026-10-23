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

The 0.6 mm front diffuser consists of four solid layers. Do not enable adaptive layers or change the first-layer height without recalculating the insert pause.

## Required insert pause

The printer's before-layer-change script emits **PAUSE before Z 4.20 mm**, after 27 layers / Z 4.05 mm have completed. Install the lid's two concealed M3 inserts (2.9 mm long, 4.2 mm outside diameter) with their tops below the paused surface, following the illustrated print guide. Resume only after the installation tool is removed and both inserts are seated. Keep the pause when importing or converting this project.

## Validation and limitations

OrcaSlicer 2.4.2 successfully sliced these settings and all three parts: approximately **6 h 4 min / 90 g PLA**, excluding the manual pause. The generated toolpath was checked for exactly one PAUSE before the 4.20 mm layer, 60 degrees C bed, and no objects outside the bed. The editable project is supplied instead of that machine-specific G-code.

This profile has **not been physically printed**. The creator verified the white PLA 0.6 mm diffuser separately. Inspect bridges, the sensor cage and insert pockets in the layer preview. Confirm that your KE firmware supports the PAUSE macro. After Creality Cloud conversion, re-slice and verify the pause is still present. Temperature settings are starting values; use your PLA manufacturer's range. Orca may warn that the bed temperature exceeds PLA's softening threshold; this is a bed-temperature advisory, not a successful physical validation.

Printer defaults derive from OrcaSlicer's bundled Creality Ender-3 V3 KE presets. Rebuild with `tools/build_print_profile.py`; install official OrcaSlicer separately. Design license: CC BY-NC-SA 4.0, NirBY.

## Creality Cloud variant

`ESP32_Clock_Ender3V3KE_Creality.3mf` preserves the same original plate geometry in the Creality project schema. Cloud conversion originally reset the machine to K2 Plus and erased the pause; the supplied variant restores the checked KE settings and pause. It was independently re-sliced successfully in OrcaSlicer (6 h 3 min). Use the Orca-named project for OrcaSlicer, or this variant for the Creality listing. Neither file contains executable G-code.
