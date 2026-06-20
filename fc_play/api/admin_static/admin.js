/* ===========================================================================
   Claude Free Play · Gateway Console — Controller
   Single theme: warm amber on obsidian
   =========================================================================== */

// ── State ─────────────────────────────────────────────────────────────────
const S = { config: null, dirty: new Map(), origValues: new Map(), view: 'dashboard' };
const MASKED = '********';
const M = '•'.repeat(8); // fallback masked display

// ── DOM ───────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const $$ = s => document.querySelectorAll(s);

function toast(msg, type = 'info') {
  const b = $('toastBox');
  const t = document.createElement('div');
  t.className = `toast ${type === 'success' ? 'good' : type === 'error' ? 'bad' : 'info'}`;
  t.textContent = msg;
  b.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

// ── API ───────────────────────────────────────────────────────────────────
async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { 'Content-Type': 'application/json', ...opts.headers }, ...opts });
  if (!r.ok) {
    const e = await r.json().catch(() => ({ error: r.statusText }));
    throw new Error(e.error || e.detail || r.statusText);
  }
  return r.json();
}

// ── Views ─────────────────────────────────────────────────────────────────
const VIEWS = [
  { id: 'dashboard', label: 'Dashboard', title: 'Dashboard' },
  { id: 'providers', label: 'Providers', title: 'Provider Configuration' },
  { id: 'models',    label: 'Models',    title: 'Model Routing' },
  { id: 'settings',  label: 'Settings',  title: 'Settings' },
];

function renderNav() {
  $('topNav').innerHTML = VIEWS.map((v, i) =>
    `<button class="tab ${i===0?'active':''}" data-view="${v.id}" onclick="switchView('${v.id}')">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:5px">
        ${v.id === 'dashboard' ? '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>' : ''}
        ${v.id === 'providers' ? '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>' : ''}
        ${v.id === 'models' ? '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>' : ''}
        ${v.id === 'settings' ? '<circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>' : ''}
      </svg>
      ${v.label}
    </button>`
  ).join('');
}

function switchView(id) {
  S.view = id;
  $$('.tab').forEach(e => e.classList.toggle('active', e.dataset.view === id));
  $$('.view-pane').forEach(e => e.classList.toggle('active', e.id === `pane-${id}`));
  const v = VIEWS.find(x => x.id === id);
  if (v) $('pageTitle').textContent = v.title;
}

// ── Dashboard ──────────────────────────────────────────────────────────────
function renderDashboard(fields, provStatus) {
  const pane = document.createElement('div');
  pane.id = 'pane-dashboard';
  pane.className = 'view-pane active';

  const allOk = Object.values(provStatus||{}).filter(p => p.status === 'on').length;
  const allTotal = Object.keys(provStatus||{}).length;

  pane.innerHTML = `
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon green">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
        </div>
        <div><span class="stat-num">${allOk}/${allTotal}</span><span class="stat-lbl">Connected Providers</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon amber">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        </div>
        <div><span class="stat-num" id="statModels">${Object.keys(provStatus||{}).length}</span><span class="stat-lbl">Available Models</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 3v18"/></svg>
        </div>
        <div><span class="stat-num">0</span><span class="stat-lbl">Active Requests</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon neutral">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div><span class="stat-num" id="uptimeVal">0s</span><span class="stat-lbl">Uptime</span></div>
      </div>
    </div>
    <div class="section">
      <div class="section-head"><h2>Connected Providers</h2><span class="section-tag">Status</span></div>
      <div class="prov-grid" id="dashProvGrid"></div>
    </div>
    <div class="section">
      <div class="section-head"><h2>Recent Activity</h2><span class="section-tag">Log</span></div>
      <div class="log-panel"><div class="log-empty">No activity yet. Start using the gateway.</div></div>
    </div>
  `;

  $('viewContainer').appendChild(pane);

  const pg = $('dashProvGrid');
  pg.innerHTML = Object.entries(provStatus||{}).map(([id, p]) => {
    const keysHtml = (p.keys||[]).map(k =>
      `<span class="key-chip ${k.has_value?'on':'off'}" title="${k.masked}">K${k.index}</span>`
    ).join('');
    return `<div class="prov-card" onclick="switchView('providers')" style="cursor:pointer">
        <div class="prov-card-top">
          <span class="prov-name">${p.label||id}</span>
          <span class="badge ${p.status}">${p.status === 'on' ? 'Ready' : 'No Key'}</span>
        </div>
        <div class="prov-meta" style="margin-top:5px;display:flex;gap:4px;flex-wrap:wrap">${keysHtml}</div>
      </div>`;
  }).join('');

  let sec = 0;
  setInterval(() => {
    sec++;
    const el = $('uptimeVal');
    if (el) el.textContent = sec < 60 ? `${sec}s` : `${Math.floor(sec/60)}m ${sec%60}s`;
  }, 1000);
}

// ── Providers Pane ────────────────────────────────────────────────────────
function renderProviders(fields, provStatus) {
  const pane = document.createElement('div');
  pane.id = 'pane-providers';
  pane.className = 'view-pane';

  pane.innerHTML = `
    <div class="section">
      <div class="section-head"><h2>All Providers</h2><span class="section-tag">${Object.keys(provStatus||{}).length} total</span></div>
      <div class="prov-grid" id="fullProvGrid"></div>
    </div>
  `;
  $('viewContainer').appendChild(pane);

  const grid = $('fullProvGrid');
  grid.innerHTML = Object.entries(provStatus||{}).map(([id, p]) => {
    const keysHtml = (p.keys||[]).map(k =>
      `<span class="key-chip ${k.has_value?'on':'off'}" title="${k.masked}">K${k.index}</span>`
    ).join('');
    return `<div class="prov-card">
      <div class="prov-card-top">
        <span class="prov-name">${p.label||id}</span>
        <span class="badge ${p.status}">${p.status === 'on' ? 'Ready' : p.status === 'warn' ? 'No Key' : 'Off'}</span>
      </div>
      <div class="prov-meta">${p.key_count || 0} key${(p.key_count||0) !== 1 ? 's' : ''}</div>
      <div class="prov-meta" style="margin-top:5px;display:flex;gap:4px;flex-wrap:wrap">${keysHtml}</div>
    </div>`;
  }).join('');
}

// ── Models Pane ───────────────────────────────────────────────────────────
function renderModels(fields) {
  const pane = document.createElement('div');
  pane.id = 'pane-models';
  pane.className = 'view-pane';

  const modelFields = fields.filter(f => f.section === 'models');
  const thinkFields = fields.filter(f => f.section === 'thinking');

  pane.innerHTML = `
    <div class="section">
      <div class="section-head"><h2>Model Routing</h2><span class="section-tag">Tiers</span></div>
      <div class="cfg-grid">${modelFields.map(f => buildField(f)).join('')}</div>
    </div>
    <div class="section">
      <div class="section-head"><h2>Extended Thinking</h2><span class="section-tag">Per-model</span></div>
      <div class="cfg-grid">${thinkFields.map(f => buildField(f)).join('')}</div>
    </div>
  `;
  $('viewContainer').appendChild(pane);
  restoreOrigValues();
}

// ── Settings Pane ─────────────────────────────────────────────────────────
function renderSettings(fields, sections) {
  const pane = document.createElement('div');
  pane.id = 'pane-settings';
  pane.className = 'view-pane';

  const viewOrder = ['general', 'api', 'providers', 'rate_limiting', 'advanced'];
  let html = '';
  for (const sid of viewOrder) {
    const sec = (sections||[]).find(s => s.id === sid);
    if (!sec) continue;
    const secFields = fields.filter(f => f.section === sid);
    const regular = secFields.filter(f => !f.advanced);
    const advanced = secFields.filter(f => f.advanced);
    if (!regular.length && !advanced.length) continue;

    html += `<div class="cfg-section">
      <div class="cfg-section-title">${sec.label}</div>
      <div class="cfg-grid">${regular.map(f => buildField(f)).join('')}</div>`;
    if (advanced.length) {
      html += `
        <button class="adv-toggle" onclick="this.classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
          <span class="chev">▸</span> Advanced (${advanced.length})
        </button>
        <div class="adv-fields">${advanced.map(f => buildField(f)).join('')}</div>`;
    }
    html += `</div>`;
  }
  pane.innerHTML = html;
  $('viewContainer').appendChild(pane);
  restoreOrigValues();
}

// ── Field Builder ─────────────────────────────────────────────────────────
const MASKED_PLACEHOLDER = 'Configured — enter new value to replace';

function buildField(f) {
  const id = `f-${f.key}`;
  const val = f.value ?? '';
  const display = (f.secret && val) ? '' : val;
  const placeholder = (f.secret && val) ? MASKED_PLACEHOLDER : (f.placeholder || '');
  const desc = f.description ? `<div class="cfg-desc">${f.description}</div>` : '';
  const locked = f.locked ? 'disabled' : '';
  const lockIcon = f.locked ? '<span class="lock-icon" title="Set via environment">🔒</span>' : '';

  let input = '';
  switch (f.type) {
    case 'boolean':
      input = `<input type="checkbox" id="${id}" data-key="${f.key}" data-original="${val}" ${(val==='true'||val===true)?'checked':''} onchange="mark('${f.key}',this)" ${locked}>`;
      break;
    case 'select':
      const opts = ['', ...(f.options||[])].map(o =>
        `<option value="${o}" ${o===val?'selected':''}>${o||'— Select —'}</option>`
      ).join('');
      input = `<select id="${id}" data-key="${f.key}" data-original="${val}" onchange="mark('${f.key}',this)" ${locked}>${opts}</select>`;
      break;
    case 'number':
      input = `<input type="number" id="${id}" data-key="${f.key}" data-original="${val}" value="${display}" onchange="mark('${f.key}',this)" ${locked}>`;
      break;
    default:
      input = `<input type="${f.secret?'password':'text'}" id="${id}" data-key="${f.key}" data-original="${val}" value="${display}" placeholder="${placeholder}" onchange="mark('${f.key}',this)" ${locked}>`;
  }
  return `<div class="cfg-field" data-key="${f.key}"><label class="cfg-label" for="${id}">${f.label}${lockIcon}</label>${input}${desc}</div>`;
}

function restoreOrigValues() {
  $$('.cfg-field input, .cfg-field select').forEach(el => {
    const key = el.dataset.key;
    if (key && S.origValues.has(key)) {
      const orig = S.origValues.get(key);
      el.dataset.original = orig;
    }
  });
}

// ── Dirty Tracking ────────────────────────────────────────────────────────
function getChangedValue(el) {
  if (el.type === 'checkbox') {
    const orig = el.dataset.original === 'true';
    return el.checked !== orig ? String(el.checked) : null;
  }
  const orig = el.dataset.original;
  const current = el.value;
  // Secret field that hasn't been changed — still shows masked placeholder
  if (el.type === 'password' && (!current || current === '') && orig && orig.length > 0) {
    return null; // unchanged secret, send nothing
  }
  if (current === orig) return null;
  return current || '';
}

function mark(key, el) {
  const v = getChangedValue(el);
  if (v === null) S.dirty.delete(key); else S.dirty.set(key, v);
  updateDirty();
}

function updateDirty() {
  const n = S.dirty.size;
  const di = $('dirtyIndicator');
  const btn = $('applyBtn');
  if (n > 0) {
    di.classList.add('dirty');
    di.innerHTML = `<span class="di-dot"></span> ${n} pending`;
    btn.disabled = false;
  } else {
    di.classList.remove('dirty');
    di.innerHTML = `<span class="di-dot"></span> No changes`;
    btn.disabled = true;
  }
}

// ── Actions ───────────────────────────────────────────────────────────────
async function validateConfig() {
  const msg = $('footbarMsg');
  msg.innerHTML = '<span class="spin"></span> Validating...';
  try {
    const changes = Object.fromEntries(S.dirty);
    await api('/admin/api/config/validate', { method: 'POST', body: JSON.stringify(changes) });
    msg.className = 'footbar-center ok';
    msg.textContent = '✓ OK';
    toast('Config valid', 'success');
  } catch (e) {
    msg.className = 'footbar-center err';
    msg.textContent = `✗ ${e.message}`;
    toast(e.message, 'error');
  }
}

async function applyConfig() {
  const msg = $('footbarMsg');
  const btn = $('applyBtn');
  msg.innerHTML = '<span class="spin"></span> Applying...';
  btn.disabled = true;
  try {
    const changes = Object.fromEntries(S.dirty);
    const result = await api('/admin/api/config/apply', { method: 'POST', body: JSON.stringify(changes) });
    msg.className = 'footbar-center ok';
    msg.textContent = '✓ Saved';
    S.dirty.clear();
    updateDirty();
    // Update stored original values from what we just applied
    for (const [key, val] of Object.entries(changes)) {
      S.origValues.set(key, val);
    }
    // Update data-original on fields to match applied state
    $$('.cfg-field input, .cfg-field select').forEach(el => {
      if (el.dataset.key && changes[el.dataset.key] !== undefined) {
        el.dataset.original = changes[el.dataset.key];
      }
    });
    const restart = result.restart_required;
    toast(restart ? 'Applied — restart may be needed' : 'Applied and active', 'success');
  } catch (e) {
    msg.className = 'footbar-center err';
    msg.textContent = `✗ ${e.message}`;
    btn.disabled = false;
    toast(e.message, 'error');
  }
}

// ── Boot ──────────────────────────────────────────────────────────────────
async function load() {
  try {
    const data = await api('/admin/api/config');
    S.config = data;

    const fields = data.fields || [];
    const sections = data.sections || [];
    const provStatus = data.provider_status || {};

    // Store original values
    fields.forEach(f => S.origValues.set(f.key, f.value || ''));

    renderNav();
    $('viewContainer').innerHTML = '';

    renderDashboard(fields, provStatus);
    renderProviders(fields, provStatus);
    renderModels(fields);
    renderSettings(fields, sections);

    updateDirty();
    toast('Console ready', 'info');
  } catch (e) {
    toast('Failed to load: ' + e.message, 'error');
  }
}

document.addEventListener('DOMContentLoaded', load);
