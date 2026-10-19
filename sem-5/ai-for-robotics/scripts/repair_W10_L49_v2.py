"""One-time L49 quality revisions, including five existing-item coverage extensions."""
from pathlib import Path
import copy,json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
p=R/'data/question-batches/W10-L49.json';before=json.loads(p.read_text());b=copy.deepcopy(before);qs={q['id'].removeprefix('W10-L49-'):q for q in b['questions']}
rv=json.loads((R/'data/reviews/W10-L49-v1-independent.json').read_text());flags=[r['questionId'].removeprefix('W10-L49-')for r in rv if r['decision']=='flagged'];accepted={r['questionId']:r['questionSha256']for r in rv if r['decision']=='verified'}
reopened=['P1545-Q04','P1548-Q02','P1561-Q02'];changed=flags+reopened
assert len(flags)==27 and len(accepted)==57 and len(set(changed))==30 and all(qs[n]['version']==1 for n in changed)
archive=R/'audits/batch-history/W10-L49-pre-v2.json';assert not archive.exists();archive.write_text(p.read_text())
def opt(n,i,text,why):
 q=qs[n];next(o for o in q['options']if o['id']==f'o{i}')['text']=text;q['solution']['optionExplanations'][f'o{i}']=why
def repl(n,options,exps,stem=None,why=None):
 for i,(s,e)in enumerate(zip(options,exps),1):opt(n,i,s,e)
 if stem:qs[n]['stem']=stem
 if why:qs[n]['solution']['justification']=qs[n]['solution']['simpleExplanation']=why
repl('P1539-Q01',[
 'Word recognition can succeed while task interpretation fails; the slide’s phoneme decomposition is not a mandatory exposed stage for every recognizer.',
 'The task choice proves the transcript must contain a word error, even though its words have been checked against the request.',
 'The missing exposed phoneme stage makes the supplied correct transcript invalid as ASR output, so intent interpretation is not the issue.',
 'The transcript is correct, so interpreting bring and cup has already determined the requested task without using any further context.'
],[
 'The observed failure separates transcription from intent; the supplied direct token recognizer also bounds the slide’s general wording.',
 'The premise explicitly establishes correct transcription, so the error can occur later.',
 'An exposed phoneme stage is not required by the supplied audio-to-text architecture.',
 'Correct words do not by themselves establish their intended task and contextual arguments.'
],stem='A recognizer maps audio features directly to text tokens, without an exposed phoneme stage. It correctly transcribes “bring the cup”, but the robot selects the wrong task. Which conclusion respects both this case and the lecture’s ASR-versus-intent distinction?',why='ASR concerns the spoken words; intent interpretation concerns the requested task. The supplied architecture shows why the slide’s phoneme description must not be treated as universal.')
opt('P1540-Q02',4,'Remembered predicates mean the response bank must be searched by nearest-vector distance rather than by authored patterns.','State predicates can condition pattern/template selection without requiring dense-vector retrieval.')
repl('P1543-Q03',[
 'A wildcard that matches several phrasings removes the need to maintain rules when new task meanings appear.',
 'Remembering the previous object makes the fixed rule bank suitable for arbitrary unseen requests without additional coverage checks.',
 'Authored rules can give predictable behavior for covered fixed tasks and retain programmed state, while new meanings still require maintained rules or a fallback.',
 'A predictable response requires exact equality of complete sentences, so a stateful or wildcard rule cannot serve a fixed-task system.'
],[
 'Surface-pattern coverage does not supply rules for every new task meaning.',
 'State helps context but does not establish coverage of open-ended requests.',
 'This preserves the fixed-domain benefit while qualifying the claimed state and generalization limits.',
 'Predictable programmed behavior can include wildcard matching and explicit state transitions.'
],stem='A robot has a small, known command set but may also hear open-ended requests. Which deployment trade-off accurately qualifies the lecture’s rule-based design?',why='Rules can be useful for bounded tasks with explicit state and fallback behavior; broader meanings still require coverage and rule maintenance.')
repl('P1544-Q03',[
 'MEMORY keeps an unchanged transcript of every turn and searches all of it for any later question.',
 'MEMORY retains selected transformed text for later reuse under limited rules.',
 'MEMORY stores only the last chosen keyword and never retains transformed response material.',
 'MEMORY immediately returns every stored transformation on the next input, regardless of whether another keyword rule applies.'
],[
 'The original mechanism is selective transformed-text storage, not a complete transcript archive.',
 'This is a bounded stored-text mechanism, not unrestricted semantic memory.',
 'The original paper describes stored transformations, not only a keyword variable.',
 'Reuse follows specific conditions; it is not unconditional next-turn playback.'
],why='The original paper’s limited transformed-text memory qualifies the slide’s blanket no-memory wording.')
repl('P1545-Q03',[
 'Use sorry first because it precedes I am in the stipulated file-order priority.',
 'Use I am first because its keyword phrase is longer than sorry.',
 'Use whichever matching keyword occurs last in the input sentence.',
 'Choose uniformly between the matching keywords before applying either decomposition.'
],[
 'This follows the explicitly supplied toy priority rule.',
 'Keyword length is not the stipulated priority rule.',
 'Input position is not the stipulated priority rule.',
 'Random choice is not the stipulated priority rule.'
],stem='For this toy trace, a simplified script prioritizes keywords by file order, with sorry before I am. This is not a claim about original ELIZA’s rank mechanism. An input matches both keywords. Which trace follows the supplied policy?')
repl('P1545-Q04',[
 '“Why are you tired today?”; the slide describes random template selection, whereas the original paper cycles ordinary reassembly alternatives and separately randomizes MEMORY transformations.',
 '“Why are you I am tired today?”; the slide and original paper both require ordinary response alternatives to be chosen randomly.',
 '“Why are you tired today?”; the original paper cycles MEMORY transformations but randomly chooses ordinary reassembly alternatives.',
 '“Why are you *?”; choosing a response policy means the wildcard marker is printed rather than replaced.'
],[
 'Only the captured phrase is substituted; the two selection mechanisms need distinct historical scope.',
 'The fixed prefix is not part of the capture, and the historical selection claim is too broad.',
 'The result text is correct, but the two original mechanisms have been exchanged.',
 'The wildcard stands for captured content, not a literal output symbol.'
],stem='In a supplied “I am *” pattern, the capture is “tired today” and the chosen template is “Why are you {capture}?”. Which result and selection-policy qualification are both correct?',why='Substitute the captured phrase into the chosen template, while distinguishing the simplified slide callout from the original program’s two selection mechanisms.')
qs['P1545-Q04']['correctOptionIds']=['o1'];qs['P1545-Q04']['difficulty']='medium';qs['P1545-Q04']['solution']['steps']=['Capture tired today, excluding the fixed I am prefix.','Insert that capture into the selected template.','Distinguish ordinary reassembly cycling from the separate randomized MEMORY transformation.'];qs['P1545-Q04']['primaryEvidence']=[{'title':'Weizenbaum original ELIZA paper','url':'https://web.stanford.edu/class/cs124/p36-weizenabaum.pdf','version':'Communications of the ACM 9(1), January 1966','locator':'Printed p.40 ordinary reassembly cycling; p.41 randomized MEMORY transformations.','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}]
repl('P1546-Q02',[
 'Nearby query vectors force their highest-ranked stored answer to be identical, regardless of where the answer vectors lie.',
 'Different strings cannot share a retrieved answer unless their vectors are exactly equal.',
 'Semantic similarity can rank the same stored answer highest for two paraphrases without exact string equality.',
 'The smaller query-vector norm alone determines which answer is retrieved, independently of the chosen similarity metric.'
],[
 'Nearby queries can still fall on different ranking boundaries; the outcome is possible, not guaranteed.',
 'Different vectors can have the same nearest candidate.',
 'Similarity-based ranking can associate differently worded queries with the same stored response.',
 'A vector norm alone is not a general answer-ranking rule.'
])
repl('P1546-Q03',[
 'The relative winner meets an adequacy threshold automatically because it outranks the other bank entries.',
 'Returning several nearest candidates removes the missing-answer limitation even if every candidate is unsuitable.',
 'The nearest available response can still be inappropriate, so an adequacy check or fallback may be needed.',
 'Rescaling all similarity scores to a zero-to-one range makes the winning response appropriate for the query.'
],[
 'Relative rank does not establish an absolute quality threshold.',
 'Several unsuitable candidates still do not supply the missing answer.',
 'Best available does not imply sufficient or correct.',
 'Changing score scale does not add missing content or validate relevance.'
])
q=qs['P1547-Q01'];q['solution']['justification']=q['solution']['simpleExplanation']='The lecture prints Artificial Linguist Internet Computer Entity; Pandorabots gives the standard name as Artificial Linguistic Internet Computer Entity, so the source wording and standard expansion differ.';q['solution']['optionExplanations']['o4']='This is the printed slide wording; the standard expansion uses Linguistic rather than Linguist.';q['primaryEvidence']=[{'title':'Pandorabots AIML history','url':'https://pandorabots.com/docs/aiml-basics/','locator':'History of AIML, A.L.I.C.E. expansion.','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}]
repl('P1547-Q02',[
 'Input-pattern processing and response construction from authored rules or templates.',
 'Both use AIML XML categories as the original script format.',
 'Both restrict matching to complete literal sentences and exclude substitutions or wildcard decomposition.',
 'Both store the full dialogue as an unrestricted semantic memory that can answer any earlier-turn question.'
],[
 'Authored pattern-based processing is the shared foundation described here.',
 'AIML belongs to the later ALICE approach; it was not original ELIZA’s script format.',
 'The descriptions include substitutions and pattern decomposition, not only complete literal equality.',
 'Limited programmed state is not unrestricted semantic memory.'
])
repl('P1548-Q02',[
 'Artificial Intelligence Markup Language; well-formed XML guarantees support for every tag in every interpreter.',
 'Automated Intent Modeling Language; nested tags represent rules that an interpreter processes.',
 'Artificial Intelligence Markup Language; structural XML validity guarantees correct intent for every input.',
 'Artificial Intelligence Markup Language; dialogue rules have nested tagged structure that an interpreter processes.'
],[
 'The expansion is right, but syntax alone does not guarantee interpreter support for each tag.',
 'The structural role is plausible, but the expansion is not the one shown in the lecture.',
 'The expansion is right, but structural validity is not an intent-correctness guarantee.',
 'This combines the printed expansion with the justified structural role.'
],stem='Which pair gives the lecture’s full expansion of AIML and a justified consequence of its XML-based format?')
opt('P1550-Q04',2,'Suppressing an assignment with think means the assigned context has already been checked against the user’s intended scope.','Output suppression controls what is displayed; it does not establish the correctness or authorization of assigned context.')
repl('P1552-Q01',[
 'AutoTokenizer: text/token mapping; AutoModelForCausalLM: inference wrapper; pipeline: pretrained causal-model weights.',
 'AutoTokenizer: inference wrapper; AutoModelForCausalLM: pretrained causal model; pipeline: text/token mapping.',
 'AutoTokenizer: text/token mapping; AutoModelForCausalLM: pretrained causal model; pipeline: inference wrapper.',
 'AutoTokenizer: pretrained causal-model weights; AutoModelForCausalLM: text/token mapping; pipeline: inference wrapper.'
],[
 'The model loader and inference-wrapper roles are exchanged.',
 'The tokenizer and wrapper roles are exchanged.',
 'This matches the intended roles shown in the simplified excerpt.',
 'The tokenizer and model-weight roles are exchanged.'
],stem='Which intended role mapping matches the simplified Python excerpt, without claiming that the incomplete module executed?',why='The excerpt intends to combine a tokenizer and a causal model through an inference wrapper; its incomplete surrounding code is not evidence of a successful run.')
for n in ['P1554-Q01','P1554-Q02']:
 for c in qs[n]['citations']:
  if c['physicalPage']==1554:c['locator']='Lecture L49, physical PDF page 1554, printed footer 18: Unnumbered wake-word, speech-to-text, NLP intent, response/action and TTS bullets.'
opt('P1555-Q01',4,'Run the lightweight detector only after the full recognizer finishes each utterance, using it as a later activation filter.','A detector applied after full recognition cannot gate the expensive recognition work for that utterance.')
for n in ['P1556-Q03','P1559-Q03','P1563-Q03']:
 qs[n]['difficulty']='easy';qs[n]['difficultyRationale']='Direct evaluation of the fully supplied rule or straightforward source-based design distinction.'
repl('P1557-Q02',[
 'Choose the group named most recently in the current dialogue, without checking whether pointing or current context changes the reference.',
 'Resolve the current referent of those and the intended scope of putting them away using context or clarification.',
 'Select every visible group because a plural demonstrative specifies all objects in view.',
 'Select the nearest visible group because distance alone determines what those denotes.'
],[
 'Recency is a possible cue, not a sufficient supplied reference rule.',
 'The demonstrative and task scope must be grounded in the current situation.',
 'Plurality does not mean universal scope over every group.',
 'Proximity alone has not been established as the speaker’s intended reference.'
])
opt('P1558-Q02',2,'The only lost distinction is the order of the two retained content words, not whether the command is negated.','Both outputs retain clean then room; the missing distinction is the discarded negation.')
repl('P1558-Q03',[
 'Alphabetically sort the same retained content words before intent selection.',
 'Preserve negation and relevant argument relations when mapping the command.',
 'Lemmatize clean and toys but continue removing the negative marker.',
 'Increase the keyword-count threshold while continuing to discard not.'
],[
 'Reordering the same collapsed representation cannot restore the missing polarity.',
 'The representation retains the semantic distinction needed for this failure case.',
 'Morphological normalization does not restore a removed negative marker.',
 'A threshold on unchanged keywords still lacks the missing polarity information.'
])
repl('P1559-Q04',[
 'The architecture retains a mandatory plain-text transcript as the only intermediate state but changes the synthesized voice.',
 'Speech representations can be modeled without a mandatory intermediate transcript bottleneck.',
 'Avoiding a mandatory transcript also forbids optional text inputs or text outputs in the architecture.',
 'Removing the named transcription box removes recognition uncertainty, so the remaining speech representation needs no error evaluation.'
],[
 'That preserves the bottleneck rather than making the stated architectural change.',
 'Plain text need not be the sole mandatory intermediate representation.',
 'Optional text paths can coexist with direct speech processing.',
 'Architectural integration does not eliminate all input or representation errors.'
])
repl('P1560-Q03',[
 'Discrete units are integer codebook choices; continuous features are codebook indices written with decimal points.',
 'Discrete units are quantized choices; continuous features are real-valued representations.',
 'Discrete units must be written words; continuous features must be literal waveform samples.',
 'Discrete units become continuous whenever their codebook is large, regardless of whether outputs remain selected indices.'
],[
 'A decimal notation for an index does not create a continuous latent representation.',
 'The difference concerns the representation domain and quantization.',
 'Discrete acoustic units need not be words, and continuous features can be latent vectors.',
 'A larger finite codebook is still a quantized representation.'
])
repl('P1561-Q02',[
 'Alternate short input/output turns and answer every detected background utterance.',
 'Buffer interruptions until the complete reply ends, then answer them without checking whom they address.',
 'Process new input during speech output, handle an interruption, and withhold a reply when context indicates the nearby speech is not addressed to the robot.',
 'Disable input while speaking, then stay silent whenever any further sound is detected.'
],[
 'Short alternating turns do not establish concurrency, and indiscriminate replies do not demonstrate appropriate silence.',
 'Deferred buffering does not demonstrate interactive interruption handling or context-sensitive silence.',
 'This combines concurrent interaction, interruption response and a justified decision not to speak.',
 'Disabled input is half-duplex, and silence triggered by every sound is not context-sensitive interaction.'
],stem='A demonstration includes a user interrupting the robot and a nearby conversation not addressed to it. Which behavior supports both the lecture’s full-duplex interaction and appropriate-silence claims?',why='The claim needs observed concurrent input handling and context-sensitive response control; merely using acoustic tokens does not establish these behaviors.')
opt('P1561-Q03',1,'It records microphone input during output but postpones all input processing until the current reply finishes.','Recording alone does not demonstrate timely processing or interruption control.')
opt('P1561-Q03',3,'It processes incoming speech concurrently but queues every change until the original spoken reply finishes.','Concurrent input analysis without timely cancellation or redirection does not establish the claimed interruption behavior.')
repl('P1562-Q01',[
 'Linguistic word content versus the grammatical classes of those same words.',
 'Linguistic word content versus which synonyms the transcript uses.',
 'Linguistic word content versus the syntactic order of the transcribed phrases.',
 'Linguistic word content versus vocal pitch, rhythm and intonation.'
],[
 'Grammatical classes concern linguistic structure, not the cited vocal expression.',
 'Synonym choice is lexical content rather than the cited delivery cues.',
 'Transcript syntax is different from acoustic rhythm and intonation.',
 'These are the vocal delivery cues named on the slide.'
])
opt('P1562-Q02',3,'Agreement among stored earlier labels removes the need to report uncertainty for a new utterance.','Historical agreement can inform inference, but new observations and calibration still matter; it does not make the hidden state directly measured.')
repl('P1563-Q01',[
 'Transcript word counts and response-template identifiers.',
 'The bot’s current personality variable and its planned reply wording.',
 'The predicted intent label and the selected robot-action identifier.',
 'Facial motion and vocal patterns observed from the person.'
],[
 'These are text or system-level records, not the two external expressive cue types named here.',
 'Robot response variables are not observations of the person’s face or voice.',
 'Task labels are not the cited external emotion-related observations.',
 'The slide explicitly names facial motion and speech patterns.'
])
repl('P1563-Q02',[
 'Choose whichever modality reports the larger raw confidence value, without checking cross-model calibration.',
 'Average the two label numbers and treat the resulting number as the person’s emotion.',
 'Use the facial label as a fixed tie-breaker even when scene context reduces its reliability.',
 'Retain uncertainty and seek context or clarification rather than treating one cue as conclusive.'
],[
 'Confidence values from different models need not be directly comparable.',
 'Category codes are not a meaningful numerical emotion scale to average.',
 'A fixed tie-breaker ignores relevant evidence about reliability.',
 'Conflicting fallible observations support a cautious, contextual response.'
],stem='Facial cues suggest one interpretation while speech and context suggest another, and both cue models are fallible. Which response is justified?')
repl('P1563-Q03',[
 'Select the highest-scoring task from the words alone, then use tone only to choose a friendly TTS voice while leaving material reference ambiguity unresolved.',
 'Validate a geometrically feasible plan for the nearest object and treat that feasibility as confirmation of the user’s intended referent.',
 'Use content and available contextual/acoustic cues, clarify material ambiguity, then validate the selected action.',
 'Resolve the object from dialogue context, but let the emotion label override a still-unresolved negative command marker before action selection.'
],[
 'A friendly voice does not resolve ambiguity that can change the requested task.',
 'Geometric feasibility does not establish which object the user intended.',
 'Interpretation, clarification and action validation address distinct requirements in the correct order.',
 'An inferred emotion does not authorize dropping unresolved command polarity.'
])
for n in changed:
 q=qs[n];q['version']=2;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('build_robotics_study_app:L49-v2-author');q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']]
kept={k:v for k,v in accepted.items()if k.removeprefix('W10-L49-')not in reopened};assert len(kept)==54
assert all(question_hash(q)==kept[q['id']]for q in b['questions']if q['id']in kept)
schema=json.loads((R/'data/schema.question.json').read_text());assert not [(q['id'],schema_errors(q,schema))for q in b['questions']if schema_errors(q,schema)]
packet=[]
for n in changed:
 q=qs[n];x={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');out=R/'audits/blind-W10-L49-v2-and-gaps.json';out.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'flaggedRevised':27,'acceptedReopenedForCoverage':reopened,'preservedAcceptedCount':54,'preservedAcceptedHashes':kept,'packetSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'actualPagesReinspected':[1539,1540,1543,1544,1545,1546,1547,1548,1550,1552,1554,1555,1556,1557,1558,1559,1560,1561,1562,1563],'boundedGapChanges':{'phoneme-scope':'P1539-Q01 adds an explicitly supplied direct-token recognizer and bounds universal phoneme wording.','rule-domain-tradeoff':'P1543-Q03 compares bounded fixed commands with open-ended coverage and maintained rules.','template-selection-policy':'P1545-Q04 preserves wildcard substitution and adds source versus original selection distinction.','aiml-expansion':'P1548-Q02 combines name and XML-role assessment.','appropriate-silence':'P1561-Q02 adds contextual nonresponse to demonstrated concurrent interruption handling.'},'primaryChecks':{'eliza':{'url':'https://web.stanford.edu/class/cs124/p36-weizenabaum.pdf','ordinarySelection':'Printed p.40: cycle ordinary alternatives.','memory':'Printed p.41: separately select MEMORY transformations randomly, retain transformed text and reuse under conditions.'},'alice':{'url':'https://pandorabots.com/docs/aiml-basics/','standardExpansion':'Artificial Linguistic Internet Computer Entity'}},'restrictions':'No restricted venv, installs, pretrained inference, original L49 notebook retrieval/run, corpus fetch or browser bypass. Primary public paper/documentation read only.'}
(R/'audits/W10-L49-v2-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
