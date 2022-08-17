"""Tests for HTMLDataBinder and related functionality."""

# Bind HTML
from bind_html import HTMLDataBinder


class TestBinder:
    """Test the HTMLDataBinder class."""

    def test_basic(self):
        """Test the baseline HTML structure."""
        basic_html = ""
        expected_result = ""

        binder = HTMLDataBinder()
        result = binder.apply(basic_html)

        assert result == expected_result
