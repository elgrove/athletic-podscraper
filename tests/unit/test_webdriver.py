import os

from core.webdriver.builder import WebDriverBuilder
import pytest


@pytest.mark.unit
class TestWebDriverBuilder:
    """Tests for the webdriver builder class."""

    def test_extensions_dir(self):
        """Test that the extensions dir can be found correctly."""
        builder = WebDriverBuilder()
        if os.uname().sysname == "Darwin":
            assert (
                builder.extensions_dir
                == "/Users/aaron/dev/athletic_podscraper/core/webdriver/extensions"
            )

    def test_extensions(self):
        """Tests that there are two extensions in the dir."""
        builder = WebDriverBuilder()
        assert len(builder.extensions) == 2
