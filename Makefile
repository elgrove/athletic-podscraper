clean:
	sudo rm -rf podcasts/*

build:
	sudo docker compose up --build

up:
	sudo docker compose up

upd:
	sudo docker compose up -d

SERVICES := scraper

test:
	$(foreach service,$(SERVICES),cd $(service) && poetry run pytest test_dir;)

format:
	$(foreach service,$(SERVICES),cd $(service) && poetry run black .; cd ..;)

lint:
	$(foreach service,$(SERVICES),cd $(service) && poetry run pylint --recursive=y .; cd ..;)