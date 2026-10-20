"""Lossless packaging/identity tests; all artifacts are isolated software fixtures."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('package_delivery', ROOT / 'scripts/package_delivery.py')
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


class DeliveryPackageTests(unittest.TestCase):
    def test_practice_package_carries_only_current_scope_support(self):
        self.report['applicationScope'] = 'practice-only'
        self.save_report()
        for relative in ['tests/browser_practice.js', 'docs/CURRENT_SCOPE.md']:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('Practice-only support fixture')
        output = self.root / 'practice.zip'
        receipt, _ = PACKAGE.package(self.html, self.report_path, output, allow_partial=True, project_root=self.root)
        self.assertEqual(receipt['classification'], 'practice-only-verified-bank')
        with zipfile.ZipFile(output) as archive:
            self.assertIn('docs/CURRENT_SCOPE.md', archive.namelist())
            self.assertNotIn('tests/browser_final_artifact.js', archive.namelist())
            self.assertNotIn('tests/browser_learning_resources_artifact.js', archive.namelist())
            self.assertIn('Answers and bookmarks save automatically', archive.read('README-delivery.txt').decode())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        payload = b'%PDF-1.4\nSOFTWARE FIXTURE ONLY, NOT A COURSE SOURCE\n'
        sha = hashlib.sha256(payload).hexdigest()
        self.asset = {'id': 'software-only-source', 'kind': 'source_pdf', 'bytes': len(payload), 'sha256': sha}
        encoded = {'id': self.asset['id'], 'kind': 'source_pdf', 'sha256': sha, 'data': base64.b64encode(payload).decode()}
        self.html = self.root / 'software-only.html'
        self.html.write_text('<!doctype html><html><script type="application/json" id="asset-data">' + json.dumps({encoded['id']: encoded}, separators=(',', ':')) + '</script></html>')
        self.report = {'bankVersion': 'SOFTWARE-ONLY', 'complete': False, 'syntheticTestFixture': False, 'validation': {'valid': True}, 'bytes': self.html.stat().st_size, 'sha256': PACKAGE.digest_file(self.html), 'embeddedAssets': [self.asset]}
        self.report_path = self.root / 'software-only.build-report.json'
        self.save_report()

    def save_report(self):
        self.report_path.write_text(json.dumps(self.report))

    def test_embedded_decoded_bytes_are_checked(self):
        checked = PACKAGE.verify_embedded_assets(self.html, [self.asset])
        self.assertEqual(checked[0]['embeddedByteIdentity'], 'verified')
        with self.assertRaisesRegex(ValueError, 'metadata differs'):
            PACKAGE.verify_embedded_assets(self.html, [{**self.asset, 'sha256': '0' * 64}])

    def test_partial_is_explicit_and_zip_is_lossless(self):
        output = self.root / 'software-only.zip'
        with self.assertRaisesRegex(ValueError, 'incomplete checkpoint'):
            PACKAGE.package(self.html, self.report_path, output)
        receipt, receipt_path = PACKAGE.package(self.html, self.report_path, output, allow_partial=True)
        self.assertEqual(receipt['classification'], 'partial-course-checkpoint')
        self.assertEqual(receipt['browserValidation']['status'], 'pending')
        self.assertEqual(receipt['verifiedZipRoundTrip']['status'], 'passed')
        self.assertEqual(json.loads(receipt_path.read_text())['archive']['sha256'], PACKAGE.digest_file(output))
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.read('ai-for-robotics-mcq.html'), self.html.read_bytes())
            self.assertIn('tests/browser_final_artifact.js', archive.namelist())
            self.assertIn('docs/OPEN_AND_STUDY.md', archive.namelist())

    def test_complete_flag_without_release_validation_is_still_checkpoint(self):
        self.report['complete'] = True
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'lacks release validation'):
            PACKAGE.package(self.html, self.report_path, self.root / 'unreleased.zip')
        receipt, _ = PACKAGE.package(self.html, self.report_path, self.root / 'unreleased.zip', allow_partial=True)
        self.assertEqual(receipt['classification'], 'partial-course-checkpoint')
        self.assertFalse(receipt['releaseValidated'])

    def test_report_and_all_embedded_bytes_remain_exact_in_zip(self):
        receipt, _ = PACKAGE.package(self.html, self.report_path, self.root / 'identity.zip', allow_partial=True)
        with zipfile.ZipFile(self.root / 'identity.zip') as archive:
            report_bytes = archive.read('ai-for-robotics-mcq.build-report.json')
        self.assertEqual(report_bytes, self.report_path.read_bytes())
        self.assertEqual(hashlib.sha256(report_bytes).hexdigest(), receipt['buildReportSha256'])

    def test_wrong_report_and_synthetic_deliverable_are_refused(self):
        self.report['sha256'] = '0' * 64
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'do not match'):
            PACKAGE.package(self.html, self.report_path, self.root / 'bad.zip', allow_partial=True)
        self.report['syntheticTestFixture'] = True
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'Synthetic'):
            PACKAGE.package(self.html, self.report_path, self.root / 'synthetic.zip', allow_partial=True)


if __name__ == '__main__':
    unittest.main()
