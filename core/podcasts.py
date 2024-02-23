import os

from core.models import PodcastSeries

podcast_env_map = {
    "TOTALLY": "The Totally Football Show",
    "TOTALLY_EURO": "The Totally Football Show European Edition",
    "TIFO": "The Tifo Football Podcast",
    "ATHLETIC": "The Athletic Football Podcast",
    "CLICHES": "Football Cliches",
    "TACTICS": "The Athletic Football Tactics Podcast",
    "TOTTENHAM": "The View from the Lane",
    "CHELSEA": "Straight Outta Cobham",
    "LEEDS": "The Phil Hay Show",
    "LIVERPOOL": "Walk On",
    "MANCITY": "Why Always Us?",
    "MANUNITED": "Talk of the Devils",
    "NEWCASTLE": "Pod on the Tyne",
    "GOLAZZO": "Golazzo: The Totally Italian Football Show",
}


podcasts = {
    "The Totally Football Show": "https://theathletic.com/podcast/200-the-totally-football-show/",
    "The Tifo Football Podcast": "https://theathletic.com/podcast/197-the-tifo-football-podcast/",
    "The Athletic Football Podcast": "https://theathletic.com/podcast/144-athletic-football-podcast/",
    "The Totally Football Show European Edition": "https://theathletic.com/podcast/202-the-totally-football-show-european-edition/",  # pylint: disable=line-too-long
    "Football Cliches": "https://theathletic.com/podcast/164-football-cliches/",
    "The Athletic Football Tactics Podcast": "https://theathletic.com/podcast/145-football-tactics-podcast/",
    "The View from the Lane": "https://theathletic.com/podcast/148-the-view-from-the-lane/",
    "Straight Outta Cobham": "https://theathletic.com/podcast/139-straight-outta-cobham/",
    "The Phil Hay Show": "https://theathletic.com/podcast/142-the-phil-hay-show/",
    "Walk On": "https://theathletic.com/podcast/140-the-red-agenda/",
    "Why Always Us?": "https://theathletic.com/podcast/159-why-always-us/",
    "Talk of the Devils": "https://theathletic.com/podcast/162-talk-of-the-devils/",
    "Pod on the Tyne": "https://theathletic.com/podcast/147-pod-on-the-tyne/",
    "Golazzo: The Totally Italian Football Show": "https://theathletic.com/podcast/290-golazzo-the-totally-italian-football-show/",
}

env_vars = list(podcast_env_map.keys())

podcast_names_to_scrape = [
    podcast_env_map[var] for var in env_vars if os.environ.get(var, "0") == "1"
]

podcast_objects = [
    PodcastSeries(k, v) for k, v in podcasts.items() if k in podcast_names_to_scrape
]
