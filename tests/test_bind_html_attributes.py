"""Tests for HTMLAttributeBinder and related functionality."""

# Bind HTML
from bind_html import HTMLAttributeBinder


class TestBinder:
    """Test the HTMLAttributeBinder class."""

    def test_basic(self):
        """Test the baseline HTML structure."""
        basic_html = ""
        expected_result = ""

        binder = HTMLAttributeBinder()
        result = binder.apply(basic_html)

        assert result == expected_result
