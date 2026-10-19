from pathlib import Path
import json,copy,hashlib,datetime,re,sys
R=Path('/workspace/shared/Btech_Hons/sem-5/ai-for-robotics');sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import DraftBatch
p=R/'data/question-batches/W06-L26.json';old=json.loads(p.read_text());report=json.loads((R/'audits/W06-L26-independent-summary.json').read_text());nums={int(f['questionId'][-3:]) for f in report['findings']}
b=DraftBatch('W06-L26',6,'L26',old['questions'][0]['topic'],774,old['authorId']);b.questions=copy.deepcopy(old['questions']);b.concepts={c['id']:copy.deepcopy(c) for c in old['concepts']};qs={int(q['id'][-3:]):q for q in b.questions}
h=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ['status','reviewIds']},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert len(nums)==47 and all(qs[n]['version']==1 for n in nums)
preserve={q['id']:h(q) for q in old['questions'] if int(q['id'][-3:]) not in nums}
archive=R/'audits/batch-history/W06-L26-before-v2-quality-repairs.json';assert not archive.exists();archive.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
def opts(n,txt,rs):
 q=qs[n];lookup=dict(zip(['o1','o2','o3','o4'],txt));q['solution']['optionExplanations']=dict(zip(['o1','o2','o3','o4'],rs))
 for o in q['options']:o['text']=lookup[o['id']]
def explain(n,t,steps=None):
 qs[n]['solution']['justification']=qs[n]['solution']['simpleExplanation']=t
 if steps is not None:qs[n]['solution']['steps']=steps
opts(1,[
 'It can learn useful regularities across examples rather than requiring a separate hand-written rule for every variation',
 'A large training set is sufficient even when its appearances are unrelated to the intended environment',
 'Adding model parameters can substitute for checking whether training examples represent the new conditions',
 'Learning removes rule maintenance, so a trained recognizer need not be reassessed after the input distribution changes'],[
 'This is the stated reason for considering learning, subject to representative data and evaluation.',
 'The amount of data alone does not make unrelated examples representative.',
 'Capacity alone does not establish relevant training coverage or reliable generalization.',
 'A learned model may also need reassessment or updates when operating conditions change.'])
opts(3,[
 'Difficulty translating human recognition knowledge into executable rules',
 'Lack of human expertise about which images show defects',
 'Absence of labeled defect examples, even though reliable executable conditions have already been written',
 'A rule evaluator that cannot implement the experts’ already specified numeric tests'],[
 'The experts can recognize the defect but cannot express usable conditions.',
 'The premise says the experts can recognize defects, so recognition expertise is available.',
 'The stated obstacle is expressing rules, not a claim that rules already exist but labels are missing.',
 'No executable numeric tests have yet been specified; this is not an evaluator limitation.'])
opts(4,[
 'Review the new pattern and revise or add suitable rules while retaining useful existing rules',
 'Keep the blacklist unchanged because rules for older patterns necessarily detect the new pattern',
 'Add a rule matching every occurrence of one common word without checking the resulting false positives',
 'Assume the fixed blacklist updates itself when a new message is passed to the filter'],[
 'Domain changes can require targeted maintenance rather than an automatic full rewrite.',
 'Existing rules may miss a genuinely new pattern.',
 'An overbroad new rule may also flag legitimate messages; its effect needs checking.',
 'The printed fixed blacklist has no automatic learning or update mechanism.'])
opts(7,[
 'SPAM with trigger urgent',
 'NOT SPAM because urgent is not a separate word',
 'SPAM with trigger insurgent, returning the whole input as the trigger',
 'The Boolean value True rather than a classification string'],[
 'The substring urgent occurs inside insurgent and is the matching blacklist entry.',
 'The membership test does not require a whole-word boundary.',
 'The return string uses the matched blacklist entry, not the entire input text.',
 'The membership test is Boolean, but the function returns a formatted classification string.'])
opts(8,[
 'None of the exact listed substrings occurs, although the slide presents it as a missed spam variant',
 'The phrase free money matches whenever its first word free occurs, so the filter should return that trigger',
 'The phrase no cost is treated as a semantic synonym of free money by Python string membership',
 'The filter tests uppercase FREE against the lowercase blacklist without normalizing the input'],[
 'The code tests complete listed substrings, not isolated words or semantic meaning.',
 'Matching one word does not match the full two-word substring free money.',
 'Literal string membership does not infer semantic synonyms.',
 'The function explicitly lowercases the message before searching.'])
opts(9,[
 'Left-align the classification in a minimum 20-character field and print at most the first 55 message characters',
 'Truncate every classification to 20 characters and print the final 55 message characters',
 'Right-align the classification and delete the first 55 message characters',
 'Left-align the classification in a minimum 20-character field and include message indices 0 through 55'],[
 'The field width is a minimum, and the slice excludes index 55.',
 'Field width does not truncate a longer classification, and the slice starts at the beginning.',
 'The alignment direction and slice interpretation are both reversed.',
 'The slice stop is exclusive, so it includes indices 0 through 54 at most.'])
opts(22,[
 'Pass the feature and label arrays to the estimator’s fitting operation; no remote upload is shown',
 'Upload the arrays to a cloud service because the method name fit requires a remote transfer',
 'Predict labels for X_tr without using y_tr to establish the fitted estimator',
 'Append y_tr as an additional input feature and train without a separate target array'],[
 'This follows the displayed local estimator call.',
 'The shown call does not specify a network service or upload operation.',
 'This confuses fitting on paired data with predicting from an already fitted model.',
 'The two arguments provide separate feature and target arrays; the labels are not appended as input features.'])
opts(25,[
 'The learning task and feedback, such as target labels, unlabeled structure or interaction rewards',
 'Whether the model uses a neural network, a tree or a distance rule, independently of its training feedback',
 'Whether inputs contain continuous numbers rather than categories, independently of labels or rewards',
 'Whether predictions are produced online or in a batch, independently of the signal used to learn'],[
 'This distinguishes the introductory learning paradigms by their task and available feedback.',
 'A model family does not by itself determine the learning paradigm.',
 'Input data type does not determine whether learning uses labels, structure or rewards.',
 'Online versus batch use is a different distinction from the type of learning feedback.'])
opts(32,[
 'Store labeled examples, receive a query, find its closest training point and return that point’s label',
 'Store labeled examples, count the most frequent label in the whole training set and return it for every query',
 'Store labeled examples, compute each class centroid and return the label of the nearest centroid',
 'Store labeled examples, select the nearest point using only the first feature even when the metric uses both'],[
 'This is the displayed single-neighbor sequence.',
 'Global majority ignores the query’s local nearest neighbor.',
 'Nearest-centroid classification is a different procedure from selecting an individual training neighbor.',
 'The declared two-feature distance must use both coordinates.'])
opts(48,[
 'NumPy constructs numeric arrays; Matplotlib plots figures; KNeighborsClassifier supplies the classifier',
 'Matplotlib constructs the numeric input arrays; NumPy plots figures; KNeighborsClassifier supplies the classifier',
 'NumPy constructs numeric arrays; KNeighborsClassifier plots figures; Matplotlib supplies the classifier',
 'NumPy constructs numeric arrays; Matplotlib plots figures; ListedColormap supplies the nearest-neighbor classifier'],[
 'This matches the imported objects and their uses.',
 'This swaps the numeric-array and plotting roles.',
 'This swaps the plotting package with the estimator.',
 'ListedColormap controls a discrete palette, not the classification algorithm.'])
opts(54,[
 'MSE=SSE/n scales the objective by a positive constant that does not depend on the fitted parameters',
 'The minimum SSE and minimum MSE must have the same numeric value for every positive n',
 'Dividing the objective by n also divides every minimizing model coefficient by n',
 'Multiplying an objective by any nonzero constant preserves its minimizers, including negative constants'],[
 'Positive parameter-independent scaling preserves the ordering of objective values.',
 'The minimizing parameter set agrees, but the minimum values generally differ by n.',
 'Scaling the objective is not the same as rescaling the minimizing parameter values.',
 'Negative scaling reverses objective ordering; the positive sign is essential.'])
opts(56,[
 'The diagram illustrates an iterative fitting idea, but OLS can also use suitable direct linear-algebra methods',
 'Every OLS implementation must use that exact iterative loop and a hand-selected initial slope',
 'Changing the numerical solver necessarily changes the squared-error objective into a different learning criterion',
 'A direct least-squares solve first needs the same initial slope used by the illustrated parameter-update loop'],[
 'A fitting objective and the numerical method used to minimize it are distinct.',
 'The diagram is not a universal implementation trace for all OLS solvers.',
 'Different solvers can minimize the same ordinary squared-error objective.',
 'A direct least-squares method does not require an initial slope for an iterative parameter search.'])
explain(34,'The coordinate differences are 3 and 4, so the Euclidean distance is √(3²+4²)=√25=5.',['Square the coordinate differences: 3²=9 and 4²=16.','Add the squares: 9+16=25.','Take the square root: √25=5.'])
qs[42]['difficulty']='easy'
explain(42,'The point [0.8, 60] has squared coordinate differences 0.01 and 4, totaling 4.01, which is smaller than the squared distances to the other training points.',['For [0.8, 60], compute coordinate differences [0.1, −2].','Compute the squared distance: 0.1²+2²=4.01.','Compare with 9.04, 729.09, 1024.04 and the larger distances to the two low-frequency points.','Take √4.01≈2.0025.'])
# Explicit prose corrections only; keep source evidence, code identifiers, literals and mathematical subscripts unchanged.
replacements={
 'slide’s8-bit':'slide’s 8-bit','intensity0':'intensity 0','and255':'and 255','maps0':'maps 0','are8×8':'are 8×8',
 'An8×8':'An 8×8','permits256':'permits 256','are64':'are 64','and256':'and 256','gives256':'gives 256','all64positions':'all 64 positions','by64':'by 64','Compute8×8=64pixels.':'Compute 8×8=64 pixels.','Multiply256 choices64times.':'Multiply 256 choices 64 times.','Use256=2^8 to obtain2^(8×64).':'Use 256=2^8 to obtain 2^(8×64).',
 'displayed8×8':'displayed 8×8','Length64':'Length 64','Length8':'Length 8','Length256':'Length 256','values[':'values [','all64cells':'all 64 cells','starts0':'starts 0',
 'exact1NN':'exact 1NN','snippet,37 of38':'snippet, 37 of 38','is37/38':'is 37/38','by100':'by 100','prevents100percent':'prevents 100 percent','Divide37 by38.':'Divide 37 by 38.','Convert to97.3684percent.':'Convert to 97.3684 percent.',
 'than2.5':'than 2.5','than5.0':'than 5.0','uses1':'uses 1','uses5':'uses 5',
 'class0':'class 0','class1':'class 1','Class0':'Class 0','Class1':'Class 1','label0':'label 0','label1':'label 1','label2':'label 2','be0':'be 0',
 'displayed1NN':'displayed 1NN','The1NN':'The 1NN','with1NN':'with 1NN','in1NN':'in 1NN','namely0.5':'namely 0.5',
 'between(0,0)':'between (0,0)','and(3,4)':'and (3,4)','labels[':'labels [','for1':'for 1','for0':'for 0','mean2/3':'mean 2/3',
 'from1to3to9':'from 1 to 3 to 9','floor0':'floor 0','gravel1and':'gravel 1 and','grass2':'grass 2',
 'of[speed':'of [speed','row[':'row [','value2':'value 2','query[':'query [','is1;':'is 1;','value62':'value 62','label 0entry':'label 0 entry','label 2entry':'label 2 entry','Gravel(Red)':'Gravel (Red)',
 'as[[':'as [[','by[0]':'by [0]',';[0]selects':'; [0] selects',';[0]sets':'; [0] sets',';[0]discards':'; [0] discards',';[0]selects':'; [0] selects','assigning class 0':'assigning class 0','supplied1×2query':'supplied 1×2 query',
 'has100percent':'has 100 percent','around1':'around 1','span10to65':'span 10 to 65','from1to0to':'from 1 to 0 to',
 'is2×3':'is 2×3','gives2.5':'gives 2.5','Multiply2×3':'Multiply 2×3','and−1×4':'and −1×4','products to2.':'products to 2.','Add0.5.':'Add 0.5.',
 'x[0]through x[p]but':'x[0] through x[p] but','Indices0throughp containp+1features;exactlyp features use0throughp−1':'Indices 0 through p contain p+1 features; exactly p features use 0 through p−1',
 'Indices0throughp containp features':'Indices 0 through p contain p features','Exactlyp features require indices1throughp+1':'Exactly p features require indices 1 through p+1','from0to p hasp+1entries':'from 0 to p has p+1 entries','Index0is':'Index 0 is','containsp+1entries':'contains p+1 entries',
 'targets[':'targets [','predictions[':'predictions [',']and ':'] and ','are[':'are [','to3':'to 3','residuals1':'residuals 1','Square to1,1,1and sum to 3.':'Square the residuals to obtain 1, 1 and 1, then sum them to 3.','Divide byn=3to obtainMSE=1.':'Divide by n=3 to obtain MSE=1.',
 'numbern':'number n','andSSEalways':'and SSE always','unlessn=1orSSE=0':'unless n=1 or SSE=0','WriteMSE=(1/n)SSEwithn>0fixed.':'Write MSE=(1/n)SSE with fixed n>0.','by1/npreserves':'by 1/n preserves',
 'output3D':'output 3D','to3D':'to 3D','treats3D':'treats 3D','everyMLdataset':'every ML dataset','an8×8pixel':'an 8×8 pixel','wholeimagecan':'whole image can',
}
def tidy(s):
 for a,z in replacements.items():s=s.replace(a,z)
 # Spaces after prose punctuation also remain valid inside displayed numeric arrays and function calls.
 s=re.sub(r',(?=[A-Za-z])',', ',s);s=re.sub(r';(?=\S)','; ',s)
 s=s.replace(']and','] and').replace(']but','] but')
 return s

def walk(v):
 if isinstance(v,str):return tidy(v)
 if isinstance(v,list):return [walk(x) for x in v]
 if isinstance(v,dict):return {k:walk(x) for k,x in v.items()}
 return v
for n in nums:
 q=qs[n]
 for k in ['stem','subtopic','assumptions','options','solution']:q[k]=walk(q[k])
 if 'conflictResolution' in q:q['conflictResolution']['basis']=tidy(q['conflictResolution']['basis'])
 q['version']=2;q['revisionAuthors']=['robotics-integration-author-L26'];q['status']='draft';q['reviewIds']=[]
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
 for cid in q['conceptIds']:b.concepts[cid]=walk(b.concepts[cid])
# The Ridge counterexample is on physical page 787.
c=next(copy.deepcopy(c) for q in old['questions'] for c in q['citations'] if c['physicalPage']==787);c['kind']='table';c['role']='premise';qs[52]['citations'].append(c)
for cid in qs[52]['conceptIds']:
 if 'lectures-p0787' not in b.concepts[cid]['slideIds']:b.concepts[cid]['slideIds'].append('lectures-p0787')
b.add(788,'neighbor-similarity-assumption','Test the assumption behind neighbor labels',
 'A 1NN classifier uses measured features to copy the nearest training label; which condition most directly supports expecting this label to be useful on a new query?',
 ['Nearby points under the chosen features and distance tend to share the relevant output, with sufficiently representative labeled examples',
 'Each class has exactly the same number of examples, even if the features carry no information about the class',
 'The number of measured features equals the number of classes, regardless of which distances are small',
 'The training rows are sorted by label before distances are computed, even if nearby points usually have different labels'],0,
 'The source relies on local similarity in feature space being related to output similarity; label transfer can fail when that relationship or representative coverage is absent.',
 ['This is the similarity premise, not a guarantee for every query.',
 'Equal class counts do not make unrelated features predictive.',
 'Matching dimension and class count does not establish a useful distance-label relation.',
 'Row order is not the similarity assumption and does not repair contradictory local labels.'],typ='scenario',difficulty='easy',assumptions=['The nearest neighbor is selected using the stated metric, and ties are not at issue.'])
b.save();assert all(h(next(q for q in b.questions if q['id']==k))==v for k,v in preserve.items())
full=json.loads((R/'audits/blind-W06-L26.json').read_text());ids={qs[n]['id'] for n in nums}|{'W06-L26-Q061'};packet=[q for q in full if q['id'] in ids];fp=R/'audits/blind-W06-L26-v2-quality-repairs.json';fp.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'batchId':'W06-L26','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changedQuestionIds':sorted(ids),'acceptedHashesPreserved':preserve,'packetSha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'revisionNotes':['47 revisions address the frozen independent review.','Added one question for the p788 similarity assumption.','13 prior accepted hashes remain exactly unchanged.','No source qualifications have been globally resolved.'],'review':'pending independent re-review with prior exposure disclosed'};(R/'audits/W06-L26-v2-quality-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared',len(ids),'objects. Packet SHA',manifest['packetSha256'])
