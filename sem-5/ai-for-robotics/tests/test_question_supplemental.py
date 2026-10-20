"""Deterministic synthetic notebook-input tests, never execute notebook code."""
import copy
import hashlib
import json
import unittest
import test_question_visuals as T

V = T.V

class SupplementalInputTests(unittest.TestCase):
    def setUp(self):
        self.base = T.QuestionVisualTests(); self.base.setUp(); self.addCleanup(self.base.doCleanups)
        self.root = self.base.root
        nb = {'cells': [{'cell_type': 'code', 'metadata': {'id': 'colab-cell'}, 'source': ['x = 2\n', 'print(x)\n'], 'outputs': [{'output_type': 'stream', 'text': ['2\n']}]}]}
        text = json.dumps(nb, ensure_ascii=False)
        self.name = 'sources/supplemental/fixture.ipynb'; path = self.root / self.name; path.parent.mkdir(parents=True); path.write_text(text)
        sha = hashlib.sha256(text.encode()).hexdigest()
        self.input = {'id': 'code-input', 'authorId':'supplemental-author', 'kind': 'verbatim_source_code', 'language': 'python', 'sourceArtifact': self.name, 'sourceSha256': sha, 'lineStart': None, 'lineEnd': None, 'notebookArtifact': self.name, 'notebookSha256': sha, 'cellIndexZeroBased': 0, 'cellId': 'colab-cell', 'cellLineStart': 1, 'cellLineEnd': 2, 'sourceUrl': None, 'upstreamCommit': None, 'upstreamGitBlobSha': None, 'upstreamPinStatus': 'local_only', 'notebookRepresentation': 'verbatim', 'text': 'x = 2\nprint(x)\n', 'textSha256': hashlib.sha256(b'x = 2\nprint(x)\n').hexdigest(), 'transformation': 'Exact source substring, no execution.'}
        self.base.manifest['supplementalInputs'] = [self.input]; self.base.manifest['assets'] = []
        self.base.record.update(assetIds=[], supplementalInputIds=['code-input'], requiredInputs=['Exact fixture code'])
        self.rebind()

    def rebind(self):
        self.base.rebind(); r = self.base.review
        r['reviewedSupplementalInputIds'] = [self.input['id']]
        r['supplementalInputHashes'] = {self.input['id']: V.digest(self.input)}
        r['supplementalSourceHashes'] = {self.input[k]: self.input[h] for k, h in [('sourceArtifact', 'sourceSha256'), ('notebookArtifact', 'notebookSha256')]}

    def test_code_only_input_accepted_without_pdf_asset_or_question_changes(self):
        before = copy.deepcopy(self.base.bank); result = self.base.prepare()
        self.assertFalse(result['diagnostics']); self.assertEqual(before, self.base.bank)
        self.assertEqual(result['bindings'][self.base.q['id']]['supplementalInputIds'], ['code-input'])
        self.assertEqual(V.projected_visual_assets(result), [])
        self.assertEqual(result['supplementalArtifacts'][self.name]['sha256'], self.input['notebookSha256'])

    def test_missing_independent_supplemental_review_is_blocked(self):
        del self.base.review['supplementalInputHashes']; self.base.blocked()

    def test_changed_local_notebook_bytes_are_blocked(self):
        path = self.root / self.name; path.write_text(path.read_text()+' '); self.base.blocked()

    def test_coherently_reviewed_wrong_text_cell_range_and_pin_are_rejected(self):
        mutations = [lambda s:s.update(text='answer = 42\n',textSha256=hashlib.sha256(b'answer = 42\n').hexdigest()),lambda s:s.update(cellIndexZeroBased=9),lambda s:s.update(cellId='other'),lambda s:s.update(cellLineEnd=99),lambda s:s.update(upstreamPinStatus='pinned'),lambda s:s.update(lineStart=1,lineEnd=2),lambda s:s.update(notebookOutputIndex=0),lambda s:s.update(language='html')]
        initial = copy.deepcopy(self.input)
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                self.input.clear(); self.input.update(copy.deepcopy(initial)); mutate(self.input); self.rebind(); self.base.blocked()

    def test_embedded_artifact_mutation_and_path_escape_are_rejected(self):
        self.base.save(); inputs = V.load_visual_inputs(self.root)
        inputs['supplementalArtifacts'][self.name]['rawText'] += ' '
        result = V.prepare_question_visuals(self.base.bank,self.root,inputs,check_files=False)
        self.assertTrue(result['diagnostics'])
        self.input['sourceArtifact'] = '../outside.py'; self.rebind(); self.base.blocked()

    def test_saved_output_requires_explicit_question_intent_review(self):
        self.input.update(kind='verbatim_saved_output',language='text',notebookOutputIndex=0,notebookOutputField='text',cellLineStart=1,cellLineEnd=1,text='2\n',textSha256=hashlib.sha256(b'2\n').hexdigest())
        self.rebind(); self.base.blocked()
        self.base.record['savedOutputUse']='explicit_output_reading'; self.rebind(); self.base.blocked()
        self.base.review['savedOutputUse']='explicit_output_reading';self.base.review['checks']['savedOutputIsQuestionStimulus']=True
        self.assertFalse(self.base.prepare()['diagnostics'])
        self.input['notebookRepresentation']='output_stripped';self.rebind();self.base.blocked()

    def test_same_snippet_provenance_is_part_of_saved_binding_and_review(self):
        accepted=self.base.prepare(); b=accepted['supplementalBindings']['code-input']
        self.assertEqual(hashlib.sha256(b['rawJSON'].encode()).hexdigest(),b['inputSha256'])
        self.input['transformation']='Changed qualifier';self.base.blocked()

    def test_commit_only_is_distinct_and_does_not_fabricate_blob(self):
        self.input.update(upstreamPinStatus='commit_only',upstreamCommit='a'*40,sourceUrl='https://github.com/example/course/blob/'+('a'*40)+'/lesson.ipynb')
        self.rebind();self.assertFalse(self.base.prepare()['diagnostics'])
        self.input['upstreamPinStatus']='pinned';self.rebind();self.base.blocked()

    def test_snippet_author_cannot_self_approve_via_different_manifest_author(self):
        self.base.review['reviewerId']=' supplemental-author ';self.base.blocked()

if __name__ == '__main__':unittest.main()
