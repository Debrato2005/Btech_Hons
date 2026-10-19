"""Regression tests of data integrity using explicitly synthetic, excluded data."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('robotics_validate', ROOT / 'scripts' / 'validate.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.bank = validator.load_json(ROOT / 'tests' / 'fixtures' / 'synthetic_bank.json')

    def result(self, **kwargs):
        return validator.validate_bank(self.bank, ROOT, allow_synthetic=True, **kwargs)

    def assertError(self, substring, **kwargs):
        result = self.result(**kwargs)
        self.assertFalse(result['valid'], result)
        self.assertTrue(any(substring in error for error in result['errors']), result['errors'])

    def rebind(self):
        self.bank['reviews'][0]['questionSha256'] = validator.question_hash(self.bank['questions'][0])

    def test_fixture_valid_for_tests_only(self):
        result = self.result()
        self.assertTrue(result['valid'], result)
        self.assertEqual(result['counts']['currentlyVerifiedQuestions'], 1)
        self.assertFalse(validator.validate_bank(self.bank, ROOT)['valid'])

    def test_empty_partial_checkpoint_is_valid(self):
        for kind in validator.ENTITY_KEYS:
            self.bank[kind] = []
        self.assertTrue(self.result()['valid'])

    def test_release_rejects_partial_checkpoint(self):
        self.assertError('complete:true', release=True)

    def test_release_rejects_skip_files_cli(self):
        p = subprocess.run([sys.executable, str(ROOT/'scripts/validate.py'), '--release', '--skip-files'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    def test_schema_requires_solution(self):
        del self.bank['questions'][0]['solution']
        self.assertError('missing required field solution')

    def test_schema_rejects_blank_stem(self):
        self.bank['questions'][0]['stem'] = '  '
        self.assertError('nonblank text')

    def test_schema_rejects_boolean_page_number(self):
        self.bank['slides'][0]['physicalPage'] = True
        self.assertError('expected integer')

    def test_duplicate_question_id(self):
        self.bank['questions'].append(copy.deepcopy(self.bank['questions'][0]))
        self.assertError('duplicate ID')

    def test_duplicate_option_id(self):
        self.bank['questions'][0]['options'][1]['id'] = 'synthetic-q1-o0'
        self.assertError('duplicate option IDs')

    def test_duplicate_option_text(self):
        self.bank['questions'][0]['options'][1]['text'] = '0 units'
        self.assertError('duplicate/equivalent option text')

    def test_missing_correct_option(self):
        self.bank['questions'][0]['correctOptionIds'] = ['not-an-option']
        self.assertError('correct answer references missing option IDs')

    def test_single_select_rejects_multiple_correct(self):
        self.bank['questions'][0]['correctOptionIds'].append('synthetic-q1-o1')
        self.assertError('exactly one correct option')

    def test_multi_select_is_valid_with_matching_independent_set(self):
        question = self.bank['questions'][0]
        question['selectionMode'] = 'multi'
        question['correctOptionIds'].append('synthetic-q1-o1')
        self.bank['reviews'][0]['independentAnswerOptionIds'].append('synthetic-q1-o1')
        self.rebind()
        self.assertTrue(self.result()['valid'])

    def test_option_explanations_must_cover_all(self):
        del self.bank['questions'][0]['solution']['optionExplanations']['synthetic-q1-o0']
        self.assertError('optionExplanations must cover exactly every option ID')

    def test_numerical_requires_workings(self):
        self.bank['questions'][0]['solution']['steps'] = []
        self.assertError('needs explicit steps')

    def test_unknown_source_citation(self):
        self.bank['questions'][0]['citations'][0]['sourceId'] = 'missing'
        self.assertError('broken citation source/slide reference')

    def test_citation_page_must_match(self):
        self.bank['questions'][0]['citations'][0]['physicalPage'] = 2
        self.assertError('citation page/source/hash')

    def test_printed_number_not_invented(self):
        self.bank['slides'][0]['printedSlideNumber'] = '1'
        self.assertError('printed slide number and its presence status disagree')

    def test_assignment_pagination_stays_separate(self):
        self.bank['sources'][0]['role'] = 'assignment_solutions'
        self.assertError('combinedLecturePage must be None')

    def test_physical_page_bounds(self):
        self.bank['slides'][0]['physicalPage'] = 2
        self.assertError('exceeds measured source page count')

    def test_complete_visual_inspection_needs_observed_notes(self):
        self.bank['slides'][0]['visualInspection']['notes'] = ''
        self.assertError('observed details')

    def test_text_extraction_not_visual_review(self):
        self.bank['slides'][0]['visualInspection']['status'] = 'pending'
        self.assertError('not actually visually inspected')

    def test_visual_review_needs_timezone(self):
        self.bank['slides'][0]['visualInspection']['inspectedAt'] = '2026-10-19T12:00:00'
        self.assertError('timezone-aware timestamp')

    def test_excluded_page_requires_reason(self):
        self.bank['slides'][0]['disposition'] = 'excluded'
        self.assertError('specific reason')

    def test_repeated_page_requires_incremental_check(self):
        self.bank['slides'][0]['disposition'] = 'repeated'
        self.assertError('incremental-change check')

    def test_source_hash_change_invalidates(self):
        self.bank['sources'][0]['sha256'] = '0' * 64
        self.assertError('source hash is stale')

    def test_file_hash_checked(self):
        self.bank['assets'][0]['sha256'] = '0' * 64
        self.assertError('file SHA-256 mismatch')

    def test_missing_assets_rejected(self):
        self.bank['assets'][0]['path'] = 'does-not-exist.pdf'
        self.assertError('missing file')

    def test_remote_assets_rejected(self):
        self.bank['assets'][0]['path'] = 'https://example.com/asset.pdf'
        self.assertError('not a URL or traversal')

    def test_asset_traversal_rejected(self):
        self.bank['assets'][0]['path'] = '../private.pdf'
        self.assertError('not a URL or traversal')

    def test_self_review_rejected(self):
        self.bank['reviews'][0]['reviewerId'] = 'synthetic-author'
        self.assertError('reviewer is the author')

    def test_review_checks_must_pass(self):
        self.bank['reviews'][0]['checks']['answerSet'] = False
        self.assertError('failed review checks')

    def test_review_answer_must_match(self):
        self.bank['reviews'][0]['independentAnswerOptionIds'] = ['synthetic-q1-o0']
        self.assertError('reviewer answer set differs')

    def test_review_source_binding_must_be_complete(self):
        self.bank['reviews'][0]['sourceVersions'] = {}
        self.assertError('not all cited source versions bound')

    def test_explanation_change_stales_review(self):
        self.bank['questions'][0]['solution']['justification'] += ' New content.'
        self.assertError('stale content/source binding')

    def test_question_version_change_stales_review(self):
        self.bank['questions'][0]['version'] = 2
        self.assertError('stale content/source binding')

    def test_status_and_review_links_do_not_change_content_hash(self):
        question = self.bank['questions'][0]
        before = validator.question_hash(question)
        question['status'] = 'draft'
        question['reviewIds'] = []
        self.assertEqual(before, validator.question_hash(question))

    def test_option_reordering_is_correctness_preserving_but_review_bound(self):
        question = self.bank['questions'][0]
        original_answer = question['correctOptionIds'][:]
        question['options'].reverse()
        self.assertEqual(original_answer, question['correctOptionIds'])
        self.assertError('stale content/source binding')

    def test_historical_stale_review_allowed_for_draft(self):
        self.bank['questions'][0]['status'] = 'draft'
        self.bank['questions'][0]['stem'] += ' Updated draft.'
        self.bank['concepts'][0]['status'] = 'drafted'
        result = self.result()
        self.assertTrue(result['valid'], result)
        self.assertEqual(result['counts']['staleReviews'], 1)

    def test_verified_status_requires_review(self):
        self.bank['questions'][0]['reviewIds'] = []
        self.assertError('lacks a current independent acceptance review')

    def test_nonblind_review_disclosed(self):
        self.bank['reviews'][0]['solvedBeforeAnswerSeen'] = False
        result = self.result()
        self.assertTrue(result['valid'], result)
        self.assertTrue(any('not blind' in w for w in result['warnings']))

    def test_reciprocal_concept_link_required(self):
        self.bank['concepts'][0]['questionIds'] = []
        self.assertError('lacks reciprocal question link')

    def test_variant_family_must_exist(self):
        self.bank['questions'][0]['variant'] = {'familyId':'missing','generatorVersion':'1','seed':'1','parameters':{},'rounding':'none','units':{}}
        self.assertError('variant familyId is missing')

    def test_normalized_region_must_fit_page(self):
        self.bank['questions'][0]['citations'][0]['region'] = {'x':.7,'y':0,'width':.5,'height':1}
        self.assertError('extends outside page')

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'duplicate.json'
            path.write_text('{"id":1,"id":2}')
            with self.assertRaisesRegex(ValueError, 'Duplicate JSON object key'):
                validator.load_json(path)

    def test_nonfinite_json_number_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'nan.json'
            path.write_text('{"value": NaN}')
            with self.assertRaisesRegex(ValueError, 'Non-finite JSON number'):
                validator.load_json(path)

    def test_distinct_math_signs_not_normalized_away(self):
        self.assertNotEqual(validator.normalized_text('-1'), validator.normalized_text('1'))
        self.assertNotEqual(validator.normalized_text('1.5'), validator.normalized_text('15'))
        self.assertNotEqual(validator.normalized_text('x+y'), validator.normalized_text('x-y'))
        self.assertNotEqual(validator.normalized_text('m'), validator.normalized_text('M'))
        self.assertNotEqual(validator.normalized_text('x²'), validator.normalized_text('x2'))

    def test_current_flagged_review_blocks_acceptance(self):
        review = copy.deepcopy(self.bank['reviews'][0])
        review['id'] = 'synthetic-r2'
        review['decision'] = 'flagged'
        review['reviewerId'] = 'another-synthetic-reviewer'
        self.bank['reviews'].append(review)
        self.assertError('current independent review dispute is unresolved')

    def test_invalid_question_not_counted_as_currently_verified(self):
        self.bank['questions'][0]['citations'][0]['physicalPage'] = 2
        self.rebind()
        self.assertEqual(self.result()['counts']['currentlyVerifiedQuestions'], 0)

    def test_published_schema_accepts_fixture_in_standard_validator(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest('Optional interoperability check: jsonschema is not installed')
        jsonschema.Draft202012Validator.check_schema(validator.load_json(validator.SCHEMA_PATH))
        jsonschema.validate(self.bank, validator.load_json(validator.SCHEMA_PATH))


if __name__ == '__main__':
    unittest.main()
