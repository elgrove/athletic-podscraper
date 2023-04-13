import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from typing import List
from core.models import Podcast, PodcastEpisode
from bs4 import BeautifulSoup
import json
from polling2 import poll_decorator
import urllib.request
from core.podcasts import podcast_objects
from core.webdriver.builder import WebDriverBuilder
from .logger import get_logger
from datetime import datetime

from mutagen import File as mutagenFile
from mutagen.id3 import ID3, TDAT, TYER, TIT2, TIT3


LOGGER = get_logger()

EPISODES_TO_SCRAPE = 3


class PodcastScraper:
    def __init__(self, podcast: Podcast, webdriver, parser=BeautifulSoup):
        self.podcast = podcast
        self.driver = webdriver
        self.driver.get(podcast.url)
        self.soup = parser(self.driver.page_source.encode("utf-8"), "lxml")

    def _make_podcast_directory(self):
        dir = f"/podcasts/{self.podcast.name}"
        if not os.path.exists(dir):
            os.mkdir(dir)

    def _scrape_podcast_json(self):
        pass

    def _scrape_podcast_image(self):
        pass

    def _scrape_episodes_json(self):
        jsons = [
            json.loads(s.string)
            for s in self.soup.find_all("script", {"type": "application/ld+json"})
            if json.loads(s.string)["@type"] == "PodcastEpisode"
        ]
        return jsons

    def _generate_episodes(self, jsons):
        episodes = [
            PodcastEpisode(
                title=j["name"],
                date_published=datetime.fromisoformat(j["datePublished"]),
                description=j["description"],
                file_url=j["associatedMedia"]["contentUrl"],
            )
            for j in jsons
        ][:EPISODES_TO_SCRAPE]
        for title in [ep.title for ep in episodes]:
            LOGGER.debug("Generated episode %s", title)
        return episodes

    @poll_decorator(step=1, timeout=30)
    def _mp3_available(self):
        return ".mp3" in self.driver.current_url

    def _navigate_to_mp3(self, episode):
        self.driver.get(episode.file_url)
        if self._mp3_available():
            return

    def _get_mp3_filepath(self, episode):
        return f"/podcasts/{self.podcast.name}/{episode.date_published.isoformat()[:10]} {episode.title}.mp3"

    def _download_mp3(self, episode):
        self._navigate_to_mp3(episode)
        urllib.request.urlretrieve(
            url=self.driver.current_url,
            filename=self._get_mp3_filepath(episode),
        )

    def _tag_mp3(self, episode):
        mp3 = mutagenFile(self._get_mp3_filepath(episode))
        if mp3.tags is None:
            mp3.add_tags()
        tags = ID3()
        tags.add(TDAT(encoding=3, text=episode.date_published.strftime("%d%m")))
        tags.add(TYER(encoding=3, text=str(episode.date_published.year)))
        tags.add(
            TIT2(
                encoding=3,
                text=episode.title,
            )
        )
        tags.add(TIT3(encoding=3, text=episode.description))
        mp3.tags = tags
        mp3.save()

    def scrape(self):
        self._make_podcast_directory()
        self._scrape_podcast_image()
        episodes = self._generate_episodes(self._scrape_episodes_json())
        for episode in episodes:
            self._download_mp3(episode)
            self._tag_mp3(episode)


class ScraperCommand:
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
            scraper.scrape()
        driver.quit()
