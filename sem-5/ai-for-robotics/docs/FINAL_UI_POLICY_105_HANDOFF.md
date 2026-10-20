# Policy 1.0.5: separate supplemental question inputs

Author-side candidate only. Independent code review and independent snippet-content review remain separate gates. Previous policy/review records are preserved. No question/answer/status, source citation, original PDF or coverage ledger was edited by this author. No notebook code was executed, browser launched, dependency installed, Git action taken or Library upload attempted.

## Distinct provenance contract

The existing question-input sidecar gains optional `supplementalInputs`, `supplementalArtifacts` and `supplementalBindings`. These are not entries in `bank.assets` and are never mislabeled as PDF pixels. Existing PNG/source/crop/review gates are unchanged.

Each input binds its stable ID and authorship, `verbatim_source_code` or `verbatim_saved_output`, language, exact local source and notebook path/SHA-256, notebook representation, zero-based cell index and exact cell ID (top-level `id`, otherwise Colab `metadata.id`), one-based inclusive cell line range, exact text/SHA-256, and a transformation qualification. A separate extracted Python file also requires its exact global line range to reproduce the same text. Notebook-as-source uses cell ranges and null global line fields.

The producer embeds each exact UTF-8 local artifact once, under its unchanged local path. Approved roots are `sources/supplemental/` and `audits/review-snapshots/`; traversal/outside-root reads fail closed. Python compares current local bytes and source slices. Runtime independently hashes the embedded artifact text and the exact selected substring, not merely declared metadata. No evaluation or code execution occurs.

Upstream provenance is explicit:
- `pinned`: known exact commit and Git blob, with the matching commit URL.
- `commit_only`: known exact commit URL, blob unknown/null.
- `local_only`: upstream commit/blob unknown/null; exact local SHA remains mandatory.

Local output-stripped notebook SHA-256 is never equated with an unchanged upstream Git blob.

## Independent review

A question record references `supplementalInputIds`; required input records may have no PNG when code/text is the actual premise. The existing current question/version/hash and inspected lecture-source references still bind the record. Each independent review additionally requires:
- `reviewedSupplementalInputIds` matching the complete requested input set;
- `supplementalInputHashes` binding complete canonical snippet metadata;
- `supplementalSourceHashes` binding both source and notebook paths;
- the existing five input review checks, with current independent identities distinct from manifest, record and snippet authors/revision authors.

Historical output is an exceptional, distinct subtype. It uses only an explicit fixed notebook output index and `text` or `data.text/plain` field. Both record and independent review must say `savedOutputUse: explicit_output_reading`, and review check `savedOutputIsQuestionStimulus` must be true. It is allowed only when the existing question explicitly asks to read/compare saved output. Ordinary compute/trace questions must not receive worked output. The code gate enforces the separately reviewed intent contract; only actual independent reading can certify that the question satisfies it.

## UI, exams and print

Required text is shown as escaped nonexecuting `pre/code` content with full provenance and linked lecture context. Code is labeled a verbatim notebook premise, not a PDF crop. Saved output is labeled historical given stimulus, not a new execution. Lecture/source navigation remains suppressed during an active exam.

Saved exam stamps additionally bind input metadata, exact text, local source and notebook hashes. Missing/stale required text blocks answering rather than replacing premises. Whole-scope exam and print preflight, import/reload deadline preservation, native print lock and post-decode image checks remain in force. Paper and worked solutions include the exact text; paper adds no computed answer key.

The build retains original PDFs and lossless PNGs, embeds supplemental artifacts in the bank, and rechecks local supplemental files before publishing the HTML. The build report separately lists supplemental IDs/artifact hashes and byte sizes.

## Author checks and independent-review handoff

- New tests: `tests/test_question_supplemental.py` (9 groups) and `tests/test_question_supplemental.js` (9 groups), with synthetic fixtures only.
- Explicit allowlisted run: 134 Node tests and 197 Python tests passed. The three runner-CLI fixture tests were deliberately not executed in this pass. No broad `tests/*.js` invocation or browser runner execution occurred.
- Existing 41 Python PNG tests and 12 Node visual UI groups remain passing.
- `audits/final-ui-policy-105-author/actual-source-byte-check.json` checks 34 current snippets across 38 current required records, with no source-byte/slice errors. This is not independent approval of snippet intent or scientific content. The author proposal contains the latest L34 plot-label and L50 code cases at freeze; later content changes need their own exact reviews.
- `audits/final-ui-policy-105-author/candidate-manifest.json` holds the frozen policy/code hashes. Neutral diffs and pre-extension baselines are retained in that directory.

The exact-file browser runner and human checklist are prepared for code/output practice, mobile layout, active exam/reload and print verification. They have not executed. The previously documented browser denial and separate reviewer execution incident remain restrictions, not browser-pass evidence.
