# AI for Robotics study bank and offline app

Status: recorded source coverage, independent content/input review and application implementation are closed; exact offline browser acceptance and the newest Git checkpoint remain pending.

This Semester 5 project is separate from OncoSyn. The sources contain 1,953 lecture pages and 59 assignment pages across 12 weeks and 60 lectures. All 2,012 physical pages have recorded distributed visual inspections.

The validated bank contains **5,069 independently reviewed questions**, zero drafts and two excluded duplicate adaptations. All 120 original assignment items are represented by 118 direct adaptations and two reviewed reuse mappings. Original answer-key conflicts and scientific qualifications remain visible.

## Application

One self-contained HTML embeds both complete original PDFs and the question bank. It provides practice, configurable timed exams, progress backups, source navigation, revision, formula/comparison/trap views, numerical variations and algorithm walkthroughs. All 18 approved learning tools activate under the reviewed policy. Study-priority and mastery scores are transparent heuristics, not official exam predictions.

The exact 20 October 2026 build has 208 passing Python tests and 137 passing Node tests. Its assembly, integrity validator, build and both test processes exited successfully with an unchanged input manifest. The receipt is `audits/validated-milestone-20261020T043414Z.json`.

The coverage audit accounts for every recorded lecture concept and assignment item. It distinguishes direct questions, qualified semantic reuse, repeated pages and narrow exclusions. This bounded review is not a guarantee that no future reviewer could identify another angle.

## Build and verify

- Follow `RESUME.md` and `docs/handoffs/integration.md` before resuming or making remote changes.
- Run `python3 scripts/record_validated_milestone.py` for assembly, integrity validation, build and deterministic tests.
- Use `scripts/package_delivery.py` for lossless ZIP packaging and byte-identity receipts.
- Use `docs/FINAL_OFFLINE_QA.md` and `tests/browser_final_artifact.js` only in a permitted browser environment for actual offline interaction and visual acceptance.

Logic tests and source review do not prove browser rendering. Actual checks of the independently downloaded HTML, source-PDF readability, print output, performance and screenshots remain pending. The app needs no server or network at runtime.

The latest verified GitHub checkpoint remains `575e2c9f304f4d3847092604afbfbcb0b814ad71`; newer work is not claimed as remotely committed while a Git blob approval is pending. The final recovery archive preserves the newer local source, tests and evidence separately.

See `EXECUTION_BRIEF.md` for the complete requirements and `sources/README.md` for source recovery.

All 5,069 active questions pass the current input-completeness gate. The 694 input-dependent questions use 487 deduplicated exact-source PNGs and 34 separately bound notebook snippets. Practice, exams and print retain those inputs without exposing the full answer source during an exam.

Read [the delivery report](docs/DELIVERY_REPORT.md) for counts by week, difficulty and type, exact hashes, source qualifications and remaining acceptance work. Read [Open and study](docs/OPEN_AND_STUDY.md) for usage. The HTML is 280,893,510 bytes; real browser load time, memory use and responsiveness are not yet measured.
