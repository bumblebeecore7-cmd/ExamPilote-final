/**
 * ExamPilote Frontend Configuration
 * Centralized settings for API endpoints and application defaults.
 * Automatically adapts between local separated dev server and production single-service deployment.
 */

const isSeparateDevServer = (window.location.port === "5500" || window.location.port === "3000");
const defaultBaseUrl = isSeparateDevServer ? "http://localhost:8000/api/v1" : "/api/v1";

export const CONFIG = {
  API_BASE_URL: defaultBaseUrl,
  DEFAULT_QUESTION_COUNT: 5,
  MAX_QUESTION_COUNT: 20,
  STORAGE_KEYS: {
    ACTIVE_QUIZ: "exampilote_active_quiz",
    LAST_ATTEMPT_ID: "exampilote_last_attempt_id"
  }
};
