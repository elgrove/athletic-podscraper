from datetime import datetime
from time import sleep
import os
import urllib.request
import json

from bs4 import BeautifulSoup
from mutagen import File as mutagenFile
from mutagen.id3 import ID3, TDAT, TYER, TIT2, TIT3
from polling2 import poll_decorator
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from PIL import Image

from core.models import PodcastSeries, PodcastEpisode
from core.logger import get_logger
from core.podcasts import podcast_objects
from core.webdriver.builder import WebDriverBuilder

LOGGER = get_logger()


class PodcastScraper:
    """Scrape a podcast from The Athletic into the docker mounted podcasts directory."""

    EPISODES_TO_SCRAPE = int(os.environ["LAST_N_PODCASTS"])

    def __init__(self, podcast: PodcastSeries, webdriver, parser=BeautifulSoup):
        """Init with the Podcast object to scrape, a webdriver and parser."""
        self.podcast = podcast
        self.driver = webdriver
        self._login_to_the_athletic(self.driver)
        self.driver.get(podcast.url)
        self.soup = parser(self.driver.page_source.encode("utf-8"), "lxml")

    @poll_decorator(step=1, timeout=30)
    def _is_logged_in_to_the_athletic(self, driver):
        try:
            _ = driver.find_element(By.ID, "header-login-button")
            return False
        except NoSuchElementException:
            return True

    def _login_to_the_athletic(self, driver):
        """Log in to The Athletic website using credentials from env vars."""
        LOGGER.debug("Checking logged-in to The Athletic")
        login_url = "https://theathletic.com/login2"
        driver.get(login_url)
        if all([driver.current_url != login_url, "redirected" in driver.current_url]):
            return
        LOGGER.debug("Logging into The Athletic")
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys(os.environ["LOGIN_EMAIL"])
        password_field.send_keys(os.environ["LOGIN_PASS"])
        password_field.send_keys(Keys.RETURN)
        sleep(5)
        if self._is_logged_in_to_the_athletic(driver):
            return

    def _make_podcast_directory(self):
        """Create a directory for the podcast series in the docker mounted dir."""
        podcast_dir = f"/podcasts/{self.podcast.name}"
        if not os.path.exists(podcast_dir):
            LOGGER.debug("Making directory for podcast series %s", self.podcast.name)
            os.mkdir(podcast_dir)

    def _scrape_podcast_json(self):
        """Scrape json from The Athletic with info about the podcast series."""
        jsons = [
            json.loads(s.string)
            for s in self.soup.find_all("script", {"type": "application/ld+json"})
            if json.loads(s.string)["@type"] == "PodcastSeries"
        ]
        return jsons[0]

    def _add_urllib_headers(self):
        """Add headers to urllib to circumvent download prevention from The Athletic cdn."""
        opener = urllib.request.build_opener()
        opener.addheaders = [
            (
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            )
        ]
        urllib.request.install_opener(opener)

    def _download_podcast_image(self):
        """Download the podcast image to the podcasts directory, and convert it to jpg."""
        image_url = self._scrape_podcast_json()["image"]
        image_ext = image_url.split(".")[-1]
        image_filepath = f"/podcasts/{self.podcast.name}/Cover."
        if not os.path.exists(image_filepath + image_ext):
            LOGGER.debug("Downloading image for podcast %s", self.podcast.name)
            self._add_urllib_headers()
            urllib.request.urlretrieve(
                url=image_url, filename=image_filepath + image_ext
            )
            os.chmod(image_filepath + image_ext, 0o777)
            if image_ext == "png":
                png = Image.open(image_filepath + "png")
                jpg = png.convert("RGB")
                jpg.save(image_filepath + "jpg")
                os.chmod(image_filepath + "jpg", 0o777)

    def _scrape_episodes_json(self):
        """Scrape json from The Athletic with information about each episode."""
        jsons = [
            json.loads(s.string)
            for s in self.soup.find_all("script", {"type": "application/ld+json"})
            if json.loads(s.string)["@type"] == "PodcastEpisode"
        ]
        return jsons

    def _generate_episodes(self, jsons):
        """Generate PodcastEpisode objects from the json scraped from The Athletic"""
        LOGGER.debug("Generating episodes for podcast %s", self.podcast.name)
        episodes = [
            PodcastEpisode(
                title=j["name"],
                date_published=datetime.fromisoformat(j["datePublished"]),
                description=j["description"],
                file_url=j["associatedMedia"]["contentUrl"],
            )
            for j in jsons
        ][: self.EPISODES_TO_SCRAPE]
        return episodes

    @poll_decorator(step=1, timeout=600)
    def _mp3_available(self):
        """Wait for an episode file to load in the browser before attempting to download it."""
        return ".mp3" in self.driver.current_url

    def _navigate_to_mp3(self, episode):
        """Navigate the webdriver browser to a podcast episode file, and wait for it to load."""
        LOGGER.debug("Navigating to MP3 for episode %s", episode.title)
        self.driver.get(self.podcast.url)
        if not self._is_logged_in_to_the_athletic(self.driver):
            self._login_to_the_athletic(self.driver)
        self.driver.get(episode.file_url)
        if self._mp3_available():
            return

    def _get_mp3_filepath(self, episode):
        """Produce a filepath for a podcast episode to be downloaded into."""
        return f"/podcasts/{self.podcast.name}/{episode.date_published.isoformat()[:10]} {episode.title}.mp3"

    def _tag_mp3(self, episode):
        """Write ID3 tags to the episode mp3 file with metadata."""
        LOGGER.debug("Tagging MP3 for episode %s", episode.title)
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

    def _download_mp3(self, episode):
        """Download the mp3 file of a podcast episode."""
        filepath = self._get_mp3_filepath(episode)
        if not os.path.exists(filepath):
            self._navigate_to_mp3(episode)
            LOGGER.info("Downloading MP3 for episode %s", episode.title)
            urllib.request.urlretrieve(
                url=self.driver.current_url,
                filename=filepath,
            )
            os.chmod(filepath, 0o777)
            self._tag_mp3(episode)
            self.driver.get(self.podcast.url)

    def scrape(self):
        """Scrape a podcast from The Athletic, creating a directory and download an image if needed."""
        self._make_podcast_directory()
        self._download_podcast_image()
        episodes = self._generate_episodes(self._scrape_episodes_json())
        for episode in episodes:
            self._download_mp3(episode)


class ScraperCommand:
    """Command class for orchestrating the scraping of a given list of PodcastSeries objects."""

    def __init__(
        self,
        podcasts=podcast_objects,
        scraper=PodcastScraper,
        driver_builder=WebDriverBuilder,
    ):
        """Init with PodcastSeries objects, the scraper class and a webdriver builder class."""
        self.podcasts = podcasts
        self.scraper = scraper
        self.driver_builder = driver_builder

    def run(self):
        """Create a webdriver, log into The Athletic and scrape podcasts as flagged by env vars."""
        LOGGER.debug("Creating webdriver")
        driver = self.driver_builder().get_driver()
        for podcast in self.podcasts:
            LOGGER.info("Working on podcast %s", podcast.name)
            scraper = self.scraper(podcast, driver)
            scraper.scrape()
        driver.quit()
