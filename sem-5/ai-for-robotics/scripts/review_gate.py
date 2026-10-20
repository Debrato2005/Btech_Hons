"""Fail-closed assembly of independently reviewed study questions.

This gate does not replace the complete validator or human source review. It
prevents a stale approval label from entering normal study while provenance is
unresolved. It changes only status/reviewIds, which are excluded from the content
hash, and records blocking reasons outside the question content.
"""
from validate import CHECK_KEYS, question_hash


def apply_review_gate(questions, reviews, slides, sources):
    by_slide = {s['id']: s for s in slides}
    by_source = {s['id']: s for s in sources}
    by_question = {}
    for review in reviews:
        by_question.setdefault(review.get('questionId'), []).append(review)
    quarantined = []
    for question in questions:
        fingerprint = question_hash(question)
        current = [r for r in by_question.get(question['id'], [])
                   if r.get('questionVersion') == question['version']
                   and r.get('questionSha256') == fingerprint]
        question['reviewIds'] = [r['id'] for r in current]
        required_slides = {c['slideId'] for c in question['citations']}
        required_sources = {c['sourceId']: c['sourceSha256'] for c in question['citations']}
        authors = {question['authorId'], *question.get('revisionAuthors', [])}

        def source_bound(review):
            versions = review.get('sourceVersions', {})
            return all(versions.get(sid) == sha for sid, sha in required_sources.items()) and all(
                sid in by_source and by_source[sid].get('sha256') == sha
                for sid, sha in versions.items())

        usable = [r for r in current if source_bound(r)]
        disputes = [r for r in usable if r.get('decision') in ('flagged', 'rejected')]
        accepted = [r for r in usable if r.get('decision') == 'verified'
                    and r.get('reviewerId') not in authors
                    and all(r.get('checks', {}).get(key) is True for key in CHECK_KEYS)
                    and bool(r.get('independentAnswerOptionIds'))
                    and set(r.get('independentAnswerOptionIds', [])) <= {o['id'] for o in question['options']}
                    and set(r.get('independentAnswerOptionIds', [])) == set(question['correctOptionIds'])
                    and required_slides <= set(r.get('reviewedSlideIds', []))]
        reasons = []
        if disputes:
            reasons.append('A current independent review dispute is unresolved.')
        if accepted:
            for citation in question['citations']:
                slide = by_slide.get(citation['slideId'])
                source = by_source.get(citation['sourceId'])
                if not slide or not source:
                    reasons.append('A cited source or page is missing.')
                    continue
                if (source.get('sha256') != citation['sourceSha256']
                        or slide.get('sourceSha256') != citation['sourceSha256']
                        or slide.get('sourceId') != citation['sourceId']
                        or slide.get('physicalPage') != citation['physicalPage']):
                    reasons.append('A citation does not match its current source/page/hash.')
                if source.get('retrievalStatus') != 'ready' or slide.get('visualInspection', {}).get('status') != 'complete':
                    reasons.append('A cited source is unavailable or not visually inspected.')
                if slide.get('disposition') in ('unreviewed', 'unresolved'):
                    reasons.append('A cited page contains unresolved source material.')
                if citation.get('role') == 'conflict' and not question.get('conflictResolution'):
                    reasons.append('Conflicting evidence has no explicit resolution.')
        if reasons:
            question['status'] = 'flagged'
            quarantined.append({'questionId': question['id'], 'reasons': sorted(set(reasons))})
        elif accepted:
            question['status'] = 'verified'
        elif question.get('status') not in ('flagged', 'rejected'):
            question['status'] = 'draft'
        elif current and not usable:
            question['status'] = 'draft'
    return quarantined
