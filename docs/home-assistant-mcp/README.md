# Clock tools for Home Assistant MCP

The MCP server runs in **Home Assistant**, not on the ESP32. These six scripts
extend HA's Assist LLM API with parameterized tools. ESPHome continues to handle
the physical clock through its existing encrypted native API.

| Tool | Capability |
|---|---|
| Status | Temperature, humidity, pressure, timer, alarm, settings, speaker, firmware versions |
| Timer | Start for 1–86400 seconds, pause, resume, cancel |
| Alarm | Set and enable a daily alarm, enable or disable an existing alarm |
| Message | Show up to 100 characters, or clear with an empty string |
| Setting | All 18 number settings, all five switches, time format |
| Music | Music Assistant search/play, pause, resume, stop, next/previous, volume, mute |

The firmware itself does not add an AI model, microphone, Google Home timer
synchronization, or a new network server. Music search needs an installed Music
Assistant integration and configured providers. Audio is limited by the current
16 kHz mono firmware pipeline. Firmware installation is deliberately not a tool:
public binaries replace private Wi-Fi/API configuration; use local ESPHome builds.

## Install

1. Inspect the entity IDs in `package.yaml` against your HA installation. Entity
   names can differ, especially on newly installed devices and Music Assistant.
   Also verify `esphome.esp32_smart_clock_start_timer` in HA Actions.
2. With packages enabled, copy `package.yaml` to
   `/config/packages/esp32_clock_mcp.yaml`, check configuration, and restart HA.
   If needed, merge this under the **existing** `homeassistant:` block:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

   Alternatively create six scripts in HA, select Edit in YAML, and paste each
   corresponding `esp32_clock_mcp_*.yaml` file. Do not install both ways.
3. Expose the six scripts to **Assist** through each script's Settings > Voice
   assistants. Their descriptions and field selectors become LLM tool schemas.
4. Add/configure **Model Context Protocol Server**, select the Assist LLM API,
   and retain authentication/admin requirements. Do not turn on every LLM API
   merely to expose this clock. Assist can also expose other entities already
   enabled for Assist; review those before granting an external AI access.
5. Connect your MCP client to your HA server's `/api/mcp/assist` endpoint using
   supported HA authentication. Never commit tokens, private hostnames or keys.
6. Reconnect the MCP client and inspect its tool list. Test Status, then a
   temporary screen message, then a short timer. Check HA script traces and
   physical playback. An accepted command is not proof of audible playback.

Examples: “Set the clock timer to seven minutes”, “Set the clock daily alarm to
07:30”, “Show HELLO on the clock”, “Play an album by Queen on the clock”, “What
are the clock temperature and humidity?”, “Show countdown for 10 seconds and
clock time for 2 seconds”.

The package validates inputs at runtime, not just in UI selectors. It only
targets the clock IDs listed in the files and cannot execute arbitrary services
or target arbitrary entities. Unknown/unavailable sensor values are returned
explicitly. Timer and alarm changes report `command_sent`; use Status to read
the subsequent device state.

## Verification status

The package is supplied for installation and testing. It is **not yet verified
end-to-end through a live MCP client**. The ESPHome timer and audible completion
melody have been tested on the physical clock. No private HA settings are
included. Regenerate with `python tools/build_ha_mcp_package.py` (PyYAML required).

References: [HA MCP Server](https://www.home-assistant.io/integrations/mcp_server/),
[exposing scripts to LLMs](https://www.home-assistant.io/voice_control/exposing_scripts_to_llms/),
[Music Assistant play media](https://www.home-assistant.io/actions/music_assistant.play_media/).
