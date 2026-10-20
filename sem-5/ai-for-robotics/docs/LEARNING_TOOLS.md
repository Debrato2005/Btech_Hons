# Learning-tool engine and evidence boundary

`app/learning-tools.js` is a dependency-free, pure JavaScript module. It exposes
`RoboticsLearningTools` in the browser and `module.exports` in Node. It has no
network requests, storage access, HTML injection, or global event handlers.

Run its checks with:

```sh
node --test tests/test_learning_tools.js
```

The original engine suite includes 2,000 generated numerical variants, save/replay checks,
100 random graph comparisons with an independent Floyd–Warshall calculation,
the lecture's BFS/UCS/A* worked example, repeated-state reopening, terminal
Q-learning updates, input validation, and mastery/revision boundary conditions.
These executable checks verify software behavior. They do **not** replace
independent inspection of course evidence or certify comprehensive coverage.

## Data and review boundary

- The canonical course envelope is in `docs/DATA_CONTRACT.md`.
- `bank.learningTools.formulaSheet`, `confusionPairs`, and `traps` contain explicit
  authored records, not facts inferred from generic JavaScript algorithms.
- `buildLearningViews(bank)` now requires a current independent extractor-policy
  approval and a separate exact-hash tool approval, current source references
  and linked question approvals. A `verified` label alone does not activate it.
  `includeDrafts:true` is for the explicitly labeled audit area.
- A synthetic record is never included in a course view, even with drafts enabled.
- The main bank validator remains responsible for version-bound review records,
  source hashes, reciprocal concept links, and reference integrity. A learning
  view's status filter is not a replacement for that validator.
- `listNumericalFamilies()` excludes built-in synthetic fixtures by default.
  `listNumericalFamilies({includeSynthetic:true})` exposes them for an explicitly
  labeled demonstration/testing area only.
- The two synthetic numerical families are **not verified course questions**.
  Their formulas must not be counted as course coverage simply because similar
  formulas occur in lectures.

## Numerical API

```js
const families = RoboticsLearningTools.listNumericalFamilies({includeSynthetic:true});
const variant = RoboticsLearningTools.generateVariant(families[0].id, {
  seed: 'attempt-2026-001',
  shuffleOptions: true
});
const replay = RoboticsLearningTools.restoreVariant(JSON.parse(JSON.stringify(variant)));
```

Every variant retains `familyId`, `generatorVersion`, `engineVersion`, original
`seed`, normalized seed, sampled `parameters`, exact option IDs and order,
precision, units, formula, assumptions, worked steps, and option justifications.
Answers are option IDs, never letters or positions. Store the **entire returned
variant** in the attempt backup. Restoration recomputes the answer and explanation
from the saved parameters, checks the identity/version, and reuses the exact saved
option order. It does not trust a saved correct-answer field.

When converting a runtime variant to the canonical question `variant` field,
use a string seed and an object of unit definitions, as required by the data
contract. The runtime uses `units` as a single answer-unit label; this is distinct
from the canonical variant's per-variable `units` object.

### Registering a course family

`registerNumericalFamily(definition)` requires:

- Stable `id` and `version`.
- `sample(rng)`, `validate(parameters)`, and `solve(parameters)` functions.
- Exact `sourceRefs` unless the family is explicitly `synthetic:true`.
- Optional title, description, status, review record, and documented
  `parameterDomains`.

`solve` returns `question`, numeric `answer`, four or more options
`{id,value,justification}`, `precision`, `units`, `formula`, variable definitions,
assumptions, worked steps, and explanation. No executable code is loaded from
JSON. Course-specific generators are implemented and reviewed as versioned code.

Validation rejects invalid domains, nonfinite results, repeated option IDs,
duplicate displayed labels, mismatched units, values equivalent after final
rounding, and missing or ambiguous correct options. Random generation retries
only option-collision cases, up to an explicit bound; invalid user-supplied
parameters fail immediately rather than silently changing the question.

Round only the final answer. The implemented convention is decimal half away
from zero using a small floating-point representation correction. Values too
large for the declared decimal precision are rejected. JavaScript floating-point
arithmetic is not arbitrary-precision symbolic mathematics; exact rational or
high-dynamic-range families need a separately reviewed numerical representation.

Built-in testing families:

1. `synthetic.bayes-two-hypotheses`: normalized two-hypothesis Bayesian update.
2. `synthetic.q-learning-update`: one sequential TD update, terminal or nonterminal.

## Graph-search API

```js
const trace = RoboticsLearningTools.searchTrace({
  directed: false,
  nodes: ['A', 'B', 'G'],
  edges: [{from:'A',to:'B',cost:2},{from:'B',to:'G',cost:3}]
}, {
  algorithm: 'astar', start: 'A', goal: 'G',
  heuristic: {A:4,B:2,G:0},
  neighborOrder: 'lexicographic', tieBreak: 'lexicographic'
});
```

`algorithm`: `bfs`, `dfs`, `ucs`, or `astar` (also accepts `a*`). Direction must be
explicit. Edges require valid endpoints and nonnegative costs; omitted costs are
one. Parallel edges are rejected rather than silently overwritten. A* requires
an explicit nonnegative heuristic for every node, without falsely certifying
its admissibility.

Each trace contains:

- Status `found`, `exhausted`, or `truncated`, path, actual edge cost, hop count,
  expansion count, and all conventions.
- Initial, expansion, goal, and terminal snapshots.
- Current node/path, ordered frontier, closed/discovered sets, best-known costs,
  and each discovery, ignored successor, decrease-key, or reopening.

### Conventions that affect answers

1. Goal tests happen when a state is removed from the frontier, before expanding
   successors. Goal removal is **not counted as an expansion**.
2. BFS uses FIFO and minimizes hops, not arbitrary weighted cost. DFS uses LIFO;
   neighbors are pushed in reverse order so the first ordered successor is
   visited first. Both mark discovered on insertion.
3. UCS prioritizes `g`; A* prioritizes `g+h`. Strictly cheaper paths replace queued
   entries and reopen closed nodes. Equal-cost alternatives do not replace paths.
4. Successors are lexicographic by default; input order can be selected explicitly.
   Weighted ties use insertion order by default; `lexicographic` can be selected.
5. Priorities and strict improvements use exact stored IEEE-754 numbers. No hidden
   rounding or approximate tie tolerance is applied.
6. A* optimality requires admissible `h` and `h(goal)=0`; reopening accommodates an
   inconsistent admissible heuristic. The engine does not assert these properties
   for arbitrary user-supplied heuristics.
7. `maxSteps` bounds expansions and returns `truncated`, never a false no-path
   result. The default is 10,000; valid explicit limits are 1–100,000.

### Course regression: lecture 36

Source: `AI_for_Robotics_All_Lectures.pdf`, SHA-256
`2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c`.
Physical PDF pages 1105–1123; original printed pages 18–36.

Undirected edge costs: AB=5, AC=2, BD=6, BE=3, CF=4, DE=2, DG=6, EF=1, FG=3.
Heuristics: A=7, B=6, C=5, D=4, E=3, F=2, G=0. Start A, goal G.

- BFS: A → B → D → G; 3 hops; cost 17; expansions A,B,C,D,E,F.
- UCS: A → C → F → G; cost 9; expansions A,C,B,F,E,D.
- A*: A → C → F → G; cost 9; expansions A,C,F.

Use lexicographic weighted ties to reproduce the lecture's p1116 order D(9)
before G(9). The slides show this ordering but do not state a universal
alphabetical tie rule; that rule is an explicit implementation convention chosen
to reproduce the displayed trace. Input-order ties can yield the same optimal
cost with a different number/order of expansions.

Visual inspection performed for p1105 (printed 18), p1116 (printed 29), and p1121
(printed 34), using existing 1800-pixel page renders. The numerical trace checks
use the text and these graph/heuristic renderings. Independent course-record
review remains a separate step. No claim is made that the whole page range or
lecture is visually inspected by these limited regression checks.

## Q-learning API

```js
const trace = RoboticsLearningTools.qLearningTrace({
  alpha: 0.5, gamma: 0.9,
  initialQ: {S:{a:2},T:{left:4,right:7}},
  transitions: [
    {state:'S',action:'a',reward:3,nextState:'T',terminal:false,nextActions:['left','right']}
  ]
});
```

`alpha` and `gamma` must lie in [0,1]. Transition order is explicit and sequential.
All bootstrap values come from the table **before** the current write, including
self-transitions. `terminal` is mandatory; terminal target equals reward alone.
Nonterminal transitions require a nonempty legal action list, either explicit
`nextActions` or the initially supplied keys for that next-state row. Missing
action estimates use the declared `initialValue`, default zero. No exploration
policy is guessed and no claim of convergence follows from a short demonstration.

Snapshots retain pre-update value, legal next-action values, maximum bootstrap,
target, TD error, new value, equation, and full Q-table.

The formula is visually supported by physical lecture p904 (printed 18), and the
sequential pseudocode/epsilon-greedy description by p905 (printed 19). Those
slides use η for learning rate; the API's `alpha` is the same parameter. The
terminal-zero bootstrap is an explicit demonstration assumption, not a claim
that p905 spells out the terminal convention. Arbitrary initialization on p905
does not itself set a terminal row to zero.

## Stepper and integration

`createStepper(trace)` provides `current()`, `next()`, `previous()`, `seek(index)`,
`reset()`, and read-only `index`/`length`. Returned states are copies, so a UI cannot
corrupt later snapshots. Buttons should be keyboard-operable, have visible focus,
and announce the current step in a polite live region. Render the stated
conventions alongside the visualization. Do not color-code without text labels.

## Mastery and mistake revision

`masteryByConcept(questions,attempts)` expects attempt records containing
`questionId`, boolean `correct`, and optional numeric/ISO `timestamp`. Only verified
questions count. Use `cognitiveSkill` or explicit `masteryDimension` to separate
factual, conceptual, application, and numerical evidence. Each distinct question
or numerical family contributes only its latest result, so 100 repetitions of one
question still provide one unit of evidence. Display the transparent heuristic
`(correct + 1) / (distinct evidence + 2)` and evidence count, not a claim of proven
mastery. Fewer than three distinct units is labeled limited evidence.

`mistakeRevision(bank,attempts,{bookmarks,reviewFlags})` recommends verified items
from recent mistakes, bookmarks, review flags, prerequisite links, and unattempted
questions on missed concepts. Input attempts must be in chronological order.
Prerequisite traversal is cycle-safe. This is a revision aid, not a prerequisite
knowledge diagnosis.

## Remaining work at this checkpoint

- Populate and independently review source-linked formula sheets, confusion
  pairs, trap records, algorithm fixtures, and course numerical families.
- Complete app rendering/storage integration and browser-based offline tests.
- Extend course algorithms only where supported by inspected course evidence.
- Re-review numerical generator versions after any correctness-affecting change.

## Source-linked draft records and runtime binding

The first authored course-learning bundle is `data/learning-tools-draft.json`:
four formula records, six confusion pairs, seven trap records, five algorithm
visualizations, and two source-derived numerical family mappings. All remain
draft pending independent review. `audits/blind-learning-tools.json` is the
answer-hidden review worksheet. The family/algorithm data is not an independent
review of the implementation.

`registerBankNumericalFamilies(bank,{includeDrafts:false})` binds canonical
`learningTools.numericalFamilies` records to allowlisted implementations without
executing JSON-supplied code. A record uses `{id,title,status,generatorKind,
generatorVersion,sourceRefs}`. Supported kinds are `q-learning-update` and
`bayes-two-hypotheses`; runtime family IDs equal record IDs. Draft registration
requires the explicit audit option `includeDrafts:true`. The result contains
`registered` IDs and rejection `diagnostics`.

Algorithm data uses `{id,title,status,graph,config,sourceRefs}` or
`{id,title,status,qLearningConfig,sourceRefs}`. Keep the record's draft/review
label visible separately from the generated trace. When calling a trace with
course data, pass a provenance object derived from that record instead of
retaining the generic synthetic-example default.

## Search-source authoring slice

`data/question-batches/search-foundations.json` contains 68 authored questions
across 20 linked concepts for physical lecture pages 1105–1137: 67 drafts and one
flagged source-conflict item. `audits/blind-search-foundations.json` omits author
answers and explanations for independent solving. All question/concept schema
checks pass; no independent verification is claimed.

All 33 pages in this slice were visually inspected. The observation ledger
`audits/learning-tools-page-observations.jsonl` preserves exact source hashes,
printed numbers, findings, links, four specific administrative exclusions, and
the unresolved p1135 start-cost conflict. It also includes seven separately
inspected pages used for the earlier learning records, for 40 distinct pages.

`audits/search-grid-arithmetic.json` independently recomputes all 19 free-cell
g-values with Python Dijkstra and all 19 h-values with the octile formula. They
agree with the p1133/p1134 tables under cardinal cost 1, diagonal cost 1.4 and
strict no-corner-cutting. This corroborates arithmetic, not independent answer
review. `audits/search-source-disputes.json` retains p1135's contradictory start
g=1.0 versus p1133's g=0.0; it is not silently corrected in the source.


## Exact question projections and additional course tools

See `docs/LEARNING_RESOURCE_REVIEW_HANDOFF.md` for the frozen review packet,
separate approval schema, code hashes and permission/runtime boundary.
`app/learning-resources.js` projects full formula objects, discriminating-question
comparisons and trap/misconception examples directly from current independently
approved questions. `app/learning-resource-ui.js` preserves each exact question
context and qualification, uses text-only DOM writes and paginates records and
source contexts. These projections are disabled until the extractor policy has
a separate independent exact-hash approval.

The 18 added draft records in `data/learning-tools-course.json` comprise five
algorithm configurations and 13 numerical families. Eleven additional static,
allowlisted numerical implementations are in `app/course-numerical.js`; no
executable code is loaded from data. They add 11,000 seeded author oracle checks
to the original two families' 2,000. These are not independent approval or
exhaustive mathematical coverage. Every new tool separately requires current
source/approved-question bindings, implementation hashes and independent review.
The original 24 draft records are not deleted or silently relabeled verified.

Browser component QA was attempted but blocked before any page opened by a local
socket permission error. No browser screenshots or interaction passes are claimed.
Default Python/Node tests and HTML build checks do not stand in for browser QA.
The restriction and stopped outcome are recorded in the review handoff.
