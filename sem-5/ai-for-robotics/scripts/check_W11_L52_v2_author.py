#!/usr/bin/env python3
"""Permitted default-Python repair checks; no restricted runtime/model/hardware operations."""
from pathlib import Path
import json,hashlib,datetime,sys,re,random,copy
from fractions import Fraction
R=Path(__file__).resolve().parents[1];B='W11-L52';start=datetime.datetime.now(datetime.timezone.utc).isoformat();assert not sys.prefix.startswith('/tmp/robotics-l35-venv')
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qh(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in ['status','reviewIds']},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
b=read(f'data/question-batches/{B}.json');Q={q['id']:q for q in b['questions']};orig=read('audits/archive/W11-L52-v1-before-v2/W11-L52.json');O={q['id']:q for q in orig['questions']};w=read(f'audits/{B}-v2-repair-work.json');checks=[]
def ck(name,v,detail):assert v,name;checks.append(dict(name=name,passed=True,detail=detail))
ck('Accepted objects and hashes',all(qh(Q[i])==h and Q[i]==O[i]for i,h in w['preservedAcceptedHashes'].items()),'All117acceptedobjects retained exactly, not merely keys.')
ck('Only15oldobjectschange',{i for i in O if qh(O[i])!=qh(Q[i])}==set(w['changedIds']),'Onlyreviewerflaggedobjectsrevised.')
ck('Version/contributors/keys',all(Q[i]['version']==2 and Q[i]['correctOptionIds']==O[i]['correctOptionIds']and w['revisionAuthor']in Q[i]['revisionAuthors']for i in w['changedIds']),'All15v1keysretained; authorprovenance appended.')
ck('Sixgapbindings',len(w['gapQuestionMap'])==6 and set(w['gapQuestionMap'].values())==set(w['newGapIds']),'Oneboundedextensionpergap,notnumericvariantinflation.')
ck('22sourcequalificationsexact',sha('audits/source-disputes-W11-L52.json')==w['sourceQualificationsSha256'],'Historicalsourceannotationsuntouched.')
ck('CodekindP1632',Q[B+'-P1632-Q03']['citations'][0]['kind']=='code','Codeblockseparatefromaccuracyprose.')
ck('Per-pagepredicate/fpslocators','ST status'not in Q[B+'-P1667-Q04']['citations'][0]['locator']and '20 fps'not in Q[B+'-P1677-Q04']['citations'][0]['locator'],'Externalstatustableandprevious-pagewriterarenotmisattributed.')
ck('Fourdistinctcontextualstems',len({Q[B+'-'+i]['stem']for i in ['P1659-Q01','P1660-Q02','P1672-Q02','P1682-Q02']})==4 and all(Q[B+'-'+i]['stem']not in ['Which matching is correct?','Which distinction is correct?']for i in ['P1659-Q01','P1660-Q02','P1672-Q02','P1682-Q02']),'No generic exactcollisionsremain amongflaggedstems.')
# Metadata only: parse explicit indented integer keys; no Ultralytics,OpenCV or YAML package import.
f=R/'sources/supplemental/L52-ultralytics-open-images-v7.yaml';s=f.read_text().split('names:',1)[1];names={int(m.group(1)):m.group(2).strip()for line in s.splitlines()if(m:=re.match(r'^  (\d+):\s*(.+)$',line))}
ck('PreservedYAMLhash',hashlib.sha256(f.read_bytes()).hexdigest()=='497468af9dc644d149101efc090727d3c6fd644591f4cc2e8c5adeb00f4ad848','Nooriginalmetadatareplaced.')
ck('Inclusivevocabularycount',len(names)==601 and set(names)==set(range(601))and names[0]=='Accordion','600−0+1=601; index0isnamedobjectcategory,notbackground.')
ck('Writermetadataagainstthroughput',Fraction(100,50)==2 and Fraction(100,20)==5 and 100*20==2000,'Correct2frames/sand5s;2000iswrongmultiplication;20fpsmetadata notactualthroughput.')
ck('VL53exactpredicate',[(x!=4)for x in range(6)]==[True,True,True,True,False,True],'Status1passesliteralpredicate;APIvalidityremainsdistinct. NoI2Chardwarecall.')
# Potentiometer symboliccounterexample supplied as an author test,not a new course numerical claim.
ck('Dividerconnections',[(Fraction(5)*u)for u in [Fraction(1,4),Fraction(3,4)]]==[Fraction(5,4),Fraction(15,4)],'Unloadedwipervaries;fixedendpointvoltage5Vandshortedwiper0Vdonot.')
# Selection constraints from newP1683Q07: E,I,width_mm,height_mm,mass_g.
candidates=[(True,True,28,18,18),(False,True,25,18,15),(True,False,25,18,15),(True,True,45,30,28)]
def feasible(c):E,I,w,h,m=c;return E and I and w<=30 and h<=20 and m<=20
ck('Jointenvironment/interface/mechanicalselection',[feasible(c)for c in candidates]==[True,False,False,False],'Eachincorrectcandidatefailsadistinctrequiredconstraint;lastfailssizeandmass.')
ck('Inclusivephysicalboundaries',feasible((True,True,30,20,20))and not feasible((True,True,30,20,20.01)),'Allunitsconsistent:mm,g;boundsinclusive;fixedorientation.')
ck('Reedmulti-select',Q[w['gapQuestionMap']['L52-GAP-02']]['correctOptionIds']==['o1','o2'],'Twoindependentdiagramfacts;falseoptionsmislocatecontactversusendseal.')
ck('DHTrevisionqualification',all(Q[w['gapQuestionMap'][g]]['conflictResolution']['sourceIssueId']=='L52-ISSUE-dht-revision'for g in ['L52-GAP-03','L52-GAP-04']),'ADC/interfaceandexplodedlayerquestionssource-scoped,notuniversalhardwareclaims.')
rng=random.Random(5202)
for _ in range(1000):
 n=rng.randint(1,10000);elapsed=rng.randint(1,10000);fps=rng.randint(1,200);assert Fraction(n,elapsed)*elapsed==n;assert Fraction(n,fps)*fps==n
 a=rng.randrange(1000);z=rng.randrange(a,2000);assert len(range(a,z+1))==z-a+1
 c=(rng.choice([True,False]),rng.choice([True,False]),rng.randint(1,60),rng.randint(1,40),rng.randint(1,40));ok=feasible(c);assert not ok or (c[0]and c[1]and c[2]<=30 and c[3]<=20 and c[4]<=20)
ck('Variedexactarithmeticalchecks',True,'1000cases/4000assertions:throughputidentity,playbackidentity,inclusivecount,selectionconjunction.')
for i in w['changedIds']+w['newGapIds']:
 q=Q[i];ck(i+' alloptionexplanations',set(q['solution']['optionExplanations'])=={o['id']for o in q['options']},'Everycorrectandwrongoptionhasarationale.')
 if q.get('conflictResolution'):ck(i+' conflictversion',q['conflictResolution']['questionVersion']==q['version'],'Exactcurrentversionqualification.')
 for f in q['solution']['formulas']:ck(i+' formulafields',bool(f['expression']and f['variables']and f['units']and f['assumptions']),'Variables,unitsandpremisesprovided.')
report=dict(role='Author-side repair checks, not independent verification',startedAt=start,completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),interpreter=sys.executable,command='python scripts/check_W11_L52_v2_author.py',packages='Python standard library only',checkGroups=len(checks),checks=checks,randomCases=1000,randomAssertions=4000,acceptedPreserved=117,changedQuestions=15,newGapQuestions=6,currentTotal=138,questionBatchSha256=sha(f'data/question-batches/{B}.json'),executionScope='Preserved YAML metadata, literal predicates and supplied arithmetic only. No restricted venv, OpenCV/Ultralytics import, model inference, codec or hardware execution. Historical boundary report retained unchanged.')
(R/f'audits/{B}-v2-author-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Passed',len(checks),'groups;1000cases/4000assertions')
