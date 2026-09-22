FROM python:3.13-slim

WORKDIR /app

# Create unprivileged system user for hardened container execution
RUN useradd -m -u 1001 -s /bin/bash appuser

# Install build dependencies, install wheels, then purge build packages to minimize image footprint
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy application source, configuration, and data
COPY data/ data/
COPY src/ src/
COPY Makefile .
COPY index.html .

# Train models and run validation quality gates during build
RUN python3 -m src.models.train && python3 -m src.models.evaluate

# Set permissions for unprivileged user
RUN chown -R appuser:appuser /app

USER appuser

ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Bind dynamically to $PORT for PaaS (Render, Railway, Fly.io, Heroku)
CMD ["sh", "-c", "uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
