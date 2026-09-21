FROM python:3.13-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and data
COPY data/ data/
COPY src/ src/
COPY Makefile .
COPY index.html .

# Train models and run validation gates during build
RUN python3 -m src.models.train && python3 -m src.models.evaluate

ENV PORT=8000
EXPOSE 8000

# Bind dynamically to $PORT for PaaS (Render, Railway, Fly.io, Heroku)
CMD ["sh", "-c", "uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
