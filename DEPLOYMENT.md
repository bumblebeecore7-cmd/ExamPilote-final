# ExamPilote — Deployment Guide (Render Free Tier)

This guide walks you through deploying **ExamPilote** to [Render.com](https://render.com) as a single, full-stack service with zero hosting costs.

---

## Architecture in Production

* **Single Web Service:** FastAPI serves both the REST API endpoints (`/api/v1`) and the static frontend UI (`/`, `/pages/generate.html`, etc.).
* **Cloud Database:** Connects securely to your cloud MongoDB Atlas cluster.
* **AI Provider:** Google Gemini API generating live questions.
* **No CORS Issues:** Both frontend and backend share the same public domain.

---

## Step 1: Push Your Code to GitHub

1. If you haven't already, create a new repository on [GitHub](https://github.com/new) named `ExamPilote` (set it to **Private** or **Public**).
2. In your VS Code Terminal, run:

```powershell
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/ExamPilote.git
git branch -M main
git push -u origin main
```

*(Note: Your `.env` and `backend/.env` are automatically excluded by `.gitignore` so your secrets will never be uploaded to GitHub).*

---

## Step 2: Create a Web Service on Render

1. Go to **[https://dashboard.render.com](https://dashboard.render.com)** and sign in (you can use your GitHub account).
2. Click **New +** in the top right and select **Web Service**.
3. Choose **Build and deploy from a Git repository** and connect your `ExamPilote` repository.
4. Fill in the service configuration:
   * **Name:** `exampilote` (or any name you like)
   * **Region:** Any close region (e.g., *Oregon (US West)* or *Frankfurt (EU)*)
   * **Language / Environment:** `Python 3`
   * **Branch:** `main`
   * **Build Command:**
     ```bash
     pip install -r backend/requirements.txt
     ```
   * **Start Command:**
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend
     ```
   * **Instance Type:** `Free`

---

## Step 3: Add Your Environment Variables on Render

Scroll down to the **Environment Variables** section on the same page and add these key-value pairs:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Enables production mode |
| `MONGODB_URI` | `mongodb+srv://bumblebeecore7_db_user:<YOUR_PASSWORD>@cluster1.buprqod.mongodb.net/?retryWrites=true&w=majority` | Your MongoDB Atlas connection string |
| `MONGODB_DATABASE` | `exampilote` | Database name |
| `AI_PROVIDER` | `gemini` | Configured AI provider |
| `AI_API_KEY` | `your_gemini_api_key` | Your Google Gemini API key |
| `AI_MODEL` | `gemini-flash-lite-latest` | Fast, high-capacity Gemini model |

---

## Step 4: Deploy & Access

1. Click **Create Web Service**.
2. Render will build the dependencies and start Uvicorn. The included
   `render.yaml` is a valid Render Blueprint and configures a lightweight
   `/healthz` check that does not depend on MongoDB or Gemini being available.
3. Once the build finishes (usually ~1-2 minutes), Render will display your live public URL:
   👉 **`https://exampilote.onrender.com`** (or your chosen service name).

Open that URL in your browser — your full-stack AI MCQ platform is live on the internet!

> A temporary `trycloudflare.com` link is not a deployment and stops working
> as soon as the local tunnel process stops. Share the `onrender.com` URL shown
> in Render after a successful deploy instead.

---

## MongoDB Atlas Network Access Note

In your [MongoDB Atlas Console](https://cloud.mongodb.com):
1. Go to **Security > Network Access**.
2. Click **Add IP Address**.
3. Select **Allow Access from Anywhere** (`0.0.0.0/0`) and click **Confirm**.
*(This ensures Render's dynamic cloud IPs can reach your Atlas cluster).*
