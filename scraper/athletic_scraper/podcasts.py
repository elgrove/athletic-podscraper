from athletic_scraper.models import Podcast

import sys
import inspect


def print_classes():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if isinstance(obj, Podcast):
            print(obj)


# TODO add podcasts
podcasts = {
    "The Tifo Football Podcast": "https://theathletic.com/podcast/197-the-tifo-football-podcast/",
    "The Totally Football Show": "https://theathletic.com/podcast/200-the-totally-football-show/",
}

podcast_objects = [Podcast(k, v) for k, v in podcasts.items()]
