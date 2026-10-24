"""Exercise the actual HA blueprint condition with HA-compatible version parsing."""
import re
from pathlib import Path
import yaml
from jinja2 import Environment
from awesomeversion import AwesomeVersion

class Loader(yaml.SafeLoader):
    pass
Loader.add_constructor('!input', lambda loader, node: loader.construct_scalar(node))
env = Environment()
env.filters['regex_replace'] = lambda value, pattern, replacement: re.sub(pattern, replacement, value)
env.tests['match'] = lambda value, pattern: re.match(pattern, value) is not None
env.globals['version'] = AwesomeVersion
cases = [
    ('0.1.0-beta.15-dev.3', '0.1.0-beta.18', 'off', True),
    ('0.1.0-beta.18-dev.3', '0.1.0-beta.18', 'off', True),
    ('0.1.0-beta.18', '0.1.0-beta.18', 'off', False),
    ('0.1.0-beta.19-dev.1', '0.1.0-beta.18', 'off', False),
    ('0.1.0-beta.9', '0.1.0-beta.18', 'off', True),
    ('0.1.0', '0.1.0-beta.18', 'off', False),
    ('0.1.0-beta.18', '0.1.0', 'off', True),
    ('', '', 'off', False),
    (None, None, 'unavailable', False),
    ('custom-old', 'custom-new', 'on', True),
    ('0.1.0-beta.15', '0.1.0-beta.18', 'unavailable', False),
]
for path in ['docs/blueprints/automation/esp32_smart_clock_auto_update.yaml',
             'docs/home-assistant-auto-update.yaml']:
    data = yaml.load(Path(path).read_text(), Loader=Loader)
    actions = data.get('actions', data.get('action'))
    template = env.from_string(next(a['value_template'] for a in actions if a.get('condition') == 'template'))
    for installed, latest, state, expected in cases:
        attrs = dict(installed_version=installed, latest_version=latest)
        actual = template.render(firmware_entity='update.clock',
                                 state_attr=lambda entity, key: attrs.get(key),
                                 states=lambda entity: state,
                                 is_state=lambda entity, value: state == value).strip()
        assert actual == str(expected), (path, installed, latest, state, actual)
print('Update notification: 22 cases passed')
