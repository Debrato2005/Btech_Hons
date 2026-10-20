# Current scope: Practice only

The user changed the delivery scope on 20 October 2026. This document overrides
multi-mode product requirements in EXECUTION_BRIEF.md. Historical content and
review requirements remain in force.

The shipped HTML contains one Practice interface and all 5,069 verified questions.
It retains complete solutions, per-option reasoning, workings, formulas, source
citations, required figures and exact code/output snippets. Two flagged duplicate
adaptations remain excluded. Question records and answer IDs are unchanged.

Practice includes course navigation, search, filters, single/multiple selection,
submission, immediate single-answer feedback, reset, skip, previous/next, a palette,
bookmarks, review marks, keyboard controls, themes and automatic resume.

The production build omits exams, revision, standalone learning tools, coverage,
progress-management and audit dashboards. It also omits their JavaScript modules,
review ledgers, whole notebook archives, tool policies, timers and initialization.
The repository keeps those records and integrity tools for development and review.

`app/practice.html`, `practice.js`, `practice-core.js`, `practice.css` and
`payloads.js` form the production interface. The builder validates the full bank
before projecting verified questions and their required inputs. It compresses the
projection losslessly. Each asset has a separate inert payload and decodes only
when needed. Closed source previews remove their PDF viewer. One source PDF Blob can stay
cached to avoid repeated decoding. Opening a different PDF releases the previous
source Blob. Unused URLs share a bounded cache. Visible images remain available.

The storage key remains `ai-for-robotics-progress-v1`. Existing selections,
bookmarks, question fingerprints and historical records remain compatible.
New Practice state stores the last question and filters. Keep the HTML at the
same path in the same browser to retain file-origin storage. A renamed file or
a different browser can use a different storage area. No backup-management UI
is part of this scope.

Mathematics remains selectable Unicode course notation, with embedded figures
for required visual inputs. Literal LaTeX code in a notebook question stays
literal code. No remote font, math service or script is required.

Use `tests/browser_practice.js --execute HTML REPORT.json` for current browser
acceptance. Historical exam/tool browser runners test the former scope and do not
establish acceptance of this build. Use `tests/browser_profile.js HTML REPORT.json`
for matched baseline comparisons. Both runners require installed Playwright and
Chromium. The application itself needs neither dependency.

The old all-course `--release` contract still rejects the historical
`complete:false` flag and eleven qualified concept dispositions. The current
coverage digest accounts for those dispositions through reviewed reuse, aliases,
a quotation-only exclusion and a terminal-initialization qualification. Preserve
them. A working Practice release is not a new scientific or exhaustive-coverage
approval. Read PRACTICE_RELEASE.md for current measurements and qualifications.
