FROM python:3.12-slim

WORKDIR /app

# Install system utilities if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application files
COPY frontend /app/frontend
COPY backend /app/backend

# Environment settings
ENV PORT=8000
ENV ENVIRONMENT=production

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir backend"]
