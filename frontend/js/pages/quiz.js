import { api } from '../services/api.js';

let questionSet = null;
let currentIndex = 0;
let userAnswers = {}; // { questionId: selectedOption }
let startTime = Date.now();
let isSubmitting = false;

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const questionSetId = urlParams.get('id');

  if (!questionSetId) {
    showError('No question set selected. Please generate or choose a quiz from history.');
    return;
  }

  await loadQuiz(questionSetId);
  initControls();
});

async function loadQuiz(id) {
  try {
    questionSet = await api.getQuestionSet(id);
    if (!questionSet || !questionSet.questions || questionSet.questions.length === 0) {
      showError('This question set has no questions.');
      return;
    }
    document.getElementById('quiz-title').textContent = questionSet.topic;
    document.getElementById('quiz-badge').textContent = `${questionSet.difficulty} • ${questionSet.questions.length} Questions`;
    renderNavStrip();
    renderCurrentQuestion();
  } catch (err) {
    showError(err.message || 'Failed to load quiz from database.');
  }
}

function initControls() {
  document.getElementById('prev-btn')?.addEventListener('click', () => {
    if (currentIndex > 0) {
      currentIndex--;
      renderCurrentQuestion();
    }
  });

  document.getElementById('next-btn')?.addEventListener('click', () => {
    if (currentIndex < questionSet.questions.length - 1) {
      currentIndex++;
      renderCurrentQuestion();
    }
  });

  document.getElementById('submit-btn')?.addEventListener('click', () => {
    openSubmitConfirmModal();
  });

  document.getElementById('confirm-cancel-btn')?.addEventListener('click', () => {
    closeSubmitConfirmModal();
  });

  document.getElementById('confirm-submit-btn')?.addEventListener('click', async () => {
    closeSubmitConfirmModal();
    await submitQuiz();
  });
}

function renderNavStrip() {
  const strip = document.getElementById('question-nav-strip');
  if (!strip || !questionSet) return;
  strip.innerHTML = '';

  questionSet.questions.forEach((q, idx) => {
    const dot = document.createElement('button');
    dot.className = `nav-dot ${idx === currentIndex ? 'active' : ''} ${userAnswers[q.id] ? 'answered' : ''}`;
    dot.textContent = idx + 1;
    dot.setAttribute('aria-label', `Question ${idx + 1}`);
    dot.addEventListener('click', () => {
      currentIndex = idx;
      renderCurrentQuestion();
    });
    strip.appendChild(dot);
  });
}

function renderCurrentQuestion() {
  if (!questionSet || !questionSet.questions[currentIndex]) return;
  const q = questionSet.questions[currentIndex];
  const total = questionSet.questions.length;

  // Update counters & progress
  document.getElementById('current-question-num').textContent = currentIndex + 1;
  document.getElementById('total-question-num').textContent = total;
  const progressPercent = ((currentIndex + 1) / total) * 100;
  document.getElementById('progress-bar').style.width = `${progressPercent}%`;

  // Question Prompt
  document.getElementById('question-text').textContent = q.question;

  // Options
  const optionsContainer = document.getElementById('options-container');
  optionsContainer.innerHTML = '';
  const letters = ['A', 'B', 'C', 'D', 'E'];

  q.options.forEach((opt, idx) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    const isSelected = userAnswers[q.id] === opt;
    btn.className = `option-btn ${isSelected ? 'selected' : ''}`;
    
    btn.innerHTML = `
      <span class="option-letter">${letters[idx] || (idx + 1)}</span>
      <span class="option-label">${escapeHtml(opt)}</span>
    `;

    btn.addEventListener('click', () => {
      userAnswers[q.id] = opt;
      renderNavStrip();
      renderCurrentQuestion();
    });

    optionsContainer.appendChild(btn);
  });

  // Buttons navigation state
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const submitBtn = document.getElementById('submit-btn');

  if (prevBtn) prevBtn.disabled = (currentIndex === 0);
  if (nextBtn) nextBtn.style.display = (currentIndex === total - 1) ? 'none' : 'inline-flex';
  if (submitBtn) submitBtn.style.display = (currentIndex === total - 1) ? 'inline-flex' : 'none';

  renderNavStrip();
}

function openSubmitConfirmModal() {
  const answeredCount = Object.keys(userAnswers).length;
  const total = questionSet.questions.length;
  const unanswered = total - answeredCount;

  const modal = document.getElementById('confirm-modal');
  const messageEl = document.getElementById('confirm-modal-text');

  if (unanswered > 0) {
    messageEl.textContent = `You have answered ${answeredCount} of ${total} questions. You have ${unanswered} unanswered question(s). Are you sure you want to submit?`;
  } else {
    messageEl.textContent = `You have answered all ${total} questions! Ready to submit your attempt?`;
  }

  modal?.classList.add('open');
}

function closeSubmitConfirmModal() {
  document.getElementById('confirm-modal')?.classList.remove('open');
}

async function submitQuiz() {
  if (isSubmitting) return;
  isSubmitting = true;

  const elapsedSeconds = Math.round((Date.now() - startTime) / 1000);
  const payload = {
    question_set_id: questionSet.id,
    answers: userAnswers,
    time_spent_seconds: elapsedSeconds
  };

  try {
    const response = await api.submitQuizAttempt(payload);
    // Redirect to results page
    window.location.href = `results.html?attempt_id=${response.id}`;
  } catch (err) {
    alert(`Submission error: ${err.message || 'Could not submit quiz.'}`);
    isSubmitting = false;
  }
}

function showError(msg) {
  const quizCard = document.getElementById('quiz-view');
  const errorCard = document.getElementById('quiz-error');
  if (quizCard) quizCard.style.display = 'none';
  if (errorCard) {
    errorCard.style.display = 'block';
    document.getElementById('error-message').textContent = msg;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
