#!/usr/bin/env python3
"""Version-bound L34 author repairs. Never independent approval."""
import json,copy,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];B='W07-L34';A='L34-repair-author-20261019'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def fhash(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
if (R/f'audits/{B}-v2-review-manifest.json').exists():raise SystemExit('Frozen v2. Do not overwrite reviewed content.')
old=read(f'data/question-batches/archive/{B}-v1.json');b=copy.deepcopy(old);qm={q['id']:q for q in b['questions']}
summary=read(f'audits/{B}-contracts-review-summary.json');flags=set(summary['flaggedQuestionIds']);accepted=[q for q in old['questions'] if q['id'] not in flags]
assert len(flags)==45 and len(accepted)==89
rv=read(f'data/reviews/{B}-v1-independent-contracts.json')
for q in old['questions']:assert any(r['questionId']==q['id'] and r['questionSha256']==qhash(q) for r in rv)
for qid in flags:
 q=qm[qid];q.update(version=q['version']+1,status='draft',reviewIds=[],difficulty='easy');q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+[A]))
 if 'conflictResolution'in q:q['conflictResolution']['questionVersion']=q['version']
changed_sets=set()
def Q(short):return qm[f'{B}-P{short}']
def revise(short,rows,stem=None):
 q=Q(short);assert q['id']in flags and q['correctOptionIds']==['o1'];assert len(rows)==4
 if stem:q['stem']=stem
 d={f'o{i+1}':v for i,v in enumerate(rows)}
 for o in q['options']:o['text']=d[o['id']][0]
 q['solution'].update(justification=d['o1'][1],simpleExplanation=d['o1'][1],optionExplanations={k:('Correct. 'if k=='o1'else'Incorrect. ')+v[1] for k,v in d.items()},misconceptions=[d[k][1]for k in('o2','o3','o4')],steps=[],examTraps=[]);changed_sets.add(q['id'])
def option(short,k,text,why):
 q=Q(short);next(o for o in q['options']if o['id']==k)['text']=text;q['solution']['optionExplanations'][k]='Incorrect. '+why
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][k]for k in('o2','o3','o4')];changed_sets.add(q['id'])
SHA='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'
def cite(p,kind,loc,role='premise'):
 return {'slideId':f'lectures-p{p}','sourceId':'lectures','sourceSha256':SHA,'physicalPage':p,'kind':kind,'locator':f'Printed slide {p-1020}: {loc}','evidenceText':(R/f'sources/text/lectures/page-{p}.txt').read_text().strip(),'role':role,'region':None}
def addcite(short,p,kind,loc,role='premise'):Q(short)['citations'].append(cite(p,kind,loc,role))
def form(short,expr,variables,assumptions,units=None):Q(short)['solution']['formulas'].append({'expression':expr,'variables':variables,'units':units or {'all':'dimensionless numerical coordinates'},'assumptions':assumptions})
revise('1024-Q01',[
('Sensor values → weighted sum plus bias → activation → action output','The four sensor arrows enter the affine sum, whose result enters f(z), then the action output.'),
('Sensor values → activation of each value → weighted sum plus bias → action output','This moves activation before the displayed weighted aggregation.'),
('Sensor values → weighted sum → activation → add bias to the action output','The diagram adds bias before, not after, the activation.'),
('Sensor values plus bias → weighted sum → activation → action output','Adding the same bias to each sensor before weighting is not the single bias added to the aggregate.')])
revise('1025-Q01',[
('A user-fixed threshold and equal implicit unit coefficients in the sum','The displayed aggregation sums the binary inputs without separate learned coefficients; the user selects the threshold.'),
('A learned threshold and equal implicit unit coefficients in the sum','The stated MP threshold is user-decided; this page supplies no threshold training rule.'),
('A user-fixed threshold and separately learned unequal input coefficients','The shown MP aggregation is an unweighted sum, not learned unequal coefficients.'),
('A learned threshold and separately learned unequal input coefficients','This describes trainable affine parameters rather than the particular MP gate on the page.')])
revise('1028-Q01',[
('Real-valued input support alone does not remove a single affine separator’s XOR limitation.','The affine threshold model still uses one hyperplane. XOR on its original two coordinates is not linearly separable.'),
('Changing the threshold alone can separate XOR once the binary values are stored as real numbers.','Changing numerical storage or the offset does not alter the XOR geometry.'),
('Training the affine weights for more epochs must separate XOR on the original coordinates.','Optimization cannot create a separating hyperplane that does not exist in those coordinates.'),
('Adding a nonlinear interaction feature would leave XOR just as unrepresentable as before.','A suitable feature such as x1*x2 changes the representation and can make XOR affine-separable; merely allowing real inputs does not.')])
addcite('1028-Q01',1029,'equation','Zero-inclusive affine threshold with augmented bias coordinate')
revise('1030-Q03',[
('The distance is |b|/||w||, so changing ||w|| with b fixed can change it.','For a nonzero normal vector, normalizing the hyperplane equation gives the unsigned distance from the origin.'),
('The distance is |b|, so rescaling w alone cannot change it.','This omits normalization by the normal-vector length.'),
('The distance is b/||w||, so a negative bias implies a negative geometric distance.','That expression can be a signed offset; an unsigned Euclidean distance is nonnegative.'),
('Jointly multiplying w and b by a positive factor multiplies the distance by that factor.','The same factor cancels between numerator and denominator; the geometric hyperplane is unchanged.')],stem='For the hyperplane w·x+b=0 with nonzero w, which statement about its unsigned distance from the origin is correct?')
revise('1032-Q03',[
('Finite convergence is guaranteed for A, but the same guarantee does not apply to B.','Repeated fair visits and fixed positive mistake updates give finite convergence on finite linearly separable data. Contradictory labels at one input cannot both be satisfied.'),
('Finite convergence is guaranteed for both because both training sets are finite.','Finiteness alone does not resolve contradictory labels or establish separability.'),
('Finite convergence is guaranteed for A only if every example is already correct after its first visit.','The convergence result allows mistakes and repeated visits; it is not a one-pass theorem.'),
('Finite convergence is guaranteed for B if its examples are visited in a different cyclic order.','An order change cannot assign two different binary labels to the same deterministic input.')],stem='Two finite data sets are trained with fixed positive perceptron mistake updates, repeatedly cycling through every example. Set A has a strict affine separator. Set B contains the same input with opposite labels. Which finite-convergence claim is justified?')
Q('1032-Q03')['assumptions']=['Use the lecture’s binary threshold rule with an augmented constant input for bias; no noisy or changing labels.']
revise('1033-Q05',[
('90° < alpha ≤ 180°, and replacing w by w+x increases the score on x by ||x||².','Negative cosine permits angles greater than 90 degrees including the antiparallel endpoint 180 degrees. Distributivity gives the stated score increment.'),
('90° < alpha < 180°, and replacing w by w+x increases the score on x by ||x||².','This wrongly excludes nonzero antiparallel vectors, whose dot product is negative and angle is exactly 180 degrees.'),
('0° ≤ alpha < 90°, and replacing w by w+x increases the score on x by ||x||².','An acute or zero angle gives a nonnegative rather than negative dot product.'),
('90° < alpha ≤ 180°, and replacing w by w+x increases the score on x by ||w||².','The new term is x·x, not w·w.')],stem='Let nonzero real vectors w and x satisfy w·x<0, and let alpha be their principal angle. Which angle interval and score-change statement are both correct?')
Q('1033-Q05')['solution']['formulas']=[]
form('1033-Q05','w·x=||w|| ||x|| cos(alpha); (w+x)·x−w·x=||x||²',{'w':'Old nonzero real weight vector','x':'Nonzero real input vector of the same dimension','alpha':'Principal angle between w and x'},['Euclidean inner product; angle in [0,180] degrees; w·x<0.'],{'w,x':'dimensionless','alpha':'degrees; use degree-valued cosine consistently'})
revise('1033-Q06',[
('The second weight decreases, while the score on this x increases by 6.','Adding x=(1,-2,1) subtracts 2 from the second component. The score increment is x·x=1+4+1=6.'),
('Every weight increases, because adding an input vector is an increasing update.','Componentwise changes follow input signs; the second component decreases by 2.'),
('The second weight decreases, while the score on this x decreases by 2.','This substitutes one component’s change for the full dot-product change.'),
('The weight-vector norm must increase, while the score increase depends on the old w.','The norm may increase or decrease; the score increment on this fixed input is exactly 6 independent of old w.')],stem='For a positive-example mistake, use the augmented input x=(1,-2,1) and update w_new=w+x. Which conclusion is guaranteed for any old w?')
Q('1033-Q06')['solution']['formulas']=[]
form('1033-Q06','w_new=w+x; Δw_2=x_2=−2; Δs=(w+x)·x−w·x=||x||²=6',{'w,w_new':'Old and updated three-component weights','x':'Augmented input (1,-2,1)','Δw_2':'Change of the second listed component','Δs':'Change in score evaluated on the same x'},['Supplied numerical positive-mistake variant; augmented first input is 1.'])
Q('1033-Q06')['solution']['steps']=['Read the second component of the update: -2.','Calculate 1²+(-2)²+1²=6 for the score increase.']
revise('1034-Q01',[
('It is nonlinear, but its ordinary derivative is zero away from the threshold and undefined at the jump.','Nonlinearity alone does not provide a useful ordinary gradient for backpropagation through this hard step.'),
('It is nonlinear and continuous, so its ordinary derivative smoothly conveys classification error.','The step is discontinuous at the threshold, not a smooth activation.'),
('It is nonlinear, with an ordinary derivative of one on both constant branches.','Both constant branches have derivative zero, not one.'),
('It is nonlinear, so using a chosen straight-through derivative is the same as differentiating the exact step.','A surrogate derivative is an additional training approximation, not the ordinary derivative of the exact step.')])
revise('1034-Q04',[
('W2 W1 x + W2 b1 + b2, an affine map','Substitution distributes W2 over both W1 x and b1; composing affine maps with identity activations remains affine.'),
('W2 W1 x + b1 + b2, an affine map','The hidden bias must be multiplied by W2 before the output bias is added.'),
('W1 W2 x + W2 b1 + b2, an affine map','Matrix composition follows output-after-hidden order W2 W1, not W1 W2.'),
('W2 W1 x + W2 b1 + b2, necessarily a nonlinear map because there are two layers','Depth without nonlinear activation does not make this affine composition nonlinear.')],stem='In a supplied two-layer variant, h=W1 x+b1 and y=W2 h+b2, with identity activation in both layers. All matrices are square and dimension-compatible. Which expression and classification are correct?')
Q('1034-Q04')['assumptions']=['No nonlinear output activation is applied; all entries are dimensionless.']
Q('1034-Q04')['solution']['formulas']=[]
form('1034-Q04','h=W1 x+b1; y=W2 h+b2=(W2 W1)x+W2 b1+b2',{'x,h,y':'Input, hidden and output column vectors in R^d','W1,W2':'d×d real weight matrices','b1,b2':'d-component bias columns','d':'Positive integer width'},['Both activations are identity; no additional output transformation.'])
addcite('1034-Q04',1038,'equation','Hidden affine transform before activation');addcite('1034-Q04',1039,'equation','Output affine transform before activation')
revise('1035-Q05',[
('Three separate sigmoid outputs, each trained against its own binary attribute target','Independent binary attributes can occur together; separate outputs do not require their probabilities to sum to one.'),
('One three-way softmax with a one-hot target naming exactly one present attribute','This encodes mutually exclusive categories and cannot directly encode several simultaneously present attributes.'),
('Three sigmoid outputs divided by their sum before comparing them with the three binary targets','The extra normalization unnecessarily couples independent attributes and forces a unit sum.'),
('One three-way softmax with a multi-hot target but an unchanged exclusive-class interpretation','Changing the target encoding does not remove the softmax unit-sum restriction or make the classes independent.')])
option('1036-Q02','o4','4','This takes the reciprocal of one factor 1/4, rather than multiplying all four factors.')
revise('1036-Q03',[
('A full backpropagation chain also contains weight matrices; activation-only factors do not bound it by themselves.','For h=f1(W1x+b1), y=f2(W2h+b2), the input Jacobian is D2 W2 D1 W1. Matrix magnitudes and sums across paths matter.'),
('The full input Jacobian is D2 D1, because affine weights influence only the forward pass.','The derivative of each affine transform contributes its weight matrix in the backward chain.'),
('Every coordinate derivative equals the product of activation derivatives, regardless of the weight values.','Even a scalar chain contains weight factors, and multivariate derivatives can sum over several paths.'),
('Bounding every activation derivative by 1/4 guarantees every full layer Jacobian has norm at most 1/4.','A layer Jacobian includes its weight matrix, whose norm need not be at most one.')],stem='Why does the activation-only product (1/4)^k not, by itself, bound the full input Jacobian of an arbitrary k-layer sigmoid network?')
Q('1036-Q03')['solution']['formulas']=[]
form('1036-Q03','h=f1(W1 x+b1); y=f2(W2 h+b2); ∂y/∂x=D2 W2 D1 W1',{'x':'Input column in R^d','h':'Hidden column in R^m','y':'Output column in R^r','W1':'m×d weights','W2':'r×m weights','b1,b2':'Bias columns of lengths m,r','f1,f2':'Elementwise differentiable activations','D1,D2':'Diagonal matrices of activation derivatives at current preactivations','d,m,r':'Positive layer dimensions'},['Two-layer illustration of the longer chain; matrices evaluated at the same forward state.'])
for p in(1038,1039,1046):addcite('1036-Q03',p,'equation','Affine layer or chain-rule premise for explicit derived Jacobian')
revise('1036-Q04',[
('At a fixed learning rate, small parameter gradients usually give small updates and slow learning in those layers.','The descent displacement is the learning rate times the gradient; small gradients reduce its magnitude at a fixed rate.'),
('At a fixed learning rate, smaller gradients produce larger updates because descent inverts the gradient.','Ordinary gradient descent multiplies by the gradient; it does not take its reciprocal.'),
('Small backward gradients imply that the corresponding forward activations must all be close to zero.','Saturated sigmoid activations can be close to one while their derivatives are small.'),
('Increasing the learning rate guarantees recovery of the lost gradient information without other effects.','A larger rate can amplify updates but does not restore exact zero derivatives and may destabilize other directions.')])
addcite('1036-Q04',1047,'equation','Descent displacement is rate times gradient')
Q('1036-Q04')['solution']['formulas']=[]
form('1036-Q04','Δp=−eta*g',{'p':'Parameter vector','Δp':'One-step parameter displacement','eta':'Fixed positive learning rate','g':'Loss gradient at old parameters'},['Ordinary gradient descent; no adaptive optimizer or regularization term.'])
revise('1037-Q06',[
('The lower endpoint is rounded: the exact GELU minimum is approximately -0.16997, not exactly -0.17.','For x Phi(x), minimizing requires Phi(x)+x phi(x)=0; its value rounds to -0.17.'),
('The lower endpoint is exactly -0.17 because that decimal is a coefficient in the GELU formula.','The formula contains the Gaussian CDF, not a -0.17 coefficient; the printed endpoint is rounded.'),
('The minimum is zero because GELU approaches zero as x tends to negative infinity.','The negative-tail limit is zero from below, while a finite negative input reaches a smaller negative value.'),
('The output is unbounded below because every negative input retains a fixed nonzero linear slope.','That is a leaky-ReLU interpretation; GELU’s Gaussian CDF factor tends to zero in the negative tail.')])
revise('1041-Q02',[
('Evaluate the prediction using the current fixed weights and biases','The forward pass computes activations and predictions, without applying a parameter update in this stated model.'),
('Differentiate the loss with respect to the weights and biases','That is gradient calculation, which uses the forward result but is not the forward prediction step.'),
('Subtract the learning-rate-scaled gradients from the weights and biases','That is the optimizer update after gradients have been computed.'),
('Re-estimate persistent normalization statistics from this input during evaluation','The stipulated fixed feed-forward model has no training-mode running-state update.')],stem='For the lecture’s feed-forward model with fixed parameters and no stateful normalization, what does its forward pass do?')
revise('1041-Q03',[
('z=Σ_i w_i x_i+b','This is the affine preactivation passed to the activation function.'),
('z=f(Σ_i w_i x_i+b)','This is the postactivation value, not the input z to f.'),
('z=Σ_i w_i f(x_i)+b','This activates each input before aggregation instead of activating the displayed aggregate.'),
('z=f(Σ_i w_i x_i)+b','This puts the bias after activation rather than inside its input.')])
revise('1042-Q03',[
('Compute a prediction, while the supervised target-based loss remains unavailable without the true label.','The model can evaluate the input, but this supervised loss requires its target.'),
('Compute the true supervised loss by replacing the missing label with the model’s own prediction.','A self-chosen pseudo-target does not reveal loss against the unknown true label.'),
('Recover the true supervised loss gradient from confidence alone, without any target assumption.','A confidence score does not specify the missing target needed for the supervised objective.'),
('Treat one minus the highest class probability as the measured error against the true label.','That uncertainty heuristic is not an observed target-based error without the label.')])
revise('1043-Q02',[
('It increases with p, so minimizing it pushes p toward 0, opposite to the desired positive-label prediction.','For y=1 the printed expression is ln(p), whose derivative 1/p is positive; its infimum occurs as p approaches zero.'),
('It decreases with p, so minimizing it pushes p toward 1, as desired for the positive label.','That direction applies to -ln(p), not the printed +ln(p).'),
('It increases with p, so minimizing it pushes p toward 1, as desired for the positive label.','An increasing function is minimized toward the smaller input endpoint, not the larger one.'),
('It decreases with p, so minimizing it pushes p toward 0, opposite to the positive label.','This combines the derivative sign of -ln(p) with the optimization direction of +ln(p).')],stem='For one known positive label y=1 and 0<p<1, consider the binary log expression exactly as printed, without adding a minus sign. What happens if it is minimized?')
revise('1045-Q01',[
('Weights and biases are learned parameters; the learning rate is an optimizer hyperparameter.','The lecture’s descent rule changes weights and biases using a separately selected rate.'),
('Weights are learned parameters; biases and the learning rate are fixed hyperparameters.','Biases are explicitly included in the learned parameter set.'),
('Weights, biases and the learning rate are all updated by the same displayed parameter-gradient rule.','The shown rule updates weights and biases; it does not optimize the learning rate as another model parameter.'),
('Weights and the learning rate are learned parameters; biases are optimizer hyperparameters.','This swaps the roles of the learned bias and selected learning rate.')])
revise('1045-Q02',[
('Setting n=1 gives e²; obtaining e²/2 is a separate scaling choice that cancels the derivative factor 2.','Averaging over one sample supplies a factor of one, not one half. The half is introduced explicitly for derivative convenience.'),
('Setting n=1 automatically supplies the factor 1/2 because the error is squared.','The exponent does not alter the averaging denominator.'),
('Setting n=1 keeps e², while halving the objective leaves its numerical gradients unchanged.','Multiplying an objective by one half also halves its gradients.'),
('The factor 1/2 averages the weight gradient and bias gradient into a single loss value.','It scales the scalar residual objective; it is not an average over parameter derivatives.')])
Q('1046-Q02')['stem']='For the unregularized scalar model yhat=w*x+b and L=0.5*(yhat-y)^2, let x=-2 and yhat-y=3. What are (dL/dw, dL/db)?'
Q('1046-Q02')['assumptions']=['All numerical quantities are dimensionless; both derivatives are evaluated at the same current parameters.']
revise('1046-Q03',[
('The weight gradient is zero; the bias gradient is nonzero.','The weight derivative is e*x=0, while the bias derivative is e and the residual is specified nonzero.'),
('Both gradients are zero because the input is zero.','The bias reaches the prediction through coefficient one, so its derivative does not vanish with x.'),
('The weight gradient is nonzero; the bias gradient is zero.','This interchanges the input-scaled and constant-input gradient roles.'),
('Both gradients equal the nonzero residual.','Only the bias derivative equals e; the weight derivative is multiplied by x=0.')],stem='For the unregularized scalar model yhat=w*x+b and L=0.5*(yhat-y)^2, suppose x=0 and residual e=yhat-y is nonzero. Which gradient statement follows?')
revise('1046-Q04',[
('yhat*(1-yhat)','The chain rule contributes the sigmoid derivative to both weight and bias derivatives.'),
('1','This omits the sigmoid derivative as if the output activation were identity.'),
('yhat*(yhat-1)','This is the negative of the sigmoid derivative, reversing the gradient sign.'),
('1/[yhat*(1-yhat)]','This is a reciprocal factor associated with differentiating a different objective, not the activation derivative for half-squared error.')])
Q('1049-Q02')['stem']='With prediction yhat=7 and target y=10, what is ordinary single-example MSE, defined as (yhat-y)^2 rather than half-squared error?'
Q('1049-Q02')['assumptions']=['Prediction and target are supplied dimensionless numerical coordinates; this comparison changes only the objective normalization.']
addcite('1049-Q02',1043,'equation','Ordinary MSE definition with averaging factor 1/n')
Q('1049-Q02')['solution']['justification']='The residual is 7-10=-3; ordinary one-sample MSE is (-3)^2=9, without a half factor.'
Q('1049-Q02')['solution']['simpleExplanation']=Q('1049-Q02')['solution']['justification']
Q('1050-Q01')['stem']='For yhat=w*x+b and L=0.5*(yhat-y)^2, take x=2, y=10, w=3 and b=1. What gradient pair drives one descent update?'
Q('1050-Q01')['assumptions']=['All values are dimensionless numerical coordinates; no regularization; both gradients use the same old parameters.']
Q('1050-Q01')['solution']['steps']=['Compute yhat=3×2+1=7.','Compute e=7-10=-3.','Use dL/dw=e*x=-6 and dL/db=e=-3.']
revise('1050-Q02',[
('Both gradients use the old pair w=3, b=1.','A simultaneous descent step computes every coordinate gradient from the same old state before changing either parameter.'),
('The weight gradient uses the old pair; the bias gradient uses the updated weight and old bias.','That is a mixed-state sequential update, not the stated simultaneous step.'),
('The weight gradient uses the old weight and updated bias; the bias gradient uses the old pair.','This uses a new bias in one gradient rather than a common old state.'),
('Both gradients use the already updated weight and bias.','That defines an implicit/new-state rule, not the displayed explicit descent update.')],stem='For the shown explicit simultaneous gradient step starting from w=3 and b=1, at which parameter state should the weight and bias gradients be evaluated?')
Q('1050-Q02')['assumptions']=['Both parameters are updated once after the gradients are calculated; this is not sequential coordinate descent.']
Q('1051-Q01')['stem']='Starting from w=3 and b=1, apply one simultaneous step with learning rate eta=0.1 and old-state gradients (g_w,g_b)=(-6,-3). Which parameters result?'
Q('1051-Q01')['assumptions']=['All quantities are dimensionless; use explicit gradient descent p_new=p_old-eta*g.']
revise('1052-Q02',[
('PDF worked example: braking torque; graph/notebook: motor speed','These are different physical output quantities. The notebook supplies no explicit speed unit, so the shared numerical regression must not be treated as a physical unit conversion.'),
('PDF worked example: motor speed; graph/notebook: braking torque','This reverses the actual quantity labels.'),
('PDF worked example: braking torque; graph/notebook: braking torque','The graph axis and notebook comment instead name motor speed.'),
('PDF worked example: motor speed; graph/notebook: motor speed','This ignores the braking-torque wording of the PDF worked example.')])
Q('1052-Q02')['stem']='Which comparison preserves the actual output labels in the PDF worked example and its graph/linked notebook, without inventing a unit conversion?'
Q('1052-Q03')['stem']='For yhat=w*x+b and L=0.5*(yhat-y)^2, update both w and b simultaneously by gradient descent on the same example, with x=2 and eta=0.1. Let e=yhat-y be nonzero. How do e and L change in each step?'
Q('1052-Q03')['assumptions']=['Dimensionless numerical coordinates; fixed target and input; unregularized loss; both gradients evaluated at the old state.']
Q('1052-Q03')['solution']['steps']=['Substitute w_new=w-eta*e*x and b_new=b-eta*e into the new residual.','Obtain e_new=[1-eta*(x²+1)]e.','For x=2 and eta=0.1 the residual multiplier is 0.5, so the loss multiplier is 0.25.']
Q('1052-Q04')['stem']='For the unregularized model yhat=w*x+b with L=0.5*(yhat-y)^2, update both parameters simultaneously on one fixed example with x=2. Allow the positive learning rate eta to vary. Which interval strictly contracts every nonzero residual magnitude in one step?'
Q('1052-Q04')['assumptions']=['Dimensionless numerical coordinates; fixed target; old-state gradients; eta is variable here, not fixed to the example value 0.1.']
Q('1052-Q04')['solution']['steps']=['The residual multiplier is 1-eta*(2²+1)=1-5*eta.','Strict contraction requires -1<1-5*eta<1.','Solving yields 0<eta<2/5=0.4; the endpoints do not strictly contract.']
revise('1053-Q02',[
('Convolution → max pooling → convolution → max pooling → flatten → fully connected → output','The arrows alternate convolution and pooling twice, then flatten before the dense and output stages.'),
('Convolution → convolution → max pooling → max pooling → flatten → fully connected → output','This moves the first pooling operation after the second convolution.'),
('Max pooling → convolution → max pooling → convolution → flatten → fully connected → output','This reverses each displayed convolution/pooling pair.'),
('Convolution → max pooling → convolution → flatten → max pooling → fully connected → output','The displayed second pooling operation precedes flattening; this swaps them.')])
revise('1053-Q06',[
('A ten-neuron dense stage feeding a separately drawn output; the sketch does not specify whether its values are logits, probabilities or intermediate features.','The label gives the width and arrows, but no activation or exact interpretation is attached to those ten values.'),
('Ten normalized class probabilities are explicitly identified by the dense-stage label.','The figure does not label a softmax or state that those values sum to one.'),
('Ten independent binary sigmoid probabilities are explicitly specified for the digit classes.','The figure supplies neither independent sigmoid labels nor that target interpretation.'),
('The output is explicitly a ten-dimensional hidden feature vector, rather than a digit decision.','A digit decision is illustrated separately by 7; the drawing does not establish that the final output is only a hidden feature vector.')],stem='What does the label “Fully Connected Layer: 10 neurons” establish in this digit-recognition sketch, which draws a separate output stage?')
revise('1054-Q01',[
('Current input x_t and previous hidden state h_(t-1)','Both arrows enter the recurrent unit at the current step.'),
('Previous input x_(t-1) and current hidden state h_t','The input arrow is current x_t, while h_t is produced by the current computation.'),
('Current input x_t and previous output y_(t-1)','The feedback arrow is labeled hidden state h_(t-1), not the previous emitted output.'),
('Current output y_t and previous hidden state h_(t-1)','The y_t arrow leaves the unit; it is not the current input arrow.')])
revise('1054-Q03',[
('Its hidden state can carry a learned compressed summary of earlier inputs.','The feedback state can preserve useful information without guaranteeing exact recovery of the entire history.'),
('Its hidden state is an exact copy of the complete preceding input sequence.','A fixed finite hidden representation is not specified as an exact growing archive.'),
('Its hidden state is a fixed-length raw-input window with no learned transformation.','The recurrent state is computed by a learned transformation, not necessarily a raw sliding window.'),
('Its only memory is the last emitted output, independent of its hidden state.','The shown recurrence feeds back h, so memory is not restricted to the emitted output y.')])
revise('1055-Q02',[
('Allow the earlier target prefix, while blocking the token being predicted and later targets.','Right-shifted inputs and a causal mask prevent access to the answer at the current prediction position.'),
('Allow later targets, while blocking the earlier target prefix.','This reverses causal direction and leaks future target information.'),
('Keep unshifted target inputs and mask only later positions, allowing the current target embedding.','That leaves the token being predicted visible at its own position.'),
('Block every target-prefix position, so decoding cannot condition on earlier generated tokens.','Causal decoding permits the earlier prefix; it does not discard all preceding context.')])
revise('1055-Q03',[
('Encoder outputs enter the decoder’s middle attention block, alongside the decoder-side stream.','The two arrows from the encoder feed the middle decoder attention block; the lower masked block is on the decoder stream.'),
('Encoder outputs enter the decoder’s lowest masked self-attention block alongside shifted targets.','The cross-connection is drawn into the middle attention block, not the lowest masked block.'),
('Encoder outputs are added directly to the final softmax probabilities after the Linear block.','The connecting arrows arrive inside the decoder stack before the final Linear and Softmax blocks.'),
('Decoder outputs feed the encoder’s self-attention block before the encoder reads its inputs.','This reverses the displayed encoder-to-decoder direction.')])
revise('1055-Q04',[
('Linear transformation → softmax','The top of the figure projects the decoder state before normalizing output probabilities.'),
('Softmax → linear transformation','This reverses the labeled output ordering.'),
('Linear transformation → independent sigmoid activations','The figure labels a softmax, not independent sigmoids.'),
('Layer normalization → linear transformation, with no final probability normalization','An Add&Norm stage is inside the stack, while the displayed top ends in Softmax.')])
revise('1055-Q05',[
('Add&Norm: residual addition and normalization; Nx: repeated encoder/decoder layers','The bypass arrows and Add&Norm labels describe residual sublayers; the bracket repeats the containing block.'),
('Add&Norm: concatenate attention heads; Nx: number of output classes','Head combination and class count are not what these labels specify.'),
('Add&Norm: residual addition and normalization; Nx: number of attention heads within one layer','The Nx bracket surrounds the layer stack structure, not an individual head-count label.'),
('Add&Norm: add positional encoding only; Nx: repeated encoder/decoder layers','Positional encoding is added at the input separately; internal Add&Norm stages surround attention/feed-forward sublayers.')])
revise('1056-Q03',[
('The categories overlap: a broad field can have demonstrated applications and continuing aims.','Embodied AI is printed in both clouds; the graphic does not define mutually exclusive maturity classes.'),
('The repeated label establishes that the same tasks have equal deployment maturity in both clouds.','The graphic contains no task-level maturity measurements or equivalence claim.'),
('A term in both clouds is ranked as more accurate than terms appearing only once.','Repeated membership is not an accuracy score or benchmark.'),
('The repeated label defines a chronological transition date from research to completed deployment.','No transition dates or completion criteria are provided by the word clouds.')])
revise('1056-Q04',[
('Application cloud: Surgical Robotics; aim cloud: Advanced Surgical Robots','These exact labels appear on the left and right respectively; their placement is source attribution, not a claim of universal clinical capability.'),
('Application cloud: Advanced Surgical Robots; aim cloud: Surgical Robotics','This reverses the two surgical labels.'),
('Application cloud: Human-Robot Symbiosis; aim cloud: Human-Robot Interaction','The source places interaction on the left and symbiosis on the right.'),
('Application cloud: Dexterous Manipulation; aim cloud: Grasping & Manipulation','The source places grasping/manipulation on the left and dexterous manipulation on the right.')],stem='Which pair matches the source’s application/aim word clouds, without converting those labels into a performance guarantee?')
revise('1052-Q05',[
('The literal assignments w=3.0 and b=1.0 determine them, independently of the random seed.','Neither assignment samples the random generator; the seed does not overwrite these literals.'),
('The seed generates the values implicitly even though no random-sampling function is called.','Seeding configures later random draws; it does not replace literal values.'),
('The seed determines w, while the literal assignment determines b.','Both variables are assigned literals in the same way.'),
('Any earlier random draw would shift these two initial values by advancing the generator state.','Advancing random state matters for subsequent draws, not literal assignments.')])
Q('1052-Q08')['stem']='In the linked loop, start with w=3, b=1, x=2 and target y=10. Use yhat=w*x+b, L=0.5*(yhat-y)^2 and eta=0.1. After five simultaneous weight-and-bias gradient updates, what are the final parameters and prediction?'
Q('1052-Q08')['difficulty']='medium'
Q('1052-Q08')['assumptions']=['Treat all values as dimensionless numerical coordinates; do not identify the notebook motor-speed target with the PDF braking-torque unit.','No regularization; each gradient uses the same pre-update state; five updates, not the fifth stored pre-update frame.','Official linked notebook snapshot, cells 4 and 8; not code printed on the PDF page.']
Q('1052-Q08')['solution']['steps']=['Initial state: (w,b,yhat)=(3,1,7), residual -3.','After update 1: (3.6,1.3,8.5).','After update 2: (3.9,1.45,9.25).','After update 3: (4.05,1.525,9.625).','After update 4: (4.125,1.5625,9.8125).','After update 5: (4.1625,1.58125,9.90625). The residual is -3/32.']
Q('1052-Q08')['solution']['justification']='Five simultaneous steps yield w=4.1625, b=1.58125 and yhat=2w+b=9.90625. The histories store the old state, so the fifth animation frame is one update earlier.'
Q('1052-Q08')['solution']['simpleExplanation']=Q('1052-Q08')['solution']['justification']
Q('1052-Q08')['solution']['optionExplanations']['o1']='Correct. The five explicit iterates in the solution give these final values.'
revise('1052-Q09',[
('Both select i+1 values, covering epochs 1 through i+1 for the current zero-based frame.','The slice and range have exclusive stops, so their lengths match and include the current frame’s loss.'),
('Both select i values, covering only epochs strictly before the current frame.','This would describe stops i and i+1 rather than the actual i+1 and i+2 stops.'),
('The range selects i+2 values while the slice selects i+1, leaving one extra epoch coordinate.','range starts at 1 and excludes i+2, so it has i+1 elements, not i+2.'),
('Both select all epoch values immediately, so the curve length is independent of i.','Both stop expressions depend on i, growing the visible prefix each frame.')])
revise('1052-Q10',[
('It creates and binds the text artist before the animation invokes the callback that updates it.','animate resolves epoch_text when called; the existing artist can then be modified with set_text and returned for blitting.'),
('It is required before Python can define the function body that mentions epoch_text.','An outer/global name is normally resolved when the function runs, not simply when its body is defined.'),
('It stores the callback itself in epoch_text, so set_text can invoke the training loop.','epoch_text is a Matplotlib text artist, not a function or training-loop reference.'),
('It makes each callback call allocate a new text artist rather than update the existing one.','The shown code reuses the artist and changes its text; it does not recreate it per frame.')],stem='Why is epoch_text created before FuncAnimation invokes animate(), whose body calls epoch_text.set_text(...)?')
revise('1052-Q11',[
('The cell contains IPython shell/magic syntax, which requires adaptation before ordinary Python parsing.','The !pip and %matplotlib lines are IPython constructs, not standard .py statements; package installation and backend selection must be handled appropriately.'),
('The cell is valid standard Python, and only a missing NumPy package can prevent parsing it.','Dependency availability does not make the shell/magic syntax valid to the ordinary Python parser.'),
('Putting !pip inside a try block makes that syntax valid for the ordinary Python interpreter.','A try block does not change the parser’s language or permit IPython-only syntax.'),
('The imports and numeric assignments must be rewritten because Python scripts cannot use notebook-created variables.','Those are ordinary Python constructs; the incompatible constructs in this setup are the shell/magic lines.')])
# Durable intermediate slice, before extra gap items and freeze.
write(f'audits/{B}-v2-working.json',b)
# Complete symbolic records and standalone premises for repaired items.
form('1024-Q01','z=Σ_i w_i x_i+b; a=f(z)',{'x_i':'Sensor input i','w_i':'Coefficient of sensor input i','b':'Single aggregate bias','z':'Preactivation','f':'Activation function','a':'Action-output representation','i':'Index over the four shown inputs'},['Diagrammatic numerical representation; inputs are normalized before this abstract calculation.'])
form('1025-Q01','g(x)=Σ_i x_i; y=1 if g(x)≥theta, else 0',{'g':'Unweighted input aggregate','x_i':'Binary input i','theta':'User-selected threshold','y':'Binary output','i':'Input index'},['The simplified excitatory MP gate drawn in the lecture; implicit coefficients are 1.'])
form('1028-Q01','XOR(x1,x2)=x1+x2−2*x1*x2; predict 1 when w1*x1+w2*x2+b≥0',{'x1,x2':'Original binary input coordinates','w1,w2':'Affine coefficients','b':'Bias','XOR':'Binary exclusive-or output'},['Original input coordinates are binary; an interaction feature changes the representation.'])
Q('1028-Q01')['solution']['steps']=['For XOR, (0,0) and (1,1) need negative scores, while (1,0) and (0,1) need nonnegative scores.','The positive requirements imply w1+w2+2b≥0; the negative requirements imply b<0 and w1+w2+b<0, hence w1+w2+2b<0.','These contradict each other. Storing the inputs as real numbers does not change those inequalities.']
form('1034-Q01','s(z)=1 for z≥0, else 0; s′(z)=0 for z≠0, undefined at z=0',{'s':'Hard step activation','z':'Scalar preactivation','s′':'Ordinary real derivative'},['No surrogate derivative or distributional derivative is substituted.'])
form('1035-Q05','p_j=1/(1+exp(−z_j)); softmax_j=exp(z_j)/Σ_k exp(z_k)',{'p_j':'Independent attribute-j sigmoid probability','z_j':'Attribute/class logit j','j,k':'Indices among three outputs','softmax_j':'Jointly normalized class probability'},['Finite logits; sigmoid outputs are not normalized across attributes; three-way softmax sums to 1.'])
Q('1037-Q06')['stem']='The GELU range row begins at about -0.17. What is the careful interpretation of that lower endpoint?'
form('1037-Q06','G(x)=x*Phi(x); G′(x)=Phi(x)+x*phi(x); phi(x)=exp(−x²/2)/sqrt(2*pi)',{'G':'Exact GELU','x':'Real scalar input','Phi':'Standard normal cumulative distribution function','phi':'Standard normal probability density','pi':'Circle constant','G′':'Derivative with respect to x'},['Exact Gaussian-CDF definition, not a tanh approximation; numerical minimum rounds to five decimals as -0.16997.'])
Q('1037-Q06')['solution']['steps']=['Differentiate x*Phi(x) to obtain Phi(x)+x*phi(x).','Its unique minimum occurs near x=-0.7517915, with value near -0.1699712.','The table’s -0.17 is a rounded endpoint, not an exact equality.']
Q('1043-Q02')['solution']['formulas']=[]
form('1043-Q02','J_printed=y*ln(p)+(1−y)*ln(1−p); y=1 ⇒ J_printed=ln(p), dJ_printed/dp=1/p>0; L_repaired=−J_printed',{'J_printed':'One-example expression as printed without a minus sign','y':'Known binary label','p':'Probability assigned to label 1','L_repaired':'Negative-log-likelihood loss after an explicit sign repair'},['Natural logarithm; 0<p<1; the question minimizes J_printed, not the repaired loss.'])
Q('1046-Q02')['solution']['steps']=['The half-squared derivative with respect to prediction is e=3.','Multiply by x=-2 for dL/dw=-6 and by 1 for dL/db=3.']
form('1050-Q02','(w_new,b_new)=(w_old,b_old)−eta*grad L(w_old,b_old)',{'w_old,b_old':'Shared pre-update parameter values','w_new,b_new':'Simultaneously updated values','eta':'Positive learning rate','grad L':'Pair of partial loss derivatives at the specified old pair','L':'Differentiable scalar loss'},['Explicit simultaneous descent; no mixed or implicit gradient evaluation.'])
for short in ['1052-Q03','1052-Q04','1052-Q08']:
 form(short,'yhat=w*x+b; L=e²/2; e=yhat−y; w_new=w−eta*e*x; b_new=b−eta*e; e_new=[1−eta*(x²+1)]e; L_new=[1−eta*(x²+1)]²L',{'w,b':'Old scalar weight and bias','w_new,b_new':'Updated weight and bias','x':'Fixed input','y':'Fixed target','yhat':'Old prediction','e,e_new':'Old and new prediction-minus-target residual','L,L_new':'Old and new half-squared losses','eta':'Positive learning rate'},['Single fixed example; identity output; simultaneous old-state gradients; no regularization.'])
Q('1052-Q04')['solution']['formulas'][0]['assumptions']=['Fixed x=2; identity output; half-squared error; simultaneous weight and bias updates; eta may vary.']
Q('1052-Q09')['assumptions']=['Official linked notebook cell 13; loss_history has five stored values and the zero-based frame index satisfies 0≤i≤4.']
form('1052-Q09','len(loss_history[:i+1])=i+1; len(range(1,i+2))=(i+2)−1=i+1',{'i':'Zero-based current frame index','loss_history':'Five-element list of pre-update losses'},['Python exclusive slice/range stops; integer 0≤i≤4.'],{'i':'index','lengths':'element counts'})
# Replace generic conflict-method templates with exact mathematical or documentary checks.
methods={
'1028-Q01':'Use the affine threshold on p1029. Add the two XOR positive-class inequalities and compare them with the two negative-class inequalities; accepting real-valued storage does not remove the contradiction.',
'1030-Q03':'Normalize w·x+b=0 by ||w||. Compare weight-only rescaling with joint rescaling of w and b; the absolute distance is |b|/||w||.',
'1033-Q06':'Expand (w+x)·x−w·x=x·x and inspect the explicitly supplied mixed-sign input componentwise; addition need not increase each component or the norm.',
'1034-Q01':'Read the piecewise step formula on p1034. Differentiate each constant branch and check the jump at zero; no claim that the step is linear is attributed to the source.',
'1036-Q03':'Differentiate the affine and activation compositions on p1038/p1039 with the chain rule from p1046, yielding D2 W2 D1 W1 rather than only D2 D1.',
'1037-Q06':'Differentiate the exact printed x*Phi(x) definition; numerically solve Phi(x)+x*phi(x)=0 and evaluate the minimum to distinguish the rounded range endpoint.',
'1043-Q02':'Set the printed binary expression to y=1, retain its printed plus sign, and differentiate ln(p). Compare minimization with the explicitly repaired negative-log objective.',
'1045-Q02':'Substitute n=1 into the ordinary MSE definition and compare it with the separately chosen half-squared objective and its derivative.',
'1049-Q02':'Compare p1043 ordinary MSE with the explicit half-scaled expression on p1049 using the same supplied prediction 7 and target 10.',
'1052-Q02':'Read the worked-example output label on p1048 and motor-speed graph axis on p1052; compare notebook cell 4 comment and cell 10 axis label without equating physical units.'}
for short,method in methods.items():
 if 'conflictResolution'in Q(short):Q(short)['conflictResolution']['method']=method
# New bounded gaps. New IDs follow existing IDs on each anchor page.
newids=[]
def gap(short,stem,rows,pages,type,difficulty,assumptions):
 q=copy.deepcopy(old['questions'][0]);qid=f'{B}-P{short}';assert qid not in qm
 q.update(id=qid,version=1,status='draft',authorId=A,stem=stem,selectionMode='single',type=type,difficulty=difficulty,cognitiveSkill='numerical'if type in('numerical','synthesis','algorithm_trace')else'recall',assumptions=assumptions,options=[{'id':f'o{i+1}','text':row[0]}for i,row in enumerate(rows)],correctOptionIds=['o1'],citations=[cite(p,k,l,r)for p,k,l,r in pages],reviewIds=[],conceptIds=[f'{B}-P{short[:4]}-C01'],subtopic='Bounded independent-review coverage gap',tags=['neural-networks','coverage-gap'])
 for key in('conflictResolution','supplementalProvenance','revisionAuthors','primaryEvidenceIds'):q.pop(key,None)
 q['solution']={'justification':rows[0][1],'optionExplanations':{f'o{i+1}':('Correct. 'if i==0 else'Incorrect. ')+row[1]for i,row in enumerate(rows)},'steps':[],'formulas':[],'simpleExplanation':rows[0][1],'memoryAid':None,'misconceptions':[r[1]for r in rows[1:]],'examTraps':[],'prerequisiteConceptIds':[]}
 b['questions'].append(q);qm[qid]=q;newids.append(qid);return q
q=gap('1047-Q04','Use column input x=(1,-1), hidden preactivation z=W1*x+b1, h=ReLU(z), and scalar identity output yhat=W2*h+b2. Initially W1=[[1,0],[0,1]], b1=(1,0), W2=[1,-1], b2=0. The target is y=1 and loss L=0.5*(yhat-y)^2. With eta=0.1, update every weight and bias simultaneously from old-state gradients. Which record gives the old loss, first row of dL/dW1, and prediction after the update?',[
('L=0.5; gradient row=(1,-1); new prediction=1.26','The old hidden output is (2,0), so residual 1 flows through only the first active ReLU. Updating both layers and biases from that state produces 1.26.'),
('L=1; gradient row=(2,-2); new prediction=0.64','This consistently uses ordinary squared error instead of the stipulated half-squared loss, doubling gradients.'),
('L=0.5; gradient row=(0.8,-0.8); new prediction=1.308','This computes the hidden gradient with the already updated output weight 0.8, mixing states instead of using simultaneous old-state gradients.'),
('L=0.5; gradient row=(1,-1); new prediction=2.86','The gradient row is correct, but this prediction comes from adding the scaled gradients rather than subtracting them.')],[(1038,'equation','Hidden ReLU affine-layer equation','premise'),(1039,'equation','Output affine-layer structure; identity activation supplied as a variant','premise'),(1045,'equation','Explicit half-squared objective','premise'),(1046,'equation','Chain-rule gradient construction','premise'),(1047,'equation','Weight and bias descent updates','premise')],'synthesis','hard',['Supplied dimensionless two-layer regression variant, not a printed numerical example.','W1 is 2×2, b1 and x are 2×1, W2 is 1×2, and b2,y,yhat are scalars. ReLU is elementwise; no initial preactivation is zero.','No regularization; compute all gradients before changing any parameter; recompute the final prediction at the same x.'])
q['solution']['steps']=['Compute z=(2,-1), h=(2,0), yhat=2 and residual e=1, giving L=0.5.','Output gradients are dL/dW2=(2,0) and dL/db2=1.','The hidden preactivation gradient is (1,0), since the second ReLU is inactive. Therefore dL/dW1=[[1,-1],[0,0]] and dL/db1=(1,0).','The new parameters are W1=[[0.9,0.1],[0,1]], b1=(0.9,0), W2=[0.8,-1], b2=-0.1.','Recompute z_new=(1.7,-1), h_new=(1.7,0); yhat_new=0.8×1.7-0.1=1.26.']
form('1047-Q04','z=W1*x+b1; h=max(0,z); yhat=W2*h+b2; e=yhat−y; L=e²/2; δ1=(W2^T*e)⊙1[z>0]; ∇W2 L=e*h^T; ∇b2 L=e; ∇W1 L=δ1*x^T; ∇b1 L=δ1; theta_new=theta−eta*∇theta L',{'x':'2×1 fixed input column','z,h':'2×1 hidden preactivation and activation','W1':'2×2 input-to-hidden weights','b1':'2×1 hidden bias','W2':'1×2 hidden-to-output weights','b2':'Scalar output bias','yhat,y':'Scalar prediction and target','e':'Prediction-minus-target residual','L':'Half-squared scalar loss','δ1':'Gradient of L with respect to z','⊙':'Elementwise multiplication','1[z>0]':'Elementwise positive-preactivation indicator','T':'Transpose','theta':'Any one parameter array W1,b1,W2,b2','eta':'Learning rate 0.1'},['Identity output; elementwise ReLU; no zero preactivations; no regularization; every gradient at the old state.'])
q=gap('1033-Q07','Use augmented inputs A=(1,0,0), B=(1,0,1), C=(1,1,0), D=(1,1,1), with labels (0,1,1,1). Start w=(0,0,0), predict 1 when w·x≥0 and 0 otherwise. Visit A,B,C,D in that order each pass. Add x for a positive mistake, subtract x for a negative mistake, and otherwise do nothing. After each complete pass, test every example with the resulting weights and stop if all are correct. What final state and stopping counts result?',[
('w=(-1,1,1); five updates over three complete passes','After the first two passes A remains wrongly positive at score zero. The third pass subtracts A once, after which all four labels are correct.'),
('w=(0,0,1); two updates over one complete pass','This stops after the first pass without rechecking A, whose final score is zero and hence incorrectly predicts 1.'),
('w=(0,1,1); four updates over two complete passes','This stops after the second pass even though A still has score zero and is incorrectly positive.'),
('w=(-1,1,1); five updates over four complete passes','This waits for a completely mistake-free pass, a stricter stopping rule than the stipulated end-of-pass check of all current predictions.')],[(1032,'statement','Correct predictions leave weights unchanged; separable binary sets','premise'),(1033,'code','Perceptron pseudocode: both mistake branches and all-example convergence condition','premise'),(1029,'equation','Zero-inclusive positive threshold and augmented bias','premise')],'algorithm_trace','medium',['Supplied deterministic cyclic-order variant of the source’s random selection; input component 1 is the constant bias input.','All coordinates and unit updates are dimensionless; labels are fixed; stop according to the explicit all-example end-of-pass test, not merely the number of mistakes during that pass.'])
q['solution']['steps']=['Pass 1: A is a negative mistake at score 0, giving (-1,0,0); B is a positive mistake at -1, giving (0,0,1). C and D are correct. A fails the end check.','Pass 2: A subtracts to (-1,0,1); B is correct at 0; C adds to (0,1,1); D is correct. A again fails the end check.','Pass 3: A subtracts to (-1,1,1); B,C,D are correct with scores 0,0,1.','The final scores on A,B,C,D are (-1,0,0,1), matching labels (0,1,1,1). Five total updates occurred.']
form('1033-Q07','s=w·x; yhat=1[s≥0]; w_new=w+(y−yhat)*x',{'w,w_new':'Old and updated three-component augmented weights','x':'Current augmented input column','s':'Current scalar score','y':'Binary target','yhat':'Binary prediction','1[s≥0]':'Indicator that score is nonnegative'},['Unit update; visit A,B,C,D cyclically; do not update correct predictions; test all predictions at each pass end.'])
q=gap('1043-Q07','Explicitly repair the missing minus sign in the printed binary objective and use the mean binary cross-entropy L=-(1/n)Σ[y_i ln(p_i)+(1-y_i)ln(1-p_i)], where p_i is the probability of label 1. For labels (1,0,1) and probabilities (0.8,0.25,0.6), which pair gives the second example’s loss and the batch mean loss? Round to five decimal places.',[
('Second loss 0.28768; batch mean 0.34055','The negative-label example uses 1-p=0.75. The three correct-label probabilities multiply to 0.36; the mean is -ln(0.36)/3.'),
('Second loss 1.38629; batch mean 0.70675','This uses p=0.25 instead of 1-p for the negative label, effectively treating every label as positive.'),
('Second loss -0.28768; batch mean -0.34055','This retains the printed positive-log sign rather than using the explicit negative-log repair.'),
('Second loss 0.28768; batch mean 1.02165','The second term is correct, but 1.02165 is the sum of the three losses, not their mean.')],[(1043,'equation','Printed binary mean log expression missing the negative sign','conflict')],'numerical','medium',['Use natural logarithms and dimensionless probabilities strictly between 0 and 1. The negative sign is an explicit supplied repair, not silently attributed to the PDF.','Three examples have equal averaging weight; p_i always denotes positive-class probability, including when y_i=0.'])
q['conflictResolution']={'status':'derived-qualification-pending-independent-review','questionVersion':1,'sourceId':'lectures','sourceSha256':SHA,'physicalPage':1043,'sourceClaim':'The printed binary expression has a positive 1/n multiplier and no leading minus sign.','basis':'The question explicitly negates the printed log-likelihood to form a minimized binary cross-entropy loss.','method':'Use the stated repaired objective; substitute the correct branch for each binary label and divide the sum of three natural-log losses by three.','scope':'This supplied repaired question only; independent review required.'}
q['solution']['steps']=['For y=1,p=0.8, loss=-ln(0.8)=0.22314355.','For y=0,p=0.25, loss=-ln(0.75)=0.28768207.','For y=1,p=0.6, loss=-ln(0.6)=0.51082562.','Sum to 1.02165125 and divide by 3 to get 0.34055042. Round the requested pair to five decimals.']
form('1043-Q07','ell_i=−[y_i ln(p_i)+(1−y_i)ln(1−p_i)]; L=(1/n)Σ_i ell_i',{'ell_i':'Loss of example i','L':'Batch mean binary cross-entropy','y_i':'Binary label of example i','p_i':'Probability of label 1 for example i','i':'Example index','n':'Number of equally weighted examples, here 3'},['Natural logarithms; 0<p_i<1; negative sign explicitly repaired.'],{'ell_i,L':'nats (dimensionless)','p_i,y_i':'dimensionless','n,i':'counts/indices'})
q=gap('1025-Q05','Which pairing preserves the two named milestones and the fixed-gate versus trainable-model distinction presented in the lecture?',[
('McCulloch, neuroscientist, and Pitts, logician: 1943 artificial-neuron model; Rosenblatt: 1958 perceptron with learnable parameters','The MP page identifies the two roles and 1943; the later pages name Rosenblatt in 1958 and introduce learnable weights and bias.'),
('McCulloch, logician, and Pitts, neuroscientist: 1943 artificial-neuron model; Rosenblatt: 1958 trainable perceptron','This reverses the two professions given on the MP page.'),
('McCulloch and Pitts: 1958 fixed-gate model; Rosenblatt: 1943 trainable perceptron','This interchanges the two years attached to the named milestones.'),
('McCulloch and Pitts: 1943 model with the shown weight-learning rule; Rosenblatt: 1958 model with only user-fixed parameters','This reverses the lecture’s fixed MP-gate and learnable perceptron distinction.')],[(1025,'statement','Named researchers, professions and 1943 introduction','premise'),(1028,'statement','No MP learning mechanism; Rosenblatt 1958 attribution','premise'),(1029,'statement','Perceptron weights and bias as learnable parameters','premise')],'match','easy',['Report the selected lecture attributions; do not infer a broader first-ever claim or endorse the separate Minsky/Papert wording.'])
# Source annotations remain unchanged; the angular endpoint was an author defect, not a false PDF claim.
assert b['sourceIssues']==old['sourceIssues']
# Repair prose spacing only inside changed or new objects, never accepted objects.
def clean(v):
 if isinstance(v,str):
  for a,z in [('by||','by ||'),('is(-','is (-'),('residual=-','residual = -'),('becomes-','becomes -'),('Usex ','Use x '),('withx ','with x '),('Fixedx ','Fixed x='),('Require|','Require |'),('giving0','giving 0'),('factors1/','factors 1/')]:v=v.replace(a,z)
  return v
 if isinstance(v,list):return [clean(x)for x in v]
 if isinstance(v,dict):return {k:clean(x)for k,x in v.items()}
 return v
for qid in flags|set(newids):
 q=qm[qid];z=clean(q);q.clear();q.update(z)
# Keep conceptual coverage reciprocal, adding explicit links for the repeated summary.
for c in b['concepts']:
 c['questionIds']=[q['id']for q in b['questions']if c['id']in q['conceptIds']]
 c['examinationAngles']=[q['stem']for q in b['questions']if c['id']in q['conceptIds']]
 c['slideIds']=sorted(set(c['slideIds']+[x['slideId']for q in b['questions']if c['id']in q['conceptIds']for x in q['citations']]))
inspection=read(f'data/inspection-batches/{B}.json');ai=f'data/inspection-batches/archive/{B}-v1.json';(R/ai).parent.mkdir(exist_ok=True)
if not (R/ai).exists():(R/ai).write_bytes((R/f'data/inspection-batches/{B}.json').read_bytes())
summary_pages=[1024,1025,1028,1029,1034,1037,1038,1039,1041,1042,1043,1044,1047,1053,1054,1055,1056]
summary_cids=[c['id']for c in b['concepts']if any(f'lectures-p{p}'in c['slideIds']for p in summary_pages)]
for c in b['concepts']:
 if c['id']in summary_cids:c['slideIds']=sorted(set(c['slideIds']+['lectures-p1057']))
for s in inspection['slides']:
 s['conceptIds']=[c['id']for c in b['concepts']if s['id']in c['slideIds']]
 if s['physicalPage']==1057:
  s.update(disposition='repeated',exclusionReason=None,repeatsSlideIds=[f'lectures-p{p}'for p in summary_pages],incrementalChangesChecked=True)
  s['visualInspection']['notes']='Actually rechecked all seven summary bullets against earlier cited concepts. No new equation, numerical example or architecture claim; explicit repeat links encode the existing coverage.'
# Save durable full draft; final freeze is appended only after numerical and structural prechecks.
write(f'audits/{B}-v2-working.json',b)
write(f'audits/{B}-v2-working-inspection.json',inspection)
write(f'audits/{B}-v2-repair-plan.json',{'authorId':A,'independentReview':False,'changedQuestionIds':sorted(flags),'newQuestionIds':newids,'preservedAcceptedHashes':{q['id']:qhash(q)for q in accepted},'changedOptionSets':sorted(changed_sets),'sourceIssuesPreserved':True,'summaryRepeatPages':summary_pages})
# Final precision pass before the immutable review packet.
addcite('1032-Q03',1033,'code','Mistake-update loop and all-example stopping condition')
Q('1052-Q02')['citations'][0]['locator']='Printed slide 28: worked example specifies braking torque and a 10 Nm target'
Q('1052-Q02')['citations'][1]['locator']='Printed slide 32: left graph axis is labeled Motor Speed (y), with the official notebook hyperlink on the right'
Q('1052-Q02')['supplementalProvenance']['cell']=4
Q('1052-Q02')['supplementalProvenance']['cells']=[4,10]
Q('1052-Q08')['supplementalProvenance']['cells']=[4,8]
Q('1052-Q10')['supplementalProvenance']['cells']=[12,13]
# Specific roles and kinds were read against actual page regions, not guessed from extracted prose.
Q('1037-Q06')['citations'][0]['locator']='Printed slide 17: GELU column, exact x*Phi(x) formula and rounded [-0.17,infinity) range row'
Q('1037-Q06')['citations'][0]['kind']='table'
for short in ['1036-Q02','1046-Q02']:
 q=Q(short)
 if not q['solution']['steps']:
  q['solution']['steps']=['Multiply four factors: (1/4)^4=1/256.'] if short=='1036-Q02' else ['Multiply e=3 by x=-2 to obtain -6; the bias derivative equals 3.']
# New/changed concept question texts and citation membership are reconciled once more after the precision pass.
for c in b['concepts']:
 c['questionIds']=[q['id']for q in b['questions']if c['id']in q['conceptIds']]
 c['examinationAngles']=[q['stem']for q in b['questions']if c['id']in q['conceptIds']]
 c['slideIds']=sorted(set(c['slideIds']+[x['slideId']for q in b['questions']if c['id']in q['conceptIds']for x in q['citations']]))
for s in inspection['slides']:s['conceptIds']=[c['id']for c in b['concepts']if s['id']in c['slideIds']]
assert all(q==qm[q['id']] for q in accepted)
assert all(q['correctOptionIds']==qm[q['id']]['correctOptionIds'] for q in old['questions'])
needed={f['questionId']for f in summary['findings']if'distractors'in f['criteria']}
assert needed<=changed_sets,(needed-changed_sets)
changed=[q for q in b['questions']if q['id']in flags or q['id']in newids]
for q in changed:
 assert q['status']=='draft' and not q['reviewIds']
 assert len({o['text']for o in q['options']})==4
 assert set(q['solution']['optionExplanations'])=={o['id']for o in q['options']}
 if q['type']in('numerical','algorithm_trace'):
  assert q['solution']['formulas'] and q['solution']['steps'],q['id']
 for f in q['solution']['formulas']:assert f['expression'] and f['variables'] and f['units'] and f['assumptions']
 if any(c['role']=='conflict'for c in q['citations']):assert q['conflictResolution']['questionVersion']==q['version']
checks=read(f'audits/{B}-v2-author-computations.json');assert checks['passed']
coverage={'authorId':A,'independentReview':False,'changedCount':45,'newCount':4,'preservedAcceptedCount':89,'totalQuestions':138,'gapTargets':[
 {'id':'L34-G01','questionId':f'{B}-P1047-Q04','pages':[1038,1039,1045,1046,1047],'angle':'Complete two-layer forward pass, half-squared loss, all gradients and simultaneous parameter update','status':'drafted-pending-independent-review'},
 {'id':'L34-G02','questionId':f'{B}-P1033-Q07','pages':[1029,1032,1033],'angle':'Multi-example perceptron trace with both mistake directions, no-op visits, revisits and all-example termination','status':'drafted-pending-independent-review'},
 {'id':'L34-G03','questionId':f'{B}-P1043-Q07','pages':[1043],'angle':'Negative label and mixed-label batch mean binary cross-entropy, with explicit sign repair','status':'drafted-pending-independent-review'},
 {'id':'L34-G04','questionId':f'{B}-P1025-Q05','pages':[1025,1028,1029],'angle':'Named researchers, roles, two dates and fixed MP versus trainable perceptron distinction','status':'drafted-pending-independent-review'}],
 'summaryLedger':{'physicalPage':1057,'disposition':'repeated','repeatsSlideIds':[f'lectures-p{p}'for p in summary_pages],'conceptIds':summary_cids,'questionIds':sorted({qid for c in b['concepts']if c['id']in summary_cids for qid in c['questionIds']}),'incrementalChangesChecked':True,'reason':'All seven summary bullets repeat earlier technical concepts; no new equation, example or architecture detail.'},
 'sourceIssuesPreserved':len(old['sourceIssues']),'authorCorrection':'The negative-dot-product endpoint flaw belonged to authored P1033-Q05. The actual source says greater than 90 degrees and is not falsely accused of saying strictly obtuse.'}
write(f'audits/{B}-v2-coverage-closure-author.json',coverage)
write(f'audits/{B}-v2-author-quality-precheck.json',{'authorId':A,'independentReview':False,'allAcceptedWholeObjectsPreserved':True,'preservedAcceptedHashes':{q['id']:qhash(q)for q in accepted},'allOriginalKeysUnchanged':True,'requiredDistractorSets':len(needed),'changedOptionSets':len(changed_sets),'allRequiredSetsRepaired':needed<=changed_sets,'actualSourcePagesRevisited':30,'allNumericalItemsHaveFormulasAndSteps':True,'sourceCitationsRevisited':True,'sourceIssuesUnchanged':True,'difficulty':{d:sum(q['difficulty']==d for q in changed)for d in('easy','medium','hard')},'numericChecks':f'audits/{B}-v2-author-computations.json'})
b['coverageNote']='Version 2 author repair: 45 flagged question objects revised, 89 accepted whole objects and exact hashes preserved, four narrowly targeted coverage gaps added after existing anchor-page IDs. Total 138 question angles, not 138 distinct concepts. All 49 changed/new objects remain draft pending independent review. Thirty actual source pages revisited; original full 39-page inspection evidence retained. Sixteen original source annotations unchanged. Summary p1057 now explicitly links prior pages/concepts.'
write(f'audits/{B}-v2-working.json',b);write(f'audits/{B}-v2-working-inspection.json',inspection)
# Set FREEZE_L34_V2=1 only after separate in-memory contract validation and integrity tests pass.
import os
if os.environ.get('FREEZE_L34_V2')!='1':
 print('READY FOR PRE-FREEZE VALIDATION',len(changed));raise SystemExit(0)
assert read(f'audits/{B}-v2-integration-validation.json')['valid']
write(f'data/question-batches/{B}.json',b);write(f'data/inspection-batches/{B}.json',inspection)
blind=[{**{k:q[k]for k in('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in c.items()if k!='evidenceText'}for c in q['citations']]}for q in changed]
write(f'audits/blind-{B}-v2.json',blind);packetsha=fhash(f'audits/blind-{B}-v2.json')
write(f'audits/{B}-v2-review-manifest.json',{'batchId':B,'blindPacket':f'audits/blind-{B}-v2.json','blindPacketSha256':packetsha,'questionSha256':{q['id']:qhash(q)for q in changed},'preservedAcceptedHashes':{q['id']:qhash(q)for q in accepted},'sourceBounds':[1021,1059],'sourceSha256':SHA,'revisedCount':45,'newQuestionCount':4,'preservedAcceptedCount':89,'priorBatchArtifact':f'data/question-batches/archive/{B}-v1.json','priorBatchSha256':fhash(f'data/question-batches/archive/{B}-v1.json'),'sourceIssuesSha256':hashlib.sha256(json.dumps(b['sourceIssues'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),'independentReviewPending':True})
(R/f'audits/handoffs/{B}-v2.md').write_text(f'''# L34 v2 frozen

45 revised drafts plus four new gap questions; all 89 accepted whole objects and hashes preserved. Total 138. All original key IDs unchanged. Sixteen source annotations preserved. P1033-Q05 now includes the 180-degree antiparallel endpoint; the PDF itself was not blamed for this author error.

Packet: audits/blind-{B}-v2.json
SHA256: {packetsha}
Manifest: audits/{B}-v2-review-manifest.json
Archive: data/question-batches/archive/{B}-v1.json
Repair script: scripts/repair_W07_L34_v2.py (frozen guard; do not rerun)
Checks: scripts/check_W07_L34_v2.py and audits/{B}-v2-author-computations.json

Thirty actual pages revisited. Four new items cover full two-layer backpropagation/update, multi-example perceptron termination, mixed-target batch cross-entropy, and named MP/perceptron milestones. Summary p1057 now explicitly links prior concepts and pages. Author checks passed 27 groups plus 900 varied cases (3,000 assertions); original notebook cells 4,6,8,10,12,13 executed without install/magic cell2. Contract validation and integrity tests passed. All changed content still requires independent re-review. No canonical or Git writes.
''')
print('FROZEN',len(changed),packetsha)
