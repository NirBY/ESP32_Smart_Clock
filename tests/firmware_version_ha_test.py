"""Regression for the HA version comparison that disables the Update button."""
from awesomeversion import AwesomeVersion as Version
import yaml
from pathlib import Path

class Loader(yaml.SafeLoader):
    pass
Loader.add_constructor('!secret', lambda loader, node: loader.construct_scalar(node))
config = yaml.load(Path('esphome-smart-clock.yaml').read_text(encoding='utf8'), Loader=Loader)
current = config['substitutions']['firmware_version']
# Capture the actual upstream parser behavior behind the reported regression.
assert not Version('0.1.0-beta.19') > Version('0.1.0-beta.15-dev.3')
assert Version(current) > Version('0.1.0-beta.18')
assert Version(current) > Version('0.1.0-beta.15')
assert not Version(current) > Version(current)
assert not Version('0.1.0-beta.18') > Version(current)
assert Version('0.1.0') > Version(current)
print('HA firmware version comparisons: 6 cases passed')
