# L04 independent review: frozen handoff

Result: 131 questions reviewed, 94 verified and 37 flagged. All keyed answer sets agree with the independently persisted solves. This is not an exhaustive lecture or course completion certificate.

## Integration files
- Reviews: `data/reviews/W01-L04-v1-independent.json`
- Review SHA256: `de9fd3f18b89cdde83646faffd05d946d9a70030acd76db31b724a15e526db26`
- Exact flags and source uncertainties: `audits/W01-L04-review-summary.json`
- Author batch reviewed SHA256: `aaf536abf4b31cff534f4efed66a49f84b6c108102959279117e7236934f8e3d`
- Every review is bound to its exact v1 correctness hash. Any repair requires a version bump and a fresh independent review; preserve the 94 approved hashes.

## Blind provenance, preserved without reattribution
- Original solver: `reviewer-independent-python-modeling-20261019`, 83 blind answers, pages 125–160 visually inspected. Original evidence `audits/blind-answers-W01-L04-v1.json` is byte-for-byte unchanged, SHA256 `50b0106805308529ca51b0a49f2f475a57917bb6fbbb7bc7a631dbe4e346fa5e`.
- Continuation solver and final solution auditor: `define_robotics_data_contracts:L04-continuation-reviewer`, 48 new blind answers. Personally inspected pages 161–170 plus 146, 147, 155, 158, 159 and 160. Separate evidence `audits/blind-answers-W01-L04-v1-continuation.json`, SHA256 `bd6dbdcc92d437dada082436a58442da6673b5f1cc8098b61172f0638967d571`.
- All 131 answers were persisted before author reveal at `2026-10-19T16:17:45.794094+00:00`, recorded in `audits/W01-L04-author-reveal.json`.
- Final reviews explicitly retain `independentSolverId`, original solve time, evidence path/hash, and source inspector IDs. The continuation reviewer audited all full solutions and every option rationale but does not claim to have personally re-solved the inherited 83.

## Findings
- Ten hard labels should be medium unless the task is genuinely redesigned: P0132-Q02, P0138-Q03, P0142-Q01, P0144-Q02, P0157-Q07, P0160-Q02, P0162-Q07, P0162-Q08, P0163-Q05, P0166-Q03.
- Twenty-six questions contain conspicuously unrelated distractors. The summary gives exact option defects and repair guidance. Do not replace correct answers merely to fix distractors.
- P0160-Q04: `[50,25,16.667]` is not the inverse of correct velocities `[1,2,3]`. It is approximately the reciprocals of position increments `[0.02,0.04,0.06]`, omitting elapsed-time scaling. Correct that rationale and its repeated misconception, or change the distractor consistently.
- Source defects remain preserved: literal NumPy block-depth failure, Pandas newline SyntaxError, function-name NameError, shell command typos, HDF reader spelling and bounded performance/API claims. Exact source and explicitly repaired variants are not conflated.

## Validation and recovery
- All 131 review records pass the live schema. Isolated in-memory integration passes with zero errors and warnings: 41 concepts, 40 with a verified question, 94 currently verified questions.
- Original 19 execution records remain untouched. The continuation has 24 passing assertions in `audits/W01-L04-v1-continuation-code-checks.json`; some overlap original checks. Original loop used integer 2, whereas continuation preserves source 2.0 and checks exact stdout. No answer changes arise.
- Reconstruct review logic with `scripts/finalize_W01_L04_review.py` only while frozen hashes match. Do not rerun after author revisions. Blind scripts now refuse to run after the reveal marker exists.
- No Git, author batch, source or bank edits were made. Parent integrates and routes revisions to a distinct reviewer.
