#!/usr/bin/env python3
"""Freeze L11 source-first review without changing its authored question batch."""
import collections
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate import CHECK_KEYS, question_hash


def load(path):
    return json.loads((ROOT/path).read_text())


blindpath = ROOT/'audits/blind-answers-W03-L11-independent.json'
blind = load(blindpath)
assert blind['complete'] and blind['solvedBeforeAnswerSeen'] and not blind['keyedBatchOpened']
packet = load('audits/blind-W03-L11-review-copy.json')
batchpath = ROOT/'data/question-batches/W03-L11.json'
batch = load(batchpath)
answers = {a['questionId']: a for a in blind['answers']}
qs = {q['id']: q for q in batch['questions']}
assert len(answers) == len(qs) == 108
for q in packet['questions']:
    for key in ['stem', 'version', 'selectionMode', 'options', 'assumptions', 'difficulty']:
        assert q[key] == qs[q['id']][key]
    assert set(qs[q['id']]['correctOptionIds']) == set(answers[q['id']]['independentAnswerOptionIds'])
computations = load('audits/W03-L11-independent-computations.json')
assert computations['allPassed'] and computations['caseCount'] == 1623
flags = {}


def flag(short, check, finding):
    qid = 'W03-L11-P' + short
    assert qid in qs
    flags.setdefault(qid, []).append({'check': check, 'finding': finding})


# Meaningful distractors must test domain misconceptions rather than absurd
# category mismatches. These requests do not change any currently correct key.
distractors = {
    '0356-Q02': 'Replace the rendering/naming and mass-without-motion/geometry-only pairs with plausible competing forward/inverse dynamics applications. The present wrong pairs can be rejected without knowing the lecture distinction.',
    '0358-Q02': 'Replace the doubled physical rotation rate, all-terms-doubled and degree-conversion explanations with plausible product-rule/transport-term omissions. The factor two should be discriminated from realistic differentiation errors.',
    '0363-Q04': 'Replace the mass-vanishes and principal-axes-never-exist alternatives with credible origin-versus-orientation confusions, keeping the explicit specified-origin distinction.',
    '0364-Q03': 'Replace uniform color and choosing a corner frame with plausible density/geometry conditions. The question should test COM versus geometric centroid, not eliminate unrelated display properties.',
    '0364-Q04': 'Replace the massless-only COM formula, no-rigid-translation and every-point-mass-equals-every-solid alternatives with realistic mistakes about preserving force balance, rotational inertia or parallel-axis contributions.',
    '0367-Q01': 'Use plausible competing matrix properties or incomplete constraints rather than negative diagonal/zero mass/arbitrary nonsymmetric matrices. Keep the nondegenerate-solid assumption and distinguish symmetry/positive definiteness from sufficient physical realizability.',
    '0367-Q02': 'Replace name-as-proof, any-matrix-is-physical and symmetry-cannot-be-encoded claims with realistic contrasts between soft penalties, constrained parameterizations and post-hoc checks. Keep the correct requirement for actual enforcement.',
    '0371-Q05': 'Replace zero mass and arbitrary-corner alternatives with credible thick-shell, radius-choice or axis assumptions. The thin-wall qualification should not be selected merely by eliminating physically unrelated statements.',
    '0372-Q03': 'Replace display textures, reporting units and only camera orientation with plausible physical component-placement strategies. Preserve the source-specific recall scope so another generally valid COM intervention does not become an unintended second answer.',
    '0372-Q05': 'Replace eliminating all constraints, geometry-independent inertia and identical COM for all designs with realistic competing structural optimization objectives or mass/stiffness tradeoffs.',
    '0373-Q01': 'Replace zero diagonal moments, unnecessary mass and antisymmetric tensor alternatives with credible distinctions among products, principal moments, origin choice and relevant symmetry planes.',
    '0373-Q02': 'Replace zero motor inertia and negative load inertia with plausible reflected-inertia or matching-ratio errors. Keep mass matching distinct from inertia matching and retain the source-attributed heuristic qualification.',
    '0374-Q02': 'Replace complete zero tensor, all mass on z and products-never-zero alternatives with plausible cancellation patterns. The useful distinction is that an xy symmetry plane cancels xz and yz, not necessarily xy.',
    '0374-Q07': 'Use plausible eigenvalue/eigenvector role swaps or component-versus-principal-axis confusions instead of unrelated joint rates/torques and COM/density categories.',
    '0374-Q09': 'Replace color calibration, temperature alone and focal-length chart with plausible mass-property measurement procedures. Retain the explicit source-example question rather than implying the named method is the only valid procedure.',
    '0375-Q04': 'Replace comparing the mass number to inertia numbers with a realistic principal-frame criterion error, and distinguish a translated frame from a rotated principal frame using credible alternatives.',
    '0375-Q07': 'Replace display-color inference, dimensionless identity and omitted-COM claims with plausible competing CAD/measurement/export workflows. Retain the historical source-attributed wording, not a current plugin availability claim.'
}
for qid, finding in distractors.items():
    flag(qid, 'distractors', finding)

hard_to_medium = {
    '0356-Q03': 'This is the short model/initial-state qualification of a schematic mapping, not a demanding dynamics calculation.',
    '0358-Q02': 'Identifying the two displayed product-rule contributions is a short derivation check.',
    '0359-Q04': 'Recognizing a general formula includes its fixed-point special case is a straightforward conceptual distinction.',
    '0363-Q04': 'The item directly contrasts origin dependence with a change of orientation.',
    '0364-Q04': 'The translational point-mass approximation versus rotational mass-spread distinction is conceptual and short.',
    '0366-Q03': 'The corner-origin positive coordinate domains directly explain the nonzero products.',
    '0367-Q02': 'The distinction between a model name and actual constraint enforcement is a basic implementation qualification.',
    '0368-Q06': 'This is one application of the common-basis rule for adding tensors.',
    '0371-Q05': 'Recognizing the thin-wall condition from a squared-radius integral is a short conceptual check.',
    '0371-Q06': 'The normal-axis versus in-plane-axis qualification is a direct application of perpendicular squared distances.',
    '0372-Q04': 'The item asks for a conditional design objective, without a difficult COM calculation.',
    '0373-Q03': 'Rejecting an unqualified universal efficiency claim requires a basic model-scope distinction.',
    '0373-Q04': 'This directly distinguishes a conditional tradeoff from universal speed/stability guarantees.',
    '0374-Q02': 'One reflection symmetry and the unchanged xy integrand settle the question immediately.',
    '0374-Q03': 'Nonnegative squared distance and an axis-supported counterexample give a short qualification.',
    '0375-Q04': 'Reading zero off-diagonal entries and identifying a principal basis is a direct conceptual application.',
    '0376-Q01': 'Comparing the two displayed formulas identifies one missing term; no difficult derivation is required.',
    '0376-Q02': 'The omitted addend must be zero, a one-condition validity check.'
}
for qid, reason in hard_to_medium.items():
    flag(qid, 'difficulty', 'Change hard to medium. ' + reason)
for qid in ['0368-Q04', '0368-Q05']:
    flag(qid, 'difficulty', 'Change extremely_tricky to hard at most. The raw-product versus signed-entry convention is genuinely subtle, but the explicit definitions and one sign change/source comparison do not justify the highest difficulty category.')
for qid, reason in {
    '0355-Q03': 'This directly identifies joints as allowing relative motion between rigid links.',
    '0356-Q02': 'This directly recalls the two application labels on the source slide.',
    '0363-Q01': 'This asks for the principal-axis definition, with no calculation.',
    '0363-Q03': 'The principal moments are explicitly supplied as the three diagonal values.',
    '0369-Q01': 'The center of a uniform axis-aligned box is the midpoint of each supplied interval.',
    '0375-Q06': 'This only compares the explicitly supplied diagonal values .003, .003 and .001.'
}.items():
    flag(qid, 'difficulty', 'Change medium to easy. ' + reason)

flag('0355-Q02', 'explanation', 'Repair the o2 rationale and copied misconception: three translations plus one rotation is not a planar rigid-body motion model. A planar rigid body has two in-plane translations and one rotation. Explain that o2 permits only one independent orientation change in a spatial setting, instead of equating it with a planar constraint.')
flag('0358-Q05', 'assumptions', 'Specify that the point is fixed in B (q_B is constant), while r=(2,0,0) is its instantaneous A-expressed offset. The present phrase "fixed r" is ambiguous and can mean fixed in A; it does not unambiguously justify setting a_rel=0. Retain the intended alpha-cross-r answer under the explicit body-fixed-point condition.')
flag('0360-Q04', 'assumptions', 'Replace "bases denoted by their subscripts" with explicit roles: alpha_AB and omega_AB describe B relative A and are expressed in A; alpha_BC and omega_BC describe C relative B and are expressed in B; R_AB maps B components to A. AB/BC are frame pairs, not uniquely identified expression bases by themselves.')
flag('0372-Q02', 'explanation', 'Replace or supplement the attached mass-change formula Delta I=Delta m*r_perp^2 with the actual fixed-mass relocation relation I=m*r_perp^2 and Delta I=m*(r_new^2-r_old^2). Define all actual symbols and units, and state that the axis and component mass remain fixed while radius changes. The existing "added or removed mass" definition and unchanged-geometry assumption do not describe this question. The numerical key and workings are correct.')

conflicts = {
    '0368-Q05': 'The raw integral convention on p362 differs from the signed-entry scalar shift on p368; the valid matrix theorem and p369 cancellation establish the distinction.',
    '0372-Q04': 'The all-configurations COM-stability guarantee must remain a design objective requiring configuration and support checks.',
    '0373-Q03': 'An inertia equality without specified drive coordinates, losses and objective cannot establish universal power-transfer efficiency.',
    '0374-Q03': 'Squared-distance integrals are nonnegative and can vanish for ideal axis-supported mass, rather than being strictly positive in all idealizations.',
    '0376-Q01': 'The summary omits origin acceleration present in the separated-origin p359 formula.',
    '0376-Q02': 'The omitted-origin formula is valid only under the added zero-origin-acceleration condition, not as an unqualified general formula.'
}
for qid, detail in conflicts.items():
    flag(qid, 'sourceSupport', 'Add precise version-bound question-level conflictResolution metadata. The citation already has role=conflict, but the question has no resolution record. Identify the literal source claim, bounded interpretation/correction and independent derivation or supplied-page basis. ' + detail + ' Preserve the source-dispute ledger; do not claim the PDF is globally resolved.')

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
reviewer = blind['reviewerId']
reviews = []
for qid, q in qs.items():
    a = answers[qid]
    checks = {key: True for key in CHECK_KEYS}
    for f in flags.get(qid, []):
        checks[f['check']] = False
    assert reviewer not in {q['authorId'], *q.get('revisionAuthors', [])}
    refs = q['citations']
    reason = a['reasoning'] + ' After freezing the source-derived answer, I checked every keyed option explanation, step, formula, assumption, citation and classification. The intended answer agrees; distinct quality or provenance failures are recorded separately. Numerical/derivation items were checked by independent vector, finite-difference, point-cloud or exact-quadrature calculations as applicable. For recall-only items calculations are not required. Figure fidelity means the actual cited source axes, offsets, equations, table or XML were read, not inferred from OCR. No problematic duplicate beyond deliberate concept/application and validity-boundary contrasts was found.'
    reviews.append({
        'id': f'REV-{qid}-v1-interface-independent',
        'questionId': qid, 'questionVersion': q['version'],
        'questionSha256': question_hash(q), 'reviewerId': reviewer,
        'decision': 'flagged' if qid in flags else 'verified', 'reviewedAt': now,
        'sourceVersions': {c['sourceId']: c['sourceSha256'] for c in refs},
        'reviewedSlideIds': a['reviewedSlideIds'],
        'sourceInspectionEvidence': [
            {'physicalPage': c['physicalPage'], 'inspectorIds': [reviewer],
             'previewSha256': hashlib.sha256((ROOT/f"sources/previews/lectures/page-{c['physicalPage']:04d}.webp").read_bytes()).hexdigest()}
            for c in refs],
        'independentAnswerOptionIds': a['independentAnswerOptionIds'],
        'solvedBeforeAnswerSeen': True, 'checks': checks, 'reasoning': reason,
        'findings': [f['finding'] for f in flags.get(qid, [])],
        'reviewType': 'independent_blind_initial_review',
        'priorReviewerExposure': False, 'priorAuthorExposure': False,
        'blindAnswersPath': str(blindpath.relative_to(ROOT)),
        'blindAnswersSha256': hashlib.sha256(blindpath.read_bytes()).hexdigest(),
        'computationsPath': 'audits/W03-L11-independent-computations.json'
    })
reviewpath = ROOT/'data/reviews/W03-L11-v1-independent.json'
assert not reviewpath.exists()
reviewpath.write_text(json.dumps(reviews, ensure_ascii=False, indent=2)+'\n')
gaps = [{
    'physicalPage': 357, 'kind': 'definition/notation',
    'gap': 'The angular-acceleration derivative/difference quotient and the shorthand omega_dot_A for the frame A angular acceleration relative to U are not directly tested. Existing p357 questions cover linear acceleration and linear-origin shorthand; p360 covers composition. Add a concise angular-rate derivative or notation-interpretation item with the observer and expression basis explicit, rather than duplicating another transport numerical case.',
    'status': 'new draft question required'
}]
summary = {
    'reviewedAt': now, 'reviewed': 108, 'verified': 108-len(flags),
    'flagged': len(flags), 'answerAgreement': 108, 'answerCorrectionsRequired': 0,
    'independentBlindReview': True, 'sourcePagesInspected': list(range(352, 379)),
    'computationGroupsPassed': len(computations['groups']),
    'computationCasesPassed': computations['caseCount'],
    'reviewPath': str(reviewpath.relative_to(ROOT)),
    'blindAnswersPath': str(blindpath.relative_to(ROOT)),
    'reviewedBatchSha256': hashlib.sha256(batchpath.read_bytes()).hexdigest(),
    'actionableFlags': flags,
    'flagCountsByCheck': dict(collections.Counter(f['check'] for ff in flags.values() for f in ff)),
    'approvedCurrentHashes': {r['questionId']: r['questionSha256'] for r in reviews if r['decision']=='verified'},
    'allReviewedCurrentHashes': {r['questionId']: r['questionSha256'] for r in reviews},
    'coverageGaps': gaps,
    'sourceAndScopeNotes': [
        'All 27 source page images and their extracted text were inspected before opening the keyed batch or author issue ledger.',
        'The frozen answer-hidden packet hash matches the assigned SHA-256. The review copy contains no citation evidenceText.',
        'All 108 intended keys agree. For the fixed-r example, the intended answer needs an explicit body-fixed-point condition; agreeing with the intended key does not approve the ambiguous wording.',
        'Raw products and signed tensor entries are deliberately distinguished. The summary omission and overbroad design/positivity claims remain preserved as source disputes.',
        'No authored question, inspection record, source-dispute ledger, PDF or canonical bank was modified.'
    ],
    'nonblockingStyleNotes': [
        'Minor prose/number joins occur throughout (for example "mass3" and "byL/2"). Repair them when revising flagged items. Do not silently polish approved objects without a version bump and review rebinding.',
        'The reusable inertia formula record could explicitly expand r=(x,y,z), dm in kg and rho/dV units to improve standalone formula-sheet readability; the position-vector and inertia definitions currently suffice to interpret these checked questions.'
    ]
}
(ROOT/'audits/W03-L11-independent-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
(ROOT/'audits/W03-L11-independent-coverage-gaps.json').write_text(json.dumps(gaps, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({key: summary[key] for key in ['reviewed', 'verified', 'flagged', 'answerAgreement', 'flagCountsByCheck', 'computationCasesPassed']}, indent=2))
