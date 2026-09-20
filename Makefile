.PHONY: install train eval test serve docker-build docker-up clean

install:
	pip install -r requirements.txt

train:
	python3 -m src.models.train

eval:
	python3 -m src.models.evaluate

test:
	pytest tests/ -v

serve:
	uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -f docker/Dockerfile -t neetpg-mlops-api:latest .

docker-up:
	docker compose -f docker/docker-compose.yml up --build -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
