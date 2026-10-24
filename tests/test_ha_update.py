"""Run inside the official Home Assistant container to verify native integration APIs."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
from homeassistant.core import State
from homeassistant.components.update import UpdateEntityFeature
from custom_components.esp32_smart_clock.update import ClockUpdate
from custom_components.esp32_smart_clock.config_flow import ConfigFlow

class NativeEntity(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hass = MagicMock()
        self.entry = SimpleNamespace(unique_id='aa:bb:cc:dd:ee:ff', data={'source_entity': 'update.clock'})
        self.entity = ClockUpdate(self.hass, self.entry)
        self.state = State('update.clock', 'off', {'installed_version': '0.1.0-beta.15-dev.3', 'latest_version': '0.1.0-beta.19'})
        self.hass.states.get.return_value = self.state

    def test_native_install_and_version_comparison(self):
        self.assertTrue(self.entity.supported_features & UpdateEntityFeature.INSTALL)
        self.assertTrue(self.entity.version_is_newer(self.entity.latest_version, self.entity.installed_version))
        self.assertFalse(self.entity.version_is_newer('0.1.0-beta.19', '0.1.0-beta.20-dev.1'))
        self.assertTrue(self.entity.version_is_newer('0.1.0-beta.19', '0.1.0-beta.19-dev.1'))
        self.assertFalse(self.entity.version_is_newer('0.1.0-beta.19', '0.1.0-beta.19'))

    async def test_config_flow_form_schema(self):
        flow = ConfigFlow()
        flow.hass = self.hass
        flow.async_show_form = MagicMock(return_value={})
        await flow.async_step_user()
        schema = flow.async_show_form.call_args.kwargs['data_schema']
        self.assertTrue(schema)

    def test_offline_not_ready(self):
        self.hass.states.get.return_value = State('update.clock', 'unavailable')
        self.assertFalse(self.entity.available)

if __name__ == '__main__':
    unittest.main()
