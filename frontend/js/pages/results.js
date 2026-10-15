import { api } from '../services/api.js';

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const attemptId = urlParams.get('attempt_id');

  if (!attemptId) {
    showError('No quiz attempt specified.');
    return;
  }

  await loadResults(attemptId);
});

async function loadResults(id) {
  try {
    const attempt = await api.getQuizAttempt(id);
    renderSummary(attempt);
    renderReviews(attempt.reviews);

    // Setup retake button
    document.getElementById('retake-btn')?.addEventListener('click', () => {
      window.location.href = `quiz.html?id=${attempt.question_set_id}`;
    });
  } catch (err) {
    showError(err.message || 'Failed to load quiz attempt results.');
  }
}

function renderSummary(attempt) {
  document.getElementById('results-topic').textContent = attempt.topic;
  document.getElementById('score-percentage').textContent = `${Math.round(attempt.percentage)}%`;

  let tagline = "Good effort! Keep practicing to master this subject.";
  if (attempt.percentage >= 90) tagline = "Outstanding! You demonstrated exceptional mastery!";
  else if (attempt.percentage >= 70) tagline = "Great job! Strong performance across core topics.";
  else if (attempt.percentage < 50) tagline = "Review your notes and try again to improve your score.";
  document.getElementById('score-tagline').textContent = tagline;

  document.getElementById('metric-score').textContent = `${attempt.score} / ${attempt.total_questions}`;
  document.getElementById('metric-correct').textContent = attempt.correct_count;
  document.getElementById('metric-incorrect').textContent = attempt.incorrect_count;
  document.getElementById('metric-time').textContent = formatSeconds(attempt.time_spent_seconds);
}

function renderReviews(reviews) {
  const container = document.getElementById('reviews-container');
  if (!container || !reviews) return;
  container.innerHTML = '';

  reviews.forEach((r, idx) => {
    const card = document.createElement('div');
    card.className = `review-card ${r.is_correct ? 'correct' : 'incorrect'}`;

    const optionsHtml = r.options.map(opt => {
      let extraClass = '';
      let badge = '';

      if (opt === r.correct_answer) {
        extraClass = 'is-correct';
        badge = '<span class="badge badge-easy">Correct Answer</span>';
      } else if (opt === r.selected_answer && !r.is_correct) {
        extraClass = 'is-selected-wrong';
        badge = '<span class="badge badge-hard">Your Answer</span>';
      } else if (opt === r.selected_answer && r.is_correct) {
        badge = '<span class="badge badge-easy">Your Answer</span>';
      }

      return `
        <div class="review-option ${extraClass}">
          <span>${escapeHtml(opt)}</span>
          ${badge}
        </div>
      `;
    }).join('');

    card.innerHTML = `
      <div class="review-header">
        <span class="badge ${r.is_correct ? 'badge-easy' : 'badge-hard'}">
          ${r.is_correct ? '✓ Correct' : '✗ Incorrect'}
        </span>
        <span class="form-text">Question ${idx + 1}</span>
      </div>
      <div class="review-question">${escapeHtml(r.question)}</div>
      <div class="review-options">${optionsHtml}</div>
      <div class="review-explanation">
        <strong>Explanation:</strong> ${escapeHtml(r.explanation)}
      </div>
    `;

    container.appendChild(card);
  });
}

function formatSeconds(secs) {
  if (!secs || secs < 0) return '0s';
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

function showError(msg) {
  const view = document.getElementById('results-view');
  const errView = document.getElementById('results-error');
  if (view) view.style.display = 'none';
  if (errView) {
    errView.style.display = 'block';
    document.getElementById('error-message').textContent = msg;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
