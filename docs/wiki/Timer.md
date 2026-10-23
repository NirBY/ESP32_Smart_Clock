# Local countdown timer (beta.15 development build)

Home Assistant shows a separate **ESP32 Smart Clock Timer** device under the
clock's connected devices. Its controls are:

| Control | Behavior |
|---|---|
| Timer Minutes | Duration for the Start Timer button, 1–1440 minutes |
| Start Timer | Starts a new countdown, replacing any previous countdown |
| Pause Timer / Resume Timer | Freeze and continue the remaining time |
| Cancel Timer | Stop and clear the countdown |
| Timer Remaining | Remaining seconds, rounded up |
| Timer State | idle, running, paused, or finished |
| Timer Display Seconds | Countdown page duration, 1–120 seconds; default 10 |
| Clock Display Seconds | Clock page duration, 0–30 seconds; default 2; 0 disables rotation |

The display slides between the countdown and the clock. The final 60 seconds
stay on the countdown. Below one hour it uses large MM:SS digits; at one hour
or longer it uses HH:MM:SS. A bottom-left dot identifies the timer page; two
dots indicate pause. Explicit messages and system alerts have higher priority.
Periodic date and sensor pages wait until the timer is inactive.

On completion the clock shows DONE for 10 seconds, plays a local three-tone chime, and
emits `esphome.timer_finished` for connected Home Assistant automations.
The countdown runs locally without HA or Internet. It does not survive a reboot;
duration/display preferences are restored, but an interrupted countdown returns
to idle. The completion event is not replayed if HA was disconnected.

For precise durations, call the HA action:

```yaml
action: esphome.esp32_smart_clock_start_timer
data:
  seconds: 90
```

Valid durations are 1–86400 seconds. The matching actions are `pause_timer`,
`resume_timer`, and `cancel_timer` with no parameters. Choose the actions from
HA's picker if the integration's action names have been customized.

This is the clock's local timer; starting an unrelated HA `timer` helper does
not automatically synchronize it. Use the clock's timer controls/actions.

The completion chime is a dedicated 2.2-second WAV (16 kHz mono), separate
from the short volume-feedback beep. It uses the speaker's current volume and
mute settings.
