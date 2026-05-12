// LocalStorage helpers — favorites, notes, viewing schedule, contact log
window.STORE = {
  K_FAV: 'apt_hunt_favorites_v1',
  K_NOTES: 'apt_hunt_notes_v1',
  K_CALLED: 'apt_hunt_called_v1',
  K_TOURED: 'apt_hunt_toured_v1',
  K_TIMELINE_DONE: 'apt_hunt_timeline_done_v1',

  _get(k, def) { try { return JSON.parse(localStorage.getItem(k)) ?? def; } catch { return def; } },
  _set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },

  favorites() { return this._get(this.K_FAV, []); },
  toggleFavorite(id) {
    const f = this.favorites();
    const i = f.indexOf(id);
    if (i >= 0) f.splice(i, 1); else f.push(id);
    this._set(this.K_FAV, f);
    return f;
  },
  isFavorite(id) { return this.favorites().includes(id); },

  notes() { return this._get(this.K_NOTES, {}); },
  getNote(id) { return this.notes()[id] || ''; },
  setNote(id, text) {
    const n = this.notes();
    if (text) n[id] = text; else delete n[id];
    this._set(this.K_NOTES, n);
  },

  called() { return this._get(this.K_CALLED, {}); },
  markCalled(id) {
    const c = this.called();
    c[id] = new Date().toISOString();
    this._set(this.K_CALLED, c);
  },

  toured() { return this._get(this.K_TOURED, {}); },
  markToured(id) {
    const t = this.toured();
    t[id] = new Date().toISOString();
    this._set(this.K_TOURED, t);
  },

  timelineDone() { return this._get(this.K_TIMELINE_DONE, {}); },
  toggleTimelineItem(itemId) {
    const t = this.timelineDone();
    if (t[itemId]) delete t[itemId]; else t[itemId] = new Date().toISOString();
    this._set(this.K_TIMELINE_DONE, t);
    return t;
  },
  isTimelineDone(itemId) { return !!this.timelineDone()[itemId]; },

  exportAll() {
    return {
      favorites: this.favorites(),
      notes: this.notes(),
      called: this.called(),
      toured: this.toured(),
      timeline_done: this.timelineDone(),
      exported_at: new Date().toISOString()
    };
  }
};
