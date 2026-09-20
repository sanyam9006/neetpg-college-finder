FROM python:3.13-slim

WORKDIR /app

# Install build essentials if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and data
COPY data/ data/
COPY src/ src/
COPY Makefile .
COPY index.html .

# Run model training during build to ensure self-contained artifact
RUN python3 -m src.models.train && python3 -m src.models.evaluate

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
