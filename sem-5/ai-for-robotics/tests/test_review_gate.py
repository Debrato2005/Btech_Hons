import copy
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from review_gate import apply_review_gate
from validate import question_hash

class ReviewGateTests(unittest.TestCase):
    def setUp(self):
        self.bank = json.loads((ROOT/'tests/fixtures/synthetic_bank.json').read_text())
    def run_gate(self):
        b=self.bank
        return apply_review_gate(b['questions'],b['reviews'],b['slides'],b['sources'])
    def test_accepts_current_independent_review(self):
        self.assertEqual(self.run_gate(),[])
        self.assertEqual(self.bank['questions'][0]['status'],'verified')
    def test_unresolved_page_is_quarantined(self):
        self.bank['slides'][0]['disposition']='unresolved'
        self.assertTrue(self.run_gate())
        self.assertEqual(self.bank['questions'][0]['status'],'flagged')
    def test_uninspected_page_is_quarantined(self):
        self.bank['slides'][0]['visualInspection']['status']='pending'
        self.assertTrue(self.run_gate())
        self.assertEqual(self.bank['questions'][0]['status'],'flagged')
    def test_missing_reviewed_page_cannot_approve(self):
        self.bank['reviews'][0]['reviewedSlideIds']=[]
        self.run_gate()
        self.assertEqual(self.bank['questions'][0]['status'],'draft')
    def test_changed_source_version_cannot_approve(self):
        self.bank['sources'][0]['sha256']='f'*64
        self.run_gate()
        self.assertEqual(self.bank['questions'][0]['status'],'draft')
    def test_revision_author_cannot_self_approve(self):
        q=self.bank['questions'][0];r=self.bank['reviews'][0]
        q['revisionAuthors']=[r['reviewerId']]
        r['questionSha256']=question_hash(q)
        self.run_gate()
        self.assertEqual(q['status'],'draft')
    def test_current_dispute_beats_acceptance(self):
        r=copy.deepcopy(self.bank['reviews'][0]);r['id']+='-dispute';r['decision']='flagged';self.bank['reviews'].append(r)
        self.run_gate()
        self.assertEqual(self.bank['questions'][0]['status'],'flagged')
    def test_gate_preserves_correctness_sensitive_hash(self):
        q=self.bank['questions'][0];before=question_hash(q)
        self.bank['slides'][0]['disposition']='unresolved';self.run_gate()
        self.assertEqual(before,question_hash(q))

if __name__=='__main__':unittest.main()
