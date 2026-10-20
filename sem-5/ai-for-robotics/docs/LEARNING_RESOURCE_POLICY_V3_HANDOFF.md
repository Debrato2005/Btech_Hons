# Narrow policy 1.0.2 re-review

The v2 reviewer froze all 18 tool computation/configuration approvals but flagged LR-P05: Python accepted a real implementation file missing from, or conflicting with, the policy's `codeHashes`. JavaScript already rejected both cases. This packet addresses only that parity defect. It does not introduce examples or change computational payloads.

## Exact changes

- `scripts/learning_resources.py`: every listed tool implementation must equal the policy's hash at the exact same path, in addition to matching actual on-disk bytes. During pre-assembly, the candidate policy is read from `data/learning-resource-policy.json`. Once bank integrity metadata is present, only its embedded policy is used. Missing/malformed embedded policy data never falls back to a different filesystem policy.
- `app/learning-resources.js`: only the supported policy-version constant changes from 1.0.1 to 1.0.2. No JavaScript computation or extraction logic changes.
- `data/learning-resource-policy.json`: version 1.0.2 with current code hashes, still draft and not independently approved.
- `tests/test_learning_resource_gate_parity.py`: adds real-file omission/conflicting-hash cross-language probes, valid controls, malformed-embedded-policy tests, and pre-assembly candidate-policy cases.

All 18 authored tool objects remain byte-for-byte unchanged. Their versions and correctness hashes remain v2; no implementation file bound directly by these objects changed. Preserve their independently approved computation reviews, but do not infer policy approval from them.

## Review materials

- Answer-free repair packet: `audits/blind-learning-resources-policy-v3.json`.
- Minimal bindings: `audits/blind-binding-learning-resources-policy-v3.json`.
- Preserved pre-repair files: `audits/resource-history/v2-before-python-parity-repair/`.
- Frozen reviewer reproduction: `audits/resource-policy-v2-review/policy-linkage-reproduction.json`.
- Prior question/resource source references and independent arithmetic remain unchanged. No new arithmetic answers are included in this packet.

Challenge Python `tool_reasons`, `integrity_errors`, and pre-assembly selection with an actual current implementation that is omitted or conflicting in an otherwise explicitly approved synthetic policy. Check valid controls and ensure incomplete embedded metadata cannot silently use the filesystem policy. Do not rewrite the frozen v2 reproduction when rerunning it; save new evidence separately.

## Author tests and remaining boundary

The shared Python and Node suites are run separately and their exact logs are saved as `audits/learning-resources-v3-author-python-tests.txt` and `audits/learning-resources-v3-author-node-tests.txt`. Passing tests are author evidence, not independent policy acceptance.

No canonical assembly, question mutation, browser launch, install, restricted environment, model, video, hardware or denied documentation route was used. Actual offline downloaded-HTML browser and visual verification remains a separate pending task. The prepared runner and its precise environment requirements remain in `docs/LEARNING_RESOURCE_POLICY_REPAIR_HANDOFF.md`; this repair neither executes nor certifies them.
