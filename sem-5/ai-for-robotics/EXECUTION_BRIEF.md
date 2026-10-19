# Build a comprehensive, source-verified AI for Robotics MCQ bank and offline study app

Act as the lead coordinator of a multi-agent team of subject specialists, assessment authors, independent reviewers, and software engineers.

Your task is to **build the complete study resource described below**, including the question bank, detailed explanations, source coverage records, learning tools, and final working HTML application. Carry the work through implementation, verification, and delivery.

Use your judgment throughout. These are outcome requirements; you may choose the architecture, internal file structure, libraries, agent assignments, and implementation sequence. Improve the approach where useful without reducing the requested coverage or correctness.

## 1. Sources, destination, and final outcome

**Source folder:**

[Google Drive — Semester 5 resources](https://drive.google.com/drive/folders/1kJJLyX3HjmCX652v4jy_RyM7gS04mpx_?usp=sharing)

The folder was found to contain these resources; verify the current inventory before starting:

- [AI_for_Robotics_All_Lectures.pdf](https://drive.google.com/file/d/11o0RzXIrDTIbb0FNe1Tl_-cgV4aKVl2m/view)
- [AI_for_Robotics_All_Assignment_Solutions.pdf](https://drive.google.com/file/d/16Ybyme8t18KxPRKQYAinJYsidLQyxoDQ/view)

**Persistence repository:**

[Debrato2005/Btech_Hons](https://github.com/Debrato2005/Btech_Hons)

Create an appropriate Semester 5 / AI for Robotics project folder, preferably `sem-5/ai-for-robotics/`, adapting to any existing repository conventions.

**Expected course scope:** 1,953 PDF pages organized into 12 weeks. Verify the actual page counts and lecture boundaries rather than treating these figures as already confirmed. Establish whether the stated count refers to the lecture PDF or the complete corpus, and report discrepancies without silently changing the coverage target.

**Final deliverable:** one downloadable, self-contained HTML file, preferably named `ai-for-robotics-mcq.html`, containing the complete question bank and study application. It must work offline when opened directly, with light/dark themes, selectable answers, detailed solutions, embedded source evidence, and portable progress backups.

Maintain structured question data, source mappings, build tooling, audit records, and recovery instructions in the repository so the HTML can be rebuilt and improved.

The central standard is:

**Every examinable part of the supplied course material should have appropriate question coverage, and every accepted answer must be defensible from the cited course material and explicitly stated assumptions.**

## 2. Work autonomously with maximum available agent capacity

Use the **maximum available number of agents that can perform useful independent work**, at the **highest reasoning level the environment actually allows you to select**.

Discover the real concurrency and configuration limits. Use supported capabilities fully, without claiming to have enabled unavailable models, reasoning settings, agents, or background execution.

Keep available workers productively assigned across source analysis, question generation, independent solving, numerical verification, interface development, and coverage review. Reassign agents as tasks finish. Agents may delegate further within the actual platform limits.

Useful responsibilities include:

- Source inventory, PDF extraction, visual slide inspection, and pagination mapping.
- Week- and lecture-specific question generation.
- Independent answer verification and ambiguity review.
- Numerical, formula, code-output, and algorithm validation.
- Cross-week synthesis, confusion pairs, and examination traps.
- Application design, accessibility, offline packaging, and performance.
- Coverage reconciliation, integration, and GitHub persistence.

These are responsibilities, not a fixed team structure. Combine or split them as useful.

Keep one coordinating integrator responsible for shared data contracts, stable identifiers, assignments, consistency, and durable checkpoints. Give workers distinct page ranges, question batches, files, or isolated worktrees so they do not overwrite each other.

Use relevant available skills and tools for PDFs, OCR, mathematics, programming, design, and testing. Install ordinary missing dependencies in an isolated environment when permitted.

Proceed without repeatedly asking me to approve routine decisions. If a blocker arises, diagnose it, use independent review where helpful, try permitted alternatives, and continue unaffected work. Ask only when essential access, information, or authorization is genuinely missing.

Continue beyond planning, extraction, a sample bank, the first week, or an attractive interface. Those are intermediate milestones.

## 3. Make GitHub the durable project record

I authorize you to create the project folder and required files in the specified repository and to commit and push this task’s work through the permitted repository workflow.

Inspect the repository’s current state and relevant instructions first. If it is empty, initialize the project. Preserve unrelated work and reconcile concurrent changes.

**Temporary cloud files and local commits alone are insufficient persistence.**

Commit each coherent, validated slice of work. A slice should include the relevant question data, explanations, source mappings, coverage updates, and review results, so its state is understandable and recoverable.

Batch pushes into meaningful checkpoints instead of pushing every small edit. Keep the amount of unpushed work bounded, push periodically during sustained work, and push before planned stops or context handoffs. After a push, verify that the expected commit is present on the remote branch.

Use one integration owner for shared Git operations where necessary. Do not let parallel agents race to rewrite shared state or publish incompatible versions.

Maintain enough project state for a fresh session to resume without the previous conversation. This should include:

- Source inventory, stable identifiers, versions, hashes, and retrieval instructions.
- Week, lecture, topic, subtopic, and page mappings.
- The structured question bank and persistent IDs.
- Slide and concept coverage records.
- Completed, active, pending, and blocked work.
- Agent assignments and ownership.
- Review results, unresolved disputes, and rejected questions.
- Build, verification, and recovery instructions.
- The next concrete actions and the latest verified remote checkpoint.

Choose sensible filenames and organization; a concise resume document plus machine-readable state is sufficient if it preserves everything necessary.

On resumption, inspect the latest remote state, reconcile partial work and stale assignments, and continue outstanding coverage. Avoid restarting completed sections or generating duplicate questions.

Persist important outputs as files as they are produced; do not leave them only in agent messages. Keep credentials and unrelated personal material out of the repository.

## 4. Inventory and inspect every source page

Retrieve the resources through available Drive tools or other permitted download methods. Handle large files with appropriate download and processing methods.

Inventory all relevant files and inspect both the lecture PDF and the assignment-solutions PDF. Record their actual page counts, identifiers, hashes, and versions. Keep their pagination systems separate.

Organize the course as:

**Week → lecture → topic → subtopic → source page → examinable concepts.**

Derive the structure from the resources. Record uncertain boundaries explicitly instead of inventing lecture or week assignments.

Inspect **every slide visually alongside its extracted text**. Use OCR and enlarged crops where needed. Successful text extraction does not establish that a slide has been fully analyzed.

Examine:

- Main text, headings, definitions, and small print.
- Equations, notation, assumptions, units, and derivation steps.
- Tables, individual entries, comparisons, and exceptions.
- Diagrams, graph structure, arrows, axes, legends, and labels.
- Code, pseudocode, algorithms, traces, and worked examples.
- Captions, annotations, footnotes, boundary conditions, and easily overlooked statements.

Record unreadable or uncertain elements and revisit them. Do not guess their contents.

Maintain a **concept-level coverage ledger for every page**. Identify the distinct facts, relationships, procedures, distinctions, examples, and interpretations that could reasonably be examined. Link each to its question IDs and review status.

A page with one question is not necessarily covered. Its other examinable content must also be accounted for.

Retain every page in the ledger, including repeated slides, title pages, references, and genuinely non-examinable pages. Give exclusions a specific reason. Repeated content may share questions, but check for incremental changes and preserve all source references.

Track separately:

- Pages inventoried.
- Pages visually inspected.
- Unique examinable concepts identified.
- Concepts with drafted questions.
- Concepts with independently verified questions.
- Partial coverage, unresolved content, and justified exclusions.

## 5. Generate comprehensive, meaningfully distinct MCQs

Interpret “all possible MCQs” as **every meaningfully distinct, plausible, examinable question supported by the material**, including useful variations in reasoning and application.

Do not impose arbitrary question totals, per-slide quotas, or a convenient stopping count. Let the material determine the bank’s size.

Avoid inflating the bank with superficial paraphrases. Retain variants when they test a distinct misconception, assumption, reasoning step, representation, application, or boundary case. Numerical variants should not inflate unique concept coverage.

Include the following wherever the source material supports them:

- Easy, medium, hard, and extremely tricky questions.
- Direct factual, definition, notation, and terminology questions.
- Conceptual, analytical, application, and scenario questions.
- Numerical problems, formula applications, derivations, and unit checks.
- Diagram, graph, table, and figure interpretation.
- Code-output, pseudocode, and algorithm-tracing questions.
- Assertion–reason and statement-based questions.
- True/false combinations and multiple-correct-answer questions.
- Match-the-following and sequence/order questions.
- NOT, EXCEPT, INCORRECT, LEAST likely, and MOST appropriate questions.
- Similar-looking options with subtle conceptual differences.
- Questions combining concepts across lectures and weeks.
- Questions about assumptions, exceptions, failure cases, limiting cases, and when a method does or does not apply.

Make difficult wording carefully controlled. Convoluted language may test close reading and conceptual understanding, but the correct answer must remain unambiguous.

State any assumption or convention that can change the answer. Specify the criterion behind “best,” “most appropriate,” or “least likely.” Clearly identify single-select and multi-select formats.

Use four or more plausible options where appropriate. Build distractors from realistic misconceptions, incorrect assumptions, sign errors, confused definitions, or plausible algorithm mistakes.

Avoid accidental clues from option length, formatting, grammatical agreement, repeated phrasing, answer-position patterns, or implausible distractors.

Use the assignment-solutions PDF to identify course-specific question styles, methods, conventions, and additional examinable material. Preserve the distinction between supplied assignment questions and newly generated questions. Verify supplied answers; do not assume that a solutions file is infallible.

## 6. Keep answers faithful to the slides

The lecture slides are the primary authority for course answers. Every accepted question must be supported by cited source statements or by a clear derivation from cited premises.

Distinguish:

- What the source explicitly states.
- What follows from the source under stated assumptions.
- Your explanatory analogy, intuition, or mnemonic.

Do not silently import a different textbook convention or use outside facts to override the course material. External technical documentation may support implementation, but question correctness must stay anchored to the supplied course resources.

If a slide contains an apparent error, omission, or contradiction:

- Record the issue and supporting evidence.
- Do not present an incorrect mathematical claim as generally true.
- Where defensible, frame a question explicitly around what the identified slide states.
- Otherwise, flag the question and exclude it from the verified examination pool until resolved.

For conflicts between lecture material and assignment solutions, retain both references and explain the disagreement.

For numerical and algorithm questions, state details that affect correctness: units, precision, rounding, graph direction, edge costs, initial conditions, neighbor ordering, tie breaking, repeated-state handling, termination rules, update timing, or other relevant conventions.

## 7. Provide complete, clear solutions and exact provenance

Every question must include:

1. The correct answer or complete correct-answer set.
2. An explicit justification.
3. Why every incorrect option is wrong in the question’s stated context.
4. Step-by-step reasoning or numerical workings where applicable.
5. Relevant formulas, variable definitions, assumptions, and units.
6. Exact supporting source references.
7. A simple explanation of why and how the concept works.
8. A useful memory aid, mnemonic, or intuition where appropriate.
9. Common misconceptions and examination traps.
10. Related concepts and recommended prerequisite revision where helpful.

Make solutions self-contained enough for revision without requiring the learner to reconstruct missing steps. Use “not applicable” internally where appropriate rather than manufacturing a formula or mnemonic.

For every citation, preserve:

- Source file identifier, filename, and version/hash.
- Physical PDF page number, using a clearly stated one-based convention.
- Combined lecture-PDF page number where applicable.
- Week and lecture identifier.
- Original printed slide number, when actually present.
- Lecture-relative page position as a separate field when useful.
- The relevant statement, equation, table, figure, or precise page region.

**Never substitute the PDF page index for an original printed slide number.** If the original number is absent or unreadable, say so explicitly.

Questions combining sources must cite all premises needed to justify the answer.

Allow navigation from a question to its exact supporting slide and from a slide to its associated questions. Clearly distinguish source content from generated explanations and redrawn figures.

## 8. Independently verify questions before accepting them

Separate authorship from verification.

For every question accepted into the verified bank, an independent reviewer must inspect the cited material and solve the question, preferably before seeing the author’s proposed answer.

Review:

- Whether the source supports the question and answer.
- Whether all necessary assumptions are stated.
- Whether exactly the declared answer set is defensible.
- Whether distractors are plausible and actually incorrect.
- Numerical calculations, units, signs, precision, and rounding.
- Algorithm traces and code behavior.
- Figure fidelity and diagram interpretation.
- Explanation clarity, difficulty classification, and duplication.

Use independent calculation or executable checks where appropriate. Matching reviewer answers alone does not prove correctness; inspect the reasoning and evidence.

Send disagreements for adjudication. Preserve findings and corrections.

Use these audit statuses:

**Draft → verified, flagged, or rejected.**

Tie verification to the reviewed question and source versions. Changes affecting correctness, evidence, diagrams, or numerical generators must trigger appropriate re-review.

Default ordinary practice, examinations, and revision recommendations to verified questions. Keep drafts and unresolved items accessible in an explicitly labeled audit area.

A coverage reviewer should separately challenge each completed section: look for overlooked details, missing contrasts, unsupported assumptions, and examinable interpretations that the original authors missed.

## 9. Build a readable, accessible question interface

Create a clean, minimal, distraction-free interface designed for sustained studying.

Use readable typography, preferably Inter for prose and KaTeX or MathJax for mathematics. Provide comfortable text sizes, line spacing, reading widths, and clear visual hierarchy.

Required capabilities:

- Light/dark mode with a saved preference.
- A collapsible week/lecture sidebar with topic and subtopic navigation.
- Clickable single-select and multi-select answers.
- Submit, skip, reset, bookmark, and mark-for-review actions.
- Previous/next navigation and a question-number palette.
- Clear answered, unanswered, correct, incorrect, bookmarked, and review states.
- Keyboard shortcuts for option selection and navigation.
- Global search across questions, explanations, concepts, and formulas.
- Filters by week, lecture, topic, difficulty, question type, and learning/audit status.
- Persistent question IDs and progress indicators.
- Zoomable diagrams, equations, and source-slide previews.
- Responsive layouts for common screen sizes.

Make controls keyboard-operable, provide visible focus, and communicate feedback through text and symbols as well as color. Support readable contrast, reduced motion, sensible mathematical overflow, and useful descriptions of diagrams.

Keyboard shortcuts must not interfere with typing in search boxes or other inputs.

Implement these study modes:

**Practice:** immediate feedback for single-select questions when enabled; multi-select questions reveal feedback after the learner submits the complete selection.

**Exam simulation:** timed, randomized sessions with configurable scope, question count, difficulty mix, and clearly stated scoring. Delay solutions and revealing feedback until submission or expiration. Preserve selections, review flags, and the attempt’s exact ordering through reloads.

**Last-day revision:** a focused route through high-yield concepts, recurring errors, bookmarks, confusion pairs, and unresolved weaknesses.

Make timer behavior reliable across reloads and background tabs. Present any configurable partial-credit or negative-marking rules before the attempt begins; do not invent an official examination scheme.

## 10. Add the requested learning tools

Integrate these with the question bank and source mappings:

- **Confusion pairs:** side-by-side comparisons of similar concepts, formulas, methods, and algorithms, with discriminating questions.
- **Week-wise formula sheet:** equations, variable meanings, units, assumptions, applications, and common mistakes.
- **Numerical variation engine:** validated parameterized question families with reproducible variants and regenerated worked solutions.
- **Algorithm visualizations:** step-by-step demonstrations of course algorithms, including BFS, DFS, UCS, A*, Q-learning, and others where supported by the material.
- **Slide coverage heatmap:** drill down from weeks and lectures to individual pages, concepts, questions, and uncovered content.
- **Mastery tracking:** distinguish factual recall from conceptual, application, and numerical performance.
- **Exam trap library:** recurring wording patterns, mistaken assumptions, and distractor mechanisms, illustrated by source-linked examples.
- **Mistake-based revision:** connect attempted questions to prerequisite concepts and recommended follow-up practice.

Treat mastery as a transparent study heuristic. Repeated success on the same memorized question must not automatically imply broad conceptual mastery.

Numerical generators must enforce valid parameter domains, assumptions, units, precision, and rounding. Reject invalid cases, duplicate options, unintended multiple answers, and options that become equivalent after rounding. Save seeds, parameters, and generator versions.

Algorithm visualizations, questions, and explanations must use the same stated conventions. Let learners inspect intermediate states, step through execution, and reset.

Redrawn diagrams must preserve the original relationships, labels, scales, and other details that affect interpretation. Validate them against the source.

## 11. Make the HTML genuinely self-contained and maintainable

The final HTML must work when opened directly from the filesystem without installation, a development server, an account, or an internet connection.

Embed everything required for normal use:

- The question bank and supporting metadata.
- Application JavaScript and CSS.
- Offline mathematics rendering or equivalent pre-rendered accessible mathematics.
- Required fonts or suitable local fallbacks.
- Diagrams, source previews, and supporting visual assets.
- Search and learning-tool data.

Keep all cited source slides available offline at a resolution that allows meaningful inspection. Plan for the full source corpus early. A thumbnail that becomes unreadable when enlarged is insufficient.

Choose an efficient asset strategy: deduplicate shared resources, compress appropriately, and render or decode content when needed. You may use embedded source documents with an offline viewer or another approach that preserves exact, readable evidence.

Measure file size, load time, memory use, and interaction performance with representative material early, then with the complete bank.

Check actual GitHub file and delivery limits before the final build. If large-file handling is necessary, use a supported durable method and verify that the downloaded deliverable is the real HTML file rather than a pointer or an incomplete build. Preserve the single-file offline goal.

Use structured JSON-based question data in the repository. Design a suitable schema with stable IDs for sources, slides, concepts, questions, options, and variants.

Store correct answers by **option IDs**, never by displayed letters or array positions.

Randomization must preserve correctness, source links, explanations, bookmarks, and results. Record enough attempt information to reproduce the same questions, variants, and option order. Avoid position-dependent option wording unless it is safely transformed during shuffling.

## 12. Preserve progress and support useful exports

Save study progress and examination state locally. Detect unavailable storage or save failures and give clear feedback.

Provide versioned JSON backup export/import covering progress, attempts, bookmarks, review flags, and relevant settings. Validate imports and handle changed bank versions or duplicate records without silently deleting existing progress.

Support:

- JSON export of structured questions and results.
- Properly escaped CSV export of questions and results.
- PDF export or a polished, clearly labeled offline print-to-PDF workflow.
- Print-friendly question papers without answers.
- Separate answer keys and worked-solution versions.

Exports must preserve question IDs, source citations, selected and correct answers, and the actual option ordering used in the relevant attempt. Include variant parameters and scoring information where needed for faithful reconstruction.

Print layouts must handle page breaks, equations, and diagrams cleanly.

## 13. Validate the complete product

Automate meaningful integrity checks for:

- Duplicate or missing IDs.
- Missing answers, invalid option references, or inconsistent answer sets.
- Missing explanations and distractor justifications.
- Invalid page mappings or broken source references.
- Missing images, diagrams, and assets.
- Duplicate questions and suspicious paraphrase clusters.
- Broken formula rendering and cross-links.
- Numerical generator failures.
- Unexpected network dependencies.
- Questions whose verification became stale.

Also test the application’s behavior with real content:

- Single-select and multi-select submission and scoring.
- Shuffling without correctness changes.
- Bookmarking, review flags, filtering, search, and navigation.
- Exam timing, reload, resumption, submission, and expiration.
- Progress persistence and backup export/import round trips.
- Exported answer keys matching displayed question order.
- Keyboard accessibility, light/dark themes, and source-preview zoom.
- Responsiveness with the full question bank and source assets.

Verify the **actual final downloaded HTML offline**, not only a development preview.

Structural checks establish data integrity; independent source-based review establishes answer correctness. Require both.

## 14. Complete the work against evidence, not a question count

Continue generation, review, and gap repair until:

- The source inventory and page counts are reconciled.
- Every page has been inspected and has an accountable disposition.
- Every identified examinable concept has appropriate verified coverage.
- Repeated pages and exclusions are explicitly mapped.
- Every question presented as verified has passed independent review.
- An independent coverage challenge finds no remaining meaningful omissions.
- The requested application and learning features work with the complete bank.
- The final HTML functions offline.
- The complete project and final checkpoint are verified on GitHub.

Do not claim mathematical exhaustiveness over infinitely many possible phrasings or numerical inputs. Demonstrate comprehensive coverage of the finite course material and its meaningful examination angles.

If missing access, unreadable sources, unresolved contradictions, or platform constraints prevent completion, preserve a usable checkpoint and specify exactly what remains. Keep partial work clearly labeled.

Provide concise progress updates during execution with actual coverage, accepted questions, unresolved issues, and the next work being completed. Avoid repetitive planning narration.

If interrupted, leave the repository in a state that a fresh session can recover from immediately. Continue from that state when resumed.

At final delivery, provide:

- The usable HTML download and repository location.
- Actual source-page and week/lecture coverage.
- Verified question totals by week, difficulty, and type.
- Separate counts for unique questions, numerical families, drafts, flags, and rejections.
- Links to coverage and audit records.
- Brief instructions for opening the app, running an exam, saving backups, and rebuilding it.
- Any precise remaining limitations or source disputes.

**Begin now: inspect the repository and source folder, establish durable project state, activate the maximum useful supported agent capacity at the highest available reasoning setting, and work through the entire course to the verified final study application.**
