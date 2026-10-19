# Offline study interface

The application is intentionally dependency-free. It runs from a `file://` URL with no service worker, account, network connection, external script, font, or CSS dependency. Prose uses a system-font stack. Equations remain selectable, screen-reader-accessible text and exact source equations remain available in the embedded source PDFs.

## Source files

- `index.html`: semantic document shell, dialogs, security policy and build tokens.
- `styles.css`: responsive light/dark interface, focus states, reduced motion and print layouts.
- `core.js`: pure scoring, deterministic shuffling, exam snapshots, search, mastery and versioned backup validation/merge.
- `app.js`: interface, offline evidence viewer, study modes, exports, storage handling and learning-tool integration.
- `learning-tools.js`: independently tested algorithm and numerical engines, maintained separately.
- `core.test.js`: software-only fixtures and deterministic logic regressions, never embedded in the course bank.

## Build and test

From the project root:

```
python scripts/validate.py
node --test app/core.test.js
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
