# Narrow final application UI review

## Author scope and frozen changes

Only `app/app.js` changes application behavior. The exact baseline-to-candidate diff is `audits/final-delivery-audit/final-ui.patch`; candidate hashes are in `audits/final-delivery-audit/final-ui-frozen-code-hashes.txt`. No question, answer, source, reviewed learning-tool object or current policy object was edited. This is a narrow application/integration review, not a new subject-matter or blind-answer approval.

The prior policy hash-binding is stale because it includes `app/app.js`. It must not be silently reused or weakened. A different reviewer must inspect these deltas, the applicable policy dependencies and exact final hashes before the coordinator creates/activates a new policy revision. Existing unchanged question/tool computation approvals are to remain intact; their unchanged objects are not newly authored by this UI work.

## Expected behaviors to challenge independently

1. Course explorer: week → lecture → topic → subtopic navigation sets all four ordinary practice filters. Parent topic and lecture scopes clear the more-specific scope. Navigation remains blocked during an active exam. Numeric/string-equivalent week labels must not duplicate the tree. Subtopic buttons are created only when their topic is expanded, once, avoiding thousands of initial DOM nodes.
2. Coverage: source → week → lecture filters reduce the heatmap without renumbering physical PDF pages. Week changes clear lecture and pagination; source changes clear week/lecture/pagination. Available lecture choices reflect the selected week. Status totals refer to the filtered page set; source ledger counts remain separately stated. Pagination describes matched records rather than falsely labeling their ordinal position as a physical page. Page → concepts → questions/source behavior is unchanged.
3. Active exam: reachable export/import backup buttons call the existing versioned backup/import path while the exam is active. No answer export menu, solution block, source button or correctness feedback is added to active-exam UI. The backup necessarily retains complete immutable question snapshots, ordering, selections, scoring and end time to support faithful recovery, just as local storage does. The normal active-exam view lock and explicit merge/conflict confirmation remain unchanged.

## Tests and distinct evidence boundaries

- `app/final-ui.test.js`: three new deterministic component/event tests with inert DOM doubles. These challenge lazy nested scope selection, filtered physical-page labels/dependent resets and active-exam backup reachability without solution rendering.
- `tests/test_final_artifact_runner.js`: no-launch CLI/identity regressions for the prepared full runner. The deliberately wrong-hash fixture is software-only and stops before importing Playwright.
- `tests/browser_final_artifact.js`: prepared exact-downloaded-file interaction suite; inert without `--execute`. It requires the delivery receipt's expected hash before browser launch, disables networking, exercises the actual bank and keeps human/source-PDF/print review pending.
- `tests/browser_learning_resources_artifact.js`: a runner-only fix now distinguishes image zoom from native PDF controls. The former version tried to click an intentionally disabled app zoom button on embedded PDFs. This does not certify native PDF rendering.
- `docs/FINAL_OFFLINE_QA.md`: precise environment requirement, transfer commands, full interaction matrix and screenshot/PDF acceptance criteria.

No browser was launched or retried by this work. No browser/visual/source-readability pass is claimed. No packages were installed, no remote routes were retried, and no Git or canonical content operations were performed.
