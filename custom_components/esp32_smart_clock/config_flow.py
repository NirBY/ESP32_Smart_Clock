"""Pair a clock with its local ESPHome Device Builder configuration."""
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er, selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .builder import Builder, BuilderError, pin_release
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                entity = er.async_get(self.hass).async_get(user_input['source_entity'])
                if not entity or entity.platform != 'esphome':
                    raise BuilderError('Select the clock Firmware Update entity from ESPHome')
                source = self.hass.config_entries.async_get_entry(entity.config_entry_id)
                device = source.runtime_data.device_info
                if not device or device.project_name != 'nirby.esp32_smart_clock':
                    raise BuilderError('The selected entity does not belong to a Smart Clock')
                async with Builder(async_get_clientsession(self.hass), user_input['builder_url'], user_input.get('username', ''), user_input.get('password', '')) as builder:
                    config = await builder.call('devices/get_config', configuration=user_input['configuration'])
                    pin_release(config, '0.1.0-beta.19')  # Validate format without changing it.
                await self.async_set_unique_id(device.mac_address.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=device.friendly_name or device.name, data={**user_input, 'esphome_entry_id': source.entry_id})
            except (BuilderError, aiohttp.ClientError, TimeoutError, ValueError, AttributeError):
                errors['base'] = 'cannot_connect'
        schema = vol.Schema({
            vol.Required('source_entity'): selector.EntitySelector(selector.EntitySelectorConfig(domain='update', integration='esphome')),
            vol.Required('builder_url'): str,
            vol.Required('configuration'): str,
            vol.Optional('username', default=''): str,
            vol.Optional('password', default=''): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
        })
        return self.async_show_form(step_id='user', data_schema=schema, errors=errors)
