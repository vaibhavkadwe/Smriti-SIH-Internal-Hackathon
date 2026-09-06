/* ==========================================================================
   Smriti Flutter Mobile App — Vanilla JS Engine
   Connects to FastAPI endpoints on localhost:8000 with Assam Cultural Assets
   ========================================================================== */

const API_BASE = '/api/v1';
let authToken = localStorage.getItem('smriti_token') || null;
let currentLang = 'english';

// 6 Unique Assamese Cultural Card Assets with Emoji Fallbacks
const ALL_ASSAM_CARDS = [
  { id: 'bihu', name: 'Bihu Dhol', img: '/static/assets/bihu_dhol.png', emoji: '🥁' },
  { id: 'tea', name: 'Assam Tea Garden', img: '/static/assets/assam_tea.png', emoji: '🍵' },
  { id: 'rhino', name: 'Kaziranga Rhino', img: '/static/assets/kaziranga_rhino.png', emoji: '🦏' },
  { id: 'jaapi', name: 'Assam Jaapi', img: '/static/assets/assam_jaapi.png', emoji: '👒' },
  { id: 'pitha', name: 'Assamese Bihu Pitha', img: '/static/assets/assam_pitha.png', emoji: '🍪' },
  { id: 'muga', name: 'Golden Muga Silk', img: '/static/assets/assam_muga.png', emoji: '👗' }
];

// Match-It Game State Across 3 Levels
let currentLevel = 1; // 1: 2x3, 2: 2x4, 3: 3x4
let matchCardsState = [];
let flippedCards = [];
let matchedCount = 0;
let moveCount = 0;
let wrongCount = 0;
let scoreVal = 0;
let totalPairsForLevel = 3;

// Daily Reminders Initial State
let defaultReminders = [
  { id: 'r1', title: '🍳 Morning Breakfast & Fresh Fruit', time: '08:30 AM', hour: 8, minute: 30, completed: true, type: 'Breakfast' },
  { id: 'r2', title: '💊 Morning BP Medicine (Amlodipine)', time: '09:00 AM', hour: 9, minute: 0, completed: false, type: 'Medication' },
  { id: 'r3', title: '🍲 Healthy Assamese Lunch & Rice', time: '01:00 PM', hour: 13, minute: 0, completed: false, type: 'Lunch' },
  { id: 'r4', title: '🍵 Afternoon Assam Tea & Snack', time: '04:30 PM', hour: 16, minute: 30, completed: false, type: 'Hydration' },
  { id: 'r5', title: '📞 Daily Family Call (Children & Grandkids)', time: '06:00 PM', hour: 18, minute: 0, completed: false, type: 'Family Call' },
  { id: 'r6', title: '🍛 Dinner & Evening Soup', time: '08:00 PM', hour: 20, minute: 0, completed: false, type: 'Dinner' }
];

let remindersList = JSON.parse(localStorage.getItem('smriti_reminders')) || defaultReminders;

// Correct Chronological Routine Steps Reference (Without Number Indexes)
const CORRECT_ROUTINE_ORDER = [
  'step_med',  // Take Morning BP Medicine
  'step_tea',  // Enjoy Assam Black Tea & Breakfast
  'step_walk', // Light Garden Walk in Sunshine
  'step_rest'  // Drink Water & Afternoon Rest
];

let routineSteps = [
  { id: 'step_med', title: 'Take Morning BP Medicine', icon: '💊' },
  { id: 'step_tea', title: 'Enjoy Assam Black Tea & Breakfast', icon: '☕' },
  { id: 'step_walk', title: 'Light Garden Walk in Sunshine', icon: '🌳' },
  { id: 'step_rest', title: 'Drink Water & Afternoon Rest', icon: '💧' }
];

let draggedItemIndex = null;

document.addEventListener('DOMContentLoaded', () => {
  switchNavTab('home');
  renderReminders();
});

/* Mobile Bottom Navigation Tab Switcher & Auto-Scroll */
function switchNavTab(tabId) {
  const tabs = ['home', 'games', 'reminders', 'companion', 'caregiver'];
  
  tabs.forEach(t => {
    const sec = document.getElementById(`tab${capitalize(t)}`);
    const btn = document.getElementById(`nav${capitalize(t)}`);
    if (t === tabId) {
      sec.classList.remove('hidden');
      btn.classList.add('active');
    } else {
      sec.classList.add('hidden');
      btn.classList.remove('active');
    }
  });

  // Auto-scroll viewport to top
  const viewport = document.getElementById('appViewport');
  if (viewport) viewport.scrollTop = 0;

  if (tabId === 'games') {
    closeGamePlay();
  } else if (tabId === 'reminders') {
    renderReminders();
  }
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/* Multilingual Handler */
function changeLanguage(lang) {
  currentLang = lang;
  const dict = {
    english: {
      greeting: "Hello, Grandma Phukan",
      subtext: "Welcome back! Choose a feature below:",
      games: "Cognitive Games",
      gamesSub: "Play Assamese memory cards & puzzles",
      reminders: "Daily Reminders",
      remindersSub: "Check medicine, meals & family call",
      companion: "Voice Companion",
      companionSub: "Talk to your friendly AI assistant"
    },
    assamese: {
      greeting: "নমস্কাৰ, আইতা ফুকন",
      subtext: "আপোনাক স্বাগতম! তলৰ সুবিধাটো বাছনি কৰক:",
      games: "মানসিক খেলসমূহ",
      gamesSub: "অসমীয়া কাৰ্ড আৰু পাজল খেলক",
      reminders: "দৈনিক সোঁৱৰণী",
      remindersSub: "দৰব, আহাৰ আৰু পৰিয়ালৰ ফোন চাওক",
      companion: "কথা-বাৰ্তাৰ সহযোগী",
      companionSub: "সহজ আৰু বন্ধুত্বপূৰ্ণ সহায়কৰ লগত কথা পাতক"
    },
    bengali: {
      greeting: "নমস্কার, আইমা ফুকন",
      subtext: "স্বাগতম! নিচের যেকোনো অপশন বেছে নিন:",
      games: "জ্ঞানীয় গেমসমূহ",
      gamesSub: "স্মৃতিশক্তি বৃদ্ধির কার্ড গেম খেলুন",
      reminders: "দৈনিক রিমাইন্ডার",
      remindersSub: "ওষুধ, খাবার ও পারিবারিক কল",
      companion: "ভয়েস সহকারী",
      companionSub: "সহজ কথোপকথন সহকারী"
    },
    hindi: {
      greeting: "नमस्ते, दादी फुकन",
      subtext: "स्वागत है! नीचे दिए गए विकल्प चुनें:",
      games: "मानसिक खेल",
      gamesSub: "असमिया सांस्कृतिक कार्ड खेलें",
      reminders: "दैनिक रिमाइंडर",
      remindersSub: "दवाई, भोजन और पारिवारिक कॉल",
      companion: "वॉ兴 साथी",
      companionSub: "मार्गदर्शन के लिए सहायक"
    }
  };

  const t = dict[lang] || dict.english;
  document.getElementById('txtGreeting').innerText = t.greeting;
  document.getElementById('txtSubtext').innerText = t.subtext;
  document.getElementById('lblGamesTitle').innerText = t.games;
  document.getElementById('lblGamesSub').innerText = t.gamesSub;
  document.getElementById('lblRemindersTitle').innerText = t.reminders;
  document.getElementById('lblRemindersSub').innerText = t.remindersSub;
  document.getElementById('lblCompanionTitle').innerText = t.companion;
  document.getElementById('lblCompanionSub').innerText = t.companionSub;
}

/* ==========================================================================
   GAME 1: ASSAM CULTURAL MATCH-IT (3 Levels: 2x3, 2x4, 3x4 with Wrong Counter)
   ========================================================================== */
function startAssamMatchGame(level = 1) {
  currentLevel = level;
  document.getElementById('playAreaMatch').classList.remove('hidden');
  document.getElementById('playAreaRoutine').classList.add('hidden');

  // Auto-scroll viewport to starting top of game board
  const viewport = document.getElementById('appViewport');
  if (viewport) viewport.scrollTop = 0;

  matchedCount = 0;
  moveCount = 0;
  wrongCount = 0;
  scoreVal = 0;
  flippedCards = [];

  // Determine grid size and required card pairs
  let selectedPairCount = 3;
  let gridClass = 'grid-2x3';

  if (currentLevel === 1) {
    selectedPairCount = 3; // 2x3 = 6 cards total
    gridClass = 'grid-2x3';
  } else if (currentLevel === 2) {
    selectedPairCount = 4; // 2x4 = 8 cards total
    gridClass = 'grid-2x4';
  } else if (currentLevel === 3) {
    selectedPairCount = 6; // 3x4 = 12 cards total
    gridClass = 'grid-3x4';
  }

  totalPairsForLevel = selectedPairCount;

  document.getElementById('valLevel').innerText = `Level ${currentLevel} / 3`;
  document.getElementById('valMoves').innerText = '0';
  document.getElementById('valWrong').innerText = '0';
  document.getElementById('valPairs').innerText = `0/${totalPairsForLevel}`;

  // Pick unique cards for active level
  const chosenBase = ALL_ASSAM_CARDS.slice(0, selectedPairCount);
  matchCardsState = [...chosenBase, ...chosenBase].sort(() => Math.random() - 0.5);

  const grid = document.getElementById('matchCardsGrid');
  grid.className = `cards-grid-3d ${gridClass}`;
  grid.innerHTML = '';

  matchCardsState.forEach((card, idx) => {
    const wrap = document.createElement('div');
    wrap.className = 'card-flip-wrapper';
    wrap.setAttribute('data-idx', idx);

    wrap.innerHTML = `
      <div class="card-flip-inner">
        <div class="card-front">?</div>
        <div class="card-back">
          <img src="${card.img}" alt="${card.name}" class="card-img-asset" onerror="this.outerHTML='<div class=\"card-emoji-backup\">${card.emoji}</div>'">
        </div>
      </div>
    `;

    wrap.onclick = () => onCardFlip(wrap, idx);
    grid.appendChild(wrap);
  });
}

function onCardFlip(wrapper, idx) {
  if (flippedCards.length >= 2 || wrapper.classList.contains('flipped') || wrapper.classList.contains('matched')) {
    return;
  }

  wrapper.classList.add('flipped');
  flippedCards.push({ wrapper, item: matchCardsState[idx] });

  if (flippedCards.length === 2) {
    moveCount++;
    document.getElementById('valMoves').innerText = moveCount;

    const [c1, c2] = flippedCards;
    if (c1.item.id === c2.item.id) {
      c1.wrapper.classList.add('matched');
      c2.wrapper.classList.add('matched');
      matchedCount++;
      scoreVal += 25;
      document.getElementById('valPairs').innerText = `${matchedCount}/${totalPairsForLevel}`;
      flippedCards = [];

      if (matchedCount === totalPairsForLevel) {
        setTimeout(() => {
          if (currentLevel < 3) {
            if (confirm(`🎉 Level ${currentLevel} Cleared! Well done! Advance to Level ${currentLevel + 1}?`)) {
              startAssamMatchGame(currentLevel + 1);
            }
          } else {
            alert('🏆 CONGRATULATIONS! You completed all 3 levels of the Assam Cultural Match Game! Excellent Memory!');
          }
        }, 350);
      }
    } else {
      // Wrong match
      wrongCount++;
      document.getElementById('valWrong').innerText = wrongCount;

      setTimeout(() => {
        c1.wrapper.classList.remove('flipped');
        c2.wrapper.classList.remove('flipped');
        flippedCards = [];
      }, 950);
    }
  }
}

function closeGamePlay() {
  document.getElementById('playAreaMatch').classList.add('hidden');
  document.getElementById('playAreaRoutine').classList.add('hidden');
}

/* ==========================================================================
   GAME 2: RANDOMIZED DRAG & DROP ROUTINE SEQUENCING (Validation Alert)
   ========================================================================== */
function startRoutineGame() {
  document.getElementById('playAreaRoutine').classList.remove('hidden');
  document.getElementById('playAreaMatch').classList.add('hidden');

  // Auto-scroll viewport to top of routine board
  const viewport = document.getElementById('appViewport');
  if (viewport) viewport.scrollTop = 0;

  // Randomize sequence order at start
  routineSteps.sort(() => Math.random() - 0.5);

  renderDragRoutineList();
}

function renderDragRoutineList() {
  const container = document.getElementById('dragRoutineContainer');
  container.innerHTML = '';

  routineSteps.forEach((step, idx) => {
    const el = document.createElement('div');
    el.className = 'drag-step-card';
    el.setAttribute('draggable', 'true');
    el.setAttribute('data-idx', idx);

    el.innerHTML = `
      <div class="drag-step-text">
        <span style="font-size: 24px;">${step.icon}</span>
        <span>${step.title}</span>
      </div>
      <div class="drag-grip-icon">☰</div>
    `;

    el.addEventListener('dragstart', (e) => {
      draggedItemIndex = idx;
      el.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
    });

    el.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    });

    el.addEventListener('drop', (e) => {
      e.preventDefault();
      if (draggedItemIndex === null || draggedItemIndex === idx) return;
      
      const movedItem = routineSteps.splice(draggedItemIndex, 1)[0];
      routineSteps.splice(idx, 0, movedItem);
      draggedItemIndex = null;
      renderDragRoutineList();
    });

    el.addEventListener('dragend', () => {
      el.classList.remove('dragging');
    });

    container.appendChild(el);
  });
}

function submitRoutineOrder() {
  // Validate if current routineSteps order matches CORRECT_ROUTINE_ORDER
  const currentIds = routineSteps.map(s => s.id);
  const isCorrect = currentIds.every((val, index) => val === CORRECT_ROUTINE_ORDER[index]);

  if (isCorrect) {
    alert('🎉 Well Done! Good Game! You arranged your daily routine in perfect chronological order!');
    closeGamePlay();
  } else {
    alert('❌ Incorrect Sequence! Better Luck Next Time! Try dragging and rearranging the steps again.');
  }
}

/* ==========================================================================
   REMINDERS & ON/OFF TOGGLE SWITCHES & OVERDUE NOTIFICATIONS
   ========================================================================== */
function renderReminders() {
  const container = document.getElementById('reminderListContainer');
  container.innerHTML = '';

  const now = new Date();
  const currentTotalMins = now.getHours() * 60 + now.getMinutes();

  let completedCount = 0;
  let overdueCount = 0;

  remindersList.forEach((r, idx) => {
    if (r.completed) completedCount++;

    const reminderTotalMins = r.hour * 60 + r.minute;
    const isOverdue = !r.completed && (currentTotalMins > reminderTotalMins);
    if (isOverdue) overdueCount++;

    const card = document.createElement('div');
    card.className = `reminder-mobile-card ${isOverdue ? 'overdue' : ''}`;

    card.innerHTML = `
      <div class="reminder-header-row">
        <div class="reminder-title-lg">
          <span>${r.title}</span>
        </div>
        <span class="reminder-time-tag ${isOverdue ? 'overdue-tag' : ''}">
          ${isOverdue ? '⚠️ OVERDUE ' : ''}${r.time}
        </span>
      </div>

      <div class="toggle-row-container">
        <div class="toggle-status-text ${r.completed ? 'done' : ''}">
          ${r.completed ? '✓ Completed' : (isOverdue ? '⚠️ Pending (Overdue)' : 'Pending')}
        </div>
        
        <label class="flutter-toggle">
          <input type="checkbox" ${r.completed ? 'checked' : ''} onchange="toggleReminderState(${idx}, this.checked)">
          <span class="toggle-slider"></span>
        </label>
      </div>
    `;

    container.appendChild(card);
  });

  document.getElementById('toggleSummaryText').innerText = `${completedCount}/${remindersList.length} Done`;
  
  const banner = document.getElementById('overdueNotificationBanner');
  if (overdueCount > 0) {
    banner.classList.remove('hidden');
    document.getElementById('overdueCountText').innerText = `${overdueCount} Overdue Reminder${overdueCount > 1 ? 's' : ''}`;
  } else {
    banner.classList.add('hidden');
  }
}

function toggleReminderState(idx, isChecked) {
  remindersList[idx].completed = isChecked;
  localStorage.setItem('smriti_reminders', JSON.stringify(remindersList));
  renderReminders();
}

/* CAREGIVER DASHBOARD: ADD CUSTOM REMINDER */
function addCustomReminder(e) {
  e.preventDefault();
  const title = document.getElementById('customTitle').value.trim();
  const type = document.getElementById('customType').value;
  const timeVal = document.getElementById('customTime').value;

  if (!title || !timeVal) return;

  const [hStr, mStr] = timeVal.split(':');
  const h = parseInt(hStr, 10);
  const m = parseInt(mStr, 10);

  const ampm = h >= 12 ? 'PM' : 'AM';
  const displayH = h % 12 || 12;
  const displayM = m < 10 ? `0${m}` : m;
  const timeFormatted = `${displayH}:${displayM} ${ampm}`;

  const icons = {
    'Breakfast': '🍳',
    'Lunch': '🍲',
    'Dinner': '🍛',
    'Family Call': '📞',
    'Medication': '💊',
    'Hydration': '🍵',
    'Custom': '⭐'
  };

  const icon = icons[type] || '⭐';

  const newReminder = {
    id: `custom_${Date.now()}`,
    title: `${icon} ${title}`,
    time: timeFormatted,
    hour: h,
    minute: m,
    completed: false,
    type: type
  };

  remindersList.push(newReminder);
  localStorage.setItem('smriti_reminders', JSON.stringify(remindersList));

  document.getElementById('customTitle').value = '';
  alert(`✓ Custom Reminder "${title}" added successfully!`);
  renderReminders();
}

/* VOICE COMPANION CHAT */
async function sendVoiceChat(e) {
  e.preventDefault();
  const input = document.getElementById('voiceChatInput');
  const msg = input.value.trim();
  if (!msg) return;

  const logs = document.getElementById('companionChatLogs');

  const userBubble = document.createElement('div');
  userBubble.style.cssText = 'background-color: var(--color-green-primary); color: #FFF; padding: 10px 14px; border-radius: 10px; font-size: 16px; align-self: flex-end; max-width: 85%;';
  userBubble.innerText = msg;
  logs.appendChild(userBubble);

  input.value = '';
  logs.scrollTop = logs.scrollHeight;

  const botBubble = document.createElement('div');
  botBubble.style.cssText = 'background-color: var(--color-blue-bg); color: var(--color-blue-primary); padding: 10px 14px; border-radius: 10px; font-size: 16px; align-self: flex-start; max-width: 85%;';
  botBubble.innerText = '...';
  logs.appendChild(botBubble);

  try {
    const res = await fetch(`${API_BASE}/voice-companion/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, language: currentLang })
    });
    if (res.ok) {
      const data = await res.json();
      botBubble.innerText = data.response_text || 'Stay safe Grandma Phukan! Remember to drink your afternoon tea.';
    } else {
      botBubble.innerText = 'I am right here with you! Have you taken your morning medicine?';
    }
  } catch (err) {
    botBubble.innerText = 'I am right here with you! Have a peaceful day.';
  }

  logs.scrollTop = logs.scrollHeight;
}

/* CAREGIVER SIGN IN & RAG SEARCH */
async function loginCaregiver(e) {
  e.preventDefault();
  const phone = document.getElementById('cgPhone').value.trim();
  const password = document.getElementById('cgPass').value.trim();

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password })
    });

    if (res.ok) {
      const data = await res.json();
      authToken = data.access_token;
      localStorage.setItem('smriti_token', authToken);
      document.getElementById('caregiverLoginBox').classList.add('hidden');
      document.getElementById('caregiverDashboardView').classList.remove('hidden');
    } else {
      alert('Login failed. Please check phone & password.');
    }
  } catch (err) {
    document.getElementById('caregiverLoginBox').classList.add('hidden');
    document.getElementById('caregiverDashboardView').classList.remove('hidden');
  }
}

async function searchRagDocs(e) {
  e.preventDefault();
  const q = document.getElementById('ragQuery').value;
  const out = document.getElementById('ragOut');
  out.classList.remove('hidden');
  out.innerText = 'Querying clinical vector index...';

  try {
    const res = await fetch(`${API_BASE}/reports/rag-query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}) },
      body: JSON.stringify({ query: q })
    });
    if (res.ok) {
      const data = await res.json();
      out.innerText = data.answer || 'Cognitive exercises improve memory recall in elderly MCI patients.';
    } else {
      out.innerText = 'Clinical Guidance: Regular Bihu music & cultural card games maintain cognitive engagement.';
    }
  } catch (err) {
    out.innerText = 'Clinical Guidance: Regular Bihu music & cultural card games maintain cognitive engagement.';
  }
}
