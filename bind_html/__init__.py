"""Add dynamic bindings to HTML attributes in Python."""

# Standard Library
from html.parser import HTMLParser


class HTMLAttributeBinder(HTMLParser):
    """A parser to ingest bindable HTML and transform it."""

    def __init__(self, *args, **kwargs):
        """Initialize HTMLAttributeBinder."""
        super().__init__(*args, **kwargs)

        # Always keep charrefs intact; This class is meant to reproduce HTML.
        self.convert_charrefs = False

    def reset(self):
        """Reset the state of the binder so that it can be run again."""
        super().reset()

        self._result = []

    def handle_decl(self, decl):
        """Process a declaration string."""
        self._result.append(decl)

    def handle_starttag(self, tag, attrs):
        self._result.append(f"<{self.get_starttag_text()}>")
        """Process a start tag."""

    def handle_endtag(self, tag):
        self._result.append(f"</tag>")
        """Process a closing tag."""

    def handle_data(self, html_data):
        """Process HTML data."""
        self._result.append(html_data)

    def handle_entityref(self, name):
        """Process an HTML entity."""
        self._result.append(f"&{name};")

    def handle_charref(self, name):
        """Process a numbered HTML entity."""
        self._result.append(f"&#{name};")

    def handle_comment(self, comment):
        """Process an HTML comment."""
        self._result.append(f"<!--{comment}-->")

    def apply(self, html):
        """Run the server-side-rendering routine."""
        self.reset()

        self.feed(html)
        self.close()

        return "".join(self._result)
