app/down:
	docker compose down --remove-orphans

app/down-volumes:
	docker compose down --remove-orphans --volumes

app/up:
	docker compose up -d

app/up/build:
	docker compose up --build

app/logs:
	docker compose logs -f importer-api billing-worker send-mail-worker

app/setup:
	bash ./developer/setup/setup.sh

docker/build:
	docker build -t $(IMAGE_NAME):latest $(CONTEXT) -f $(DOCKERFILE)

test:
	docker run --rm -v "$(PWD)/$(CONTEXT)":/opt/app $(IMAGE_NAME):latest python -m pytest --cov=.
