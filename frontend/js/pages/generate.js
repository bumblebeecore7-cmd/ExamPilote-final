import { api } from '../services/api.js';

let selectedFile = null;
let currentQuestionSet = null;
let revealAnswers = false;

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('generate-form');
  const dropzone = document.getElementById('file-dropzone');
  const fileInput = document.getElementById('file-input');
  const removeFileBtn = document.getElementById('remove-file-btn');
  const startQuizBtn = document.getElementById('start-quiz-btn');

  // File dropzone events
  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
      }
    });
  }

  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      selectedFile = null;
      if (fileInput) fileInput.value = '';
      updateFileDisplay();
    });
  }

  const changeFileBtn = document.getElementById('change-file-btn');
  if (changeFileBtn) {
    changeFileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (fileInput) fileInput.click();
    });
  }

  // Form submit
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await handleGenerate();
    });
  }

  // Toggle Answer Key button
  const toggleAnswersBtn = document.getElementById('toggle-answers-btn');
  if (toggleAnswersBtn) {
    toggleAnswersBtn.addEventListener('click', () => {
      revealAnswers = !revealAnswers;
      toggleAnswersBtn.textContent = revealAnswers ? '🙈 Hide Answer Key' : '👁️ Reveal Answer Key';
      if (currentQuestionSet) {
        renderPreview(currentQuestionSet);
      }
    });
  }

  // Start Quiz button
  if (startQuizBtn) {
    startQuizBtn.addEventListener('click', () => {
      if (currentQuestionSet && currentQuestionSet.id) {
        window.location.href = `quiz.html?id=${currentQuestionSet.id}`;
      }
    });
  }
});

function handleFileSelect(file) {
  const allowed = ['.txt', '.pdf', '.docx'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showAlert('error', `Invalid file type "${ext}". Allowed: .txt, .pdf, .docx`);
    return;
  }
  if (file.size === 0) {
    showAlert('error', `The file "${file.name}" is completely empty (0 bytes on disk). Please ensure the download or file transfer completed on your device.`);
    selectedFile = null;
    updateFileDisplay();
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showAlert('error', 'File size exceeds 10MB limit.');
    return;
  }
  selectedFile = file;
  updateFileDisplay();
}

function updateFileDisplay() {
  const infoEl = document.getElementById('selected-file-info');
  const nameEl = document.getElementById('selected-file-name');
  const placeholderEl = document.getElementById('dropzone-placeholder');

  if (selectedFile) {
    nameEl.textContent = `${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)`;
    infoEl.style.display = 'flex';
    placeholderEl.style.display = 'none';
  } else {
    infoEl.style.display = 'none';
    placeholderEl.style.display = 'block';
  }
}

async function handleGenerate() {
  const topic = document.getElementById('topic-input')?.value?.trim();
  const studyMaterial = document.getElementById('notes-input')?.value?.trim();
  const count = parseInt(document.getElementById('count-input')?.value, 10) || 5;
  const difficulty = document.getElementById('difficulty-select')?.value || 'Medium';
  const format = document.getElementById('format-select')?.value || 'Single-correct MCQ';
  const customInstructions = document.getElementById('instructions-input')?.value?.trim();

  if (!topic && !studyMaterial && !selectedFile) {
    showAlert('error', 'Please provide a topic, paste study notes, or upload a document.');
    return;
  }

  const loadingMsg = selectedFile ? 'Parsing document & generating AI questions...' : 'Generating Questions with AI...';
  setLoading(true, loadingMsg);
  hideAlert();

  try {
    let result;
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('topic', topic);
      formData.append('question_count', count);
      formData.append('difficulty', difficulty);
      formData.append('format', format);
      formData.append('custom_instructions', customInstructions);

      result = await api.generateWithDocument(formData);
    } else {
      const payload = {
        topic: topic,
        study_material: studyMaterial,
        question_count: count,
        difficulty: difficulty,
        format: format,
        custom_instructions: customInstructions
      };
      result = await api.generateQuestions(payload);
    }

    currentQuestionSet = result;
    renderPreview(result);
    if (result.storage_warning) {
      showAlert('warning', `Questions generated for practice! Note: ${result.storage_warning}`);
    } else {
      showAlert('success', `Successfully generated and saved ${result.questions.length} questions to MongoDB Atlas!`);
    }
  } catch (err) {
    showAlert('error', err.message || 'Generation failed.');
  } finally {
    setLoading(false);
  }
}

function renderPreview(questionSet) {
  const previewCard = document.getElementById('preview-card');
  const previewList = document.getElementById('preview-list');
  const previewTitle = document.getElementById('preview-title');
  const previewBadge = document.getElementById('preview-badge');

  if (!previewCard || !previewList) return;

  previewTitle.textContent = questionSet.topic;
  previewBadge.textContent = `${questionSet.difficulty} • ${questionSet.questions.length} Questions`;
  previewList.innerHTML = '';

  const letters = ['A', 'B', 'C', 'D', 'E'];

  questionSet.questions.forEach((q, idx) => {
    const item = document.createElement('div');
    item.className = 'question-preview-item';

    const optionsHtml = q.options.map((opt, optIdx) => {
      const letter = letters[optIdx] || (optIdx + 1);
      const isCorrect = (opt === q.correct_answer);

      if (revealAnswers) {
        return `
          <div class="option-pill ${isCorrect ? 'correct' : ''}">
            <strong>${letter}.</strong> ${escapeHtml(opt)} ${isCorrect ? '✓ (Correct)' : ''}
          </div>
        `;
      } else {
        return `
          <div class="option-pill">
            <strong>${letter}.</strong> ${escapeHtml(opt)}
          </div>
        `;
      }
    }).join('');

    const explanationHtml = revealAnswers ? `
      <div class="form-text" style="margin-top: 0.75rem; background: var(--bg-alt); padding: 0.6rem; border-radius: var(--radius-sm);">
        <strong>Explanation:</strong> ${escapeHtml(q.explanation)}
      </div>
    ` : '';

    item.innerHTML = `
      <div class="question-preview-header">
        <span class="badge badge-info">Question ${idx + 1}</span>
        <span class="badge badge-${q.difficulty.toLowerCase()}">${q.difficulty}</span>
      </div>
      <div class="question-preview-title">${escapeHtml(q.question)}</div>
      <div class="option-pill-list">${optionsHtml}</div>
      ${explanationHtml}
    `;
    previewList.appendChild(item);
  });

  if (!revealAnswers) {
    const hint = document.createElement('div');
    hint.className = 'form-text';
    hint.style.cssText = 'text-align: center; margin-top: 1rem; color: var(--text-muted); font-style: italic;';
    hint.textContent = '💡 Answers & explanations are hidden so you can test yourself. Click "Start Interactive Quiz" to begin!';
    previewList.appendChild(hint);
  }

  previewCard.style.display = 'block';
  previewCard.scrollIntoView({ behavior: 'smooth' });
}

function setLoading(isLoading, customText = '') {
  const submitBtn = document.getElementById('generate-submit-btn');
  const btnText = document.getElementById('generate-btn-text');
  const btnSpinner = document.getElementById('generate-btn-spinner');

  if (submitBtn) submitBtn.disabled = isLoading;
  if (btnText) btnText.textContent = isLoading ? (customText || 'Generating Questions...') : 'Generate Questions';
  if (btnSpinner) btnSpinner.style.display = isLoading ? 'inline-block' : 'none';
}

function showAlert(type, message) {
  const alertEl = document.getElementById('generate-alert');
  if (!alertEl) return;
  alertEl.className = `alert alert-${type === 'error' ? 'danger' : 'success'}`;
  alertEl.textContent = message;
  alertEl.style.display = 'flex';
}

function hideAlert() {
  const alertEl = document.getElementById('generate-alert');
  if (alertEl) alertEl.style.display = 'none';
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
