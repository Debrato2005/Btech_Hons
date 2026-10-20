# Exact-download offline release verification

## Status and the precise remaining environment requirement

The deterministic logic and static artifact suites are not browser verification. As of the initial final-delivery audit, there are **zero executed application-browser checks**. The previous executor Chromium launch aborted before opening a page (`socket() failed: Operation not permitted (1)`, SIGABRT). The separate supported cloud browser denies `file:` navigation, cannot reach the executor's loopback server (`ERR_CONNECTION_REFUSED`), and blocks the executor-address route (`ERR_BLOCKED_BY_CLIENT`). Those routes are not to be retried unchanged, tunneled, disguised or bypassed.

What is needed is a **permitted computer or task environment** with an already installed Node.js, Playwright module and Chromium-compatible browser. Its browser process must be allowed to create its ordinary local process sockets and open a local `file://` URL. The independently downloaded final HTML and its delivery receipt must be readable there. A normal offline PDF reader is additionally required if that browser does not render embedded PDF objects. No server, account, network connection, package installation or permission weakening is required by the application. A computer being listed does not establish authorization or a connection to use it.

## Identity of the file under test

1. Build/package only after the content and UI checkpoint is frozen. Do not substitute an earlier `dist` file.
2. Download the delivered HTML, or download the lossless ZIP and extract its HTML. Keep the original downloaded ZIP and the receipt.
3. Compare the HTML's SHA-256 and byte length with the delivery receipt. ZIP compression must not change the extracted HTML bytes. If either differs, stop and investigate. A Git LFS pointer, truncated HTML or HTML error page is not a deliverable.
4. Run the test against that exact downloaded/extracted path, not the source tree's build output. The test records its own SHA-256 before opening the file.
5. A matching hash proves byte identity, not that a browser rendered it or that the source answers are correct. Record the actual download URL, retrieval date and hash separately.

## Prepared runner commands

The full runner is `tests/browser_final_artifact.js`. Without `--execute` it only prints instructions and never imports Playwright or starts a browser. In the permitted environment, with dependencies already installed:

```sh
node tests/browser_final_artifact.js --execute \
  --artifact /absolute/path/to/downloaded/ai-for-robotics-mcq.html \
  --expected-sha256 COPY_THE_HTML_SHA256_FROM_THE_RECEIPT \
  --report /absolute/path/to/qa/browser-final.json \
  --download-description "Downloaded from VERIFIED_DELIVERY_URL at UTC_DATE"
```

Set `CHROMIUM_PATH` to an already installed, permitted browser when Playwright's existing default browser is not the intended one. Add `--headed` for an ordinary visible browser. Do not run the command in the unchanged denied executor. A launch failure is recorded as blocked and is not retried. Do not install a browser or alter security flags as part of this check.

The runner uses a disposable browser context, never an existing study profile. It disables networking before navigation, does not modify question/tool/source data, records exact browser and Node versions, and exercises the actual embedded bank. Real-course single- and multi-select questions are selected from that bank; missing eligible content is pending, never replaced by a synthetic approval. It records interactions, download hashes, screenshots, initial load/interaction timings and browser memory metrics where supported. Exam expiration uses a separately disclosed accelerated JavaScript wall clock, while the reload/resume check first uses ordinary time.

The resource-only runner remains available:

```sh
node tests/browser_learning_resources_artifact.js --execute \
  /absolute/path/to/downloaded/ai-for-robotics-mcq.html \
  /absolute/path/to/qa/browser-resources.json
```

A prepared runner and a syntax/fixture test are not evidence that it has executed successfully in a real browser.

## Human interaction and visual acceptance

Review the exact file offline at desktop (1440×1000), tablet (768×1024), and mobile (390×844) sizes. Test light and dark themes, system theme, and 200% browser zoom. Inspect the screenshots and the actual responsive UI, rather than accepting a non-overflow number alone. Record browser/version, operating system, HTML SHA-256, reviewer, time, each result and screenshot filename in the visual review report. Use `passed`, `failed`, or `pending`; no missing result may be called passed.

| Area | Required interaction / visual evidence | Acceptance criterion |
| --- | --- | --- |
| Initial load | Open the downloaded HTML with Internet disconnected; photograph/screenshot the settled practice screen. | No blank app, missing font symbols, broken assets or console errors. Partial/completion status and actual counts are legible and honest. Record measured load time and peak/settled memory; do not equate build time with browser performance. |
| Navigation | Collapse/expand sidebar; open a week, lecture, topic and subtopic; clear filters; use previous/next and a distant question-palette page. | The intended verified subset and stable question ID appear; current, unanswered, correct/incorrect, bookmark and review states have text/symbol distinctions, not color alone. |
| Practice | Answer a single-select correctly and incorrectly; toggle immediate feedback; answer a multi-select partially, then with its complete set; submit/reset/skip. | Single-select feedback respects the setting. Multi-select never reveals until explicit submit. Every distractor has its matching explanation after shuffle. Reset retains history but clears the current selection. |
| Keyboard | Tab through controls; use Enter/Space, 1–9, arrows, B/R, `/`, Escape; type those characters in search and configuration inputs. | Visible focus; native button activation works; typing never triggers shortcuts; dialogs can be closed and focus is useful; options and all essential actions are keyboard reachable. |
| Exam setup | Scope by week/lecture, count and exact difficulty mix; set +marks, penalty and partial credit. | Scoring is shown before start and explicitly not called the official marking scheme. Invalid counts/mixes are rejected rather than silently altered. |
| Exam session | Select, clear, flag and navigate; reload; background the tab; close/reopen the same file. | Exact question/option ordering, selections, flags and fixed end time survive. No solution, correctness class, source evidence or answer export is exposed during the active attempt. |
| Submission / expiry | Submit an attempt; separately allow a short real-time attempt to expire while backgrounded and reopen it. | Saved selections are scored once; unanswered items receive zero; no reset timer or duplicate history. The runner's accelerated-clock test does not replace this real-time human check. |
| Revision / mastery | Mark a question, make mistakes, repeat an answer, open revision and progress. | Bookmarks/errors/high-yield route and prerequisite/related links are usable. Repeating one memorized question does not increase breadth. Current and historical versions are not conflated. |
| Source evidence | Open both a lecture citation and an assignment citation; read its exact one-based page, printed-slide distinction and SHA; save each embedded PDF. | Correct source and physical page, readable full-resolution text/equations/diagram labels. Saved PDF hashes match the original sources. If the PDF viewer ignores `#page`, use its page control and record the limitation. |
| Source zoom | Zoom native PDF controls, or save/open offline when no native viewer exists. For image assets use app zoom and keyboard activation. | Small print, formulas and figure labels are actually readable. Disabled app zoom on a PDF is intentional; native PDF controls are separate. A nonempty PDF object rectangle is not proof of rendering. |
| Coverage | Drill source → week → lecture → page → concept → verified/audit questions; inspect an excluded/repeated/unresolved page when present. | Counts and specific disposition reasons are visible; links reach the intended source/question; one question is not misrepresented as full concept coverage. |
| Formulas / confusions / traps | Filter by week/lecture and search, page results, open exact-context details and all source/approval links. | Formula variables/units/assumptions and source qualifications remain readable. Side-by-side distinctions are clear on desktop and stack on mobile. Closed review gates remain closed, never empty without an explanation. |
| Algorithms | Run each approved BFS, DFS, UCS, A* and Q-learning record; step/back/reset; inspect graph/frontier/closed states or Q-table and convention details. | Labels and edge costs are not clipped; each state change is visible; source configuration and chosen algorithm agree. Synthetic/editor changes stay clearly labeled and cannot silently become verified. |
| Numerical tools | Generate each approved family with a saved seed, answer, save JSON and regenerate. | Four distinct plausible options, matching units/rounding, complete regenerated workings and exact seed/version/parameters. Invalid/currently revoked families do not activate. |
| Backups | Export; open a fresh browser profile; import; merge the same file twice; import a different-bank and malformed backup. | History, attempts, bookmarks/review flags survive; duplicate records do not multiply; existing progress is not silently removed; settings/conflict behavior is stated. Save failures show a persistent actionable warning. |
| Structured exports | Save question/results JSON and CSV; inspect a shuffled completed exam. | Stable IDs, citations, selected and correct IDs, actual order, variants and scoring survive. CSV quotes/newlines/Unicode and spreadsheet-leading formula characters are safely handled. |
| Print/PDF | Print a small scoped paper, key and worked solutions; save all three PDFs and inspect each page. | Paper contains no answers; separate key matches actual displayed order; solution includes every option explanation/source. No clipped equations/figures, cropped lines, illegible breaks or dark theme backgrounds. |

### Required screenshots / files

- Practice desktop, tablet and mobile in light/dark; one focused control and one opened mobile sidebar.
- A full worked solution containing equations and per-option explanations.
- Active exam with selected/review-marked questions and no correctness feedback; completed result with the same ordering.
- A source dialog for a lecture and an assignment, plus an actually readable zoomed source page. The screenshot must capture rendered source pixels, not only the outer dialog.
- Coverage drilldown with concepts and source links.
- Formula, confusion-pair and trap context; an intermediate search graph and Q-learning Q-table; a generated numerical worked solution.
- Progress/backups and storage-failure warning.
- First and last pages (and every problematic equation/diagram page) of paper/key/worked-solution PDFs.
- Browser report, download receipt, screenshot hash manifest, saved source-PDF hash checks and a separately completed visual-review record.

Do not label final browser verification complete until both the interaction report and actual image/PDF review pass for the same artifact hash. If only a checkpoint can be delivered, state unfinished content, UI or browser gates precisely.

## Lossless transport packaging

The final HTML may exceed a service's ordinary attachment or Git-object limit. `scripts/package_delivery.py` makes a standard lossless ZIP without downsampling or omitting either original source PDF. The HTML remains self-contained after extraction; QA files/receipts in the ZIP are optional and are never runtime dependencies.

After a new validated build, use a workspace disk with sufficient free space:

```sh
python scripts/package_delivery.py \
  --html dist/ai-for-robotics-mcq.html \
  --build-report dist/ai-for-robotics-mcq.build-report.json \
  --output dist/ai-for-robotics-mcq.zip
```

A partial checkpoint requires the additional explicit `--allow-partial` flag and remains labeled partial in both receipts. The helper refuses synthetic course deliverables, mismatched HTML/build-report bytes, missing/corrupted embedded source data and a failing integrity report. It hashes every decoded embedded asset, creates the ZIP, stream-decompresses its HTML member and verifies the exact hash/length again. The external `.delivery-receipt.json` records both the HTML and ZIP hashes; it does not mark browser QA passed.

The earlier packaging probe found that `/tmp` was a separate nearly full 4.9 GiB tmpfs, while the workspace filesystem had ample capacity. Prefer `dist/` on the workspace filesystem rather than `/tmp` for large packaging/download outputs. Do not delete unrelated files or change permissions to work around capacity.

Before actual delivery, independently check the selected service's current upload/download limits and access. Uploading, downloading and testing that exact copy are separate steps, not accomplished by making the ZIP locally. Do not publish a Git LFS pointer, an older pre-repair build or an unchecked generated download link as the final app.

### Fresh-profile revision acceptance

Before answering anything, open Revision with all ordinary filters clear. Capture `fresh-source-assignment-revision.png`: the route must be nonempty when the final bank has currently approved assignment adaptations, show the Source-assignment priority badge, and state that this is a study-order heuristic, not predicted exam likelihood. Verify a week/lecture filter narrows the route; return to clear filters. An unsubmitted question must not show a solution. Then make one error and bookmark a different question and verify those priorities coexist with the assignment route without creating duplicate questions or mastery events. Missing/stale mapping evidence must remove its reuse priority, never authorize new question content.

For reviewed semantic reuse, capture the assignment coverage concept with its unchanged original status and “Zero added questions” label. Follow each reused target, use its assignment-reuse source backlink, and use “Practice questions linked to this page” to return to the linked verified questions. Verify the excluded duplicate is not newly offered as verified. These links must disappear when current mapping/review evidence is missing or stale.

Legacy closure metadata must remain distinct: inspect an L30 semantic alias and the closing-quotation commentary concept. Recorded IDs/evidence paths and qualifications must be visible without unchecked navigation or green/direct-verified promotion. The quotation exclusion must say it does not exclude the whole source page. Capture both examples and expand the complete recorded metadata.

### Mistake-derived follow-ups and visible state symbols

After an incorrect current-version answer, inspect Progress and Revision. A recorded shared concept or prerequisite must provide a verified follow-up with its reason; an ordinary submitted solution must also show bounded related/prerequisite suggestions. The labels must say these are study heuristics, not new author-reviewed semantic equivalences or exam predictions. Change week/lecture/search filters and verify they apply before the eight-item solution cap. Answer the original question correctly later: its old miss must stop seeding weak-concept suggestions. Imported unbound/stale-version events must not seed them. Capture the incorrect and correct palette states with visible ✕ and ✓. During an active exam, answered/unanswered states must use ● and ○ without correctness symbols, related panels or study-answer navigation.

### Required question-input figures

The independent input inventory is separate from answer reviews and full-PDF source citations. The runner checks every verified question's current visual binding and actual embedded image SHA, then exercises one real required-input question through practice, keyboard zoom, an active exam, reload and paper printing. It saves `required-input-practice.png`, `required-input-zoom.png`, `required-input-active-exam.png`, `required-input-exam-zoom.png`, the exact crop download and `required-input-paper.pdf`. These prepared checks have not executed in the denied environment.

Human acceptance must inspect those actual pixels, plus the independently reviewed crop inventory for representative diagram, table, code, graph and equation-input layouts present in the final artifact. Verify complete labels/axes/values and readable text at desktop/mobile/200% zoom. Compare source page and crop rectangle with the approved source. No highlighted answer, completed solution, answer-key marker or result unavailable in the question may appear before answering. Active-exam zoom must open only its reviewed input crop, never the complete source PDF. Practice/source evidence still offers the unchanged original PDFs outside the exam.

Required-input failure is explicit: an absent/stale independent inventory or crop blocks answer controls. Starting an exam or printing an incomplete selected scope must refuse the whole scope with named question IDs, not silently choose fewer questions. Browser image-decode failure also blocks answering/printing. A saved required-figure exam binds its exact reviewed question, record, reviewer and pixel identities. Import/reload into a mismatched bank must preserve selections and the original deadline while refusing replacement images. Restore its original HTML to continue; a legacy exam without input stamps is usable only for an exact-current independently reviewed self-contained question. A delayed backup import that activates an exam must revoke an already-open full source preview, including its zoom/download buttons. Observe this with real interactions; deterministic tests are not a substitute.

Printing waits for every required image to decode and rechecks current eligibility immediately before opening print. Inspect each resulting figure-containing PDF page for clipping, missing pixels, text legibility and answer separation. No screenshot or byte hash alone establishes these visual criteria.

Prepare an answer key, then start an exam and use the browser’s ordinary Print command. The cached key must be gone; only a neutral print-lock notice may appear. Repeat a native print after revoking a visual binding in the deterministic fixture, not by editing the delivered course artifact. Browser print guarding is a UI privacy boundary, not a claim that an offline client can enforce proctored exam security. The prepared runner additionally saves `blocked-active-exam-print.pdf` for human inspection.

## Deterministic test entrypoint and browser restriction

Run `python3 scripts/record_validated_milestone.py` for the deterministic integration suite.
Its explicit Node allowlist is `app/*.test.js` plus `tests/test_*.js`; these patterns exclude the browser runners.
Do not run `node --test tests/*.js`, `node tests/*.js`, or another wildcard that includes browser scripts.
Browser runners require a separately confirmed permitted browser environment and the exact independently downloaded artifact.
The recorded executor socket and cloud file-policy failures do not permit repeated launch attempts or alternate-route bypasses.
A passing logic suite does not establish browser, offline, interaction, screenshot, print-layout or PDF-viewer verification.

### Supplemental notebook/code inputs (policy 1.0.5)

These premises are separate text evidence, never PDF crops. Before answering, a required notebook question must display the exact reviewed code substring with local file and notebook SHA-256, zero-based cell index, cell ID (including recorded Colab metadata IDs), one-based inclusive cell/output line range, and a linked lecture citation. Commit-plus-blob, commit-only and locally hash-bound provenance must be visibly distinct. An output-stripped local notebook must not be called the unchanged upstream Git blob. No source code is executed by the app or these QA checks.

Only an explicitly reviewed output-reading/comparison question may show `Historical saved notebook output · given stimulus`. That label must say it is not a new execution. Ordinary calculate/trace questions must not receive a saved worked answer. Independently inspect every supplied snippet's question intent and source slice; matching text hashes alone do not certify no-answer-leak content.

The prepared runner now compares exact displayed code text, exercises code/output questions in an active exam and across reload, verifies their saved supplemental identities, and generates `supplemental-QUESTION-ID.pdf` plus desktop/mobile/exam screenshots. Inspect whitespace, indentation, wrapping, long identifiers, provenance legibility and printed page breaks. A stale file/text/review binding must block the whole selected exam/print scope; source or text updates must not silently replace a saved exam's premises. No browser run is implied by preparation or syntax checking of this runner.
