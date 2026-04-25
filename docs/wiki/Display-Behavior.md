# Display Behavior

The display follows a fixed 7-rule spec. Anything not covered by these rules falls back to the clock.

## Clock Display Logic

1. **Default:** show the clock. Time is synced from NTP/SNTP and the time source is refreshed every `1h`. Before NTP is valid, the display shows `--:--`.
2. **Screen message from Home Assistant:** show the message for `10 seconds` by default, then return to the clock. The duration is configurable with `Screen Message Seconds`. Sent via the `esphome.esp32_smart_clock_show_message` action or by writing the `Screen Message` text entity.
3. **Indoor sensors:** every `30 seconds` by default, show temperature and humidity for `3 seconds` by default. Both values are configurable from Home Assistant. The matrix uses a fixed non-scrolling layout like `24°C 57%`; if data is missing, it shows `00°C 00%`. Barometric pressure is still exposed to Home Assistant, but it is not shown on the LED matrix.
4. **Music / TTS:** while the speaker is active, show a label (`MUSIC` for media playback, `SPEAKER` for TTS/announcements). The label clears immediately on pause / idle / turn-off, and is hard-capped at `10 seconds` by default if no clear event arrives. The cap is configurable with `Media Message Seconds`.
5. **Wi-Fi disconnected:** every `30 seconds` by default, show `NO WIFI` for `3 seconds` by default until Wi-Fi recovers. Both values are configurable from Home Assistant.
6. **Date and day:** at the top of every hour, show day-of-week and date for `3 seconds` by default. The duration is configurable with `Date Message Seconds`.
7. **Invalid or missing data:** if any branch above has bad / `NaN` / not-yet-valid data (NTP not synced, sensor read failed, empty message, etc.), that branch is skipped and the clock is shown instead.

## Display Priority Order

Multiple events can be active at the same time. The display lambda checks branches in this fixed order; the first match wins:

1. `text_message` - Home Assistant message (`Screen Message Seconds`)
2. `media_message` - `MUSIC` / `SPEAKER` (`Media Message Seconds`)
3. `wifi_alert` - `NO WIFI` (`Wi-Fi Alert Seconds`)
4. `date_message` - `Day DD/MM` (`Date Message Seconds`)
5. `sensor_message` - `temp humidity` (`Sensor Message Seconds`)
6. Default clock - `HH:MM:SS`

This is why a Home Assistant message hides a sensor screen, but a sensor screen never hides a message.

## Temporary Screens

| Trigger | Display | Duration | Source in `esphome-smart-clock.yaml` |
|---|---|---:|---|
| `esphome.esp32_smart_clock_show_message` action or `Screen Message` text entity | message text | `Screen Message Seconds` (default 10 s) | sets `text_message_until` in `api.actions.show_message` and `text.set_action` |
| Music playback starts | `MUSIC` | `Media Message Seconds` (default 10 s), cleared on pause/idle/off | `media_player.on_play` sets `media_message_until` |
| TTS / announcement starts | `SPEAKER` | `Media Message Seconds` (default 10 s), cleared on pause/idle/off | `media_player.on_announcement` sets `media_message_until` |
| Music pauses, idles, or turns off | returns to clock | immediately | `on_pause` / `on_idle` / `on_turn_off` clear `media_message_until` |
| Wi-Fi disconnected | `NO WIFI` | `Wi-Fi Alert Seconds` every `Wi-Fi Alert Interval Seconds` | dynamic `interval: 1s` check + `not: wifi.connected` sets `wifi_alert_until` |
| Top of each hour | `Day DD/MM` | `Date Message Seconds` (default 3 s) | `time.on_time` with `seconds: 0, minutes: 0` sets `date_message_until` |
| Indoor sensors | fixed `temp humidity`, for example `24°C 57%`; missing data shows `00°C 00%` | `Sensor Message Seconds` every `Sensor Message Interval Seconds` | dynamic `interval: 1s` check sets `sensor_message_until`; the display uses a fixed non-scrolling pixel layout |
| Alarm time reached | `ALARM` | `Alarm Message Seconds` (default 10 s) | `alarm_triggered` script sets `text_message_until` |
| Invalid / missing data on any branch | clock | immediately | each branch only renders after its own validity check; otherwise control falls through to the clock |

## Rendering And Hardware Notes

Short English/number messages use a custom 3x7 pixel renderer that spreads the text across all 32 columns. Longer supported messages scroll across the full matrix.

Hebrew screen messages use the `Noto Sans Hebrew` font. Short Hebrew messages are spread across the full matrix, and long Hebrew messages scroll from right to left.

Display brightness can be changed from Home Assistant with the `Display Brightness` number entity. `0` is dimmest, `15` is brightest.

Brightness changes are sent directly to the MAX7219 chips at runtime and are also re-applied after boot when the restored Home Assistant value is available.

Temporary display timings can also be changed from Home Assistant. The ESPHome firmware exposes number entities for `Screen Message Seconds`, `Media Message Seconds`, `Alarm Message Seconds`, `Wi-Fi Alert Seconds`, `Wi-Fi Alert Interval Seconds`, `Date Message Seconds`, `Sensor Message Seconds`, and `Sensor Message Interval Seconds`. These values are restored after reboot.

## Song Name Limitation

The ESPHome `media_player: speaker` platform does not surface track-title metadata to the firmware, so the MAX7219 only ever shows the static labels `MUSIC` (for media playback) and `SPEAKER` (for TTS / announcements).

If you want the song title on the matrix, push it from a Home Assistant automation as a screen message:

```yaml
action: esphome.esp32_smart_clock_show_message
data:
  message: "{{ state_attr('media_player.esp32_smart_clock_speaker', 'media_title') }}"
```

That will show for `Screen Message Seconds` and then return to the clock, like any other screen message.

## Reset Behavior

The display returns to the clock immediately when any of these happens:

- `esphome.esp32_smart_clock_clear_message` is called, or `Screen Message` is set to an empty string.
- The media player fires `on_pause`, `on_idle`, or `on_turn_off`.
- A temporary screen's data becomes invalid (`NaN` sensor read, empty message, NTP not yet valid). The matching branch is skipped and control falls through to the clock.
- All temporary timeouts have expired and no event is currently active.

## Hebrew Text

Hebrew is supported for Home Assistant screen messages.

Example:

```yaml
action: esphome.esp32_smart_clock_show_message
data:
  message: "שלום"
```

Limitations:

- The MAX7219 matrix is only 8 pixels high, so Hebrew is readable but small.
- Complex Hebrew shaping, nikud, and mixed Hebrew/English sentence layout are not handled.

## Text Does Not Use All LEDs

For the ESPHome firmware, the default clock and supported English/number messages are drawn across the full 8x32 matrix.

If supported text still appears on only part of the display, check the number of MAX7219 modules:

- Four 8x8 modules: keep `num_chips: 4`.
- One 8x8 module: change `num_chips: 1`.

In `esphome-smart-clock.yaml`:

```yaml
display:
  - platform: max7219digit
    num_chips: 4
```

If the text appears on only part of the display:

- Check DIN, CLK, CS wiring.
- Check that every MAX7219 module has 5V and GND.
- Check module direction. Many 8x32 boards have an input side and output side.
- Try `rotate_chip`, `reverse_enable`, or wiring from the other end if the display is mirrored or shifted.
