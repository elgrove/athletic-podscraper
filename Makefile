test:
	poetry run pytest tests

format:
	poetry run black .

lint:
	poetry run pylint --recursive .

PACKAGE_VERSION := $(shell poetry version --no-ansi | cut -d " " -f 2)
IMAGE_NAME := athletic_podscraper


build:
	docker build -t $(IMAGE_NAME):$(PACKAGE_VERSION) .

publish
	docker push ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION)
