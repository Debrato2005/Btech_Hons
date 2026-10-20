"""Deterministic, read-only-input checks for this audit closure packet."""
import hashlib,itertools,json,pathlib,sys,datetime
R=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,canonical_json,schema_errors
B=json.loads((R/'data/bank.json').read_text());Q={q['id']:q for q in B['questions']};SC=json.loads((R/'data/schema.bank.json').read_text());draft=json.loads((D/'qualified-drafts-v1.json').read_text());neutral=json.loads((D/'neutral-packet-v1.json').read_text());freeze=json.loads((D/'freeze-manifest-v1.json').read_text());ad=json.loads((R/'audits/lecture-ledger-challenge/L02-L05-independent-adjudication.json').read_text());amap={a['conceptId']:a for a in ad['decisions']}
def sha(o):return hashlib.sha256(canonical_json(o).encode()).hexdigest()
def fsha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];errors=[]
def check(name,value):checks.append({'check':name,'passed':bool(value)});errors.extend([] if value else [name])
check('six questions, distinct original concepts',len(draft['questions'])==len({q['id'] for q in draft['questions']})==len({q['conceptIds'][0] for q in draft['questions']})==6)
check('draft file matches freeze',fsha(D/'qualified-drafts-v1.json')==freeze['draftFileSha256'])
check('neutral file matches freeze',fsha(D/'neutral-packet-v1.json')==freeze['neutralFileSha256'])
check('adjudication remains hash bound',fsha(R/'audits/lecture-ledger-challenge/L02-L05-independent-adjudication.json')==freeze['adjudicationSha256'])
permutationChecks=0
for q,n,bind in zip(draft['questions'],neutral['questions'],freeze['questionBindings']):
 pre=q['id']+': '
 check(pre+'question and whole object hashes',question_hash(q)==bind['questionSha256'] and sha(q)==bind['wholeObjectSha256'] and sha(n)==bind['neutralObjectSha256'])
 check(pre+'valid question schema',not schema_errors(q,SC['$defs']['question'],root=SC))
 check(pre+'no author self-approval',q['status']=='draft' and q['reviewIds']==[])
 check(pre+'original caveat and evidence scope exact',q['conflictResolution']['qualification']==amap[q['conceptIds'][0]]['reason'] and q['primaryEvidence']['scope']==amap[q['conceptIds'][0]]['primaryEvidenceScope'])
 check(pre+'one rationale per option',set(q['solution']['optionExplanations'])=={o['id'] for o in q['options']} and all(q['solution']['optionExplanations'].values()))
 check(pre+'neutral fields restricted',set(n)=={'id','version','stem','selectionMode','assumptions','options','citations','sourceEvidence'})
 check(pre+'neutral authored fields exact',all(n[k]==q[k] for k in ['id','version','stem','selectionMode','assumptions','options','citations']))
 check(pre+'preview unchanged',fsha(R/n['sourceEvidence']['previewPath'])==n['sourceEvidence']['previewSha256'])
 check(pre+'selection cardinality valid',len(q['correctOptionIds'])==1 if q['selectionMode']=='single' else len(q['correctOptionIds'])>1)
 check(pre+'no duplicate stem in current bank',all(q['stem']!=old['stem'] for old in B['questions']))
 for order in itertools.permutations(q['options']):
  assert {o['id'] for o in order if o['id'] in q['correctOptionIds']}==set(q['correctOptionIds']);permutationChecks+=1
accepted=freeze['acceptedQuestionPreservation'];check('all baseline accepted whole objects unchanged',all(b['id'] in Q and sha(Q[b['id']])==b['wholeObjectSha256'] for b in accepted))
check('all baseline correctness-sensitive hashes unchanged',all(question_hash(Q[b['id']])==b['questionSha256'] for b in accepted))
alias=json.loads((D/'L30-durable-coverage-crosslinks.json').read_text());check('eight aliases preserved',len(alias['items'])==8)
for item in alias['items']:
 for bind in item['verifiedQuestionCrosslinks']:
  check(item['legacyConceptId']+'/'+bind['id']+' crosslink current',sha(Q[bind['id']])==bind['wholeObjectSha256'] and question_hash(Q[bind['id']])==bind['questionSha256'])
term=next(a for a in alias['items'] if a['legacyConceptId']=='learning-observed-P0905-C03');adapt=next(b for b in term['verifiedQuestionCrosslinks'] if b['id']=='W06-L30-Q056')
check('terminal omission retained without fabricated p905 citation',bool(term['residualSourceQualification']) and adapt['actualCitedPhysicalPages']==[914] and adapt['directlyCitesContextPage'] is False)
quote=json.loads((D/'L02-summary-quote-disposition.json').read_text());check('only quote excluded with all seven summary rows retained',quote['substantiveRowCount']==len(quote['substantiveRowsPreserved'])==7 and quote['pageRemainsExaminable'] is True)
for row in quote['substantiveRowsPreserved']:
 for bind in row['semanticQuestionCrosslinks']:check('summary row '+row['row']+' hash current',sha(Q[bind['id']])==bind['wholeObjectSha256'])
ledger=json.loads((D/'full-lecture-ledger-challenge.json').read_text());check('full lecture ledger covers 1953 pages',ledger['lecturePages']==1953 and len(json.loads((D/'lecture-page-accountability.json').read_text()))==1953)
check('inspection-batch IDs reconcile',not ledger['bankSlidesAbsentFromInspectionBatches'] and not ledger['inspectionBatchSlidesMissingFromBank'])
check('current review gate unchanged',not ledger['reviewGateStatusChanges'])
result={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pass' if not errors else 'fail','checkCount':len(checks),'failedChecks':errors,'optionPermutationsChecked':permutationChecks,'baselineAcceptedWholeObjectsPreserved':len(accepted),'currentBankVersion':B['bankVersion'],'currentBankSha256':fsha(R/'data/bank.json'),'checks':checks,'limitations':['Deterministic checks do not establish independent question correctness or actual browser behavior.','This author has not approved the new questions.','No canonical source, question or app file was changed.']}
(D/'deterministic-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2));raise SystemExit(bool(errors))
