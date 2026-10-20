# Expanded final UI / source-assignment priority policy review

This supersedes the scope of the earlier narrow UI handoff only for the new changes described here. The initial independent UI evidence remains preserved in `audits/final-ui-independent-review/`; it is not retroactively an approval of this expansion. No new browser execution occurred.

## Author-owned behavior

- `app/core.js`: `rankRevisionQuestions` applies ordinary filters first, includes only verified records with revision score above one, adds two study-priority points to assignment-linked IDs and sorts deterministically by score, week, lecture, and stable question ID. Existing current-fingerprint errors, review flags and bookmarks rank ahead of a fresh assignment priority. It does not record answers or mutate questions.
- `app/learning-resources.js`: version 1.0.3 and `assignmentPriority` add a separately gated study-order projection. The unchanged exact-question/context and approved-tool gates remain in force. Direct adaptations require current independent question/source approval, assignment origin and an assignment-solutions citation. Their actual `assignmentSourceItemId` is retained.
- `app/app.js`: the Revision route consumes this projection, retains ordinary source/concept/search/learning filters, explains “not predicted exam likelihood,” labels individual priority questions, and preserves confusion/formula shortcuts. No answer/solution behavior is added to an active exam.
- `scripts/assemble_bank.py` and `scripts/validate.py`: a separate author implemented the shared reuse sidecar and integrity checks. No competing learning-resource sidecar was introduced.

## Shared bank contract

`assignmentReuse.formatVersion = 1`. `candidates` retain exact mapping batch UTF-8 `rawJSON`/`sha256`, current independent `reviews`, canonical review-object raw JSON plus hash bindings, and immutable `originalRecords`. `links` are only assembled after source inspection, unchanged accepted target questions/reviews, excluded duplicates, originals and independent mapping approval pass. Reverse maps are `bySourceItem`, `byQuestion`, and `byConcept`; diagnostics are retained separately.

Every link carries mapping path/file hash, canonical `mappingRawJSON`/`mappingSha256`, source item/concept/source/page IDs, primary and reused target IDs, zero additional unique questions, mapping review raw/hash bindings and exact question/review bindings. `duplicateBinding` carries the excluded duplicate’s version, content hash and canonical JSON without status/reviewIds. No original question receives new citations or answer changes.

Runtime rechecks the exact candidate bytes, unique mapping/source-item/review IDs, matching assembled link, canonical mapping object, assignment source role/hash/page/inspection, concept/source slides, original record bytes and identity, excluded duplicate status/content/source item, every current eligible reused target/version/content/source/review, independent mapping reviewer versus all authors, disputes, exact target hashes and zero additional unique counts. Review and mapping canonical strings are hashed as supplied, then parsed and compared semantically: this avoids Python/JavaScript numeric serialization drift. Missing metadata fails closed. Raw draft status is never treated as acceptance.

## Evidence and independent challenges

`tests/test_assignment_revision.js` uses explicit software-only fixtures. It checks the fresh learner route without question mutation, valid exact reuse, missing/stale/disputed/malformed evidence, deterministic ranking/filtering, and actual app route revocation. `tests/test_assignment_reuse.py` independently covers producer/integrity contracts. Existing UI and learning-tool tests must all still pass.

The reviewer should independently exercise the current real bank when a genuine matching policy approval exists, confirm unchanged approved tool payloads, compare all policy-bound files and rerun the earlier course-tree/heatmap/active-exam probes. Challenge source and target review mutation, original/duplicate mutation, missing sidecar/link, wrong/missing policy, mapping-author self-approval, duplicate mapping IDs/source items, and a learner with errors/bookmarks before approval.

`tests/browser_final_artifact.js` now checks a nonempty, correctly labeled fresh revision route in a disposable offline profile before any answers. This runner remains inert unless explicitly executed against the exact downloaded HTML hash in a permitted Chromium environment. Deterministic passes do not establish layout, actual PDF pixels, downloads, file:// persistence, or browser safety.

## Policy and payload boundaries

Policy 1.0.3 is author-side draft until an independent reviewer records acceptance at its exact hash. The original policy author is retained and revision authors are explicit. Existing 18 approved algorithm/numerical tool objects must remain byte-identical. Question/object content and subject-matter approvals are owned by their original ledgers, not this application change. Final content assembly, HTML build, Git checkpoint, ZIP packaging and download remain coordinator operations after independent approval.

## Final source/coverage addendum

The same runtime-accepted reuse links are exposed separately by `assignmentPriority(..., {reuseOnly:true})`. This bounded call evaluates only linked target questions to avoid hashing the entire bank for each ordinary source-button render, while it still checks full raw source, original and excluded-duplicate evidence. It is not a separate approval mechanism.

Coverage page/concept cards show “Reviewed semantic reuse” and “Zero added questions,” retain the original concept/duplicate statuses and link to unchanged verified targets. Those target questions have an explicit assignment-reuse source backlink. Source-page and concept-scoped practice include only the targets of runtime-accepted links. Revoked or missing evidence removes all three surfaces. The new inert-DOM test exercises actual functions for both directions and mutation-driven disappearance; the exact-file runner is prepared to test those paths without synthetic substitutions.

## Legacy semantic-reference and commentary display

A final display-only addendum renders existing `coverageDisposition`, `coverageResolution` and `semanticCoverage` separately from direct links. Source qualifications, commentary exclusion reason, remaining limitations, surviving concept IDs, recorded reference IDs/versions/hashes and evidence-packet path/hash remain visible. Complete metadata is expandable. The legacy packet is not revalidated by this view, so its references are deliberately plain, nonnavigable recorded IDs, not newly approved links. They do not affect statuses, direct counts, citations or page color. A concept-only quotation exclusion explicitly does not exclude the rest of its page. An inert actual-renderer test verifies both metadata types, no unchecked navigation, retained source caveat, and no input mutation.
