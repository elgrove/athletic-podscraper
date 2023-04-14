# The Athletic Podcast Scraper

Scrape ad-free podcasts from The Athletic's website to use in your podcast player of choice. Requires a subscription.

## How to use

This app has one prerequisite: docker.

* Clone this repo
* In the project root, add a `secrets.env` file with LOGIN_EMAIL and LOGIN_PASS
* In `docker-compose.yml`, edit the environment variables to flag which podcasts you want to scrape
* Run `make upd`
* The podcasts will be downloaded into a `podcasts` directory in the project root