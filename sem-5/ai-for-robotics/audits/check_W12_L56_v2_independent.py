"""Independent supplied-model checks only; no ROS, API, model or hardware execution."""
import json, pathlib, hashlib, datetime
R=pathlib.Path(__file__).resolve().parents[1]
# Speech cancellation and late-chunk trace: model exactly the supplied policy.
heard=['a1']; queue=['a2','a3']; canceled=set(); extent={'R1':60}; turns=['earlier']
canceled.add('R1');queue.clear();extent['R1']=20
if 'R1' not in canceled: queue.append('a4')
turns.append('U2');queue.extend(['b1','b2']);heard.append(queue.pop(0))
assert (heard,queue,extent['R1'],turns[-1])==(['a1','b1'],['b2'],20,'U2')
# Graph with explicitly supplied dependency and fallback rules, not generic ROS semantics.
def fault(depth=True, emotion_alive=True):
 color=True; detector=color and depth; emotion=emotion_alive and color and detector
 return dict(dialogueTexts=True,annotations=detector,emotionLabels=emotion)
assert fault(False)==dict(dialogueTexts=True,annotations=False,emotionLabels=False)
assert fault(True,False)==dict(dialogueTexts=True,annotations=True,emotionLabels=False)
# Inclusive freshness/score gate, using integer milliseconds to avoid round-off boundary claims.
records=[(.95,9500),(.70,9900),(.80,9750)]
assert [i+1 for i,(score,t) in enumerate(records) if score>=.75 and 0<=10000-t<=300]==[3]
assert .75>=.75 and 10000-9700<=300
frame=640*480*5; rates={str(fps):frame*fps+48000 for fps in [20,30]}
assert frame==1536000 and rates=={'20':30768000,'30':46128000}
assert rates['20']<=40000000<rates['30'] and 1000/80==12.5
# At each worker start k*80, newest-only takes the latest periodic 50 ms capture.
starts=[k*80 for k in range(1000)]
newest_ages=[start+80+20-(start//50)*50 for start in starts]
fifo_ages=[start+80+20-k*50 for k,start in enumerate(starts)]
assert max(newest_ages)==140 and min(newest_ages)==100
assert newest_ages[:5]==[100,130,110,140,120]
assert fifo_ages[:4]==[100,130,160,190] and fifo_ages[-1]>150
# If simultaneous service-start/capture resolves with the immediately prior waiting frame,
# a boundary age can become 150 ms, still inclusive-feasible; no key depends on tie ordering.
prior_at_ties=[start+100-((start-1)//50)*50 if start and start%50==0 else a for start,a in zip(starts,newest_ages)]
assert max(prior_at_ties)==150
out=dict(review='Independent supplied-state-machine, supplied fault policy and deterministic arithmetic only',
 checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), speech=dict(heard=heard,queue=queue,R1AudioExtentMs=extent['R1'],retainedNewTurn=turns[-1]),
 failures=dict(depthLoss=fault(False),emotionNodeFailure=fault(True,False)), ratesBytesPerSecond=rates,frameBytes=frame,
 workerResultsPerSecond=12.5,newest1000Starts=dict(minAgeMs=min(newest_ages),maxAgeMs=max(newest_ages),firstFiveAgesMs=newest_ages[:5],alternateTieMaxAgeMs=max(prior_at_ties)),fifoFirstFourAgesMs=fifo_ages[:4],
 runtimeClaimsExcluded=['ROS or Gazebo','camera or microphone','pretrained model','OpenAI API','browser','course code execution'])
(R/'audits/W12-L56-v2-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
