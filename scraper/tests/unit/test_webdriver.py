import os

import pytest

from athletic_scraper.webdriver import WebDriverBuilder


class TestWebDriverBuilder:
    def test_extensions_dir(self):
        builder = WebDriverBuilder()
        if os.uname().sysname == "Darwin":
            assert (
                builder.extensions_dir
                == "/Users/aaron/dev/athletic/scraper/athletic_scraper/webdriver/extensions"
            )

    def test_extensions(self):
        builder = WebDriverBuilder()
        assert len(builder.extensions) == 2
