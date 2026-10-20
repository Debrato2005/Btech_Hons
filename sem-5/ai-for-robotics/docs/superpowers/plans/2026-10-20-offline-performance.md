# Offline performance implementation plan

Goal: finish and test one Practice-only HTML with lower startup memory.
Spec: the attached continuation request and EXECUTION_BRIEF.md.
Execution: one implementer, plus the required independent policy review.

1. Preserve the exact baseline. Recover and hash embedded assets and the bank.
2. Measure full-bank startup, process RSS, heap, navigation and preview use.
3. Preserve Practice only. Exclude all other modes and development payloads from production.
4. Test lossless bank decoding, saved-answer compatibility and bounded asset lifetimes.
5. Compress the verified Practice projection. Store each asset outside parsed JSON. Decode on demand.
6. Clear closed source previews. Bound unused Blob URLs. Preserve visible inputs.
7. Rebind changed implementation hashes after independent review.
8. Run integrity and logic checks. Test the exact file offline in Chromium.
9. Inspect screenshots, source evidence and print output. Fix confirmed defects.
10. Package with all embedded hashes. Publish source and release artifacts if access permits.

Constraints: preserve question records, versions, answers, citations and progress keys.
Keep both original PDFs and all required inputs. Use no network at runtime.
Record failures and blocked checks separately from passes.
