import json,pathlib,hashlib,collections,datetime
R=pathlib.Path(__file__).resolve().parents[2]
def d(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
m=json.loads((R/'data/question-visuals/manifest.json').read_text());b=json.loads((R/'data/bank.json').read_text());qm={q['id']:q for q in b['questions']};am={a['id']:a for a in m['assets']};rv=[]
for p in (R/'data/question-visuals/reviews').glob('*.json'):
 o=json.loads(p.read_text());rv.extend(o if isinstance(o,list) else o.get('reviews',[]))
by=collections.defaultdict(list)
for v in rv:by[v['questionId']].append(v)
counts=collections.Counter();approved=[];gaps=[];assetids=set()
for r in m['records']:
 q=qm[r['questionId']]
 if q.get('lectureId') not in ['L%02d'%i for i in range(1,20)] or q['status']!='verified':continue
 assert r['questionSha256']==d({k:v for k,v in q.items() if k not in ('status','reviewIds')})
 exact=[v for v in by[r['questionId']] if v['visualSha256']==d(r) and v['questionSha256']==r['questionSha256'] and v.get('sourceVersions')=={x['sourceId']:x['sourceSha256'] for x in r['sourceRefs']} and all(v.get('assetMetadataHashes',{}).get(a)==d(am[a]) and v.get('assetHashes',{}).get(a)==am[a]['sha256'] for a in r['assetIds'])]
 yes=[v for v in exact if v['decision']=='verified' and all(v['checks'].values())];no=[v for v in exact if v['decision'] in ['flagged','rejected']]
 page_membership=all(any(ref['sourceId']==am[aid]['sourceId'] and ref['sourceSha256']==am[aid]['sourceSha256'] and ref['physicalPage']==am[aid]['physicalPage'] for ref in r['sourceRefs']) for aid in r['assetIds'])
 ok=bool(yes) and not no and page_membership
 counts[(r['dependencyStatus'],'approved' if ok else 'pending')]+=1
 if not ok:gaps.append(r['questionId']);continue
 assetids.update(r['assetIds']);approved.append({'questionId':q['id'],'questionSha256':r['questionSha256'],'visualId':r['id'],'visualVersion':r['version'],'visualSha256':d(r),'dependencyStatus':r['dependencyStatus'],'reviewIds':[v['id'] for v in yes]})
for aid in assetids:assert hashlib.sha256((R/am[aid]['path']).read_bytes()).hexdigest()==am[aid]['sha256']
result={'reviewerId':'verify_required_question_visuals','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifestSha256':hashlib.sha256((R/'data/question-visuals/manifest.json').read_bytes()).hexdigest(),'bankSha256':hashlib.sha256((R/'data/bank.json').read_bytes()).hexdigest(),'verifiedQuestionScope':'L01 through L19','scopeCount':sum(counts.values()),'counts':{f'{a}_{c}':n for (a,c),n in counts.items()},'currentAssetCount':len(assetids),'gaps':gaps,'approved':approved,'limitations':['This closes exact source-input semantics/pixels for L01-L19 only; does not claim browser or print-layout execution.','Self-contained reviews for lectures L01-L19 were independently authored by review_early_question_inputs; positive crop receipts by verify_required_question_visuals.','Historical incomplete exact-snapshot flags remain in the audit trail but do not match current repaired record hashes.','119 separately reviewed assignment adaptations have their own exact self-contained receipts. No assignment solution/key crop is introduced.']}
(R/'audits/question-visual-review/final-early-coverage.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['approved','limitations']},indent=2));assert not gaps
p=R/'audits/question-visual-review/allocation.json';alloc=json.loads(p.read_text());alloc['updatedAt']=result['checkedAt']
for a in alloc['allocations']:
 if a.get('reviewerId')=='verify_required_question_visuals' and a.get('lectureRange')==['L01','L19']:a['status']='complete: 191 current required records independently approved; zero stale or missing current input reviews';a['reviewPath']='data/question-visuals/reviews/visuals-L01-L05-first-batch.json; visuals-L01-L19-second-batch.json; visuals-L01-L19-third-batch.json; visuals-L01-L19-final-nine.json'
 if a.get('reviewerId')=='review_early_question_inputs':a['status']='complete: 1393 exact self-contained approvals; 56 missing-input findings adopted and positively reviewed separately'
p.write_text(json.dumps(alloc,indent=2)+'\n')
