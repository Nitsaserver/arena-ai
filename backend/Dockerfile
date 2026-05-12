# ==========================================================
# Arena-AI Backend Dockerfile
# ==========================================================

FROM python:3.11-slim

WORKDIR /app

# --------------------------
# System dependencies
# --------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    pkg-config \
    ca-certificates \
    default-libmysqlclient-dev \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*




# --------------------------
# Python dependencies (BACKEND ONLY)
# --------------------------
# 🔥 IMPORTANT: use backend/requirements.txt
COPY backend/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --------------------------
# Copy backend source code
# --------------------------
COPY backend/ /app/backend

# --------------------------
# Environment
# --------------------------
ENV PYTHONPATH=/app
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt


# --------------------------
# FastAPI port
# --------------------------
EXPOSE 8000

# --------------------------
# Run FastAPI app
# --------------------------
CMD ["uvicorn","backend.app:app","--host", "0.0.0.0","--port", "8000","--workers", "2"]
