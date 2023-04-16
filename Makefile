test:
	poetry run pytest tests

format:
	poetry run black .

lint:
	poetry run pylint --recursive .

PACKAGE_VERSION := $(shell poetry version --no-ansi | cut -d " " -f 2)
IMAGE_NAME := athletic_podscraper
LAST_COMMIT_TYPE := $(shell git log --format=%B -n 1 HEAD^1 | awk 'NR==1{sub(/:.*/, ""); print}')

bump:
	poetry run bump2version ${LAST_COMMIT_TYPE}

push:
	git push origin main

build:
	docker build -t ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION) .

publish: bump push build
	docker push ghcr.io/elgrove/$(IMAGE_NAME):$(PACKAGE_VERSION)