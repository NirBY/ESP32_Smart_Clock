# Listing fields

- Title: **ESP32 Smart Clock - LED Matrix, Speaker & Sensor**
- Creator: **NirBY**
- Source: **Original** (confirmed by creator)
- License: **CC BY-NC-SA 4.0**
- Suggested listing: **Free**, non-exclusive
- Print method: **FFF / FDM**
- Suggested category: **Gadgets / Electronics**; choose the closest available category in the upload form.
- Tags: `ESP32`, `smart clock`, `LED matrix`, `MAX7219`, `Home Assistant`, `ESPHome`, `electronics enclosure`, `PLA`
- Main model files: `stl/body.stl`, `stl/lid.stl`, `stl/sensor_cage.stl`
- Optional fit samples: both files in `test-pieces/`; label them as optional.
- Covers: repository `docs/images/promo-4x3.png` and `promo-3x4.png` (illustrative feature showcases). Real assembly and component photos are in `docs/images/`; `previews/` contains STL-based CAD renders.
- Assembly attachment: `PRINT_GUIDE.pdf`.

## Description to paste

A rounded three-part enclosure for a DIY ESP32 smart clock with an 8x32 MAX7219 display, speaker, NS4168 amplifier and external AHT20/BMP280 sensor. Designed by NirBY for measured hardware, with accessible USB-C connectors on opposite sides, two feet, concealed sensor wiring and M3 brass inserts.

Show time, countdowns, temperature and humidity, or your own messages sent from Home Assistant. Includes a daily alarm and speaker support. Six optional Home Assistant MCP scripts cover status, settings, timers, alarms, messages and Music Assistant playback. These require installation and end-to-end verification; no MCP server runs on the ESP32. Promotional display modes are illustrative; real build photos are also included.

The front is closed by a continuous 0.6 mm diffuser. Print the body in white PLA: this thickness was successfully checked by the creator. Opaque black PLA blocks the LEDs.

IMPORTANT: The lid requires a print pause to install two inserts. Print the first layer AND all subsequent layers at 0.15 mm. Pause AFTER Z 4.05 mm (27 completed layers), BEFORE Z 4.20 mm. Heat-set two M3 inserts, length 2.9 mm, so their tops are below the paused surface, then resume. Their pockets are closed from outside by an integral 0.6 mm skin. Print the small ESP fit sample first. The latest full assembly and this pause workflow have not yet been physically validated.

Print one body, one lid and one sensor cage, in the supplied orientations, at 100% scale in millimetres. Body: 158 x 60 x 49.7 mm. Overall with lid, feet and cage: 158 x 77.5 x 51.2 mm. PLA / Ender-3 V3 KE is the design target. Body layer height: 0.20 mm including first layer, at least three solid bottom layers. Suggested starting point: 0.4 mm nozzle, three perimeters, 20% infill; inspect bridges and overhangs in your slicer. Keep supports out of insert pockets and wire openings. No machine-specific G-code or tested slicing profile is included.

Compatible measured components: display 132.1 x 32.1 x 17.8 mm wired; ESP32 PCB 51.6 x 28.2 mm, 53.5 mm with USB projection, 23 mm wired depth; speaker 69.7 x 31.2 x 16.6 mm; amplifier PCB 38.5 x 22.4 mm, 42.4 mm wired length and 10.1 mm height; sensor 15 x 15 x 7.6 mm; snap-in power USB-C body 12.8 x 5.2 mm with 12.7 mm depth behind flange. Check your hardware against the guide: board variants differ.

Hardware: 14 M3 inserts, 2.9 mm long and 4.2 mm maximum outside diameter. Screw lengths and washers are listed in the illustrated guide. Use four lid screws, four ESP screws, two speaker screws, two amplifier screws and two cage screws. The sensor PCB rests loose in its external cage; the display is located by four separate L-shaped stops.

All three assembly STLs are single watertight solids and have passed geometric fit checks. Physical tolerances, buttons, springs and flexible wires still need a fit check. The two optional fit samples are not assembly parts.

Firmware, wiring and source: https://github.com/NirBY/ESP32_Smart_Clock

Copyright (c) 2026 NirBY. Licensed CC BY-NC-SA 4.0: give credit, use noncommercially, and share adaptations under the same license. https://creativecommons.org/licenses/by-nc-sa/4.0/
