# Learning-resource policy repair handoff, version 1.0.1

This is a narrow implementation-policy re-review, not a new blind arithmetic claim. The original independent reviewer passed 18 computations/configurations, 39 fixed examples, five traces and 13,000 varied cases, but flagged the separate extraction/activation policy. That original review and its exact files remain preserved. The policy and all rebound records remain inactive until current-hash independent acceptance.

## Frozen input

- Answer-free packet: `audits/blind-learning-resources-policy-v2.json`.
- Minimal bindings: `audits/blind-binding-learning-resources-policy-v2.json`.
- Original code, policy and tool objects: `audits/resource-history/v1-before-policy-repairs/`.
- Current policy: `data/learning-resource-policy.json`.
- Current authored tools: `data/learning-tools-course.json`.
- Original before-key examples remain `audits/blind-learning-resources-v1.json`. No new example keys or expected outputs are included in this repair packet.

All 18 records advance from version 1 to version 2 only because their shared `app/learning-tools.js` implementation hash changed. Their source references, assumptions, algorithm configurations, numerical domains, linked question bindings and other computational payloads are exactly unchanged. The generator formula versions remain unchanged. Old acceptance hashes do not verify the new objects. Inspect the code delta and exact payload equality before deciding whether the original arithmetic evidence can support a new version-bound review.

## Repairs to inspect independently

1. Registry replacement evicts removed/bank-switched families. Each listing, generation and restoration checks the current record, content digest, source, question, independent reviews and policy. Cached course variants carry a resource/policy binding. The binding enters their identity, so a new approval cannot mix new answers into an old historical attempt. The renderer rechecks before display, scoring, persistence, download and replay. Cached approved algorithm traces receive the same revocation boundary. Explicit author-only draft generation requires both draft registration and `allowDrafts:true`; it remains labeled draft and cannot be restored as current approved practice.
2. Projection contexts retain a detached copy of every original question field and the complete solution, not an extension-field whitelist. Supplemental notebook URL/SHA/cell, external evidence, implementation/experiment provenance, diagram references and source disputes remain available in lazy, text-only UI details. No question object or escape sequence is rewritten.
3. Both language gates require nonempty, unique literal key and independent-answer arrays using valid stable option IDs and declared single/multi cardinality. Reviewer identities must be nonblank and distinct from authors/revision authors after trimming. Conditional intended answers are never substituted. Tool implementation hashes must agree with the approved policy.
4. Question citations and tool references share positive, bounded physical-page and explicit-disposition checks. Source identity/hash, page identity and completed inspection must agree. Unsupported disposition, page zero, out-of-range/fractional/boolean pages and missing page bounds are rejected.

Relevant code: `app/learning-resources.js`, `app/learning-resource-ui.js`, `app/learning-tools.js`, `app/app.js`, `scripts/learning_resources.py`. The unchanged algorithm/formula implementation is not newly certified merely because source arithmetic passed previously.

## Author checks, not independent acceptance

- `python -m unittest discover -s tests -p 'test_*.py' -v`.
- `node --test app/*.test.js tests/test_*.js`.
- Regression details: `tests/test_learning_resource_revocation.js` and `tests/test_learning_resource_gate_parity.py`.
- Real-field projection census: `audits/learning-resources-v2-author-context-checks.json`.
- Rebinding/equality record: `audits/learning-resources-v2-author-rebinding.json`.

The structural DOM tests are inert Node data structures, not a browser, layout engine or permission workaround. The corpus census uses a plainly synthetic in-memory policy approval only to inspect extraction and never writes that approval to any bank or review file.

## Precise pending browser task

The recorded Chromium attempt failed before opening a page with `socket() failed: Operation not permitted (1)` and SIGABRT. It was not retried. The remaining requirement is a permitted environment with an already installed Chromium/Playwright/Node stack, where the browser process may create its local sockets/processes and read the independently downloaded final HTML. No Internet connection is needed for the artifact checks. The existing restricted environment, denied downloads and model/notebook routes stay stopped.

A transferable exact-artifact resource runner is prepared at `tests/browser_learning_resources_artifact.js`. It does not launch anything unless explicitly run with `--execute`. In the permitted testing environment:

`node tests/browser_learning_resources_artifact.js --execute /absolute/path/to/downloaded-final.html /absolute/path/to/resource-browser-report.json`

Use `CHROMIUM_PATH` only for the already installed, permitted browser in that environment. Do not install dependencies, alter system permissions, switch to an alternate blocked route or retry this denied workspace launch. The runner opens `file://` with networking disabled, records exact artifact SHA256/browser version, and exercises current resource pagination, filters, premise/source navigation and zoom, each approved algorithm, numerical answer/replay/export, and desktop/mobile screenshots. Inactive features remain pending rather than receiving synthetic approvals. Human/image review of screenshots remains a separate required result. The general app runner `tests/browser_offline.js` and the remaining full-app interaction matrix are additional gates, not replaced by this resource-specific runner.
