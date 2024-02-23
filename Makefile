test:
	poetry run pytest tests

format:
	-poetry run docformatter -r --in-place --black core tests main.py || [ $$? -eq 3 ] # accept error code 3 as success
	poetry run black core tests main.py
	poetry run isort core tests main.py

lint: format
	poetry run flake8 core tests main.py
	poetry run pylint core main.py

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

publish: build
ifeq ($(shell uname),Darwin)
	docker push ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION)
else
	sudo docker push ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION)
endif