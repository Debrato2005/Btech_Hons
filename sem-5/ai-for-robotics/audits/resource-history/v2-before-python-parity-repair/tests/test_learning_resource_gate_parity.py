"""Synthetic fail-closed probes; never approve real course records."""
from pathlib import Path
import copy, importlib.util, json, subprocess, unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gate_parity_lr',ROOT/'scripts/learning_resources.py')
LR=importlib.util.module_from_spec(spec);spec.loader.exec_module(LR)
class LearningResourceGateParityTests(unittest.TestCase):
 def fixture(self):
  raw=subprocess.run(['node','-e',"console.log(JSON.stringify(require('./tests/fixtures/learning-resource-bank.js').fixture()))"],cwd=ROOT,text=True,capture_output=True,check=True)
  bank=json.loads(raw.stdout);q=bank['questions'][0]
  record={'id':'synthetic-test-record','version':1,'status':'verified','authorId':'tool-author','questionIds':[q['id']],'sourceRefs':copy.deepcopy(q['citations'])}
  review={'id':'test-review','toolId':record['id'],'toolVersion':1,'reviewerId':'tool-reviewer','decision':'verified','sourceVersions':{'S':'a'*64},'reviewedSlideIds':['S1'],'checks':dict.fromkeys(LR.TOOL_CHECKS,True)}
  self.refresh(bank,record,review)
  self.assertEqual(LR.tool_reasons(record,bank,ROOT,[review])[0],[])
  return bank,record,review
 def refresh(self,bank,record,review):
  q=bank['questions'][0];h=LR.question_hash(q);bank['reviews'][0]['questionSha256']=h
  record['questionBindings']=[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':h}]
  review['toolSha256']=LR.question_hash(record)
 def rejected(self,change):
  b,t,r=self.fixture();change(b,t,r);self.refresh(b,t,r)
  self.assertTrue(LR.tool_reasons(t,b,ROOT,[r])[0])
 def test_invalid_literal_keys_and_independent_answers(self):
  for keys,answers in [([],[]),(['missing'],['missing']),(['o1','o1'],['o1']),(['o1'],['o1','o1']),(['o1'],[]),(['o1','o2'],['o1','o2'])]:
   with self.subTest(keys=keys,answers=answers):
    self.rejected(lambda b,t,r:(b['questions'][0].update(correctOptionIds=keys),b['reviews'][0].update(independentAnswerOptionIds=answers)))
 def test_duplicate_option_ids_and_missing_selection_mode(self):
  self.rejected(lambda b,t,r:b['questions'][0]['options'][1].update(id='o1'))
  self.rejected(lambda b,t,r:b['questions'][0].pop('selectionMode'))
 def test_blank_and_author_equivalent_question_and_tool_reviewers(self):
  for who in ['', '   ',None,17,' author ']:
   with self.subTest(who=who):self.rejected(lambda b,t,r:b['reviews'][0].update(reviewerId=who))
  for who in ['', '   ',None,17,' tool-author ']:
   with self.subTest(who=who):self.rejected(lambda b,t,r:r.update(reviewerId=who))
 def test_positive_bounded_integer_question_page_and_tool_page(self):
  for page in [0,-1,1.5,True,None,'1',4]:
   def mutate(b,t,r):
    b['questions'][0]['citations'][0]['physicalPage']=page;b['slides'][0]['physicalPage']=page
   with self.subTest(page=page):self.rejected(mutate)
  self.rejected(lambda b,t,r:t['sourceRefs'][0].update(physicalPage=0))
 def test_explicit_dispositions_and_valid_source_page_count(self):
  for disposition in ['invented','unreviewed','unresolved','']:
   with self.subTest(disposition=disposition):self.rejected(lambda b,t,r:b['slides'][0].update(disposition=disposition))
  for count in [0,None,'3',True,2.5]:
   with self.subTest(count=count):self.rejected(lambda b,t,r:b['sources'][0].update(pageCount=count))
 def test_source_identity_inspection_and_conflict_for_linked_question(self):
  self.rejected(lambda b,t,r:b['slides'][0].update(sourceId='other'))
  self.rejected(lambda b,t,r:b['slides'][0]['visualInspection'].update(status='pending'))
  self.rejected(lambda b,t,r:b['questions'][0]['citations'][0].update(role='conflict'))
 def test_nonempty_valid_multiselect_is_accepted(self):
  b,t,r=self.fixture();b['questions'][0].update(selectionMode='multi',correctOptionIds=['o1','o2']);b['reviews'][0]['independentAnswerOptionIds']=['o2','o1'];self.refresh(b,t,r)
  self.assertEqual(LR.tool_reasons(t,b,ROOT,[r])[0],[])
 def test_policy_identity_is_trimmed_and_revision_authors_excluded(self):
  policy={'id':'P','version':'test','authorId':'author','revisionAuthors':['repairer']}
  for who,accepted in [('reviewer',True),(' ',False),(' author ',False),('repairer',False)]:
   r={'resourceId':'P','resourceVersion':'test','resourceSha256':LR.digest(policy),'reviewerId':who,'decision':'verified','checks':dict.fromkeys(LR.POLICY_CHECKS,True)}
   self.assertEqual(LR.policy_approval(policy,[r]),accepted)
if __name__=='__main__':unittest.main()
