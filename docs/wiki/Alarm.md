# Alarm schedules

The Alarm device in Home Assistant has one configurable alarm. Choose an hour,
minute, and schedule, then turn **Alarm Enabled** on. Existing alarms continue
to use **Every day** until you choose another schedule.

| Schedule | What to select | Example |
| --- | --- | --- |
| Every day | Hour and minute | Every day at 07:30 |
| Weekly | One or more weekday switches | Monday, Wednesday and Friday at 07:30 |
| Monthly | Alarm Day of Month, from 1 to 31 | Day 15 of each month at 09:00 |
| Specific date | Alarm Date using the date picker | 2026-12-25 at 08:00 |

Turn on **Limit Alarm to Date Range** and select **Alarm Start Date** and
**Alarm End Date** to restrict a schedule. Both endpoints are included. For
example, select Weekly, Monday through Friday, and a start/end date for a
holiday work schedule. The range also applies to Specific date if enabled.

**Alarm Schedule Summary** shows the time, enabled state, selected days, and
any date limits, such as `On | 07:30 | Weekly: Mon, Wed, Fri`. It refreshes
within a second. The [example dashboard](../home-assistant-dashboard.yaml)
shows weekday, monthly, and date controls only when relevant. Adjust its
entity IDs to match your installation.

## Scheduling rules

- Weekly schedules need at least one selected weekday.
- Dates must be valid, and the range start must not follow the range end.
  An incomplete or invalid schedule does not trigger; the summary asks you
  to finish setup.
- Months without the selected day are skipped: day 31 does not run in April,
  and day 29 runs in February only in leap years.
- A specific-date alarm runs only on that date. Its Enabled switch stays on,
  so the saved configuration remains visible afterward.
- Settings survive restart. Scheduling uses the clock's configured local
  timezone and requires synchronized time. Missed alarms are not replayed.
- A time skipped by a daylight-saving transition does not run. Repeated local
  times are guarded against a second trigger on the same day while running;
  rebooting clears that duplicate guard.

The existing alarm action is unchanged: it displays `ALARM` and emits
`esphome.alarm_triggered` to Home Assistant. Configure a Home Assistant
automation to play your preferred sound or perform other actions.
