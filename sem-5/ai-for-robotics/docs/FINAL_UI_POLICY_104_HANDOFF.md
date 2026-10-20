# Policy 1.0.4 author handoff

Status: author-side code candidate frozen for separate independent review. Content crop approvals and actual browser verification remain separate. No canonical question, source citation, concept coverage or approved learning-tool payload was edited by this UI change.

## Required UI closures

- Mistake-derived practice now reaches the actual Revision and Progress screens through the unchanged reviewed `mistakeRevision` engine. `currentStudyProgress` uses only latest current-fingerprint outcomes; later correct answers clear the miss. Ordinary worked solutions expose up to eight current eligible exact shared/prerequisite/authored-related suggestions. The six authored related-link records no longer bound all related navigation. Suggestions are explicitly heuristic, not new semantic-review assertions or exam predictions.
- Normal filters/source/concept scope apply before limiting recommendations. Click handlers recompute eligibility, history and filters. Active exams suppress and block study routes even for stale handlers.
- Palette buttons visibly contain ✓, ✕ and ○ outside exams, and only neutral ●/○ during active exams. Correctness remains hidden until completion.
- Required pre-answer figures come from a separate visual inventory and independent pixel/input review, not from modified question objects. Practice/exam/print use reviewed exact crops; original PDFs remain available as post-answer/source evidence outside active exams.

## Runtime visual gate

`RoboticsLearningResources.visualEligibility(bank, embeddedAssets, questionIds)` returns `{ready, diagnostics}`. It independently requires:

1. Current extractor policy and attached independent answer-review eligibility.
2. One exact current question-input record; original Python canonical JSON text, SHA-256 and parsed-object equality all agree.
3. Separate independent review of the exact record/question/source, with all five visual checks true, `displayRole: question_input`, exact asset hashes and crop-metadata hashes. Current flagged/rejected reviews close the gate.
4. Current inspected source pages. Additional premise pages may differ from the question citation page, but must belong to the same current cited source ID/hash and be independently reviewed; citations are never rewritten.
5. Canonical and embedded asset metadata exactly match the reviewed PNG metadata. Actual decoded base64 bytes are SHA-256 checked. The cache is keyed by immutable payload value plus expected SHA/dimensions, not merely an asset ID. Metadata/pixel changes are rechecked. PNG header and dimensions must agree.

Missing author inventory is not treated as self-contained approval. Missing or stale input approval disables question answer controls and direct keyboard/select/submit paths with a named warning. An actual browser image decoding error also closes the question gate.

## Exams, imports, source dialog and printing

- `createExamWithVisuals` preflights the entire selected pool before random selection. It refuses incomplete scopes instead of silently reducing the pool. Each chosen question gets a separate `visualBindings` stamp covering question, record, accepted reviews and image identities. Original question snapshots/hashes remain untouched.
- `questionVisualState` compares a saved normalized question snapshot with the current question and checks the exact visual stamp. Required-figure legacy exams without stamps or mismatched stamps are blocked, preserving selections and deadline. Only exact-current independently reviewed self-contained legacy items can operate without an old stamp. The user is told to restore the original HTML rather than accept substitute pixels.
- Input zoom opens only the independently reviewed crop. Full source previews are blocked while an exam is active, including a source dialog already open when a delayed backup import activates an exam. Zoom/download recheck current eligibility and saved identity. Stale practice handlers cannot bypass exam isolation.
- Active-exam entry clears previously prepared key/solution print content. A native `beforeprint` handler independently rechecks exam state, current inputs and decoded images, replacing blocked content with a neutral notice. This is UI answer separation, not proctored security.
- Print preflight refuses the entire selected scope before constructing a paper, key or solution. Figures are inserted into paper/solutions, never replaced by full answer pages. Printing waits for image decode, then rechecks input eligibility and exam status before opening print. Decode failure or intervening revocation cancels printing.

## Evidence and exact handoff

- `audits/final-ui-policy-104-author/candidate-manifest.json`: exact policy and code bindings.
- `audits/final-ui-policy-104-author/{app.js,core.js,learning-resources.js}.patch`: neutral diffs against preserved approved 1.0.3 baselines.
- `tests/test_mistake_followups.js`: seven recommendation/palette regression groups.
- `tests/test_question_visuals.js`: twelve visual runtime/actual-function integration groups, including decoded-byte mutation, whole-scope refusal, saved stamps, missing reviews, stale callbacks, decode failure, asynchronous print revocation and active source-dialog isolation.
- Author regression run: 128 Node tests and 188 Python tests passed. These are software tests, not browser evidence. Logs are in the author evidence directory.
- Independent reviewer writes separate evidence under `audits/final-ui-policy-104-review`; the author does not self-approve or overwrite historical review records.

The prepared `tests/browser_final_artifact.js` and `docs/FINAL_OFFLINE_QA.md` include the new UI paths, exact-file identity checks and human screenshot/pixel/print acceptance criteria. Browser execution is still pending the precise permitted environment described in the checklist. No previously denied browser route was retried.
