#!/usr/bin/env python3
"""Targeted author repairs of L39. No self-approval or accepted-object mutation."""
import json,hashlib,copy,os,random,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];B='W08-L39';A='L39-repair-author-20261019';SHA='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c';NOW='2026-10-19T21:32:18Z'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def fhash(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items()if k not in('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
if (R/f'audits/{B}-v2-review-manifest.json').exists():raise SystemExit('Frozen v2. Do not rerun after review.')
old=read(f'data/question-batches/archive/{B}-v1.json');b=copy.deepcopy(old);qm={q['id']:q for q in b['questions']};rv=read(f'data/reviews/{B}-v1-independent.json');summary=read(f'audits/{B}-v1-independent-summary.json');flags={r['questionId']for r in rv if r['decision']=='flagged'};accepted={r['questionId']:r['questionSha256']for r in rv if r['decision']=='verified'}
assert len(flags)==27 and len(accepted)==38
assert all(qhash(qm[r['questionId']])==r['questionSha256']for r in rv)
for qid in flags:
 q=qm[qid];q.update(version=q['version']+1,status='draft',reviewIds=[]);q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+[A]))
 if 'conflictResolution'in q:q['conflictResolution']['questionVersion']=q['version']
def Q(n):return qm[f'{B}-Q{n:03}']
def revise(n,rows,stem=None):
 q=Q(n);assert q['id']in flags and q['correctOptionIds']==['o1']
 if stem:q['stem']=stem
 q['options']=[dict(id=f'o{i}',text=t)for i,(t,r)in enumerate(rows,1)]
 q['solution'].update(justification=rows[0][1],simpleExplanation=rows[0][1],optionExplanations={f'o{i}':('Correct. 'if i==1 else'Incorrect. ')+r for i,(t,r)in enumerate(rows,1)},misconceptions=[r for t,r in rows[1:]],memoryAid=None,examTraps=[])
def form(n,expression,variables,units,assumptions):Q(n)['solution']['formulas'].append(dict(expression=expression,variables=variables,units=units,assumptions=assumptions))
def cite(p,kind,loc,role='premise'):
 return dict(slideId=f'lectures-p{p}',sourceId='lectures',sourceSha256=SHA,physicalPage=p,kind=kind,locator=f'Printed slide {p-1196}: {loc}',evidenceText=(R/f'sources/text/lectures/page-{p}.txt').read_text().strip(),role=role,region=None)
def role(n):
 for c in Q(n)['citations']:c['role']='premise'
for n in(4,5,16,20,26,45,49,51,54,57,58):role(n)
for n in(16,42,44,50,54,57,59,61):Q(n)['difficulty']='easy'
# Item-linked primary source locators, read during this revision, rather than generic all-purpose attribution.
locs={4:['ISRO: Navigation with Indian Constellation section, regional system and coverage area.','QZSS overview: Japanese system and Asia-Oceania availability discussion; no live constellation-count claim.'],5:['QZSS overview, Complements GPS section: compatible additional visible satellites and obstruction limits.'],8:['Navipedia GNSS Basic Observables, Pseudorange section: reception-minus-transmission clocks and additive error model, oldid=15397.'],13:['Navipedia Code Based Positioning (SPS), equations (2), (5), (6): receiver coordinates and common receiver clock offset, oldid=12251.'],16:['Navipedia Code Based Positioning (SPS), equation (6) and geometry-matrix definition, oldid=12251.','Navipedia Positioning Error, equations (1), (7), (8): geometry-dependent covariance under a stated error model.'],19:['Navipedia Code Based Positioning (SPS), opening paragraphs and equations (2), (6): broadcast satellite data and receiver-state estimation, oldid=12251.'],20:['Navipedia Ellipsoidal and Cartesian Coordinates Conversion, opening definition of (phi,lambda,h), oldid=16115.'],26:['Navipedia GNSS Basic Observables, code and carrier-phase equations and explicit opposite ionospheric signs, oldid=15397.']}
for n,ls in locs.items():
 for e,l in zip(Q(n).get('primaryEvidence',[]),ls):e['locator']=l;e['checkedAt']=NOW
nb=read('sources/supplemental/L39-official-notebook.ipynb');cellids=[i for i,c in enumerate(nb['cells'])if c['cell_type']=='code'];assert len(cellids)==1
nbsha=fhash('sources/supplemental/L39-official-notebook.ipynb');codesha=fhash('sources/supplemental/L39-official-code.py')
code_locs={42:'to_fake_latlon: LAT0/LON0 offsets, 300 reference coordinate and round(...,5).',44:'map_match: math.hypot distance over NODES; NODES entries N9,N10,N5,N1.',45:'map_match: ordered NODES.items() iteration and strict d < best_dist update. A/B tie is a supplied variant, not an original graph pair.',49:'euclidean and heuristic: hypot/100. The question explicitly removes build_adjacency edge rounding for a derived metric argument.',50:'build_adjacency rounds each edge to two decimals; heuristic returns unrounded euclidean. N2/N3 coordinates are in NODES.',51:'astar, ADJACENCY and heuristic are the tested program. The all-pairs Dijkstra experiment is in the separate author check, not in the notebook.',54:'build_adjacency versus build_waypoints: rounded stored edge weights versus raw euclidean accumulation before output rounding.',57:'current_waypoint: first cumulative_km >= distance_travelled_km - 1e-6; run_pipeline: travelled = total * 0.60.',58:'current_waypoint: executable >= comparison and 1e-6 tolerance; docstring next not-yet-reached does not exclude equality in the code.',59:'current_waypoint and run_pipeline: supplied travelled-distance fraction, with no live position feedback or motion-command law.'}
for n,l in code_locs.items():
 for e in Q(n).get('primaryEvidence',[]):
  if e['title'].startswith('Official'):
   e.update(locator=f'Original notebook code cell {cellids[0]} (zero-based): {l}',checkedAt=NOW,executionEvidence=f'audits/{B}-v2-author-computations.json')
 Q(n)['supplementalProvenance']={'path':'sources/supplemental/L39-official-notebook.ipynb','sha256':nbsha,'codeCellZeroBased':cellids[0],'codePath':'sources/supplemental/L39-official-code.py','codeSha256':codesha,'locator':l,'sourceUnmodified':True,'executionScope':'Original code cell executed unchanged in author checks; supplied test inputs are separate from source program.'}
revise(4,[
('NavIC is India’s regional system; QZSS is Japan’s region-focused system','The lecture supplies country pairings. ISRO and Japan’s Cabinet Office supply the regional-coverage qualification, not the PDF list itself.'),
('NavIC is India’s globally covering system; QZSS is Japan’s region-focused system','This mistakes NavIC’s regional service design for independent global coverage.'),
('NavIC is India’s regional system; QZSS is Japan’s globally covering system','This mistakes the QZSS regional focus for an independently worldwide navigation constellation.'),
('NavIC is Japan’s regional system; QZSS is India’s regional system','This reverses the two system-country associations printed in the lecture.')],stem='The lecture lists NavIC (India) and QZSS (Japan). Which coverage qualification is supported by the linked ISRO and Japan Cabinet Office descriptions?')
revise(5,[
('It can gain additional usable ranging signals when the signals and service region are supported','The lecture states multiple-constellation use; the QZSS overview explains compatible additional satellites as a way to improve availability under some obstructions.'),
('It must solve a separate four-satellite position fix for every constellation before combining any measurements','Compatible ranging measurements can contribute to a combined solution; a complete independent fix per constellation is not a general prerequisite.'),
('It can combine signals only when all participating constellations have the same national operator','Signal and receiver compatibility, not shared ownership, governs whether the receiver can use the signals.'),
('It must discard regional-system measurements whenever any global-system measurements are present','A regional system can complement a compatible global system within its supported region.')])
revise(8,[
('Clock offsets and propagation effects can enter the measured time difference','The time-derived observation is an apparent range; clock and propagation contributions can separate it from geometric range.'),
('Squaring the coordinate-distance equation makes the measured pseudorange itself a squared distance','The squared equation is an algebraic representation; the underlying pseudorange has units of length, not length squared.'),
('The code records a round-trip travel time that must be halved to obtain one-way geometric range','The stated satellite-to-receiver code observation is one-way, not a reflected two-way ranging measurement.'),
('Correcting the satellite clock alone removes the receiver clock and atmospheric contributions as well','These are distinct contributions; one correction does not remove all remaining terms.')])
Q(8)['citations']=[cite(1203,'statement','Measured distance is called pseudorange'),cite(1205,'equation','Unsquared pseudorange with additive receiver clock term')]
revise(13,[
('Three receiver coordinates and one common receiver clock offset','Under the simplified single-epoch model, satellite positions and corrections are given; the receiver estimates its three coordinates and shared time offset.'),
('Three receiver coordinates and one independently estimated propagation speed','The speed constant is supplied by the ranging model, not a fourth receiver-state unknown.'),
('Three receiver coordinates and the clock offset of a selected transmitting satellite','Satellite-clock corrections are treated as supplied here; the remaining shared offset belongs to the receiver.'),
('Three receiver coordinates and receiver clock drift, with no receiver clock offset','Drift describes change of clock offset over time; the single-epoch pseudorange model contains offset itself.')])
Q(13)['assumptions']=['Use the source’s simplified single-epoch model with supplied satellite coordinates and clock/propagation corrections; one common receiver clock bias remains.']
revise(16,[
('The count alone does not guarantee a well-conditioned four-unknown solution','The number of equations does not determine whether their geometry provides independent, stable information.'),
('Four measurement rows imply full rank because there are four receiver-state unknowns','A square geometry matrix can be singular or nearly singular; row count alone is insufficient.'),
('Dividing every measurement row by its length removes the near-dependence of the directions','Row scaling does not create independent directional information absent from the original geometry.'),
('Repeating a measurement in the same direction provides the missing independent spatial constraint','Repeated observations may reduce noise along measured directions, but do not create a new geometric direction.')])
revise(17,[
('Space: broadcast navigation signals; control: monitor orbit/timing and upload updates; user: estimate receiver state','These assignments agree with the broadcast and control links and the ground/user roles in the architecture diagram.'),
('Space: monitor the ground clock network; control: estimate each user state; user: upload satellite orbit updates','This shifts monitoring, user computation and orbit-update duties to the wrong segments.'),
('Space: broadcast navigation signals; control: estimate each user state; user: monitor constellation orbit and timing','Broadcasting is placed correctly, but the control/user responsibilities are interchanged.'),
('Space: compute finished user fixes; control: upload those user fixes; user: decode fixes without solving ranges','The basic architecture broadcasts satellite navigation information, not a personalized finished fix for each passive user.')])
revise(19,[
('The receiver uses broadcast timing and satellite data to solve its own position','The source shorthand should not be expanded into a claim that satellites solve every user fix; the receiver estimates its state from the measurements.'),
('The control segment uploads a finished receiver position into each satellite’s navigation message','Ground control supplies satellite orbit/timing information, not a personalized passive-user solution.'),
('The receiver estimates only its clock offset because the broadcast message already supplies its coordinates','The broadcast supplies satellite information; receiver position remains an unknown to solve.'),
('Each satellite solves the receiver coordinates separately, and the receiver averages those finished fixes','A single satellite’s ranging message does not supply an individual solved user position; the receiver combines measurements in its own solution.')],stem='The slides say that satellites calculate positions in a global frame. Which interpretation avoids incorrectly extending that shorthand to a claim that satellites solve each user’s position?')
Q(19)['conflictResolution'].update(sourceClaim='Physical page 1207 says GNSS satellites calculate positions in a global 3D reference frame; page 1208 says satellites compute positions in ECEF. Neither sentence literally says each user position.',basis='Distinguish the quoted shorthand from the receiver’s own positioning calculation, using the receiver statement on page 1208 and the linked SPS equations.',method='Read the exact wording without inserting user into the quotation; identify receiver coordinates and clock bias as the unknowns in the primary SPS measurement model.',sourceId='lectures',sourceSha256=SHA,physicalPage=1207)
Q(19)['citations'][1]['role']='premise'
Q(20)['stem']='In the ellipsoidal geodetic convention defined by the linked Navipedia conversion reference, what does (φ, λ, h) denote?'
Q(20)['solution']['justification']='The PDF names latitude, longitude and height but does not define the height datum. Navipedia’s ellipsoidal-coordinate definition specifies height above the reference ellipsoid.';Q(20)['solution']['simpleExplanation']=Q(20)['solution']['justification']
revise(23,[
('Car example: UTM (Universal Transverse Mercator), 2D grid X,Y for maps and routes; rover example: local tangent X,Y,Z for motion control and sensor fusion','These are the two branches printed in the diagram, offered as application examples rather than exclusive rules for every vehicle.'),
('Car example: local tangent X,Y,Z for maps and routes; rover example: UTM (Universal Transverse Mercator), 2D grid X,Y for control and fusion','This exchanges the two coordinate-system branches shown in the source.'),
('Car example: UTM (Universal Transverse Mercator), latitude and longitude in degrees; rover example: local tangent X,Y,Z for control and fusion','The car branch produces projected 2D grid coordinates, not the unchanged angular receiver outputs.'),
('Car example: UTM (Universal Transverse Mercator), 2D grid X,Y for maps and routes; rover example: Earth-centered X,Y,Z for control and fusion','The rover branch is local tangent coordinates, not the global Earth-centered frame.')],stem='Which pairing matches the car-navigation and autonomous-rover examples in the coordinate-conversion diagram?')
Q(23)['assumptions']=['Treat the diagram as two example design choices, not mandatory or exclusive frame choices for every car or rover.'];Q(23)['type']='match'
revise(26,[
('Code: positive ionospheric and tropospheric contributions; carrier phase: opposite ionospheric sign but the same tropospheric sign','The PDF supplies the atmospheric premise. The linked primary code and carrier equations distinguish the ionospheric signs while retaining the tropospheric term.'),
('Code: positive ionospheric and tropospheric contributions; carrier phase: both atmospheric signs reversed','Only the first-order ionospheric contribution reverses sign in these two observation models.'),
('Code and carrier phase: the same positive ionospheric and tropospheric signs','This applies the code-delay interpretation to the carrier ionospheric term without its sign reversal.'),
('Code: negative ionospheric and positive tropospheric contributions; carrier phase: both positive','This reverses which observable has the positive first-order ionospheric range contribution.')],stem='Using the linked primary code and carrier-phase range models, how should the slide’s atmospheric-delay explanation be qualified?')
Q(26)['solution']['formulas']=[]
form(26,'P_atm=T+I; Phi_atm=T−I',{'P_atm':'Atmospheric contribution to code pseudorange','Phi_atm':'Atmospheric contribution to carrier phase expressed as a range','T':'Tropospheric range delay','I':'Positive first-order ionospheric code-range delay at the chosen frequency'},{'P_atm,Phi_atm,T,I':'m'},['Compare the same ray and frequency in the stated primary model; these terms omit geometry, clocks, ambiguity and other non-atmospheric contributions.'])
revise(29,[
('PDOP 2: low; PDOP 4: moderate; PDOP 7: high','Each chosen value lies away from the ambiguous shared boundary at 3 and belongs to the displayed band.'),
('PDOP 2: high; PDOP 4: moderate; PDOP 7: low','This reverses the low/high ordering of geometric dilution.'),
('PDOP 2: low; PDOP 4: low; PDOP 7: high','Four belongs to the printed moderate band, not the low band.'),
('PDOP 2: moderate; PDOP 4: moderate; PDOP 7: high','Two lies inside the printed low band, not the moderate band.')],stem='Using the slide’s illustrative low band approximately 1–3, moderate band 3–6 and high band greater than 6, how are PDOP values 2, 4 and 7 classified?')
Q(29)['assumptions']=['Do not resolve the overlapping written boundary at 3; none of the test values equals that boundary. These bands are illustrative, not universal accuracy guarantees.'];Q(29)['citations'][0]['kind']='statement';Q(29)['conflictResolution']['method']='Compare each supplied value with the actual bulleted intervals, leaving the shared endpoint 3 unresolved.'
revise(37,[
('No transfer is available there unless the graph explicitly encodes one','A geometric crossing is not by itself an adjacency relation; it may represent a non-junction crossing.'),
('A transfer is available because intersecting line segments imply the same graph vertex','This confuses a geometric intersection of the drawing with an explicitly encoded junction.'),
('A transfer is available whenever both crossing roads are undirected','Undirected edges allow travel both ways along each encoded edge, not switching between unrelated crossing edges.'),
('A transfer is available if their coordinates share the crossing point, even when their endpoint identifiers differ','Sharing an interior geometric location does not add a junction vertex or edges to the stored topology.')])
# Numerical/code repairs use explicit finite supplied inputs and complete models.
Q(42)['stem']='The linked code states lat = 28.6139 + (300 − y) × 0.00006 and lon = 77.2090 + (x − 300) × 0.00006, rounded to 5 decimals. For (x,y) = (400,200), what is the displayed pair?'
Q(42)['citations'][1]['kind']='figure';Q(42)['citations'][1]['locator']='Printed slide 24: graphical demo’s synthetic latitude/longitude readout; conversion body is in the official notebook'
Q(42)['solution']['steps']=['Compute 300−200=100 and 400−300=100 plot units.','Each offset is 100×0.00006=0.006 degrees.','Add to the corresponding references: latitude 28.61990, longitude 77.21500 degrees.']
Q(44)['stem']='A synthetic fix is (150,420). Candidate nodes are N9=(140,430), N10=(330,420), N5=(110,270), and N1=(90,110). Which does Euclidean nearest-node matching select?'
Q(44)['solution']['steps']=['Squared distances to N9,N10,N5,N1 are 200, 32400, 24100 and 99700 plot units squared.','The smallest squared distance is 200, so select N9.'];Q(44)['solution']['formulas'][0]['assumptions']=['The four listed candidates use the same planar plotting coordinate frame and unit; no other candidate is included in this supplied comparison.']
revise(45,[('A, the first equally nearest candidate visited','After A sets best_dist, the equal distance for B does not satisfy the strict less-than comparison.'),('B, the last equally nearest candidate visited','This would follow from replacing on less-than-or-equal, not the actual strict less-than update.')])
Q(45)['optionCountRationale']='The stipulated exact two-candidate tie has two credible outcomes, first or last. Two options avoid inventing unsupported list returns or exceptions.';Q(45)['solution']['steps']=['A sets the current best distance.','B has the same distance, so d < best_dist is false; A remains.']
revise(46,[
('Projection (50,0), distance 2 units; either endpoint is about 50.04 units away','The orthogonal foot lies halfway along the segment. Its residual is vertical with length 2; either endpoint distance is sqrt(2504).'),
('Projection (50,0), distance 4 units; either endpoint is 2504 units away','These are squared distances, not Euclidean distances; their units would be squared plot units.'),
('Projection (0.5,0), distance about 49.54 units; either endpoint is about 50.04 units away','This adds the dimensionless fraction 0.5 as a displacement instead of multiplying it by the 100-unit segment vector.'),
('Projection (100,0), distance about 50.04 units; either endpoint is about 50.04 units away','This can result from clamping the unnormalized dot product instead of the normalized segment parameter; the true parameter is 0.5, not 1.')])
revise(49,[
('Repeated triangle inequalities make the direct Euclidean distance no larger than the sum of path-segment lengths','With a common positive scale and unrounded Euclidean edges, the norm of the total displacement is at most the sum of the segment norms.'),
('Nonnegative edge costs alone make Euclidean distance a lower bound, even when those costs are travel times','Nonnegativity does not relate arbitrary cost units to geometric distance; a compatible metric and scale are required.'),
('Rounding every edge downward preserves the bound because a shorter sum is always a safer lower-bound comparison','A smaller stored path cost can fall below the unrounded direct distance, breaking admissibility for that rounded graph.'),
('The triangle inequality makes the sum of segment lengths no larger than the direct distance','This reverses the triangle inequality; a detouring broken path is generally at least as long as the straight displacement.')])
Q(49)['assumptions']=['This is an explicitly unrounded geometric-graph variant, not the source’s rounded ADJACENCY costs. All edge costs and the heuristic use the same positive scale.'];Q(49)['solution']['formulas'][0]['variables'].update({'i':'Segment index from 0 to k−1','p_0,p_k':'Start and goal positions'});Q(49)['solution']['formulas'][0]['units']['norms and their sum']='same plotting length unit before the common positive scale'
Q(50)['stem']='The code stores edge N2–N3 as 2.00 demo km but uses h(N2,N3)=sqrt(200²+10²)/100≈2.002498 demo km. What does this example show?'
Q(50)['solution']['formulas'][0]['assumptions']=['The direct stored edge is a feasible remaining path; the shortest graph cost is therefore at most 2.00 demo km. The heuristic is unrounded.'];Q(50)['solution']['steps']=['The direct stored edge gives a feasible cost of 2.00 demo km.','The heuristic is about 2.002498, which exceeds that feasible cost and thus also exceeds the true shortest remaining cost.']
Q(50)['conflictResolution'].update(sourceClaim='Physical page 1216 stores round(euclidean(a,b),2), while page 1223 sets heuristic(a,b) to euclidean(a,b) without rounding.',method='Evaluate the N2–N3 coordinate difference in the unrounded heuristic and compare it with the direct rounded edge cost; this exhibits a concrete admissibility counterexample rather than a claim that every search fails.')
Q(51)['stem']='An author-added test compared the unchanged source A* with Dijkstra on all 144 ordered node pairs in its 12-node graph and found equal path costs. What is justified?'
Q(51)['experimentProvenance']={'path':f'audits/{B}-v2-author-computations.json','check':'All 144 ordered pairs compared against separate Dijkstra implementation','independentReview':False}
revise(54,[
('Sum individually rounded edges for graph cost; round the sum of raw edge lengths for waypoint totals','The two procedures need not commute. They produce 9.07 and 9.08 demo km for this route without requiring a mathematical error.'),
('Round the raw total for graph cost; sum individually rounded edges for waypoint totals','This reverses which source function uses each rounding procedure.'),
('Round the cumulative total after every edge and reuse that rounded accumulator for waypoint totals','build_waypoints retains the unrounded cumulative variable; only each emitted cumulative_km field is rounded.'),
('Sum the rounded cumulative waypoint entries to recover the graph’s route cost','Cumulative entries repeatedly include earlier edges, so adding those entries double-counts distance instead of summing individual edges.')],stem='The official code searches with round(d(edge),2), but build_waypoints accumulates raw d(edge) before rounding each emitted cumulative value. The highlighted route has graph cost 9.07 demo km and raw total 9.0830789 demo km. Which pair of procedures explains its displayed waypoint total 9.08 demo km?')
Q(54)['citations'][1]['kind']='figure';Q(54)['citations'][2]['kind']='table';Q(54)['solution']['formulas'][0]['variables']['i']='Edge index along the route';Q(54)['solution']['formulas'][0]['assumptions']=['Use the same route in both computations; round to nearest hundredth only at the specified stages.'];Q(54)['solution']['steps']=['Sum the stored two-decimal edge weights to obtain 9.07 demo km.','Sum the original Euclidean edge lengths to obtain about 9.0830789 demo km.','Round that raw cumulative sum to 9.08 demo km; do not add already-cumulative waypoint rows.']
Q(57)['stem']='The source’s ordered waypoint cumulative values are 0, 1.90, 3.91, 5.73, 7.33 and 9.08 demo km for N9,N10,N11,N12,N8,N4. current_waypoint returns the first value at least travelled−10^-6 demo km. Which target is returned at 60% of 9.08 demo km?'
Q(57)['citations'][0]['kind']='table';Q(57)['citations'][1]['kind']='figure';Q(57)['solution']['formulas'][0]['variables'].update({'i':'Waypoint index in route order','alpha':'Supplied route fraction 0.60','epsilon':'Comparison tolerance, 10^-6 demo km'});Q(57)['solution']['formulas'][0]['assumptions']=['Use the displayed cumulative values in route order and the exact source comparison; this is a supplied progress fraction, not a new GNSS measurement.'];Q(57)['solution']['steps']=['Compute 0.60×9.08=5.448 demo km.','The previous threshold 3.91 is below 5.448−10^-6; 5.73 is the first threshold at least that value.','Return N12, the fourth waypoint.']
Q(58)['stem']='The source returns the first waypoint with cumulative_km ≥ travelled−10^-6. At travelled=3.91 demo km with cumulative values 0,1.90,3.91,5.73 demo km, which value is returned?';Q(58)['citations'][0]['kind']='figure';Q(58)['solution']['formulas'][0]['variables']['i']='Waypoint index in route order';Q(58)['solution']['steps']=['The threshold is 3.91−0.000001=3.909999 demo km.','The first two cumulative values fail the test; 3.91 passes and is returned.'];Q(58)['solution']['justification']='The executable >= comparison returns the equal-distance waypoint. The docstring’s next not-yet-reached wording is looser than this exact boundary behavior.';Q(58)['solution']['simpleExplanation']=Q(58)['solution']['justification']
revise(59,[
('Repeated state measurement or estimation, followed by an error-dependent law producing motion commands','A closed loop needs updated state and a command that responds to tracking error; the supplied distance-threshold lookup alone does neither.'),
('Fresh position estimates used only to redraw the route, while motion commands remain fixed in advance','Updating a display does not make the actual command depend on tracking error.'),
('A motion-command generator driven only by elapsed time and the planned speed profile','This is open-loop playback if it does not use measured or estimated tracking state.'),
('New state measurements used only to advance the waypoint label, with no command computed from the error','Waypoint management can support tracking, but by itself does not implement the feedback law that drives the vehicle.')])
Q(59)['citations'][0]['kind']='statement';Q(59)['conflictResolution']['method']='Contrast the actual feedback narrative and screenshot with the official current_waypoint threshold loop and run_pipeline supplied progress fraction; no repeated sensor read or motion-command computation exists in those functions.'
revise(61,[
('B: 6 minutes; A: 12 minutes','Time is distance divided by speed; converting hours to minutes gives 6 for B and 12 for A.'),
('A: 4 minutes; B: 6 minutes','This treats each kilometre as one minute, ignoring the two different specified speeds.'),
('B: 0.1 minutes; A: 0.2 minutes','Those are the correct values in hours, mislabeled as minutes without multiplying by 60.'),
('A: 300 minutes; B: 600 minutes','This applies 60 times speed divided by distance, reversing the distance-over-speed relation.')],stem='Route A is 4 km at 20 km/h; route B is 6 km at 60 km/h. With constant speeds and no stops, which route/time comparison is correct?')
Q(61)['solution']['steps']=['A: 60×4/20=12 minutes.','B: 60×6/60=6 minutes; B is faster despite its greater distance.']
revise(62,[
('Preprocessing can accelerate repeated shortest-path queries, with runtime still dependent on the graph and implementation','The source places Contraction Hierarchies in the precomputed-graph/search-speed role, not as a universal fixed-time guarantee.'),
('The main purpose is to avoid any preprocessing by repeating the same full graph search for every query','This reverses the stated precomputation-versus-query-time tradeoff.'),
('The main purpose is to reduce every query’s cost by discarding roads that are not on the previous query’s route','A previous route is not a sufficient network for arbitrary future endpoints; that would change the routing problem.'),
('The main purpose is to change the objective from shortest road route to straight-line displacement','Search acceleration should preserve the chosen routing objective, not replace road-constrained cost by unconstrained geometry.')])
Q(62)['citations'][1]['kind']='table'
revise(63,[
('Update the road’s feasibility or cost and compute a replacement route that respects the closure','Advancing a waypoint index cannot repair a path that still contains an unavailable edge.'),
('Remove the waypoint at the closed road and connect its predecessor directly to its successor without checking the graph','Skipping a waypoint does not establish that the resulting shortcut is a permitted road connection.'),
('Increase the closed edge’s cost in the map but keep executing the previously selected path without rechecking it','A map update alone does not change a route already selected and being followed.'),
('Choose a reachable nearby detour node and rejoin the old route before the same closed edge','That local maneuver still leads back to the unavailable part unless the replacement route actually bypasses it.')])
revise(64,[
('Complementary observations can sustain state estimation during noisy or missing GNSS, while uncertainty and drift still need management','The cited fusion examples combine information rather than removing the need for measurement models or uncertainty tracking.'),
('Averaging sensor coordinates directly is sufficient even when their reference frames and timestamps differ','Measurements must be expressed consistently in the estimation model; a raw average of mismatched frames or times is not a valid fusion rule.'),
('Treating correlated measurements as independent is beneficial because it counts the same information with greater confidence','Double-counting correlated information can make uncertainty estimates overconfident rather than add independent evidence.'),
('The filter can leave inertial biases unmodeled because GNSS fixes before the outage permanently remove future drift','Bias effects can accumulate during the outage; a past correction does not make future dead reckoning immune to them.')])
Q(64)['citations'][0]['kind']='table'
revise(50,[
('The heuristic can slightly exceed the graph’s true remaining cost','The direct stored edge costs 2.00 demo km, below the unrounded estimate; a true shortest route can cost no more than that feasible edge.'),
('Displaying the heuristic rounded to 2.00 makes the unrounded priority calculation admissible','Formatting an output does not change the value actually used by the search.'),
('A small relative excess is permitted by the exact admissibility inequality','The mathematical bound is h≤true cost; no relative tolerance was added to that definition.'),
('Agreement with Dijkstra on this graph would prove that the heuristic never overestimates','Matching returned path costs can coexist with a heuristic overestimate; algorithm outcomes and the pointwise bound are different properties.')])
revise(51,[
('Those finite cases matched, despite a separate rounding-related heuristic guarantee gap','The experiment establishes agreement for the tested graph and endpoints, not a universal property of every heuristic value.'),
('Matching route costs proves every heuristic value is below the true remaining cost','Returned path-cost agreement does not logically imply the separate pointwise admissibility condition.'),
('The result proves the same endpoints will match after arbitrary road-weight changes','Changing weights changes the tested problem, so the old finite result does not establish the new outcomes.'),
('The comparison tests only start-to-goal reachability, because Dijkstra cannot compare weighted route costs','A separate Dijkstra calculation does compute weighted shortest costs on this nonnegative graph, so the recorded comparison is stronger than reachability alone.')])
Q(58)['options']=[o for o in Q(58)['options']if o['id']!='o4'];Q(58)['solution']['optionExplanations'].pop('o4');Q(58)['optionCountRationale']='Three credible threshold interpretations are previous, equal and next waypoint; an impossible no-result option is omitted.'
Q(58)['solution']['misconceptions']=[Q(58)['solution']['optionExplanations'][k]for k in('o2','o3')]
# Three new items close accepted-target gaps without changing their accepted originals.
newids=[]
def gap(n,title,stem,rows,citations,typ='conceptual',difficulty='easy',assumptions=None):
 q=copy.deepcopy(old['questions'][0]);qid=f'{B}-Q{n:03}';assert qid not in qm;cid=f'{B}-C-gap-{n}'
 for k in('conflictResolution','primaryEvidence','supplementalProvenance','revisionAuthors'):q.pop(k,None)
 q.update(id=qid,version=1,status='draft',authorId=A,stem=stem,type=typ,difficulty=difficulty,cognitiveSkill='numerical'if typ=='numerical'else'conceptual',subtopic=title,tags=['bounded-coverage-gap'],conceptIds=[cid],assumptions=assumptions or[],options=[dict(id=f'o{i}',text=t)for i,(t,r)in enumerate(rows,1)],correctOptionIds=['o1'],citations=[cite(*c)for c in citations],reviewIds=[])
 q['solution']=dict(justification=rows[0][1],simpleExplanation=rows[0][1],optionExplanations={f'o{i}':('Correct. 'if i==1 else'Incorrect. ')+r for i,(t,r)in enumerate(rows,1)},steps=[],formulas=[],memoryAid=None,misconceptions=[r for t,r in rows[1:]],examTraps=[],prerequisiteConceptIds=[])
 qm[qid]=q;b['questions'].append(q);newids.append(qid)
 b['concepts'].append(dict(id=cid,title=title,description='Bounded meaningful source angle identified by independent coverage challenge.',slideIds=sorted({c['slideId']for c in q['citations']}),questionIds=[qid],status='drafted',topic=q['topic'],subtopic=title,prerequisiteConceptIds=[],examinationAngles=[stem]));return q
q=gap(66,'Planar range consistency and degeneracy','Apply the printed planar circle equations to three supplied cases. I: centers (0,0),(2,0),(0,2), each squared range 2. II: centers (−1,0),(0,0),(1,0), squared ranges 2,1,2 respectively. III: the same centers as I, each squared range 1. Coordinates are in metres and squared ranges in m². How many common points satisfy all three equations in each case?',[
('I: one; II: two; III: none','I gives (1,1). II gives mirror points (0,1) and (0,−1). In III the first two circles meet only at (1,0), which fails the third range.'),
('I: one; II: one; III: none','This assumes three references always remove reflection ambiguity; the collinear centers in II leave two symmetric solutions.'),
('I: one; II: none; III: two','Collinearity does not mean inconsistency in II, and the contradictory ranges in III do not yield two solutions.'),
('I: two; II: two; III: one','Noncollinear centers remove the two-way ambiguity in consistent case I, while inconsistent case III has no exact common point.')],[(1203,'equation','Three planar circle equations with matched indices'),(1203,'statement','Unqualified unique-point claim below the equations','conflict')],'numerical','medium',['Use exact noiseless circle equations with no additional clock unknown; these coordinates and squared ranges are supplied variants, not read from the drawing.','Use the matched-index equations, not the drawing’s swapped R1/R3 labels. This is planar range geometry, not a claim about every full GNSS solution.'])
q['conflictResolution']=dict(status='derived-qualification-pending-independent-review',questionVersion=1,sourceId='lectures',sourceSha256=SHA,physicalPage=1203,sourceClaim='The page says simultaneous solution of three planar circle equations will give a unique point.',basis='Uniqueness needs suitable geometry and consistent ranges; exact collinear references can retain mirror ambiguity and inconsistent ranges can yield no common point.',method='Subtract pairs of the explicitly supplied circle equations and substitute the resulting coordinates into all original equations.',scope='The supplied planar cases only; independent review required.')
q['solution']['steps']=['Case I: subtract the first circle from the second to obtain x=1; subtract it from the third to obtain y=1. The point satisfies squared range 2 for all three centers.','Case II: the center circle gives x²+y²=1. Subtracting it from the left circle gives 2x+1=1, so x=0 and y=±1. Both satisfy the right circle.','Case III: the first two unit circles force x=1,y=0. The squared distance to (0,2) is 5, not 1, so no common point exists.','The examples separate a unique consistent noncollinear solution, a collinear mirror ambiguity, and inconsistent measurements.']
form(66,'(x−x_i)²+(y−y_i)²=R_i; −2(x_j−x_i)x−2(y_j−y_i)y+(x_j²+y_j²−x_i²−y_i²)=R_j−R_i',{'x,y':'Unknown planar point','x_i,y_i':'Coordinates of reference center i','R_i':'Supplied squared range to reference i','i,j':'Distinct reference indices'},{'x,y,x_i,y_i':'m','R_i and every term of the subtracted equation':'m²','i,j':'indices'},['Exact Euclidean planar circles; all three equations must hold simultaneously; no extra time-bias unknown.'])
q=gap(67,'Direct reflected and diffracted path labels','Which association matches the labeled radio paths in the GNSS-error figure?',[
('Green direct path: LOS; red building and dark-blue ground paths: reflection; blue roof-edge and yellow tree paths: diffraction','These associations follow the actual separate labels in the drawing; no relative error severity is inferred.'),
('Green direct path: LOS; red building and dark-blue ground paths: diffraction; blue roof-edge and yellow tree paths: reflection','This interchanges the drawing’s reflected and diffracted path labels.'),
('Green direct path: reflection; red building and dark-blue ground paths: LOS; blue roof-edge and yellow tree paths: diffraction','The green ray is explicitly LOS, while the two bent surface-contact paths are labeled reflected.'),
('Green direct path: LOS; red building path: reflection; dark-blue ground and both edge/tree paths: diffraction','The ground-bounce path is labeled reflected, not diffracted; the two edge/tree paths carry the diffraction labels.')],[(1210,'figure','Right-hand figure: green LOS, red building reflection, dark-blue ground reflection, blue building-edge diffraction, yellow tree diffraction','explicit')],'diagram','easy',['Identify the source’s labels only; do not infer diffraction equations or a universal ranking of position error from the drawing.'])
q=gap(68,'Named HMM map-matching model','The lecture names a Hidden Markov Model (HMM) over candidate road segments. Which interpretation best connects that named model with its sequence-of-fixes example?',[
('Candidate road segments are hidden states; successive noisy fixes are observations used to infer a plausible segment sequence','The lecture links candidate segments and a sequence of fixes. The hidden segment identity is inferred rather than treated as directly observed.'),
('Candidate road segments are directly measured observations; GNSS fix coordinates are the hidden states to infer','This reverses the observed fix data and the unobserved road-segment association.'),
('Each fix selects its nearest node independently; calling those choices an HMM supplies sequence information without transition modeling','Independent nearest-node snapshots do not encode how candidate segment states evolve across the fix sequence.'),
('The HMM hidden state is only the final destination, so recent fixes need not distinguish intermediate road segments','The cited HMM example is over candidate road segments, not merely the destination label.')],[(1222,'statement','HMM over candidate segments after sequence/heading discussion','premise'),(1227,'table','Map Matching row: nearest segment plus HMM over a sequence of fixes','premise')],'conceptual','easy',['Interpret the named HMM as the lecture’s example, not a requirement that every production navigation system use this model. No HMM parameter derivation is requested.'])
for n in(8,13):
 Q(n)['solution']['formulas'][0]['variables']['i']='Satellite measurement index'
 Q(n)['solution']['formulas'][0]['units']['i']='index'
 Q(n)['solution']['formulas'][0]['assumptions'].append('Receiver and satellite vectors use the same Cartesian reference frame and length unit.')
Q(50)['solution']['formulas'][0]['variables']['goal']='Target vertex N3'
Q(50)['solution']['formulas'][0]['units']['goal']='vertex label'
# More precise kinds/locators reflect actual pixels, not broad code labels.
for n in(4,5):Q(n)['citations'][0]['locator']='Printed slide 6: system-country bullet pairs and multiple-constellation statement; regional/availability qualification is from item-linked primary evidence'
Q(16)['citations'][0]['locator']='Printed slide 9: three position unknowns plus one receiver clock unknown';Q(16)['citations'][1]['locator']='Printed slide 16: spread-versus-clustered geometry and amplified position errors'
Q(20)['citations'][0]['locator']='Printed slide 12: latitude, longitude and unspecified height; ellipsoidal height definition is supplied by the linked primary reference'
Q(26)['citations'][0]['locator']='Printed slide 15: ionosphere/troposphere delay prose; carrier-phase distinction is from the linked primary equations'
Q(45)['citations'][0]['locator']='Printed slide 25: map_match(fix) call and nearest-node premise; strict comparison is in the linked notebook function'
Q(54)['citations'][1]['locator']='Printed slide 28: highlighted route and 9.08 km display';Q(54)['citations'][2]['locator']='Printed slide 29: displayed cumulative waypoint table; raw accumulator code is notebook-only'
Q(57)['citations'][0]['locator']='Printed slide 29: six cumulative waypoint values';Q(57)['citations'][1]['locator']='Printed slide 30: waypoint-tracking screenshot; comparison rule and 60% input are notebook-only'
Q(58)['citations'][0]['locator']='Printed slide 30: tracking screenshot and linked repository; exact equality/epsilon behavior comes from current_waypoint'
form(50,'h(N2,N3)=sqrt((x_2−x_3)²+(y_2−y_3)²)/k; w(N2,N3)=round(h(N2,N3),2)',{'x_2,y_2,x_3,y_3':'N2 and N3 plotting coordinates; differences are 200 and 10 plot units','k':'100 plot units per demo km','h':'Unrounded heuristic','w':'Stored direct edge weight'},{'coordinates':'plot units','k':'plot units per demo km','h,w':'demo km'},['Artificial plotting scale from the source; round the stored edge to nearest hundredth.'])
Q(66)['solution']['formulas'][0]['variables'].pop('x_i,y_i')
Q(66)['solution']['formulas'][0]['variables']['x_i,y_i,x_j,y_j']='Coordinates of distinct reference centers i and j'
# Complete every formula record, including the code comparison assumptions.
for n in(8,13,42,44,45,46,49,50,54,57,58,61,66):
 q=Q(n)
 for f in q['solution']['formulas']:
  assert f['expression'] and f['variables'] and f['units']
  if not f['assumptions']:f['assumptions']=['Use the question’s explicitly supplied finite inputs and the stated source convention.']
Q(42)['solution']['formulas'][0]['variables'].update({'LAT0,LON0':'Reference display coordinates 28.6139 and 77.2090 degrees','k':'Display scale 0.00006 degrees per plotting unit','300':'Reference plotting coordinate, in plot units'})
# Fix ordinary prose spacing in changed objects only; never rewrite code, formulas, evidence text or accepted objects.
replacements={'bands1':'bands 1','include3':'include 3','scale0.00006':'scale 0.00006','coordinate300':'coordinate 300','tolerance10^-6':'tolerance 10^-6','all144':'all 144','its12':'its 12','at60':'at 60','of9.08':'of 9.08','is9.':'is 9.','cost9.':'cost 9.','total9.':'total 9.','by100':'by 100','distance2':'distance 2','to28.':'to 28.','and77.':'and 77.','is200':'is 200','N9,N10,N5,N1':'N9, N10, N5, N1','is+':'is +','order(lat,lon)':'order (lat, lon)','is√':'is √','is180':'is 180','costs2.00':'costs 2.00','positive2.00':'positive 2.00','Its3.91':'Its 3.91','below5.448':'below 5.448','than3.909999':'than 3.909999','is(50,2)':'is (50,2)','5.448;5.73':'5.448; 5.73'}
def clean(v):
 if isinstance(v,str):
  for a,z in replacements.items():v=v.replace(a,z)
  return v
 if isinstance(v,list):return [clean(x)for x in v]
 if isinstance(v,dict):return{k:(x if k=='evidenceText'else clean(x))for k,x in v.items()}
 return v
changed=[q for q in b['questions']if q['id']in flags or q['id']in newids]
for q in changed:
 z=clean(q);q.clear();q.update(z)
 random.Random(q['id']+'-v2-author-order').shuffle(q['options'])
 if q['type']in('numerical','algorithm_trace') and not q['solution']['steps']:raise AssertionError(q['id'])
 assert len({o['text']for o in q['options']})==len(q['options'])
 assert {o['id']for o in q['options']}==set(q['solution']['optionExplanations'])
 assert q['status']=='draft' and not q['reviewIds']
for c in b['concepts']:
 c['questionIds']=[q['id']for q in b['questions']if c['id']in q['conceptIds']];c['examinationAngles']=[q['stem']for q in b['questions']if c['id']in q['conceptIds']]
 c['slideIds']=sorted(set(c['slideIds']+[z['slideId']for q in b['questions']if c['id']in q['conceptIds']for z in q['citations']]))
inspection=read(f'data/inspection-batches/archive/{B}-v1.json')
for s in inspection['slides']:s['conceptIds']=[c['id']for c in b['concepts']if s['id']in c['slideIds']]
assert all(qhash(qm[qid])==h and qm[qid]==next(q for q in old['questions']if q['id']==qid)for qid,h in accepted.items())
assert all(q['correctOptionIds']==qm[q['id']]['correctOptionIds']for q in old['questions'])
assert fhash(f'audits/{B}-source-qualifications.json')==fhash(f'audits/archive/{B}-source-qualifications-v1.json')
# Preserve original ten annotations literally; precise current amendments are separate, never silently replacing source history.
amendments={'authorId':A,'independentReview':False,'originalQualificationFile':f'audits/{B}-source-qualifications.json','originalQualificationSha256':fhash(f'audits/{B}-source-qualifications.json'),'originalTenRecordsPreserved':True,'currentQuestionAmendments':[{'questionId':Q(n)['id'],'questionVersion':Q(n)['version'],'conflictResolution':Q(n).get('conflictResolution'),'primaryEvidence':Q(n).get('primaryEvidence',[])}for n in(19,29,50,59,66)],'additionalSourceAnnotations':[{'physicalPage':1203,'printedSlideNumber':'7','sourceSha256':SHA,'region':'Lower-left three-circle figure versus three matched-index equations','finding':'Upper P1 is labeled R3 and lower-left P3 is labeled R1 in the drawing; equations pair i with r_i. Equation-scoped questions preserve matched indices and do not ask students to memorize the label swap.'},{'physicalPage':1226,'region':'Official notebook current_waypoint docstring versus comparison','finding':'The next not-yet-reached docstring is loose at exact equality: executable >= with 1e-6 returns the reached threshold. This is a notebook boundary qualification, not code printed on the PDF page.'}],'roundingStatus':'Graph sum of rounded edges 9.07 and rounded raw waypoint sum 9.08 are different specified operations, not a mathematical defect.'}
write(f'audits/{B}-v2-source-qualification-amendments.json',amendments)
write(f'audits/{B}-v2-primary-evidence.json',[{'questionId':q['id'],'questionVersion':q['version'],'primaryEvidence':q.get('primaryEvidence',[]),'supplementalProvenance':q.get('supplementalProvenance')}for q in changed if q.get('primaryEvidence')])
b['coverageNote']='27 flagged objects revised; 38 accepted whole objects and hashes preserved. Q023 closes the conversion-branch gap; three new items close planar consistency/uniqueness, figure radio-path labels, and named HMM interpretation. All 30 changed/new items require independent review; total 68.'
write(f'audits/{B}-v2-working.json',b);write(f'audits/{B}-v2-working-inspection.json',inspection)
write(f'audits/{B}-v2-coverage-closure-author.json',{'independentReview':False,'revisedCount':27,'newCount':3,'acceptedCount':38,'totalQuestions':68,'gapQuestions':{'L39-GAP-planar-uniqueness':Q(66)['id'],'L39-GAP-conversion-branches':Q(23)['id'],'L39-GAP-radio-path-labels':Q(67)['id'],'L39-GAP-HMM-mapmatching':Q(68)['id']},'sourceQualifications':'Ten original records preserved plus separate exact amendments and radius-label annotation.'})
if os.environ.get('FREEZE_L39_V2')!='1':print('WORKING',len(changed));raise SystemExit(0)
assert read(f'audits/{B}-v2-author-computations.json')['passed'];assert read(f'audits/{B}-v2-integration-validation.json')['valid']
write(f'data/question-batches/{B}.json',b);write(f'data/inspection-batches/{B}.json',inspection)
blind=[{**{k:q[k]for k in('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]}for q in changed]
write(f'audits/blind-{B}-v2.json',blind);packetsha=fhash(f'audits/blind-{B}-v2.json')
write(f'audits/{B}-v2-review-manifest.json',{'batchId':B,'blindPacket':f'audits/blind-{B}-v2.json','blindPacketSha256':packetsha,'questionSha256':{q['id']:qhash(q)for q in changed},'preservedAcceptedHashes':accepted,'revisedCount':27,'newQuestionCount':3,'preservedAcceptedCount':38,'sourceBounds':[1197,1230],'sourceSha256':SHA,'priorBatchArtifact':f'data/question-batches/archive/{B}-v1.json','priorBatchSha256':fhash(f'data/question-batches/archive/{B}-v1.json'),'sourceQualificationSha256':fhash(f'audits/{B}-source-qualifications.json'),'independentReviewPending':True})
(R/f'audits/handoffs/{B}-v2.md').write_text(f'''# L39 v2 frozen\n\n27 revised drafts plus three new gap questions. All 38 accepted whole objects and hashes preserved; total 68. Original keys unchanged. Ten original qualification records remain literally unchanged, with precise current amendments and p1203 radius-label mismatch recorded separately.\n\nPacket: audits/blind-{B}-v2.json\nSHA256: {packetsha}\nManifest: audits/{B}-v2-review-manifest.json\nArchive: data/question-batches/archive/{B}-v1.json\nRepairs: scripts/repair_W08_L39_v2.py (frozen guard)\nChecks: scripts/check_W08_L39_v2.py; audits/{B}-v2-author-computations.json\n\n23 actual source pages revisited. Four bounded gaps closed in Q023 and Q066–Q068 pending independent review. PDF premises distinguished from primary references and exact notebook functions. Source notebook executes unchanged; graph9.07 versus waypoint9.08 remains intentional different rounding. Q045 uses two plausible tie outcomes with explicit option-count rationale. All changed content remains draft. No canonical or Git writes.\n''')
print('FROZEN',packetsha)
