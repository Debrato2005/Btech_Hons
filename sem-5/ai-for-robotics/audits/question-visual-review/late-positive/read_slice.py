from pathlib import Path
import json,sys
s=json.loads(Path('audits/question-visual-review/late-positive/snapshot-initial.json').read_text());q={x['id']:x for x in s['questions']};a={x['id']:x for x in s['assets']}
for r in s['records']:
 x=q[r['questionId']]
 if x['lectureId'] not in sys.argv[1:]:continue
 print(x['id'],'MIXED' if r.get('supplementalInputIds') else '', 'assets:',[(a[z]['physicalPage'],a[z]['path']) for z in r['assetIds']]);print(x['stem']); print('Assumptions:',json.dumps(x['assumptions']));print('Options:', '; '.join(z['id']+': '+z['text'] for z in x['options']))
