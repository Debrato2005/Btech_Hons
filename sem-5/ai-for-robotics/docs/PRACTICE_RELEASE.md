# Practice delivery: AI for Robotics

Open `ai-for-robotics-mcq/ai-for-robotics-mcq.html` directly in a modern browser.
The app needs no server, account, installation or network.
Current scope is [Practice only](CURRENT_SCOPE.md).

All **5,069 verified questions** match the original delivery exactly, including
solutions, answer IDs, workings, assumptions and citations. Two flagged duplicate
adaptations remain excluded. The bank version stays `0.1.20261020T043415Z`.
Both original PDFs, all 487 PNGs and 34 required code/output snippets remain.
The 694 input-dependent questions retain their full inputs. Reviews and coverage
records stay in the repository.

## Performance

| Metric | Original | Practice |
|---|---:|---:|
| HTML size (MiB) | 267.9 | 201.6 |
| Usable (seconds) | 5.79 | 1.62 |
| Peak startup browser RSS (MiB) | 1,999.6 | 884.8 |
| Steady browser RSS (MiB) | 1,335.6 | 770.5 |
| Steady renderer RSS (MiB) | 1,049.4 | 483.7 |
| Steady JS heap (MiB) | 301.8 | 56.4 |

These measurements use fresh offline Chromium 153 headless-shell processes.
A separate full Chromium run includes native PDF rendering. Its steady browser
RSS changes from 1,785.5 to 1,232.2 MiB. Renderer RSS changes
from 1,281.8 to 722.4 MiB. Usable time changes
from 10.06 to 1.88 seconds.
Environment: `Linux-6.18.33.2-microsoft-standard-WSL2-x86_64-with-glibc2.39`.

Each run opens the full bank through `file://` with networking disabled.
It exercises 100 question navigations, 30 source previews, 20 figure questions
and three revisits. The final cache has 5 entries. Closed previews remove
the viewer. One cached PDF avoids repeated decoding. A different source replaces
that PDF. Four unused URLs and visible inputs form the remaining cache.

Full Chromium browser RSS at preview cycles 10/20/30 is
1,352.6/1,381.4/1,419.1 MiB.
After diagnostic garbage collection, browser RSS is 1,257.5 MiB
and retained heap is 47.2 MiB. The app never requests garbage collection.
Headless preview memory stabilizes around 950 MiB during rapid use.
Native viewer and allocator memory still fluctuate.

Reference budgets are 3 seconds to usable, 850 MiB steady headless browser RSS,
550 MiB renderer RSS and 75 MiB heap. Full Chromium budgets are 1.35 GiB steady
browser RSS and 800 MiB renderer RSS. The final measurements meet these budgets.

RSS sums count shared pages per process. Peaks use 100 ms samples. OS disk caches
are uncontrolled. These are runtime measurements, separate from artifact size.
One final run per configuration supplements earlier development probes.

## Validation

- **213 Python tests and 145 Node tests pass**, with no skips.
- **15 real offline browser checks pass** at the final HTML hash.
- Screenshots cover both themes, 1440/768/390 px widths and 200% root text.
- Native lecture page 675 visibly matches printed slide 7. Both saved PDFs match
  their original hashes and contain 1,953 and 59 pages.
- Required figures, exact code, formulas and the two-page print are readable.
- Shuffling, complete multi-select grading, bookmarks, resume, old progress and
  storage failures pass. Required image failures suppress answer feedback.
- No HTTP runtime request or page error occurs. Independent review binds the
  current implementation and includes 20,276 scoring comparisons.

The browser is Chromium 153. Physical phones, Firefox, Safari, screen readers
and actual browser zoom remain untested. Root-text enlargement is a separate test.

## Content qualifications

The current coverage digest is
`f2ee0c07ba462a8b2c7aa01471ae6290ccf5e931d50d010f1a6ca1c838afc6eb`.
Eleven nonverified concept records have recorded dispositions: two assignment
reuses, one quotation-only exclusion, seven aliases and one terminal-initialization
qualification. They are not eleven omitted topics. Twelve conflicting original
assignment keys and 26 source qualifications remain in the evidence record.

The historical all-course `--release` contract still returns 14 errors. It does
not recognize those qualified dispositions or the newer coverage binding. The full
bank retains `complete:false`. Ordinary integrity validation passes. This release
accepts the Practice application and its full verified bank. It creates no new
scientific or exhaustive-coverage approval.

## Restore and rebuild

Use a fresh checkout of the release source commit. Download the HTML and
`ai-for-robotics-build-inputs.tar.gz`. Check their hashes against the release
manifest. Extract the archive into the project directory. It restores the full
bank snapshot and three exact preview files. Then run:

```sh
python3 scripts/embedded_payloads.py /absolute/path/to/ai-for-robotics-mcq.html
python3 scripts/validate.py
python3 scripts/build.py
python3 -m unittest discover -s tests -p 'test_*.py'
for file in app/*.test.js tests/test_*.js; do node "$file" || exit 1; done
```

Node 22 is the measured development runtime. The application only needs a modern
browser with native gzip support. Recovery checks every original asset hash.
Practice HTML recovery writes its production snapshot under `dist/`. It cannot
replace the canonical review bank. No question generation or model execution is
needed. The original comparison HTML remains under `dist/baseline/`, outside Git.

A second build produces the same HTML SHA-256 in this environment:
`9461b5f1a5f2852657a015a2c596e3c88e8cd96d3c0c5e2010559b7f68f0bcba`. The file has 211,397,021 bytes.
Package receipts check every embedded asset and the actual ZIP round trip.
Release downloads receive a separate hash check.

Keep the same HTML path and browser to retain file-origin progress storage.
The storage key and original answer fingerprints remain compatible. Old histories
remain stored. New Practice saves keep one compact result per question fingerprint.
All 5,069 answered questions use about 2.29 million characters. A browser save and
reload verifies the full bank. Repeating an answer 100 times keeps one new result.
Removed dashboards and timers never initialize.

Git metadata is read-only in this managed workspace. Live GitHub main matched
local `535950d` before work. Publication uses a guarded fast-forward update and
preserves unrelated paths. No shared history is rewritten.
