# Recovery instructions

1. Fetch the latest `main` from `Debrato2005/Btech_Hons` before resuming.
2. Read `EXECUTION_BRIEF.md`, `project-state.json`, `docs/DATA_CONTRACT.md` when present, and all audit files.
3. Reconcile existing files and unfinished assignments; do not restart or duplicate reviewed work.
4. Source files originate from Drive folder `1kJJLyX3HjmCX652v4jy_RyM7gS04mpx_`.
5. The lecture PDF ID is `11o0RzXIrDTIbb0FNe1Tl_-cgV4aKVl2m`.
6. The assignment-solutions PDF ID is `16Ybyme8t18KxPRKQYAinJYsidLQyxoDQ`.
7. Verify source hashes against the saved inventory before relying on any previous review.
8. Only the integration owner commits and pushes; workers use separate owned paths.
9. Commit validated slices and regularly push a meaningful checkpoint; verify the remote SHA after each push.
10. Keep unverified, flagged and rejected questions out of the ordinary study and examination pool.
11. A successful data validator does not establish source correctness or complete visual coverage.
12. Never modify the OncoSyn document or repository in this project.

## Next actions

Read docs/handoffs/integration.md and each worker handoff before assigning more work. Sources are retrieved and hashed: 1,953 lecture pages plus59 assignment pages. Read sources/README.md to recover sources and regenerate maps/text/previews. Run python3 scripts/assemble_bank.py, python3 scripts/validate.py, and python3 scripts/build.py after recovery. Question and inspection batches are the editable source of truth; generated bank.json is rebuilt. Review records bind exact question/source hashes and are never reusable after content revisions. Keep source disputes visible and unresolved items out of accepted study. App and learning engines are implemented, but full course content and actual downloaded-file offline QA remain unfinished.

## Verification of checkpoints

Use `git ls-remote origin refs/heads/main` and compare with the intended commit. Local commits alone are not durable completion. This file is updated at meaningful checkpoints; current commits are self-identifying through Git history.
