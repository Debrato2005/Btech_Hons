#!/usr/bin/env python3
"""Repair only the 25 L06 records and add one new coverage question.
Author revisions are drafts, not independent approvals. No shared bank writes.
The original author script recreates v1; this script applies the quality revision.
"""
from pathlib import Path
import copy, hashlib, json, math
from validate import question_hash
ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / 'audits/batch-history/W02-L06-v1-before-quality-repair.json'
TARGET = ROOT / 'data/question-batches/W02-L06.json'
original = json.loads(HISTORY.read_text())
batch = copy.deepcopy(original)
reviews = json.loads((ROOT / 'data/reviews/W02-L06-v1-independent.json').read_text())
expected = {r['questionId'] for r in reviews if r['decision'] == 'flagged'}
approved = {r['questionId'] for r in reviews if r['decision'] == 'verified'}
assert len(expected) == 24 and len(approved) == 53
CONFLICT_ITEM = 'W02-L06-P0238-Q01'
expected.add(CONFLICT_ITEM)
approved.remove(CONFLICT_ITEM)
before = {q['id']: q for q in original['questions']}
by = {q['id']: q for q in batch['questions']}
changed = set()
AUTHOR = 'build_offline_study_interface-L06-quality-reviser'


def revise(short, **updates):
    qid = 'W02-L06-' + short
    assert qid in expected and qid not in changed
    q = by[qid]
    assert q['version'] == 1
    q.update(version=2, status='draft', reviewIds=[], revisionAuthors=[AUTHOR])
    for key, value in updates.items():
        if key == 'options':
            assert set(value) == {o['id'] for o in q['options']}
            for option in q['options']:
                option['text'] = value[option['id']]
        elif key == 'reasons':
            assert set(value) == {o['id'] for o in q['options']}
            q['solution']['optionExplanations'] = value
        elif key == 'why':
            q['solution'].update(justification=value, simpleExplanation=value)
        elif key in ('steps', 'formulas', 'misconceptions', 'examTraps'):
            q['solution'][key] = value
        else:
            q[key] = value
    changed.add(qid)
    return q


def formula(expression, variables, units, assumptions):
    return [{'expression': expression, 'variables': variables, 'units': units, 'assumptions': assumptions}]


revise('P0217-Q02', formulas=formula(
    '||p||=sqrt(p_x²+p_y²+p_z²)',
    {'p': '3×1 position column of the point measured from the origin of frame A, expressed in A',
     'p_x': 'Signed projection on the unit X_A axis', 'p_y': 'Signed projection on the unit Y_A axis',
     'p_z': 'Signed projection on the unit Z_A axis', '||p||': 'Euclidean distance from the A origin'},
    {'p, p_x, p_y, p_z, ||p||': 'metres in this question'},
    ['The three Cartesian axes are mutually perpendicular unit directions.',
     'All components use the same origin, frame and length unit.']))
revise('P0221-Q02', formulas=formula(
    'r_ij = e_i^A · e_j^B = cos(theta_ij)',
    {'r_ij': 'Entry in row i, column j of the rotation matrix ^A_B R mapping B components to A components',
     'e_i^A': 'Unit direction of axis i of frame A, expressed in a common frame for the dot product',
     'e_j^B': 'Unit direction of axis j of frame B, expressed in that same common frame',
     'i, j': 'Axis indices 1, 2, 3 corresponding to X, Y, Z',
     'theta_ij': 'Geometric angle between the selected A axis and B axis, in [0°,180°]'},
    {'r_ij, e_i^A, e_j^B': 'dimensionless', 'theta_ij': 'degrees here; use a consistent angle unit for cosine'},
    ['Both axis vectors have unit length.', 'Rows refer to A axes and columns refer to B axes.']))
for short, axis, angle, expression in [
    ('P0222-Q01', 'X', 'gamma', 'Rx(gamma)=[[1,0,0],[0,c_gamma,-s_gamma],[0,s_gamma,c_gamma]]'),
    ('P0223-Q01', 'Y', 'beta', 'Ry(beta)=[[c_beta,0,s_beta],[0,1,0],[-s_beta,0,c_beta]]'),
    ('P0224-Q01', 'Z', 'alpha', 'Rz(alpha)=[[c_alpha,-s_alpha,0],[s_alpha,c_alpha,0],[0,0,1]]')]:
    symbol = 'R' + axis.lower()
    revise(short, formulas=formula(expression,
        {symbol + '(' + angle + ')': f'3×3 elementary right-hand rotation about the {axis} axis acting on column vectors',
         angle: f'Rotation angle about the positive {axis} axis',
         'c_' + angle: f'cos({angle})', 's_' + angle: f'sin({angle})'},
        {angle: 'degrees when marked °; convert to radians for the slide’s Python call',
         symbol + ', c_' + angle + ', s_' + angle: 'dimensionless matrix entries and trigonometric values'},
        ['Right-handed orthonormal Cartesian axes; positive angle follows the right-hand rule.',
         'Column-vector multiplication is on the left; the opposite coordinate-map direction uses the transpose.',
         'The matrix changes orientation only; it contains no translation.']))
revise('P0222-Q02',
    stem='In the slide’s R=rotx(np.pi/2) animation with dims=[−1.5,1.5,−1.5,1.5,−1.5,1.5], which interpretation is correct?',
    options={
        'o1': 'The rotation angle is 90°, the X component is invariant, and dims sets Cartesian plotting bounds',
        'o2': 'The rotation angle is about 1.571°, the X component is invariant, and dims sets Cartesian plotting bounds',
        'o3': 'The rotation angle is 90°, the X component is invariant, and dims sets angular limits about the three axes',
        'o4': 'The rotation angle is 90°, the Y component is invariant, and dims sets Cartesian plotting bounds'},
    reasons={
        'o1': 'The code uses pi/2 radians, equal to 90°. The X-rotation matrix keeps x unchanged. The six dims entries give lower and upper Cartesian plot bounds.',
        'o2': 'Pi/2 is about 1.571 radians, not 1.571 degrees. Converting radians to degrees gives 90°.',
        'o3': 'The displayed plot has X, Y and Z coordinate limits of −1.5 to 1.5; dims is not a set of rotation-angle limits.',
        'o4': 'The invariant component is X, the axis of this rotation. Y and Z mix through the sine and cosine entries.'},
    why='The angle argument, invariant axis and display bounds have different roles: pi/2 radians specifies a quarter-turn about X, while dims controls the Cartesian viewing box.',
    steps=['Convert (pi/2) radians × (180°/pi) to 90°.',
           'Read the Rx first row [1,0,0], giving x_out=x_in.',
           'Match the three lower/upper dims pairs to the coordinate limits on the displayed plot.'],
    examTraps=['Do not interpret a radian value as degrees or plotting bounds as rotation parameters.'])
revise('P0226-Q02', difficulty='easy')
revise('P0227-Q01', formulas=formula(
    '^A P=^B P+^A P_BORG',
    {'^A P': 'Position column of the same point P measured from the A origin, expressed in A',
     '^B P': 'Position column of P measured from the B origin, expressed in B',
     '^A P_BORG': 'Displacement from the A origin to the B origin, expressed in A'},
    {'^A P, ^B P, ^A P_BORG': 'the same length unit as the supplied coordinates'},
    ['A and B have aligned axes with the same positive directions, so their orientation matrix is the identity.',
     'Column vectors are added componentwise after the aligned-axis identification; only the origin changes.']))
revise('P0228-Q02', formulas=formula(
    '^A P=R ^B P+p',
    {'^A P': 'Position of point P relative to A, expressed as a 3×1 A-coordinate column',
     '^B P': 'Position of the same point P relative to B, expressed as a 3×1 B-coordinate column',
     'R': '^A_B R, the 3×3 proper rotation whose columns are the B unit axes expressed in A; it converts B components to A components',
     'p': '^A P_BORG, the 3×1 displacement from the A origin to the B origin, already expressed in A'},
    {'^A P, ^B P, p': 'the same length unit as the supplied coordinates', 'R': 'dimensionless'},
    ['Right-handed Cartesian frames and column-vector convention.',
     'Rotate the B-coordinate point before adding the A-coordinate origin offset; do not rotate p again.']))
revise('P0229-Q03', difficulty='medium')
revise('P0230-Q02', difficulty='medium', formulas=formula(
    '[R1,p1;0,1][R2,p2;0,1]=[R1R2,R1p2+p1;0,1]',
    {'R1': '^A_B R, a 3×3 rotation converting B components into A components',
     'p1': '3×1 position of the B origin relative to A, expressed in A',
     'R2': '^B_C R, a 3×3 rotation converting C components into B components',
     'p2': '3×1 position of the C origin relative to B, expressed in B',
     'R1R2': '^A_C R, the composed 3×3 rotation from C coordinates to A coordinates',
     'R1p2+p1': '3×1 position of the C origin relative to A, expressed in A',
     '0': '1×3 zero row in each homogeneous matrix', '1': 'Dimensionless homogeneous bottom-right scalar'},
    {'R1, R2, R1R2, 0, 1': 'dimensionless', 'p1, p2, R1p2+p1': 'a common length unit'},
    ['Each bracket denotes a 4×4 block matrix acting on homogeneous column coordinates.',
     'Compatible frames: T1 maps B to A; T2 maps C to B; T1T2 maps C to A.']))
revise('P0230-Q03', difficulty='medium')
revise('P0230-Q04', difficulty='medium')
revise('P0230-Q06', formulas=formula(
    'T^−1=[R^T,-R^T p;0,1]',
    {'T': '^A_B T=[R,p;0,1], the 4×4 transform from homogeneous B coordinates to A coordinates',
     'T^−1': '^B_A T, the reverse coordinate mapping from A to B',
     'R': '^A_B R, the 3×3 proper rotation converting B vector components to A components',
     'R^T': 'Transpose of R, equal to ^B_A R because R is orthogonal',
     'p': '3×1 position of the B origin relative to A, expressed in A',
     '-R^T p': '3×1 position of the A origin relative to B, expressed in B',
     '0': '1×3 zero row', '1': 'Dimensionless homogeneous bottom-right scalar'},
    {'R, R^T, 0, 1': 'dimensionless', 'p, -R^T p': 'the same length unit as the supplied coordinates',
     'T, T^−1': 'mixed blocks: dimensionless rotation/bottom row and length-valued translation column'},
    ['Rigid Cartesian transform with R^T R=I and det(R)=+1; column-coordinate convention.',
     'The inverse displacement must be expressed in B, so negating p without rotating it is generally insufficient.']))
revise('P0231-Q02',
    options={
        'o1': 'The 4×4 T_R includes a fourth physical spatial axis absent from the 3×3 samples',
        'o2': 'Because translation is zero, the 4×4 T_R can multiply an ordinary 3-component point directly',
        'o3': 'The 3×3 rotation is embedded by adding a zero column and an entirely zero bottom row',
        'o4': 'The formula is a 4×4 homogeneous embedding, while the code uses the corresponding 3×3 rotation-only samples'},
    reasons={
        'o1': 'The added coordinate is homogeneous bookkeeping, not a fourth spatial axis; the physical rotation remains three-dimensional.',
        'o2': 'Zero translation does not remove the dimension mismatch. A point must be augmented to a 4-component homogeneous column before multiplication by T_R.',
        'o3': 'The embedding uses a zero translation column and bottom row [0,0,0,1]. An all-zero bottom row would be singular and would not preserve the homogeneous point coordinate.',
        'o4': 'The lecture’s Z-rotation definition is 3×3. Its pure-rotation homogeneous embedding is [Rz,0;0,1], encoding the same spatial rotation without translation.'},
    why='The source presents the same pure Z rotation in two representations: a 3×3 rotation matrix and its 4×4 homogeneous embedding. The extra coordinate is not an extra spatial dimension.',
    steps=['Compare the displayed 4×4 T_R with the 3×3 Z-rotation matrix on physical page 224.',
           'The 4×4 form has Rz in its upper-left block, zero translation, and bottom row [0,0,0,1].',
           'The rotz(t) sample line is rotation-only notation; it does not explicitly build the 4×4 block matrix.'],
    examTraps=['A 4×4 representation of 3D pose does not introduce a fourth physical axis.',
               'A zero translation column does not permit multiplying a 4×4 matrix by a 3-component column.'])
revise('P0233-Q01', formulas=formula(
    '^A P=Rz(30°)^B P+[10,5,0]^T',
    {'^A P': 'Position of point P relative to A, expressed as a 3×1 A-coordinate column',
     '^B P': 'Position of the same point relative to B; [3,7,0]^T in this example',
     'Rz(30°)': '^A_B R, the right-hand +30° rotation about Z converting B components into A components',
     '[10,5,0]^T': '^A P_BORG, the B-origin position measured from the A origin and expressed in A',
     'T (superscript on a vector)': 'Transpose, used to display the listed entries as a column'},
    {'^A P, ^B P, [10,5,0]^T': 'common length units; the source does not specify metres',
     '30°': 'degrees', 'Rz(30°)': 'dimensionless'},
    ['Column-coordinate convention with the origin offset already expressed in A.',
     'Use exact sin(30°)=1/2 and cos(30°)=sqrt(3)/2, then round final coordinates to three decimals.']))
revise('P0233-Q03', formulas=formula(
    'p_inverse=−R^T p',
    {'p_inverse': '^B P_AORG, the 3×1 position of the A origin relative to B, expressed in B',
     'R': '^A_B R=Rz(30°), the 3×3 rotation converting B components to A components',
     'R^T': '^B_A R=Rz(−30°), the reverse rotation converting A components to B components',
     'p': '^A P_BORG=[10,5,0]^T, the B-origin position relative to A, expressed in A'},
    {'p, p_inverse': 'common length units; the source does not specify metres',
     'R, R^T': 'dimensionless', '30°': 'degrees'},
    ['R is an exact proper rotation, so its inverse equals its transpose.',
     'Negate the displacement and express it in B, not merely negate its A-coordinate entries.',
     'Use exact trigonometric values and round only the final coordinates to three decimals.']))
revise('P0233-Q04', difficulty='medium',
    options={
        'o1': 'The printed numeric entries still satisfy R^T R=I exactly, because 0.866 is exactly cos30°',
        'o2': 'Normalizing the rounded columns is guaranteed to recover the exact intended 30° angle',
        'o3': 'The discrepancy can be rounding error; the exact trigonometric matrix remains a proper rotation',
        'o4': 'For this rounded numeric matrix, its transpose must still equal its inverse exactly without any tolerance'},
    reasons={
        'o1': '0.866 is a rounded approximation to sqrt(3)/2. Using the printed numbers literally gives 0.866²+0.5²=0.999956, not 1.',
        'o2': 'Normalizing can restore unit column lengths in this special matrix, but it does not restore the exact original angle: the rounded sine/cosine ratio has already changed slightly.',
        'o3': 'The residual follows directly from rounding cos30°. The exact sine/cosine matrix satisfies orthogonality and determinant +1.',
        'o4': 'The literal rounded matrix is not exactly orthogonal, so its transpose and true inverse differ slightly. Exact rotation identities must not be asserted without accounting for finite precision.'},
    why='The intended geometric rotation and its finite-precision printed approximation are different objects. A small residual here is explained by rounding; exact orthogonality belongs to the exact trigonometric matrix.',
    steps=['For the literal printed values, calculate 0.866²+0.5²=0.999956.',
           'For the exact values, (sqrt(3)/2)²+(1/2)²=1.',
           'Distinguish a numerical tolerance check from the exact identity R^T R=I.'],
    misconceptions=['Treating an approximate decimal as an exact trigonometric value.',
                    'Assuming normalization necessarily recovers the precise angle before rounding.'],
    examTraps=['State whether a calculation uses exact trigonometry or literal printed decimals.'])
q = revise('P0238-Q01', conflictResolution={
    'status': 'derived-correction-pending-independent-review',
    'sourceClaim': 'Physical page 238 labels the first rotation local X before R1=rotz(alpha), and the final rotation local Z before R_euler=R2 @ rotx(gamma). Those two comments contradict the executable calls.',
    'basis': 'The page 237 Z-Y-X derivation specifies first local Z, then local Y, then local X and the product Rz(alpha)Ry(beta)Rx(gamma). Page 238 uses exactly those calls; their alpha=60°, beta=30°, gamma=45° product reproduces the displayed output matrix.',
    'method': 'Preserve the printed comment mismatch as explicit evidence. Keep the executable calls and product unchanged; correct only the two axis labels to local Z first and local X last. No claim is made that the source PDF itself has been edited.'})
q['citations'][1]['role'] = 'premise'
revise('P0238-Q03', difficulty='medium')
revise('P0239-Q01', difficulty='medium')
revise('P0239-Q07', difficulty='hard',
    options={
        'o1': 'Only alpha+gamma remains, so equal and opposite yaw/roll changes preserve the matrix',
        'o2': 'The remaining entries depend on alpha−gamma, so many yaw/roll pairs give the same matrix',
        'o3': 'Yaw and roll remain separately unique because Atan2(r21,r11) and Atan2(r32,r33) still recover both',
        'o4': 'Only alpha remains, because the preceding 90° pitch makes the final Rx(gamma) ineffective'},
    reasons={
        'o1': 'For the stated +90° pitch the surviving combination is alpha−gamma. The alpha+gamma dependence belongs to the opposite −90° pitch branch under this convention.',
        'o2': 'Substituting beta=+90° into Rz(alpha)Ry(beta)Rx(gamma) leaves sine and cosine of alpha−gamma. Adding the same amount to alpha and gamma preserves their difference.',
        'o3': 'At this singular pitch r11=r21=r32=r33=0. These Atan2 pairs do not identify separate angles, and the nonsingular formulas divide by cos(beta)=0.',
        'o4': 'Roll still changes the matrix through alpha−gamma. It is inseparable from yaw, not physically ineffective.'},
    why='At beta=+90°, the matrix retains only the yaw-minus-roll combination. It is not independent of roll, and the opposite singular pitch has a different angle-combination sign.',
    steps=['Set cos(beta)=0 and sin(beta)=1 in the expanded Z-Y-X matrix.',
           'Obtain R=[[0,−sin(alpha−gamma),cos(alpha−gamma)],[0,cos(alpha−gamma),sin(alpha−gamma)],[−1,0,0]].',
           'Replacing (alpha,gamma) with (alpha+delta,gamma+delta) preserves every entry; separate recovery is therefore nonunique.'],
    examTraps=['Keep the +90° and −90° pitch branches distinct.',
               'An unidentifiable separate angle is not the same as an angle having no effect.'])
revise('P0239-Q08', difficulty='medium',
    options={
        'o1': 'Three unit-column constraints are the only restrictions, leaving six continuous orientation parameters',
        'o2': 'Orthonormality supplies six independent local constraints, leaving three continuous degrees of freedom',
        'o3': 'Six orthonormality constraints plus det(R)=+1 remove seven continuous parameters, leaving two',
        'o4': 'All nine entries of R^T R=I are independent constraints, leaving no continuous orientation parameters'},
    reasons={
        'o1': 'Unit lengths alone are insufficient. The three distinct pairs of columns must also be perpendicular, supplying three further constraints.',
        'o2': 'Three unit-column conditions and three pairwise orthogonality conditions impose six independent local constraints. Thus 9−6=3; det(R)=+1 selects proper rather than improper orthogonal matrices.',
        'o3': 'On the orthogonal-matrix set the determinant is already either +1 or −1. Choosing +1 selects a component; it does not remove another continuous degree of freedom.',
        'o4': 'R^T R is symmetric, so its off-diagonal equations occur in duplicate pairs. There are six independent conditions, not nine.'},
    why='A 3×3 proper rotation stores nine numbers but only three are locally independent. Column normalization and mutual orthogonality provide six independent constraints; the determinant sign is a discrete component choice.',
    steps=['Count three column unit-length equations.', 'Count three distinct column-pair orthogonality equations.',
           'Subtract six independent local constraints from nine entries to obtain three continuous degrees of freedom.',
           'Choose determinant +1 to exclude reflections without removing another continuous parameter.'],
    examTraps=['Do not count symmetric off-diagonal equations twice or the determinant sign as an extra continuous constraint.'])
revise('P0239-Q09', difficulty='hard')
revise('P0240-Q03',
    stem='In the lecture’s representations, p is a 3-component Cartesian position vector, R is a 3×3 proper rotation matrix, and T is a 4×4 rigid homogeneous transform. Which matching of these objects to their spatial roles is correct?',
    options={
        'o1': 'p: combined pose; R: orientation; T: position only',
        'o2': 'p: orientation; R: position; T: combined pose',
        'o3': 'p: position; R: combined pose; T: orientation only',
        'o4': 'p: position; R: orientation; T: combined pose'},
    reasons={
        'o1': 'The stated Cartesian p gives no orientation, so it is not full pose. T contains both the rotation block and translation column, not position alone.',
        'o2': 'This swaps the roles of the stated Cartesian position vector and rotation matrix. A three-angle orientation parameterization would be a different object from p.',
        'o3': 'R contains orientation but no independent origin translation. T combines that orientation with a translation, so it is not orientation only.',
        'o4': 'The lecture uses Cartesian vectors for position, rotation matrices for orientation, and homogeneous transforms to combine both.'},
    why='The meaning depends on the defined object, not only its number of entries: the stated Cartesian vector describes position, the rotation matrix describes orientation, and the homogeneous transform combines them.',
    examTraps=['Do not confuse a Cartesian position vector with a separate three-angle orientation parameterization.'])

# New direct coverage for the p234 existence claim; existing approved Q01 is untouched.
new = copy.deepcopy(before['W02-L06-P0234-Q01'])
new.update(id='W02-L06-P0234-Q02', version=1, status='draft', authorId=AUTHOR, reviewIds=[],
    stem='A rigid body starts aligned with a reference frame and must reach an arbitrary target orientation while its reference point stays fixed. What does the lecture’s three-successive-rotation result guarantee?',
    type='scenario', difficulty='medium', cognitiveSkill='conceptual',
    assumptions=['Use ideal rigid-body rotations without joint limits or collisions.',
                 'Use a valid specified sequence such as fixed X-Y-Z; arbitrary does not mean repeatedly using only one axis.'],
    options=[
        {'id': 'o3', 'text': 'Three rotations about the same fixed Z axis suffice for every target orientation'},
        {'id': 'o1', 'text': 'Two rotations, one about fixed X and one about fixed Y, suffice for every target orientation'},
        {'id': 'o4', 'text': 'Three successive rotations in a suitable coordinate-axis sequence can reach the target with appropriately chosen angles'},
        {'id': 'o2', 'text': 'A fixed X-Y-Z sequence can reach only small orientation changes; larger changes require a different representation'}],
    correctOptionIds=['o4'])
new['citations'] = [copy.deepcopy(before['W02-L06-P0234-Q01']['citations'][0]),
                    copy.deepcopy(before['W02-L06-P0235-Q01']['citations'][0])]
new['citations'][0].update(locator='Physical page 234, printed slide 23: third main bullet stating the three-successive-rotation result',
    evidenceText='Any arbitrary orientation in three-dimensional space can be achieved through three successive rotations about coordinate axes.', role='explicit')
new['citations'][1]['role'] = 'premise'
new['solution'] = {
    'justification': 'The source states that three successive coordinate-axis rotations can represent any target orientation. Fixed X-Y-Z is one suitable convention shown next. This is a sufficiency claim: special targets can use zero angles, and the claim does not promise a unique triple.',
    'optionExplanations': {
        'o1': 'Two rotations about these specified fixed axes do not cover every 3D orientation; they omit a general third rotational degree of freedom.',
        'o2': 'The lecture gives full sine/cosine rotation matrices, not a small-angle approximation. The valid three-axis representation is not limited to small changes.',
        'o3': 'Rotations about the same fixed Z axis combine into another Z-axis rotation. They cannot reach a target that tilts the Z axis.',
        'o4': 'This is the stated existence result. A suitable sequence such as fixed X-Y-Z, with appropriately chosen angles, can represent the target orientation.'},
    'steps': [], 'formulas': [],
    'simpleExplanation': 'Three suitably chosen axis rotations are enough to set an arbitrary 3D orientation. This does not say that any three axis choices work, that every angle must be nonzero, or that the angle triple is unique.',
    'memoryAid': None,
    'misconceptions': ['Confusing a suitable three-axis sequence with three repetitions about one axis.',
                       'Assuming a full finite-rotation formula is only a small-angle model.'],
    'examTraps': ['Sufficiency does not mean exactly three nonzero actions are necessary for every special target.'],
    'prerequisiteConceptIds': ['W02-L06-C-orientation']}
new['notes'] = 'New question addressing the independent coverage gap on physical page 234; requires first independent blind review.'
batch['questions'].append(new)
batch['questions'].sort(key=lambda q: q['id'])
by[new['id']] = new
concept = next(c for c in batch['concepts'] if c['id'] == 'W02-L06-C-angle-conventions')
concept['questionIds'].append(new['id'])
concept['examinationAngles'].append('Sufficiency of a suitable three-coordinate-axis sequence for arbitrary orientation, distinct from repetition about one axis or small-angle restrictions.')
concept['description'] = 'A suitable sequence of three coordinate-axis rotations can represent arbitrary orientation. Angles need axis, order and fixed/moving conventions; three parameters do not imply global uniqueness.'
concept['coverageNotes'] = 'The p234 arbitrary-orientation claim now has direct draft question P0234-Q02, in addition to the convention question. New and revised items still require independent review.'

assert changed == expected
assert all(by[qid] == before[qid] for qid in approved), 'An approved question changed'
assert all(question_hash(by[qid]) == question_hash(before[qid]) for qid in approved)
assert all(by[qid]['correctOptionIds'] == before[qid]['correctOptionIds'] for qid in changed)
for q in batch['questions']:
    assert len(q['options']) == 4 and len({o['text'] for o in q['options']}) == 4
    assert {o['id'] for o in q['options']} == set(q['solution']['optionExplanations'])
    assert len(q['correctOptionIds']) == 1 if q['selectionMode'] == 'single' else len(q['correctOptionIds']) >= 1
    if q['id'] in changed or q['id'] == new['id']:
        assert q['status'] == 'draft' and not q['reviewIds']
assert len(batch['questions']) == 78
# Stable independent review input excludes all keys and solutions.
packet = [{k: q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
          for q in batch['questions'] if q['id'] in changed or q['id'] == new['id']]
current = json.loads(TARGET.read_text())
assert current == original or current == batch, 'External batch change detected; reconcile before writing'
TARGET.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'audits/blind-W02-L06-v2.json').write_text(json.dumps(packet, ensure_ascii=False, indent=2) + '\n')
report = {
    'batchId': 'W02-L06', 'revisionAuthorId': AUTHOR,
    'revisedQuestionCount': len(changed), 'newQuestionCount': 1,
    'approvedQuestionHashesPreserved': len(approved), 'approvedQuestionObjectsPreservedExactly': True,
    'answerSetsUnchangedForAllRevisions': True,
    'historyPath': str(HISTORY.relative_to(ROOT)), 'historySha256': hashlib.sha256(HISTORY.read_bytes()).hexdigest(),
    'blindPacketPath': 'audits/blind-W02-L06-v2.json',
    'newQuestion': {'id': new['id'], 'version': 1, 'sha256': question_hash(new), 'reason': 'Direct coverage of the p234 three-successive-rotation existence result'},
    'sourcePixelsReinspected': [217,221,222,223,224,226,227,228,229,230,231,233,234,235,237,238,239,240],
    'sourceInspectionMethod': 'Actual faithful 1800×1013 page renders viewed at original detail; no text-only inspection claim.',
    'revisions': [{'questionId': qid, 'oldVersion': 1, 'newVersion': 2,
                   'oldSha256': question_hash(before[qid]), 'newSha256': question_hash(by[qid]),
                   'reviewFindingsAddressed': (['Integration validator requires explicit resolution metadata for the preserved code-comment conflict.'] if qid == CONFLICT_ITEM else next(r['findings'] for r in reviews if r['questionId'] == qid))}
                  for qid in sorted(changed)],
    'reviewStatus': 'Revised items require independent re-review; the new item requires first blind review. Author does not claim independent approval.'}
(ROOT / 'audits/W02-L06-v2-revision-summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('revisedQuestionCount','newQuestionCount','approvedQuestionHashesPreserved','blindPacketPath','reviewStatus')}, indent=2))
