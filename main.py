import os
from time import sleep

import schedule

from core import ScraperCommand


def main():
    """Entry point for the scraper container. Runs on startup then every n hours as defined by an env var."""
    scraper = ScraperCommand()
    scraper.run()
    schedule.every(int(os.environ["SCRAPE_INTERVAL_HR"])).hours.do(scraper.run)
    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == "__main__":
    main()
