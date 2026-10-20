# Resume and recovery

Read `docs/CURRENT_SCOPE.md` and `docs/PRACTICE_RELEASE.md` first. The user changed
the product to Practice only on 20 October 2026. Do not restart content generation
or restore removed dashboards to the production HTML.

The unchanged original HTML is under `dist/baseline/`, outside Git tracking.
Its SHA-256 is `ef7ef2723af4c55176ed2f1cd8211182c0369224a6e8e71152320c5f34b0ac84`.
The current delivery is `ai-for-robotics-mcq/ai-for-robotics-mcq.html`.
Use `delivery/practice-release-manifest.json` for its exact hash and release URLs.

## Rebuild without authoring questions

1. Use a fresh checkout of the release source commit.
2. Download and hash-check the standalone HTML and build-input archive.
3. Extract `ai-for-robotics-build-inputs.tar.gz` into this project directory.
4. Run `python3 scripts/embedded_payloads.py /absolute/path/to/ai-for-robotics-mcq.html`.
5. Run `python3 scripts/validate.py`, then `python3 scripts/build.py`.

The archive restores the full bank snapshot and three exact summary previews.
The HTML restores every PDF and PNG with its original hash. A Practice-only bank
cannot replace the canonical review bank. No course download, model execution or
question generation is needed. The measured rebuild is byte-identical.

Do not run assembly against missing `sources/page_maps/`. For content changes,
restore page maps from the full bank or original sources before deliberate
reassembly. Preserve the bank version when question content is unchanged.
Question/review batches remain authoritative. Generated `data/bank.json` is ignored.

## Verification and limits

Current evidence is under `audits/offline-optimization/`. It separates integrity,
358 deterministic tests, 15 browser checks, screenshot review and process memory.
Use `tests/browser_practice.js` and `tests/browser_profile.js` for current scope.
Historical exam/tool runners test the former product.

All 2,012 source pages and 5,069 active questions retain their recorded review
bindings. The eleven qualified concept dispositions and original source conflicts
remain. The old all-course release validator does not recognize the newer
qualified-coverage contract. Keep its `complete:false` flag and limitations honest.

The storage key stays `ai-for-robotics-progress-v1`. Keep the same file path and
browser to retain file-origin progress. Existing answer fingerprints, selections,
bookmarks and histories remain compatible. Removed timers never initialize.

Git metadata is read-only in this managed workspace. Inspect the live remote and
current worktree before further changes. The publication receipt records the
verified source commit. Do not reset, rewrite shared history or stage unrelated
paths. Preserve all unrelated projects and existing runtime restrictions in
`sources/README.md` and the historical audit records.
