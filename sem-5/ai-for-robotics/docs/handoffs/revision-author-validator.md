# Revision-author independence enforcement

Standalone `scripts/validate.py` now excludes both the original author and all `revisionAuthors` from valid acceptance reviews, matching `scripts/review_gate.py`. Optional `revisionAuthors` is schema-checked as a unique array of nonblank IDs in every embedded question schema. The contract documents the requirement.

Validation on 2026-10-19: 58 integrity tests pass, including eight new synthetic regressions; all eight assembly-gate tests pass; validator compiles. No question content changed. Tests cover multiple revision authors, unrelated reviewer acceptance, malformed/blank/duplicate metadata, hash binding, draft nonacceptance and the original author exclusion.
