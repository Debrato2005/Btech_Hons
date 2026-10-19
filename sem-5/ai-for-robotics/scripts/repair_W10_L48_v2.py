"""One-time source-based L48 repairs and three bounded coverage additions."""
from pathlib import Path
import copy, json, hashlib, datetime, sys, math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash, schema_errors
p=R/'data/question-batches/W10-L48.json';before=json.loads(p.read_text());b=copy.deepcopy(before)
qs={int(q['id'][-3:]):q for q in b['questions']}
rv=json.loads((R/'data/reviews/W10-L48-v1-independent.json').read_text())
changed=[int(r['questionId'][-3:])for r in rv if r['decision']=='flagged']
accepted={r['questionId']:r['questionSha256']for r in rv if r['decision']=='verified'}
assert len(changed)==20 and len(accepted)==57 and all(qs[n]['version']==1 for n in changed)
archive=R/'audits/batch-history/W10-L48-pre-v2.json'
if archive.exists():assert archive.read_text()==p.read_text(), 'Prior attempt changed the batch; do not repeat.'
else:archive.write_text(p.read_text())
AUTHOR='build_robotics_study_app:L48-v2-author'
def opt(n,i,text,why):
 q=qs[n];next(o for o in q['options']if o['id']==f'o{i}')['text']=text;q['solution']['optionExplanations'][f'o{i}']=why
def repl(n,opts,exps):
 for i,(s,e)in enumerate(zip(opts,exps),1):opt(n,i,s,e)
qs[8]['stem']='Which distinction correctly separates time sampling from amplitude quantization in speech digitization?'
opt(19,2,'FFT approximates a different spectrum by omitting selected DFT frequency bins, even with exact arithmetic.','An FFT algorithm computes the same DFT coefficients; floating-point error is not its defining mathematical distinction.')
qs[24]['solution']['steps'][1]='m ≈ 781.1769 mel, or 781.18 mel to two decimal places.'
qs[26]['solution']['optionExplanations']['o2']='This divides the total power 1+4+9=14 by the two filters, giving 7 for each; it does not apply either filter-weight vector.'
opt(30,3,'Computing static coefficients separately on successive frames automatically appends their temporal differences to every vector.','A sequence of static vectors provides time context but does not itself append delta or delta-delta features.')
repl(35,[
 'Machine learning, signal processing and speech synthesis.',
 'Machine learning, phonetics and natural language processing.',
 'Machine learning, signal processing and natural language processing.',
 'Statistical language modeling, signal processing and natural language processing.'
],[
 'Speech synthesis replaces the displayed natural-language-processing circle.',
 'Phonetics is relevant to speech, but it replaces the displayed signal-processing circle.',
 'These are the three labeled circles in the source figure.',
 'Statistical language modeling replaces the broader machine-learning label in the figure.'
])
qs[38]['solution']['optionExplanations']['o3']='Identity output would require replacing the entire kernel by [0,1,0], not merely changing its center weight; [1,1,−1] instead gives [−1,0,1,7].'
opt(42,2,'The encoder contextualizes acoustic features; the decoder conditions only on previous text and does not use encoder output.','The diagram explicitly connects the acoustic encoder output to the text decoder; previous text alone is insufficient for this architecture.')
opt(44,4,'Q and V from decoder states; K from encoder states.','Both keys and values are projected from the encoder acoustic states; only the query is from the decoder.')
qs[45]['difficulty']='easy';qs[45]['difficultyRationale']='Direct conformable matrix-shape multiplication with all three dimensions supplied.'
opt(50,3,'Using the current decoder-input position as well as later positions, because the mask must exclude its diagonal.','The inclusive causal mask allows the current input position and earlier ones; shifted decoder inputs must not be confused with the unknown next target.')
opt(51,2,'Keep a and b as a width-two beam and compare their later sequence scores.','A width-two beam retains alternatives; greedy decoding commits to one current maximum.')
opt(57,4,'The external-LM term disappears and the acoustic score also loses its division by character count.','The character-count normalizer is independent of λ and remains when only the external-LM weight is set to zero.')
repl(59,[
 'Both checkpoints require 128 Mel bins; the 80-bin acoustic representation belongs only to an older illustration.',
 'Both checkpoints require 80 Mel bins; the stated 128-bin preprocessing should be replaced for either one.',
 'whisper-small uses 80 Mel bins; whisper-large-v3 uses 128, so the count must be tied to the model.',
 'whisper-small uses 128 Mel bins and whisper-large-v3 uses 80 Mel bins.'
],[
 'The checked whisper-small configuration requires 80 acoustic Mel bins.',
 'The checked whisper-large-v3 configuration requires 128 acoustic Mel bins.',
 'The official configurations differ, so the feature extractor must match its checkpoint.',
 'This reverses the two checked feature configurations.'
])
opt(65,4,'It transposes the array to shape (N,2), moving the channel dimension to the end.','squeeze removes size-one axes; it does not transpose two non-singleton dimensions.')
opt(69,3,'The displayed output establishes that a copied excerpt reproduces the exact sentence without recording the audio or model revision.','Reported output is not an independent rerun, and reproduction depends on the actual input and compatible artifacts.')
opt(69,4,'The speaker icon and sentence together are a sufficient input record, so the referenced audio artifact does not need to be checked.','A visual icon and transcript do not identify or supply the waveform that the code loads.')
opt(70,3,'Compatible libraries, the actual audio and model weights, with any speech processor configuration because feature settings are interchangeable.','The processor feature and token settings must match the selected checkpoint; an arbitrary speech processor is not a sufficient prerequisite.')
repl(72,[
 'Text-to-speech reads the recognized user transcript first; language understanding and response generation run afterward.',
 'Language understanding and response generation produce reply text, then text-to-speech produces the spoken reply.',
 'Language understanding identifies the intent; text-to-speech reads the user transcript, and response generation runs after that playback.',
 'Response generation chooses reply text before language understanding interprets the transcript; text-to-speech then speaks that earlier choice.'
],[
 'Speaking the recognized input before generating reply content reverses the illustrated response dependency.',
 'The reply content is determined before the speech waveform is synthesized.',
 'The illustrated synthesis input is the generated response, not a replay of the recognized request.',
 'The illustrated response is based on understanding the request, not chosen before that interpretation.'
])
repl(73,[
 'It reverses the modality direction, but text alone does not uniquely recover the original speaker, timing and prosody.',
 'It reverses the modality direction and uniquely recovers the original waveform whenever the transcript has no word errors.',
 'It recovers the original timing and intonation from word order alone, while only speaker identity remains unspecified.',
 'It recovers the original waveform after matching the sample rate, because the transcript supplies all remaining acoustic information.'
],[
 'Many acoustically different utterances can have the same linguistic transcript.',
 'Even a perfect word transcript omits acoustic details needed to identify the original waveform.',
 'The same words can be spoken with different timing and intonation.',
 'Sample rate describes the time grid, not the missing sample amplitudes or vocal characteristics.'
])
repl(77,[
 'Convert dictated speech into text for an input field.',
 'Read existing screen text aloud without recognizing incoming speech.',
 'Identify the enrolled speaker from a voice recording without transcribing the dictated words.',
 'Detect a wake word and then require the user to type the rest of the message.'
],[
 'Dictation substitutes recognized speech for manual text entry.',
 'This is a speech-output or screen-reader role rather than dictated input.',
 'Speaker recognition identifies who spoke, not the message to enter.',
 'Wake-word detection can activate an interface but does not transcribe the remaining message.'
])
def cite(page,desc,kind='statement'):
 c=copy.deepcopy(qs[8]['citations'][0]);c.update(slideId=f'lectures-p{page}',physicalPage=page,kind=kind,role='premise',locator=f'Lecture L48, physical PDF page {page}, printed footer {page-1506}: {desc}',evidenceText=(R/f'sources/text/lectures/page-{page}.txt').read_text().strip());return c
def add(n,title,stem,opts,key,exps,why,citations,typ='conceptual',difficulty='easy'):
 q=copy.deepcopy(qs[8]);q.update(id=f'W10-L48-Q{n:03d}',version=1,status='draft',authorId=AUTHOR,stem=stem,type=typ,difficulty=difficulty,cognitiveSkill='conceptual',subtopic=title,tags=[f'gap-{n}'],conceptIds=[f'W10-L48-C-gap-{n}'],assumptions=[],correctOptionIds=[f'o{key}'],reviewIds=[],citations=citations)
 q['options']=[{'id':f'o{i+1}','text':s}for i,s in enumerate(opts)]
 q['solution']=dict(justification=why,optionExplanations={f'o{i+1}':s for i,s in enumerate(exps)},steps=[],formulas=[],simpleExplanation=why,memoryAid=None,misconceptions=[s for i,s in enumerate(exps,1)if i!=key],examTraps=[],prerequisiteConceptIds=[])
 for k in ['authorCheckEvidence','primaryEvidence','revisionAuthors']:q.pop(k,None)
 qs[n]=q;b['questions'].append(q);b['concepts'].append(dict(id=q['conceptIds'][0],title=title,description=why,slideIds=[c['slideId']for c in citations],questionIds=[q['id']],status='drafted',topic=q['topic'],subtopic=title,prerequisiteConceptIds=[],examinationAngles=[typ]));return q
add(78,'Earliest illustrated ASR stage and FFT role','Which pair matches the earliest node in the lecture’s simplified ASR timeline and the FFT role explained later?',[
 '1960–70s: FFT algorithms for efficient computation of discrete frequency analysis.',
 '1960–70s: HMM–GMM statistical recognition, with FFT first appearing at the 1990s node.',
 '1990s: FFT algorithms, before the diagram’s 1960–70s HMM–GMM node.',
 '1960–70s: end-to-end CTC recognition, with FFT introduced only at the deep-learning node.'
],1,[
 'The first node is labeled FFT Algorithms, 1960–70s; the frequency-analysis page identifies FFT as efficient DFT computation.',
 'The timeline places statistical HMM–GMM ASR in the 1990s and FFT at its first node.',
 'Both the method-era labels and the stated chronology contradict the source timeline.',
 'The diagram places end-to-end CTC/RNN-transducer ASR in the mid-2010s, not at the first node.'
],'This reads the source’s simplified teaching timeline, not a claim that each method was invented at exactly that era.',[cite(1510,'First timeline node FFT Algorithms / 1960–70s.','figure'),cite(1518,'DFT mathematical transform and efficient FFT computation.')])
add(79,'Cepstrum source and tract distinction','Which separation is the explicit purpose attributed to the cepstrum on the MFCC slide?',[
 'Separate successive temporal frames so that every static coefficient becomes a temporal derivative.',
 'Separate the speaker’s voice-source or excitation contribution from vocal-tract characteristics.',
 'Separate high and low sample bit depths while leaving the acoustic source and vocal tract combined.',
 'Separate text tokens from acoustic samples by directly decoding the final sentence.'
],2,[
 'Temporal framing and delta augmentation are different operations from the stated source/tract distinction.',
 'The slide explicitly identifies the speaker’s voice source and vocal-tract characteristics.',
 'Bit-depth conversion is quantization, not the cepstral purpose named here.',
 'The slide describes an acoustic feature operation, not direct token decoding.'
],'The slide says the cepstrum helps separate voice-source and vocal-tract characteristics; this is not a guarantee of exact physical recovery.',[cite(1521,'Third bullet: cepstrum helps separate voice source from vocal-tract characteristics.')])
add(80,'Frontend and non-attention block paths','Across the two architecture diagrams, which trace correctly associates the non-attention components with their shown paths?',[
 'The two Conv1D layers with GELU form the acoustic frontend; layer normalization precedes shown sublayers, feedforward/MLP transforms features, and residual paths add the sublayer result to a bypassed representation.',
 'The two Conv1D layers with GELU form the text output head; layer normalization is the acoustic frontend, and residual paths replace the bypassed representation rather than adding it.',
 'The two Conv1D layers with GELU form the acoustic frontend; layer normalization performs vocabulary decoding, and the feedforward/MLP block supplies the encoder-to-decoder cross-attention keys.',
 'The two Conv1D layers with GELU form the acoustic frontend; each residual path concatenates the bypassed representation with the sublayer result, doubling its width at every addition symbol.'
],1,[
 'The frontend label, normalization boxes, feedforward/MLP boxes and additive bypass junctions support this trace.',
 'The Conv1D/GELU block is below the audio encoder; the residual junctions add rather than discard the bypass.',
 'Normalization is not vocabulary decoding, and a feedforward block is not the cross-attention operation.',
 'The diagram shows additive residual junctions, not concatenation that doubles the feature width.'
],'The source diagrams include feature transformation, normalization and additive bypass paths in addition to attention; the frontend is explicitly labeled 2 × Conv1D + GELU.',[cite(1527,'Layer Normalize, Feedforward and residual-addition paths in encoder/decoder blocks.','figure'),cite(1530,'Acoustic frontend 2 × Conv1D + GELU and MLP boxes.','figure')],typ='diagram',difficulty='medium')
for n in changed:
 q=qs[n];q['version']=2;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append(AUTHOR)
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']]
assert all(question_hash(q)==accepted[q['id']]for q in b['questions']if q['id']in accepted)
packet=[];fields=['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']
for n in changed+[78,79,80]:
 q=qs[n];errs=schema_errors(q,json.loads((R/'data/schema.question.json').read_text()));assert not errs,(q['id'],errs)
 x={k:copy.deepcopy(q[k])for k in fields}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
checks={'mel700':1127*math.log(2),'mel700FourDecimals':format(1127*math.log(2),'.4f'),'filterEnergies':[sum(a*w for a,w in zip([1,4,9],v))for v in [[1,.5,0],[0,.5,1]]],'mistakenAverage':14/2}
x=[0,1,2,3,4,0]
checks['kernelOutputs']={str(w):[sum(x[j+k]*w[k]for k in range(3))for j in range(4)]for w in [[1,0,-1],[1,1,-1],[0,1,0]]}
assert checks['mel700FourDecimals']=='781.1769' and checks['filterEnergies']==[3,11]
assert checks['kernelOutputs']['[1, 1, -1]']==[-1,0,1,7]
checks.update(executedWith='Existing default Python standard library only.',pretrainedInferenceExecuted=False,originalNotebookExecuted=False,restrictedEnvironmentUsed=False)
(R/'audits/W10-L48-v2-author-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
out=R/'audits/blind-W10-L48-v2-and-gaps.json';out.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revised':20,'added':3,'preservedAcceptedCount':57,'preservedAcceptedHashes':accepted,'packetSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'actualPagesReinspected':[1510,1515,1518,1519,1520,1521,1523,1525,1526,1527,1528,1529,1530,1531,1532,1533],'boundedGapsAddressed':{'L48-GAP-FFT-TIMELINE':'Q078 pairs earliest stage with its signal-analysis role, not another full-order clone.','L48-GAP-CEPSTRUM-SEPARATION':'Q079 explicitly tests source/excitation versus vocal-tract distinction.','L48-GAP-BLOCK-PATHS':'Q080 tests frontend, normalization, feedforward/MLP and additive residual paths.'},'restrictions':'No use of /tmp/robotics-l35-venv; no dependency/model/audio/NLTK retrieval, no original notebook execution, no browser bypass. Historical source qualifications and runtime incident remain unchanged.'}
(R/'audits/W10-L48-v2-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
