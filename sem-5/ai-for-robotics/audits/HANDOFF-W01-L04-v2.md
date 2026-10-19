# L04 v2 revisions: frozen, awaiting a distinct reviewer

- Exactly **37 flagged questions revised to v2**, all draft, with no v2 approval.
- All **94 approved v1 correctness hashes unchanged**. Full slice remains 131 questions and 41 concepts.
- Revision author: `define_robotics_data_contracts:L04-v2-revision-author`, recorded in each changed question's `revisionAuthors`, revision history and batch metadata. This agent reviewed v1 and authored v2, so it must not approve v2.
- Repairs: ten hard→medium difficulty corrections, 26 plausible distractor replacements with corresponding rationales/misconceptions, and the P0160-Q04 arithmetic distractor explanation. All original correct answer IDs remain unchanged.

## Start the independent review here

Read `audits/blind-W01-L04-v2-revisions.json` before the full author batch or revision summary. It contains 37 questions and full correctness hashes but omits answer keys, solutions and author-written citation `evidenceText`; source IDs, hashes, pages and locators remain.

Blind packet SHA256: `8776b32adead703875949f90b9e5af2a22d40a4d0cda897e4a5243627366757e`.

Hash manifest: `audits/W01-L04-v2-revision-question-hashes.json`.

Derive answers from actual source pixels and save them before revealing the full batch. Record prior exposure honestly. Do not read the author script or summaries to derive blind answers.

## Frozen author artifacts

- Full current batch: `data/question-batches/W01-L04.json`.
- Current batch SHA256: `1e41179bd7da4158aac6ea6f5aba40b44a008ecebde6e2be2f24019725859c2f`.
- Archived original: `data/question-batches/archive/W01-L04-v1.json`, SHA256 `aaf536abf4b31cff534f4efed66a49f84b6c108102959279117e7236934f8e3d`.
- Preserved v1 review: `data/reviews/W01-L04-v1-independent.json`.
- Exact change history and hashes: `audits/W01-L04-v2-revision-summary.json`.
- One-time guarded revision script: `scripts/revise_W01_L04_v2.py`; do not rerun against v2.
- Author-side checks: `audits/W01-L04-v2-author-checks.json` and `scripts/check_W01_L04_v2_revision.py`. These are not independent verification.

The 86 author assertions passed, including all 94 approved hashes preserved, exact 37 changed IDs, hidden packet content, corrected reciprocal arithmetic, and the first-row NumPy in-place cast failure. Isolated integration validates with zero errors and 37 expected stale historical-review warnings. Those historical reviews do not approve v2.

Original blind evidence and source uncertainty records remain intact. The broader course and lecture coverage challenge is still open. No Git, bank or source writes were made.
