"""Bounded scanner regressions on software-only fixtures, not browser evidence."""
import importlib.util
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    'offline_artifact_scanner', Path(__file__).with_name('test_app_offline.py'))
OFFLINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OFFLINE)

HEAD = '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width">'
TAIL = '</html>'


class ArtifactScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'software-only.html'

    def scan(self, text):
        self.path.write_bytes(text.encode('utf-8') if isinstance(text, str) else text)
        return OFFLINE.scan_artifact(self.path)

    def assert_matches_full_parser(self, middle):
        text = HEAD + middle + TAIL
        expected = OFFLINE.ArtifactParser()
        expected.feed(text)
        expected.close()
        actual = self.scan(text)['parser']
        for name in ('dependencies', 'ids', 'lang', 'viewport', 'in_script', 'script_type'):
            self.assertEqual(getattr(expected, name), getattr(actual, name), name)
        self.assertEqual(''.join(expected.scripts), ''.join(actual.scripts))
        return actual

    def test_json_opening_tags_keep_ids_and_dependencies(self):
        parser = self.assert_matches_full_parser(
            '<script type="application/json" id="same" src="https://example.invalid/data">'
            '{"fake":"<img src=remote.png>","sw":"serviceWorker.register("}</script>'
            '<div id="same"></div><script src="local.js">const x=1;</script>')
        self.assertEqual(['same', 'same'], parser.ids)
        self.assertEqual(2, len(parser.dependencies))
        self.assertNotIn('serviceWorker', ''.join(parser.scripts))

    def test_parser_equivalence_for_quotes_comments_case_and_raw_text(self):
        cases = [
            '<SCRIPT TYPE="application/json" id="bank" data-note=">">{"a":1}</SCRIPT>'
            '<img src="remote.png">',
            "<script type='application/json' data-note='>' id='bank'>{}</script>",
            '<script type="application&#x2f;json" id="bank">{}</script>',
            '<!-- <script type="application/json"> -->'
            '<script type="application/json" id="bank">{}</script><img src="remote.png">',
            '<!-- <script type="application/json"> never an element -->',
            '<div title="<script type=application/json>">x</div>'
            '<script type="application/json">{}</script>',
            '<style>/* <script type="application/json"> */ body{color:red}</style>'
            '<script type="application/json">{}</script>',
            '<script>const literal = "<script type=application/json>";'
            'navigator.serviceWorker.register("offline.js");</script>',
            '<script type="APPLICATION/JSON">serviceWorker.register("kept")</script>',
            '<script type="application/json"/><img src="remote.png">',
            '<script type="application/json">{"a":"</scriptx>"}</script>',
            '<script type="application/json">{"a":"<\\/script>"}</script>',
            '<script type="application/json">{"a":"</script><img src="remote.png">"}',
        ]
        for middle in cases:
            with self.subTest(middle=middle):
                self.assert_matches_full_parser(middle)

    def test_active_parser_end_tag_forms_do_not_hide_following_dom(self):
        for ending in ('</script>', '</SCRIPT>', '</script >', '</script\n>',
                       '</script data-x>', '</script/>', '</script / >'):
            with self.subTest(ending=ending):
                # Older Python parsers may treat unusual forms as raw text.
                # Match the active reference parser rather than inventing HTML rules.
                self.assert_matches_full_parser(
                    '<script type="application/json">{}' + ending
                    + '<img id="after" src="https://example.invalid/required.png">'
                    '<script type="application/json">{}</script>')

    def test_json_payload_never_reaches_html_parser(self):
        lengths = []
        original = OFFLINE.ArtifactParser

        class ObservedParser(original):
            def feed(self, data):
                lengths.append(len(data))
                return super().feed(data)

        text = HEAD + '<!-- <script type="application/json"> -->'
        text += '<script type="application/json" id="bank">{"data":"'
        text += 'A' * (4 * 1024 * 1024)
        text += '"}</script><img id="after" src="remote.png">' + TAIL
        with patch.object(OFFLINE, 'ArtifactParser', ObservedParser):
            parser = self.scan(text)['parser']
        self.assertLess(max(lengths), 1024)
        self.assertEqual(['bank', 'after'], parser.ids)
        self.assertEqual([('img', 'src', 'remote.png')], parser.dependencies)

    def test_entire_artifact_css_scan_includes_skipped_json(self):
        for expression, key in (
                ('@import "https://example.invalid/style.css"', 'external_import'),
                ('url(//example.invalid/image.png)', 'external_css_url')):
            with self.subTest(expression=expression):
                # Put the dependency far outside either identity buffer.
                text = HEAD + '<script type="application/json">{"data":"'
                text += 'A' * 8192 + expression + 'B' * 8192
                text += '"}</script>' + TAIL
                self.assertTrue(self.scan(text)[key])

    def test_css_byte_patterns_preserve_unicode_string_regex_results(self):
        whitespaces = [chr(code) for code in range(0x110000) if chr(code).isspace()]
        imports = re.compile(r"@import\s+(?:url\()?\s*['\"]?https?://", re.I)
        urls = re.compile(r"url\(\s*['\"]?(?:https?:)?//", re.I)
        for space in whitespaces + [' ', '\n\t', '\u200b', 'x']:
            for expr in (
                    '@import' + space + '"https://example.invalid/x"',
                    '@İmport' + space + 'url(' + space + "'httpſ://example.invalid/x')",
                    '@ımport' + space + 'http://example.invalid/x',
                    'url(' + space + '"https://example.invalid/x")',
                    'URL(' + space + "'HTTPſ://example.invalid/x')",
                    'url(' + space + '//example.invalid/x)'):
                with self.subTest(space=repr(space), expr=expr):
                    raw = expr.encode('utf-8')
                    self.assertEqual(bool(imports.search(expr)), bool(OFFLINE.EXTERNAL_IMPORT.search(raw)))
                    self.assertEqual(bool(urls.search(expr)), bool(OFFLINE.EXTERNAL_CSS_URL.search(raw)))

    def test_utf8_validation_covers_skipped_json_and_chunk_boundaries(self):
        OFFLINE.validate_utf8('aéλ🦾z'.encode('utf-8'), chunk_size=3)
        for bad in (b'\xff', b'\xc3', b'\xed\xa0\x80', b'\xf0\x80\x80\x80'):
            with self.subTest(bad=bad):
                text = HEAD.encode() + b'<script type="application/json">{"data":"'
                with self.assertRaises(UnicodeDecodeError):
                    self.scan(text + bad + b'"}</script>' + TAIL.encode())
        with self.assertRaises(UnicodeDecodeError):
            OFFLINE.validate_utf8(b'ab\xe2\x82', chunk_size=3)

    def test_non_json_service_worker_code_is_retained(self):
        parser = self.assert_matches_full_parser(
            '<script type="application/json">{"fake":"serviceWorker.register("}</script>'
            '<script>navigator.serviceWorker\n . register ("offline.js")</script>')
        self.assertRegex(''.join(parser.scripts), r'serviceWorker\s*\.\s*register\s*\(')

    def test_all_original_dependency_kinds_are_preserved(self):
        elements = [f'<{tag} src="remote-{tag}" srcset="remote-2x 2x" poster="remote-poster">'
                    for tag in ('img', 'iframe', 'source', 'audio', 'video', 'embed', 'input')]
        elements += ['<object data="remote-object"></object>']
        elements += [f'<link rel="{rel}" href="remote-{rel}">'
                     for rel in ('stylesheet', 'preload', 'modulepreload', 'icon', 'manifest')]
        elements += ['<a href="https://example.invalid/citation">ordinary citation</a>',
                     '<script src="remote-script">const ok=true;</script>']
        self.assert_matches_full_parser(''.join(elements))

    def test_unterminated_scripts_are_explicit_failures(self):
        for text in (HEAD + '<script type="application/json">{}' + TAIL,
                     HEAD + '<script>const x=1;</script data-x'):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, 'Unterminated script'):
                    self.scan(text)

    def test_identity_requires_real_header_and_trailer(self):
        gate = OFFLINE.OfflineArtifactTests('test_real_html_not_lfs_pointer')
        gate.scan = self.scan(HEAD + TAIL)
        gate.test_real_html_not_lfs_pointer()
        for text in (
                'version https://git-lfs.github.com/spec/v1\n' + HEAD + TAIL,
                '<html lang="en"></html>',
                HEAD + '<body>truncated',
                HEAD + TAIL + 'x' * 4096):
            with self.subTest(text=text[:80]):
                gate.scan = self.scan(text)
                with self.assertRaises(AssertionError):
                    gate.test_real_html_not_lfs_pointer()


if __name__ == '__main__':
    unittest.main()
