"""Generate bounded Home Assistant script tools for the native HA MCP server."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/home-assistant-mcp'
OUT.mkdir(exist_ok=True)
P = 'esp32_smart_clock_'
def ent(domain, name): return f'{domain}.{P}{name}'
def field(description, selector, required=False):
    return dict(description=description, required=required, selector=selector)
def select(options): return {'select': {'options': options}}
def num(low, high): return {'number': {'min': low, 'max': high, 'mode': 'box'}}
def call(action, entity=None, **data):
    d = {'action': action}
    if entity: d['target'] = {'entity_id': entity}
    if data: d['data'] = data
    return d
def guard(condition, message):
    return {'if': '{{ not (' + condition + ') }}', 'then': [{'stop': message, 'error': True}]}
def result(**values):
    return [{'variables': {'result': values}}, {'stop': 'Clock request completed', 'response_variable': 'result'}]
def script(alias, description, fields, sequence):
    return dict(alias='ESP32 Clock MCP '+alias, description=description, mode='queued', max=10, fields=fields, sequence=sequence)

numbers = {'timer_timer_display_seconds': (1,120), 'timer_clock_display_seconds': (0,30),
 'timer_timer_minutes': (1,1440), 'display_brightness': (0,15), 'system_alert_seconds': (1,30),
 'system_alert_interval_seconds': (3,300), 'screen_message_seconds': (1,60), 'media_message_seconds': (1,60),
 'audio_hourly_beep_quiet_start_hour': (0,23), 'audio_hourly_beep_quiet_end_hour': (0,23),
 'alarm_message_seconds': (1,60), 'wi_fi_alert_seconds': (1,30), 'wi_fi_alert_interval_seconds': (5,300),
 'date_message_seconds': (1,30), 'sensor_message_seconds': (1,30), 'sensor_message_interval_seconds': (5,300),
 'alarm_hour': (0,23), 'alarm_minute': (0,59)}
switches = ['show_system_alerts','speaker_connected','audio_hourly_beep_enabled','audio_hourly_beep_quiet_hours_enabled','alarm_enabled']
entities = [ent('number',n) for n in numbers] + [ent('switch',n) for n in switches] + [ent('sensor',n) for n in ['temperature','humidity','pressure','bmp280_temperature','timer_timer_remaining','timer_timer_state']] + [ent('select','time_format'), ent('text','screen_message'), ent('media_player','speaker'), ent('media_player','audio_speaker'), ent('update','system_firmware_update')]
scripts = {}
scripts['esp32_clock_mcp_status'] = script('Status', 'Read clock temperature, humidity, pressure, countdown, alarm, display settings, speaker and firmware state. No changes. Unknown/unavailable values are not measurements.', {}, [
 {'variables': {'clock_entities': entities}},
 {'variables': {'result': "{% set ns=namespace(items=[]) %}{% for e in clock_entities %}{% set ns.items=ns.items+[dict(entity_id=e,state=states(e),unit=state_attr(e,'unit_of_measurement'),volume=state_attr(e,'volume_level'),muted=state_attr(e,'is_volume_muted'),installed_version=state_attr(e,'installed_version'),latest_version=state_attr(e,'latest_version'))] %}{% endfor %}{{ dict(entities=ns.items) }}"}},
 {'stop':'Clock state snapshot','response_variable':'result'}])

choices=[]
for n,(lo,hi) in numbers.items():
    step=5 if n in ['wi_fi_alert_interval_seconds','sensor_message_interval_seconds'] else 1
    choices.append({'conditions': "{{ setting == '"+n+"' }}", 'sequence':[
      guard(f"is_number(value) and {lo} <= value|float <= {hi} and (value|float - {lo}) % {step} == 0",f'Value must be {lo}..{hi} in steps of {step}'),
      call('number.set_value',ent('number',n),value='{{ value | float }}')]})
for n in switches:
    choices.append({'conditions': "{{ setting == '"+n+"' }}",'sequence':[
      guard("value|string|lower in ['on','off']",'Use on or off'),
      call("{{ 'switch.turn_on' if value|string|lower == 'on' else 'switch.turn_off' }}",ent('switch',n))]})
choices.append({'conditions':"{{ setting == 'time_format' }}",'sequence':[guard("value in ['HH:MM','HH:MM:SS']",'Unsupported time format'),call('select.select_option',ent('select','time_format'),option='{{ value }}')]})
scripts['esp32_clock_mcp_setting']=script('Setting','Change one clock setting: brightness, countdown/clock rotation seconds, time format, screen durations, hourly beep/quiet hours, speaker enabled or alarm settings. Read Status for current values. Clock rotation 0 means countdown only.',{'setting':field('Clock setting to change.',select(list(numbers)+switches+['time_format']),True),'value':field('Numeric value as text, on/off for switches, or HH:MM / HH:MM:SS for time format.',{'text':{}},True)},[
 guard('setting is defined and value is defined','setting and value are required'),
 {'choose':choices,'default':[{'stop':'Unknown clock setting','error':True}]}]+result(setting='{{ setting }}',requested_value='{{ value }}',status='command_sent'))

scripts['esp32_clock_mcp_timer']=script('Timer','Start, pause, resume or cancel the physical clock countdown. Start replaces any current countdown. It runs locally, shows remaining time, and plays a six-second melody on completion unless muted. Convert minutes to seconds.',{'operation':field('start, pause, resume or cancel.',select(['start','pause','resume','cancel']),True),'seconds':field('Required for start only. Whole seconds from 1 to 86400.',num(1,86400))},[
 guard("operation is defined and operation in ['start','pause','resume','cancel']",'Invalid operation'),
 {'choose':[{'conditions':"{{ operation == 'start' }}",'sequence':[guard('seconds is defined and is_number(seconds) and 1 <= seconds|float <= 86400 and seconds|float == seconds|int','Start requires whole seconds 1..86400'),call('esphome.esp32_smart_clock_start_timer',seconds='{{ seconds | int }}')]}], 'default':[call('button.press',"{{ 'button.esp32_smart_clock_timer_' + operation + '_timer' }}")]}]+result(operation='{{ operation }}',status='command_sent'))

scripts['esp32_clock_mcp_alarm']=script('Alarm','Set the clock daily alarm in local clock time (24-hour hour/minute), enable it or disable it. This is a repeating daily alarm, not a dated calendar reminder. Only enable after hour and minute are set.',{'operation':field('set sets time and enables; enable/disable preserve the saved time.',select(['set','enable','disable']),True),'hour':field('24-hour hour, required for set.',num(0,23)),'minute':field('Minute, required for set.',num(0,59))},[
 guard("operation is defined and operation in ['set','enable','disable']",'Invalid operation'),
 {'if':"{{ operation == 'set' }}",'then':[guard('hour is defined and minute is defined and is_number(hour) and is_number(minute) and 0 <= hour|float <= 23 and 0 <= minute|float <= 59 and hour|float == hour|int and minute|float == minute|int','Hour/minute must be whole numbers in range'),call('switch.turn_off',ent('switch','alarm_enabled')),call('number.set_value',ent('number','alarm_hour'),value='{{ hour|int }}'),call('number.set_value',ent('number','alarm_minute'),value='{{ minute|int }}')]},
 call("{{ 'switch.turn_off' if operation == 'disable' else 'switch.turn_on' }}",ent('switch','alarm_enabled'))]+result(operation='{{ operation }}',status='command_sent'))

scripts['esp32_clock_mcp_message']=script('Message','Show a scrolling message on the clock, or clear it with empty text. Use supported Latin characters/emojis; Hebrew rendering is not guaranteed. Message overrides timer temporarily. Duration is configured by screen_message_seconds.',{'message':field('Text, at most 100 characters. Empty text clears the display message.',{'text':{}},True)},[guard('message is defined and message is string and message|length <= 100','message must be a string of at most 100 characters'),call('text.set_value',ent('text','screen_message'),value='{{ message }}')]+result(status='command_sent'))

audio_ops=['play','pause','resume','stop','next','previous','volume','mute','unmute']
audio_choices=[]
for op,service in [('pause','media_pause'),('resume','media_play'),('stop','media_stop'),('next','media_next_track'),('previous','media_previous_track')]:
 audio_choices.append({'conditions':"{{ operation == '"+op+"' }}",'sequence':[call('media_player.'+service,ent('media_player','audio_speaker'))]})
audio_choices += [
 {'conditions':"{{ operation == 'play' }}",'sequence':[guard('query is defined and query is string and query|trim|length > 0','Provide a song/artist/album/playlist name or URI'),guard("media_type|default('track') in ['track','artist','album','playlist','radio']",'Invalid media type'),call('music_assistant.play_media',ent('media_player','audio_speaker'),media_id='{{ query }}',media_type="{{ media_type|default('track') }}",enqueue='play')]},
 {'conditions':"{{ operation == 'volume' }}",'sequence':[guard('volume is defined and is_number(volume) and 0 <= volume|float <= 100','volume must be 0..100'),call('media_player.volume_set',ent('media_player','speaker'),volume_level='{{ volume|float / 100 }}')]},
 {'conditions':"{{ operation in ['mute','unmute'] }}",'sequence':[call('media_player.volume_mute',ent('media_player','speaker'),is_volume_muted="{{ operation == 'mute' }}")]}]
scripts['esp32_clock_mcp_music']=script('Music','Play music on the clock through Music Assistant by song, artist, album, playlist or radio name/URI; pause, resume, stop, next/previous, set volume or mute. Requires Music Assistant and a configured music provider. Playback commands do not guarantee an audible result.',{'operation':field('Music operation.',select(audio_ops),True),'query':field('Name or provider URI for play. Include the artist in a song query to disambiguate.',{'text':{}}),'media_type':field('Type of query for play; defaults to track.',select(['track','artist','album','playlist','radio'])),'volume':field('Percent 0..100 for volume; does not automatically unmute.',num(0,100))},[guard('operation is defined','operation required'),{'choose':audio_choices,'default':[{'stop':'Invalid audio operation','error':True}]}]+result(operation='{{ operation }}',status='command_sent'))

package={'script':scripts}
(OUT/'package.yaml').write_text(yaml.safe_dump(package,sort_keys=False,allow_unicode=True,width=110),encoding='utf-8')
for name, data in scripts.items():
 (OUT/(name+'.yaml')).write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True,width=110),encoding='utf-8')
print(f'Generated {len(scripts)} scoped MCP script tools')
