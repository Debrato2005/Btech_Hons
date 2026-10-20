import sys,json,pathlib,hashlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3]
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def qhash(q):return digest({k:v for k,v in q.items() if k not in ('status','reviewIds')})
m=json.load(open(ROOT/'data/question-visuals/manifest.json')); qs={q['id']:q for p in (ROOT/'data/question-batches').glob('*.json') for q in json.load(open(p))['questions']}
lec=sys.argv[1];start=int(sys.argv[2]) if len(sys.argv)>2 else 0; end=int(sys.argv[3]) if len(sys.argv)>3 else 999
rs=sorted((r for r in m['records'] if r['dependencyStatus']=='self_contained' and qs[r['questionId']]['lectureId']==lec),key=lambda r:r['questionId'])
selected=rs[start:end]; audit={'lecture':lec,'range':[start,min(end,len(rs))],'total':len(rs),'readStatus':'displayed_pending_adjudication','records':[{'questionId':r['questionId'],'questionSha256':qhash(qs[r['questionId']]),'visualSha256':digest(r),'record':r} for r in selected]}
(ROOT/f'audits/question-visual-review/early-inputs/{lec}-{start:03}-{min(end,len(rs)):03}.json').write_text(json.dumps(audit,indent=2))
print(lec, 'total',len(rs),'range',start,min(end,len(rs)))
for r in selected:
 q=qs[r['questionId']];print('\n'+q['id']+' ['+q['selectionMode']+'] '+q['stem']);print(' | '.join(o['text'] for o in q['options'])); print('Assumptions: '+json.dumps(q.get('assumptions',[]),ensure_ascii=False))
