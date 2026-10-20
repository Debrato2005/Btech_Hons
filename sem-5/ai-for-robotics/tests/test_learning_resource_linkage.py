"""Isolated import and inactive-policy regressions. No course approvals are created."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class LearningResourceLinkageTests(unittest.TestCase):
 def test_validator_file_import_from_unrelated_cwd_without_scripts_path(self):
  program='''import importlib.util,json,sys
from pathlib import Path
root=Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('isolated_validator',root/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
bank=json.loads((root/'tests/fixtures/synthetic_bank.json').read_text());r=v.validate_bank(bank,root,allow_synthetic=True);assert r['valid'],r
assert str(root/'scripts') not in sys.path
print('isolated-file-import-passed')
'''
  with tempfile.TemporaryDirectory() as directory:
   p=subprocess.run([sys.executable,'-I','-c',program,str(ROOT)],cwd=directory,capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stderr+p.stdout)
 def test_learning_resource_module_uses_same_canonical_hash(self):
  spec=importlib.util.spec_from_file_location('isolated_lr',ROOT/'scripts/learning_resources.py');lr=importlib.util.module_from_spec(spec);spec.loader.exec_module(lr)
  spec2=importlib.util.spec_from_file_location('isolated_v',ROOT/'scripts/validate.py');v=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(v)
  for q in ({'id':'θ','value':1.0,'status':'draft','reviewIds':[]},{'id':'a','value':[1e-8,False,None]}):self.assertEqual(lr.question_hash(q),v.question_hash(q))
 def test_verified_tool_without_integrity_metadata_rejected(self):
  spec=importlib.util.spec_from_file_location('isolated_lr2',ROOT/'scripts/learning_resources.py');lr=importlib.util.module_from_spec(spec);spec.loader.exec_module(lr)
  self.assertTrue(lr.integrity_errors({'learningTools':{'formulaSheet':[{'status':'verified'}]}},ROOT))
