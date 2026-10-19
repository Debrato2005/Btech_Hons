# Independent source, answer, and release review protocol

Status: active protocol, not a claim that reviews have been performed.

## Authority and review separation

The supplied lecture PDF is the primary course authority. Assignment solutions are independently checked, not presumed correct. Public sources may support implementation but cannot silently replace the course's conventions. Each accepted question requires both machine integrity checks and independent source-based review. Neither implies the other.

Authors may draft questions, alternatives, explanations and proposed answers. A distinct reviewer solves a blinded packet before opening the proposed answer. The reviewer must not approve their own question. Generation and review by the same worker do not count as independent review.

## Reproducible blind-answer workflow

1. Freeze the authored question and its citations, assumptions, figure/generator versions, and source checksums. Record its correctness-sensitive hash. Whitespace-only cosmetic changes can be tracked separately.
2. Make a blinded packet containing the question ID, complete stem, options with stable IDs, declared selection mode, explicit assumptions, citations, and required source evidence. Do not include the correct-answer IDs, solution, rationale, distractor explanations, hints, or answer-revealing metadata. For new assignment-derived questions, avoid reading the supplied answer until the independent solution has been recorded. If an answer is already visible on the source page, record this exposure and use a second independent derivation rather than calling it a blind review.
3. The reviewer opens the actual cited source pages, visually inspects relevant material at readable scale, and records the source/page/hash plus observed equation, diagram relationship, or statement. Text extraction or a successful render alone does not satisfy visual review.
4. Before answer reveal, persist the reviewer-selected option-ID set, derivation/reasoning, assumptions, source observations, uncertain points, and UTC timestamp. Hash this record. A saved timestamp establishes ordering, not truth; the reasoning remains reviewable.
5. Reveal the author answer and every explanation. Compare option-ID sets, check all distractors, and independently reproduce calculations and algorithm traces. Numerical variants require executable checks across valid and invalid domains, boundary cases, rounding collisions and seed reproducibility.
6. Record agreement or disagreement, disposition, reviewer identity, source versions, question hash, blind-record hash, tests run, and corrections. Agreement alone is insufficient: source support, exact answer cardinality, assumptions, every-option rationale, figure fidelity, and meaningful distinctness must all pass.
7. Disagreements remain `flagged` until adjudicated against all relevant source pages. Preserve the original disagreement and resolution. Reject an irreparably unsupported or duplicative item; do not delete the audit history.
8. Any correctness-sensitive edit, source replacement, changed citation, generator change, answer-relevant figure change, or changed algorithm convention invalidates verification and returns the affected question to draft/pending review.

Statuses are `draft`, `verified`, `flagged`, and `rejected`. A reviewer must not set `verified` with unresolved conditions. Practice, exam, ordinary revision, and mastery recommendations default to verified items only; other items belong in a conspicuously labeled audit area.

## Every-page visual evidence and concept accounting

A complete page record identifies source ID, exact source SHA-256/version, physical one-based PDF page, actual printed slide number or explicit absent/unreadable status, week/lecture mapping with confidence, and lecture-relative page when established. Combined-lecture page and assignment page numbers must never be conflated.

To mark a page visually inspected, record:

- Reviewer, timestamp, rendered image/crop reference and rendering scale or dimensions.
- Evidence the reviewer actually looked at the page: compact observations covering its title, formulas, table/figure relationships, fine print and incremental changes where applicable.
- All distinct examinable concepts and examination angles, not just one question per page.
- Unreadable/uncertain regions and a resolution or explicit open blocker.
- An accountable disposition: examinable, repeated with incremental-difference check and canonical references, title/administrative, references, or another specific exclusion reason.

A contact sheet may locate content but does not establish readability of small equations, diagram labels, or table cells. Enlarge pages/crops when needed. Do not count `rendered`, `extracted`, `OCR-complete`, or an automatically produced page ledger as `visually inspected`.

Keep independent counters for inventoried pages, rendered pages, visually inspected pages, identified unique concepts, concepts with drafts, concepts with verified coverage, partially covered concepts, uncertain pages and justified exclusions. Zero and unknown are different: use unknown/null until measured. Numerical variants do not increase unique-concept counts. Repeated pages remain in the ledger with all source references preserved.

## Independent coverage challenge

A coverage reviewer should inspect each allegedly complete section without relying solely on the author's concept list. Challenge:

- Definitions, notational distinctions, domain assumptions, units and dimension checks.
- Every equation term, derivation step, sign, boundary/limiting case and exception.
- Every table row/column, axis, legend, directed relationship, label, annotation and footnote.
- Code/pseudocode execution, initial state, stopping rules, neighbor order, ties and repeated-state behavior.
- Similar concepts, discriminating conditions, common wrong inferences, application and failure cases.
- Repeated slides with incremental additions, references and administrative exclusions.
- Assignment-specific styles, methods and conventions; conflicts between assignments and lectures.
- Cross-lecture premises that support synthesis questions and necessary prerequisite links.
- Question duplication, superficial numeric/paraphrase inflation and unsupported difficulty claims.

A section can be closed only when all pages have accountable dispositions, each identified examinable concept has appropriate verified questions, the independent challenge records no unresolved meaningful omissions, and evidence is tied to the exact versions reviewed. A sample audit is valuable but cannot certify the full corpus.

## Numerical and algorithm review checklist

State and independently check units, reference frames, radians/degrees, matrix/vector orientation, normalization, probability conditioning, priors, index conventions, precision and final rounding. Inspect zero/negative/domain boundaries. Check whether a formula's stated assumptions apply. For numerical options, detect equality after display rounding and duplicate options; validate that the declared answer set remains unique.

For search, record directed/undirected edges, edge costs, start/goal, frontier discipline, neighbor ordering, tie breaking, visited-state timing, replacement/reopening behavior and stopping condition. For Q-learning and related updates, record learning rate, discount, terminal conventions, old/new update timing and tie rules. Generators, animations and questions must use matching conventions.

## Offline application and release gates

Test the actual release HTML opened with a `file://` URL in a browser with networking disabled, not only a development server. Test the exact bytes downloaded from the durable release destination again before claiming delivery verification.

Mandatory behavior: single/multi-select scoring, correctness under option shuffles, navigation, keyboard interactions without typing interference, search/filters, bookmark/review states, reset, both themes, mobile layout, readable mathematical overflow, source evidence zoom, all learning tools, progress persistence, storage failure warnings, validated backup/import merging, escaped CSV/JSON exports, stable answer keys, and print questions/key/solutions.

Exam tests cover stated scoring before start, verified-only scope, randomized exact ordering, delayed solutions, preserved choices/review flags/order on reload, elapsed wall-clock deadlines across background/reload, explicit submission, expiration, completed attempts, and resumption without accidental restart.

Record machine/browser versions, source/bank/artifact hashes, exact commands, fixture/full-corpus scope, file and gzip sizes, load/DOM ready/first interaction times, JS heap where available, console/page errors, network requests and screenshot evidence. Empty/synthetic banks must be labeled and never used to claim complete-bank performance. No browser metric substitutes for a readable visual inspection.

Final completion requires the reconciled full source inventory, every-page visual accountability, complete verified concept coverage, independent coverage challenge, all product gates, exact offline downloaded artifact validation, and a verified GitHub checkpoint. If a gate is pending, failed, or blocked, report that exact state and the remaining work rather than calling the project complete.
