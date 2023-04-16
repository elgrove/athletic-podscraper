# The Athletic Podcast Scraper

Scrape ad-free podcasts from The Athletic's website to use in your podcast player of choice. Requires a subscription.

## How to use

This app has one prerequisite: docker. Use the docker compose file provided to create the scraping service.

A `secrets.env` file is required in the project root to log in to The Athletic, in the format as follows:

```
LOGIN_EMAIL="harry.kane@tottenhamhotspur.com"
LOGIN_PASS="g0alz"
```

