// ── State ──────────────────────────────────────────────────────────────────────
let timerInterval = null;
let elapsedSeconds = 0;
let currentSessionId = null;
let stats = { total_minutes: 0, session_count: 0, milestones: [] };

const MILESTONES = [
,
];

// ── DOM refs ───────────────────────────────────────────────────────────────────
const timerDisplay   = document.getElementById('timerDisplay');
const startBtn       = document.getElementById('startBtn');
const stopBtn        = document.getElementById('stopBtn');
const sessionLabel   = document.getElementById('sessionLabel');
const streakFill     = document.getElementById('streakFill');
const nextMilestone  = document.getElementById('nextMilestone');
const totalHoursEl   = document.getElementById('totalHours');
const sessionCountEl = document.getElementById('sessionCount');
const badgeCountEl   = document.getElementById('badgeCount');
const milestonesGrid = document.getElementById('milestonesGrid');
const badgePopup     = document.getElementById('badgePopup');
const overlay        = document.getElementById('overlay');

// ── Timer logic ────────────────────────────────────────────────────────────────
function formatTime(secs) {
  const h = String(Math.floor(secs / 3600)).padStart(2, '0');
  const m = String(Math.floor((secs % 3600) / 60)).padStart(2, '0');
  const s = String(secs % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

function tick() {
  elapsedSeconds++;
  timerDisplay.textContent = formatTime(elapsedSeconds);
  updateProgressBar();
}

function updateProgressBar() {
  const elapsedMinutes = elapsedSeconds / 60;
  const totalMinutes   = (stats.total_minutes || 0) + elapsedMinutes;

  // Find next uncrossed milestone
  const next = MILESTONES.find(m => m.minutes > totalMinutes);
  const prev = [...MILESTONES].reverse().find(m => m.minutes <= totalMinutes);

  if (!next) {
    streakFill.style.width = '100%';
    nextMilestone.textContent = '🎉 All milestones reached!';
    return;
  }

  const base    = prev ? prev.minutes : 0;
  const range   = next.minutes - base;
  const current = totalMinutes - base;
  const pct     = Math.min((current / range) * 100, 100);

  streakFill.style.width = `${pct}%`;
  nextMilestone.textContent = `Next milestone: ${next.label} (${next.minutes >= 60
    ? next.minutes / 60 + 'h total'
    : next.minutes + ' min'})`
  ;
}

// ── API calls ──────────────────────────────────────────────────────────────────
async function startSession() {
  const res  = await fetch('/api/session/start', { method: 'POST' });
  const data = await res.json();
  currentSessionId = data.session_id;
}

async function endSession() {
  if (!currentSessionId) return [];
  const res  = await fetch('/api/session/end', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: currentSessionId, elapsed_seconds: elapsedSeconds }),
  });
  const data = await res.json();
  return data.new_badges || [];
}

async function loadStats() {
  const res  = await fetch('/api/stats');
  stats = await res.json();
  renderStats();
  renderMilestones();
}

// ── Render ─────────────────────────────────────────────────────────────────────
function renderStats() {
  const h = Math.floor(stats.total_minutes / 60);
  const m = stats.total_minutes % 60;
  totalHoursEl.textContent   = `${h}h ${m}m`;
  sessionCountEl.textContent = stats.session_count;
  badgeCountEl.textContent   = stats.milestones.filter(m => m.earned).length;
}

function renderMilestones() {
  milestonesGrid.innerHTML = '';
  (stats.milestones || MILESTONES.map(m => ({ ...m, earned: false }))).forEach(m => {
    const row = document.createElement('div');
    row.className = `milestone-row ${m.earned ? 'earned' : ''}`;
    const timeLabel = m.minutes >= 60 ? `${m.minutes / 60}h total` : `${m.minutes} min`;
    row.innerHTML = `
      <div class="milestone-icon">${m.icon}</div>
      <div class="milestone-info">
        <div class="milestone-name">${m.label}</div>
        <div class="milestone-time">${timeLabel}</div>
      </div>
      ${m.prize_eligible ? '<span class="milestone-prize">🎁 Real Prize</span>' : ''}
    `;
    milestonesGrid.appendChild(row);
  });
}

// ── Badge popup ────────────────────────────────────────────────────────────────
let badgeQueue = [];

function showNextBadge() {
  if (!badgeQueue.length) return;
  const badge = badgeQueue.shift();
  document.getElementById('popupIcon').textContent  = badge.icon;
  document.getElementById('popupTitle').textContent = badge.label + ' Unlocked!';
  document.getElementById('popupDesc').textContent  = badge.prize_eligible
    ? `You've studied ${badge.minutes >= 60 ? badge.minutes/60 + ' hours' : badge.minutes + ' minutes'} total. You're eligible for a real prize! 🎁`
    : `You've studied ${badge.minutes >= 60 ? badge.minutes/60 + ' hours' : badge.minutes + ' minutes'} total. Keep going!`;
  badgePopup.classList.remove('hidden');
  overlay.classList.remove('hidden');
}

window.closeBadgePopup = function() {
  badgePopup.classList.add('hidden');
  overlay.classList.add('hidden');
  // Show next badge if queued
  if (badgeQueue.length) setTimeout(showNextBadge, 300);
};

// ── Event handlers ─────────────────────────────────────────────────────────────
startBtn.addEventListener('click', async () => {
  await startSession();
  elapsedSeconds = 0;
  timerDisplay.textContent = '00:00:00';
  timerDisplay.classList.add('running');
  sessionLabel.textContent = 'SESSION IN PROGRESS';
  startBtn.classList.add('hidden');
  stopBtn.classList.remove('hidden');
  timerInterval = setInterval(tick, 1000);
});

stopBtn.addEventListener('click', async () => {
  clearInterval(timerInterval);
  timerInterval = null;
  timerDisplay.classList.remove('running');
  sessionLabel.textContent = 'SESSION COMPLETE';
  startBtn.classList.remove('hidden');
  stopBtn.classList.add('hidden');

  const newBadges = await endSession();
  await loadStats();
  updateProgressBar();

  if (newBadges.length) {
    badgeQueue = [...newBadges];
    showNextBadge();
  }
});

// ── Init ───────────────────────────────────────────────────────────────────────
loadStats();
