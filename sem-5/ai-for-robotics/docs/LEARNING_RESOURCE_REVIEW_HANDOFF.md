# Learning resources: frozen independent review handoff

## What is frozen

- Author: `robotics-learning-resource-projection-author-20261019`, distinct from any accepting reviewer.
- Answer-free packet: `audits/blind-learning-resources-v1.json`, SHA256 `04ff5ce53239ebbf58648c4bdeb1c486da94735b1d337c980d4b2f7c2788c24f`.
- Minimal bindings: `audits/blind-binding-learning-resources-v1.json`, SHA256 `a12922b7115f9460d80550b3d20363a412237b26cb7b954c196f0b94246d2507`.
- 18 draft tool records: five algorithm configurations and 13 numerical families. The packet gives 39 independently answerable numerical examples, with option IDs remapped to `o1` etc. It contains no expected answers or traces.
- The extractor policy binds 11 code/integration files. Its canonical policy SHA256 is `6cdb73bb280557f7b072332d19a575e04c988312bbbfd284c5d0cb3db1a34787`.
- No question objects, canonical bank or Git state were changed. The original 24 draft tool records are preserved separately.

## Review order

1. Read the packet and minimal bindings, inspect the actual source pages and independently freeze the 39 example responses and five algorithm traces. Question/source links are evidence only, not automatic tool approval. Prior exposure to an underlying question must be disclosed rather than counted as fresh blindness.
2. Then inspect `data/learning-tools-course.json`, `app/course-numerical.js`, `app/learning-tools.js`, and the separate author output `audits/learning-resources-v1-author-example-results.json`. Check all generated premises, units, assumptions, distractors, solution steps, variable definitions and source qualifications, not just final arithmetic.
3. Inspect the policy and gate/UI integration files named in the minimal binding. The policy transforms exact currently approved question evidence. It does not write new factual summaries or independently approve the underlying facts a second time. Exact whole formula objects, not expression strings alone, are deduplicated. Incorrect comparison alternatives must remain explicitly labeled incorrect. Every context retains its premise, assumptions, justification, sources, qualifications and exact approval binding.
4. Challenge mutation failure modes, stale hashes, author self-approval, source inspection, current disputes, unverified/synthetic records, review removal, renderer text safety and pagination. Canonical Python hashes and the separately named JavaScript runtime digest are deliberately distinct representations.
5. Report flags without authoring and accepting your own replacement. Do not mark an unassessed check as passed. The separate browser boundary below is not covered by passing Node checks.

## Review persistence format

Use a JSON array at `data/learning-resource-policy-reviews.json` for the policy. A policy record has `id`, `reviewerId`, `resourceId`, `resourceVersion`, `resourceSha256`, `decision` (`verified`, `flagged`, or `rejected`), `checks`, and review notes/evidence as appropriate. All five checks are required for activation:

- `exactProjection`
- `contextPreservation`
- `sourceAndReviewBinding`
- `failClosedMutationTests`
- `runtimeTests`

Use a JSON array at `data/learning-tool-reviews.json` for tools. Each record has `id`, `reviewerId`, `toolId`, `toolVersion`, `toolSha256`, `decision`, `checks`, `sourceVersions` (source ID to full SHA256), `reviewedSlideIds`, and independent response/trace/evidence notes. All seven checks are required:

- `sourceSupport`
- `assumptions`
- `answerOrTrace`
- `calculations`
- `runtimeTests`
- `explanation`
- `sourceLinkage`

Canonical tool hash is `scripts/validate.py question_hash(record)`, excluding only `status` and `reviewIds`. Policy hash is SHA256 of `validate.canonical_json(policy)`, including every policy field. Do not edit the draft policy's status to activate it: that would change its hash. The separate independent review and `policyEligible` gate perform activation. Do not edit the authored tool objects merely to set verified status: parent assembly derives status/review IDs from separate reviews.

## Runtime and permission boundary

Use only the already available default Python and Node environments. Never use `/tmp/robotics-l35-venv`, its installed dependencies/audio, model/checkpoint or pretrained-inference routes, new downloads/installs, NLTK corpora or the twice-denied L49 notebook. No Git or canonical bank writes by this author.

An attempted existing Chromium/Playwright component test failed before opening a page: `socket() failed: Operation not permitted (1)`, then SIGABRT. No browser checks or screenshots were produced. The stopped launch was not retried by an alternate route. `audits/learning-resource-browser-author-checks.json` records `blocked`, not a pass. Actual browser rendering/layout and offline interaction remain pending; Node DOM-independent tests are not substituted for them.

## Author checks and honest coverage limits

The new 11 families have 11,000 reproducible seeded cases, each checked against a separately expressed arithmetic oracle, domain checks, four distinct displayed alternatives, replay and solution metadata. The two existing families add 2,000 cases in the shared suite. These are author software checks, not independent approvals and not 13,000 distinct concept claims. Numerical values are deliberately added exercises, not falsely quoted slide measurements.

The five algorithms include the source road graph for BFS/UCS/A*, an explicitly defined eager-discovery iterative DFS application of the source definition to that graph, and a supplied sequential Q-learning exercise. DFS is not claimed to reproduce the different p116 red trace. Q-learning's true-terminal mask is explicit and does not erase the source's termination/truncation conflict.

Source author inspection revisited 34 actual readable page renders; its audit is `audits/learning-resource-completion-source-inspections.json`. It is not independent inspection. Exact projections cover whatever approved evidence the current bank contains, not every meaningful comparison or every infinite numerical input. The original finite-course completeness challenges remain separate. A fresh bounded projection census and trace checks are saved separately without altering these frozen objects.
