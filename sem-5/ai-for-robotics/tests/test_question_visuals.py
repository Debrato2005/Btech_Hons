"""Explicit software fixtures for independent question-input visual gates.

No real source pixels, question reviews, or browser rendering are certified here.
"""
import base64
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result

V = module('test_question_visual_gate', 'question_visuals.py')
B = module('test_visual_build', 'build.py')


def png(width=4, height=4):
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff)
    data = b'\x89PNG\r\n\x1a\n'
    data += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    data += chunk(b'IDAT', zlib.compress((b'\x00' + b'\xff\xff\xff' * width) * height))
    return data + chunk(b'IEND', b'')


class QuestionVisualTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bank = json.loads((ROOT / 'tests/fixtures/synthetic_bank.json').read_text())
        self.q = self.bank['questions'][0]
        ref = {k: self.q['citations'][0][k] for k in ('sourceId', 'sourceSha256', 'slideId', 'physicalPage')}
        data = png(); sha = hashlib.sha256(data).hexdigest()
        self.asset = {'id': 'qv-' + sha, 'path': 'assets/question-visuals/' + sha + '.png', 'mimeType': 'image/png',
                      'sha256': sha, 'width': 4, 'height': 4, **ref, 'cropRectangle': [0, 0, 2, 2],
                      'renderDpi': 144, 'alt': 'SYNTHETIC TEST ONLY: four-pixel white square, not course evidence.'}
        path = self.root / self.asset['path']; path.parent.mkdir(parents=True); path.write_bytes(data)
        self.record = {'id': 'QV-synthetic-q1', 'version': 1, 'authorId': 'visual-fixture-author',
                       'questionId': self.q['id'], 'questionVersion': self.q['version'], 'questionSha256': V.question_hash(self.q),
                       'dependencyStatus': 'required', 'reason': 'Synthetic software test: an input square is required.',
                       'assetIds': [self.asset['id']], 'requiredInputs': ['Synthetic white square'], 'sourceRefs': [ref]}
        self.manifest = {'schemaVersion': '1.0.0', 'authorId': 'visual-manifest-author',
                         'sourceVersions': {ref['sourceId']: ref['sourceSha256']}, 'records': [self.record], 'assets': [self.asset]}
        self.review = {'id': 'QV-review-synthetic-q1', 'visualId': self.record['id'], 'visualVersion': 1,
                       'visualSha256': V.digest(self.record), 'reviewerId': 'independent-visual-fixture-reviewer', 'decision': 'verified',
                       'questionId': self.q['id'], 'questionVersion': self.q['version'], 'questionSha256': V.question_hash(self.q),
                       'sourceVersions': dict(self.manifest['sourceVersions']), 'assetHashes': {self.asset['id']: self.asset['sha256']},
                       'assetMetadataHashes': {self.asset['id']: V.digest(self.asset)}, 'reviewedAssetIds': [self.asset['id']],
                       'displayRole': 'question_input', 'checks': {k: True for k in V.VISUAL_CHECKS}, 'reviewedAt': '2026-10-20T03:00:00Z',
                       'reasoning': 'Synthetic fixture only. Not actual source-pixel approval.'}
        self.reviews = [self.review]; self.save()

    def save(self):
        path = self.root / 'data/question-visuals/manifest.json'; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.manifest))
        path = self.root / 'data/question-visuals/reviews/fixture.json'; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.reviews))

    def prepare(self):
        self.save(); return V.prepare_question_visuals(self.bank, self.root)

    def blocked(self):
        result = self.prepare(); self.assertNotIn(self.q['id'], result['bindings']); self.assertTrue(result['diagnostics']); return result

    def rebind(self):
        self.review['visualSha256'] = V.digest(self.record)
        self.review['visualVersion'] = self.record['version']
        self.review['assetHashes'] = {a['id']: a['sha256'] for a in self.manifest['assets'] if a['id'] in self.record['assetIds']}
        self.review['assetMetadataHashes'] = {a['id']: V.digest(a) for a in self.manifest['assets'] if a['id'] in self.record['assetIds']}
        self.review['reviewedAssetIds'] = list(self.record['assetIds'])

    def install(self):
        sidecar = self.prepare(); self.bank['questionVisuals'] = sidecar
        self.bank['assets'].extend(V.projected_visual_assets(sidecar)); return sidecar

    def test_required_visual_passes_without_question_mutation(self):
        original = copy.deepcopy(self.bank); result = self.prepare()
        self.assertEqual(result['diagnostics'], []); self.assertEqual(self.bank, original)
        binding = result['bindings'][self.q['id']]
        self.assertEqual(binding['assetIds'], [self.asset['id']])
        self.assertEqual(V.digest(json.loads(binding['recordRawJSON'])), binding['recordSha256'])
        rb = result['reviewBindings'][self.review['id']]
        self.assertEqual(hashlib.sha256(rb['rawJSON'].encode()).hexdigest(), rb['reviewSha256'])
        self.assertEqual(V.projected_visual_assets(result), [{**self.asset, 'kind': 'diagram'}])

    def test_self_contained_requires_separate_dependency_review(self):
        self.record.update(dependencyStatus='self_contained', assetIds=[], requiredInputs=[]); self.manifest['assets'] = []
        self.rebind(); self.assertEqual(self.prepare()['diagnostics'], [])
        self.reviews = []; self.blocked()

    def test_missing_inventory_blocks_verified_question(self):
        self.manifest['records'] = []; self.blocked()

    def test_duplicate_inventory_blocks_verified_question(self):
        self.manifest['records'].append(copy.deepcopy(self.record)); self.blocked()

    def test_flagged_duplicate_not_visual_denominator(self):
        self.q['status'] = 'flagged'; self.manifest['records'] = []
        result = self.prepare(); self.assertEqual(result['diagnostics'], []); self.assertEqual(result['bindings'], {})

    def test_missing_visual_review_cannot_use_answer_review(self):
        self.reviews = []; self.blocked()

    def test_answer_review_is_separately_required(self):
        self.bank['reviews'] = []; result = self.blocked()
        self.assertTrue(any('Answer-review eligibility' in r for r in result['diagnostics'][0]['reasons']))

    def test_current_visual_dispute_overrides_acceptance(self):
        dispute = copy.deepcopy(self.review); dispute.update(id='visual-dispute', decision='flagged'); self.reviews.append(dispute); self.blocked()

    def test_stale_question_content_blocks_visual_approval(self):
        self.q['stem'] += ' Changed.'; self.blocked()

    def test_stale_record_content_blocks_visual_approval(self):
        self.record['requiredInputs'].append('Unreviewed input'); self.blocked()

    def test_stale_visual_review_question_binding_blocks(self):
        self.review['questionSha256'] = '0' * 64; self.blocked()

    def test_visual_author_cannot_self_approve(self):
        self.review['reviewerId'] = ' ' + self.record['authorId'] + ' '; self.blocked()

    def test_manifest_author_cannot_self_approve(self):
        self.review['reviewerId'] = self.manifest['authorId']; self.blocked()

    def test_revision_author_cannot_self_approve(self):
        self.record['revisionAuthors'] = [self.review['reviewerId']]; self.rebind(); self.blocked()

    def test_each_independent_check_is_required(self):
        for check in V.VISUAL_CHECKS:
            with self.subTest(check=check):
                self.review['checks'][check] = False; self.blocked(); self.review['checks'][check] = True

    def test_no_answer_leak_check_cannot_be_omitted(self):
        del self.review['checks']['noAnswerLeak']; self.blocked()

    def test_required_record_without_assets_fails(self):
        self.record['assetIds'] = []; self.rebind(); self.blocked()

    def test_required_record_without_input_description_fails(self):
        self.record['requiredInputs'] = []; self.rebind(); self.blocked()

    def test_self_contained_record_cannot_hide_required_assets(self):
        self.record['dependencyStatus'] = 'self_contained'; self.rebind(); self.blocked()

    def test_uninspected_source_fails(self):
        self.bank['slides'][0]['visualInspection']['status'] = 'pending'; self.blocked()

    def test_extra_same_source_premise_page_is_allowed(self):
        slide = copy.deepcopy(self.bank['slides'][0]); slide.update(id='synthetic-page-2', physicalPage=2)
        self.bank['sources'][0]['pageCount'] = 2; self.bank['slides'].append(slide)
        self.record['sourceRefs'][0].update(slideId=slide['id'], physicalPage=2)
        self.asset.update(slideId=slide['id'], physicalPage=2); self.rebind()
        self.assertEqual(self.prepare()['diagnostics'], [])

    def test_asset_metadata_change_invalidates_pixel_review(self):
        self.asset['cropRectangle'] = [0, 0, 1, 1]; self.blocked()

    def test_missing_metadata_hash_cannot_use_only_pixel_hash(self):
        self.review['assetMetadataHashes'] = {}; self.blocked()

    def test_missing_png_fails(self):
        (self.root / self.asset['path']).unlink(); self.blocked()

    def test_changed_png_bytes_fail(self):
        (self.root / self.asset['path']).write_bytes(png(5, 5)); self.blocked()

    def test_rebound_nonpng_bytes_still_fail(self):
        data = b'not a PNG'; (self.root / self.asset['path']).write_bytes(data)
        self.asset['sha256'] = hashlib.sha256(data).hexdigest(); self.rebind(); self.blocked()

    def test_rebound_corrupt_png_still_fails(self):
        data = bytearray(png()); data[44] ^= 1; data = bytes(data)
        (self.root / self.asset['path']).write_bytes(data); self.asset['sha256'] = hashlib.sha256(data).hexdigest(); self.rebind(); self.blocked()

    def test_dimension_mismatch_fails_after_rebinding(self):
        self.asset['width'] = 999; self.rebind(); self.blocked()

    def test_invalid_crop_rectangle_fails_after_rebinding(self):
        self.asset['cropRectangle'] = [2, 0, 1, 2]; self.rebind(); self.blocked()

    def test_path_escape_fails_after_rebinding(self):
        self.asset['path'] = '../outside.png'; self.rebind(); self.blocked()

    def test_duplicate_pixel_bytes_require_one_shared_asset_id(self):
        duplicate = copy.deepcopy(self.asset); duplicate['id'] += '-duplicate'; self.manifest['assets'].append(duplicate)
        self.record['assetIds'].append(duplicate['id']); self.rebind(); self.blocked()

    def test_validator_accepts_current_sidecar_and_asset_projection(self):
        self.install(); self.assertEqual(V.question_visual_errors(self.bank, self.root), [])
        result = V._VALIDATOR.validate_bank(self.bank, self.root, allow_synthetic=True, check_files=False)
        self.assertTrue(result['valid'], result['errors'])

    def test_validator_rejects_missing_required_asset_projection(self):
        self.install(); self.bank['assets'] = [a for a in self.bank['assets'] if a['id'] != self.asset['id']]
        self.assertTrue(V.question_visual_errors(self.bank, self.root))

    def test_validator_rejects_forged_ready_binding(self):
        self.install(); self.bank['questionVisuals']['bindings'][self.q['id']]['recordSha256'] = 'f' * 64
        self.assertTrue(V.question_visual_errors(self.bank, self.root))

    def test_validator_rejects_stale_source_manifest(self):
        self.install(); self.record['reason'] += ' New assessment.'; self.save()
        self.assertTrue(V.question_visual_errors(self.bank, self.root))

    def test_validator_rejects_missing_course_inventory(self):
        self.bank.pop('synthetic'); self.assertTrue(V.question_visual_errors(self.bank, self.root))

    def test_build_selects_required_png_and_preserves_original_pdf(self):
        self.install(); chosen = B.selected_assets(self.bank)
        self.assertIn(self.asset['id'], {a['id'] for a in chosen})
        self.assertTrue(any(a['kind'] == 'source_pdf' for a in chosen))
        self.assertEqual(len([a for a in chosen if a['id'] == self.asset['id']]), 1)

    def test_embedded_png_is_byte_identical_and_shared(self):
        self.install(); handle = io.StringIO()
        with patch.object(B, 'ROOT', self.root):
            B.stream_assets(handle, V.projected_visual_assets(self.bank['questionVisuals']))
        payload = json.loads(handle.getvalue()); self.assertEqual(len(payload), 1)
        self.assertEqual(base64.b64decode(payload[self.asset['id']]['data']), (self.root / self.asset['path']).read_bytes())

    def test_build_rejects_asset_change_during_embedding(self):
        self.install(); (self.root / self.asset['path']).write_bytes(png(5, 5))
        with patch.object(B, 'ROOT', self.root):
            with self.assertRaisesRegex(ValueError, 'changed during build'):
                B.stream_assets(io.StringIO(), V.projected_visual_assets(self.bank['questionVisuals']))

    def test_milestone_manifest_includes_visual_inputs_and_pixels(self):
        import ast
        script = ROOT / 'scripts/record_validated_milestone.py'
        tree = ast.parse(script.read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'input_manifest')
        scope = {'R': self.root, 'hashfile': lambda p: hashlib.sha256(p.read_bytes()).hexdigest()}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(script), 'exec'), scope)
        inputs = scope['input_manifest']()
        for path in ('data/question-visuals/manifest.json', 'data/question-visuals/reviews/fixture.json', self.asset['path']):
            self.assertEqual(inputs[path], hashlib.sha256((self.root / path).read_bytes()).hexdigest())

    def test_schema_rejects_malformed_visual_binding(self):
        self.install(); self.bank['questionVisuals']['bindings'][self.q['id']]['questionSha256'] = 'bad'
        result = V._VALIDATOR.validate_bank(self.bank, self.root, allow_synthetic=True, check_files=False)
        self.assertFalse(result['valid']); self.assertTrue(any('questionVisuals' in e for e in result['errors']))


if __name__ == '__main__':
    unittest.main()
