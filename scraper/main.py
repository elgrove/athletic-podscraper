from athletic_scraper import ScraperDirector

# scrape the podcasts on a schedule
# podcast object holds its schedule, link
# env vars for how much history to keep
# could evolve into self contained podcast stack w/ the front end and the storage


if __name__ == "__main__":
    ScraperDirector().run()
