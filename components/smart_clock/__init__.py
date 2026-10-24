"""Headers shared by the remote Smart Clock package."""
import esphome.codegen as cg
import esphome.config_validation as cv

CONFIG_SCHEMA = cv.Schema({})

async def to_code(config):
    # Run after generated global declarations: helper headers reference ESPHome types.
    for name in ('audio_startup', 'system_health', 'clock_timer', 'alarm_schedule'):
        cg.add_global(cg.RawStatement(f'#include "esphome/components/smart_clock/{name}.h"'))
