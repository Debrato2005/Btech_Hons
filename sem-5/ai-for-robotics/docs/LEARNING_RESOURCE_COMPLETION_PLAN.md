# Source-linked learning-resource completion

Author for this implementation: `robotics-learning-resource-projection-author-20261019`.
The worker is now authoring these resources and will not independently approve them.

## Frozen audit

`audits/whole-course-learning-tools-coverage-independent.json` binds the audit to assembled bank SHA256 `93b0efc95804632f2ba0ff9033f00f7c606b4c2f85843ee3050c21e02679f7f1`.
All 24 original tool records are draft and lack question/concept/review links. The engine tests pass, but no verified course tool activates. There are 1,464 formula occurrences in 1,293 approved questions, 770 exactly distinct formula objects across all 11 currently represented weeks and 51 lectures. There are 301 explicit trap entries, 11,342 misconception entries in 3,902 approved questions, and 125 comparison-stem candidates across 44 lectures. Counts will change when later lectures are assembled; none are unique-concept counts.

## Implementation boundary

1. Add a pure, dependency-free projection and provenance module. Formula cards copy exact expression, variables, units and formula assumptions. They retain every relevant question's complete premise, assumptions, correct alternatives, explanation, citations, source qualifications, primary evidence, version and canonical content hash. Dedupe only identical complete formula objects; do not equate superficially similar expressions from different contexts.
2. Project misconception/trap material without summarizing or treating incorrect alternatives as true statements. Comparison cards label the correct distinction and explicitly incorrect tempting alternative, retain the discriminating question and exact every-option rationale, and disclose that this is a view of reviewed question evidence, not a new independent factual approval.
3. Require an independently approved extractor policy and current question approval/source bindings. Generate runtime digests without adding fields to approved question objects. Fail closed on stale versions, edited source fields, conflicting current reviews, unverified questions, source mismatches and policy/code changes. Build checks use the canonical Python question hash. Browser checks use a separate explicitly named deterministic runtime digest; do not conflate them.
4. Add week/lecture/search filtering and bounded pagination so thousands of records do not create an unresponsive DOM. Preserve exact citations, context and the distinction between projected questions, separately reviewed resources and synthetic demonstrations.
5. Bind five existing source algorithm examples and two existing numerical families to actual current approved questions. Author additional bounded high-yield numerical families across the represented mathematical domains only with explicit valid/invalid domains, distinct rounded alternatives, worked steps, seed replay and varied execution tests.
6. Freeze new configuration, code hashes, source evidence and author test results. Parent routes the bounded review packet to the independent contracts worker. Only its exact-hash approval activates new/transformed resources. Author tests are never independent approval.

No approved question object, original source dispute, canonical bank file or Git state will be edited by this worker. Parent owns assembly and release. All incident-environment, model/audio/download, NLTK and denied-notebook restrictions remain in force. The tentative Unicode escape concern was disproved by parsed-string inspection; no renderer normalization change is justified for that observation.
