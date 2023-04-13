from dataclasses import dataclass
from datetime import datetime


@dataclass
class Podcast:
    name: str
    url: str


@dataclass
class PodcastEpisode:
    title: str
    date_published: datetime
    description: str
    file_url: str
