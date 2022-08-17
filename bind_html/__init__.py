"""Add dynamic bindings to HTML data in Python."""

# Standard Library
import re
from html import unescape
from html.parser import HTMLParser


class HTMLDataBinder(HTMLParser):
    """A parser to ingest bindable HTML and transform it."""

    def __init__(self, *args, **kwargs):
        """Initialize HTMLDataBinder."""
        super().__init__(*args, **kwargs)

        # Always keep charrefs intact; This class is meant to reproduce HTML.
        self.convert_charrefs = False

    def reset(self):
        """Reset the state of the binder so that it can be run again."""
        super().reset()

        self._result = []

    def apply(self, html):
        """Run the transformation routine."""
        self.reset()

        self.feed(html)
        self.close()

        return "".join(self._result)

    def handle_decl(self, decl):
        """Process a declaration string."""
        self._result.append(f"<!{decl}>")

    def handle_starttag(self, tag, attrs):
        """Process a start tag."""
        # Turn attribute data in to strings
        attr_strings = []
        for attr in attrs:
            attr_name = attr[0]
            if attr[1] is not None:
                value = str(attr[1])
                if self.should_trim_attrs:
                    value = value.strip()
                value = value.replace('"', "&quot;")
                attr_strings.append(f' {attr_name}="{value}"')
            else:
                attr_strings.append(f" {attr_name}")

        attr_string = "".join(attr_strings)

        self._result.append(f"<{tag}{attr_string}>")

    def handle_endtag(self, tag):
        """Process a closing tag."""
        self._result.append(f"</{tag}>")

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

    def goahead(self, end):
        """Handle data as far as reasonable.

        Copied from:
        https://github.com/python/cpython/blob/230b630a767a457c6e7e4d797548a172c64ae735/Lib/html/parser.py#L133

        No logical modifications, except to replace character reference regexes
        with alternatives that mandate the semicolon. This *might* break the
        ability to call this function multiple times to concatenate data, but
        we don't use that functionality.
        """
        starttagopen = re.compile("<[a-zA-Z]")
        incomplete = re.compile("&[a-zA-Z#]")

        # Add semicolons to these
        entityref = re.compile("&([a-zA-Z][-.a-zA-Z0-9]*)[^a-zA-Z0-9];")
        charref = re.compile("&#(?:[0-9]+|[xX][0-9a-fA-F]+)[^0-9a-fA-F];")

        rawdata = self.rawdata
        cursor = 0
        size = len(rawdata)
        while cursor < size:
            if self.convert_charrefs and not self.cdata_elem:
                cursor2 = rawdata.find("<", cursor)
                if cursor2 < 0:
                    # if we can't find the next <, either we are at the end
                    # or there's more text incoming.  If the latter is True,
                    # we can't pass the text to handle_data in case we have
                    # a charref cut in half at end.  Try to determine if
                    # this is the case before proceeding by looking for an
                    # & near the end and see if it's followed by a space or ;.
                    buffer_size = 34
                    amppos = rawdata.rfind("&", max(cursor, size - buffer_size))
                    if amppos >= 0 and not re.compile(r"[\s;]").search(rawdata, amppos):
                        break  # wait till we get all the text
                    cursor2 = size
            else:
                match = self.interesting.search(rawdata, cursor)  # < or &
                if match:
                    cursor2 = match.start()
                else:
                    if self.cdata_elem:
                        break
                    cursor2 = size
            if cursor < cursor2:
                if self.convert_charrefs and not self.cdata_elem:
                    self.handle_data(unescape(rawdata[cursor:cursor2]))
                else:
                    self.handle_data(rawdata[cursor:cursor2])
            cursor = self.updatepos(cursor, cursor2)
            if cursor == size:
                break
            startswith = rawdata.startswith
            if startswith("<", cursor):
                if starttagopen.match(rawdata, cursor):  # < + letter
                    cursor2 = self.parse_starttag(cursor)
                elif startswith("</", cursor):
                    cursor2 = self.parse_endtag(cursor)
                elif startswith("<!--", cursor):
                    cursor2 = self.parse_comment(cursor)
                elif startswith("<?", cursor):
                    cursor2 = self.parse_pi(cursor)
                elif startswith("<!", cursor):
                    cursor2 = self.parse_html_declaration(cursor)
                elif (cursor + 1) < size:
                    self.handle_data("<")
                    cursor2 = cursor + 1
                else:
                    break
                if cursor2 < 0:
                    if not end:
                        break
                    cursor2 = rawdata.find(">", cursor + 1)
                    if cursor2 < 0:
                        cursor2 = rawdata.find("<", cursor + 1)
                        if cursor2 < 0:
                            cursor2 = cursor + 1
                    else:
                        cursor2 += 1
                    if self.convert_charrefs and not self.cdata_elem:
                        self.handle_data(unescape(rawdata[cursor:cursor2]))
                    else:
                        self.handle_data(rawdata[cursor:cursor2])
                cursor = self.updatepos(cursor, cursor2)
            elif startswith("&#", cursor):
                match = charref.match(rawdata, cursor)
                if match:
                    name = match.group()[2:-1]
                    self.handle_charref(name)
                    cursor2 = match.end()
                    if not startswith(";", cursor2 - 1):
                        cursor2 = cursor2 - 1
                    cursor = self.updatepos(cursor, cursor2)
                    continue

                if ";" in rawdata[cursor:]:  # bail by consuming &#
                    self.handle_data(rawdata[cursor : cursor + 2])
                    cursor = self.updatepos(cursor, cursor + 2)
                break
            elif startswith("&", cursor):
                match = entityref.match(rawdata, cursor)
                if match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    cursor2 = match.end()
                    if not startswith(";", cursor2 - 1):
                        cursor2 = cursor2 - 1
                    cursor = self.updatepos(cursor, cursor2)
                    continue
                match = incomplete.match(rawdata, cursor)
                if match:
                    # match.group() will contain at least 2 chars
                    if end and match.group() == rawdata[cursor:]:
                        cursor2 = match.end()
                        if cursor2 <= cursor:
                            cursor2 = size
                        cursor = self.updatepos(cursor, cursor + 1)
                    # incomplete
                    break
                elif (cursor + 1) < size:
                    # not the end of the buffer, and can't be confused
                    # with some other construct
                    self.handle_data("&")
                    cursor = self.updatepos(cursor, cursor + 1)
                else:
                    break
            else:
                assert 0, "interesting.search() lied"  # noqa: WPS444 (copied from source)
        # end while
        if end and cursor < size and not self.cdata_elem:
            if self.convert_charrefs and not self.cdata_elem:
                self.handle_data(unescape(rawdata[cursor:size]))
            else:
                self.handle_data(rawdata[cursor:size])
            cursor = self.updatepos(cursor, size)
        self.rawdata = rawdata[cursor:]
