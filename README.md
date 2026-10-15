# ExamPilote — AI Multiple-Choice Question (MCQ) Generation Platform

ExamPilote is an educational assessment platform that transforms study materials, syllabi, notes, and uploaded documents into psychometrically sound, validated Multiple-Choice Questions (MCQs) complete with educational explanations.

Built with a modular architecture, vanilla ES module frontend, FastAPI backend, and persistent cloud storage using MongoDB Atlas.

---

## Architecture Overview

```
ExamPilote/
│
├── frontend/                     # Vanilla ES6+ HTML/CSS/JS (No frameworks)
│   ├── index.html                # Home page & live Atlas status badge
│   ├── pages/
│   │   ├── generate.html         # MCQ generator form & preview
│   │   ├── quiz.html             # One-at-a-time interactive quiz engine
│   │   ├── results.html          # Score metrics & explanation reviews
│   │   └── history.html          # Saved question sets & previous attempts
│   ├── css/                      # Modular design system (tokens, reset, pages)
│   └── js/                       # API client, config, and page controllers
│
├── backend/                      # FastAPI Python Application
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Secret environment file (git-ignored)
│   ├── app/
│   │   ├── main.py               # Application entrypoint & CORS
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic settings & env resolution
│   │   │   └── database.py       # PyMongo client, masking & health ping
│   │   ├── schemas/              # Pydantic validation models
│   │   ├── repositories/         # MongoDB Atlas persistence layer
│   │   ├── services/             # Generation, document parsing, quiz scoring
│   │   ├── providers/            # Replaceable AI adapters (Mock, Gemini)
│   │   ├── prompts/              # Editable external prompt templates
│   │   └── api/v1/               # REST API endpoints (/health, /questions, /quiz)
│   └── tests/                    # Pytest test suite (13 passing tests)
│
├── .gitignore                    # Strictly excludes .env and .venv
├── .env.example                  # Safe template for environment variables
└── PROJECT_STATUS.md             # Comprehensive progress tracker
```

---

## Prerequisites

- **OS:** Windows 10/11
- **Python:** Python 3.10+ (Python 3.12 verified)
- **PowerShell:** Standard Windows PowerShell
- **Database:** MongoDB Atlas Free Tier or dedicated cluster

---

## Getting Started (Windows PowerShell)

### 1. Virtual Environment Setup & Installation

If not already created, set up the virtual environment:

```powershell
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
```

### 2. Environment Configuration

Your backend configuration is stored at `backend/.env`. A template is provided in `.env.example`.

In `backend/.env`, ensure your connection string and settings are configured:

```env
MONGODB_URI=mongodb+srv://bumblebeecore7_db_user:<YOUR_NEW_PASSWORD>@cluster1.buprqod.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=exampilote
FRONTEND_ORIGIN=http://localhost:5500
AI_PROVIDER=mock
AI_MODEL=gemini-1.5-flash
```

> **Security Note:** Never commit `backend/.env` or `.env` to Git. It is automatically ignored by `.gitignore`.

### 3. Running the Backend Server

Start the FastAPI backend with Uvicorn:

```powershell
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --app-dir backend --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Database Health Check: `http://localhost:8000/api/v1/health/database`

### 4. Serving the Frontend

In a separate PowerShell window, start a lightweight HTTP server:

```powershell
python -m http.server 5500 --directory frontend
```

Open your browser and navigate to:
```
http://localhost:5500
```

---

## Running Automated Tests

Run the test suite using pytest:

```powershell
$env:PYTHONPATH="backend"
& ".\.venv\Scripts\python.exe" -m pytest backend/tests -v
```

All 13 unit tests test schemas, mock generation, scoring algorithms, repository operations, and health checks.

---

## Modular Customization Guide

### How to Change AI Providers
1. Open `backend/.env`.
2. To use Google Gemini:
   ```env
   AI_PROVIDER=gemini
   AI_API_KEY=your_gemini_api_key_here
   AI_MODEL=gemini-1.5-flash
   ```
3. To add a new provider (e.g. Anthropic, OpenAI):
   - Subclass `BaseAIProvider` in `backend/app/providers/`.
   - Register it in `backend/app/providers/factory.py`.

### How to Edit Generation Prompts
The generation engine loads external prompt files without modifying Python code:
- System Prompt: `backend/app/prompts/mcq_system.txt`
- Generation Prompt: `backend/app/prompts/mcq_generation.txt`

### How to Replace the Document Parser
The text extraction logic is located in `backend/app/services/document_service.py`. You can swap or extend parsers (such as OCR via pytesseract) without altering the generation service.

### How to Change the Frontend Theme
Colors and layout tokens are defined in `frontend/css/variables.css`. Updating CSS variables changes the appearance across all pages simultaneously.

---

## Troubleshooting

- **MongoDB Authentication Failed (`code 8000`):**
  Check that the password in `backend/.env` matches the password set for the database user in the MongoDB Atlas Console under **Security > Database Access**.
- **MongoDB Connection Timeout:**
  In MongoDB Atlas, check **Security > Network Access** and ensure your IP address (or `0.0.0.0/0` for development) is allowed.
- **CORS Error:**
  Check that `FRONTEND_ORIGIN` in `backend/.env` matches the port where you serve your frontend (default: `http://localhost:5500`).
