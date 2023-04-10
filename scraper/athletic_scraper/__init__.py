import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from typing import List
from athletic_scraper.models import Podcast, PodcastEpisode
from bs4 import BeautifulSoup
import json
from polling2 import poll_decorator
import urllib.request
from athletic_scraper.podcasts import podcast_objects
from athletic_scraper.webdriver.builder import WebDriverBuilder
from .logger import get_logger

LOGGER = get_logger()

EPISODES_TO_SCRAPE = 3


class PodcastScraper:
    def __init__(self, podcast: Podcast, webdriver):
        self.podcast = podcast
        self.driver = webdriver

    def scrape_episodes_json(self, soup):
        jsons = [
            json.loads(s.string)
            for s in soup.find_all("script", {"type": "application/ld+json"})
            if json.loads(s.string)["@type"] == "PodcastEpisode"
        ]
        return jsons

    def generate_episodes(self, jsons):
        episodes = [
            PodcastEpisode(
                name=j["name"],
                date_published=j["datePublished"],
                description=j["description"],
                file_url=j["associatedMedia"]["contentUrl"],
            )
            for j in jsons
        ][:EPISODES_TO_SCRAPE]
        for name in [ep.name for ep in episodes]:
            LOGGER.debug("Generated episode %s", name)
        return episodes

    @poll_decorator(step=1, timeout=30)
    def wait_for_mp3(self, driver):
        return ".mp3" in driver.current_url

    def scrape_episodes(self, podcast):
        self.driver.get(podcast.url)
        soup = BeautifulSoup(self.driver.page_source.encode("utf-8"), "lxml")
        jsons = self.scrape_episodes_json(soup)
        episodes = self.generate_episodes(jsons)
        for episode in episodes:
            LOGGER.debug("Navigating to episode %s", episode.name)
            self.driver.get(episode.file_url)
            if self.wait_for_mp3(self.driver):
                LOGGER.info("Downloading episode %s", episode.name)
                urllib.request.urlretrieve(
                    url=self.driver.current_url,
                    filename=f"/podcasts/{episode.date_published} {podcast.name} - {episode.name}",
                )


class ScraperDirector:
    def __init__(
        self,
        podcasts=podcast_objects,
        scraper=PodcastScraper,
        driver_builder=WebDriverBuilder,
    ):
        self.podcasts = podcasts
        self.scraper = scraper
        self.driver_builder = driver_builder

    def login_to_the_athletic(self, driver):
        driver.get("https://theathletic.com/login2")
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys(os.environ["LOGIN_EMAIL"])
        password_field.send_keys(os.environ["LOGIN_PASS"])
        password_field.send_keys(Keys.RETURN)
        sleep(10)  # TODO poll instead

    def run(self):
        LOGGER.debug("Creating webdriver")
        driver = self.driver_builder().get_driver()
        LOGGER.debug("Logging into The Athletic")
        self.login_to_the_athletic(driver)
        for podcast in self.podcasts:
            LOGGER.info("Scraping podcast %s", podcast.name)
            scraper = self.scraper(podcast, driver)
            scraper.scrape_episodes(podcast)
        driver.quit()
