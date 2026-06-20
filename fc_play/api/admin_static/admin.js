/* =============================================================================
   FC-Play Admin — Dashboard Controller
   Swiss Minimalism × Dark OLED — Smooth UX
   ============================================================================= */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const state = {
  config: null,
  dirtyFields: new Map(),
  activeView: 'providers',
};

const MASKED = '••••••••';

// ---------------------------------------------------------------------------
// View definitions
// ---------------------------------------------------------------------------
const VIEWS = [
  { id: 'providers', label: 'Providers', icon: 'cube', title: 'Providers & Configuration' },
  { id: 'status', label: 'Status', icon: 'activity', title: 'Server Status' },
];

const NAV_ICONS = {
  cube: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
  activity: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
  settings: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
};

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------
const $ = (id) => document.getElementById(id);
const $$ = (sel) => document.querySelectorAll(sel);

function showToast(message, type = 'info') {
  const container = $('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------
async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || err.detail || res.statusText);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------
async function load() {
  try {
    const data = await api('/admin/api/config');
    state.config = data;
    renderNav();
    renderProviders(data.provider_status || {});
    renderConfigSections(data.sections || {});
    updateDirtyState();
    showToast('Dashboard loaded', 'info');
  } catch (err) {
    showToast(`Failed to load config: ${err.message}`, 'error');
  }
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------
function renderNav() {
  const nav = $('sectionNav');
  nav.innerHTML = VIEWS.map((v, i) => `
    <button class="nav-link ${i === 0 ? 'active' : ''}"
            onclick="setActiveView('${v.id}')"
            data-view="${v.id}">
      ${NAV_ICONS[v.icon] || ''}
      ${v.label}
    </button>
  `).join('');
}

function setActiveView(viewId) {
  state.activeView = viewId;
  $$('.nav-link').forEach(el => el.classList.toggle('active', el.dataset.view === viewId));
  $$('.admin-view').forEach(el => el.hidden = el.id !== `view-${viewId}`);
  const view = VIEWS.find(v => v.id === viewId);
  if (view) $('pageTitle').textContent = view.title;
}

// ---------------------------------------------------------------------------
// Provider Grid
// ---------------------------------------------------------------------------
const PROVIDER_ICONS = {
  custom: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
  openai: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5"/><line x1="12" y1="22" x2="12" y2="15.5"/><polyline points="22 8.5 12 15.5 2 8.5"/></svg>',
  default: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><box x="3" y="3" width="18" height="18"/><path d="M3 9h18"/></svg>',
};

function statusPill(status) {
  const labels = { ok: 'Connected', warn: 'No Key', error: 'Offline', neutral: 'Unknown' };
  return `<span class="status-pill ${status}"><span class="dot"></span> ${labels[status] || status}</span>`;
}

function renderProviders(providers) {
  const grid = $('providerGrid');
  const entries = Object.entries(providers);
  $('providerCount').textContent = `${entries.filter(([_, p]) => p.status === 'ok').length} connected`;

  grid.innerHTML = entries.map(([id, provider]) => `
    <div class="provider-card" data-provider="${id}">
      <div class="provider-card-title">
        ${PROVIDER_ICONS[id] || PROVIDER_ICONS.default}
        ${provider.label || id}
      </div>
      <div class="provider-card-meta">
        ${statusPill(provider.status)}
      </div>
    </div>
  `).join('');
}

// ---------------------------------------------------------------------------
// Config Sections
// ---------------------------------------------------------------------------
function renderConfigSections(sections) {
  const container = $('configSections');
  container.innerHTML = '';

  Object.entries(sections).forEach(([key, section], idx) => {
    const sectionEl = document.createElement('div');
    sectionEl.className = 'config-section';

    const regularFields = section.fields.filter(f => !f.advanced);
    const advancedFields = section.fields.filter(f => f.advanced);

    sectionEl.innerHTML = `
      <div class="config-section-title">${section.label}</div>
      <div class="field-grid" data-section="${key}">
        ${regularFields.map(f => renderField(f)).join('')}
      </div>
      ${advancedFields.length ? `
        <div class="advanced-section">
          <button class="advanced-toggle" onclick="this.classList.toggle('active'); this.nextElementSibling.classList.toggle('show')">
            <svg class="chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            Advanced Settings (${advancedFields.length})
          </button>
          <div class="advanced-fields">
            ${advancedFields.map(f => renderField(f)).join('')}
          </div>
        </div>
      ` : ''}
    `;

    container.appendChild(sectionEl);
  });
}

function renderField(field) {
  const inputId = `field-${field.key}`;
  const value = field.value ?? '';
  const isSecret = field.secret;
  const displayValue = isSecret && value ? MASKED : value;

  let input = '';
  let extraAttr = '';

  switch (field.type) {
    case 'boolean':
      input = `<input type="checkbox" id="${inputId}" data-key="${field.key}"
                ${value === true || value === 'true' ? 'checked' : ''}
                onchange="markDirty('${field.key}', this)">`;
      break;
    case 'select':
    case 'options':
      const opts = (field.options || []).map(o =>
        `<option value="${o}" ${o === value ? 'selected' : ''}>${o}</option>`
      ).join('');
      input = `<select id="${inputId}" data-key="${field.key}" onchange="markDirty('${field.key}', this)">
        <option value="">— Select —</option>
        ${opts}
      </select>`;
      break;
    case 'textarea':
      input = `<textarea id="${inputId}" data-key="${field.key}"
                onchange="markDirty('${field.key}', this)"
                placeholder="${field.placeholder || ''}">${displayValue}</textarea>`;
      break;
    case 'number':
      input = `<input type="number" id="${inputId}" data-key="${field.key}"
                value="${displayValue}"
                onchange="markDirty('${field.key}', this)"
                placeholder="${field.placeholder || ''}">`;
      break;
    default:
      extraAttr = isSecret ? `type="password"` : `type="text"`;
      input = `<input ${extraAttr} id="${inputId}" data-key="${field.key}"
                value="${displayValue}"
                onchange="markDirty('${field.key}', this)"
                placeholder="${field.placeholder || ''}"
                ${isSecret && value ? 'data-masked="true"' : ''}>`;
  }

  return `
    <div class="field-group" data-field="${field.key}">
      <label for="${inputId}">
        ${field.label}
        ${field.description ? `<span class="field-source" title="${field.description}">ⓘ</span>` : ''}
      </label>
      ${input}
      ${field.description ? `<div class="field-desc">${field.description}</div>` : ''}
    </div>
  `;
}

// ---------------------------------------------------------------------------
// Dirty State Tracking
// ---------------------------------------------------------------------------
function getFieldValue(input) {
  if (input.type === 'checkbox') return input.checked;
  if (input.dataset.masked && input.value === MASKED) return null; // unchanged secret
  return input.value;
}

function markDirty(key, input) {
  const val = getFieldValue(input);
  if (val === null) {
    state.dirtyFields.delete(key);
  } else {
    state.dirtyFields.set(key, val);
  }
  updateDirtyState();
}

function updateDirtyState() {
  const count = state.dirtyFields.size;
  const el = $('dirtyState');
  const btn = $('applyBtn');

  if (count > 0) {
    el.classList.add('dirty');
    el.innerHTML = `<span class="dirty-dot"></span> ${count} change${count > 1 ? 's' : ''} pending`;
    btn.disabled = false;
  } else {
    el.classList.remove('dirty');
    el.innerHTML = `<span class="dirty-dot"></span> No changes`;
    btn.disabled = true;
  }
}

// ---------------------------------------------------------------------------
// Validate & Apply
// ---------------------------------------------------------------------------
async function validate() {
  const msg = $('actionMessage');
  msg.innerHTML = '<span class="spinner"></span> Validating...';

  try {
    const changes = Object.fromEntries(state.dirtyFields);
    const result = await api('/admin/api/config/validate', {
      method: 'POST',
      body: JSON.stringify(changes),
    });
    msg.className = 'action-message success';
    msg.textContent = '✓ Config valid';
    showToast('Configuration is valid', 'success');
  } catch (err) {
    msg.className = 'action-message error';
    msg.textContent = `✗ ${err.message}`;
    showToast(`Validation failed: ${err.message}`, 'error');
  }
}

async function apply() {
  const msg = $('actionMessage');
  const btn = $('applyBtn');
  msg.innerHTML = '<span class="spinner"></span> Applying...';
  btn.disabled = true;

  try {
    const changes = Object.fromEntries(state.dirtyFields);
    const result = await api('/admin/api/config/apply', {
      method: 'POST',
      body: JSON.stringify(changes),
    });
    msg.className = 'action-message success';
    msg.textContent = '✓ Changes applied successfully';
    state.dirtyFields.clear();
    updateDirtyState();
    showToast('Configuration saved! Restart may be required.', 'success');
  } catch (err) {
    msg.className = 'action-message error';
    msg.textContent = `✗ ${err.message}`;
    btn.disabled = false;
    showToast(`Failed to apply: ${err.message}`, 'error');
  }
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  load();
  // Start activity simulation
  const uptime = $('uptimeDisplay');
  let seconds = 0;
  setInterval(() => {
    seconds++;
    if (seconds < 60) uptime.textContent = `${seconds}s`;
    else uptime.textContent = `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  }, 1000);
});
