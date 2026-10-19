#!/usr/bin/env python3
"""Repair frozen L10 quality findings without changing the 44 accepted hashes."""
from pathlib import Path
import copy,json,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W02-L10.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
ids={8,24,27,37,40,41,47,50,51,52,54,56,57};author='robotics-integration-L10-v2-revision-author'
archive=R/'audits/batch-history/W02-L10-v1-flagged-before-v2.json';assert not archive.exists()
archive.write_text(json.dumps([q for q in b['questions'] if int(q['id'][-3:]) in ids],ensure_ascii=False,indent=2)+'\n')
changes={
8:{3:('Their angular velocities match, and v3−v2=p23×ω','The velocity increment is ω×p23; reversing the cross-product order reverses its sign.')},
24:{2:('Treat joints as locked → project the hand wrench directly onto every joint axis → omit load transport between origins','Each joint requires the moment about its own origin, so distal loads must be transported before projection.'),3:('Treat joints as locked → write only force balance → project force onto each revolute joint axis','Revolute effort is the axis component of moment, and force balance alone cannot determine it.'),4:('Treat joints as locked → write only moment balance → project moment onto each prismatic joint axis','Prismatic effort is the axis component of force; its force balance cannot be replaced by moment projection.')},
27:{2:('From the base toward the hand, treating the prescribed hand wrench as the base boundary load','The prescribed load acts at the hand, not at the base; upstream moments must account for the changing lever arms.'),3:('From the hand toward the base, but restart every link from the original hand moment without carrying offset moments','The direction is inward, but the moment must accumulate each translated force contribution.'),4:('From the hand toward the base for forces, but from the base toward the hand for moments','Both force and moment are propagated inward from the same distal wrench boundary.')},
37:{4:('(6,7) N·m','This uses J³F instead of (J³)ᵀF: [[2,0],[1,1]](3,4)=(6,7), the wrong map for joint torque.')},
40:{3:('τ1=τ2=0, which proves the arm can support an arbitrarily large axial load','Zero ideal actuator torque does not remove structural stress, buckling, bearing limits or material load limits.')},
41:{3:('Add M only to τ1','The distal joint also transmits the terminal couple, so its torque must increase by M.'),4:('Subtract M from both τ1 and τ2','This reverses the specified exerted-couple sign; the unchanged positive joint convention requires adding M.')},
47:{3:('1.3 W','This omits joint 1: −0.8+2.1=1.3 W, instead of including its +0.6 W contribution.'),4:('3.5 W','This replaces the negative joint-2 contribution by its absolute value: 0.6+0.8+2.1=3.5 W.')},
50:{3:('A locked relative joint implies that the entire rigid body has zero angular velocity','No relative motion between the frames does not imply zero inherited rigid-body angular velocity.'),4:('The relative rate may be nonzero as long as the two frame origins coincide','Coincident origins do not suppress a relative angular rate; the fixed-body assumption concerns orientation as well.')},
51:{3:('Because one may use −[p]×R while retaining p in A coordinates','The equivalent reordered form requires the rotated offset: −[Rp]×R, not −[p]×R with p still in A.'),4:('Because only v_A needs rotation, while ω×p can be added unchanged in A components','All terms in the final B-coordinate velocity must use B components; R acts on the complete sum.')},
56:{3:('Rotate linear velocity and force, but leave angular velocity and moment components unchanged','Angular velocity and moment are vectors too, so a change of basis rotates their components.'),4:('Use the forward rotation for linear velocity and its inverse for angular velocity in the same output frame','Both components of one twist must be expressed in the same target basis, using the same coordinate rotation.')}
}
for q in b['questions']:
 n=int(q['id'][-3:])
 if n not in ids:continue
 prior=question_hash(q);q.update(version=2,status='draft',reviewIds=[]);q.setdefault('revisionAuthors',[]).append(author)
 q.setdefault('revisionHistory',[]).append({'version':2,'authorId':author,'revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'priorQuestionSha256':prior,'reason':'Apply frozen independent quality/assumption/citation findings; answer key unchanged.'})
 for i,(text,expl) in changes.get(n,{}).items():
  oid=f'choice-{i}'
  next(o for o in q['options'] if o['id']==oid)['text']=text;q['solution']['optionExplanations'][oid]=expl
 q['solution']['misconceptions']=[v for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']]
 if n in (47,52,54):q['difficulty']='medium'
 if n==47:q['solution']['optionExplanations']['choice-2']='This omits the joint-2 contribution: 0.6+2.1=2.7 W, rather than adding the signed −0.8 W term.'
 if n in (52,54):
  q['stem']=q['stem'].replace('p_A→B=(1,0,0) m','p_A→B=(1,0,0) m expressed in A')
  q['assumptions'].append('The displacement from origin A to origin B is expressed in frame A; F_B and N_B, where present, are expressed in B.')
  if n==52:q['solution']['formulas'][0]['variables']['p^A']='A-to-B origin offset expressed in A'
  else:q['solution']['formulas'].append({'expression':'F_A=R_AB F_B; N_A=R_AB N_B+p_A→B^A×F_A','variables':{'p_A→B^A':'A-to-B origin offset expressed in A','R_AB':'rotation converting B components into A','F_A,F_B':'same force in A and B','N_A,N_B':'moments about the respective origins in their indicated bases'},'units':{'p_A→B^A':'m','R_AB':'dimensionless','F_A,F_B':'N','N_A,N_B':'N·m'},'assumptions':[]})
 if n==57:
  c=copy.deepcopy(q['citations'][0]);c.update(slideId='lectures-p0340',physicalPage=340,locator='Lecture 10, physical PDF page 340, printed slide 15: hand-to-base statics propagation',evidenceText=(R/'sources/text/lectures/page-0340.txt').read_text().strip())
  q['citations'].append(c)
  next(c for c in b['concepts'] if c['id'] in q['conceptIds'])['slideIds'].append('lectures-p0340')
 assert q['correctOptionIds']==next(x for x in old['questions'] if x['id']==q['id'])['correctOptionIds']
assert all(question_hash(q)==question_hash(next(x for x in old['questions'] if x['id']==q['id'])) for q in b['questions'] if int(q['id'][-3:]) not in ids)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[]
for q in b['questions']:
 if int(q['id'][-3:]) not in ids:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W02-L10-v2.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
print('13 repaired drafts; 44 accepted hashes preserved.')
