app/down:
	docker compose down --remove-orphans

app/down-volumes:
	docker compose down --remove-orphans --volumes

app/up:
	docker compose up -d

app/up/build:
	docker compose up --build

app/logs:
	docker compose logs -f importer-api process-worker send-mail-service

docker/build:
	docker build -t $(IMAGE_NAME):latest .

test:
	docker run --rm -v $(PWD):/opt/app $(IMAGE_NAME):latest python -m pytest --cov=.
