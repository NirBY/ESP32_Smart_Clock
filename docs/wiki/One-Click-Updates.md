# One-click firmware updates

The **ESP32 Smart Clock Updates** integration adds a native **Personalized
firmware** update entity to Home Assistant. Open it from Settings → Updates or
the notification's **Review and install** link, then choose **Install**.

The installer downloads the selected release's source, compiles it in your
ESPHome Device Builder with your saved credentials and overrides, and uploads
over Wi-Fi. It waits for the clock to reconnect and report the new version.
Wi-Fi passwords and API encryption keys stay in your local setup; GitHub only
serves public source files. The generic public binary is not used.

## One-time setup

1. Run the current **ESPHome Device Builder** on your Home Assistant host,
   another computer, or a server. Home Assistant OS users can use the ESPHome
   app. Home Assistant Container users need a separate builder. The builder
   must support the modern `/ws` API, `devices/update_config` with `expected`,
   and the `firmware/install` job API. Legacy dashboards are not supported.
   A pinned [Docker/Synology setup](../../deployment/esphome-builder/README.md)
   is included for users without a builder.
2. In the builder, create your clock YAML from [examples/clock.yaml](../../examples/clock.yaml).
   Set the **same device name and API encryption key** as your existing clock.
   Keep Wi-Fi, fallback access point and encryption secrets in the builder's
   `secrets.yaml`. Copy any local hardware/display overrides below the package.
   The example `smart_clock_release` substitution is managed by the updater.
3. Validate the configuration in the builder. If migrating an existing clock,
   compare its local YAML carefully: a copied full configuration cannot be
   automatically converted without risking removal of personal customizations.
   The updater refuses unmanaged configurations instead of overwriting them.
4. Install **ESP32 Smart Clock Updates** as a HACS custom repository:
   `https://github.com/NirBY/ESP32_Smart_Clock`, category **Integration**.
   Alternatively, copy `custom_components/esp32_smart_clock` into HA's
   `custom_components` directory. Restart Home Assistant after installation.
5. In **Settings → Devices & services → Add integration**, select
   **ESP32 Smart Clock Updates**. Choose the clock's ESPHome **Firmware Update**
   entity, the builder's own URL (for example `http://your-builder:6052`), its
   clock YAML filename, and builder login if configured. An HA ingress URL is
   not a builder URL. Enable the original Firmware Update entity if disabled.
6. Re-import the [notification blueprint](../blueprints/automation/esp32_smart_clock_auto_update.yaml).
   In your existing automation, select the new **Personalized firmware** entity.
   Keep automatic installation off to decide when to update.

The builder must be reachable from HA and the clock must be reachable from
the builder. Keep the builder on your trusted network; do not expose it
publicly. Use its authenticated HTTPS endpoint when crossing network boundaries.

## What Install does

- Changes only `smart_clock_release` in your managed clock YAML, using a
  compare-and-swap save so concurrent edits cannot be overwritten.
- Validates the resolved project, release, device name and API key against the
  clock already paired with HA before uploading anything.
- Builds on the selected builder (`force_local`), preserving its `secrets.yaml`
  and local overrides. No example credentials replace your credentials.
- Queues upload only after compilation succeeds. HA shows build/upload status.
- Confirms the clock's reported version after restart before declaring success.

Keep the builder online during the update. A failed compile does not flash the
clock. If HA or the network disconnects while a builder job is active, inspect
that job in Device Builder before retrying; the builder manages its own queue.
If upload succeeds but the clock does not return within three minutes, HA
reports that verification failed rather than claiming success.

The native firmware entity still reports the original device version. The
personalized updater and notification blueprint handle old strings such as
`0.1.0-beta.15-dev.3` correctly when comparing them with published beta versions.

## Existing notification-only installations

Re-importing the blueprint fixes notifications immediately. It does **not**
install the new integration, create a builder, migrate your YAML, or flash the
clock. Complete the one-time setup above to enable the Install control.
Each clock can use its own builder YAML and local overrides.
