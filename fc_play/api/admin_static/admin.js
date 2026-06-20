/* ===========================================================================
   FC-Play · Gateway Console — Controller
   Top tabs, warm palette, compact layout
   =========================================================================== */

// ── State ─────────────────────────────────────────────────────────────────
const S = { config: null, dirty: new Map(), view: 'dashboard' };
const M = '•'.repeat(8); // masked

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
    `<button class="tab ${i===0?'active':''}" data-view="${v.id}" onclick="switchView('${v.id}')">${v.label}</button>`
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
function renderDashboard(sections, provStatus) {
  const pane = document.createElement('div');
  pane.id = 'pane-dashboard';
  pane.className = 'view-pane active';

  const allOk = Object.values(provStatus||{}).filter(p => p.status === 'on').length;
  const allTotal = Object.keys(provStatus||{}).length;

  pane.innerHTML = `
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon green">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
        </div>
        <div><span class="stat-num">${allOk}/${allTotal}</span><span class="stat-lbl">Connected Providers</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon amber">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        </div>
        <div><span class="stat-num" id="statModels">${Object.keys(provStatus||{}).length}</span><span class="stat-lbl">Available Models</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 3v18"/></svg>
        </div>
        <div><span class="stat-num">0</span><span class="stat-lbl">Active Requests</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon neutral">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
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

  // Render mini provider grid
  const pg = $('dashProvGrid');
  pg.innerHTML = Object.entries(provStatus||{}).map(([id, p]) =>
    `<div class="prov-card">
      <div class="prov-card-top">
        <span class="prov-name">${p.label||id}</span>
        <span class="badge ${p.status}"></span>
      </div>
      <div class="prov-meta">${p.status === 'on' ? 'Connected' : 'No key'}</div>
    </div>`
  ).join('');

  // Uptime
  let sec = 0;
  setInterval(() => {
    sec++;
    $('uptimeVal').textContent = sec < 60 ? `${sec}s` : `${Math.floor(sec/60)}m ${sec%60}s`;
  }, 1000);
}

// ── Providers Pane ────────────────────────────────────────────────────────
function renderProviders(provStatus) {
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
  grid.innerHTML = Object.entries(provStatus||{}).map(([id, p]) =>
    `<div class="prov-card">
      <div class="prov-card-top">
        <span class="prov-name">${p.label||id}</span>
        <span class="badge ${p.status}">${p.status === 'on' ? 'Ready' : p.status === 'warn' ? 'No Key' : 'Off'}</span>
      </div>
      <div class="prov-meta">${p.status === 'on' ? '✓ Configured' : '—'}</div>
    </div>`
  ).join('');
}

// ── Models Pane ───────────────────────────────────────────────────────────
function renderModels(sections) {
  const pane = document.createElement('div');
  pane.id = 'pane-models';
  pane.className = 'view-pane';

  const modelSection = sections?.models || { fields: [] };
  const thinkingSection = sections?.thinking || { fields: [] };

  pane.innerHTML = `
    <div class="section">
      <div class="section-head"><h2>Model Routing</h2><span class="section-tag">Tiers</span></div>
      <div class="cfg-grid">${(modelSection.fields||[]).map(f => buildField(f)).join('')}</div>
    </div>
    <div class="section">
      <div class="section-head"><h2>Extended Thinking</h2><span class="section-tag">Per-model</span></div>
      <div class="cfg-grid">${(thinkingSection.fields||[]).map(f => buildField(f)).join('')}</div>
    </div>
  `;
  $('viewContainer').appendChild(pane);
  bindFields();
}

// ── Settings Pane ─────────────────────────────────────────────────────────
function renderSettings(sections) {
  const pane = document.createElement('div');
  pane.id = 'pane-settings';
  pane.className = 'view-pane';

  const order = ['general', 'api', 'providers', 'rate_limiting', 'advanced'];
  let html = '';
  for (const key of order) {
    const sec = sections?.[key];
    if (!sec) continue;
    const regular = sec.fields.filter(f => !f.advanced);
    const advanced = sec.fields.filter(f => f.advanced);
    html += `<div class="cfg-section">
      <div class="cfg-section-title">${sec.label}</div>
      <div class="cfg-grid">${regular.map(f => buildField(f)).join('')}</div>
      ${advanced.length ? `
        <button class="adv-toggle" onclick="this.classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
          <span class="chev">▸</span> Advanced (${advanced.length})
        </button>
        <div class="adv-fields">${advanced.map(f => buildField(f)).join('')}</div>
      ` : ''}
    </div>`;
  }
  pane.innerHTML = html;
  $('viewContainer').appendChild(pane);
  bindFields();
}

// ── Field Builder ─────────────────────────────────────────────────────────
function buildField(f) {
  const id = `f-${f.key}`;
  const val = f.value ?? '';
  const display = f.secret && val ? M : val;
  const desc = f.description ? `<div class="cfg-desc">${f.description}</div>` : '';
  const info = f.description ? `<span class="info-icon" title="${f.description.replace(/"/g,'&quot;')}">?</span>` : '';

  let input = '';
  switch (f.type) {
    case 'boolean':
      input = `<input type="checkbox" id="${id}" data-key="${f.key}" ${(val===true||val==='true')?'checked':''} onchange="mark('${f.key}',this)">`;
      break;
    case 'select':
    case 'options':
      const opts = ['', ...(f.options||[])].map(o =>
        `<option value="${o}" ${o===val?'selected':''}>${o||'— Select —'}</option>`
      ).join('');
      input = `<select id="${id}" data-key="${f.key}" onchange="mark('${f.key}',this)">${opts}</select>`;
      break;
    case 'textarea':
      input = `<textarea id="${id}" data-key="${f.key}" onchange="mark('${f.key}',this)">${display}</textarea>`;
      break;
    case 'number':
      input = `<input type="number" id="${id}" data-key="${f.key}" value="${display}" onchange="mark('${f.key}',this)">`;
      break;
    default:
      input = `<input type="${f.secret?'password':'text'}" id="${id}" data-key="${f.key}" value="${display}" onchange="mark('${f.key}',this)" ${f.secret&&val?'data-masked':''}>`;
  }
  return `<div class="cfg-field" data-key="${f.key}"><label class="cfg-label" for="${id}">${f.label}${info}</label>${input}${desc}</div>`;
}

function bindFields() {
  $$('.cfg-field input, .cfg-field select, .cfg-field textarea').forEach(el => {
    const key = el.dataset.key;
    if (key) {
      // restore dirty state if previously marked
    }
  });
}

// ── Dirty Tracking ────────────────────────────────────────────────────────
function getVal(el) {
  if (el.type === 'checkbox') return el.checked;
  if (el.dataset.masked && el.value === M) return null;
  return el.value;
}
function mark(key, el) {
  const v = getVal(el);
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
    await api('/admin/api/config/apply', { method: 'POST', body: JSON.stringify(changes) });
    msg.className = 'footbar-center ok';
    msg.textContent = '✓ Saved';
    S.dirty.clear();
    updateDirty();
    toast('Applied — restart may be needed', 'success');
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

    renderNav();
    $('viewContainer').innerHTML = '';

    const sections = data.sections || {};
    const provStatus = data.provider_status || {};

    renderDashboard(sections, provStatus);
    renderProviders(provStatus);
    renderModels(sections);
    renderSettings(sections);

    updateDirty();
    toast('Console ready', 'info');
  } catch (e) {
    toast('Failed to load: ' + e.message, 'error');
  }
}

document.addEventListener('DOMContentLoaded', load);
