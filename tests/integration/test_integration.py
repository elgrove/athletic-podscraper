import pytest
from core.models import PodcastSeries
from core.scraper import PodcastScraper

from core.webdriver.builder import WebDriverBuilder


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv("LOGIN_EMAIL", "")
    monkeypatch.setenv("LOGIN_PASS", "")


@pytest.fixture
def webdriver():
    driver = WebDriverBuilder(host="100.76.187.39").get_driver()
    yield driver
    driver.quit()


def test_integration(webdriver):
    series = PodcastSeries(
        "The Athletic Football Podcast",
        "https://theathletic.com/podcast/144-athletic-football-podcast",
    )
    scraper = PodcastScraper(series, webdriver)
    scraper.scrape()
    assert 1 == 2
