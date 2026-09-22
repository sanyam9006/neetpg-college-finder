FROM python:3.13-slim

WORKDIR /app

# Create unprivileged system user
RUN useradd -m -u 1001 -s /bin/bash appuser

# Install dependencies and clean up build cache
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy application source and data
COPY data/ data/
COPY src/ src/
COPY Makefile .
COPY index.html .

# Train models during build to ensure self-contained artifact
RUN python3 -m src.models.train && python3 -m src.models.evaluate

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
