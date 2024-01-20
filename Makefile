test:
	poetry run pytest tests

format:
	poetry run black .

lint:
	poetry run pylint --recursive .

PACKAGE_VERSION := $(shell poetry version --no-ansi | cut -d " " -f 2)
IMAGE_NAME := athletic_podscraper

major:
	poetry run bump2version major pyproject.toml

minor:
	poetry run bump2version minor pyproject.toml

patch:
	poetry run bump2version patch pyproject.toml

push:
	git push origin main

build:
ifeq ($(shell uname),Darwin)
	docker build -t ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION) .
else 
	sudo docker build -t ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION) .
endif

publish: push build
ifeq ($(shell uname),Darwin)
	docker push ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION)
else
	sudo docker push ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION)
endif