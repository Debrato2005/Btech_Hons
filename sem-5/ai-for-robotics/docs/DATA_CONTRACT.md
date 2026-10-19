# AI for Robotics data contract v1

`data/bank.json` is the canonical bank consumed by the builder. UTF-8 JSON, schema version `1.0.0`. IDs are stable, opaque strings and unique within their entity collection; option IDs are unique within their question (persist question ID plus option ID); option IDs, never letters or positions, define answers. All physical PDF page numbers are **one-based**. Unknown metadata is `null`, never inferred from a page index.

## Bank envelope

Required keys: `schemaVersion`, `bankVersion` (nonempty release identifier), `title`, `complete` (boolean), `sources`, `slides`, `concepts`, `questions`, `reviews`, `assets`, `learningTools`.

`learningTools` has arrays `formulaSheet`, `confusionPairs`, `traps`, `algorithmVisualizations`, `numericalFamilies`. Their source-linked specialist records may add fields; any `questionIds`, `conceptIds`, `slideIds`, or `assetIds` are validated when present. A record must have a stable `id`. No synthetic fixture is part of the course bank.

Partial checkpoints are valid. Empty arrays and unavailable sources must remain honestly labeled, with `complete:false`. A valid partial bank is not a coverage or correctness claim. `--release` adds completion and offline-evidence gates. Optional `notes` may explain gaps.

## Source

Required: `id`, `filename`, `role` (`lectures`, `assignment_solutions`, `other`), `url`, `providerFileId`, `retrievalStatus` (`pending`, `ready`, `unavailable`), `sha256` (64 lowercase hex or null), `pageCount` (positive integer or null), `version` (string or null), `localPath` (project-relative path or null), `assetId` (asset ID or null).

A ready source requires a measured page count, non-null SHA-256 and existing local PDF path. Preserve its provider ID separately from the stable project ID. A changed file hash requires new inspections/reviews even if the filename stays unchanged. Keep lecture and assignment PDF pagination separate.

## Asset

Required: `id`, `kind` (`source_pdf`, `source_page`, `diagram`, `font`, `other`), `path` (project-relative file), `mimeType`, `sha256`, `alt` (description). Optional `sourceId`, `physicalPage`, `width`, `height`. Never use a remote URL as an offline asset path. `source_page` is an exact rendering, not a redraw; label generated diagrams separately. The builder embeds assets from these paths. A source's `assetId` points to its complete PDF; a slide's optional `assetId` points to a readable page preview. A citation can use either, but final offline evidence must actually be embedded.

## Slide / source-page ledger

Every page of each ready PDF has exactly one record, including title, blank, repeated, reference, and excluded pages.

Required: `id`, `sourceId`, `sourceSha256`, `physicalPage`, `combinedLecturePage` (same physical page for the combined lecture PDF, otherwise null), `week` (integer or null), `lectureId` (string or null), `lectureTitle` (string or null), `lectureRelativePage` (positive integer or null), `printedSlideNumber` (string or null), `printedSlideNumberStatus` (`present`, `absent`, `unreadable`, `unchecked`), `title`, `text`, `disposition` (`unreviewed`, `examinable`, `repeated`, `excluded`, `unresolved`), `exclusionReason` (string or null), `repeatsSlideIds` (array), `incrementalChangesChecked` (boolean), `conceptIds` (array), `assetId` (asset ID or null), `visualInspection`.

`visualInspection`: `{status:'pending'|'complete'|'uncertain', inspectorId:null|string, inspectedAt:null|ISO-8601 timestamp, method:null|'rendered_page'|'pdf_viewer', notes:string}`. Text extraction never establishes visual inspection. A complete inspection requires an identified inspector, timestamp, method, and a ready source. An excluded slide needs a specific reason. A repeated slide needs earlier slide links and an explicit incremental-change check. Unresolved or uncertain content cannot count as complete.

## Concept

Required: `id`, `title`, `description`, `slideIds` (one or more), `questionIds` (possibly empty), `status` (`identified`, `drafted`, `verified`, `flagged`), `topic`, `subtopic`, `prerequisiteConceptIds` (array). Optional `coverageNotes`, `examinationAngles` (array of distinct tested/missing angles). A verified concept needs at least one currently verified question, but that alone does not establish exhaustive meaningful-angle coverage. Reciprocal slide/concept and concept/question links are required.

## Question

Required:

- `id`, `version` (positive integer), `status` (`draft`, `verified`, `flagged`, `rejected`), `authorId`.
- `stem`, `selectionMode` (`single` or `multi`), `type` (e.g. `conceptual`, `numerical`, `algorithm_trace`, `statement`, `assertion_reason`, `match`, `sequence`, `diagram`, `definition`, `scenario`, `exception`, `synthesis`), `difficulty` (`easy`, `medium`, `hard`, `extremely_tricky`), `cognitiveSkill` (`recall`, `conceptual`, `application`, `numerical`, `algorithm`, `synthesis`).
- `week` (integer or null), `lectureId` (string or null), `topic`, `subtopic`, `tags` (array), `conceptIds` (nonempty array), `assumptions` (array).
- `options:[{id,text}]`, `correctOptionIds:[...]`. At least two options, unique texts and IDs. Single-select has exactly one correct option; multi-select has at least one. Fewer than four options requires nonempty optional `optionCountRationale`.
- `citations:[...]` (nonempty), `solution`, `origin` (`generated`, `assignment_adapted`, `assignment_verbatim`), `reviewIds` (array).
- Optional `assetIds`, `relatedQuestionIds`, `variant` (see below), `duplicateGroupId`, `notes`, and `revisionAuthors` (a unique array of nonblank contributor IDs). Record every contributor who changes correctness-sensitive question content in `revisionAuthors`; retain the original `authorId`.

Do not use option-relative wording such as “all of the above” if options can shuffle. Avoid answers containing a displayed letter instead of an option ID.

### Citation

`{slideId,sourceId,sourceSha256,physicalPage,kind,locator,evidenceText,role,region}`.

`kind`: `statement`, `equation`, `table`, `figure`, `code`, `derivation`, `other`. `role`: `explicit`, `premise`, `conflict`. `locator` precisely identifies the region, statement, equation, table row/cell, or figure. `evidenceText` is the relevant source content (not invented explanation). `region` is null or normalized `{x,y,width,height}` within the page, values 0–1. Citation page/hash must match the slide and source. Week/lecture/original printed numbering resolve losslessly through `slideId`; exporters should materialize those fields from that record. A derivation cites all needed premises. An unresolved conflict cannot be silently accepted.

### Solution

Required: `justification` (nonempty), `optionExplanations` (object keyed by every option ID, including correct options), `steps` (string array), `formulas` (array of `{expression,variables,units,assumptions}` with objects for variable meanings/units and string-array assumptions), `simpleExplanation` (nonempty), `memoryAid` (string or null), `misconceptions` (string array), `examTraps` (string array), `prerequisiteConceptIds` (array).

A numerical/algorithm question requires step-by-step workings; “not applicable” is represented by an empty array or null rather than invented formulas/mnemonics. Explain every option in the question's stated context. Distinguish slide claims from derivation and generated intuition in the explanation.

### Numerical variant provenance

If present, `variant` contains `familyId`, `generatorVersion`, `seed` (string), `parameters` (object), `rounding` (string), `units` (object). Persist the instantiated option IDs and exact variant in attempts. The family validator must check domains, arithmetic, duplicate/equivalent rounded options, and reproducibility. Pure numerical reparameterizations do not inflate unique concept coverage.

## Review and verification binding

Required review fields: `id`, `questionId`, `questionVersion`, `questionSha256`, `reviewerId`, `decision` (`verified`, `flagged`, `rejected`), `reviewedAt`, `sourceVersions` (object: source ID → SHA-256), `reviewedSlideIds`, `independentAnswerOptionIds`, `solvedBeforeAnswerSeen` (boolean), `checks`, `reasoning`, `findings` (string array).

`checks` requires boolean keys: `sourceSupport`, `assumptions`, `answerSet`, `distractors`, `calculations`, `figureFidelity`, `explanation`, `difficulty`, `duplication`. Nonapplicable checks may be true only when the review reasoning says why. A verified question requires at least one verified review by someone other than `authorId` and every ID in `revisionAuthors`, with all checks true, exact matching answer set, all cited slides reviewed, and all cited source hashes bound. A structurally valid record does not prove the reviewer really inspected evidence; preserve real review work.

`scripts/validate.py question-hash <question.json>` computes the binding: SHA-256 of canonical UTF-8 JSON of the entire question, excluding only `status` and `reviewIds`, using sorted object keys, separators `(',',':')`, `ensure_ascii=False`, and no NaN/Infinity. Whitespace within strings is significant. The question's `version` is part of the hash. Changes to stem, options, answers, solution, assumptions, citations, assets, variant, or classification invalidate an old review; increment `version` and re-review. Pure status/review-link changes do not. Source changes also invalidate reviews. A current flagged/rejected review blocks verified acceptance even if omitted from `reviewIds`. Preserve the dispute and adjudication notes; correct or clarify the question, increment its version, and obtain a new independent review. Historic reviews remain in the audit log.

## Workflow and commands

1. Retrieve and hash sources; map every actual page without guessing boundaries.
2. Visually inspect each page, record concepts/exclusions/repetitions and exact provenance.
3. Author source-supported questions as drafts; add reciprocal concept links.
4. Give the independent reviewer source material and question/options without proposed answer where feasible. Persist their reasoning and answer before reconciling.
5. Resolve disagreements, increment changed question versions, obtain current review records, then set verified and review links.
6. Run `python scripts/validate.py` and `python -m unittest discover -s tests -p 'test_integrity.py'` before integration. `python scripts/validate.py --release` requires complete coverage and assets; it is not a substitute for the independent coverage challenge or browser tests.
7. Builder ordinary practice/exam/revision pools must include only `status:'verified'` with valid review bindings. Drafts/flags/rejections belong in an explicitly labeled audit view. Never use synthetic fixtures to fill an empty course pool.

`tests/fixtures/synthetic_bank.json` is intentionally synthetic validator data, clearly labeled, and must never be bundled as course content. The validator rejects `synthetic:true` in course input unless `--allow-synthetic` is explicitly used for tests.

## Intentional extensibility

Schemas allow additional descriptive fields for specialist tools and future evidence. Existing required fields and semantics may not be renamed. Semantic validation checks identity, referential integrity, complete source page ledgers, review freshness, local asset existence/hash, full option explanations, and suspicious duplicates. Reports clearly separate errors from warnings and raw counts from verified coverage. The schema does not replace source review, legibility inspection, meaningful-angle coverage challenge, or runtime offline testing.
