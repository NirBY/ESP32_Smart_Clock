"""Native HA Install control: local compile and OTA, never public binaries."""
import asyncio
import re
from awesomeversion import AwesomeVersion
from homeassistant.components.update import UpdateEntity, UpdateEntityFeature, UpdateDeviceClass
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers import entity_registry as er
from .builder import Builder, BuilderError, RELEASE
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ClockUpdate(hass, entry)])

class ClockUpdate(UpdateEntity):
    _attr_has_entity_name = True
    _attr_name = 'Personalized firmware'
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES
    _attr_should_poll = False

    def __init__(self, hass, entry):
        self.hass, self.entry = hass, entry
        self._attr_unique_id = entry.unique_id + '_personalized_firmware'
        self._busy = False
        self._phase = 'Idle'
        self._lock = asyncio.Lock()
        self._source = entry.data['source_entity']

    async def async_added_to_hass(self):
        self.async_on_remove(async_track_state_change_event(self.hass, [self._source], self._changed))
        # Attach to the same logical device as the original firmware update.
        registry = er.async_get(self.hass)
        source = registry.async_get(self._source)
        if source and source.device_id:
            registry.async_update_entity(self.entity_id, device_id=source.device_id)

    @callback
    def _changed(self, event):
        self.async_write_ha_state()

    def _attribute(self, name):
        state = self.hass.states.get(self._source)
        return state.attributes.get(name) if state else None

    @property
    def available(self):
        state = self.hass.states.get(self._source)
        return state is not None and state.state not in ('unknown', 'unavailable')

    @property
    def installed_version(self):
        return self._attribute('installed_version')

    def version_is_newer(self, latest_version, installed_version):
        base = re.sub(r'-dev\.[0-9]+$', '', installed_version)
        return AwesomeVersion(latest_version) > AwesomeVersion(base) or (latest_version == base and base != installed_version)

    @property
    def latest_version(self):
        return self._attribute('latest_version')

    @property
    def release_url(self):
        return self._attribute('release_url')

    @property
    def title(self):
        return 'ESP32 Smart Clock'

    @property
    def in_progress(self):
        return self._busy

    @property
    def extra_state_attributes(self):
        return {'update_phase': self._phase, 'device_installed_version': self._attribute('installed_version')}

    async def async_release_notes(self):
        return 'Build this release locally with your saved Wi-Fi credentials, encryption key and YAML overrides, then install it over Wi-Fi. The clock restarts after upload.'

    async def async_update(self):
        await self.hass.services.async_call('homeassistant', 'update_entity', {'entity_id': self._source}, blocking=True)

    def _progress(self, phase):
        self._phase = phase
        self.async_write_ha_state()

    async def async_install(self, version, backup, **kwargs):
        if self._lock.locked():
            raise HomeAssistantError('A clock update is already running')
        async with self._lock:
            target = self.latest_version
            if not target or not RELEASE.fullmatch(target):
                raise HomeAssistantError('No supported release is available')
            source_entry = self.hass.config_entries.async_get_entry(self.entry.data['esphome_entry_id'])
            device = source_entry.runtime_data.device_info
            self._busy = True
            self._progress('Preparing')
            try:
                data = self.entry.data
                # Serialize builds across entries using the same builder.
                locks = self.hass.data.setdefault(DOMAIN, {})
                lock = locks.setdefault(data['builder_url'].rstrip('/'), asyncio.Lock())
                async with lock:
                    async with Builder(async_get_clientsession(self.hass), data['builder_url'], data.get('username', ''), data.get('password', '')) as builder:
                        await builder.prepare(data['configuration'], target, device.name, source_entry.data.get('noise_psk'))
                        await builder.install(data['configuration'], self._progress)
                self._progress('Waiting for clock')
                async with asyncio.timeout(180):
                    while self._attribute('installed_version') != target:
                        await asyncio.sleep(2)
                self._phase = 'Complete'
            except asyncio.CancelledError:
                self._phase = 'Interrupted; check builder jobs'
                raise
            except Exception as err:
                self._phase = 'Failed; check ESPHome builder'
                message = str(err) if isinstance(err, BuilderError) else 'Update did not complete; check the local ESPHome builder'
                raise HomeAssistantError(message) from None
            finally:
                self._busy = False
                self.async_write_ha_state()
