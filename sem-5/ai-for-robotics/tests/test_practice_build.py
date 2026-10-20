"""Production projection and lazy packaging regressions."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from practice_projection import project
from validate import question_hash
from embedded_payloads import assets, recover
from package_delivery import verify_embedded_assets


class PracticeBuildTests(unittest.TestCase):
    def fixture(self):
        q = {'id': 'stable', 'version': 1, 'status': 'verified', 'options': [{'id': 'answer', 'text': 'A'}], 'correctOptionIds': ['answer'], 'solution': {'steps': ['preserve']}, 'citations': [{'slideId': 's1'}], 'conceptIds': ['c1']}
        binding = {'questionVersion': 1, 'questionSha256': question_hash(q), 'assetIds': ['figure'], 'supplementalInputIds': ['code']}
        return {'schemaVersion': '1', 'bankVersion': 'same', 'title': 'course', 'questions': [q, {**q, 'id': 'excluded', 'status': 'flagged'}], 'sources': [{'id': 'original'}], 'slides': [{'id': 's1', 'physicalPage': 1, 'printedSlideNumber': 9}], 'concepts': [{'id': 'c1', 'title': 'concept'}], 'questionVisuals': {'bindings': {'stable': binding}, 'supplementalInputs': [{'id': 'code', 'text': 'print(x)'}]}, 'reviews': ['development only'], 'learningTools': ['development only']}

    def test_projection_retains_complete_verified_questions_and_inputs(self):
        b = self.fixture()
        result = project(b)
        self.assertEqual(result['questions'], [b['questions'][0]])
        self.assertEqual(result['bankVersion'], b['bankVersion'])
        self.assertEqual(result['practiceInputs']['stable']['assetIds'], ['figure'])
        self.assertEqual(result['supplementalInputs']['code']['text'], 'print(x)')
        self.assertEqual(result['slides'][0]['printedSlideNumber'], 9)
        self.assertNotIn('reviews', result)
        self.assertNotIn('learningTools', result)

    def test_stale_question_input_binding_stops_projection(self):
        b = self.fixture()
        b['questions'][0]['solution']['steps'] = ['changed']
        with self.assertRaisesRegex(ValueError, 'missing or stale'):
            project(b)

    def test_lazy_metadata_handles_quoted_braces_and_checks_original_bytes(self):
        payload = b'%PDF-1.4\noriginal fixture bytes'
        sha = hashlib.sha256(payload).hexdigest()
        asset = {'id': 'pdf', 'sha256': sha, 'kind': 'source_pdf', 'bytes': len(payload)}
        metadata = {**asset, 'alt': 'a } brace and "quoted" text', 'payloadId': 'blob-0', 'path': 'sources/raw/test.pdf'}
        html = '<!doctype html><script type="application/json" id="asset-data">' + json.dumps({'pdf': metadata}, separators=(',', ':')) + '</script><script type="application/octet-stream" id="blob-0">' + base64.b64encode(payload).decode() + '</script>'
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'test.html'
            p.write_text(html)
            self.assertEqual(verify_embedded_assets(p, [asset])[0]['embeddedByteIdentity'], 'verified')
            p.write_text(html.replace(base64.b64encode(payload).decode(), 'YQ=='))
            with self.assertRaisesRegex(ValueError, 'differ'):
                verify_embedded_assets(p, [asset])

    def test_practice_recovery_never_replaces_canonical_review_bank(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / 'data/bank.json'
            target.parent.mkdir()
            target.write_text('{"reviews":["keep"]}')
            html = root / 'practice.html'
            html.write_text('<script type="application/json" id="bank-data">{"scope":"practice-only"}</script><script type="application/json" id="asset-data">{}</script>')
            recover(html, root)
            self.assertEqual(json.loads(target.read_text()), {'reviews': ['keep']})
            self.assertTrue((root / 'dist/recovered-practice-bank.json').exists())


if __name__ == '__main__':
    unittest.main()
