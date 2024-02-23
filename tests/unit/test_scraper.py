from unittest.mock import MagicMock

from bs4 import BeautifulSoup
from core.scraper import PodcastScraper, PodcastSeries
import requests


def mock_parser(*args, **kwargs):
    response = requests.get(
        "https://theathletic.com/podcast/200-the-totally-football-show/"
    )
    soup = BeautifulSoup(response.text)
    return soup


class TestScraper:
    def test_scrape(self):
        series = PodcastSeries(
            "The Totally Football Show",
            "https://theathletic.com/podcast/200-the-totally-football-show/",
        )
        scraper = PodcastScraper(series, webdriver=MagicMock(), parser=mock_parser)
        scraper.scrape()
