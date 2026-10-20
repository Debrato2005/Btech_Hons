"""Static offline artifact checks; browser behavior is tested separately.

Run: python -m unittest discover -s tests -p 'test_app*.py' -v
Scanner regressions: python -m unittest discover -s tests -p 'test_artifact_scanner.py' -v
Set ROBOTICS_HTML to test a particular release/downloaded artifact.
Missing artifact is a skip, never evidence that a release passed.
"""
import codecs
import os
import mmap
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = [ROOT / "dist/ai-for-robotics-mcq.html", ROOT / "ai-for-robotics-mcq.html"]

# Preserve the former Unicode regex behavior while scanning mapped UTF-8 bytes.
# Python's Unicode \s includes these characters in addition to ASCII whitespace.
UTF8_SPACE = (rb"(?:[\t\n\v\f\r\x1c-\x20]|\xc2[\x85\xa0]|\xe1\x9a\x80|"
              rb"\xe2(?:\x80[\x80-\x8a\xa8\xa9\xaf]|\x81\x9f)|\xe3\x80\x80)")
UNICODE_I = rb"(?:i|\xc4\xb0|\xc4\xb1)"
UNICODE_S = rb"(?:s|\xc5\xbf)"
EXTERNAL_IMPORT = re.compile(
    rb"@" + UNICODE_I + rb"mport" + UTF8_SPACE + rb"+(?:url\()?" + UTF8_SPACE
    + rb"*['\"]?http" + UNICODE_S + rb"?://", re.I)
EXTERNAL_CSS_URL = re.compile(rb"url\(" + UTF8_SPACE + rb"*['\"]?(?:http" + UNICODE_S + rb"?:)?//", re.I)


def validate_utf8(raw, chunk_size=1024 * 1024):
    """Keep read_text's strict UTF-8 guarantee, including skipped JSON bodies."""
    decoder = codecs.getincrementaldecoder('utf-8')('strict')
    for start in range(0, len(raw), chunk_size):
        decoder.decode(raw[start:start + chunk_size])
    decoder.decode(b'', final=True)


def script_end_pattern(parser):
    """Use this Python HTMLParser's raw-text delimiter, not a stricter guess.

    Modern HTMLParser accepts end tags with attributes or a trailing slash.
    Older versions use a different, Unicode-whitespace-aware delimiter.
    Mirroring the active parser prevents skipping real DOM after either form.
    """
    pattern = parser.interesting.pattern.encode('ascii')
    flags = parser.interesting.flags
    if not flags & re.ASCII:
        pattern = pattern.replace(rb'\s', UTF8_SPACE).replace(
            b'script', UNICODE_S + rb'cr' + UNICODE_I + rb'pt')
    return re.compile(pattern, flags & ~(re.UNICODE | re.ASCII))


class ArtifactParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dependencies = []
        self.ids = []
        self.lang = None
        self.viewport = None
        self.scripts = []
        self.in_script = False
        self.script_type = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "meta" and attrs.get("name") == "viewport":
            self.viewport = attrs.get("content")
        if tag == "script":
            self.in_script = True
            self.script_type = attrs.get("type", "")
        # Ordinary citation anchors are not runtime dependencies.
        if tag in {"script", "img", "iframe", "source", "audio", "video", "embed", "input"}:
            for key in ("src", "srcset", "poster"):
                if attrs.get(key):
                    self.dependencies.append((tag, key, attrs[key]))
        if tag == "object" and attrs.get("data"):
            self.dependencies.append((tag, "data", attrs["data"]))
        if tag == "link" and attrs.get("rel", "").lower() in {
            "stylesheet", "preload", "modulepreload", "icon", "manifest"
        } and attrs.get("href"):
            self.dependencies.append((tag, "href", attrs["href"]))

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_script and self.script_type != "application/json":
            self.scripts.append(data)


def scan_artifact(path):
    """Scan exact artifact bytes without copying its large JSON/base64 payloads.

    HTMLParser normally buffers an entire script raw-text section. JSON script
    bodies are data, not DOM or executable JavaScript, so only their actual
    opening/closing tags go to the parser. Non-JSON script bodies remain parsed.
    CSS dependency expressions still scan every byte, including the JSON data.
    """
    parser = ArtifactParser()
    opening = re.compile(rb"<script\b(?:\"[^\"]*\"|'[^']*'|[^'\">])*>", re.I)
    with Path(path).open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as raw:
        validate_utf8(raw)
        position = 0
        while match := opening.search(raw, position):
            parser.feed(raw[position:match.end()].decode('utf-8'))
            position = match.end()
            # A script-shaped string inside a comment, attribute or style is not
            # an element. Continue searching without buffering its alleged body.
            if parser.cdata_elem != 'script':
                continue
            end = script_end_pattern(parser).search(raw, position)
            if end is None:
                raise ValueError('Unterminated script in offline artifact.')
            end_position = raw.find(b'>', end.start()) + 1
            if not end_position:
                raise ValueError('Unterminated script end tag in offline artifact.')
            if not (parser.in_script and parser.script_type == 'application/json'):
                parser.feed(raw[position:end.start()].decode('utf-8'))
            parser.feed(raw[end.start():end_position].decode('utf-8'))
            position = end_position
        parser.feed(raw[position:].decode('utf-8'))
        parser.close()
        return {
            'parser': parser,
            'head': raw[:2048],
            'tail': raw[-2048:],
            'external_import': EXTERNAL_IMPORT.search(raw) is not None,
            'external_css_url': EXTERNAL_CSS_URL.search(raw) is not None,
        }


class OfflineArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        supplied = os.getenv("ROBOTICS_HTML")
        candidates = [Path(supplied)] if supplied else DEFAULT_CANDIDATES
        cls.path = next((path for path in candidates if path.is_file()), None)
        if cls.path is None:
            raise unittest.SkipTest("Release HTML has not been built; offline release gate remains pending.")
        cls.scan = scan_artifact(cls.path)
        cls.parser = cls.scan['parser']

    def test_real_html_not_lfs_pointer(self):
        self.assertNotIn(b"version https://git-lfs.github.com/spec/v1", self.scan['head'])
        self.assertRegex(self.scan['head'].lower(), rb"<!doctype\s+html")
        self.assertIn(b"</html>", self.scan['tail'].lower())

    def test_semantic_document_basics(self):
        self.assertTrue(self.parser.lang, "Document must state its language")
        self.assertTrue(self.parser.viewport, "Responsive viewport metadata missing")
        self.assertEqual(len(self.parser.ids), len(set(self.parser.ids)), "Duplicate DOM IDs")

    def test_no_external_required_asset(self):
        bad = [(tag, key, value[:160]) for tag, key, value in self.parser.dependencies
               if not value.startswith(("data:", "blob:", "#"))]
        self.assertEqual([], bad, "Required resources must be embedded in the one-file artifact")

    def test_no_external_css_dependency(self):
        self.assertFalse(self.scan['external_import'])
        self.assertFalse(self.scan['external_css_url'])

    def test_no_service_worker_requirement(self):
        scripts = "\n".join(self.parser.scripts)
        self.assertNotRegex(scripts, r"serviceWorker\s*\.\s*register\s*\(",
                            "file:// artifact cannot require a service worker")


if __name__ == "__main__":
    unittest.main()
