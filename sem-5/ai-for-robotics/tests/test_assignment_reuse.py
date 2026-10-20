"""Synthetic, deterministic reuse-provenance tests; no source review is implied."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('reuse_assembler',ROOT/'scripts/assemble_bank.py')
assembler=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(assembler)
validator=assembler._reuse_validator()


class AssignmentReuseTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.bank=json.loads((ROOT/'tests/fixtures/synthetic_bank.json').read_text())
  self.bank['sources'][0]['role']='assignment_solutions'
  self.bank['slides'][0]['combinedLecturePage']=None
  self.target=self.bank['questions'][0];self.target_review=self.bank['reviews'][0]
  duplicate=copy.deepcopy(self.target);duplicate.update(id='synthetic-duplicate',status='flagged',assignmentSourceItemId='synthetic-source-item',reviewIds=[],conceptIds=['synthetic-assignment'])
  self.bank['questions'].append(duplicate);self.duplicate=duplicate
  concept=copy.deepcopy(self.bank['concepts'][0]);concept.update(id='synthetic-assignment',status='drafted',questionIds=[duplicate['id']])
  self.bank['concepts'].append(concept);self.bank['slides'][0]['conceptIds'].append(concept['id'])
  self.original={'id':'synthetic-source-item','sourceId':'synthetic-source','sourceSha256':self.bank['sources'][0]['sha256'],'physicalPages':[1]}
  self.original_path='audits/assignment-originals/synthetic.json';self.write(self.original_path,self.original)
  self.mapping={'id':'synthetic-reuse','sourceItemId':self.original['id'],'assignmentConceptId':concept['id'],
   'sourceId':self.original['sourceId'],'sourceSha256':self.original['sourceSha256'],'physicalPages':[1],
   'originalRecordPath':self.original_path,'originalRecordSha256':self.sha(self.original_path),
   'duplicateQuestionId':duplicate['id'],'duplicateQuestionSha256':validator.question_hash(duplicate),
   'primaryReusedQuestionId':self.target['id'],'reusedQuestionIds':[self.target['id']],
   'reusedQuestions':[{'questionId':self.target['id'],'questionVersion':self.target['version'],'questionSha256':validator.question_hash(self.target),
    'reviewIds':[self.target_review['id']],'sourceSlideIds':['synthetic-page-1']}]}
  self.batch={'authorId':'synthetic-mapping-author','mappings':[self.mapping],'proposedAdditionalUniqueQuestions':0,'duplicatesToExcludeFromVerifiedPool':[duplicate['id']]}
  self.batch_path='data/assignment-reuse-batches/synthetic.json';self.write(self.batch_path,self.batch)
  self.review={'id':'synthetic-mapping-review','reviewerId':'synthetic-mapping-reviewer','reviewType':'independent_source_item_reuse_mapping',
   'decision':'verified','mappingPath':self.batch_path,'mappingSha256':self.sha(self.batch_path),'mappingReviews':[
    {'mappingId':self.mapping['id'],'sourceItemId':self.original['id'],'decision':'verified','sourcePages':[1],
     'reusedQuestionHashes':{self.target['id']:validator.question_hash(self.target)},'additionalUniqueQuestions':0,'originalRecordPreserved':True,'duplicateExclusionRequired':duplicate['id']}]}
  self.review_path='data/assignment-reuse-reviews/synthetic.json';self.write(self.review_path,self.review)

 def write(self,path,value):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
 def sha(self,path):return hashlib.sha256((self.root/path).read_bytes()).hexdigest()
 def build(self,**kwargs):return assembler.build_assignment_reuse(self.bank,self.root,**kwargs)
 def assert_closed(self,**kwargs):
  result=self.build(**kwargs);self.assertEqual(result['links'],[],result);self.assertEqual(result['bySourceItem'],{});self.assertEqual(result['byQuestion'],{});self.assertEqual(result['byConcept'],{});self.assertTrue(result['diagnostics'])
 def save_review(self):self.write(self.review_path,self.review)
 def test_approved_mapping_has_two_way_links_without_question_mutation(self):
  before=copy.deepcopy(self.bank);result=self.build();self.assertEqual(len(result['links']),1);link=result['links'][0]
  self.assertEqual(result['bySourceItem'],{'synthetic-source-item':['synthetic-reuse']})
  self.assertEqual(result['byQuestion'],{'synthetic-q1':['synthetic-reuse']})
  self.assertEqual(result['byConcept'],{'synthetic-assignment':['synthetic-reuse']})
  self.assertEqual(link['additionalUniqueQuestions'],0);self.assertEqual(link['coverageKind'],'reviewed_semantic_reuse')
  self.assertEqual(self.bank,before);self.assertEqual(self.duplicate['status'],'flagged');self.assertEqual(self.bank['concepts'][-1]['status'],'drafted')
  rb=link['questionBindings'][0]['reviewBindings'][0];self.assertEqual(rb['reviewSha256'],hashlib.sha256(rb['rawJSON'].encode()).hexdigest())
 def test_stale_mapping_bytes_fail_closed(self):
  self.mapping['physicalPages']=[2];self.write(self.batch_path,self.batch);self.assert_closed()
 def test_missing_mapping_file_invalidates_prebuilt_candidate(self):
  candidate=assembler.assignment_reuse_candidates(self.root);(self.root/self.batch_path).unlink();self.assert_closed(candidates=candidate)
 def test_missing_mapping_review_fails_closed(self):
  (self.root/self.review_path).unlink();self.assert_closed()
 def test_rejected_mapping_review_fails_closed(self):
  self.review['decision']='rejected';self.save_review();self.assert_closed()
 def test_rejected_mapping_item_fails_closed(self):
  self.review['mappingReviews'][0]['decision']='rejected';self.save_review();self.assert_closed()
 def test_current_mapping_dispute_beats_approval(self):
  dispute=copy.deepcopy(self.review);dispute.update(id='dispute',decision='flagged');self.write('data/assignment-reuse-reviews/dispute.json',dispute);self.assert_closed()
 def test_mapping_author_cannot_approve(self):
  self.review['reviewerId']=self.batch['authorId'];self.save_review();self.assert_closed()
 def test_mapping_revision_author_cannot_approve(self):
  self.batch['revisionAuthors']=[self.review['reviewerId']];self.write(self.batch_path,self.batch);self.review['mappingSha256']=self.sha(self.batch_path);self.save_review();self.assert_closed()
 def test_missing_mapping_author_fails_closed(self):
  self.batch.pop('authorId');self.write(self.batch_path,self.batch);self.review['mappingSha256']=self.sha(self.batch_path);self.save_review();self.assert_closed()
 def test_missing_concept_link_fails_closed(self):
  self.bank['concepts'][-1]['questionIds']=[];self.assert_closed()
 def test_duplicate_source_item_mappings_invalidate_both(self):
  duplicate=copy.deepcopy(self.mapping);duplicate['id']='second-synthetic-reuse';self.batch['mappings'].append(duplicate);self.write(self.batch_path,self.batch)
  self.review['mappingSha256']=self.sha(self.batch_path);item=copy.deepcopy(self.review['mappingReviews'][0]);item['mappingId']=duplicate['id'];self.review['mappingReviews'].append(item);self.save_review();self.assert_closed()
 def test_mapping_target_set_cannot_be_reduced(self):
  self.review['mappingReviews'][0]['reusedQuestionHashes']={};self.save_review();self.assert_closed()
 def test_stale_target_content_fails_closed(self):
  self.target['stem']+=' Changed';self.assert_closed()
 def test_missing_target_fails_closed(self):
  self.bank['questions'].remove(self.target);self.assert_closed()
 def test_target_status_is_not_authority(self):
  self.bank['reviews']=[];self.assert_closed()
 def test_target_rejected_review_fails_closed(self):
  self.target_review['decision']='rejected';self.assert_closed()
 def test_target_current_dispute_fails_closed(self):
  dispute=copy.deepcopy(self.target_review);dispute.update(id='target-dispute',decision='flagged');self.bank['reviews'].append(dispute);self.assert_closed()
 def test_target_review_missing_independent_check_fails_closed(self):
  self.target_review['checks']['duplication']=False;self.assert_closed()
 def test_duplicate_literal_independent_answers_fail_closed(self):
  self.target_review['independentAnswerOptionIds']*=2;self.assert_closed()
 def test_blank_literal_independent_answers_fail_closed(self):
  self.target_review['independentAnswerOptionIds']=[''];self.assert_closed()
 def test_whitespace_mapping_author_cannot_self_approve(self):
  self.review['reviewerId']=' '+self.batch['authorId']+' ';self.save_review();self.assert_closed()
 def test_target_review_wrong_answer_fails_closed(self):
  self.target_review['independentAnswerOptionIds']=['synthetic-q1-o0'];self.assert_closed()
 def test_target_review_wrong_source_hash_fails_closed(self):
  self.target_review['sourceVersions']['synthetic-source']='f'*64;self.assert_closed()
 def test_target_review_does_not_cover_page_fails_closed(self):
  self.target_review['reviewedSlideIds']=[];self.assert_closed()
 def test_missing_source_page_fails_closed(self):
  self.bank['slides']=[];self.assert_closed()
 def test_uninspected_source_page_fails_closed(self):
  self.bank['slides'][0]['visualInspection']['status']='pending';self.assert_closed()
 def test_changed_source_hash_fails_closed(self):
  self.bank['sources'][0]['sha256']='f'*64;self.assert_closed()
 def rebind_fixture(self):
  # Deliberately coherent synthetic approval: the structural guard, not a stale
  # hash somewhere else, must reject the malformed source or literal options.
  self.write(self.original_path,self.original);self.mapping['originalRecordSha256']=self.sha(self.original_path)
  h=validator.question_hash(self.target);self.target_review['questionSha256']=h;self.mapping['reusedQuestions'][0]['questionSha256']=h
  self.mapping['duplicateQuestionSha256']=validator.question_hash(self.duplicate)
  self.review['mappingReviews'][0]['reusedQuestionHashes']={self.target['id']:h}
  self.write(self.batch_path,self.batch);self.review['mappingSha256']=self.sha(self.batch_path);self.save_review()
 def test_coherently_rebound_malformed_source_hash_fails_closed(self):
  for sha in ('not-a-sha256','A'*64,'g'*64,'a'*63):
   with self.subTest(sha=sha):
    self.bank['sources'][0]['sha256']=sha;self.bank['slides'][0]['sourceSha256']=sha
    for q in (self.target,self.duplicate):
     for citation in q['citations']:citation['sourceSha256']=sha
    self.target_review['sourceVersions']={self.original['sourceId']:sha};self.original['sourceSha256']=sha;self.mapping['sourceSha256']=sha
    self.rebind_fixture();self.assert_closed()
 def test_coherently_rebound_one_option_target_fails_closed(self):
  self.target['options']=[o for o in self.target['options'] if o['id'] in self.target['correctOptionIds']]
  self.rebind_fixture();self.assert_closed()
 def test_coherently_rebound_malformed_option_records_fail_closed(self):
  for options in (None,[],[None,None],[{'id':' '},{'id':'valid'}],[{'id':'valid'},{}]):
   with self.subTest(options=options):
    self.target['options']=options;self.rebind_fixture();self.assert_closed()
 def test_nonassignment_source_is_not_reuse_evidence(self):
  self.bank['sources'][0]['role']='lectures';self.assert_closed()
 def test_invalid_selection_mode_fails_closed(self):
  self.target['selectionMode']='invalid';self.assert_closed()
 def test_original_record_must_be_unchanged(self):
  self.original['extra']='changed';self.write(self.original_path,self.original);self.assert_closed()
 def test_original_record_must_exist(self):
  (self.root/self.original_path).unlink();self.assert_closed()
 def test_duplicate_cannot_enter_default_pool(self):
  self.duplicate['status']='verified';self.assert_closed()
 def test_duplicate_content_hash_is_bound(self):
  self.duplicate['stem']+=' Changed';self.assert_closed()
 def test_validator_rejects_reverse_link_removal(self):
  self.bank['assignmentReuse']=self.build();self.bank['assignmentReuse']['byQuestion']={}
  self.assertTrue(assembler.assignment_reuse_errors(self.bank,self.root))
 def test_validator_rejects_mapping_review_object_mutation(self):
  self.bank['assignmentReuse']=self.build();self.bank['assignmentReuse']['candidates'][0]['reviews'][0]['reviewerId']='changed'
  self.assertTrue(assembler.assignment_reuse_errors(self.bank,self.root))
 def test_validator_rejects_missing_mapping_candidate(self):
  self.bank['assignmentReuse']=self.build();self.bank['assignmentReuse']['candidates']=[]
  self.assertTrue(assembler.assignment_reuse_errors(self.bank,self.root))
 def test_validator_rejects_edited_target_review_even_if_still_approvable(self):
  self.bank['assignmentReuse']=self.build();self.target_review['reasoning']+=' New reason.'
  self.assertTrue(assembler.assignment_reuse_errors(self.bank,self.root))
 def test_validator_accepts_exact_sidecar_without_mutating_input(self):
  self.bank['assignmentReuse']=self.build();before=copy.deepcopy(self.bank)
  self.assertEqual(assembler.assignment_reuse_errors(self.bank,self.root),[]);self.assertEqual(self.bank,before)
  self.assertTrue(validator.validate_bank(self.bank,self.root,allow_synthetic=True,check_files=False)['valid'])
 def test_raw_review_binding_handles_fractional_numbers(self):
  self.target_review['syntheticFloat']=1.0;result=self.build();binding=result['links'][0]['questionBindings'][0]['reviewBindings'][0]
  self.assertEqual(json.loads(binding['rawJSON']),self.target_review);self.assertEqual(hashlib.sha256(binding['rawJSON'].encode()).hexdigest(),binding['reviewSha256'])
 def test_invalid_candidate_json_fails_closed(self):
  candidate=assembler.assignment_reuse_candidates(self.root);candidate[0]['rawJSON']='{bad';self.assert_closed(candidates=candidate)

if __name__=='__main__':unittest.main()
