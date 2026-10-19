#!/usr/bin/env python3
"""Bounded L36 author repairs, with accepted content immutable. Not independent review."""
import json,hashlib,copy,os
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];B='W08-L36-COVERAGE-GAP';PREFIX='W08-L36';A='L36-gap-repair-author-20261019'
SHA='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def fhash(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
if (R/f'audits/{B}-v2-review-manifest.json').exists():raise SystemExit('Frozen v2; do not overwrite reviewed content.')
old=read(f'data/question-batches/archive/{B}-v1.json');b=copy.deepcopy(old);qm={q['id']:q for q in b['questions']}
summary=read('audits/W08-L36-contracts-review-summary.json');flags=set(summary['flaggedQuestionIds']);accepted=summary['acceptedQuestionHashes'];legacy=read('data/question-batches/search-foundations.json')
allold={q['id']:q for q in old['questions']+legacy['questions']};assert len(flags)==8 and len(accepted)==74
assert all(qhash(allold[qid])==h for qid,h in accepted.items())
for qid in flags:
 q=qm[qid];q.update(version=q['version']+1,status='draft',reviewIds=[]);q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+[A]))
 if 'conflictResolution'in q:q['conflictResolution']['questionVersion']=q['version']
def Q(short):return qm[f'{PREFIX}-P{short}']
def option(short,k,text,reason):
 q=Q(short);next(o for o in q['options']if o['id']==k)['text']=text;q['solution']['optionExplanations'][k]=('Correct. 'if k=='o1'else'Incorrect. ')+reason
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][x]for x in('o2','o3','o4')]
def revise(short,rows,stem=None):
 q=Q(short)
 if stem:q['stem']=stem
 for i,(t,r)in enumerate(rows,1):option(short,f'o{i}',t,r)
 q['solution'].update(justification=rows[0][1],simpleExplanation=rows[0][1])
def form(q,expression,variables,units,assumptions):q['solution']['formulas'].append(dict(expression=expression,variables=variables,units=units,assumptions=assumptions))
def cite(p,kind,loc,role='premise'):
 return dict(slideId=f'lectures-p{p}',sourceId='lectures',sourceSha256=SHA,physicalPage=p,kind=kind,locator=f'Printed slide {p-1087}: {loc}',evidenceText=(R/f'sources/text/lectures/page-{p}.txt').read_text().strip(),role=role,region=None)
option('1091-Q01','o4','It is feasible if collision checking uses the full swept body, even though the turning-radius limit is still violated','Swept-body collision clearance addresses spatial occupancy, not the separately violated minimum turning radius.')
option('1091-Q02','o2','It proves the shortest feasible route because its centerline looks shorter than other ways around the rectangles','A visually short point curve is not a comparison of all permitted paths under the robot’s footprint and motion constraints.')
option('1096-Q02','o4','Agreement between fused sensors proves the pose is exact even if they share a systematic bias','Agreement does not exclude common measurement bias or map error; several agreeing sensors can support the same inaccurate estimate.')
revise('1097-Q02',[
('It is still whole-route planning in this example, although it is recomputed online','The scope remains the whole-map route. The slide’s offline/global comparison is simplified and does not prohibit recomputing that route during motion.'),
('It is local planning because the computation happens online, regardless of the route’s spatial scope','Online timing alone does not classify a whole-map route as a short-range reactive maneuver.'),
('It is a map update only, because marking the closure and selecting a new destination route are the same operation','Updating traversability and searching that updated map for a route are distinct steps; the scenario explicitly includes route recomputation.'),
('It is local planning because it reacts to one changed road, even though it recomputes the complete destination route','The geographical extent of the changed observation does not determine the scope of the resulting route search.')])
Q('1097-Q02')['assumptions']=['The planner searches the complete updated map and outputs a route to the original destination, not just an immediate steering command.']
option('1099-Q04','o3','The robot fits because its half-width is 0.5 m, less than the corridor’s full 0.8 m width','This compares half the body width with the entire corridor. On the centerline, each side offers only 0.4 m clearance, less than the required 0.5 m.')
option('1099-Q04','o4','The robot fits if each wall is inflated by 0.1 m, because 0.1 m is half the width deficit','Obstacle inflation must account for the robot’s half-width, not half the already-existing fit deficit. Inflating by 0.5 m on each side leaves no feasible centerline.')
q=Q('1099-Q04');q['assumptions'].append('The binary free labels describe raw point occupancy, not an already footprint-inflated configuration-space map; the body travels centered and parallel to straight corridor walls.')
form(q,'w_robot ≤ w_corridor is necessary; c_side=w_corridor/2; r_robot=w_robot/2',{'w_robot':'Robot width, 1.0 m','w_corridor':'Corridor width, 0.8 m','c_side':'Wall clearance on either side of the centered reference point','r_robot':'Required side clearance, half the robot width'},{'all widths and clearances':'m'},['Rigid body, no narrower orientation, straight corridor; boundary contact is not accepted.'])
q['solution']['steps']=['The available side clearance is 0.8/2=0.4 m.','The required side clearance is 1.0/2=0.5 m, so the centered body overlaps both walls.','The width deficit is 0.2 m; its half, 0.1 m, is not the robot’s footprint radius.']
q=Q('1100-Q03');q['stem']='The directed map has edges A→B:3, A→C:1, C→B:7, B→E:1, B→D:5, C→D:2 and D→E:7. With additive edge costs, which A-to-E route has minimum total cost?'
for o in q['options']:o['text']=o['text'].split(', cost')[0]
q['difficulty']='medium'
revise('1102-Q05',[
('BFS still minimizes hops, but unequal step costs no longer make hop count equal total path cost','A cardinal step and a diagonal step each count as one hop but have different geometric costs, so the equal-cost proof no longer applies.'),
('BFS minimizes geometric cost because its FIFO queue automatically prefers the cheaper of two same-depth routes','FIFO orders discovery, not cumulative weighted cost; a cost-sensitive priority rule would be a different algorithm.'),
('BFS must return a more expensive route on every grid containing a diagonal edge','Loss of the general equal-cost guarantee is not proof that every instance fails; some returned routes are also cost-optimal.'),
('BFS remains cost-optimal because assigning one queue entry to each move makes all move costs equal','A bookkeeping entry counts one move but does not change its assigned weight from square root of two to one.')])
form(Q('1102-Q05'),'H=n_c+n_d; C=n_c+sqrt(2)*n_d',{'H':'Number of edges (hops) in a route','C':'Geometric route cost in unit-cell lengths','n_c':'Number of cardinal moves','n_d':'Number of diagonal moves'},{'H,n_c,n_d':'counts','C':'unit-cell lengths'},['Equal square cells; cardinal weight 1 and diagonal weight sqrt(2); no extra costs.'])
revise('1104-Q02',[
('No route exists in that represented graph under its encoded transition rules','Exhausting all reachable represented states proves disconnection in that graph, not completeness of the physical map.'),
('No physically possible route exists, even if the map omitted a valid passage','A real passage missing from the graph cannot be discovered by graph search; the physical conclusion is stronger than the evidence.'),
('The same failure certificate would hold if the search had instead stopped at a fixed depth limit','A depth-limited search can stop before reaching an existing longer route; its stopping condition is not the exhaustive one stipulated here.'),
('The same failure certificate would hold if the successor generator had skipped one permitted edge','An omitted edge can hide the only route. Exhaustive correctness depends on the stated complete successor enumeration.')])
newids=[]
def gap(short,title,stem,rows,cites,typ,difficulty,assumptions):
 q=copy.deepcopy(old['questions'][0]);qid=f'{PREFIX}-P{short}';assert qid not in allold
 cid=f'{qid}-COVERAGE'
 q.update(id=qid,version=1,status='draft',authorId=A,stem=stem,selectionMode='single',type=typ,difficulty=difficulty,cognitiveSkill={"scenario":"application","algorithm_trace":"algorithm"}.get(typ,typ),subtopic=title,tags=['path-planning','bounded-coverage-gap'],conceptIds=[cid],assumptions=assumptions,options=[{'id':f'o{i}','text':t}for i,(t,r)in enumerate(rows,1)],correctOptionIds=['o1'],citations=[cite(*c)for c in cites],reviewIds=[])
 q.pop('conflictResolution',None);q.pop('revisionAuthors',None)
 q['solution']=dict(justification=rows[0][1],optionExplanations={f'o{i}':('Correct. 'if i==1 else'Incorrect. ')+r for i,(t,r)in enumerate(rows,1)},steps=[],formulas=[],simpleExplanation=rows[0][1],memoryAid=None,misconceptions=[r for t,r in rows[1:]],examTraps=[],prerequisiteConceptIds=[])
 qm[qid]=q;b['questions'].append(q);newids.append(qid)
 b['concepts'].append(dict(id=cid,title=title,description='Bounded reviewer-identified synthesis gap; supplied numerical premises are distinguished from source conventions.',slideIds=sorted({c['slideId']for c in q['citations']}),questionIds=[qid],status='drafted',topic=q['topic'],subtopic=title,prerequisiteConceptIds=[],examinationAngles=[stem]))
 return q
q=gap('1099-Q05','Resolution and represented passage connectivity','A point robot moves in the fixed open corridor 0.3<y<0.9 m. The planning region is 0≤x≤4 m. Square grids share origin (0,0); a cell is free only if its entire closed square lies inside the open corridor. Compare cell sides 1.0 m and 0.2 m for start (0.5,0.5) m and goal (3.5,0.5) m, using 4-connected free cells. Which conclusion follows?',[
('The coarse grid blocks the endpoints, while the fine grid represents a horizontal route; the physical corridor is unchanged','The coarse row spans y=0 to 1 and intersects both walls. The fine row spans y=0.4 to 0.6, lies strictly inside the corridor, and connects the two endpoints.'),
('Both grids represent a route because both endpoint coordinates lie physically inside the corridor','Physical inclusion of the center does not make its entire coarse square free under the supplied conservative occupancy rule.'),
('Neither grid represents a route because the corridor width is smaller than the coarse cell side','This applies the coarse 1.0 m scale to the fine 0.2 m grid, whose row from 0.4 to 0.6 m is wholly free.'),
('The coarse grid represents a route but the fine grid blocks it, because finer cells create more occupied cells','Counting occupied cells does not determine connectivity; the coarse endpoint cells intersect the walls, while the specified fine row does not.')],[(1099,'statement','Occupancy-grid binary convention and precision limitation due to grid resolution'),(1102,'statement','Place vertices in cells and connect reachable neighbors')],'scenario','medium',['All coordinates and cell sides are supplied illustrative values, not measurements from the slide figure.','Walls occupy y≤0.3 and y≥0.9 m; any boundary contact makes a cell occupied. The robot is a point, so no additional footprint inflation is needed.','Use grid cells contained in the stated x range; there are no obstacles or forbidden transitions along the interior horizontal row.'])
q['solution']['steps']=['At y=0.5, the coarse grid row is [0,1] m, which fails 0.3<y<0.9 for the entire square.','The fine grid row is [0.4,0.6] m, so every cell in that row is free.','The start and goal lie at centers in this same fine row; successive horizontal neighbors join them.','Only the represented connectivity changes; the physical free strip remains 0.6 m wide.']
form(q,'j=floor(y/s); [y_low,y_high]=[j*s,(j+1)*s]; free iff 0.3<y_low and y_high<0.9',{'s':'Square cell side, 1.0 or 0.2 m','y':'Endpoint vertical coordinate, 0.5 m','j':'Zero-origin row index','y_low,y_high':'Lower and upper row boundaries','floor':'Greatest integer not exceeding its argument'},{'s,y,y_low,y_high':'m','j':'dimensionless integer'},['Grid origin is zero; closed cells must lie strictly inside the open free strip; equality with a wall is occupied.'])
q=gap('1102-Q06','Connectivity to shortest geometric grid distance','In an obstacle-free square grid with cell side 0.4 m, the goal is five columns and three rows from the start. Cardinal moves cost one cell side, and diagonal moves cost sqrt(2) cell sides. What are the minimum geometric path lengths under 4-connected and 8-connected motion, respectively?',[
('3.2 m; (0.8+1.2 sqrt(2)) m','Four-connected motion needs five horizontal and three vertical steps. Eight-connected motion uses three diagonals and two cardinal steps.'),
('3.2 m; 2.0 m','This counts five moves in the eight-connected case but incorrectly gives diagonal moves the cardinal cost.'),
('(0.4 sqrt(34)) m; (0.4 sqrt(34)) m','The straight Euclidean displacement is a lower bound, but the grid permits only cardinal or 45-degree diagonal headings, not an arbitrary straight heading.'),
('3.2 m; 3.2 m','The four-connected length is correct, but this ignores the shorter diagonal substitutions allowed in the eight-connected case.')],[(1102,'equation','Cardinal cost 1 and diagonal cost square root of 2'),(1107,'statement','BFS ignores actual edge weight'),(1111,'figure','Weighted routes distinguish geometric distance from hop count')],'numerical','medium',['The endpoint displacement is supplied in integer cell indices; the grid has no obstacles or boundary restrictions.','Minimize sum of geometric edge lengths, not hop count. Diagonal moves are allowed without a corner constraint because the grid is obstacle-free.'])
q['solution']['steps']=['Four-connected motion requires |dx|+|dy|=5+3=8 cardinal moves, giving 8(0.4)=3.2 m.','Pair three horizontal and vertical steps into three diagonals; two horizontal steps remain.','The eight-connected cost is 0.4(2+3 sqrt(2))=0.8+1.2 sqrt(2)≈2.49706 m.','Replacing each diagonal by two cardinal moves would increase length because sqrt(2)<2.']
form(q,'L4=s*(|dx|+|dy|); L8=s*(max(|dx|,|dy|)+(sqrt(2)-1)*min(|dx|,|dy|))',{'L4,L8':'Minimum geometric path length for 4- and 8-connected motion','s':'Cell side, 0.4 m','dx,dy':'Integer horizontal and vertical goal displacement, 5 and 3'},{'L4,L8,s':'m','dx,dy':'cell-index differences (dimensionless)'},['Obstacle-free grid; cardinal edge length s and diagonal edge length s*sqrt(2); sum edge lengths.'])
q=gap('1117-Q02','Complete UCS and A-star traces and parent reconstruction','Run UCS and A* from A to G on the undirected graph with edges AB=5, AC=2, BD=6, BE=3, CF=4, EF=1, ED=2, DG=6 and FG=3 km. For A*, use h(A,B,C,D,E,F,G)=(7,6,5,4,3,2,0) km. Each algorithm relaxes a vertex only for a strictly smaller g, breaks equal priorities alphabetically, and stops when G is popped. Count only non-goal expansions. Which complete record is correct?',[
('UCS expands A,C,B,F,E,D (6); A* expands A,C,F (3); both return A→C→F→G at 9 km','UCS improves E from 8 to 7 via F, then D from 11 to 9 via E. The alphabetical D/G tie expands D before G. A* priorities reach G after A,C,F; both reconstruct the parent chain through C and F.'),
('UCS expands A,C,B,F (4); A* expands A,C,F (3); both return A→C→F→G at 9 km','The UCS list stops when G is first generated from F rather than when G is popped; E and then D must still be expanded under the given rule.'),
('UCS expands A,C,B,F,E,D,G (7); A* expands A,C,F,G (4); both return A→C→F→G at 9 km','This includes the popped goal in the expansion count, contrary to the explicit non-goal convention and goal-before-expansion test.'),
('UCS expands A,C,B,F,E,D (6) and returns A→C→F→E→D→G at 15 km; A* expands A,C,F (3) and returns A→C→F→G at 9 km','The longer UCS path would overwrite G’s existing 9 km parent when D proposes 15 km. Strict improvement rejects that proposal, so G retains parent F.')],[(1112,'figure','Original nine undirected edges and weights'),(1112,'statement','UCS lowest cumulative g priority'),(1113,'statement','Initial A expansion frontier'),(1114,'statement','C then B expansions'),(1115,'statement','E improvement through F'),(1116,'statement','D improvement and D/G priority tie'),(1117,'statement','Final reconstructed UCS path'),(1119,'equation','A-star priority f=g+h'),(1119,'figure','Seven heuristic labels'),(1121,'statement','A-star initial frontier'),(1122,'statement','A-star C and F updates'),(1123,'statement','Final reconstructed A-star path')],'algorithm_trace','hard',['Weights and heuristic labels are transcribed from the source graph; all distances use km. Both directions of each listed undirected edge are permitted.','Initialize g(A)=0 and all other g values to infinity. Use a minimum-priority frontier: g for UCS, g+h for A*. Update parent on every strictly cheaper route; do not overwrite on equal or worse routes.','Ignore stale priority entries and already-expanded vertices; the supplied heuristic is consistent on this graph, so no reopening is needed. Test the goal immediately after a valid pop, before expanding successors.'])
q['solution']['steps']=['UCS: A creates B=5,C=2; C creates F=6; B creates E=8,D=11.','UCS: F improves E to 7 and creates G=9; E improves D to 9.','UCS: D and G tie at 9; alphabetical priority expands D. Its candidate for G is 9+6=15, so G keeps its 9 km value and parent F.','UCS then pops G; six non-goal vertices have expanded. Reconstruct G←F←C←A.','A*: A creates C with f=2+5=7 and B with f=5+6=11; C creates F with f=6+2=8.','A*: F creates G with f=9 and E with f=7+3=10. G is next and terminates the search after three non-goal expansions.','Both returned routes cost 2+4+3=9 km; the rejected UCS detour costs 2+4+1+2+6=15 km.']
form(q,'g_new(v)=g(u)+c(u,v); update iff g_new(v)<g(v); f_UCS(v)=g(v); f_A*(v)=g(v)+h(v)',{'u,v':'Current vertex and a neighboring vertex','c(u,v)':'Listed undirected edge length','g(v)':'Best recorded start-to-vertex distance','g_new(v)':'Candidate distance through u','h(v)':'Specified remaining-distance heuristic','f_UCS,f_A*':'Frontier priority in each algorithm'},{'c,g,g_new,h,f_UCS,f_A*':'km','u,v':'vertex labels'},['All edge weights positive; start g=0; alphabetical ties; goal test on pop; only non-goal pops count as expansions.'])
# Preserve source qualifications, original objects, and accepted hashes exactly.
assert b['sourceIssues']==old['sourceIssues']
for qid in accepted:
 current=qm.get(qid,allold[qid]);assert current==allold[qid] and qhash(current)==accepted[qid]
assert all(q['correctOptionIds']==qm[q['id']]['correctOptionIds']for q in old['questions'])
for c in b['concepts']:
 c['questionIds']=[q['id']for q in b['questions']if c['id']in q['conceptIds']]
 c['examinationAngles']=[q['stem']for q in b['questions']if c['id']in q['conceptIds']]
 c['slideIds']=sorted(set(c['slideIds']+[x['slideId']for q in b['questions']if c['id']in q['conceptIds']for x in q['citations']]))
inspection=read(f'data/inspection-batches/{B}.json');archive=f'data/inspection-batches/archive/{B}-v1.json'
if not (R/archive).exists():(R/archive).write_bytes((R/f'data/inspection-batches/{B}.json').read_bytes())
for s in inspection['slides']:s['conceptIds']=sorted(set(s.get('conceptIds',[])+[c['id']for c in b['concepts']+legacy['concepts']if s['id']in c['slideIds']]))
changed=[q for q in b['questions']if q['id']in flags or q['id']in newids]
for q in changed:
 assert q['status']=='draft' and q['reviewIds']==[]
 assert len(set(o['text']for o in q['options']))==4
 assert set(q['solution']['optionExplanations'])==set(o['id']for o in q['options'])
 if q['type']in('numerical','algorithm_trace'):assert q['solution']['formulas']and q['solution']['steps']
 if any(c['role']=='conflict'for c in q['citations']):assert q['conflictResolution']['questionVersion']==q['version']
b['coverageNote']='Original 39 accepted objects untouched. Of 43 earlier gap objects, 35 accepted objects are preserved and eight flagged objects revised. Three bounded reviewer-identified synthesis gaps are drafted; 85 total L36 questions, 74 accepted and 11 awaiting independent review.'
b['authorChecks']='scripts/check_W08_L36_gap_v2.py; author-only calculations, not independent verification.'
write(f'audits/{B}-v2-working.json',b);write(f'audits/{B}-v2-working-inspection.json',inspection)
write(f'audits/{B}-v2-coverage-closure-author.json',{'independentReview':False,'changedCount':8,'newCount':3,'acceptedCount':74,'lectureTotal':85,'sourceIssuesPreserved':11,'gapQuestions':dict(zip(['L36-G01','L36-G02','L36-G03'],newids)),'legacyQualityConcernsUnchanged':summary['legacyQualityConcerns']})
if os.environ.get('FREEZE_L36_V2')!='1':print('WORKING',len(changed));raise SystemExit(0)
assert read(f'audits/{B}-v2-author-computations.json')['passed']
assert read(f'audits/{B}-v2-integration-validation.json')['valid']
write(f'data/question-batches/{B}.json',b);write(f'data/inspection-batches/{B}.json',inspection)
blind=[{**{k:q[k]for k in('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]}for q in changed]
write(f'audits/blind-{B}-v2.json',blind);packetsha=fhash(f'audits/blind-{B}-v2.json')
write(f'audits/{B}-v2-review-manifest.json',{'batchId':B,'blindPacket':f'audits/blind-{B}-v2.json','blindPacketSha256':packetsha,'questionSha256':{q['id']:qhash(q)for q in changed},'preservedAcceptedHashes':accepted,'revisedCount':8,'newQuestionCount':3,'preservedAcceptedCount':74,'sourceBounds':[1088,1126],'sourceSha256':SHA,'priorBatchArtifact':f'data/question-batches/archive/{B}-v1.json','priorBatchSha256':fhash(f'data/question-batches/archive/{B}-v1.json'),'sourceIssuesSha256':hashlib.sha256(json.dumps(b['sourceIssues'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),'independentReviewPending':True})
(R/f'audits/handoffs/{B}-v2.md').write_text(f'''# L36 gap v2 frozen\n\nEight revised drafts plus three bounded gaps; all 74 accepted whole objects and hashes preserved, including all 39 original search-foundations questions. Total L36 85. Eleven source annotations unchanged. Prior keys unchanged.\n\nPacket: audits/blind-{B}-v2.json\nSHA256: {packetsha}\nManifest: audits/{B}-v2-review-manifest.json\nArchive: data/question-batches/archive/{B}-v1.json\nRepair script: scripts/repair_W08_L36_gap_v2.py (frozen guard)\nChecks: scripts/check_W08_L36_gap_v2.py and audits/{B}-v2-author-computations.json\n\nNineteen actual source pages revisited. Gaps address conservative-grid passage connectivity, optimal cardinal/diagonal distance with scale, and full UCS/A-star execution plus parent reconstruction. All changes remain draft pending independent review. Legacy quality concerns are preserved separately, not silently changed or reapproved. No canonical or Git writes.\n''')
print('FROZEN',packetsha)
