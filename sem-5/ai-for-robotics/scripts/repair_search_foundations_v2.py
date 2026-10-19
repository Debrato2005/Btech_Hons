#!/usr/bin/env python3
"""Apply only the 15 independently flagged, repairable search revisions.
Preserves all other answer-bearing records and an exact original history copy.
This is author revision, not independent review. Source pixels inspected 2026-10-19.
"""
from pathlib import Path
import json,copy,hashlib,math
from validate import question_hash
ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/'audits/batch-history/search-foundations-v1-before-quality-repair.json'
TARGET=ROOT/'data/question-batches/search-foundations.json'
original=json.loads(HISTORY.read_text());batch=copy.deepcopy(original)
flags=json.loads((ROOT/'audits/search-foundations-independent-summary.json').read_text())['flags']
conflict='W08-L37-P1135-Q03';expected={f['questionId'] for f in flags if f['questionId']!=conflict}
by={q['id']:q for q in batch['questions']};before={q['id']:q for q in original['questions']}
changed=set();log=[]

def revise(qid,*,stem=None,options=None,reasons=None,why=None,difficulty=None,assumptions=None,steps=None,traps=None):
 assert qid in expected and qid not in changed
 q=by[qid];assert q['version']==1
 q.update(version=2,status='draft',reviewIds=[])
 q['revisionAuthors']=['build_offline_study_interface-search-quality-reviser']
 if stem:q['stem']=stem
 if difficulty:q['difficulty']=difficulty
 if assumptions is not None:q['assumptions']=assumptions
 if options:
  assert len(options)==4 and len(set(options))==4
  texts={f'o{i+1}':v for i,v in enumerate(options)}
  for o in q['options']:o['text']=texts[o['id']]
 if reasons:
  assert len(reasons)==4
  q['solution']['optionExplanations']={f'o{i+1}':v for i,v in enumerate(reasons)}
  # Wrong-option explanations are referenced by stable identity, not display position.
  q['solution']['misconceptions']=[v for i,v in enumerate(reasons,1) if f'o{i}' not in q['correctOptionIds']]
 if why:q['solution'].update(justification=why,simpleExplanation=why)
 if steps is not None:q['solution']['steps']=steps
 if traps is not None:q['solution']['examTraps']=traps
 changed.add(qid);log.append({'questionId':qid,'oldVersion':1,'newVersion':2,'oldSha256':question_hash(before[qid]),'repairReason':next(f['findings'] for f in flags if f['questionId']==qid)})
 return q

revise('W08-L36-P1106-Q02',
 stem='Which metric does this slide explicitly request for comparing search-efficiency gains, distinct from the returned route’s quality?',
 options=['Number of expanded zones','Total kilometres on the returned route','Maximum number of vertices held in the frontier','Number of edges on the returned route'],
 reasons=['The slide explicitly asks to compare expanded-zone counts.','Route length measures the resulting travel cost, not the requested search-work count.','Peak frontier size is a meaningful memory-use metric, but it is not the comparison requested on this slide.','Hop count measures the route’s number of transitions, not all zones processed during search.'],
 why='The requested comparison counts expanded zones. Route distance, route hops and peak frontier size are useful but different measures.',
 traps=['Do not substitute a plausible memory or route-quality measure for the exact search-effort measure requested.'])
revise('W08-L36-P1107-Q02',
 stem='Using the slide’s open/closed-set terminology, which statement distinguishes the frontier from the explored set?',
 options=['Frontier contains discovered vertices scheduled for processing; explored contains vertices already processed','Frontier contains already processed vertices; explored contains vertices still waiting for processing','Frontier contains every vertex discovered so far, including those already processed; explored contains only processed vertices','Frontier contains all as-yet-undiscovered vertices; explored contains every discovered vertex, including those still queued'],
 reasons=['This separates pending work in the open set from completed processing in the closed set.','This reverses the open and closed roles.','Already processed vertices are not retained as pending frontier work under this convention.','Undiscovered vertices have not been scheduled; queued but unprocessed vertices do not yet belong to this closed set.'],
 why='The frontier schedules discovered but unprocessed states. The explored set tracks completed processing, rather than every state that has merely been discovered.',
 assumptions=['Interpret the slide’s closed-set “visited” terminology as processed/expanded; do not use a separate implementation convention that marks discovery as visited.'],
 traps=['Discovery, enqueueing and expansion are different events.'])
revise('W08-L36-P1107-Q03',
 options=['The selected hop-minimizing route remains the same; its physical travel cost may change','Both the selected route and its physical travel cost must remain the same','The physical travel cost remains the same, but the selected route may change','The minimum hop count remains the same, but BFS must reselect a route using the new road distances'],
 reasons=['BFS uses the unchanged topology and queue order, while summing changed weights can alter route cost.','The sum of changed distances on an unchanged route need not remain fixed.','BFS does not change its selected route here, and there is no invariant physical-cost sum.','The minimum hop count is unchanged, but BFS does not use road distances to break ties or reselect a route.'],
 assumptions=['Only edge weights change; topology, start, goal, neighbor ordering, repeated-state handling and goal-test timing remain fixed.','All road distances remain positive and all vertices remain reachable exactly as before.'],
 why='With all search conventions fixed, BFS makes the same FIFO/topological decisions. Only the numerical distance subsequently summed along its selected route may change.',
 traps=['An unchanged route is not the same as an unchanged weighted route cost.'])
revise('W08-L36-P1116-Q03',difficulty='medium',
 options=['The returned optimal cost stays 9, and D is not expanded before termination','The returned cost becomes 15 because D’s alternative path replaces G’s cost','The returned cost stays 9, but both tied nodes must still be expanded before termination','The returned cost stays 9, but choosing the other tied node necessarily destroys UCS optimality'],
 reasons=['Removing G triggers the stated goal test immediately; its best cost is already 9.','The more expensive D-to-G candidate is 15 and cannot replace the existing 9-cost goal entry.','Goal-on-removal terminates when G is removed; it does not require emptying the equal-priority group.','Tie choice among equal minimum g values in this positive-cost example can change effort without invalidating the optimal cost.'],
 why='At frontier [D(9),G(9)], removing G first ends the search before D’s expansion. The goal’s accumulated cost remains 9.',
 steps=['The frontier already contains G with g=9.','Choose G under the changed equal-cost tie rule.','Goal test on removal succeeds immediately, so D remains unexpanded.'],
 traps=['Tie-breaking changes an expansion trace; it does not automatically change the best goal cost.'])
revise('W08-L36-P1120-Q03',difficulty='medium')
revise('W08-L36-P1124-Q03',
 stem='Which pair of environment representations is explicitly named in the lecture summary?',
 options=['Grid maps and graph-based maps','Grid maps and polygonal boundary maps','Visibility graphs and Voronoi diagrams','Landmark maps and potential fields'],
 reasons=['The summary explicitly names these two representation categories.','The summary names grid maps but does not pair them with polygonal boundary maps.','These are not the two category names printed in this summary.','Neither is the pair named in the relevant summary bullet.'],
 why='This is an exact source-recall question: the summary says grid maps or graph-based maps, not that these are the only possible spatial models.',
 traps=['Distinguish what is explicitly named from what could be used in other planning methods.'])
revise('W08-L37-P1128-Q01',
 options=['Occupancy grid → polar histogram → steering','Steering → polar histogram → occupancy grid','Polar histogram → occupancy grid → steering','Occupancy grid → steering → polar histogram'],
 reasons=['This is the processing order printed in the learning objective.','This reverses the stated flow from sensed spatial representation toward a steering decision.','This swaps the occupancy-grid input and its polar-histogram transformation.','The steering decision follows the polar representation in the printed outline, rather than preceding it.'],
 why='The slide describes VFH as reducing occupancy information to a polar histogram and then choosing steering.',
 traps=['Use the printed input-to-decision order, not a permutation of the same stage names.'])
revise('W08-L37-P1132-Q04',
 stem='Which ordering matches the four numbered grid-to-graph conversion steps in the slides?',
 options=['Define coordinates → encode occupancy → create free-cell vertices → add legal weighted neighbor edges','Define coordinates → create free-cell vertices → encode occupancy → add legal weighted neighbor edges','Encode occupancy → define coordinates → add legal weighted neighbor edges → create free-cell vertices','Define coordinates → encode occupancy → add legal weighted neighbor edges → create free-cell vertices'],
 reasons=['This follows Step 1, Step 2, Step 3 and Step 4 as printed.','This places vertex creation before the printed occupancy-encoding step.','This changes both the coordinate/occupancy order and the vertex/edge order.','This reverses the printed Step 3 vertex construction and Step 4 edge construction.'],
 why='The question asks for the source’s stated sequence: index cells, encode occupancy, create vertices for free cells, then connect permitted neighboring vertices with movement costs.',
 traps=['A possible software implementation order is not necessarily the four numbered steps printed here.'])
# Remove unsupported highlight wording, rather than borrowing the inconsistent start-g label.
q=revise('W08-L37-P1135-Q02',
 stem='For the 5×5 source grid, which proposed start-to-goal route is legal under the no-corner-cutting rule and has the correctly stated cost? Use (row,column), start (4,4), goal (2,0), cardinal cost 1 and diagonal cost 1.4.',
 why='The route along row 4 through columns 3,2,1, then up to (3,1) and diagonally to (2,0), uses four cardinal moves and one legal diagonal. Its cost is 4+1.4=5.4. This conclusion is derived from occupancy and movement rules, not from a highlighted-cost map.',
 assumptions=['Rows and columns run from 0 to 4. Blocked cells are (0,0),(0,1),(0,2),(1,2),(2,2),(3,2); all other cells are traversable.','Start accumulated cost is zero as defined on physical page 1133.','Use exactly 1.4 for each allowed diagonal. A diagonal requires both side-adjacent cardinal cells to be traversable.'],
 reasons=['All cells and moves are legal: four cardinal moves plus one diagonal give 5.4.','The move (4,2)→(3,1) cuts the corner beside blocked cell (3,2), although its arithmetic total would be 4.8.','The proposed route passes through blocked cell (2,2); it also attempts a forbidden diagonal beside the wall.','This repeats the legal route but incorrectly totals it as 6.4 instead of 5.4.'],
 steps=['Read blocked cells from the coordinate grid; retain start and goal as traversable.','Check every proposed move, including the two side-adjacent cells for any diagonal.','The legal route is (4,4)→(4,3)→(4,2)→(4,1)→(3,1)→(2,0).','Its four cardinal moves cost 4; its final diagonal costs 1.4; total 5.4.'],
 traps=['A geometrically short diagonal may be forbidden beside a wall.','Count move costs from g(start)=0; do not import the inconsistent later start-g annotation.'])
for cite in q['citations']:
 if cite['physicalPage']==1131:
  cite.update(kind='figure',locator='Physical page 1131, printed slide 5: left 5×5 row/column-labelled occupancy grid',evidenceText='Grid indices are (row,column), 0 through 4. Black cells: (0,0),(0,1),(0,2),(1,2),(2,2),(3,2). Green start: (4,4). Red goal: (2,0). Other cells are white/free.',role='premise')
 elif cite['physicalPage']==1132:
  cite.update(kind='equation',locator='Physical page 1132, printed slide 6: Steps 2–4 and cardinal/diagonal edge costs',evidenceText='Occupancy 0 is traversable and 1 is wall. Create a vertex for each free cell and edges for traversable neighbors under the connectivity model. Cardinal edges cost 1.0; diagonal edges cost √2 ≈ 1.4.',role='premise')
 elif cite['physicalPage']==1133:
  cite.update(kind='figure',locator='Physical page 1133, printed slide 7: green start g=0.0 and blue corner-warning rectangle',evidenceText='g(n) is accumulated move cost from Start. The green start has g=0.0. The warning forbids diagonal steps at corners to avoid wall collision; its marked corner is beside blocked cell (3,2). The goal label is 5.4.',role='premise')
 else:cite['role']='premise'
q['notes']='Derived legality/cost question using physical pages 1131–1134. It makes no assertion about highlighted cells on page 1135 and does not adopt that page’s inconsistent start g=1.0 annotation.'
revise('W08-L37-P1135-Q04',
 options=['A* selects among current discovered frontier entries; a final cost map does not show which cells are available at the current step','Every free cell with a printed heuristic is automatically a frontier entry, even before a route to it is generated','Once a cell receives any g label, that label is its final search cost and never needs a lower-cost update','The next expansion may be chosen from the explored set whenever one of its recorded f values is below all frontier values'],
 reasons=['Eligibility depends on discovery and the current open set; a static table is not that changing set.','Knowing a heuristic is not the same as having generated a finite start-to-cell path and queued that state.','Search g values are best-known costs and may improve when a better path is found; a printed final map omits that history.','Already explored states are not chosen again merely because their old f is small; any reopening must follow the algorithm’s improved-path rule.'],
 why='A* minimizes f over its current frontier entries. A prelabelled map does not encode discovery, expansion or cost-update history and cannot replace the trace.',
 assumptions=['Use the graph-search frontier convention demonstrated on physical pages 1121–1122.','The question concerns candidate eligibility, not the correctness of each numerical label on physical page 1135. Its inconsistent start g=1.0 label is not adopted as a rule.'],
 traps=['A visible heuristic or final g label does not imply current frontier membership.'])
revise('W08-L37-P1136-Q02',
 options=['The route was planned using a known static map, but a later obstacle can invalidate a previously free segment','The route remains safe whenever the start and goal stay fixed, even if intermediate cells become occupied','Changing only the tie-breaking rule on the unchanged old map incorporates newly sensed obstacles','A shortest route on the original map must remain collision-free after the environment changes'],
 reasons=['People, robots or moved furniture can occupy cells assumed free during planning.','Fixed endpoints do not ensure that the connecting route remains traversable.','Tie-breaking chooses among existing priorities; it does not update occupancy or add sensed obstacles to the map.','Optimality was conditional on the old map, not a guarantee against subsequent changes.'],
 why='A globally optimal route is a solution for the environment model used to plan it. New sensed obstacles require updating that model and responding through avoidance or replanning.',
 traps=['Do not confuse a change to search ordering with an update to the environment representation.'])
revise('W08-L37-P1137-Q03',difficulty='easy')
revise('W08-L37-P1137-Q04',difficulty='easy')
revise('W08-L36-P1120-Q04',difficulty='easy',
 options=['The UCS priority g(v), the accumulated path cost','The BFS depth priority, the number of edges from the start regardless of weight','The cost of the single most recent edge into v, ignoring earlier edges','The greedy best-first priority h(v) alone, so all vertices receive the same primary priority'],
 reasons=['Substitute h(v)=0 into f(v)=g(v)+h(v) to obtain f(v)=g(v).','Weighted g need not equal depth unless all edge costs are equal.','g is cumulative cost over the path, not just the newest edge weight.','A* retains g even when h is zero; it does not switch to heuristic-only selection.'],
 why='Zeroing h removes heuristic guidance, not accumulated cost. With matching tie and repeated-state rules, the remaining primary priority is the same g used by UCS.',
 steps=['Start from f(v)=g(v)+h(v).','Set h(v)=0 for every vertex.','Then f(v)=g(v), the UCS priority.'],
 traps=['Distinguish accumulated cost, hop count, last-edge cost and heuristic-only priority.'])
q=revise('W08-L37-P1132-Q05',difficulty='medium',
 stem='For a fixed legal path containing diagonal moves, which consequence follows if its diagonal costs use exact √2 instead of the printed table’s 1.4, before rounding final totals?',
 options=['The exact total is slightly larger under √2; the numerical convention must be stated','The exact totals are identical because √2 and 1.4 are the same number','The exact √2 total is slightly smaller because 1.4 rounds √2 upward','The difference is always √2−1.4, regardless of how many diagonal moves the path contains'],
 reasons=['Each diagonal contributes √2−1.4≈0.01421356 more; the change accumulates over the fixed path.','The values are approximately, not exactly, equal.','1.4 is less than √2, so the direction of the claimed rounding error is reversed.','With d diagonals the difference is d(√2−1.4), not a fixed one-diagonal error.'],
 why='For the same legal path with d diagonal moves and c cardinal moves, the totals are c+d√2 and c+1.4d. Their difference is d(√2−1.4)>0 when d>0.',
 assumptions=['The path and legal-move rules stay fixed; at least one diagonal is used. Cardinal costs remain exactly 1.','Compare unrounded totals; this does not assert that two separately optimized path choices are identical.'],
 steps=['Let c be the number of cardinal moves and d>0 the number of diagonal moves.','Subtract (c+1.4d) from (c+d√2).','The difference is d(√2−1.4), which is positive and grows with d.'],
 traps=['Rounding error accumulates per diagonal; it does not by itself change the legal connectivity.'])
q['solution']['formulas']=[{'expression':'C_exact−C_table=d(√2−1.4)','variables':{'d':'number of diagonal moves on the fixed legal path','C_exact':'total with exact √2 diagonal cost','C_table':'total with 1.4 diagonal cost'},'units':{'C_exact,C_table':'grid-cost units','d':'dimensionless move count'},'assumptions':q['assumptions']}]
# Correct the malformed extracted square-root symbol only on this revised record.
for cite in q['citations']:
 if cite['physicalPage']==1132:
  cite['evidenceText']='Step 2 encodes free cells as 0 and walls as 1. Step 3 creates vertices for free cells. Step 4 creates permitted neighboring edges. Cardinal edge cost=1.0. Diagonal edge cost=√2≈1.4 (square-root sign visually confirmed).'
  cite['kind']='equation';cite['role']='premise'

assert changed==expected and len(changed)==15
for q in batch['questions']:
 if q['id'] not in changed:assert q==before[q['id']],'Untargeted record changed'
# Status only: unresolved conflicting item remains excluded, retaining identical hash/version.
by[conflict]['status']='flagged'
assert question_hash(by[conflict])==question_hash(before[conflict]) and by[conflict]['version']==1
verified_v1=json.loads((ROOT/'data/reviews/search-foundations-v1-independent.json').read_text())
if isinstance(verified_v1,dict):verified_v1=verified_v1['reviews']
approved={r['questionId'] for r in verified_v1 if r['decision']=='verified'}
assert len(approved)==52 and approved.isdisjoint(changed)
assert all(by[i]==before[i] for i in approved)
for entry in log:entry['newSha256']=question_hash(by[entry['questionId']])
# Recompute the repaired grid-path options rather than relying on the source's final label.
blocked={(0,0),(0,1),(0,2),(1,2),(2,2),(3,2)}
def route(path):
 cost=0
 for a,b in zip(path,path[1:]):
  dr,dc=b[0]-a[0],b[1]-a[1]
  if a in blocked or b in blocked or max(abs(dr),abs(dc))!=1:return False,None
  if dr and dc:
   if (a[0]+dr,a[1]) in blocked or (a[0],a[1]+dc) in blocked:return False,None
   cost+=1.4
  else:cost+=1
 return True,cost
legal=[(4,4),(4,3),(4,2),(4,1),(3,1),(2,0)]
assert route(legal)==(True,5.4)
assert route([(4,4),(4,3),(4,2),(3,1),(2,0)])[0] is False
assert route([(4,4),(3,3),(2,2),(2,1),(2,0)])[0] is False
assert 2*(math.sqrt(2)-1.4)>math.sqrt(2)-1.4>0
# Guard against overwriting somebody else's changes: rerun is allowed only for our exact result.
current=json.loads(TARGET.read_text())
assert current==original or current==batch,'Current batch changed externally; reconcile before writing.'
TARGET.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
blind=[{k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')} for q in batch['questions'] if q['id'] in changed]
(ROOT/'audits/blind-search-foundations-v2.json').write_text(json.dumps(blind,ensure_ascii=False,indent=2)+'\n')
report={'revisionAuthorId':'build_offline_study_interface-search-quality-reviser','revisedQuestionCount':15,'approvedQuestionsPreservedExactly':52,'unresolvedConflict':{'questionId':conflict,'status':'flagged','version':1,'contentHashUnchanged':True},'historyPath':str(HISTORY.relative_to(ROOT)),'blindPacketPath':'audits/blind-search-foundations-v2.json','sourcePixelsInspected':[1106,1107,1112,1116,1117,1119,1120,1121,1122,1124,1128,1131,1132,1133,1134,1135,1136,1137],'authorComputations':{'legalRouteCost':route(legal),'cornerCuttingAlternativeRejected':True,'blockedCellAlternativeRejected':True,'roundingErrorPerDiagonal':math.sqrt(2)-1.4},'revisions':log,'reviewStatus':'independent_reverification_required'}
(ROOT/'audits/search-foundations-v2-revision-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['revisedQuestionCount','approvedQuestionsPreservedExactly','unresolvedConflict','blindPacketPath','reviewStatus']},indent=2))
