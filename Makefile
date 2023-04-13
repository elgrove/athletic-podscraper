clean:
	sudo rm -rf podcasts/*

build:
	sudo docker compose up --build

up:
	sudo docker compose up

upd:
	sudo docker compose up -d