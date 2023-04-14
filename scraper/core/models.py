from dataclasses import dataclass
from datetime import datetime


@dataclass
class PodcastSeries:
    """Dataclass representing a podcast series."""

    name: str
    url: str


@dataclass
class PodcastEpisode:
    """Dataclass representing an individual podcast episode of a series."""

    title: str
    date_published: datetime
    description: str
    file_url: str
