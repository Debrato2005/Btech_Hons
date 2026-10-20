"""One-time source-based L50 quality repairs and bounded synthesis questions."""
from pathlib import Path
import copy,json,hashlib,datetime,sys,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
p=R/'data/question-batches/W10-L50.json';before=json.loads(p.read_text());b=copy.deepcopy(before)
qs={int(q['id'].split('Q')[-1]):q for q in b['questions']}
rv=json.loads((R/'data/reviews/W10-L50-v1-independent-contracts.json').read_text());flags=[int(r['questionId'].split('Q')[-1])for r in rv if r['decision']=='flagged'];accepted={r['questionId']:r['questionSha256']for r in rv if r['decision']=='verified'}
assert len(flags)==35 and len(accepted)==30 and all(qs[n]['version']==1 for n in flags)
archive=R/'audits/batch-history/W10-L50-pre-v2.json';assert not archive.exists()
def opt(n,i,text,why):
 q=qs[n];next(o for o in q['options']if o['id']==f'o{i}')['text']=text;q['solution']['optionExplanations'][f'o{i}']=why
def repl(n,options,exps,stem=None,why=None):
 for i,(s,e)in enumerate(zip(options,exps),1):opt(n,i,s,e)
 if stem:qs[n]['stem']=stem
 if why:qs[n]['solution']['justification']=qs[n]['solution']['simpleExplanation']=why
repl(1,[
 'Use the identical transcripts to select the same tone, because wording alone supplies the difference needed here.',
 'Use the difference in loudness as the intended task, replacing interpretation of the words and situation.',
 'Keep the words as linguistic evidence and consider prosody and context before choosing the response style.',
 'Treat the estimated expression as the intended task, rather than combining it with the words and situation.'
],[
 'Identical words do not capture the stipulated difference in delivery or situation.',
 'Acoustic delivery can inform interpretation but does not replace the task meaning.',
 'This combines complementary evidence without treating an affect estimate as certain private knowledge.',
 'An expression estimate is not itself the complete intended task.'
],stem='Two speakers say “That is fine” with the same transcript but different delivery and situations. Which response-planning approach addresses the lecture’s text-only limitation?',why='The words, delivery and situation provide different evidence for interpreting the utterance and choosing a response style.')
repl(2,[
 'STT → LLM → intent parsing, with TTS and the ROS state machine branching from the parser.',
 'STT → intent parsing → LLM, with separate paths to TTS and to the ROS state machine → robot action.',
 'STT → intent parsing, with a direct robot-action branch and an LLM used only after TTS.',
 'STT → intent parsing → LLM → TTS → ROS state machine → robot action, as one compulsory serial output path.'
],[
 'The shown parser precedes the LLM, not the reverse.',
 'This preserves the diagram’s input stages and separate speech/action output paths.',
 'The diagram routes the action path through the LLM and ROS state machine.',
 'TTS and the state-machine path branch from the LLM; TTS is not an obligatory action intermediary.'
])
repl(4,[
 'HAPPY is the latest estimated user label, so the robot policy necessarily copied that label unchanged.',
 'HAPPY is the outward facial expression, so no separate internal state is represented.',
 'HAPPY names a simulated software state that can guide a response and need not equal the estimated user state.',
 'HAPPY is the linguistic intent selected from the request, rather than a state used by the response policy.'
],[
 'The human estimate and robot policy state are separate; the policy need not copy the label.',
 'An internal state can guide an expression without being identical to that output.',
 'The lecture explicitly distinguishes the simulated robot state and human model.',
 'Task intent and simulated affect state have different roles.'
],why='A named software state is distinct from the user estimate, task intent and generated expression.')
repl(5,[
 'Cue: source state; neutral→supportive: trigger; soft voice: transition.',
 'Cue: trigger; neutral→supportive: transition; soft voice: output action.',
 'Cue: output action; neutral→supportive: transition; soft voice: destination state.',
 'Cue: trigger; neutral→supportive: output action; soft voice: transition.'
],[
 'The cue causes a change; it is not the source state itself.',
 'The cue triggers the transition, and softened speech is generated behavior.',
 'The cue is an input, and the destination state is supportive rather than the voice output.',
 'The state change is the transition; the voice change is the output.'
])
repl(8,[
 'Happy and friend lie on the right; sad and stranger lie on the left.',
 'Happy and stranger lie on the left; sad and friend lie on the right.',
 'Happy and friend lie on the left; sad and stranger lie on the right.',
 'Friend and sad lie on the left; stranger and happy lie on the right.'
],[
 'This reverses the diagram’s left and right groups.',
 'This exchanges friend and stranger relative to their displayed sides.',
 'These are the named left/right placements in this diagram, not the different notebook angles.',
 'This exchanges happy and sad relative to their displayed sides.'
])
repl(13,[
 'The pair is independent, so raising one value leaves its opposite unchanged.',
 'The sum of every emotion across all pairs is100, so updating one pair rescales all the others.',
 'Each paired software value complements the other to100; this is a modeling constraint rather than a measured law of human affect.',
 'A sum of100 requires the two members of every pair to be equal, regardless of updates.'
],[
 'The chosen rule explicitly couples the two members.',
 'The constraint is per opposite pair, not a shared total over all pairs.',
 'It specifies how the demonstration updates its state values, not an empirical psychological identity.',
 'Many unequal pairs sum to100, such as75 and25.'
])
repl(14,[
 'The smallest and largest polar angles, followed by radial values found independently of those directions.',
 'The minimum and maximum radial values, retaining the angle associated with each extremum.',
 'The mean radius and a mean of all angles, without preserving either radial boundary.',
 'Only the maximum radius and its angle, treating the opposite direction as the minimum without scanning it.'
],[
 'The stated scan finds radial extrema and their corresponding angles, not independent angle extrema.',
 'The slide names both radial boundaries and their associated directions.',
 'A mean does not identify the two specified extrema.',
 'The source requires both extrema rather than deriving the minimum from an assumed opposite direction.'
])
repl(16,[
 'A chosen initial estimate that can later change when conversational evidence arrives.',
 'A fresh observation inferred from the first utterance, even though no utterance has yet arrived.',
 'The final estimate carried over from this person’s preceding conversation, whether or not one exists.',
 'A calibrated population measurement establishing the person’s most likely state from labeled data.'
],[
 'The middle values are initialization assumptions, not measurements.',
 'No current conversational evidence has yet been processed.',
 'The shown initialization does not restore a prior conversation state.',
 'The demonstration supplies no calibration or population-data calculation for initialization.'
])
repl(17,[
 'Estimate emotion → generate response from the old robot state → update both states → save the conversation.',
 'Estimate emotion → update human state → save the current input as a complete pair → generate response → update robot state.',
 'Estimate emotion → update robot state from the old human state → generate response → update human state → save the conversation.',
 'Estimate emotion → update human state → update robot state → generate response → save the conversation.'
],[
 'The displayed response uses the updated states, not the old robot state.',
 'A complete pair is saved after its response exists; the robot state is updated before generation.',
 'The human state update precedes the robot-state update in the displayed pseudocode.',
 'This follows the displayed dependencies before response generation and memory storage.'
])
qs[17]['solution']['steps']=['Infer the current estimate from the input.','Update the human model, then the robot state.','Generate the response using the updated state and prior memory.','Store the input and generated response, then display them.']
repl(22,[
 'Reject the out-of-range input and leave the previous happy/sad pair unchanged.',
 'Assign happy150 and its complement sad−50 without applying a clamp.',
 'Clamp happy to100, then assign its complement sad0.',
 'Compute sad−50 from the original input, then clamp only happy to100.'
],[
 'The method clips rather than rejecting a recognized emotion’s numeric value.',
 'The code clips the supplied value before assignment.',
 'The complement is computed from the clipped value.',
 'The complement is not computed from the unbounded input.'
])
qs[22]['solution']['steps']=['Clip150 to the allowed interval0–100, giving100.','Assign happy100.','Assign sad=100−100=0 and recompute the mood.']
qs[23]['solution']['optionExplanations']['o4']='30 and20 are the unweighted deviations50*v and−50*a; this omits both confidence0.5 and the neutral offset50.'
repl(25,[
 'Treat the friendly-axis number as a calibrated probability that the person will cooperate.',
 'Treat the arousal-to-friendly relation as a direct consequence of the facial classifier’s categorical label vocabulary.',
 'Treat the friendly-axis number as the arousal value itself, without a sign or scale change.',
 'Treat it as a chosen social-response mapping that needs separate justification, rather than equating calmness with friendliness.'
],[
 'The code supplies a handcrafted state value, not a calibrated cooperation probability.',
 'A label vocabulary does not derive this numerical policy.',
 'The code reverses and scales arousal, then weights the deviation by confidence.',
 'The numerical transformation implements a demonstration policy, not a psychological equivalence.'
])
repl(26,[
 'Set curious62 and return, leaving the sad-specific welcome/friend assignments unexecuted.',
 'Set curious62, then continue into the sad branch and assign welcome88 and friend82.',
 'Assign the default neutral branch’s welcome60 and curious62 because any confidence below1 is neutral.',
 'Execute the sad branch because the confidence guard includes only values strictly below0.2.'
],[
 '0.2<0.30 triggers the early return before label-specific branches.',
 'The return prevents fall-through into the sad branch.',
 'The actual low-confidence branch differs from the later default label branch.',
 'The guard is confidence<0.30, not confidence<0.2.'
])
repl(27,[
 'Assign welcome88, friend82 and curious62; this can lower a value that was already above its assigned target.',
 'Add88,82 and62 to the previous welcome, friend and curious values, respectively.',
 'Assign sad88, distant82 and frustrated62 so that the robot directly mirrors the user label.',
 'Assign welcome88 but retain the preceding friend and curious values because only one axis may change per turn.'
],[
 'These are fixed assignments in the sad branch, not guaranteed increases.',
 'The code calls change with target values, not nudge with increments.',
 'The policy chooses supportive robot targets rather than copying the sad label.',
 'The branch updates all three named dimensions and their complements.'
],stem='With confidence0.8 and a sad label, what does update_robot_policy assign, regardless of the previous robot state?',why='The sad branch sets welcome88, friend82 and curious62; the direction of each change depends on its previous value.')
repl(28,[
 'The last6 pairs remain, beginning with pair3, and turn_count is6 because trimming resets the counter.',
 'The last4 pairs remain, beginning with pair5, and turn_count is8 because the list cap counts three entries per pair.',
 'The last6 pairs remain, beginning with pair3, and turn_count is8 because the lifetime counter is not trimmed.',
 'The last8 pairs remain, beginning with pair1, and turn_count is8 because the cap counts pairs rather than messages.'
],[
 'The list is trimmed, but the separate counter retains all eight calls.',
 'Each pair adds two role-tagged messages, not three.',
 'Twelve messages contain six complete pairs; the counter increments on every add_turn call.',
 'The cap is twelve message entries, not twelve pairs.'
],stem='Starting with empty memory, eight numbered input/reply pairs are added through add_turn. Which history and counter remain?')
qs[32]['stem']='Each candidate includes the required explanation string "demo"; only the other four fields are shown. Which candidate satisfies the notebook’s EmotionAnalysis label and numeric constraints?'
repl(33,[
 'A failed classification has been replaced by a neutral label with zero confidence; the label does not establish the person’s actual state.',
 'The previous valid human estimate has been retained unchanged, with its confidence copied into the new result.',
 'The neutral label is a successful classification whose zero confidence disables all subsequent human-state mapping.',
 'The service failure is represented by adding an unknown label outside the schema’s permitted labels.'
],[
 'The exception handler supplies explicit fallback fields rather than a valid affect observation.',
 'The handler constructs a new neutral, zero-confidence result.',
 'The fallback still reaches state mapping; zero confidence drives mapped human axes to their midpoint.',
 'The fallback uses the permitted neutral label, not an out-of-schema value.'
])
repl(35,[
 'Call the estimated user label synthesis and the generated vocal expression recognition.',
 'Call the text transcript affect recognition and the unchanged stored label affect synthesis.',
 'Call inference from observed cues recognition and generation of expressive behavior synthesis.',
 'Call selection of a motor command recognition and extraction of a facial feature vector synthesis.'
],[
 'This exchanges the inference and generation roles.',
 'A transcript alone is not an affect estimate, and storing a label is not generating an expression.',
 'Recognition estimates a pattern from evidence; synthesis produces an expressive pattern.',
 'Feature extraction supports recognition, while expressive motor output belongs to synthesis.'
])
repl(36,[
 'Match the number of human-provided label names, then infer that model and observer accuracy are equal.',
 'Compare training-set agreement with an observer’s performance on different, unseen cases.',
 'Define comparable cases and labels, then measure whether the model meets the observer comparison target.',
 'Compare the model’s confidence scores directly with the fraction of cases on which observers agree.'
],[
 'Sharing a label vocabulary does not establish comparable accuracy.',
 'Different evaluation populations and training exposure confound that comparison.',
 'The statement supplies a goal that requires an appropriate empirical comparison.',
 'Confidence scores and observer agreement are different quantities; matching their values is not an accuracy test.'
],why='A stated observer-level goal is not an achieved result; it requires a defined and comparable evaluation.')
repl(38,[
 'Choose the strategy with the best final-test score and report that same score as untouched evaluation.',
 'Select a strategy on validation data, then repeatedly tune it against the final test labels before reporting.',
 'Select settings using training/validation data or cross-validation, then evaluate the chosen system on a held-out final test set.',
 'Fit preprocessing on all available examples before splitting, then use validation selection and a held-out final score.'
],[
 'Selection on the final test set makes it part of the selection process.',
 'Repeated tuning against the final test labels also leaks information into selection.',
 'This separates model selection from the final assessment, as the cited documentation explains.',
 'Learning preprocessing from all examples can leak held-out information before evaluation.'
],stem='The FER slide depicts a “Test FER Model” loop but does not distinguish a separate validation set. Which methodological refinement, supported by the cited scikit-learn evaluation guidance, separates strategy selection from final assessment?',why='Use selection data for tuning and preserve held-out data for final assessment; this is an explicitly sourced refinement, not a literal reading of the slide loop.')
qs[38]['primaryEvidence']=[{'title':'scikit-learn cross-validation guide','url':'https://scikit-learn.org/stable/modules/cross_validation.html','version':'1.9.1 as retrieved on 2026-10-19','locator':'Section3.1: hyperparameter selection, validation set and final test set; Data transformation with held-out data.','checkedAt':'2026-10-19T23:44:14+00:00'}]
repl(41,[
 'The larger trainable model should be selected from training accuracy alone, even when its held-out score is lower.',
 'A frozen backbone is preferable whenever its parameter count is larger, regardless of feature mismatch or available data.',
 'The original pretraining score determines the ranking among new-task tuning strategies without a new-task comparison.',
 'Data quantity, feature mismatch, optimization and held-out performance determine the trade-off; additional trainable capacity can overfit.'
],[
 'Training fit alone does not establish performance on unseen target examples.',
 'Parameter count alone does not resolve whether the inherited features suit the target data.',
 'Pretraining performance does not determine the ranking after adaptation to another task.',
 'This respects the slide’s sufficient-data qualification and avoids an unconditional strategy ranking.'
])
repl(42,[
 'Dense256 → dropout0.2 → Dense128 → dropout0.2 → Dense8 → sigmoid.',
 'Dense128 → dropout0.2 → Dense256 → dropout0.2 → Dense8 → softmax.',
 'Dense256 → dropout0.2 → Dense128 → dropout0.2 → Dense8 → softmax.',
 'Dense256 → dropout0.8 → Dense128 → dropout0.8 → Dense8 → softmax.'
],[
 'The displayed final activation is softmax rather than sigmoid.',
 'The diagram orders256 units before128 units.',
 'This preserves both dense widths, both stated dropout rates, the eight outputs and softmax.',
 'The displayed dropout rate is0.2, not0.8.'
])
qs[43]['solution']['optionExplanations']['o4']='2,056 equals2×(128×8)+8: it doubles the weight count but adds only one set of eight biases; the single layer has1,024+8=1,032.'
repl(44,[
 'Keep eight softmax outputs and assign the unused index to an arbitrary existing label, without changing the seven-label targets.',
 'Choose a seven-class head or explicitly define a different task and compatible labels; make training targets and output mapping agree.',
 'Keep the eight-output normalization but drop its eighth probability only when computing the seven-class training loss.',
 'Add an eighth class name after training without providing corresponding targets or specifying what it represents.'
],[
 'An arbitrary duplicate index does not establish a coherent task and target mapping.',
 'The head, target encoding and interpretation must describe the same defined classification task.',
 'Ignoring an output without redesigning the loss/normalization does not make the pictured task automatically seven-class.',
 'A post-hoc class name does not supply a defined trained class.'
])
repl(47,[
 'This example uses contempt, fear, anger, sadness, happiness, disgust and surprise, with neutral omitted.',
 'This example includes neutral with six other listed categories; distinguish its classifier label set from Ekman’s seven-emotion list.',
 'This example includes both contempt and neutral, giving the eight categories required by the preceding head illustration.',
 'This example’s seven names are the six schema labels in the Albert notebook plus a second spelling of happy.'
],[
 'The slide includes neutral, not contempt.',
 'The local classifier labels and the cited theoretical list should not be conflated.',
 'Contempt is not listed here, and the mismatch with the eight-output head remains separate.',
 'The notebook’s labels include frustrated and differ from this facial-classifier list.'
])
repl(50,[
 'Horizontal: valence decreasing from left to right; vertical: arousal increasing upward.',
 'Horizontal: valence increasing rightward; vertical: arousal decreasing upward.',
 'Horizontal: valence increasing rightward; vertical: arousal increasing upward.',
 'Horizontal: arousal increasing rightward; vertical: valence increasing upward.'
],[
 'The printed V values become more positive toward the right.',
 'The printed A values become more positive toward the top.',
 'This follows the numeric V/A annotations despite the conflicting outer labels.',
 'This follows the swapped outer labels, not the numeric annotations asked about.'
])
repl(54,[
 'Waveform → word transcript → text sentiment model → estimated emotion, using no acoustic feature path.',
 'Waveform → acoustic feature representation → learned pattern model → estimated emotion.',
 'Waveform → acoustic feature representation → fixed loudness-threshold label, with no learned model.',
 'Waveform → acoustic feature representation → phoneme transcript, treating transcription as the final affect output.'
],[
 'This is a text-only route, not the illustrated acoustic SER route.',
 'The diagram extracts speech features and applies a learned model to estimate affect.',
 'The illustrated path includes a learned model, not only a fixed threshold.',
 'Phoneme transcription is not the diagram’s estimated affect output.'
])
repl(56,[
 'Train three independent predictors and average only their final class scores, without a shared learned feature representation.',
 'Train on synchronized features but shuffle the voice-to-face pairing at inference while retaining the original timestamps.',
 'Use one modality to select a label and feed that fixed label to the others without allowing their features to affect it.',
 'Learn from aligned face, voice and language features together so that cross-modal relationships can influence the representation.'
],[
 'This is score-level late combination, not the joint feature representation asked for.',
 'Shuffling destroys the stipulated correspondence between observations.',
 'A fixed one-way decision does not learn the requested joint representation.',
 'This directly matches the lecture’s joint-representation description.'
],stem='The design goal is a learned joint feature representation, rather than merely combining independent final scores. Which multimodal design most directly meets that goal?')
repl(57,[
 'Feed zero-valued pixels to the complete-input model and interpret its usual confidence as evidence of unchanged reliability.',
 'Keep the last facial estimate as if it were a simultaneous observation, without marking its age or missingness.',
 'Use the supported missing-input pathway with available cues and its evaluated uncertainty limits.',
 'Treat the missing camera as a neutral facial-class vote and combine it as an ordinary confident observation.'
],[
 'A zero image is not automatically equivalent to a modeled missing-input condition.',
 'A stale estimate is not a current observed face and needs explicit treatment.',
 'The premise supplies actual missing-input support; performance still needs bounded interpretation.',
 'Missing evidence is not a confident neutral observation.'
],stem='A fusion model has been trained and evaluated with an explicit camera-missing mask. Its camera is now obscured while speech remains available. Which handling respects that supported design without claiming unchanged accuracy?')
repl(59,[
 'Use the earlier preference as a fixed affect label, so a new request for quiet cannot alter the response.',
 'Use the earlier preference as context and the current request as new evidence when choosing a response.',
 'Replace the stored preference with the current affect label, losing the fact that it concerned a different situation.',
 'Average the names of the old preference and new label without checking what either refers to.'
],[
 'A context-specific remembered preference does not override all later evidence.',
 'This combines prior context with the latest cue rather than treating either as permanent certainty.',
 'An affect label and a factual preference are different records with different scope.',
 'Combining records requires their meanings and contexts, not arithmetic over label names.'
],stem='Memory says a user previously liked enthusiastic greetings, but the current message asks for a quiet response. Which planning approach uses memory and current evidence together?')
repl(60,[
 'A warehouse robot may maintain task memory, while the social-robot example additionally emphasizes conversational context and affect-aware dialogue.',
 'A warehouse robot with stored task history is already the same dialogue architecture, even if it has no conversational input or output.',
 'A conversational robot with a fixed stateless script necessarily implements the illustrated conversation-memory stage.',
 'A robot with an affect classifier but no response planner necessarily implements the full illustrated dialogue-planning pipeline.'
],[
 'Memory is not exclusive to social robots; the example emphasizes its conversational use.',
 'Task memory alone does not establish conversational or affect-aware functionality.',
 'A stateless script does not by itself provide conversation memory.',
 'An input classifier alone does not supply the response-planning stage.'
])
repl(62,[
 'Use the calm wording with a compatible restrained voice and gesture chosen for the current conversational goal.',
 'Use the calm wording but retain an unrelated celebration gesture because gestures are controlled by a separate output module.',
 'Use the calm wording with the preceding turn’s excited speech style, ignoring the changed context.',
 'Match the gesture to an earlier keyword while matching the spoken response to the current request, without checking consistency.'
],[
 'Coordinated output channels help express the intended current response.',
 'Separate implementation modules can still produce cues that need coordination.',
 'A stale style can conflict with the intended current response.',
 'Independently matched cues can communicate inconsistent intentions.'
],stem='A robot has planned a calm explanation after a request to slow down. Which output plan best applies the lecture’s coordination principle?')
repl(63,[
 'Only microphone sampling-rate variation explains the difference, even though these examples use face images alone.',
 'A mismatch between motor-torque units and image labels explains why the single expression label is incomplete.',
 'The problem is solely that the images have different file names, which fixes the representational ambiguity when renamed.',
 'Expression patterns vary across people and contexts, and a single category can omit mixed or differently intense affect.'
],[
 'Microphone sampling is not the face-only input condition.',
 'Motor units are not the representational issue in this classifier.',
 'File names do not resolve individual variation or mixed expression.',
 'These are the human-variation and representation challenges identified in the lecture.'
],stem='Face images are correctly decoded, uniformly sized and labeled using one shared class list, yet individual expressions and mixed states vary. Which remaining challenge is not resolved by that technical standardization?')
# Keep all distractors within plausible classifier limitations, not unrelated hardware.
opt(63,1,'The only remaining challenge is image-resolution mismatch, even though all images are already uniformly sized.','Uniform sizing is already stipulated and does not remove individual or mixed-expression variation.')
opt(63,2,'The only remaining challenge is class-name mismatch, even though all examples already use the same label list.','Shared names do not guarantee identical expression patterns or capture mixtures.')
opt(63,3,'The only remaining challenge is decoding failure, even though every image is correctly decoded.','Successful decoding does not settle the human-variation or representation problem.')
repl(64,[
 'Store encrypted face recordings for a month even though the agreed purpose needs only a temporary estimate during this session.',
 'Keep only the temporary estimate needed for this session and explain its uncertainty and deletion at session end.',
 'Delete raw recordings at session end but retain person-linked estimates for a new long-term profiling purpose that was not agreed.',
 'Retain the same temporary estimate as planned but present its category as a certain fact about the person.'
],[
 'Encryption does not satisfy the stated session-only collection/retention requirement.',
 'This meets the supplied purpose, retention and uncertainty requirements.',
 'Removing raw media does not authorize a new purpose for person-linked estimates.',
 'The supplied requirement includes communicating uncertainty, not only limiting retention.'
],stem='A project specifies session-only affect estimation, no raw-media storage, no secondary profiling and clear uncertainty notices. Which design meets those stated requirements while addressing the lecture’s privacy concern?',why='The requirements are explicit premises of this design exercise, not a privacy-law claim attributed to the slide.')
repl(65,[
 'Offer a certain interpretation of the user’s feelings and select advice from that interpretation without acknowledging uncertainty.',
 'Adapt wording cautiously, avoid claiming certain knowledge of feelings, and direct situations outside the demo’s role to an appropriate qualified person.',
 'Avoid naming an emotion but present the demonstration robot as a qualified professional whenever the user requests it.',
 'Use a low-confidence estimate to select the most assertive reply style, rather than preserving ambiguity.'
],[
 'The notebook explicitly forbids claiming exact knowledge of the user’s feelings.',
 'This matches the response-generation constraints in the cited notebook cell.',
 'The notebook says not to pretend to be a professional in those situations.',
 'The response rules call for cautious adaptation rather than confident assertions from weak evidence.'
],stem='Which response policy follows Albert’s actual notebook response-generation constraints, rather than inferring a professional role from the applications slide?',why='The notebook bounds Albert as a demonstration and asks it to adapt cautiously without claiming certainty or professional authority.')
qs[65]['primaryEvidence']=copy.deepcopy(qs[23]['primaryEvidence']);qs[65]['primaryEvidence'][0]['locator']='Cell15, generate_reply system prompt: cautious adaptation, no exact-feelings claim, and qualified-person referral for situations outside the demonstration role.'
repl(63,[
 'A common label list makes the affect-to-face mapping identical for each person, so only class frequency remains relevant.',
 'A large winning softmax probability directly measures expression intensity, so the single winning category preserves mixtures and strength.',
 'Using one category removes ambiguity from the underlying interaction rather than only choosing a simplified representation.',
 'Expressions vary across people and contexts, while one category can omit mixtures and intensity even with standardized input and labels.'
],[
 'Common class names do not establish identical expression patterns across people.',
 'Class probability, intensity and a mixture of expressed states are different quantities.',
 'A representation choice does not remove ambiguity from the underlying observation.',
 'These limits concern variation and representation, not only preprocessing.'
],stem='A face classifier uses consistently decoded, uniformly sized images and a shared label vocabulary. Which statement best describes limits that remain when expressions differ across people and include mixed affect?')
def form(expr,variables,units,assumptions):return {'expression':expr,'variables':variables,'units':units,'assumptions':assumptions}
def new(n,title,stem,options,key,exps,pages,steps=None,forms=None,code=None,typ='scenario',difficulty='medium',assumptions=None):
 q=copy.deepcopy(qs[1]);q.update(id=f'W10-L50-Q{n:03}',version=1,status='draft',authorId='build_robotics_study_app:L50-v2-author',stem=stem,subtopic=title,type=typ,difficulty=difficulty,cognitiveSkill='numerical'if typ=='numerical'else'conceptual',tags=[f'coverage-gap-{n}'],conceptIds=[f'W10-L50-C-gap-{n}'],assumptions=assumptions or[],options=[{'id':f'o{i+1}','text':s}for i,s in enumerate(options)],correctOptionIds=[f'o{key}'],reviewIds=[])
 q['citations']=[]
 for page in pages:
  c=copy.deepcopy(qs[1]['citations'][0]);c.update(slideId=f'lectures-p{page}',physicalPage=page,kind='derivation'if typ=='numerical'else'statement',role='premise',locator=f'Lecture50, physical page{page}, printed footer{page-1565}: {title}; supplied scenario derives from the displayed concept'+('; exact program behavior is in the pinned notebook.'if code else'.'),evidenceText=(R/f'sources/text/lectures/page-{page:04}.txt').read_text());q['citations'].append(c)
 q['solution']={'justification':exps[key-1],'optionExplanations':{f'o{i+1}':e for i,e in enumerate(exps)},'steps':steps or[],'formulas':forms or[],'simpleExplanation':exps[key-1],'memoryAid':None,'misconceptions':[e for i,e in enumerate(exps)if i!=key-1],'examTraps':[],'prerequisiteConceptIds':[]}
 if code:q['primaryEvidence']=copy.deepcopy(qs[23]['primaryEvidence']);q['primaryEvidence'][0].update(locator=code,executionEvidence='audits/W10-L50-v2-author-checks.json',checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
 else:q.pop('primaryEvidence',None)
 b['questions'].append(q);qs[n]=q;b['concepts'].append({'id':f'W10-L50-C-gap-{n}','title':title,'description':exps[key-1],'slideIds':[f'lectures-p{x}'for x in pages],'questionIds':[q['id']],'status':'drafted','topic':q['topic'],'subtopic':title,'prerequisiteConceptIds':[],'examinationAngles':[q['cognitiveSkill']]})
new(66,'Multi-axis centered resultant and plotting limit',
 'Use the notebook convention, not the different slide half-range formula. Begin with all eight angular-axis values50, then set happy80, welcome90 and friend70 and their complements. Angles in degrees are happy112, welcome22, friend67, curious157, sad292, distant202, strange247 and frustrated337. Sum each centered value(v−50) times its unit vector. The mood is the nearest named axis for radius≥10, with first dictionary entry breaking an exact tie. Which result is correct, rounded to two decimals?',
 ['x67.33, y122.42, raw radius139.71, angle61.19°, FRIEND, plotted radius100.',
  'x33.66, y61.21, raw radius69.86, angle61.19°, FRIEND, plotted radius69.86.',
  'x67.33, y122.42, raw radius139.71, angle28.81°, WELCOME, plotted radius100.',
  'x67.33, y122.42, raw radius100, angle61.19°, FRIEND, plotted radius100.'],1,
 ['Opposite centered members reinforce their paired direction; the computed raw radius is retained even though the plot clips its arrow to100.',
  'This counts only one centered member of each complementary pair and halves both vector components.',
  '28.81° swaps the x/y roles in the angular calculation; atan2(y,x) gives61.19°.',
  'The plotting clip does not replace the engine’s stored raw radius.'],[1572,1573,1574,1576],
 steps=['Complement values are sad20, distant10 and strange30; curious and frustrated stay50.','Each opposite pair contributes twice the active centered value along its active axis.','Compute x=60cos112°+80cos22°+40cos67°=67.3276 and y=60sin112°+80sin22°+40sin67°=122.4198.','Use hypot(x,y)=139.7125 and atan2(y,x)=61.1904°.','The closest axis is friend67°; clipping only the displayed radius gives100.'],
 forms=[form('x=Σ(v_i−50)cos θ_i; y=Σ(v_i−50)sin θ_i; r=hypot(x,y); θ=atan2(y,x) mod360°',{'v_i':'State value on axis i','θ_i':'Assigned axis direction','x,y':'Resultant Cartesian components','r':'Raw resultant magnitude','θ':'Resultant direction'},{'v_i,x,y,r':'Demonstration state units','θ_i,θ':'Degrees' },['Use all eight angular axes and their stated complements; convert degrees appropriately for trigonometric functions.','No clipping of r occurs in the state update; only the plot clips to100.'])],code='Cells9 and19: RobotEmotionEngine.update and _plot_engine.',typ='numerical',difficulty='hard')
new(67,'Three-turn state persistence and confidence boundary',
 'Run the pinned notebook’s state-mapping and policy functions with synthetic results, not live inference. Start the robot at default state and fresh80. Process (fearful, confidence0.8, valence−0.5, arousal0.5), then (sad,0.30,−0.6,−0.4), then the failure fallback (neutral,0,0,0). Each turn maps the human state, updates robot policy, then drains fresh by2. Which final values follow?',
 ['Human happy50/friendly50; robot welcome60/friend82/curious62/happy50/fresh74.',
  'Human happy50/friendly50; robot welcome88/friend82/curious62/happy50/fresh74.',
  'Human happy41/friendly56; robot welcome88/friend82/curious62/happy50/fresh74.',
  'Human happy50/friendly50; robot welcome92/friend85/curious62/happy50/fresh74.'],2,
 ['The zero-confidence fallback returns from the early curiosity branch; it does not execute the default label branch’s welcome60 assignment.',
  'The confidence0.30 sad turn sets88/82, and the failure fallback resets human mapped axes while preserving those unrelated robot dimensions.',
  '41/56 are the second turn’s human values; the zero-confidence third mapping returns them to50/50.',
  'The guard is strictly below0.30, so the second turn executes the sad branch and replaces the earlier fearful targets.'],[1576,1588],
 steps=['Fearful0.8 sets robot welcome92, friend85, curious58; fresh becomes78.','Sad0.30 is not below0.30, so it sets welcome88, friend82, curious62; fresh becomes76.','Fallback confidence0 maps human happy/friendly to50 and enters only the early curiosity branch.','Other robot axes persist; the third battery drain gives fresh74 and tired26.'],code='Cells9,11,17 and21; synthetic source-cell trace recorded in W10-L50-v2-author-checks.',difficulty='hard')
new(68,'Memory cap versus prompt transport messages',
 'Memory starts empty and stores seven complete input/reply pairs before preparing reply8. In the notebook, add_turn retains the last12 message entries; analyse_emotion packs history[-6:] inside one user prompt plus a system message; generate_reply sends a system message, history[-8:] and the current input. Which counts apply before reply8, and which pairs remain after it is saved?',
 ['Classifier:8 transport messages; reply:10 transport messages; after saving, pairs3–8 remain and turn_count8.',
  'Classifier:2 transport messages; reply:8 transport messages; after saving, pairs3–8 remain and turn_count8.',
  'Classifier:2 transport messages; reply:10 transport messages; after saving, pairs3–8 remain and turn_count8.',
  'Classifier:2 transport messages; reply:10 transport messages; after saving, pairs1–8 remain and turn_count6.'],3,
 ['Six history entries are serialized inside one prompt; they are not six additional transport messages for classification.',
  'The reply has eight historical messages plus one system and one current user message.',
  'Classification uses two transport messages, reply generation uses ten, and trimming retains six pairs while the lifetime counter reaches eight.',
  'The list cap retains twelve messages, or six pairs, but does not reset turn_count.'],[1576,1588],
 steps=['Before reply8, history stores pairs2–7, which is12 messages.','Classification embeds the last three pairs inside its user prompt and sends2 messages total.','Reply generation includes the last four pairs plus system/current input:8+2=10.','Adding pair8 trims pair2, retaining pairs3–8 with turn_count8.'],code='Cells13 and15: ConversationMemory.add_turn, analyse_emotion and generate_reply.',difficulty='hard')
new(69,'Blank input, reset and stored facts',
 'For the pinned demonstration, compare submitting whitespace-only input, adding a normal input/reply pair, and pressing Reset. Which behavior follows the actual code?',
 ['Whitespace returns before analysis or memory change; adding a pair does not extract known_facts; Reset creates fresh engines/memory and clears last_analysis.',
  'Whitespace adds a neutral turn; adding a pair does not extract known_facts; Reset creates fresh engines and memory.',
  'Whitespace returns before analysis; add_turn extracts the user’s name into known_facts whenever the input contains “name”; Reset preserves that fact.',
  'Whitespace returns before analysis; adding a pair does not extract known_facts; Reset clears only the visible log while keeping turn_count and engine state.'],1,
 ['The early return, explicit add_turn implementation and reset assignments establish these three separate behaviors.',
  'The blank-input guard returns before analysis and add_turn.',
  'No fact-extraction code runs inside add_turn, and reset replaces memory with a new object.',
  'reset_demo reconstructs the engines and memory and sets last_analysis=None.'],[1576,1588],code='Cells13 and21: add_turn, submit_message blank-input guard and reset_demo.',difficulty='medium')
new(70,'Full classifier head and trainable scope',
 'Suppose the five-block feature extractor in the illustration outputs7×7×512 values. Compare Flatten with global average pooling to512 features before the shown256→128→8 dense head. Each dense output has one bias; dropout has no trainable parameters. Which head totals and training-scope statement are correct?',
 ['Flatten6,456,712; pooling165,256; classifier-only training also updates all five convolutional blocks.',
  'Flatten6,456,320; pooling164,864; classifier-only training leaves the backbone weights fixed.',
  'Flatten165,256; pooling6,456,712; partial tuning updates the final convolutional block plus the head.',
  'Flatten6,456,712; pooling165,256; classifier-only training freezes the backbone, while the illustrated partial strategy also tunes its last block.'],4,
 ['The totals are correct, but classifier-only training does not update the backbone blocks.',
  'These totals omit the256+128+8=392 dense biases.',
  'The totals are exchanged: flattening retains25,088 features, while averaging leaves512.',
  'Count each dense layer’s weights and biases; the source distinguishes head-only, last-block and full-network trainable scopes without guaranteeing their performance order.'],[1579,1580],
 steps=['Flatten produces7×7×512=25,088 inputs; global averaging produces512.','The later layers contribute(256+1)×128+(128+1)×8=33,928 parameters.','Flatten head:25,089×256+33,928=6,456,712.','Pooled head:513×256+33,928=165,256.','Dropout adds no trainable parameters; changing trainable scope does not by itself guarantee accuracy.'],
 forms=[form('P=(d+1)×256+(256+1)×128+(128+1)×8',{'P':'Total trainable parameters in the three dense layers','d':'Input feature count after reduction'},{'P':'Parameter count','d':'Feature count'},['Each output has one bias.','Dropout and feature reduction add no trainable parameters in this exercise.','Feature-map dimensions are supplied, not inferred from an unspecified input image size.'])],typ='numerical',difficulty='hard')
new(71,'Dataset targets, representation and domain limits',
 'A course exercise needs facial-expression classes plus continuous valence/arousal targets. Use only the slide’s displayed dataset descriptions, not undocumented benchmark claims. Which source-and-evaluation plan fits those requirements?',
 ['Use FER2013 because grayscale pixels alone define continuous valence and arousal targets, then assume color conversion supplies any missing labels.',
  'Use the displayed AffectNet targets; distinguish FER2013’s grayscale and RAF-DB’s listed grayscale/RGB descriptions, align labels and test new lighting/occlusion conditions rather than assuming transfer.',
  'Use the RAF-DB categorical example and replace each class number with the same numeric value for both valence and arousal without annotation or a stated mapping.',
  'Use speech MFCCs as if they were the facial-image labels, then treat a shared category name as proof of performance under new camera conditions.'],2,
 ['Pixel channels do not create missing supervised target annotations.',
  'The slide explicitly lists AffectNet class and valence/arousal targets; representation compatibility and target-domain evaluation remain separate requirements.',
  'A category code is not automatically a valid continuous affect annotation.',
  'Acoustic features are a different input modality, and shared label names do not establish camera-domain performance.'],[1581,1582,1583,1585,1590],difficulty='medium',assumptions=['Dataset channel descriptions are reported as displayed in this lecture, not a verified claim about every distribution or preprocessing variant.','No photographed person’s private internal state is inferred in this exercise.'])
for n in flags:
 q=qs[n];q['version']=2;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('build_robotics_study_app:L50-v2-author');q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']]
assert all(question_hash(q)==accepted[q['id']]for q in b['questions']if q['id']in accepted)
schema=json.loads((R/'data/schema.question.json').read_text());errors=[(q['id'],schema_errors(q,schema))for q in b['questions']if schema_errors(q,schema)];assert not errors,errors
changed=flags+list(range(66,72));packet=[]
for n in changed:
 q=qs[n];x={k:copy.deepcopy(q[k])for k in ['id','version','stem','selectionMode','type','difficulty','options','assumptions','citations']}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
archive.write_text(p.read_text());p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');out=R/'audits/blind-W10-L50-v2-and-gaps.json';out.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'flaggedRevised':35,'newQuestions':6,'preservedAcceptedCount':30,'preservedAcceptedHashes':accepted,'packetSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'actualPagesReinspected':list(range(1568,1594)),'boundedGaps':{'L50-G01':['Q066'],'L50-G02':['Q067','Q068','Q069'],'L50-G03':['Q070'],'L50-G04':['Q071']},'authorChecks':'audits/W10-L50-v2-author-checks.json','restrictions':'Only default installed Python deterministic source cells and inert local client stub; no live model, installation, hardware, denied environment or access-route bypass.','scientificScope':'Preserve all original polar-formula, axis-layout, label taxonomy and model-confidence qualifications. Source disagreement is not silently resolved by rewriting the lecture.'}
(R/'audits/W10-L50-v2-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'questions':len(b['questions']),'revised':35,'new':6,'packetSha256':manifest['packetSha256']}))
