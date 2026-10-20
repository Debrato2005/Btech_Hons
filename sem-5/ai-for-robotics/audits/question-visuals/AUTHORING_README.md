# Exact question-input sidecar

The inventory in `data/question-visuals/manifest.json` is separate from question content and answer reviews. Every raw question has one hash/version-bound disposition. Only independently accepted current records may enter normal study, exams or print; an author build receipt is not approval.

## Current authored coverage

- 5,071 dispositions: 694 required, 4,377 self-contained (two flagged duplicates remain excluded by the separate answer gate).
- Byte-deduplicated, exact-source PNG crops at 216 DPI; the current count is recorded in build-receipt.json. No redraws, masks, rescaled screenshots, or embedded answer-key substitutes.
- 34 separately provenance-bound verbatim notebook/code/output snippets serving 38 records. Historical saved output is only a stimulus for an explicit output-reading comparison.
- All final L01–L60 independent full-text classifications have been reconciled; source-pixel and snippet approvals remain independent.
- The parent independently corrected/promoted two L46 source-conflict questions to version2 before their input bindings were refreshed. This authoring tool did not edit those questions or their answer reviews.

## Reproduction and safe incremental changes

1. Edit an exact PDF-point crop plan only after source inspection. Keep labels, axes, scales, and input context; exclude irrelevant solution calculations and outputs.
2. To add a crop to an existing question, use `python scripts/augment_question_visuals.py QUESTION_ID CROP_KEY ...`. It preserves both explicit and implicitly page-derived input keys before unioning additions. Never append one crop to a newly created empty list when previous defaults already supplied other inputs.
3. Run `python scripts/build_question_visuals.py`. Changed source/page/rectangle/DPI or PNG bytes trigger exact rerendering. Existing canonical records are deterministic. Supplemental source/artifact hashes and precise cell/line/output selectors are validated without executing code.
4. Independent reviewers bind the exact record, question, source, asset metadata and PNG/snippet hashes. Changing any required input invalidates its old receipts. Do not edit reviewer receipts to make a new record pass.
5. Supplemental snippets augment existing required PDF inputs. Deliberately notebook-only records use explicit empty crop keys, avoiding accidental substitution of generic slide pseudocode.

Unreferenced crops are retained on disk and in `render-cache.json`, but excluded from the manifest and delivery. Their inventory is `unreferenced-crops-not-packaged.json`. No source files or archival crop files were deleted.

## Provenance and reconciliation evidence

- `build-receipt.json`: exact current manifest and bank hashes, counts, missing-input report.
- `current-gate-audit.json`: current producer eligibility and named independent-review holds. This is a point-in-time audit, not an automatic approval.
- `idempotence-check.json`: repeated producer run does not change manifest, source proposal or bank bytes.
- `lead-negative-reason-restoration.json`: 421 harmless prose-only changes restored exactly to previously accepted full-record digests. No question, classification, input, source reference or review receipt was changed by that restoration. Detailed independent rationales remain in the review triage ledger.
- `latest-merge-receipt.json`: late-author snapshot integration, preserving already accepted self-contained records and the two promoted version2 inputs.

## Final author handoff

At 2026-10-20 04:25:46 UTC, the full producer gate accepted all 5,069 current verified questions with zero diagnostics. The two excluded duplicates remain excluded. The final manifest SHA-256 is `68c429f4ff8ca8018bae8bb8c05eeacedd74259b78e4181b1bf53bf5d5730d66`.

The accepted manifest contains 487 exact-source PNG assets (87,485,545 bytes), 34 supplemental snippets across 38 question records and six exact local artifacts. There are 130 independent review files containing 5,085 historical/current receipts, with exactly 5,069 accepted current review IDs. All 694 required records and all 4,375 active self-contained records pass. Two additional self-contained inventory records correspond to the excluded duplicates.

`final-zero-diagnostic-gate.json` freezes the exact manifest hash, current bank hash at inspection, all review-file hashes and authoring-script hashes. The author will make no further edits after this handoff unless the parent identifies a concrete new defect. This is an authoring freeze, not a filesystem permission change; the integration owner performs the final assembled application and milestone checks.
