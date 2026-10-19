"""Persist actual full-resolution L33 inspection notes, not extraction claims."""
from pathlib import Path
import json,copy,hashlib
R=Path(__file__).resolve().parents[1]
NOTES={
987:'Title: Lecture 33, Image Feature Extraction. No substantive content.',
988:'Objectives: region, line and point features; dimensionality and robotic use. Roadmap only.',
989:'Contents: region features, line features and point features. Roadmap only.',
990:'Motivation: compact features support localization, grasping and navigation. Raw-pixel impossibility is overbroad; learned systems can learn their own features. Counts are illustrative.',
991:'Camera-to-feature diagram explicitly includes edges, corners, object outline and motion vectors. Feature outputs may be scalars or vectors. Pose and velocity require suitable geometric or temporal context.',
992:'Actual illustrations show near/far cube projection, car occlusion by a tree, lighting changes to a red ball and spurious shadows/reflections. Scene assumptions limit reliability; pixel area alone is not metric object size.',
993:'Actual figures distinguish homogeneous regions, corridor line structure and distinctive point/corner features. Keypoints are not limited to corners.',
994:'Original tourist-information sign versus segmented letters/symbols demonstrates object/background partition; robustness means graceful degradation when assumptions fail, not automatic text recognition.',
995:'Region pipeline: pixel classification, instance segmentation, description. Otsu and local threshold t=mean(W)-k std(W) displayed. Weighted variance matters; this adaptive formula is not every library implementation.',
996:'Read castle as float; t=.7 is overwritten by castle.otsu() before displayed threshold. Source Otsu value .6039 and histogram .603 are rounding. Adaptive h=15 caption says window size 15; API semantics need checking. Adaptive result visibly retains brick texture.',
997:'Cone-response equations, primary mixing matrix, RGB normalization and light/reflectance/eye diagram inspected. Arbitrary luminance scaling must not disappear into unit color-matching functions. Mercury-line attribution for all three primaries requires qualification.',
998:'XYZ uses imaginary primaries; normalized xy has two degrees of freedom. Actual xy versus Lab plots motivate approximate perceptual uniformity, not exact perceptual distances or complete illumination invariance.',
999:'RGB to Lab then a*b* clustering removes lightness from clustering, not all illumination dependence. Green-red and blue-yellow axes, C-class k-means and color-constancy motivation inspected.',
1000:'Four yellow targets but two chromatic clusters. Code uses gamma=sRGB, Lab a*:b* planes, k=2 seed=0. Actual cluster 0 is yellow/high b*, cluster 1 gray/near origin. Color-space centroids are not spatial object centers.',
1001:'Inversion maps yellow class 0 to foreground255 and gray1 to background0; connected labels show four instances, top1/left2/right3/bottom4, background0. Label count return requires API checking. MSER and graph methods only named.',
1002:'Raw spatial moment sum, binary area, centroid and central moments inspected. Nonempty mask and binary versus intensity-weighted interpretation must be declared.',
1003:'Central moment identities, displayed J matrix, eigenvalue semiaxes, aspect ratio, orientation and Hu moments inspected. J is coordinate scatter, not unqualified mechanical inertia; atan loses quadrants; repeated eigenvalues lose unique orientation; Hu scale invariance needs normalized central moments.',
1004:'Blob table and code inspected. Blob3 top centroid365.7040,218.2074 area5609.5 umin331 aspect.7489; index differs from connected label1. Fractional contour area differs from integer pixel count. J3 code references undefined u11/u02. Blue centers, red boxes and green ellipses visible; code explicitly plots only one J3 ellipse.',
1005:'Boundary edgels, direction chain codes, circle circularity4piA/P², square contrast and centroid-radius signature. Chain start and diagonal metric matter. Raw radius sequence needs phase alignment for rotation invariance.',
1006:'Code polar() uses blob0 but caption says blob3. polarmatch(1), radius normalization, perimeter shape/length and blob3 orange outline inspected. Plot x-coordinate is contour sample index, not theta. Normalized curves do not automatically align rotation phase.',
1007:'Street diagram displays detector boxes and labels. Faster R-CNN description conflates box detection with pixel/instance segmentation; standard masks require a mask branch. COCO80 is a trained configuration, not universal architecture property.',
1008:'Original street versus extracted line structure. Lines emphasize geometric boundaries useful in engineered environments without preserving color/texture.',
1009:'Gaussian smoothing, derivative convolution, associativity, gradient magnitude and atan2 direction inspected, including two-branch gradient flow diagram.',
1010:'Canny nonmaximum suppression along gradient direction and high/low hysteresis inspected. Weak chains connected to strong edges can survive; isolated weak responses do not.',
1011:'Hough polar line equation rho=u cos(theta)+v sin(theta), normal-angle diagram and accumulator voting inspected. Theta is normal angle, not line direction; domain controls signed rho.',
1012:'Five points, accumulator curves and Hough code inspected. h.lines(2) comment says minimum3 votes; strict threshold API must be checked before alleging a mismatch. Plot includes negative rho and multiple candidate lines.',
1013:'Church Gaussian(5,5),sigma1.4; Canny50,100; probabilistic Hough100,min length200,max gap5,seed0. Actual images show dense edges then selected long segments. Canny default norm differs from explicit Euclidean theory.',
1014:'Harris A=w*gradient-product matrix, eigenvalue flat/edge/corner cases and C=det(A)-alpha trace(A)^2 inspected. Gradients are filtered image derivatives, not Gaussian kernels alone. Ordinary Harris is not inherently scale invariant.',
1015:'Scale-space volume, Gaussian differences and LoG motivation inspected. 26 neighbors means8 same scale+9 each adjacent scale. DoG approximates proportional scale-normalized LoG, not identical unscaled LoG.',
1016:'SIFT detection, localization, orientation, descriptor pipeline inspected.16x16 patch,4x4 spatial cells,8 descriptor bins means128 dimensions; descriptor bins are not necessarily dominant-orientation assignment bins.',
1017:'Harris nfeat500 and filtered SIFT percentstrength50,minscale5 code inspected. Figures show Harris crosses versus SIFT circles/angle hands. Percentstrength may be relative maximum, not top half count; API check needed.',
1018:'Summary repeats region/line/point roles and overstates joint Harris/SIFT scale invariance; retain explicit qualification rather than universal guarantee.',
1019:'Bibliography only: Szeliski, Corke, Forsyth. Named books have not been claimed read.',
1020:'Thank-you closing page only.'}
EX={987:'Title only.',988:'Objectives roadmap only.',989:'Contents roadmap only.',1019:'Bibliography only.',1020:'Closing page only.'}
if __name__=='__main__':
 maps={s['physicalPage']:s for s in map(json.loads,(R/'sources/page_maps/lectures.jsonl').read_text().splitlines())};slides=[]
 batch=R/'data/question-batches/W07-L33.json';concepts=json.loads(batch.read_text())['concepts'] if batch.exists() else []
 for p,note in NOTES.items():
  s=copy.deepcopy(maps[p]);s.update(disposition='excluded' if p in EX else 'examinable',exclusionReason=EX.get(p),conceptIds=[c['id'] for c in concepts if s['id'] in c['slideIds']],printedSlideNumber=str(p-986),printedSlideNumberStatus='present',printedNumberEvidence='Actual footer inspected in rendered page; retained separately from physical PDF page.')
  s['visualInspection']={'status':'complete','inspectorId':'build_offline_study_interface:L33-author','inspectedAt':'2026-10-19T19:47:25+00:00','method':'rendered_page','notes':note+' Actual 1800×1013 pixels viewed alongside extracted text.','previewSha256':hashlib.sha256((R/s['previewPath']).read_bytes()).hexdigest(),'dimensions':[1800,1013]};slides.append(s)
 (R/'data/inspection-batches/W07-L33.json').write_text(json.dumps({'batchId':'W07-L33','slides':slides},ensure_ascii=False,indent=2)+'\n')
 (R/'audits/W07-L33-page-observations.json').write_text(json.dumps({'sourceId':'lectures','sourceSha256':slides[0]['sourceSha256'],'notes':NOTES,'inspectionComplete':True,'questionAuthoringComplete':False,'independentReviewComplete':False},ensure_ascii=False,indent=2)+'\n')
 print('Persisted',len(slides),'actual page inspections;',len(slides)-len(EX),'substantive pages.')
