# Current status

See COMPLETION.md and final-validation.json: all six qualified questions now independently accepted and staged, with no shared bank or Git write. The earlier notes below preserve the review sequence rather than current pending counts.

# Qualified legacy-concept closure

Six new draft questions are frozen for independent answer-first review. Read `neutral-packet-v1.json` first (SHA256 `8cf5edc49c8fa7cfcd1a651329f4e751d0cc6669cf15f98088d2282f44e8b167`). Freeze independent answers before reading `qualified-drafts-v1.json` or `author_qualified_drafts.py`. Exact correctness-sensitive and whole-object hashes are in `freeze-manifest-v1.json`. New IDs: W01-L02-Q-106/107 and W01-L05-Q-081/082/083/084. Existing six concept IDs and all adjudicated caveats/evidence scopes are preserved. No approval is implied by prior adjudication or this author packet.

All writes in this stream are audit-only. No Git, canonical bank, app, data, scripts or tests were changed. All 4915 accepted whole objects from the author freeze remain unchanged after the newer integration snapshot. L59v2 is untouched.

- `L30-durable-coverage-crosslinks.json`: eight legacy aliases resolve to exact-hash reviewed questions, retaining original concept objects and source pages. Source-local and semantic-only links are separate. Page 905 still omits terminal-row zeroing; Q056 cites page 914 and is a stated adaptation, not a source-printed terminal mask.
- `L02-summary-quote-disposition.json`: exclude only the attributed quotation/commentary, not the whole page. All seven technical summary rows remain accounted for. The perception row links semantically to unchanged Q038 at pages 70/80, not a fabricated citation to page 93.
- `summary-row-crosslinks.json`: all substantive rows of summaries 984/1085/1195 have explicit prior reviewed question/hash links, with source overstatements retained as qualifications. No accepted question needs editing.
- `full-lecture-ledger-challenge.json` and `lecture-page-accountability.json`: scan all 1953 lecture pages and current concepts. No missing inspection-batch IDs, no unreviewed/unresolved dispositions, no asymmetric concept links, and no review-gate status mismatch. Four uncited substantive page candidates are p175 plus those three summaries. Nine explicit repeated summaries and 34 stale L60 conceptLedgerPending flags remain metadata reconciliation, not newly missing source content. This is not a claim that one reviewer freshly viewed all 1953 pages; 15 actual pages were personally viewed in this stream.
- `integration-proposals.json`: integration instructions without canonical edits. Resolve coverage through sidecars/metadata, not mutation of accepted question objects. Concept schema has no excluded status: retain quote concept ID with an explicit commentary coverage disposition rather than inventing a status enum.
- `deterministic-validation.json`: validates frozen schemas, neutral packet, exact scopes, aliases, accepted-object preservation and 144 option-order permutations. This is logic/integrity validation, not independent answer review or browser QA.

Primary evidence provenance stays exact: ROS releases and OccupancyGrid are official indexed result evidence, not full reads. Direct rolling Releases and OccupancyGrid message pages were Anubis-denied. Do not retry those pages or retrieve blocked content through alternate routes. All previously denied ROS QoS/Nodes/robot_localization/REP105, notebook, dependency/model retrieval and browser routes remain stopped. This stream used only installed Python and local source image inspection.

Next: lead freezes independent answers, then reveals six keys/explanations and records exact-hash decisions. Integrator may consume proposed sidecars after that review while preserving accepted question objects. Existing assignment, actual offline browser, final download and GitHub release gates remain separate.

## Review and staging update

Independent v1 review approved Q082/Q083/Q084 and requested three narrow repairs. V1 files remain immutable. The repaired Q106/Q107/Q081 are frozen in `neutral-packet-v2.json` (SHA256 `a9b7fa38c6ceee20044ffdf317560d6f99ff64e64ef75a42b233e3254253b20f`); keys are in `qualified-drafts-v2.json`. Do not open the v2 key file or repair script until independent responses are sealed.

With lead authorization, canonical authoring inputs were subsequently staged, but the shared bank was NOT reassembled. `canonical-staging-report.json` lists the exact nine touched paths. The three v1-approved question whole objects are unchanged, all 192 existing L02/L05 assembled question whole objects remain identical after an in-memory gate pass, and the three v2 repairs correctly remain drafts. Six original concepts gain their question links; eight L30 aliases and the quote concept gain explicit schema-safe coverage dispositions; p93 preserves seven summary rows and 984/1085/1195 gain repeated-page crosslinks. L59 and L60 files remain untouched.

The first staging command stopped at a missing review directory before any canonical write; creating that ordinary local directory resolved it. The next command completed our writes then stopped on a concurrent unrelated duplicate concept ASSIGN-W06-C008 in the two assignment W06 files. No assignment file was changed. Owned lecture-scope validation passes; reconcile that other stream before full assembly if the duplicate is still present. The staging script is intentionally not rerunnable after additions exist; use the read-only `finalize_staging_report.py` for checks.
