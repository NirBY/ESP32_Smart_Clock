/* Load as a Home Assistant dashboard JavaScript module. No dependencies. */
class SmartClockBrightnessCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error('Brightness schedule entity is required');
    this.config = config;
    if (!this.shadowRoot) this.attachShadow({mode: 'open'});
    this.rows = [];
    this.dirty = false;
    this.source = undefined;
    this.render();
  }
  set hass(hass) {
    this._hass = hass;
    if (!this.config) return;
    const state = hass.states[this.config.entity];
    this.available = !!state && !['unknown', 'unavailable'].includes(state.state);
    if (this.pending !== undefined && this.available) {
      if (state.state !== this.pending) return;
      clearTimeout(this.saveTimer);
      this.pending = undefined;
      this.dirty = false;
      this.source = undefined;
    }
    if (this.available && state.state !== this.source) {
      if (!this.dirty) {
        this.rows = this.parse(state.state);
        this.source = state.state;
        this.render();
      } else if (state.state !== this.source) {
        this.message('The schedule changed elsewhere. Reload before saving.');
      }
    }
    const save = this.shadowRoot.querySelector('[data-save]');
    if (save) save.disabled = !this.available || this.saving;
    if (!this.available) this.message('Clock unavailable. Editing is kept; saving requires a connection.');
  }
  parse(value) {
    if (!value) return [];
    return value.split(';').map(part => {
      const match = /^(\d{2}:\d{2})-(\d{2}:\d{2})=(\d{1,2})$/.exec(part);
      if (!match) throw new Error('Invalid schedule received from clock');
      return {start: match[1], end: match[2], level: Number(match[3])};
    });
  }
  serialize() {
    const time = /^(?:[01]\d|2[0-3]):[0-5]\d$/;
    for (const row of this.rows) {
      if (!time.test(row.start) || !time.test(row.end)) throw new Error('Choose a start and end time for every range.');
      if (row.start === row.end) throw new Error('Start and end must be different.');
      if (!Number.isInteger(row.level) || row.level < 0 || row.level > 15) throw new Error('Brightness must be 0–15.');
    }
    const value = this.rows.map(r => `${r.start}-${r.end}=${r.level}`).join(';');
    if (value.length > 254) throw new Error('The clock schedule is full. Remove a range before adding another.');
    return value;
  }
  message(text) { this.shadowRoot.querySelector('[role="status"]').textContent = text; }
  async save() {
    try {
      if (!this.available || this.saving) return;
      if (this._hass.states[this.config.entity].state !== this.source) throw new Error('The schedule changed elsewhere. Reload before saving.');
      const value = this.serialize();
      this.pending = value;
      this.saving = true;
      this.shadowRoot.querySelectorAll('input, button').forEach(el => { el.disabled = true; });
      this.shadowRoot.querySelector('[data-save]').disabled = true;
      await this._hass.callService('text', 'set_value', {entity_id: this.config.entity, value});
      if (this.pending !== undefined) {
        this.message('Waiting for clock confirmation…');
        this.saveTimer = setTimeout(() => {
          this.pending = undefined;
          this.shadowRoot.querySelectorAll('input, button').forEach(el => { el.disabled = false; });
          this.message('No confirmation from clock. Reload to check, or retry saving.');
          this.shadowRoot.querySelector('[data-save]').disabled = !this.available;
        }, 10000);
      } else this.message('Schedule saved.');
    } catch (error) { this.pending = undefined; this.message(error.message || 'Could not save. Try again.'); }
    finally {
      this.saving = false;
      this.shadowRoot.querySelectorAll('input, button').forEach(el => { el.disabled = this.pending !== undefined; });
      this.shadowRoot.querySelector('[data-save]').disabled = !this.available || this.pending !== undefined;
    }
  }
  render() {
    this.shadowRoot.innerHTML = `
      <style>
        ha-card {padding:20px; color:var(--primary-text-color)}
        h2 {font-size:20px;margin:0 0 8px} p {color:var(--secondary-text-color);line-height:1.5}
        .row {display:flex;flex-wrap:wrap;align-items:end;gap:12px;padding:14px 0;border-bottom:1px solid var(--divider-color)}
        label {display:flex;flex-direction:column;gap:6px;font-size:14px}
        input {font:inherit;padding:8px;border:1px solid var(--divider-color);border-radius:8px;background:var(--card-background-color);color:inherit;color-scheme:light dark}
        input[type=number] {width:65px} button {font:inherit;cursor:pointer;padding:9px 14px;border:1px solid var(--divider-color);border-radius:8px;background:var(--card-background-color);color:var(--primary-color)}
        button:disabled {opacity:.5;cursor:default} .actions {display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
        [role=status] {min-height:1.5em;margin-bottom:0} .remove {color:var(--error-color)}
      </style>
      <ha-card><h2>Day / night brightness</h2>
        <p>Choose daily time ranges and brightness (0–15). Ranges can cross midnight. The last matching range wins.</p>
        <div class="ranges"></div>
        <div class="actions"><button data-add>Add range</button><button data-save>Save</button><button data-reload>Reload</button></div>
        <p role="status" aria-live="polite"></p>
      </ha-card>`;
    const container = this.shadowRoot.querySelector('.ranges');
    this.rows.forEach((row, index) => {
      const element = document.createElement('div');
      element.className = 'row';
      for (const [key, caption, type] of [['start', 'From', 'time'], ['end', 'Until', 'time'], ['level', 'Brightness', 'number']]) {
        const label = document.createElement('label');
        label.textContent = `${index + 1}. ${caption}`;
        const input = document.createElement('input');
        input.type = type;
        input.value = row[key];
        input.required = true;
        if (type === 'time') input.step = '60';
        else {input.min = '0'; input.max = '15'; input.step = '1';}
        input.addEventListener('input', () => {
          row[key] = type === 'number' ? (input.value === '' ? NaN : Number(input.value)) : input.value;
          this.dirty = true;
          this.message('Unsaved changes');
        });
        label.append(input);
        element.append(label);
      }
      const remove = document.createElement('button');
      remove.textContent = 'Remove';
      remove.className = 'remove';
      remove.setAttribute('aria-label', `Remove range ${index + 1}`);
      remove.onclick = () => {this.rows.splice(index, 1); this.dirty = true; this.render(); this.message('Unsaved changes');};
      element.append(remove);
      container.append(element);
    });
    this.shadowRoot.querySelector('[data-add]').onclick = () => {
      this.rows.push({start: '07:00', end: '22:00', level: 3});
      this.dirty = true;
      this.render();
      this.message('Unsaved changes');
    };
    this.shadowRoot.querySelector('[data-save]').disabled = !this.available || this.saving;
    this.shadowRoot.querySelector('[data-save]').onclick = () => this.save();
    this.shadowRoot.querySelector('[data-reload]').onclick = () => {
      this.dirty = false;
      this.source = undefined;
      if (this._hass) this.hass = this._hass;
    };
  }
  getCardSize() { return 3 + this.rows.length; }
}
customElements.define('smart-clock-brightness-card', SmartClockBrightnessCard);
window.customCards = window.customCards || [];
window.customCards.push({type: 'smart-clock-brightness-card', name: 'Smart Clock Brightness', description: 'Daily brightness ranges with time pickers'});
