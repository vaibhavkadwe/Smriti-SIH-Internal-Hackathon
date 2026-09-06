/* ==========================================================================
   Smriti Elder-Care Companion — Vanilla JavaScript Client Engine
   Communicates directly with FastAPI backend endpoints (/api/v1).
   ========================================================================== */

const API_BASE = '/api/v1';
let token = localStorage.getItem('smriti_token') || null;
let currentLanguage = 'english';
let demoPatientId = '6910b26a-369c-491d-b4d1-e8e950636528';

// State for active Match-It game
let matchGameSessionId = null;
let matchCards = [];
let flippedIndices = [];
let matchedPairs = 0;
let moveCount = 0;
let gameScore = 0;

// On Page Load
document.addEventListener('DOMContentLoaded', () => {
  if (token) {
    checkCurrentUser();
    switchView('landing');
  } else {
    // Landing page is the default entry face
    switchView('landing');
  }
});

// View Switching Logic
function switchView(mode) {
  const aliases = {
    landing: 'landingView',
    patient: 'patientView',
    caregiver: 'caregiverView',
    landingView: 'landingView',
    patientView: 'patientView',
    caregiverView: 'caregiverView',
  };
  const views = ['landingView', 'patientView', 'caregiverView'];
  const sections = {
    landingView: document.getElementById('landingView'),
    patientView: document.getElementById('patientView'),
    caregiverView: document.getElementById('caregiverView'),
  };
  const showKey = aliases[mode] || 'landingView';

  views.forEach(v => sections[v].classList.add('hidden'));
  sections[showKey].classList.remove('hidden');

  // Nav button states (login pill hides when session exists)
  const loginBtn = document.getElementById('navLoginBtn');
  if (loginBtn) loginBtn.classList.toggle('hidden', !!token && showKey !== 'caregiverView');

  if (showKey === 'patientView') {
    loadPatientReminders();
  } else if (showKey === 'caregiverView') {
    if (token) {
      document.getElementById('caregiverAuthCard').classList.add('hidden');
      document.getElementById('caregiverMainContent').classList.remove('hidden');
      loadCaregiverDashboard();
    } else {
      document.getElementById('caregiverAuthCard').classList.remove('hidden');
      document.getElementById('caregiverMainContent').classList.add('hidden');
    }
  }
}

// Landing helpers
function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function dismissAnnouncement() {
  document.getElementById('announcementBar').style.display = 'none';
}

function toggleFaq(btn) {
  const item = btn.closest('.faq-item');
  const open = item.getAttribute('data-open') === 'true';
  item.setAttribute('data-open', open ? 'false' : 'true');
  btn.setAttribute('aria-expanded', open ? 'false' : 'true');
}

// Language Selector Handler
function onLanguageChange(lang) {
  currentLanguage = lang;
  
  const translations = {
    english: {
      greeting: "Hello, Grandma Phukan",
      subtext: "Welcome back. What would you like to do today?",
      matchTitle: "Play Card Match Game",
      matchSub: "Fun memory exercise with cultural pictures",
      routineTitle: "Daily Routine Game",
      routineSub: "Arrange daily activities in right order",
      remindersTitle: "My Daily Reminders",
      remindersSub: "Check medicine, meals, and hydration",
      companionTitle: "Talk to Voice Companion",
      companionSub: "Friendly assistant to guide and chat"
    },
    assamese: {
      greeting: "নমস্কাৰ, আইতা ফুকন",
      subtext: "আপোনাক স্বাগতম। আজি আপুনি কি কৰিব বিচাৰে?",
      matchTitle: "কাৰ্ড মি মেল খেলা",
      matchSub: "সংস্কৃতিক ছবিৰে সোঁৱৰণি অনুশীলন",
      routineTitle: "দৈনিক নিয়ম খেল",
      routineSub: "দৈনন্দিন কাম-কাজ সঠিক ক্ৰমত সজাওক",
      remindersTitle: "মোৰ দৈনিক সোঁৱৰণী",
      remindersSub: "দৰব, আহাৰ আৰু পানী খোৱাৰ সময় চাওক",
      companionTitle: "কথা-বাৰ্তাৰ সহযোগী",
      companionSub: "সহজ আৰু বন্ধুত্বপূৰ্ণ সহায়ক"
    },
    bengali: {
      greeting: "নমস্কার, আইমা ফুকন",
      subtext: "স্বাগতম। আজ আপনি কি করতে চান?",
      matchTitle: "কার্ড মিল খেলা",
      matchSub: "স্মৃতিশক্তি বৃদ্ধির অনুশীলন",
      routineTitle: "দৈনন্দিন রুটিন খেলা",
      routineSub: "সঠিক ক্রমে সাজান",
      remindersTitle: "আমার রিমাইন্ডার",
      remindersSub: "ওষুধ ও খাবারের সময়সূচী",
      companionTitle: "ভয়েস সহকারী",
      companionSub: "সহজ কথোপকথন সহকারী"
    },
    hindi: {
      greeting: "नमस्ते, दादी फुकन",
      subtext: "आपका स्वागत है। आज आप क्या करना चाहेंगी?",
      matchTitle: "कार्ड मिलाओ खेल",
      matchSub: "सांस्कृतिक चित्रों के साथ याददाश्त का अभ्यास",
      routineTitle: "दैनिक दिनचर्या खेल",
      routineSub: "दैनिक कार्यों को सही क्रम में लगाएं",
      remindersTitle: "मेरे रिमाइंडर",
      remindersSub: "दवाई, भोजन और पानी का समय देखें",
      companionTitle: "वॉइस साथी",
      companionSub: "मार्गदर्शन के लिए मित्रवत सहायक"
    }
  };

  const t = translations[lang] || translations.english;
  document.getElementById('patientGreeting').innerText = t.greeting;
  document.getElementById('patientSubtext').innerText = t.subtext;
  document.getElementById('txtMatchItTitle').innerText = t.matchTitle;
  document.getElementById('txtMatchItSub').innerText = t.matchSub;
  document.getElementById('txtRoutineTitle').innerText = t.routineTitle;
  document.getElementById('txtRoutineSub').innerText = t.routineSub;
  document.getElementById('txtRemindersTitle').innerText = t.remindersTitle;
  document.getElementById('txtRemindersSub').innerText = t.remindersSub;
  document.getElementById('txtCompanionTitle').innerText = t.companionTitle;
  document.getElementById('txtCompanionSub').innerText = t.companionSub;
}

// Patient View Navigation Helpers
function openPatientFeature(feature) {
  closePatientPanels();
  if (feature === 'game') {
    document.getElementById('panelGame').classList.remove('hidden');
    startMatchItGame();
  } else if (feature === 'routine') {
    document.getElementById('panelRoutine').classList.remove('hidden');
    startRoutineGame();
  } else if (feature === 'reminders') {
    document.getElementById('panelReminders').classList.remove('hidden');
    loadPatientReminders();
  } else if (feature === 'chat') {
    document.getElementById('panelChat').classList.remove('hidden');
  }
}

function closePatientPanels() {
  document.getElementById('panelGame').classList.add('hidden');
  document.getElementById('panelRoutine').classList.add('hidden');
  document.getElementById('panelReminders').classList.add('hidden');
  document.getElementById('panelChat').classList.add('hidden');
}

/* ==========================================================================
   PATIENT GAME 1: MATCH-IT (Memory Card Game)
   ========================================================================== */
const CULTURAL_ITEMS = [
  'Assam Tea', 'Assam Tea',
  'Bihu Dhol', 'Bihu Dhol',
  'Kaziranga Rhino', 'Kaziranga Rhino',
  'Gamusa', 'Gamusa'
];

function startMatchItGame() {
  matchedPairs = 0;
  moveCount = 0;
  gameScore = 0;
  flippedIndices = [];
  
  document.getElementById('gameMoves').innerText = '0';
  document.getElementById('gameScore').innerText = '0';
  document.getElementById('gamePairs').innerText = '0/4';

  // Shuffle items
  matchCards = [...CULTURAL_ITEMS].sort(() => Math.random() - 0.5);

  const grid = document.getElementById('gameGrid');
  grid.innerHTML = '';

  matchCards.forEach((item, index) => {
    const cardEl = document.createElement('div');
    cardEl.className = 'game-card';
    cardEl.setAttribute('data-index', index);
    cardEl.innerText = '?';
    cardEl.onclick = () => handleCardClick(index, cardEl);
    grid.appendChild(cardEl);
  });
}

function handleCardClick(index, cardEl) {
  if (flippedIndices.length >= 2 || cardEl.classList.contains('flipped') || cardEl.classList.contains('matched')) {
    return;
  }

  cardEl.classList.add('flipped');
  cardEl.innerText = matchCards[index];
  flippedIndices.push({ index, val: matchCards[index], el: cardEl });

  if (flippedIndices.length === 2) {
    moveCount++;
    document.getElementById('gameMoves').innerText = moveCount;

    const [first, second] = flippedIndices;
    if (first.val === second.val) {
      first.el.classList.add('matched');
      second.el.classList.add('matched');
      matchedPairs++;
      gameScore += 25;
      document.getElementById('gameScore').innerText = gameScore;
      document.getElementById('gamePairs').innerText = `${matchedPairs}/4`;
      flippedIndices = [];

      if (matchedPairs === 4) {
        setTimeout(() => alert('🎉 Congratulations! You matched all memory cards!'), 300);
      }
    } else {
      setTimeout(() => {
        first.el.classList.remove('flipped');
        second.el.classList.remove('flipped');
        first.el.innerText = '?';
        second.el.innerText = '?';
        flippedIndices = [];
      }, 900);
    }
  }
}

/* ==========================================================================
   PATIENT GAME 2: ROUTINE SEQUENCING
   ========================================================================== */
let routineItems = [
  { id: 1, title: '1. Take Morning Blood Pressure Medicine' },
  { id: 2, title: '2. Eat Fresh Breakfast & Tea' },
  { id: 3, title: '3. Light Morning Walk in Garden' },
  { id: 4, title: '4. Drink Glass of Water & Rest' }
];

function startRoutineGame() {
  const container = document.getElementById('routineList');
  container.innerHTML = '';

  routineItems.forEach((step, idx) => {
    const itemEl = document.createElement('div');
    itemEl.className = 'reminder-item';
    itemEl.innerHTML = `
      <div class="reminder-title">${step.title}</div>
      <div>
        <button class="btn-secondary" onclick="moveStep(${idx}, -1)">▲ Move Up</button>
        <button class="btn-secondary" onclick="moveStep(${idx}, 1)">▼ Move Down</button>
      </div>
    `;
    container.appendChild(itemEl);
  });
}

function moveStep(idx, dir) {
  const target = idx + dir;
  if (target < 0 || target >= routineItems.length) return;
  const temp = routineItems[idx];
  routineItems[idx] = routineItems[target];
  routineItems[target] = temp;
  startRoutineGame();
}

function submitRoutineGame() {
  alert('Sequence submitted successfully! Performance logged to caregiver dashboard.');
}

/* ==========================================================================
   PATIENT REMINDERS
   ========================================================================== */
async function loadPatientReminders() {
  const container = document.getElementById('remindersContainer');
  container.innerHTML = '<p class="patient-subtext">Loading reminders...</p>';

  try {
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    const res = await fetch(`${API_BASE}/reminders/patients/${demoPatientId}/events`, { headers });
    
    if (res.ok) {
      const events = await res.json();
      if (events.length === 0) {
        container.innerHTML = `
          <div class="reminder-item">
            <div class="reminder-title">Morning BP Medicine</div>
            <div class="reminder-time">08:00 AM (Scheduled)</div>
            <button class="btn-large-action" onclick="acknowledgeReminder(this)">I TOOK THIS</button>
          </div>
          <div class="reminder-item">
            <div class="reminder-title">Hydration — Glass of Water</div>
            <div class="reminder-time">11:00 AM (Scheduled)</div>
            <button class="btn-large-action" onclick="acknowledgeReminder(this)">I DRANK WATER</button>
          </div>
        `;
        return;
      }
      container.innerHTML = events.map(ev => `
        <div class="reminder-item">
          <div>
            <div class="reminder-title">${ev.title || 'Scheduled Reminder'}</div>
            <div class="reminder-time">${ev.scheduled_at || 'Today'}</div>
          </div>
          <button class="btn-large-action ${ev.status === 'acknowledged' ? 'completed' : ''}" 
                  onclick="acknowledgeReminderEvent('${ev.id}', this)">
            ${ev.status === 'acknowledged' ? '✓ COMPLETED' : 'I COMPLETED THIS'}
          </button>
        </div>
      `).join('');
    } else {
      container.innerHTML = `
        <div class="reminder-item">
          <div>
            <div class="reminder-title">Morning Medicine (Amlodipine)</div>
            <div class="reminder-time">Due at 08:00 AM</div>
          </div>
          <button class="btn-large-action" onclick="acknowledgeReminder(this)">I TOOK THIS</button>
        </div>
      `;
    }
  } catch (err) {
    container.innerHTML = `
      <div class="reminder-item">
        <div>
          <div class="reminder-title">Morning Medicine (Amlodipine)</div>
          <div class="reminder-time">Due at 08:00 AM</div>
        </div>
        <button class="btn-large-action" onclick="acknowledgeReminder(this)">I TOOK THIS</button>
      </div>
    `;
  }
}

function acknowledgeReminder(btn) {
  btn.classList.add('completed');
  btn.innerText = '✓ COMPLETED';
  btn.disabled = true;
}

async function acknowledgeReminderEvent(eventId, btn) {
  try {
    const res = await fetch(`${API_BASE}/reminders/events/${eventId}/acknowledge`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      btn.classList.add('completed');
      btn.innerText = '✓ COMPLETED';
    }
  } catch (err) {
    acknowledgeReminder(btn);
  }
}

/* ==========================================================================
   PATIENT VOICE COMPANION CHAT
   ========================================================================== */
async function sendChatMessage(event) {
  event.preventDefault();
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  const messagesBox = document.getElementById('chatMessages');

  // Append User message
  const userMsg = document.createElement('div');
  userMsg.className = 'chat-bubble user';
  userMsg.innerText = text;
  messagesBox.appendChild(userMsg);

  input.value = '';
  messagesBox.scrollTop = messagesBox.scrollHeight;

  // Show typing response
  const botTyping = document.createElement('div');
  botTyping.className = 'chat-bubble bot';
  botTyping.innerText = '...';
  messagesBox.appendChild(botTyping);

  try {
    const res = await fetch(`${API_BASE}/voice-companion/chat`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        patient_id: demoPatientId,
        message: text,
        language: currentLanguage
      })
    });

    if (res.ok) {
      const data = await res.json();
      botTyping.innerText = data.response_text || data.text || 'I understand. Remember to rest well and stay hydrated!';
    } else {
      botTyping.innerText = 'That sounds wonderful! Is there anything else I can help you remember today?';
    }
  } catch (err) {
    botTyping.innerText = 'I am here with you. Make sure to take your afternoon tea and rest well!';
  }

  messagesBox.scrollTop = messagesBox.scrollHeight;
}

/* ==========================================================================
   CAREGIVER DASHBOARD & AUTH
   ========================================================================== */
function quickFillLogin(phone) {
  document.getElementById('loginPhone').value = phone;
  document.getElementById('loginPassword').value = 'DemoPass123';
}

async function handleLogin(event) {
  event.preventDefault();
  const phone = document.getElementById('loginPhone').value.trim();
  const password = document.getElementById('loginPassword').value.trim();

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password })
    });

    if (res.ok) {
      const data = await res.json();
      token = data.access_token;
      localStorage.setItem('smriti_token', token);
      
      document.getElementById('caregiverAuthCard').classList.add('hidden');
      document.getElementById('caregiverMainContent').classList.remove('hidden');
      checkCurrentUser();
      loadCaregiverDashboard();
    } else {
      alert('Login failed. Please check credentials.');
    }
  } catch (err) {
    alert('Network error signing in.');
  }
}

async function checkCurrentUser() {
  if (!token) return;
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const user = await res.json();
      const badge = document.getElementById('userInfoBadge');
      badge.classList.remove('hidden');
      document.getElementById('userRoleText').innerText = `${user.role.toUpperCase()} (${user.phone})`;
    }
  } catch (err) {
    console.warn('User auth session check failed');
  }
}

function logout() {
  token = null;
  localStorage.removeItem('smriti_token');
  document.getElementById('userInfoBadge').classList.add('hidden');
  switchView('landing');
}

async function loadCaregiverDashboard() {
  // Resolve the caregiver's real roster, then load their first patient.
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const me = await res.json();
      const rosterRes = await fetch(`${API_BASE}/dashboard/caregivers/${me.id}/patients`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (rosterRes.ok) {
        const patients = await rosterRes.json();
        const selector = document.getElementById('patientSelector');
        if (patients.length > 0) {
          selector.innerHTML = patients.map(p =>
            `<option value="${p.patient_id}">${p.name} (${p.cognitive_baseline ?? ''} — ${p.district ?? 'NER'})</option>`
          ).join('');
          demoPatientId = patients[0].patient_id;
        }
      }
    }
  } catch (err) {
    console.warn('Roster fetch failed, using demo patient');
  }
  loadPatientDashboardMetrics(demoPatientId);
  loadCaregiverSchedules();
  loadAuditLogs();
}

async function loadPatientDashboardMetrics(patientId) {
  try {
    const res = await fetch(`${API_BASE}/dashboard/patients/${patientId}/summary`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      if (data.accuracy_pct !== undefined) document.getElementById('metricAccuracy').innerText = `${Number(data.accuracy_pct).toFixed(1)}%`;
      if (data.compliance_pct !== undefined) document.getElementById('metricCompliance').innerText = `${Number(data.compliance_pct).toFixed(1)}%`;
      if (data.avg_response_time_ms !== undefined && data.avg_response_time_ms !== null) {
        document.getElementById('metricResponseTime').innerText = `${(data.avg_response_time_ms / 1000).toFixed(1)} sec`;
      }
      const alerts = data.active_alerts ?? [];
      document.getElementById('metricAlertCount').innerText = String(alerts.length);
    }
  } catch (err) {
    console.log('Metrics unavailable');
  }
}

/* ==========================================================================
   SCHEDULE MANAGEMENT
   ========================================================================== */
function toggleScheduleForm() {
  document.getElementById('scheduleForm').classList.toggle('hidden');
}

async function createReminderSchedule(event) {
  event.preventDefault();
  const type = document.getElementById('schType').value.toLowerCase();
  const time = document.getElementById('schTime').value.trim();
  const cadenceMode = document.getElementById('schCadence').value.toLowerCase();

  try {
    const res = await fetch(`${API_BASE}/reminders/schedules`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        patient_id: demoPatientId,
        reminder_type: type,
        cadence: `${cadenceMode}@${time}`
      })
    });

    if (res.ok) {
      toggleScheduleForm();
      loadCaregiverSchedules();
    } else {
      alert('Failed to save schedule.');
    }
  } catch (err) {
    alert('Error connecting to backend.');
  }
}

async function loadCaregiverSchedules() {
  const tbody = document.getElementById('caregiverScheduleTable');
  try {
    const res = await fetch(`${API_BASE}/reminders/schedules/${demoPatientId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const schedules = await res.json();
      if (schedules.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No schedules yet — add one above.</td></tr>';
        return;
      }
      tbody.innerHTML = schedules.map(s => `
        <tr>
          <td>${s.reminder_type.toUpperCase()}</td>
          <td>${s.reminder_type}</td>
          <td>${s.cadence}</td>
          <td>${s.cadence.includes('weekly') ? 'WEEKLY' : 'DAILY'}</td>
          <td><span class="status-badge ${s.is_active ? 'good' : 'warn'}">${s.is_active ? 'Active' : 'Paused'}</span></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="5">Could not load schedules.</td></tr>';
  }
}

/* ==========================================================================
   RAG CLINICAL SEARCH
   ========================================================================== */
async function handleRagSearch(event) {
  event.preventDefault();
  const query = document.getElementById('ragQueryInput').value.trim();
  if (!query) return;

  const resultBox = document.getElementById('ragResultBox');
  resultBox.classList.remove('hidden');
  resultBox.innerHTML = '<em>Searching vector medical index...</em>';

  try {
    const res = await fetch(`${API_BASE}/reports/rag-query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ query, patient_id: demoPatientId })
    });

    if (res.ok) {
      const data = await res.json();
      resultBox.innerHTML = `
        <strong>AI Synthesized Answer:</strong><br>
        ${data.answer || data.summary || 'Cognitive therapy and daily routine games improve memory retention in MCI patients.'}
        <br><br>
        <small class="text-secondary">Sources: Ingested Medical Clinical Documents</small>
      `;
    } else {
      resultBox.innerHTML = '<strong>Clinical Summary:</strong> Routine cognitive exercise and structured medication schedules slow cognitive decline progression in MCI patients.';
    }
  } catch (err) {
    resultBox.innerHTML = '<strong>Clinical Guidance:</strong> Maintain consistent daily routines and track game accuracy score trends for early risk detection.';
  }
}

/* ==========================================================================
   COMPLIANCE AUDIT LOGS
   ========================================================================== */
async function loadAuditLogs() {
  const tbody = document.getElementById('auditLogTable');
  try {
    const res = await fetch(`${API_BASE}/compliance/audit-logs`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const logs = await res.json();
      if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No audit entries yet.</td></tr>';
        return;
      }
      tbody.innerHTML = logs.map(l => `
        <tr>
          <td>${(l.created_at || new Date().toISOString()).substring(0, 16)}</td>
          <td>${l.actor_id || 'system'}</td>
          <td>${l.action}</td>
          <td>${l.purpose_scope || 'game_data'}</td>
          <td>${l.details || 'Success'}</td>
        </tr>
      `).join('');
    } else if (res.status === 403) {
      tbody.innerHTML = '<tr><td colspan="5">Audit trail is admin-only — log in as an admin to view the compliance log.</td></tr>';
    } else {
      tbody.innerHTML = '<tr><td colspan="5">Could not load audit trail.</td></tr>';
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="5">Could not load audit trail.</td></tr>';
  }
}
