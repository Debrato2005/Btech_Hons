"""Static offline artifact checks; browser behavior is tested separately.

Run: python -m unittest discover -s tests -p 'test_app*.py' -v
Set ROBOTICS_HTML to test a particular release/downloaded artifact.
Missing artifact is a skip, never evidence that a release passed.
"""
import os
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = [ROOT / "dist/ai-for-robotics-mcq.html", ROOT / "ai-for-robotics-mcq.html"]


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


class OfflineArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        supplied = os.getenv("ROBOTICS_HTML")
        candidates = [Path(supplied)] if supplied else DEFAULT_CANDIDATES
        cls.path = next((path for path in candidates if path.is_file()), None)
        if cls.path is None:
            raise unittest.SkipTest("Release HTML has not been built; offline release gate remains pending.")
        cls.text = cls.path.read_text(encoding="utf-8")
        cls.parser = ArtifactParser()
        cls.parser.feed(cls.text)

    def test_real_html_not_lfs_pointer(self):
        self.assertNotIn("version https://git-lfs.github.com/spec/v1", self.text[:200])
        self.assertRegex(self.text.lower(), r"<!doctype\s+html")
        self.assertIn("</html>", self.text.lower())

    def test_semantic_document_basics(self):
        self.assertTrue(self.parser.lang, "Document must state its language")
        self.assertTrue(self.parser.viewport, "Responsive viewport metadata missing")
        self.assertEqual(len(self.parser.ids), len(set(self.parser.ids)), "Duplicate DOM IDs")

    def test_no_external_required_asset(self):
        bad = [(tag, key, value[:160]) for tag, key, value in self.parser.dependencies
               if not value.startswith(("data:", "blob:", "#"))]
        self.assertEqual([], bad, "Required resources must be embedded in the one-file artifact")

    def test_no_external_css_dependency(self):
        self.assertIsNone(re.search(r"@import\s+(?:url\()?\s*['\"]?https?://", self.text, re.I))
        self.assertIsNone(re.search(r"url\(\s*['\"]?(?:https?:)?//", self.text, re.I))

    def test_no_service_worker_requirement(self):
        scripts = "\n".join(self.parser.scripts)
        self.assertNotRegex(scripts, r"serviceWorker\s*\.\s*register\s*\(",
                            "file:// artifact cannot require a service worker")


if __name__ == "__main__":
    unittest.main()
