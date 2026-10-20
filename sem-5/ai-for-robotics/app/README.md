# Offline study interface

The application is intentionally dependency-free. It runs from a `file://` URL with no service worker, account, network connection, external script, font, or CSS dependency. Prose uses a system-font stack. Equations remain selectable, screen-reader-accessible text and exact source equations remain available in the embedded source PDFs.

## Source files

- `index.html`: semantic document shell, dialogs, security policy and build tokens.
- `styles.css`: responsive light/dark interface, focus states, reduced motion and print layouts.
- `core.js`: pure scoring, deterministic shuffling, exam snapshots, search, mastery and versioned backup validation/merge.
- `app.js`: interface, offline evidence viewer, study modes, exports, storage handling and learning-tool integration.
- `learning-tools.js`: independently tested algorithm and numerical engines, maintained separately.
- `core.test.js`: software-only fixtures and deterministic logic regressions, never embedded in the course bank.
- `algorithm-selector.test.js`: isolated component/event regressions using minimal DOM doubles, not a substitute for browser QA.

## Build and test

From the project root:

```
python scripts/validate.py
node --test app/core.test.js app/algorithm-selector.test.js
node --test tests/test_learning_tools.js
python scripts/build.py
python -m unittest discover -s tests -p 'test_app_offline.py' -v
node tests/browser_offline.js dist/ai-for-robotics-mcq.html
```

A release additionally requires `python scripts/build.py --release`. It cannot bypass incomplete coverage, stale review bindings, missing evidence or an unfinished independent coverage challenge. The default build is allowed to create an honestly labeled partial checkpoint.

For isolated browser fixtures, `--test-fixture --bank tests/fixtures/synthetic_bank.json --output /tmp/robotics-fixture.html` explicitly permits software-test data. The builder rejects the production filename for this mode. Synthetic question fixtures must never be copied into `data/bank.json`.

## Evidence packaging and size

The default build embeds each complete original source PDF and all required diagrams. Exact page previews are omitted only when their complete source PDF is embedded; `--include-page-previews` adds them too. This avoids duplicating 2,012 pages while preserving every source page offline. PDFs decode lazily to local Blob URLs on first use. PDF navigation uses the citation’s **one-based physical page**, never a printed slide number. The complete PDF is downloadable if a browser lacks a native embedded PDF viewer. Native PDF viewer controls handle PDF zoom; image previews have application zoom controls.

`dist/ai-for-robotics-mcq.build-report.json` records size, hash, embedded assets, integrity results and build time. Build time does not certify browser load time. Browser performance, PDF rendering and file-download QA are separate gates.

## Study behavior

- Practice, exams, revision and mastery use verified questions by default. Draft/flagged/rejected records remain in the audit view.
- The algorithm laboratory lists only verified source-linked records by default, plus an explicitly labeled synthetic demonstration. An opt-in audit checkbox exposes unverified source examples. Missing, stale, unavailable, uninspected or unresolved source provenance remains excluded even in audit mode. Turning audit off or changing a configuration clears the prior trace. Leaving Learning tools resets audit mode.
- Answer IDs survive every option shuffle. Single-select immediate feedback is optional; multi-select always requires submission.
- Exams store immutable question snapshots, exact option order, scoring, selections, review flags and a fixed wall-clock end time. Reload/background time never restarts the timer. Solutions and answer exports are locked until completion. Changing the system clock is not supported.
- Partial credit is opt-in and explicitly described before starting. A complete correct answer earns the positive mark; unanswered earns zero. Fractional multi-select subtracts the proportion of wrong options selected and floors at the selected negative penalty. Selecting every option does not yield full credit.
- A changed question fingerprint resets its current practice selection and prevents old responses from establishing mastery of the changed version. Historical exam snapshots and result answer keys remain intact.
- Mastery counts distinct questions and reports skill coverage separately from latest-answer accuracy. The numerical engine’s distinct family model is separate from ordinary question evidence.
- Local storage failures produce a persistent warning. Progress backups merge by event/attempt IDs, preserve unknown question IDs and keep current settings. Active-exam conflicts require an explicit choice.
- Exports include question IDs, exact option order, selected/correct option IDs, citations, source hashes, variant provenance and scoring. CSV fields are quoted, UTF-8 with BOM, and protected against spreadsheet formula injection. Print-to-PDF offers separate paper, key and complete worked-solution versions.

## Accessibility

Controls use semantic labels, native buttons, fieldsets, visible focus, status text and non-color symbols. The interface supports system/light/dark themes, keyboard shortcuts, responsive widths, reduced motion and zoomable evidence. Shortcuts are inactive while typing. Search indexes question text, options, explanations, tags, concepts and formulas.

## QA limits at initial checkpoint

Pure logic and static offline checks are executable locally. A restricted runtime initially prevented Chromium from creating its process socket, and the separate elevated launch failed in the environment wrapper. These are **unexecuted browser tests**, not passes. Do not claim final browser behavior or readable PDF rendering has been verified until the browser report and inspected screenshots establish it.

### Supported cloud-browser route checked

A later check reached the cloud Chromium/CDP inventory through the supported Computer Use tool. The tool explicitly denied `file:` navigation because that surface allows only HTTP(S); the denial was respected. A separate normal HTTP development server returned HTTP 200 inside the task executor, but the cloud browser could not reach it: loopback returned `ERR_CONNECTION_REFUSED`, and the executor's observed address returned `ERR_BLOCKED_BY_CLIENT`. The server was stopped. No tunnel, protocol disguise or native-browser workaround was used. **Executed application browser checks remain zero**, including final downloaded-file/offline behavior. These attempts establish access limits, not application correctness.

## Final UI and delivery checks

The course explorer now includes lazy, nested subtopic links. Coverage can be narrowed by source, week and lecture without changing physical page numbering. Active exams expose their versioned backup/import controls while continuing to hide solution/source feedback and ordinary answer exports.

The changed application bytes require a fresh independent resource-policy hash review before final build activation. Read `docs/FINAL_UI_REVIEW_HANDOFF.md`; do not silently preserve an obsolete implementation binding.

Run all deterministic suites with `node --test app/*.test.js tests/test_*.js` and `python -m unittest discover -s tests -p 'test_*.py' -v`. The inert DOM regressions in `app/final-ui.test.js` are not browser tests.

Use `tests/browser_final_artifact.js` for the comprehensive exact-downloaded-file interaction suite. It is inert without `--execute`, requires the expected HTML SHA-256 from the delivery receipt before launch, and never grants human visual/source-PDF acceptance. The earlier `browser_offline.js` remains only a smoke/performance runner. Full environment requirements, commands, screenshot criteria and lossless packaging instructions are in `docs/FINAL_OFFLINE_QA.md`. The requirement-by-requirement implementation audit is `docs/APP_REQUIREMENT_AUDIT.md`.

`python scripts/package_delivery.py --html dist/ai-for-robotics-mcq.html --build-report dist/ai-for-robotics-mcq.build-report.json --output dist/ai-for-robotics-mcq.zip` creates a lossless transport ZIP and receipt. An incomplete checkpoint requires `--allow-partial`. Every decoded embedded asset and the extracted HTML are rehashed; neither original source PDF is omitted or downsampled. The HTML still works alone after extraction. Upload, independently downloaded byte verification and actual browser/visual review remain separate steps.

The last-day revision view now includes a bounded source-assignment priority for fresh learners: currently verified assignment adaptations and exact independently approved reuse links. It is explicitly not a prediction of exam likelihood. Existing mistakes, review flags and bookmarks retain stronger ranking; normal scope/search/learning filters apply first. The route does not edit questions or count reused coverage as new mastery evidence. Runtime and assembler metadata are separately fail-closed; policy 1.0.3 requires independent approval before activation.
