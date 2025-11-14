# Dockerfile for Arena Orchestrator
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir requests

CMD ["python", "run_simulation.py"]
