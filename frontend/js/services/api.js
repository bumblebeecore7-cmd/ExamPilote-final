import { CONFIG } from '../config.js';

class ApiService {
  constructor() {
    this.baseUrl = CONFIG.API_BASE_URL;
  }

  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    try {
      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json',
          ...(options.headers || {})
        },
        ...options
      });

      if (!response.ok) {
        let errorDetail = `Request failed with status ${response.status}`;
        try {
          const errJson = await response.json();
          if (errJson && errJson.detail) {
            errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
          }
        } catch (_) {}
        throw new Error(errorDetail);
      }

      return await response.json();
    } catch (err) {
      console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, err);
      throw err;
    }
  }

  // Health & Database
  async getHealth() {
    return this._request('/health');
  }

  async getDatabaseHealth() {
    return this._request('/health/database');
  }

  // Questions
  async generateQuestions(payload) {
    return this._request('/questions/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  }

  async generateWithDocument(formData) {
    return this._request('/questions/generate-with-document', {
      method: 'POST',
      body: formData // Note: Content-Type is set automatically with boundary by fetch
    });
  }

  async getQuestionSets(page = 1, pageSize = 10) {
    return this._request(`/question-sets?page=${page}&page_size=${pageSize}`);
  }

  async getQuestionSet(id) {
    return this._request(`/question-sets/${id}`);
  }

  async deleteQuestionSet(id) {
    return this._request(`/question-sets/${id}`, { method: 'DELETE' });
  }

  // Quiz
  async submitQuizAttempt(payload) {
    return this._request('/quiz-attempts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  }

  async getQuizAttempts(page = 1, pageSize = 10) {
    return this._request(`/quiz-attempts?page=${page}&page_size=${pageSize}`);
  }

  async getQuizAttempt(id) {
    return this._request(`/quiz-attempts/${id}`);
  }
}

export const api = new ApiService();
