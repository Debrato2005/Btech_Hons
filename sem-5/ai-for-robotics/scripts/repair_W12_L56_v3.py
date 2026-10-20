from pathlib import Path
import json,hashlib,copy,datetime,sys,re
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from validate import validate_bank
B='W12-L56';ident='W12-L56-P1789-Q04';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads((R/p).read_text())
def dump(p,d):(R/p).parent.mkdir(parents=True,exist_ok=True);(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sh(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qh(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
assert not (R/f'audits/blind-{B}-v3.json').exists()
b=read(f'data/question-batches/{B}.json');s=read('audits/W12-L56-v2-independent-review-summary.json');accepted={**s['acceptedQuestionHashes'],**s['preservedAcceptedQuestionHashes']};assert len(accepted)==67
qm={q['id']:q for q in b['questions']};assert all(qh(qm[k])==v for k,v in accepted.items());q=qm[ident];old=copy.deepcopy(q);assert q['version']==2
dump('audits/archive/W12-L56-v2-before-v3/question.json',old)
q['version']=3;q['status']='draft';q['reviewIds']=[];q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+['complete_robotics_python_coverage:L56-v3-metadata-repair']))
q['conflictResolution']['questionVersion']=3;q['conflictResolution']['sourceSha256']='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
assert all(qh(qm[k])==v for k,v in accepted.items())
new=copy.deepcopy(q);prev=copy.deepcopy(old)
for k in ['version','status','reviewIds','revisionAuthors']:new.pop(k,None);prev.pop(k,None)
for k in ['questionVersion','sourceSha256']:new['conflictResolution'].pop(k);prev['conflictResolution'].pop(k)
assert new==prev,'Unexpected substantive edit'
assert q['conflictResolution']['sourceSha256']==q['citations'][0]['sourceSha256']
invalid=[]
def scan(x,path=''):
 if isinstance(x,dict):
  for k,v in x.items():
   if k.lower().endswith('sha256')and isinstance(v,str)and not re.fullmatch('[0-9a-f]{64}',v):invalid.append(path+'.'+k)
   scan(v,path+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):scan(v,path+f'[{i}]')
scan(b);assert not invalid,invalid
bank=read('data/bank.json');bank['questions']=[z for z in bank['questions']if z['id']!=ident]+[copy.deepcopy(q)];v=validate_bank(bank,R,check_files=False);assert v['valid'],v['errors']
dump(f'data/question-batches/{B}.json',b)
z={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','cognitiveSkill','week','lectureId','topic','subtopic','assumptions','options']};z['citations']=[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]
for c in z['citations']:c['locator']=f"Lecture physical page {c['physicalPage']}: printed Realtime interaction discussion."
if q.get('externalSources'):z['externalSources']=[{k:v for k,v in e.items()if k in ['title','url','version']}for e in q['externalSources']]
dump(f'audits/blind-{B}-v3.json',{'batchId':B+'-v3','questions':[z]})
dump(f'audits/blind-binding-{B}-v3.json',{'packetSha256':sh(f'audits/blind-{B}-v3.json'),'questions':[{'id':ident,'version':3,'sha256':qh(q)}]})
dump(f'audits/{B}-v3-author-checks.json',{'checkedAt':now,'role':'Author metadata checks, not independent review','checks':['All 67 accepted hashes preserved','Only version/revision attribution and conflict binding metadata differ','Conflict source SHA equals exact lecture citation SHA','All nested SHA256 fields in batch have exact 64 lowercase hexadecimal characters','Question stem, options, intended key, solution and policy are exactly unchanged','In-memory structural validation passed'],'acceptedQuestionHashes':accepted,'currentQuestionHash':qh(q),'validation':v})
dump(f'audits/{B}-v3-repair-manifest.json',{'frozenAt':now,'repairedCount':1,'preservedAcceptedCount':67,'packetSha256':sh(f'audits/blind-{B}-v3.json'),'bindingSha256':sh(f'audits/blind-binding-{B}-v3.json'),'pendingIndependentReview':True})
(R/'audits/handoffs/W12-L56-repair.md').write_text('L56 v3: one metadata-only repair to P1789-Q04 restores exact conflictResolution source SHA and increments version/binding. All 67 accepted objects preserved. No stem/options/solution/policy changes. Six author metadata checks and in-memory validation pass. Packet audits/blind-W12-L56-v3.json; binding audits/blind-binding-W12-L56-v3.json. Independent re-review pending. Do not rerun old author/repair scripts.\n')
print(sh(f'audits/blind-{B}-v3.json'))
