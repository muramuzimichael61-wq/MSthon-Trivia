const QUESTION_SECONDS = 15;
const ROUND_SIZE = 10;
const TIMER_CIRCUMFERENCE = 50.27;

const state = {
  questions: [],
  index: 0,
  score: 0,
  streak: 0,
  bestStreak: 0,
  category: "All",
  secondsLeft: QUESTION_SECONDS,
  timer: null,
  advanceTimer: null,
  locked: false,
  adminToken: "",
  installPrompt: null,
  room: null,
  roomPollTimer: null,
  roomBusy: false,
};

const content = document.querySelector("#quiz-content");
const categorySelect = document.querySelector("#category-select");
const topicList = document.querySelector("#topic-list");
const adminDialog = document.querySelector("#admin-dialog");
const adminMessage = document.querySelector("#admin-message");
const toast = document.querySelector("#toast");

async function api(path, options = {}) {
  const response = await fetch(path, {
    cache: "no-store",
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...options.headers,
    },
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function setMessage(element, text, isError = false) {
  element.textContent = text;
  element.classList.toggle("error", isError);
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove("visible"), 2400);
}

async function loadMetadata() {
  const metadata = await api("/api/meta");
  categorySelect.replaceChildren(new Option("All topics", "All"));
  topicList.replaceChildren();
  addTopic("All", "Everything", "✳");
  metadata.categories.forEach((category, index) => {
    categorySelect.add(new Option(category, category));
    addTopic(category, category, ["⌘", "</>", "◇", "⚙", "λ", "✳"][index % 6]);
  });
  categorySelect.value = state.category;
  document.querySelector("#question-count").textContent =
    `${metadata.question_count} QUESTIONS IN THE BANK`;
  const roomCategory = document.querySelector("#room-category");
  const selectedRoomCategory = roomCategory.value || "All";
  roomCategory.replaceChildren(new Option("All topics", "All"));
  metadata.categories.forEach((category) => roomCategory.add(new Option(category, category)));
  roomCategory.value = metadata.categories.includes(selectedRoomCategory) || selectedRoomCategory === "All"
    ? selectedRoomCategory
    : "All";
}

function addTopic(value, label, icon) {
  const chip = document.createElement("button");
  chip.type = "button";
  chip.className = `topic-chip${value === state.category ? " selected" : ""}`;
  chip.dataset.topic = value;
  chip.innerHTML = `${icon} <span>${escapeHtml(label)}</span>`;
  chip.addEventListener("click", () => selectCategory(value));
  topicList.append(chip);
}

function selectCategory(category) {
  if (state.category === category) return;
  state.category = category;
  categorySelect.value = category;
  topicList.querySelectorAll(".topic-chip").forEach((chip) => {
    chip.classList.toggle("selected", chip.dataset.topic === category);
  });
  stopTimers();
  state.locked = false;
  state.questions = [];
  renderWelcome();
}

function stopTimers() {
  window.clearInterval(state.timer);
  window.clearTimeout(state.advanceTimer);
  state.timer = null;
  state.advanceTimer = null;
}

function renderWelcome() {
  document.querySelector("#round-label").textContent = "— / 10";
  document.querySelector("#progress-bar").style.width = "0%";
  content.innerHTML = `
    <div class="question-meta"><span class="tag">${escapeHtml(state.category === "All" ? "All topics" : state.category)}</span><span class="tag difficulty">15 SEC / QUESTION</span></div>
    <h3 class="question-prompt">A little curiosity goes a long way. Ready to put your code knowledge to the test?</h3>
    <p style="color:#aaa6b2;font-size:11px;line-height:1.7;margin:-7px 0 13px">Ten questions. Fifteen seconds each. Learn something new along the way.</p>
    <div class="quiz-actions"><button class="button button-primary" id="start-button">Let's play <span>→</span></button><span class="timer-wrap">✳&nbsp; No pressure, just progress</span></div>`;
  document.querySelector("#start-button").addEventListener("click", startRound);
}

async function startRound() {
  stopTimers();
  state.locked = true;
  content.innerHTML = '<div class="loading-state"><span class="loader"></span><p>Finding your next challenge…</p></div>';
  try {
    const result = await api(`/api/questions?category=${encodeURIComponent(state.category)}&limit=${ROUND_SIZE}`);
    if (!result.questions.length) throw new Error("There are no questions in this topic yet. Try another topic.");
    state.questions = result.questions;
    state.index = 0;
    state.score = 0;
    state.streak = 0;
    updateScore();
    renderQuestion();
  } catch (error) {
    state.locked = false;
    content.innerHTML = `<div class="loading-state"><p>${escapeHtml(error.message)}</p></div><div class="quiz-actions"><button class="button button-primary" id="retry-button">Try again <span>↻</span></button></div>`;
    document.querySelector("#retry-button").addEventListener("click", renderWelcome);
  }
}

function updateScore() {
  document.querySelector("#score-display").innerHTML = `${state.score}<span> pts</span>`;
  document.querySelector("#streak-display").innerHTML = `${state.bestStreak} <small>in a row</small>`;
}

function renderQuestion() {
  stopTimers();
  state.locked = false;
  state.secondsLeft = QUESTION_SECONDS;
  const item = state.questions[state.index];
  const number = state.index + 1;
  document.querySelector("#round-label").textContent = `${number} / ${state.questions.length}`;
  document.querySelector("#progress-bar").style.width = `${((number - 1) / state.questions.length) * 100}%`;
  content.innerHTML = `
    <div class="question-meta"><span class="tag">${escapeHtml(item.category)}</span><span class="tag difficulty">${escapeHtml(item.difficulty)}</span></div>
    <h3 class="question-prompt">${escapeHtml(item.question)}</h3>
    <div class="answer-list">${item.options.map((option, index) => `
      <button type="button" class="answer-option" data-answer="${index}">
        <span class="answer-key">${index + 1}</span><span>${escapeHtml(option)}</span>
      </button>`).join("")}
    </div>
    <div class="feedback-row"><span id="feedback-text">Trust your instincts.</span><span class="timer-wrap" id="timer-wrap"><svg class="timer-ring" viewBox="0 0 20 20" aria-hidden="true"><circle class="track" cx="10" cy="10" r="8"></circle><circle class="value" id="timer-ring" cx="10" cy="10" r="8"></circle></svg><span id="timer-value">${QUESTION_SECONDS}s</span></span></div>`;
  content.querySelectorAll(".answer-option").forEach((button) => {
    button.addEventListener("click", () => submitAnswer(Number(button.dataset.answer)));
  });
  state.timer = window.setInterval(tick, 100);
}

function tick() {
  state.secondsLeft = Math.max(0, state.secondsLeft - 0.1);
  const remaining = Math.ceil(state.secondsLeft);
  const ring = document.querySelector("#timer-ring");
  const timerWrap = document.querySelector("#timer-wrap");
  const timerValue = document.querySelector("#timer-value");
  if (!ring || !timerWrap || !timerValue) return;
  ring.style.strokeDasharray = TIMER_CIRCUMFERENCE;
  ring.style.strokeDashoffset = `${TIMER_CIRCUMFERENCE * (1 - state.secondsLeft / QUESTION_SECONDS)}`;
  timerValue.textContent = `${remaining}s`;
  timerWrap.classList.toggle("is-low", remaining <= 5);
  if (state.secondsLeft <= 0) {
    stopTimers();
    state.locked = true;
    state.streak = 0;
    updateScore();
    content.querySelectorAll(".answer-option").forEach((button) => { button.disabled = true; });
    const feedback = document.querySelector("#feedback-text");
    feedback.innerHTML = "<strong class=\"wrong\">Time's up!</strong> The next one is yours.";
    state.advanceTimer = window.setTimeout(nextQuestion, 1400);
  }
}

async function submitAnswer(answer) {
  if (state.locked) return;
  state.locked = true;
  stopTimers();
  const item = state.questions[state.index];
  content.querySelectorAll(".answer-option").forEach((button) => { button.disabled = true; });
  try {
    const result = await api("/api/answer", {
      method: "POST",
      body: JSON.stringify({ question_id: item.id, answer }),
    });
    const buttons = [...content.querySelectorAll(".answer-option")];
    buttons[result.correct_answer].classList.add("is-correct");
    if (!result.correct) {
      buttons[answer].classList.add("is-wrong");
      state.streak = 0;
    } else {
      state.score += 100;
      state.streak += 1;
      state.bestStreak = Math.max(state.bestStreak, state.streak);
    }
    updateScore();
    const feedback = document.querySelector("#feedback-text");
    const response = result.correct
      ? "<strong>That's right! +100 points</strong>"
      : "<strong class=\"wrong\">Not quite.</strong>";
    feedback.innerHTML = `${response}${result.explanation ? ` <span class="explanation">${escapeHtml(result.explanation)}</span>` : ""}`;
    state.advanceTimer = window.setTimeout(nextQuestion, 1800);
  } catch (error) {
    state.locked = false;
    showToast(error.message);
    state.timer = window.setInterval(tick, 100);
  }
}

function nextQuestion() {
  if (state.index + 1 < state.questions.length) {
    state.index += 1;
    renderQuestion();
  } else {
    renderResults();
  }
}

function renderResults() {
  stopTimers();
  state.locked = true;
  document.querySelector("#round-label").textContent = `${state.questions.length} / ${state.questions.length}`;
  document.querySelector("#progress-bar").style.width = "100%";
  const correct = state.score / 100;
  const message = correct >= 8 ? "Brilliant work." : correct >= 5 ? "Nice momentum." : "Every round makes you sharper.";
  content.innerHTML = `
    <div class="question-meta"><span class="tag">ROUND COMPLETE</span><span class="tag difficulty">${correct} / ${state.questions.length} CORRECT</span></div>
    <h3 class="question-prompt">${message}</h3>
    <p style="color:#aaa6b2;font-size:12px;line-height:1.7">You scored <strong style="color:#c6b2ff">${state.score} points</strong> and built a best streak of <strong style="color:#c6b2ff">${state.bestStreak}</strong>. Keep going — the question bank keeps growing.</p>
    <div class="quiz-actions"><button class="button button-primary" id="play-again-button">Play another round <span>→</span></button><span class="timer-wrap">✳&nbsp; Nice work showing up</span></div>`;
  document.querySelector("#play-again-button").addEventListener("click", startRound);
}

categorySelect.addEventListener("change", (event) => selectCategory(event.target.value));
document.querySelector("#admin-open").addEventListener("click", openAdmin);
document.querySelector("#footer-admin").addEventListener("click", openAdmin);
document.querySelector("#admin-close").addEventListener("click", () => adminDialog.close());

function openAdmin() {
  setMessage(adminMessage, "");
  adminDialog.showModal();
  document.querySelector(state.adminToken ? "#new-question" : "#admin-password").focus();
}

document.querySelector("#admin-login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const password = new FormData(event.currentTarget).get("password");
  setMessage(adminMessage, "Signing in…");
  try {
    const result = await api("/api/admin/login", {
      method: "POST",
      body: JSON.stringify({ password }),
    });
    state.adminToken = result.token;
    document.querySelector("#admin-login-panel").hidden = true;
    document.querySelector("#admin-editor-panel").hidden = false;
    setMessage(adminMessage, "You're signed in. Add a new question below.");
    document.querySelector("#new-question").focus();
  } catch (error) {
    setMessage(adminMessage, error.message, true);
  }
});

document.querySelector("#question-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {
    question: form.get("question"),
    options: [0, 1, 2, 3].map((index) => form.get(`option${index}`)),
    correct_answer: Number(form.get("correct_answer")),
    category: form.get("category"),
    difficulty: form.get("difficulty"),
    explanation: form.get("explanation"),
  };
  setMessage(adminMessage, "Saving question…");
  try {
    await api("/api/admin/questions", {
      method: "POST",
      token: state.adminToken,
      body: JSON.stringify(payload),
    });
    event.currentTarget.reset();
    await loadMetadata();
    setMessage(adminMessage, "Question added to the live bank. It will appear in a new round.");
    showToast("New question added to Myk!");
  } catch (error) {
    if (error.message === "Admin sign-in required.") {
      state.adminToken = "";
      document.querySelector("#admin-login-panel").hidden = false;
      document.querySelector("#admin-editor-panel").hidden = true;
    }
    setMessage(adminMessage, error.message, true);
  }
});

document.addEventListener("keydown", (event) => {
  if (adminDialog.open || event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.target instanceof HTMLElement && event.target.closest("button, input, textarea, select, a")) return;
  if (event.key === "Enter" && !state.questions.length) {
    event.preventDefault();
    startRound();
  } else if (/^[1-4]$/.test(event.key) && !state.locked && state.questions.length) {
    submitAnswer(Number(event.key) - 1);
  }
});

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  state.installPrompt = event;
  document.querySelector("#install-button").hidden = false;
});
document.querySelector("#install-button").addEventListener("click", async () => {
  if (!state.installPrompt) return;
  state.installPrompt.prompt();
  await state.installPrompt.userChoice;
  state.installPrompt = null;
  document.querySelector("#install-button").hidden = true;
});
window.addEventListener("appinstalled", () => showToast("Myk Quiz is installed and ready!"));

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/sw.js").catch((error) => {
    console.error("Service worker registration failed:", error);
  }));
}

loadMetadata().then(renderWelcome).catch((error) => {
  content.innerHTML = `<div class="loading-state"><p>${escapeHtml(error.message)} Check that the Myk server is running, then refresh.</p></div>`;
});

const roomDialog = document.querySelector("#room-dialog");
const roomEntry = document.querySelector("#room-entry");
const roomSession = document.querySelector("#room-session");
const roomEntryMessage = document.querySelector("#room-entry-message");
const roomSessionMessage = document.querySelector("#room-session-message");

function saveRoomCredentials() {
  if (state.room) {
    sessionStorage.setItem("myk-room", JSON.stringify({
      code: state.room.code,
      token: state.room.token,
      role: state.room.role,
      name: state.room.name || "",
    }));
  } else {
    sessionStorage.removeItem("myk-room");
  }
}

function showRoomEntry(message = "") {
  stopRoomPolling();
  state.room = null;
  saveRoomCredentials();
  roomEntry.hidden = false;
  roomSession.hidden = true;
  setMessage(roomEntryMessage, message, Boolean(message));
}

function stopRoomPolling() {
  window.clearInterval(state.roomPollTimer);
  state.roomPollTimer = null;
}

function openRoomDialog() {
  if (state.room) {
    roomEntry.hidden = true;
    roomSession.hidden = false;
    startRoomPolling();
  } else {
    roomEntry.hidden = false;
    roomSession.hidden = true;
    const joinCode = new URLSearchParams(window.location.search).get("join");
    if (joinCode) {
      document.querySelector("#join-code").value = joinCode.toUpperCase();
      document.querySelector('[data-panel="join-panel"]').click();
    }
  }
  roomDialog.showModal();
}

document.querySelector("#room-open").addEventListener("click", openRoomDialog);
document.querySelector("#room-close").addEventListener("click", () => roomDialog.close());
document.querySelectorAll(".room-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".room-tab").forEach((item) => item.classList.toggle("selected", item === tab));
    document.querySelectorAll("[data-room-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.roomPanel !== tab.dataset.panel;
      panel.classList.toggle("active", !panel.hidden);
    });
    setMessage(roomEntryMessage, "");
  });
});

document.querySelector("#open-question-studio").addEventListener("click", () => {
  roomDialog.close();
  window.setTimeout(openAdmin, 0);
});

document.querySelector("#room-host-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  setMessage(roomEntryMessage, "Creating your room…");
  try {
    const result = await api("/api/rooms", {
      method: "POST",
      body: JSON.stringify({
        category: form.get("category"),
        question_count: Number(form.get("question_count")),
      }),
    });
    state.room = { code: result.code, token: result.token, role: "host", snapshot: null };
    saveRoomCredentials();
    startRoomPolling();
  } catch (error) {
    setMessage(roomEntryMessage, error.message, true);
  }
});

document.querySelector("#room-join-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  setMessage(roomEntryMessage, "Joining your room…");
  try {
    const result = await api("/api/rooms/join", {
      method: "POST",
      body: JSON.stringify({ code: form.get("code"), name: form.get("name") }),
    });
    state.room = { code: result.code, token: result.token, role: "player", name: form.get("name"), snapshot: null };
    saveRoomCredentials();
    startRoomPolling();
  } catch (error) {
    setMessage(roomEntryMessage, error.message, true);
  }
});

function startRoomPolling() {
  roomEntry.hidden = true;
  roomSession.hidden = false;
  setMessage(roomSessionMessage, "");
  refreshRoom();
  stopRoomPolling();
  state.roomPollTimer = window.setInterval(refreshRoom, 1000);
}

async function refreshRoom() {
  if (!state.room || state.roomBusy) return;
  try {
    const snapshot = await api(`/api/rooms/${encodeURIComponent(state.room.code)}`, {
      token: state.room.token,
    });
    state.room.snapshot = snapshot;
    renderRoom(snapshot);
    setMessage(roomSessionMessage, "");
  } catch (error) {
    if (error.message.includes("Room not found") || error.message.includes("not signed in")) {
      stopRoomPolling();
      showRoomEntry(error.message);
    } else {
      setMessage(roomSessionMessage, `${error.message} Reconnecting…`, true);
    }
  }
}

function renderRoom(snapshot) {
  const header = document.querySelector("#room-session-header");
  const body = document.querySelector("#room-session-content");
  if (snapshot.role === "host") {
    const joinUrl = `${window.location.origin}${window.location.pathname}?join=${encodeURIComponent(snapshot.code)}`;
    header.innerHTML = `
      <span class="room-role">YOU'RE THE HOST</span>
      <div class="room-code-row"><div><small>SHARE THIS ROOM CODE</small><strong>${escapeHtml(snapshot.code)}</strong></div><button class="button button-quiet copy-code" type="button">Copy invite</button></div>
      <div class="room-share-link">${escapeHtml(joinUrl)}</div>`;
    header.querySelector(".copy-code").addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(joinUrl);
        showToast("Room invite link copied.");
      } catch {
        await navigator.clipboard.writeText(snapshot.code).catch(() => {});
        showToast("Room code: " + snapshot.code);
      }
    });
  } else {
    header.innerHTML = `<span class="room-role">YOU'RE PLAYING AS</span><div class="player-name-banner">${escapeHtml(state.room.name || "Player")} <span>· room ${escapeHtml(snapshot.code)}</span></div>`;
  }

  if (snapshot.status === "lobby") {
    body.innerHTML = `
      <div class="lobby-status"><span class="live-dot"></span> WAITING FOR THE HOST</div>
      <h3 class="room-question-title">The quiz is about to begin.</h3>
      <p class="dialog-intro">${snapshot.total} questions · 15 seconds each · ${snapshot.players.length} player${snapshot.players.length === 1 ? "" : "s"} joined</p>
      ${snapshot.role === "host" ? `<div class="player-roster">${roomPlayerRows(snapshot.players, true)}</div><button class="button button-primary form-submit host-action" data-action="start">Start the quiz <span>→</span></button>` : `<div class="waiting-card">You're in! Keep this screen open. Your host will start soon.</div>`}`;
  } else if (snapshot.status === "finished") {
    body.innerHTML = `
      <div class="lobby-status"><span class="live-dot"></span> QUIZ COMPLETE</div>
      <h3 class="room-question-title">${snapshot.role === "host" ? "Final leaderboard." : "That's the last question."}</h3>
      ${snapshot.role === "player" ? `<div class="result-banner ${snapshot.score ? "passed" : "missed"}">YOUR FINAL SCORE <strong>${snapshot.score} pts</strong></div>` : ""}
      <div class="player-roster">${roomPlayerRows(snapshot.players, true)}</div>
      ${snapshot.role === "host" ? `<button class="button button-primary form-submit host-action" data-action="restart">Close room</button>` : ""}`;
  } else {
    const item = snapshot.question;
    const hasAnswer = Boolean(snapshot.my_answer);
    const timedOut = snapshot.remaining_seconds <= 0;
    const showOptions = snapshot.role === "player" && !hasAnswer && !timedOut;
    const feedback = snapshot.role === "player"
      ? hasAnswer
        ? `<div class="result-banner ${snapshot.my_answer.correct ? "passed" : "missed"}">${snapshot.my_answer.correct ? "PASSED — CORRECT ANSWER" : "NOT PASSED — TRY THE NEXT ONE"}<strong>${snapshot.my_answer.correct ? "+100 pts" : "0 pts"}</strong>${snapshot.my_answer.correct_answer !== undefined ? `<span>Correct answer: ${escapeHtml(item.options[snapshot.my_answer.correct_answer])}</span>` : ""}</div>`
        : timedOut
          ? `<div class="result-banner missed">TIME'S UP — QUESTION NOT PASSED<span>Wait for the host to reveal the next question.</span>${item.correct_answer !== undefined ? `<span>Correct answer: ${escapeHtml(item.options[item.correct_answer])}</span>` : ""}</div>`
          : ""
      : `<div class="room-clock">${timedOut ? "TIME UP — ADVANCE WHEN READY" : `${snapshot.remaining_seconds}s remaining`}</div>`;
    body.innerHTML = `
      <div class="lobby-status"><span class="live-dot"></span> QUESTION ${snapshot.index + 1} OF ${snapshot.total}<span class="room-clock">${snapshot.role === "player" ? `${snapshot.remaining_seconds}s` : ""}</span></div>
      <span class="tag">${escapeHtml(item.category)} · ${escapeHtml(item.difficulty)}</span>
      <h3 class="room-question-title">${escapeHtml(item.question)}</h3>
      <div class="room-options">${item.options.map((option, index) => {
          const revealedAnswer = item.correct_answer ?? (snapshot.my_answer && snapshot.my_answer.correct_answer);
          const isChosenWrong = hasAnswer && snapshot.my_answer.answer === index && !snapshot.my_answer.correct;
          const correctOption = revealedAnswer === index;
          return `<button type="button" class="room-option${correctOption ? " option-correct" : ""}${isChosenWrong ? " option-wrong" : ""}" ${showOptions ? `data-room-answer="${index}"` : "disabled"}><span>${index + 1}</span>${escapeHtml(option)}</button>`;
      }).join("")}</div>
      ${feedback}
      ${snapshot.role === "host" ? `<div class="player-roster">${roomPlayerRows(snapshot.players, timedOut)}</div><button class="button button-primary form-submit host-action" data-action="next">${snapshot.index + 1 >= snapshot.total ? "Finish quiz" : "Next question"} <span>→</span></button>` : `<div class="result-banner player-score-line">YOUR SCORE <strong>${snapshot.score} pts</strong></div>`}
      ${snapshot.question.explanation && snapshot.revealed && snapshot.role === "host" ? `<p class="room-explanation">${escapeHtml(snapshot.question.explanation)}</p>` : ""}`;
  }

  body.querySelectorAll(".host-action").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.action === "restart") {
        showRoomEntry("Room closed. You can start a new quiz whenever you're ready.");
        return;
      }
      runHostAction(button.dataset.action);
    });
  });
  body.querySelectorAll("[data-room-answer]").forEach((button) => {
    button.addEventListener("click", () => submitRoomAnswer(Number(button.dataset.roomAnswer)));
  });
}

function roomPlayerRows(players, showResults) {
  if (!players.length) return '<div class="waiting-card">No players yet. Share the code to invite your crowd.</div>';
  return `<div class="roster-heading">${showResults ? "PLAYERS" : "IN THE ROOM"} <span>${players.length}</span></div><div class="roster-list">${players.map((player, index) => {
    const status = player.passed === true ? '<span class="roster-passed">PASSED</span>'
      : player.passed === false ? '<span class="roster-missed">NOT PASSED</span>'
        : showResults && !player.answered ? '<span class="roster-waiting">NO ANSWER</span>'
          : player.answered ? '<span class="roster-waiting">ANSWERED</span>'
            : '<span class="roster-waiting">THINKING…</span>';
    return `<div class="roster-row"><span class="roster-rank">${index + 1}</span><span class="roster-name">${escapeHtml(player.name)}</span>${status}<strong>${player.score} <small>pts</small></strong></div>`;
  }).join("")}</div>`;
}

async function runHostAction(action) {
  if (!state.room || state.roomBusy) return;
  state.roomBusy = true;
  try {
    await api(`/api/rooms/${encodeURIComponent(state.room.code)}/${action}`, {
      method: "POST",
      token: state.room.token,
      body: JSON.stringify({}),
    });
    await refreshRoom();
  } catch (error) {
    setMessage(roomSessionMessage, error.message, true);
  } finally {
    state.roomBusy = false;
  }
}

async function submitRoomAnswer(answer) {
  if (!state.room || state.roomBusy) return;
  state.roomBusy = true;
  try {
    const result = await api(`/api/rooms/${encodeURIComponent(state.room.code)}/answer`, {
      method: "POST",
      token: state.room.token,
      body: JSON.stringify({ answer }),
    });
    showToast(result.correct ? "Passed! +100 points" : "Not passed — keep going!");
    await refreshRoom();
  } catch (error) {
    setMessage(roomSessionMessage, error.message, true);
    await refreshRoom();
  } finally {
    state.roomBusy = false;
  }
}

document.querySelector("#room-leave").addEventListener("click", () => {
  showRoomEntry("You left the room on this device. To rejoin, use the same room code and a new player name.");
});
roomDialog.addEventListener("close", () => {
  stopRoomPolling();
  if (!state.room) {
    roomEntry.hidden = false;
    roomSession.hidden = true;
  }
});

try {
  const savedRoom = JSON.parse(sessionStorage.getItem("myk-room") || "null");
  if (savedRoom && savedRoom.code && savedRoom.token && ["host", "player"].includes(savedRoom.role)) {
    state.room = savedRoom;
    state.room.name = savedRoom.name || "";
  }
} catch (error) {
  console.error("Could not restore the saved quiz room:", error);
  sessionStorage.removeItem("myk-room");
}
