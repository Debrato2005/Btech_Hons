"""Project a fully validated bank into the production Practice payload."""
from validate import question_hash


def project(bank):
    questions = [q for q in bank['questions'] if q['status'] == 'verified']
    sidecar = bank['questionVisuals']
    inputs = {}
    supplemental_ids = set()
    for q in questions:
        binding = sidecar['bindings'].get(q['id'])
        if not binding or binding['questionVersion'] != q['version'] or binding['questionSha256'] != question_hash(q):
            raise ValueError('Practice input binding is missing or stale: ' + q['id'])
        supplemental_ids.update(binding.get('supplementalInputIds', []))
        if binding['assetIds'] or binding.get('supplementalInputIds'):
            inputs[q['id']] = {k: binding.get(k, []) for k in ('assetIds', 'supplementalInputIds', 'requiredInputs')}
    slide_ids = {c['slideId'] for q in questions for c in q['citations']}
    concept_ids = {cid for q in questions for cid in q['conceptIds']}
    slide_fields = ('id', 'sourceId', 'sourceSha256', 'physicalPage', 'combinedLecturePage', 'week', 'lectureId', 'lectureTitle', 'lectureRelativePage', 'printedSlideNumber', 'printedSlideNumberStatus', 'assetId')
    return {
        'schemaVersion': bank['schemaVersion'], 'bankVersion': bank['bankVersion'],
        'title': bank['title'], 'scope': 'practice-only',
        'questions': questions,
        'sources': bank['sources'],
        'slides': [{k: s[k] for k in slide_fields if k in s} for s in bank['slides'] if s['id'] in slide_ids],
        'concepts': [{k: c.get(k, '') for k in ('id', 'title', 'description')} for c in bank['concepts'] if c['id'] in concept_ids],
        'practiceInputs': inputs,
        'supplementalInputs': {s['id']: s for s in sidecar.get('supplementalInputs', []) if s['id'] in supplemental_ids},
    }
