const today = document.body.dataset.today;
const dashboardDate = document.body.dataset.dashboardDate || today;
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
let editingId = null;
let toastTimer;

function notify(message, isError = false) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.toggle('error', isError);
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3600);
}

async function api(url, options = {}) {
  const response = await fetch(url, {headers: {'Content-Type': 'application/json'}, ...options});
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'The request could not be completed.');
  return body;
}

function showView(name) {
  $$('.view').forEach(view => view.classList.toggle('active', view.id === `view-${name}`));
  $$('.nav-item').forEach(button => button.classList.toggle('active', button.dataset.view === name));
  $('#crumb-current').textContent = ({dashboard: 'Overview', students: 'Students', attendance: 'Take attendance', reports: 'Reports'})[name];
  if (name === 'dashboard') loadDashboard();
  if (name === 'students') loadStudents();
  if (name === 'attendance') loadAttendance();
  if (name === 'reports') loadReports();
  history.replaceState(null, '', `#${name}`);
}

$$('[data-view]').forEach(button => button.addEventListener('click', () => showView(button.dataset.view)));
$$('[data-go]').forEach(button => button.addEventListener('click', () => showView(button.dataset.go)));

async function loadDashboard() {
  try {
    const data = await api(`/api/dashboard?date=${encodeURIComponent($('#dashboard-date').value)}`);
    $('#metric-total').textContent = data.total;
    $('#metric-present').textContent = data.present;
    $('#metric-absent').textContent = data.absent;
    $('#metric-rate').textContent = Number(data.overall).toFixed(2).replace(/\.00$/, '');
    $('#low-count').textContent = `${data.low.length} student${data.low.length === 1 ? '' : 's'}`;
    $('#low-list').innerHTML = data.low.length ? data.low.map(student => `<div class="low-row"><span class="low-id">${escapeHtml(student['Student ID'])}</span><span class="low-name">${escapeHtml(student['Student Name'])}</span><span class="low-rate">${Number(student['Attendance %']).toFixed(1)}%</span></div>`).join('') : '<div class="empty-state">No students below 75% in recorded classes.</div>';
  } catch (error) { notify(error.message, true); }
}
$('#dashboard-date').addEventListener('change', loadDashboard);

async function loadStudents(query = $('#student-search').value) {
  try {
    const data = await api(`/api/students?q=${encodeURIComponent(query)}`);
    $('#student-count').textContent = `(${data.length})`;
    $('#students-body').innerHTML = data.map(student => `<tr><td>${escapeHtml(student['Student ID'])}</td><td class="student-name">${escapeHtml(student['Student Name'])}</td><td>${escapeHtml(student.Department)}</td><td>${escapeHtml(student.Semester)}</td><td>${escapeHtml(student.Section)}</td><td><button class="row-action" data-edit="${escapeHtml(student['Student ID'])}">Edit</button></td></tr>`).join('');
    $('#students-empty').classList.toggle('hidden', data.length > 0);
  } catch (error) { notify(error.message, true); }
}
let searchDelay;
$('#student-search').addEventListener('input', () => { clearTimeout(searchDelay); searchDelay = setTimeout(() => loadStudents(), 180); });
$('#new-student').addEventListener('click', () => openStudentForm());
$('#cancel-student').addEventListener('click', closeStudentForm);
$('#students-body').addEventListener('click', async event => {
  const button = event.target.closest('[data-edit]');
  if (!button) return;
  try {
    const rows = await api(`/api/students?q=${encodeURIComponent(button.dataset.edit)}`);
    const student = rows.find(row => row['Student ID'] === button.dataset.edit);
    if (student) openStudentForm(student);
  } catch (error) { notify(error.message, true); }
});
function openStudentForm(student = null) {
  editingId = student ? student['Student ID'] : null;
  const form = $('#student-form');
  form.reset();
  $('#student-form-title').textContent = student ? `Edit ${student['Student ID']}` : 'Add a student';
  for (const [name, key] of [['student_id', 'Student ID'], ['name', 'Student Name'], ['department', 'Department'], ['semester', 'Semester'], ['section', 'Section']]) {
    form.elements[name].value = student ? student[key] : '';
    form.elements[name].readOnly = Boolean(student && name === 'student_id');
  }
  $('#student-form-panel').classList.remove('hidden');
  $('#student-form-panel').scrollIntoView({behavior: 'smooth', block: 'nearest'});
}
function closeStudentForm() { $('#student-form-panel').classList.add('hidden'); editingId = null; }
$('#student-form').addEventListener('submit', async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form));
  try {
    const url = editingId ? `/api/students/${encodeURIComponent(editingId)}` : '/api/students';
    const method = editingId ? 'PUT' : 'POST';
    const result = await api(url, {method, body: JSON.stringify(data)});
    notify(result.message);
    closeStudentForm();
    await loadStudents();
    await loadDashboard();
  } catch (error) { notify(error.message, true); }
});

async function loadAttendance() {
  const date = $('#attendance-date').value;
  try {
    const data = await api(`/api/attendance?date=${encodeURIComponent(date)}`);
    $('#attendance-body').innerHTML = data.map(student => {
      const status = student.Status || '';
      const selectClass = status === 'Present' ? 'present' : status === 'Absent' ? 'absent' : status === 'On Leave' ? 'leave' : '';
      return `<tr><td>${escapeHtml(student['Student ID'])}</td><td class="student-name">${escapeHtml(student['Student Name'])}</td><td>${escapeHtml(student.Department)}</td><td><select class="status-select ${selectClass}" data-student="${escapeHtml(student['Student ID'])}" aria-label="Attendance for ${escapeHtml(student['Student Name'])}"><option value="">Not recorded</option><option ${status === 'Present' ? 'selected' : ''}>Present</option><option ${status === 'Absent' ? 'selected' : ''}>Absent</option><option ${status === 'On Leave' ? 'selected' : ''}>On Leave</option></select></td></tr>`;
    }).join('');
    $('#attendance-empty').classList.toggle('hidden', data.length > 0);
    $('#attendance-state').textContent = data.some(row => row.Status) ? 'Existing records are shown; you can correct them.' : 'Choose statuses to begin';
  } catch (error) { notify(error.message, true); }
}
$('#attendance-date').addEventListener('change', loadAttendance);
$('#attendance-body').addEventListener('change', event => {
  if (!event.target.matches('.status-select')) return;
  event.target.classList.remove('present', 'absent', 'leave');
  event.target.classList.add(event.target.value === 'Present' ? 'present' : event.target.value === 'Absent' ? 'absent' : event.target.value === 'On Leave' ? 'leave' : '');
});
$('#save-attendance').addEventListener('click', async () => {
  const statuses = Object.fromEntries($$('.status-select').filter(select => select.value).map(select => [select.dataset.student, select.value]));
  if (!Object.keys(statuses).length) return notify('Choose a status for at least one student.', true);
  let result;
  try {
    result = await api('/api/attendance', {method: 'POST', body: JSON.stringify({date: $('#attendance-date').value, statuses})});
  } catch (error) {
    if (!error.message.includes('already exists')) return notify(error.message, true);
    if (!window.confirm('Attendance already exists for one or more selected students on this date. Correct those entries?')) return;
    try {
      result = await api('/api/attendance', {method: 'POST', body: JSON.stringify({date: $('#attendance-date').value, statuses, correct_existing: true})});
    } catch (correctionError) { return notify(correctionError.message, true); }
  }
  try {
    notify(result.message);
    await loadAttendance();
    await loadDashboard();
    await loadReports();
  } catch (error) { notify(error.message, true); }
});

async function loadReports() {
  const params = new URLSearchParams();
  for (const [id, key] of [['filter-id', 'student_id'], ['filter-start', 'start_date'], ['filter-end', 'end_date'], ['filter-department', 'department'], ['filter-semester', 'semester']]) {
    const value = $(`#${id}`).value.trim();
    if (value) params.set(key, value);
  }
  try {
    const data = await api(`/api/reports/students?${params}`);
    $('#reports-body').innerHTML = data.map(student => {
      const rate = Number(student['Attendance %']);
      const badge = student['Counted Classes'] === 0 ? '<span class="status-pill">No classes counted</span>' : `<span class="status-pill ${rate < 75 ? 'low' : 'good'}">${rate.toFixed(1)}%${rate < 75 ? ' · Below 75%' : ''}</span>`;
      return `<tr><td>${escapeHtml(student['Student ID'])}</td><td class="student-name">${escapeHtml(student['Student Name'])}</td><td>${student['Present Days']}</td><td>${student['Absent Days']}</td><td>${student['Leave Days']}</td><td>${student['Counted Classes']}</td><td>${badge}</td></tr>`;
    }).join('');
    $('#reports-empty').classList.toggle('hidden', data.length > 0);
  } catch (error) { notify(error.message, true); }
}
$('#apply-filters').addEventListener('click', loadReports);
$('#export-summary').addEventListener('click', () => exportReport(''));
$('#export-daily').addEventListener('click', () => exportReport($('#export-date').value));
async function exportReport(date) {
  try { const result = await api('/api/reports/export', {method: 'POST', body: JSON.stringify({date})}); notify(result.message); }
  catch (error) { notify(error.message, true); }
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}

$('#today-text').textContent = new Intl.DateTimeFormat(undefined, {weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'}).format(new Date(`${today}T12:00:00`));
$('#dashboard-date').value = dashboardDate;
$('#attendance-date').value = today;
$('#export-date').value = today;
showView(location.hash.slice(1) || 'dashboard');
