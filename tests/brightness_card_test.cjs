const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
let Card;
const context = {HTMLElement: class {}, window: {}, customElements: {define: (_, c) => {Card = c;}}, setTimeout, clearTimeout};
vm.runInNewContext(fs.readFileSync('docs/home-assistant/smart-clock-brightness-card.js', 'utf8'), context);
function card(value = '07:00-22:00=3;22:00-07:00=0') {
  const c = new Card();
  c.config = {entity: 'text.clock'};
  c.rows = c.parse(value);
  c.source = value;
  c.available = true;
  c.shadowRoot = {querySelector: () => ({}), querySelectorAll: () => []};
  c.message = text => {c.status = text;};
  c.render = () => {};
  return c;
}
(async () => {
  const c = card();
  assert.equal(c.serialize(), c.source);
  c.rows.pop(); // dynamic removal
  assert.equal(c.serialize(), '07:00-22:00=3');
  c.rows.push({start: '23:00', end: '05:30', level: 15});
  assert.equal(c.serialize(), '07:00-22:00=3;23:00-05:30=15');
  c.rows[1].end = '23:00';
  assert.throws(() => c.serialize(), /different/);
  c.rows[1].end = '24:00';
  assert.throws(() => c.serialize(), /Choose/);
  c.rows[1].end = '05:30'; c.rows[1].level = NaN;
  assert.throws(() => c.serialize(), /0–15/);
  c.rows = [];
  assert.equal(c.serialize(), '');
  c.rows = Array(20).fill({start: '07:00', end: '22:00', level: 15});
  assert.throws(() => c.serialize(), /full/);
  c.rows = c.parse('08:00-20:00=4'); c.dirty = true;
  let sent;
  c._hass = {states: {'text.clock': {state: c.source}}, callService: async (...args) => {sent = args;}};
  await c.save();
  assert.equal(sent[0], 'text');
  assert.equal(sent[2].value, '08:00-20:00=4');
  assert.equal(c.dirty, true); // retain draft until actual device state confirms
  c.hass = {...c._hass, states: {'text.clock': {state: sent[2].value}}};
  assert.equal(c.pending, undefined);
  assert.equal(c.dirty, false);
  const failed = card(); failed.dirty = true;
  failed._hass = {states: {'text.clock': {state: failed.source}}, callService: async () => {throw Error('offline');}};
  await failed.save();
  assert.equal(failed.dirty, true);
  assert.equal(failed.pending, undefined);
  assert.equal(failed.status, 'offline');
  failed._hass.states['text.clock'].state = '';
  await failed.save();
  assert.match(failed.status, /changed elsewhere/);
  console.log('Brightness card validation, dynamic rows, save acknowledgement, conflict and failure tests passed.');
})().catch(error => {console.error(error); process.exitCode = 1;});
