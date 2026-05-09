# Calendar And Announcements

The calendar agenda blueprint lets Home Assistant read today's events, show a
compact agenda on the ESP32 Smart Clock matrix, and optionally speak the agenda
through the clock speaker.

Import the blueprint:

[![Import ESP32 Smart Clock calendar agenda automation](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FNirBY%2FESP32_Smart_Clock%2Fblob%2Fmain%2Fdocs%2Fblueprints%2Fautomation%2Fesp32_smart_clock_calendar_agenda.yaml)

The blueprint file is:

`docs/blueprints/automation/esp32_smart_clock_calendar_agenda.yaml`

## What It Does

- Calls `calendar.get_events` for today, from `00:00` to `23:59:59`.
- Builds a short matrix message like `Today: 09:00 Work; 18:30 Dinner`.
- Sends that message to `esphome.esp32_smart_clock_show_message`.
- Optionally calls `tts.speak` and plays the spoken agenda on the clock speaker.
- Runs from a daily time trigger, an `input_button` helper, or both.

## Required Entities

Select these when creating the automation from the blueprint:

| Blueprint input | Example | Purpose |
|---|---|---|
| Calendar | `calendar.family` | Source for today's events |
| Clock display action | `esphome.esp32_smart_clock_show_message` | Prints the agenda on the matrix |
| TTS provider | `tts.home_assistant_cloud` | Converts the agenda to speech |
| Clock speaker | `media_player.esp32_smart_clock_speaker` | Plays the spoken agenda |
| Manual run input button | `input_button.esp32_smart_clock_today_events` | Optional dashboard/manual trigger |

Entity IDs can be different on your Home Assistant system. Use Developer Tools >
States to confirm the exact IDs.

## Run At A Specific Time

Keep **Run every day at a specific time** enabled and choose **Daily agenda
time**. For example, set it to `07:30:00` for a morning agenda.

If you only want a manual button, turn **Run every day at a specific time** off.

## Run From A Button

Create a helper:

1. Open Home Assistant.
2. Go to Settings > Devices & services > Helpers.
3. Create helper.
4. Choose Button.
5. Name it `ESP32 Smart Clock Today Events`.
6. Select that input button in the blueprint.

You can add the helper button to any dashboard. Pressing it runs the same
calendar display and TTS action immediately.

If you do not want a manual button, leave the default dummy
`input_button.esp32_smart_clock_today_events` value. The scheduled trigger still
works, and the missing helper simply never fires a manual trigger.

## Display And TTS Options

- **Show events on the clock display** controls the LED matrix message.
- **Speak events with TTS** controls whether Home Assistant speaks the agenda.
- **Maximum events** limits how many events are printed and spoken.
- **Display prefix** defaults to `Today:`.
- **No events** messages can be customized separately for display and speech.

The display is intentionally compact because the matrix is only 8x32 pixels. For
long event names, the firmware scrolls the message.

## Notes

- The speaker pipeline is tuned for low-memory TTS and announcements. This is a
  better fit than high-quality music streaming.
- If the speaker is already busy, ESPHome may reject or interrupt audio
  depending on Home Assistant timing.
- Calendar event details come from Home Assistant, so permissions and calendar
  integration setup are handled there.
