import { api } from '../services/api.js';

let currentTab = 'sets'; // 'sets' or 'attempts'

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  loadCurrentTab();
});

function initTabs() {
  const tabSets = document.getElementById('tab-sets');
  const tabAttempts = document.getElementById('tab-attempts');

  tabSets?.addEventListener('click', () => {
    if (currentTab !== 'sets') {
      currentTab = 'sets';
      tabSets.classList.add('active');
      tabAttempts.classList.remove('active');
      loadCurrentTab();
    }
  });

  tabAttempts?.addEventListener('click', () => {
    if (currentTab !== 'attempts') {
      currentTab = 'attempts';
      tabAttempts.classList.add('active');
      tabSets.classList.remove('active');
      loadCurrentTab();
    }
  });
}

async function loadCurrentTab() {
  const container = document.getElementById('history-list');
  const emptyState = document.getElementById('empty-state');
  const loadingIndicator = document.getElementById('loading-indicator');

  if (!container) return;
  container.innerHTML = '';
  if (emptyState) emptyState.style.display = 'none';
  if (loadingIndicator) loadingIndicator.style.display = 'block';

  try {
    if (currentTab === 'sets') {
      const data = await api.getQuestionSets(1, 20);
      if (loadingIndicator) loadingIndicator.style.display = 'none';
      if (!data.items || data.items.length === 0) {
        showEmpty('No Question Sets Saved Yet', 'Generate multiple-choice questions from your notes or documents to start.');
      } else {
        renderQuestionSets(data.items);
      }
    } else {
      const data = await api.getQuizAttempts(1, 20);
      if (loadingIndicator) loadingIndicator.style.display = 'none';
      if (!data.items || data.items.length === 0) {
        showEmpty('No Quiz Attempts Recorded Yet', 'Complete and submit a quiz to track your mastery scores over time.');
      } else {
        renderQuizAttempts(data.items);
      }
    }
  } catch (err) {
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    showEmpty('Could Not Retrieve History', err.message || 'Please check backend and database connectivity.');
  }
}

function renderQuestionSets(items) {
  const container = document.getElementById('history-list');
  container.innerHTML = '';

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'history-card';
    const dateFormatted = new Date(item.created_at).toLocaleDateString(undefined, {
      month: 'short', day: 'numeric', year: 'numeric'
    });

    card.innerHTML = `
      <div class="history-info">
        <div class="history-title">${escapeHtml(item.topic)}</div>
        <div class="history-meta">
          <span class="badge badge-${item.difficulty.toLowerCase()}">${item.difficulty}</span>
          <span class="badge badge-info">${item.question_count} Questions</span>
          <span>Created on ${dateFormatted}</span>
        </div>
      </div>
      <div class="history-actions">
        <a href="quiz.html?id=${item.id}" class="btn btn-primary btn-sm">Take Quiz</a>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderQuizAttempts(items) {
  const container = document.getElementById('history-list');
  container.innerHTML = '';

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'history-card';
    const dateFormatted = new Date(item.submitted_at).toLocaleDateString(undefined, {
      month: 'short', day: 'numeric', year: 'numeric'
    });

    const isGood = item.percentage >= 70;

    card.innerHTML = `
      <div class="history-info">
        <div class="history-title">${escapeHtml(item.topic)}</div>
        <div class="history-meta">
          <span class="badge ${isGood ? 'badge-easy' : 'badge-hard'}">${Math.round(item.percentage)}% Score</span>
          <span>Score: ${item.score} / ${item.total_questions}</span>
          <span>Submitted on ${dateFormatted}</span>
        </div>
      </div>
      <div class="history-actions">
        <a href="results.html?attempt_id=${item.id}" class="btn btn-secondary btn-sm">Review Results</a>
        <a href="quiz.html?id=${item.question_set_id}" class="btn btn-primary btn-sm">Retake</a>
      </div>
    `;
    container.appendChild(card);
  });
}

function showEmpty(title, desc) {
  const emptyState = document.getElementById('empty-state');
  if (!emptyState) return;
  document.getElementById('empty-title').textContent = title;
  document.getElementById('empty-desc').textContent = desc;
  emptyState.style.display = 'block';
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
