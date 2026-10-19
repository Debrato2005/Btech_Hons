"""Persist actual rendered inspections of L40, whose title prints Lecture 45."""
from pathlib import Path
import json,copy,hashlib,datetime
R=Path(__file__).resolve().parents[1]
NOTES={
1231:'Title is Fuzzy Logic Control and explicitly prints Lecture Number 45; sequence identity remains L40. Footer 1. No assessed numbering trivia.',
1232:'Contents roadmap only: crisp/fuzzy values, membership, inference/defuzzification, two examples, simulation and robotics.',
1233:'Warm/hot/heat/large/a bit/comfortable descriptors highlighted in red. They lack a unique numerical threshold without a defined context; the calendar date is incidental.',
1234:'Context dependence illustrated by the same linguistic pain phrase in different situations. This is a language-modeling example, not a clinically valid diagnostic rule or guidance.',
1235:'Expert-system language ambiguity and exact thermostat rule T≥24 °C inspected; 23.9 °C fails the predicate. No hysteresis or fuzzy cure is actually specified.',
1236:'Fuzzification → rule base → defuzzification roles and Lotfi Zadeh historical attribution inspected. The page does not supply a publication year.',
1237:'Crisp 24 °C versus context-dependent labels inspected. Crisp singleton value does not imply that every crisp set has exactly one member.',
1238:'Membership/truth degrees 0–1 inspected. The prose contrasting one true crisp value is overbroad if read as a definition of all crisp sets; membership degree is not an automatic probability.',
1239:'Design-stage set choices and runtime fuzzification wording inspected. Number/range/representation are designer choices refined by simulation, not unconstrained guarantees of coverage or performance.',
1240:'Actual Gaussian bell and trapezoid sketches inspected. Trapezoid has four breakpoints and rising/plateau/falling line segments. Membership is not required to integrate to one; a chosen trapezoid is not exactly a Gaussian.',
1241:'Triangle and decreasing Z/increasing S sketches inspected. Triangle uses three breakpoints; shoulders can represent persistent low/high saturation. Second-order refers to the illustrated smooth families, not every possible S-shaped function.',
1242:'Three IF–THEN templates inspected: one condition, combined conditions, and multiple consequences. Antecedents describe input conditions and consequents describe outputs.',
1243:'Singleton weighted-average recipe explicitly inspected. Its numerator is membership-weighted singleton output and denominator is the sum of weights; this is not automatically the area centroid of arbitrary fuzzy output shapes.',
1244:'Mamdani figure and clipping/OR/area-centroid procedure inspected. Upper envelope consolidates clipped outputs; OR must not be silently treated as ordinary arithmetic addition.',
1245:'Cooling controller has temperature and humidity inputs and power-setting output. This identifies controlled command, not a measured output temperature.',
1246:'All three graphs inspected. Temperature cold shoulder 60–65 then zero at 70; warm triangle 65,75,85; hot 75,85,95; very-hot rises 90–95. Humidity axis descends 100→40; very-humid shoulder 90–100 with zero at 70, humid triangle 40,60,90, dry shoulder 40–45 with zero at 50. Power axis descends 100→0: fast shoulder 80–100 zero at 50; medium 20,50,80; slow 0,20,50; off shoulder at 0 falling to zero at 20. Marked Hot 0.27 and Humid 0.65 disagree with exact straight-line interpolation at 78 and 70 (0.3 and 2/3); use stated grades separately.',
1247:'All 12 cooling rules read: temperature rows very-hot/hot/warm/cold and humidity columns very-humid/humid/dry yield [fast,fast,medium], [fast,medium,medium], [medium,slow,slow], [slow,off,off].',
1248:'Graphical rule network inspected: only a subset of wiring is drawn; R5 links Hot and Humid to Medium, R8 links Warm and Humid to Slow. Zero antecedents block other rules under min-AND. Do not infer unconnected rules are absent.',
1249:'Reported inputs 78 °F and 70% humidity, grades Warm 0.7, Hot 0.27, Humid 0.65, all others zero. The numeric annotations are authoritative supplied premises for this worked example, not exact reconstruction of p1246 triangle endpoints.',
1250:'Min-AND produces Medium 0.27 and Slow 0.65. Descending output axis has singleton representative centers Slow 20 and Medium 50. AND=min is the selected convention, not the only possible fuzzy conjunction.',
1251:'Weighted singleton result (0.65×20+0.27×50)/0.92=28.8043%, rounded 29%; separate Mamdani area result reported as 34%. Actual output envelope inspected. Reconstruct using explicit breakpoints before claiming exact reproduction of 34%.',
1252:'3D cooling surface axes Temperature, Humidity and Power inspected; power rises generally with temperature/humidity in this designed rule set. Software names FIDE/FUDGE/MATLAB/scikit-fuzzy are listed; no source code or exact simulation settings supplied.',
1253:'Membership/rule entry, inference, input-domain sweep and plot-based refinement inspected. A finite plotted grid alone does not prove every continuous input safe or closed-loop stability.',
1254:'Three applications inspected: rough-terrain action selection, gripping force using size/weight, and color sorting. The force-proportional wording does not supply a universal force law or guarantee slip-free/damage-free operation.',
1255:'Robot example inputs slope and terrain type; output speed. Slope range −45 to +45 degrees with five labels; terrain four labels; speed 0–20 miles/hour with five labels. Source typo slop is recorded as slope, not a separate quantity.',
1256:'All three graphs inspected. Slope shoulders at ±35 to ±45, negative peak about −19 and positive peak about +19; level support about −15 to +15. Exact noninteger endpoints are not supplied in text. Terrain axis descends 100→0: rough triangle 40,60,80; moderate 20,40,60; smooth shoulder 0–20 falling to zero at 40; very-rough rises 60–80. Speed plot has narrow spikes near 3,6,10,15,19 mph; treat as declared singleton representatives only when explicitly assumed, not an unprovided continuous Mamdani shape.',
1257:'Eleven robot rules and 5×4=20 count inspected. Large-positive outputs [very-slow,slow,medium,medium]; positive [very-slow,slow,medium,fast]; level first three [slow,medium,fast].',
1258:'Remaining nine rules inspected: level/smooth→very-fast; negative [very-slow,slow,medium,fast]; large-negative [very-slow,very-slow,slow,medium]. Large positive/negative policies are not exactly symmetric.',
1259:'Actual control surface and reported slope 20°, terrain index 30, speed about 13 mph inspected. Terrain 30 is a designer index halfway between smooth/moderate, not 30% slope. Caption says Mamdani although preceding outputs appear singleton-like; exact inference/sampling settings are absent. Broad speed decrease is a trend, not strict decrease everywhere.',
1260:'Summary repeats membership, rule inference, defuzzification, simulation and applications. Fuzzification is correctly summarized as crisp inputs to membership values; no new calculation.',
1261:'Bibliographic reference to Niku second edition only; no new examinable content.',
1262:'Closing thank-you page only; footer 32.'}
EX={1231:'Title page only; printed Lecture 45 retained separately from L40.',1232:'Contents roadmap only.',1261:'Bibliography only.',1262:'Closing page only.'}
def save(authoring_complete=False):
 maps={s['physicalPage']:s for s in map(json.loads,(R/'sources/page_maps/lectures.jsonl').read_text().splitlines())};slides=[]
 bp=R/'data/question-batches/W08-L40.json';concepts=json.loads(bp.read_text())['concepts'] if bp.exists() else []
 for p,n in sorted(NOTES.items()):
  s=copy.deepcopy(maps[p]);s.update(disposition='excluded' if p in EX else 'examinable',exclusionReason=EX.get(p),conceptIds=[c['id'] for c in concepts if s['id'] in c['slideIds']],lectureId='L40',week=8,lectureTitle='Fuzzy Logic Control',printedLectureNumber=45,printedSlideNumber=str(p-1230),printedSlideNumberStatus='present',printedNumberEvidence='Actual rendered footer and title-page lecture number inspected separately from sequence and physical PDF page.')
  s['visualInspection']={'status':'complete','inspectorId':'build_offline_study_interface:L40-author','inspectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'rendered_page','notes':n+' Actual 1800×1013 page pixels viewed alongside text.','previewSha256':hashlib.sha256((R/s['previewPath']).read_bytes()).hexdigest(),'dimensions':[1800,1013]};slides.append(s)
 (R/'data/inspection-batches/W08-L40.json').write_text(json.dumps({'batchId':'W08-L40','slides':slides},ensure_ascii=False,indent=2)+'\n')
 (R/'audits/W08-L40-page-observations.json').write_text(json.dumps({'sourceId':'lectures','sequenceLectureId':'L40','printedLectureNumber':45,'notes':NOTES,'inspectionComplete':True,'authoringComplete':authoring_complete,'independentReviewComplete':False,'sourceCodePresent':False},ensure_ascii=False,indent=2)+'\n')
 print('Persisted',len(slides),'actual inspections.')
if __name__=='__main__':save()
