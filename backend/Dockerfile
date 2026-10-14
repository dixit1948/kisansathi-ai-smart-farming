# Multi-stage Dockerfile — non-root user, minimal image
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ── Production stage ──────────────────────────────────────────────────────────
FROM python:3.11-slim

# Non-root user
RUN useradd -m -u 1000 appuser

# System deps for Pillow and python-magic
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Create upload dir with proper ownership
RUN mkdir -p /app/uploads && chown -R appuser:appuser /app

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
