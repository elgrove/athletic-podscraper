from dataclasses import dataclass
from datetime import datetime


@dataclass
class Podcast:
    name: str
    url: str


@dataclass
class PodcastEpisode:
    name: str
    date_published: str  # TODO datetime
    description: str
    file_url: str
