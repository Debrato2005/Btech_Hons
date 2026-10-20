#!/usr/bin/env python3
"""Union exact crop plans with a question's existing explicit OR derived inputs.
Does not edit questions, source content, or review receipts. Run the sidecar
producer afterwards. Unlike appending to an empty list, this preserves implicit
page-based inputs when the first explicit crop is added.
"""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text())
def write(name,value):
 p=ROOT/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');t.replace(p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('question_id');ap.add_argument('crop_keys',nargs='+');a=ap.parse_args()
 bank=read('data/bank.json');q=next(q for q in bank['questions'] if q['id']==a.question_id)
 plans=read('data/question-visuals/crop-plan.json');over=read('audits/question-visuals/decision-overrides.json');refs=read('audits/question-visuals/source-overrides.json')
 ov=over.setdefault(q['id'],{});oldrefs=refs.get(q['id'],q['citations'])
 current=[]
 for ref in oldrefs:
  if isinstance(ref,int):ref={'sourceId':'lectures','physicalPage':ref}
  ref={'sourceId':ref['sourceId'],'physicalPage':ref['physicalPage']}
  if ref not in current:current.append(ref)
 keys=list(ov['cropKeys']) if 'cropKeys' in ov else [f'{r["sourceId"]}-p{r["physicalPage"]:04}' for r in current if f'{r["sourceId"]}-p{r["physicalPage"]:04}' in plans]
 before=list(keys)
 for key in a.crop_keys:
  p=plans[key]
  if key not in keys:keys.append(key)
  if not any(r['sourceId']==p['sourceId'] and r['physicalPage']==p['physicalPage'] for r in current):current.append({'sourceId':p['sourceId'],'physicalPage':p['physicalPage']})
 ov.update(dependencyStatus='required',cropKeys=keys);refs[q['id']]=current
 write('audits/question-visuals/decision-overrides.json',over);write('audits/question-visuals/source-overrides.json',refs)
 print(json.dumps({'questionId':q['id'],'previousEffectiveCropKeys':before,'currentCropKeys':keys},indent=2))
if __name__=='__main__':main()
