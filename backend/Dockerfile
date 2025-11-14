#==========================================================
# ✅ Final Backend Dockerfile (for context = ./backend)
# ==========================================================
FROM python:3.11-slim

WORKDIR /app
# Install system deps
RUN apt-get update && apt-get install -y \
    curl \
    default-libmysqlclient-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple --timeout=200

# Copy backend code
COPY . /app/backend

# Add Python path
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8000

# Launch FastAPI app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]