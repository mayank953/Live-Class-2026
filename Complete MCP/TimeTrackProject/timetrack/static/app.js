// TimeTrack frontend -- talks only to this app's own REST API (/api/...).

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('view-' + tab.dataset.view).classList.add('active');
  });
});

async function loadEntries() {
  const res = await fetch('/api/entries');
  const entries = await res.json();
  const tbody = document.querySelector('#entriesTable tbody');
  tbody.innerHTML = entries.map(e => `
    <tr>
      <td>${e.entry_date}</td>
      <td>${escapeHtml(e.employee_name)}</td>
      <td>${escapeHtml(e.project)}</td>
      <td>${e.hours}</td>
      <td>${escapeHtml(e.description)}</td>
    </tr>
  `).join('');
}

async function loadProjectOptions() {
  const res = await fetch('/api/projects');
  const projects = await res.json();
  const select = document.getElementById('projectSelect');
  select.innerHTML = projects.map(p => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join('');
}

document.getElementById('loadSummaryBtn').addEventListener('click', async () => {
  const project = document.getElementById('projectSelect').value;
  const res = await fetch(`/api/projects/${encodeURIComponent(project)}/summary`);
  const summary = await res.json();
  const rows = Object.entries(summary.by_employee)
    .map(([name, hours]) => `<div class="row"><span>${escapeHtml(name)}</span><span>${hours}h</span></div>`)
    .join('');
  document.getElementById('summaryResult').innerHTML = `
    <div class="total">${summary.total_hours}h total</div>
    <p style="color:#64748b;font-size:13px;margin:4px 0 16px">${escapeHtml(summary.project)}</p>
    ${rows}
  `;
});

document.getElementById('logForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    employee_name: document.getElementById('employeeInput').value.trim(),
    project: document.getElementById('projectInput').value.trim(),
    entry_date: document.getElementById('dateInput').value,
    hours: parseFloat(document.getElementById('hoursInput').value),
    description: document.getElementById('descInput').value.trim(),
  };
  await fetch('/api/entries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  document.getElementById('logForm').reset();
  loadEntries();
  loadProjectOptions();
});

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

loadEntries();
loadProjectOptions();
