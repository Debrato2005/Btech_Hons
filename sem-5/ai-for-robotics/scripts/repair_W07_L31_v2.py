#!/usr/bin/env python3
"""L31 author repairs, not independent verification. Preserve 64 accepted objects."""
import json,copy,hashlib
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1];B='W07-L31';A='L31-author-20261019'
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def qhash(q):return hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def fhash(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
manifest=f'audits/{B}-v2-review-manifest.json'
if (R/manifest).exists():raise SystemExit('L31 v2 is frozen. Do not regenerate over reviewed objects.')
old=read(f'data/question-batches/{B}.json');b=copy.deepcopy(old);qm={q['id']:q for q in b['questions']}
rv=read(f'data/reviews/{B}-v1-independent.json');flags={r['questionId']:r for r in rv if r['decision']=='flagged'}
assert len(flags)==44 and len(old['questions'])==108
accepted=[q for q in old['questions'] if q['id'] not in flags];assert len(accepted)==64
for q in accepted:assert any(r['questionId']==q['id'] and r['decision']=='verified' and r['questionSha256']==qhash(q) for r in rv)
archive=f'data/question-batches/archive/{B}-v1.json'
if (R/archive).exists():assert read(archive)==old
else:(R/archive).write_bytes((R/f'data/question-batches/{B}.json').read_bytes())
sourcehash=fhash(f'audits/source-disputes-{B}.json')
for qid,r in flags.items():
 q=qm[qid];assert q['version']==1 and qhash(q)==r['questionSha256']
 q.update(version=2,status='draft',reviewIds=[]);q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+[A]))
 if 'conflictResolution' in q:q['conflictResolution']['questionVersion']=2
changed_sets=set()
def q(short):return qm[B+'-'+short]
def revise(short,rows,stem=None):
 item=q(short);assert item['id'] in flags and item['correctOptionIds']==['o1'];assert len(rows)==4
 if stem:item['stem']=stem
 values={f'o{i+1}':v for i,v in enumerate(rows)}
 for o in item['options']:o['text']=values[o['id']][0]
 why={k:v[1] for k,v in values.items()}
 item['solution'].update(justification=why['o1'],simpleExplanation=why['o1'],optionExplanations={k:('Correct. ' if k=='o1' else 'Incorrect. ')+v for k,v in why.items()},misconceptions=[why[k] for k in ('o2','o3','o4')]);changed_sets.add(item['id'])
revise('P0926-Q01',[
 ('Camera with eye; interpretation algorithms with brain','The diagram pairs optical sensing with the eye and interpretation of acquired information with the brain.'),
 ('Camera with brain; interpretation algorithms with eye','This reverses the diagram’s sensing and interpretation roles.'),
 ('Camera with eye; interpretation algorithms with retina alone','The intended analogy places interpretation at the brain level, not solely at the retinal sensing stage.'),
 ('Camera with pupil alone; interpretation algorithms with lens','The pupil and lens are optical components; this pairing omits the diagram’s brain-level interpretation role.')])
revise('P0927-Q02',[
 ('The robot’s measured features still need interpretation to obtain semantic object labels','The schematic contrasts human semantic labels with the robot’s uncertain interpretation of image features; it does not establish that recognition is impossible.'),
 ('The robot already has semantic labels and is uncertain only about metric depth','The question marks do not show established object identities with only a depth-estimation problem remaining.'),
 ('The robot’s recognition problem is resolved once the edge map is computed','Computing edges provides features but does not by itself assign the illustrated semantic object labels.'),
 ('The robot’s uncertainty indicates a need to recalibrate the camera rather than interpret features','Calibration can matter in vision, but the diagram motivates semantic interpretation, not a diagnosed calibration failure.')])
revise('P0928-Q01',[
 ('Line labeling: infer 3D structure from drawings; pictorial structures: flexible arrangements of object parts','These are the two roles assigned in the early-scene-understanding column.'),
 ('Line labeling: infer 3D structure from drawings; pictorial structures: recover camera motion across views','The first role matches, but camera-motion recovery is not the stated role of pictorial part structures.'),
 ('Line labeling: assign object-category labels to pixels; pictorial structures: flexible arrangements of object parts','The second role matches, but the line-labeling entry concerns interpreting line drawings for 3D structure rather than semantic pixel labeling.'),
 ('Line labeling: recover camera motion across views; pictorial structures: assign object-category labels to pixels','These are plausible vision tasks, but neither matches the historical technique-to-purpose pair on the slide.')])
revise('P0928-Q03',[
 ('Pyramids/scale-space: multiple resolutions; regularization: smoothness constraints for ill-posed problems','The source assigns multiresolution analysis to pyramids/scale-space and stabilizing smoothness constraints to regularization.'),
 ('Pyramids/scale-space: multiple resolutions; regularization: increasing the weight of the data residual alone','The multiresolution role matches, but the listed regularization role adds smoothness constraints rather than merely emphasizing data fit.'),
 ('Pyramids/scale-space: shape descriptions at one fixed scale; regularization: smoothness constraints for ill-posed problems','The regularization role matches, but a single fixed scale misses the defining multiresolution purpose.'),
 ('Pyramids/scale-space: unordered object-part arrangements; regularization: initializing camera motion between frames','These are plausible modeling or estimation operations, but not the paired purposes given in this column.')])
revise('P0928-Q04',[
 ('Probabilistic models for global optimization','This is the historical diagram’s stated role for Markov Random Fields.'),
 ('Deterministic multiresolution representations of an image','The slide associates multiresolution representations with pyramids and scale-space, not the MRF entry.'),
 ('Independent pixel classifiers with no neighborhood dependencies','An independent-pixel description omits the spatial dependencies characteristic of the MRF model referenced here.'),
 ('Camera-motion estimation from correspondences across views','Motion-based reconstruction is a different task from the MRF modeling role named in this column.')])
revise('P0928-Q05',[
 ('Structure from Motion: 3D reconstruction; computational photography: HDR and panoramas; deep learning: learned representations','The later-period column names Structure from Motion, computational-photography examples including HDR/panoramas, and deep learning. “Learned representations” describes the last method, without assigning an exact invention date.'),
 ('Structure from Motion: exposure fusion; computational photography: 3D reconstruction from motion; deep learning: learned representations','The first two associations exchange the listed reconstruction and computational-photography examples.'),
 ('Structure from Motion: 3D reconstruction; computational photography: HDR and panoramas; deep learning: hand-specified line-label rules','The first two associations match, but hand-specified line-label rules are not the later deep-learning approach.'),
 ('Structure from Motion: flexible object-part arrangements; computational photography: smoothness regularization; deep learning: learned representations','The first two roles instead refer to earlier pictorial-structure and regularization entries, not the later examples.')])
revise('P0930-Q01',[
 ('Intensity distribution over wavelength; selective changes in component strengths','E(λ) represents how light intensity varies with wavelength. Wavelength-dependent absorption can alter the relative spectral strengths.'),
 ('A single intensity integrated over wavelength; selective changes in component strengths','An integrated total is one number; E(λ) retains wavelength-dependent information.'),
 ('Intensity distribution over wavelength; the same attenuation factor at every wavelength','The first description matches, but absorption can be wavelength selective rather than uniformly scaling every component.'),
 ('The surface reflectance spectrum; the incident source’s wavelength distribution','E(λ) denotes illumination, while the later R(λ) denotes reflectance. These factors should not be interchanged.')])
revise('P0930-Q04',[
 ('White light can contain several wavelength components with different refraction angles','The prism illustration separates wavelength components already present in the incident white light.'),
 ('White light contains several components, but separation occurs through selective absorption alone','Selective absorption can change spectral strengths, but the illustrated spatial separation relies on wavelength-dependent refraction.'),
 ('White light enters at one wavelength and is converted into several wavelengths by refraction','Ordinary dispersive refraction separates incident components; it does not create the spectrum by converting one input wavelength into many.'),
 ('White light contains several components whose different intensities alone set their exit angles','The dispersion illustrated depends on wavelength, not merely on the intensity of each component.')])
revise('P0931-Q01',[
 ('The reflected component is zero, while incident light at that wavelength may be nonzero','In L(λ)=E(λ)R(λ), R(λ)=0 forces L(λ)=0 without requiring E(λ)=0.'),
 ('Both the reflected component and the incident component must be zero','Zero reflectance removes the reflected contribution but does not require the incident source to lack that wavelength.'),
 ('The reflected component equals the incident component because the surface contributes nothing','Equal reflected and incident components would correspond to R(λ)=1 in this simplified product, not R(λ)=0.'),
 ('The reflected component is zero only if receptor sensitivity at that wavelength is also zero','The reflected spectrum L is already zero before multiplication by any receptor sensitivity.')])
revise('P0931-Q03',[
 ('Rods: sensitive low-light intensity response; cones: daylight color response','The source contrasts rod sensitivity in low light with cone-based color vision under brighter conditions.'),
 ('Rods: daylight color response; cones: sensitive low-light intensity response','This reverses the two roles emphasized by the source.'),
 ('Rods: sensitive low-light color response; cones: daylight intensity response without color separation','This assigns color-channel discrimination to rods and removes the cone color role stated on the slide.'),
 ('Rods: mainly daylight intensity response; cones: mainly low-light color response','This reverses the emphasized operating-light regimes and misplaces low-light color performance.')])
revise('P0931-Q04',[
 ('Specify whether the quantities are per wavelength and whether an angular radiance convention is used','A spectral radiometric model needs a wavelength-density convention and, for radiance, an angular convention. The slide’s W m⁻² label and simplified product alone do not supply these definitions.'),
 ('Use W m⁻² unchanged for both band-integrated power and density per unit wavelength','A density per unit wavelength carries an additional inverse-wavelength unit; it should not silently be treated as a band-integrated quantity.'),
 ('Give reflectance an inverse-wavelength unit to make the printed unit spectral','Reflectance R(λ) is a dimensionless fraction in this model; adding inverse-wavelength units to it does not define the illumination’s spectral convention.'),
 ('Treat radiance and irradiance as the same quantity because both refer to light on a surface','Radiance and irradiance have different angular definitions. Their distinction cannot be removed by the simplified notation.')],stem='What additional definition is needed before treating the slide’s W m⁻² label as a complete unit specification for the spectral quantities in L(λ)=E(λ)R(λ)?')
revise('P0934-Q03',[
 ('A physical array of light-sensitive silicon sites that generates electrical signals','The prose beneath the pipeline describes a regular photosite array that converts incident light into electrical signals.'),
 ('A filter array that selects spectral bands but does not generate electrical signals','That describes the color filters placed over photosites, not the light-sensitive sites themselves.'),
 ('A reconstructed array of full-color values produced after missing-channel interpolation','That describes a processed color image, not the physical sensor array before demosaicing.'),
 ('A lenslet array that redirects light onto a separate light-sensitive layer','Lenslets can redirect light, but the source’s photosites are the light-sensitive electronic conversion sites.')])
revise('P0935-Q01',[
 ('CCD: shift charge toward common output conversion; CMOS: local conversion and addressed readout','The diagrams contrast CCD charge transfer toward output circuitry with pixel-associated CMOS conversion and addressing.'),
 ('CCD: local conversion and addressed readout; CMOS: shift charge toward common output conversion','This reverses the architecture contrast shown in the diagrams.'),
 ('CCD: shift charge toward common output conversion; CMOS: the same charge-transfer chain with a different color filter','The CCD part matches, but the CMOS diagram differs in local conversion/readout rather than merely in its color filters.'),
 ('CCD: local conversion before transferring pixel voltages; CMOS: local conversion and addressed readout','The CMOS part matches, but the CCD figure shows transferred charge, not a voltage conversion at every pixel before the transfer chain.')])
revise('P0935-Q02',[
 ('Generate an electrical image signal from incident light','Both CCD and CMOS are image-sensor technologies performing light-to-electrical acquisition.'),
 ('Transfer each pixel’s charge through the same serial conversion path','A shared CCD-style transfer path is not the common function across the two contrasting architectures.'),
 ('Convert charge to voltage locally at each addressed pixel','Local addressed conversion characterizes the depicted CMOS architecture, not both diagrams.'),
 ('Reconstruct the two unmeasured color channels at every filtered site','Missing-channel reconstruction is demosaicing, a subsequent processing step rather than the shared photosensing function.')])
revise('P0935-Q03',[
 ('Use complementary metal-oxide-semiconductor; retain the local-conversion/readout comparison','The standard expansion is complementary metal-oxide-semiconductor. Correcting the acronym wording does not require reversing the separately illustrated readout contrast.'),
 ('Use complementary metal-oxide-semiconductor; exchange the CCD and CMOS readout descriptions','The acronym correction is appropriate, but the wording issue provides no basis for exchanging the architecture labels.'),
 ('Use complementary metal oxide on silicon; retain the local-conversion/readout comparison','The readout concept can be retained, but the printed wording is not the standard CMOS expansion.'),
 ('Use complementary metal-oxide sensor; retain the local-conversion/readout comparison','The diagram can be retained, but replacing semiconductor with sensor still does not give the standard expansion.')],stem='Which treatment corrects the source’s “Complementary Metal Oxide on Silicon” expansion while keeping its separate CCD/CMOS readout comparison?')
revise('P0936-Q03',[
 ('Amplify the already-sensed electrical signal before ADC','The analog gain lies after sensing and before ADC. At fixed illumination and exposure, increasing it does not itself collect additional incident photons.'),
 ('Increase the number of collected photons in proportion to the gain','Photon collection depends on the optical exposure; downstream electrical amplification does not itself increase it.'),
 ('Reduce the existing photon-count fluctuations before amplifying the signal','Multiplying the existing signal also scales its existing fluctuations; it is not a photon-shot-noise removal step.'),
 ('Rescale only the digital values after the ADC has quantized the signal','That describes digital gain. The question specifically asks about the analog gain stage before conversion.')])
revise('P0936-Q05',[
 ('Provide different sites with wavelength-selective samples for later color reconstruction','Color filters give neighboring photosites different spectral sensitivities, supplying channel samples for reconstruction.'),
 ('Resolve the complete wavelength spectrum independently at each filtered site','A channel-filtered intensity is a weighted spectral measurement, not a complete independently resolved spectrum.'),
 ('Measure a full red-green-blue triplet simultaneously at each filtered site','In the depicted mosaic, each site records one filtered sample; missing channels still require reconstruction.'),
 ('Measure the same broad-band intensity at all sites and assign color from spatial position alone','The filters intentionally provide different wavelength-selective measurements, rather than identical broad-band measurements.')])
revise('P0937-Q02',[
 ('Shot noise: photon-count variability; dark current: thermally generated electrons','These are the two mechanisms named in the source.'),
 ('Shot noise: thermally generated electrons; dark current: photon-count variability','This exchanges the named photon and thermal mechanisms.'),
 ('Shot noise: photon-count variability; dark current: ADC rounding error','The shot-noise part matches, but dark current is generated thermally rather than by digital quantization.'),
 ('Shot noise: readout-amplifier fluctuations; dark current: thermally generated electrons','The dark-current part matches, but amplifier read noise is a different mechanism from photon shot noise.')])
revise('P0937-Q03',[
 ('Apply a denoising filter aimed at suppressing random fluctuations','The source identifies denoising as the processing step for visible noise or graininess, particularly in low light.'),
 ('Apply white-balance gains to make a neutral region colorless','White balance corrects relative channel color, not the random fluctuations that define the stated graininess.'),
 ('Apply a color-correction matrix to map sensor channels to a standard space','Color-space correction addresses channel response, not specifically random sensor noise.'),
 ('Apply edge sharpening to increase local high-frequency contrast','Sharpening emphasizes edge contrast and can also accentuate noise, rather than directly suppressing graininess.')])
revise('P0937-Q04',[
 ('It can increase edge contrast without guaranteeing recovery of detail lost at capture','Sharpening enhances the appearance of existing edges. This alone does not establish recovery of information that was not recorded.'),
 ('It recovers the pre-blur scene whenever edge contrast is increased','Increased contrast is not evidence that the unique original scene has been recovered from blurred data.'),
 ('It suppresses random noise by using the same local averaging operation as smoothing','Smoothing and sharpening have different objectives; sharpening is not simply the denoising average operation.'),
 ('It improves edge contrast without affecting high-frequency noise already present','High-frequency noise can also be enhanced, so edge contrast improvement does not imply that noise is unaffected.')])
revise('P0938-Q02',[
 ('Sensor channels need mapping to a desired color space, potentially mixing channels rather than only scaling them','Camera filter sensitivities do not exactly match the desired human or standard color-space responses. A matrix can mix channels beyond the gains used for white balance.'),
 ('The matrix estimates the two missing channel samples at each mosaic photosite','Estimating missing samples is demosaicing; the stated matrix maps the resulting color responses.'),
 ('The matrix replaces the need to specify the target color space after white balance','The matrix is chosen for a desired representation such as CIE XYZ or sRGB; it does not remove that specification.'),
 ('The matrix performs the same independent channel gains as white balance, with no channel mixing','A general color-correction matrix can have off-diagonal coefficients, so it is not restricted to independent channel gains.')])
revise('P0938-Q05',[
 ('Gamma: nonlinear intensity encoding; compression: reduce the data representation','Gamma changes how intensity is encoded; compression reduces the representation used for storage or transmission.'),
 ('Gamma: reduce the number of stored samples; compression: nonlinear intensity encoding','This exchanges the principal signal-encoding and data-reduction roles.'),
 ('Gamma: equalize a neutral patch’s channels; compression: reduce the data representation','The compression role matches, but equalizing channels for a neutral patch is white balance rather than gamma encoding.'),
 ('Gamma: nonlinear intensity encoding; compression: map sensor RGB to a standard color space','The gamma role matches, but mapping sensor responses to a standard color space is color correction, not compression.')])
revise('P0939-Q01',[
 ('The physical sensor is behind the optics; the virtual image plane is a construction in front','The drawing places the real sensor behind the lens and a virtual geometric image plane on the object side.'),
 ('The physical sensor is in front of the optics; the virtual plane is behind','This reverses the locations shown in the figure.'),
 ('Both planes are behind the optics, with the virtual plane farther from the lens','The depicted virtual plane is on the front, object-facing side rather than behind the optics.'),
 ('The front plane is the physical detector, and the rear plane is its geometric projection','This assigns the physical detector role to the front virtual construction rather than the rear sensor.')])
revise('P0939-Q02',[
 ('The direction perpendicular to the local surface, separate from the viewing ray','The surface normal describes local surface orientation. The reflected ray toward the camera is drawn separately.'),
 ('The direction tangent to the local surface, separate from the viewing ray','A normal is perpendicular, not tangent, to the local surface.'),
 ('The incoming illumination direction toward the surface','The incident illumination is a separate ray; it does not define the surface normal.'),
 ('The reflected-light direction from the surface toward the camera','The viewing/reflected ray is separate from the normal and need not point in the same direction.')])
revise('P0940-Q01',[
 ('Straight rays from the object’s top cross the opening and reach the lower rear plane','The top and bottom ray paths cross at the aperture, producing an inverted real image on the rear plane.'),
 ('The aperture reflects the top rays downward before they reach the rear plane','The pinhole illustration uses straight transmission through the opening, not a reflecting surface at the aperture.'),
 ('The aperture refracts the top rays downward in the same way as a convex lens','The ideal pinhole model does not contain a refractive lens. Inversion follows from straight-ray geometry.'),
 ('The diagram uses the upright front virtual plane as the physical rear sensor','A front virtual plane can yield an upright convention, but the physical rear plane in this drawing receives the inverted image.')])
revise('P0940-Q02',[
 ('A lens collects light over a larger aperture while bringing suitable rays to a focused image','A tiny pinhole admits little light. A lens can collect light over a larger area and focus it, subject to the optical focusing model.'),
 ('A lens collects more light because a larger opening has the same ray selectivity as a pinhole','An unassisted larger opening admits a wider range of ray paths and blur. A lens adds focusing rather than preserving pinhole selectivity unchanged.'),
 ('A lens collects light over a larger aperture while removing dependence on object distance','The light-collection advantage does not remove the lens’s object/image distance focusing relation.'),
 ('A lens collects the same amount of light as a tiny pinhole while sharpening by blocking more rays','The stated motivation is greater light collection and focusing, not retaining the tiny aperture’s light level by further blocking.')])
revise('P0940-Q03',[
 ('Ideal pinhole: no lens-focus adjustment; real aperture size still affects light and sharpness','The geometric pinhole selects narrow ray paths without lens focusing, but real aperture size introduces light-collection and sharpness limits.'),
 ('Ideal pinhole: the same reciprocal-distance focus adjustment as a thin lens; real aperture size affects light','A pinhole has no refracting lens with the specified reciprocal-distance focus relation.'),
 ('Ideal pinhole: no lens-focus adjustment; decreasing real aperture size improves sharpness without a lower-limit trade-off','The ideal geometric model cannot justify indefinite real-image sharpening as the aperture shrinks; light collection and diffraction impose limits.'),
 ('Ideal pinhole: adjust aperture diameter to move a refractive focal plane; smaller diameters reduce light','A pinhole does not move a refractive focal plane by changing its diameter, even though aperture diameter affects collected light.')])
revise('P0941-Q04',[
 ('Define and consistently use signed object, image and focal distances for the broader case','The source’s positive-distance equation is scoped to its real-object/real-image drawing. Extending it to virtual images requires a consistent sign convention.'),
 ('Keep both distances positive and use the same plus-sign equation for every image type','Taking magnitudes while retaining the real-image plus signs discards the sign information needed in the broader virtual-image case.'),
 ('Negate the image distance but keep an unrelated convention for object and focal distances','Changing one sign without defining the full convention can mix incompatible formulas; all signed quantities must be interpreted consistently.'),
 ('Use the magnification sign to choose the image-distance sign independently of the lens convention','Magnification and the lens equation must follow the same distance convention, not independent sign choices.')],stem='How should the slide’s absolute-distance thin-lens equation be extended to a virtual-image calculation?')
revise('P0941-Q05',[
 ('The eye’s crystalline lens is contrasted with compound glass/plastic camera lenses','This is the simplified comparison printed on the slide, not a claim that the crystalline lens exhausts the eye’s optics.'),
 ('The eye’s cornea alone is contrasted with compound glass/plastic camera lenses','The cornea has an optical role, but the source’s particular comparison names the crystalline lens rather than the cornea alone.'),
 ('The eye’s crystalline lens is contrasted with one thin glass element in every camera','The eye element matches the source, but the camera discussion describes compound elements rather than a universal single element.'),
 ('Several separate crystalline elements in the eye are contrasted with one plastic camera element','This reverses the simplified single-eye-lens versus compound-camera description and changes the stated camera construction.')])
revise('P0946-Q05',[
 ('Retain continuous coordinates for geometry; round when a particular integer pixel-index operation requires it','Projection can return fractional image locations. Rounding is a sampling/indexing choice, not a necessary part of the continuous projective map.'),
 ('Round immediately because integer-addressed photosites make fractional image locations undefined','Discrete sample addresses do not make continuous projected locations or subpixel estimation undefined.'),
 ('Round the homogeneous coordinates before dividing by their third component','Rounding before normalization changes the represented point and depends on arbitrary homogeneous scale.'),
 ('Retain fractional coordinates only when the sensor has physically fractional pixel addresses','Subpixel positions are continuous locations relative to the pixel grid, not a requirement for fractional hardware addresses.')])
revise('P0947-Q04',[
 ('SE3 is undefined at the call; bind it with an import such as from spatialmath import SE3','The displayed import binds CentralCamera but not the separately referenced SE3 name.'),
 ('SE3 becomes available automatically because CentralCamera imports its own dependencies','A module’s internal dependencies do not automatically create every dependency name in the caller’s global namespace.'),
 ('SE3 can be imported after the failed move call to make that earlier call succeed without rerunning it','A later import does not retroactively execute a statement that already failed with an undefined name.'),
 ('SE3 is a camera instance attribute and must be reached by changing SE3.Tx to camera.SE3.Tx','The displayed expression references the separate spatialmath transformation class, not an SE3 attribute supplied by the camera instance.')])
revise('P0947-Q05',[
 ('The name camera now refers to the new pixel-calibrated object, so the call uses its calibration','Sequential assignment rebinds camera. The method now uses the new pixel pitch and principal point rather than the first constructor’s metric-scale defaults.'),
 ('The name camera still refers to the first object because the constructors use the same class','Using the same class does not prevent a later assignment from rebinding the variable to the newly created instance.'),
 ('The new principal point is used, but the first object’s sampling pitch remains attached to the name','Assignment does not merge selected attributes from the old and new instances; the call uses the newly constructed camera’s calibration.'),
 ('The new sampling pitch is used only after modifying the world-point array P in place','P remains expressed in the supplied world units. Projection applies the camera calibration without first rewriting P as pixel coordinates.')])
revise('P0947-Q06',[
 ('f: physical focal length; rho: physical pixel pitch; imagesize: pixel counts; pp: principal-point pixels','These parameter meanings turn the metric projection into the displayed pixel output.'),
 ('f: focal length in pixels; rho: physical pixel pitch; imagesize: pixel counts; pp: principal-point pixels','The f argument here is a physical focal length; the ratio f/rho gives focal length in pixels.'),
 ('f: physical focal length; rho: pixels per unit length; imagesize: pixel counts; pp: principal-point pixels','rho is physical pitch, a length per pixel, rather than its reciprocal sampling density.'),
 ('f: physical focal length; rho: physical pixel pitch; imagesize: physical sensor dimensions; pp: principal-point lengths','imagesize and pp are specified in pixel units, not physical sensor lengths.')])
revise('P0948-Q02',[
 ('No; a nearer surface on the same viewing ray can occlude the in-bounds point','Bounds and positive depth establish field-of-view eligibility. Occlusion also requires comparing scene geometry along the viewing ray.'),
 ('Yes; positive depth selects the nearest surface on each viewing ray','Positive depth only places a point in front of the camera. Several points at different positive depths can share a viewing ray.'),
 ('Yes; image-boundary tests reject farther points that share a pixel with nearer ones','A boundary test checks image coordinates, not a nearest-depth competition between surfaces.'),
 ('No; an additional focal-length calibration alone resolves all remaining occlusions','Better intrinsic calibration does not supply the missing scene geometry needed to decide whether another surface blocks the ray.')])
revise('P0948-Q03',[
 ('Different grid points can have different camera depths, producing different perspective scale factors','Perspective divides by camera depth. A tilted planar grid can therefore have nonuniform apparent spacing without changing its physical spacing.'),
 ('The tilted grid has one common depth scale, but its principal point differs at each grid node','The principal point is a camera parameter, not a separate value at every grid point; the relevant variation is depth.'),
 ('The tilted grid retains a single scale, and unequal spacing arises solely from rotating the image axes','An in-plane axis rotation alone preserves equal distances; oblique perspective can additionally vary depth and scale.'),
 ('Nonuniform spacing requires radial lens distortion even for a tilted plane','An ideal undistorted perspective camera can produce the stated effect, so radial distortion is not necessary.')])
revise('P0948-Q04',[
 ('The shared direction has a nonzero camera-depth component, with nondegenerate line projections','For common direction d, the finite limiting point depends on d_x/d_z and d_y/d_z, requiring d_z≠0; degenerate line projections are excluded.'),
 ('The shared direction is parallel to the image plane, with zero camera-depth component','When d_z=0, the vanishing point is at infinity rather than a finite image location.'),
 ('Both lines have positive depth somewhere, regardless of their shared direction','A positive-depth point does not imply that the direction has the nonzero depth component needed for a finite vanishing point.'),
 ('Both lines lie in one plane, even when their shared direction is parallel to the image plane','Coplanarity does not turn a direction with d_z=0 into a finite vanishing point.')])
revise('P0949-Q05',[
 ('The first mkgrid call precedes its displayed import, and camera and SE3 require existing bindings','A fresh top-to-bottom execution needs all referenced names initialized before their use. The page otherwise behaves as a continuation fragment.'),
 ('The import below the first mkgrid call makes that earlier call valid in a fresh execution','Python executes imports in sequence; a later import does not resolve an undefined name at an earlier executed statement.'),
 ('Importing NumPy as np also binds mkgrid and SE3 because the later calculations use arrays','Importing NumPy binds its requested module name, not unrelated toolbox and spatialmath names.'),
 ('Earlier notebook cells are irrelevant because each displayed code fragment has an isolated namespace','Notebook cells can retain prior bindings. That shared state can make a fragment work even when it is not standalone.')])
revise('P0949-Q06',[
 ('The original stored camera pose, unless a separate operation has changed it','The supplied API rule makes pose an override for one call only. A later call without the keyword uses the unchanged stored pose.'),
 ('The prior keyword pose, retained as the default until another keyword is supplied','This would be a persistent override, contrary to the explicitly supplied non-mutating per-call rule.'),
 ('An identity pose, because finishing a keyword override resets camera.pose','Non-mutating means the stored pose is retained, not reset to identity after the call.'),
 ('An error, because later projection calls must repeat any previously supplied pose keyword','The supplied rule allows a later call without the keyword; that call uses the stored pose rather than requiring repeated arguments.')])
revise('P0950-Q01',[
 ('Construct cube-edge coordinates and project them as a wireframe using the camera','mkcube creates the spatial edge geometry and plot_wireframe renders its camera projection.'),
 ('Construct only the cube center and infer the visible edges from that single projection','The edge arrays provide spatial edge geometry rather than only a single center point.'),
 ('Construct cube-edge coordinates and draw their X and Y values without perspective projection','The camera method projects the 3D coordinates; it is not simply a direct Cartesian X-versus-Y plot.'),
 ('Construct a filled textured surface and determine every hidden-face boundary','The shown operation is a wireframe projection; the fragment does not establish textured surface rendering or complete hidden-face handling.')])
# Two citation-flagged objects also receive comparable spectral distractors.
revise('P0932-Q04',[
 ('Different spectra may give the same three weighted responses','Three weighted measurements need not uniquely recover a spectrum with more than three independently variable bands.'),
 ('Equal response triples imply equal intensity at every wavelength','Equality of the three weighted totals does not imply equality of all the individual spectral components.'),
 ('Three responses recover the full spectrum whenever the sensitivity curves are normalized','Normalizing three sensitivity curves does not supply the missing independent spectral measurements.'),
 ('Three responses remove all dependence on the incident illumination spectrum','The received spectrum is weighted by the receptor sensitivities; illumination still affects the resulting responses.')])
revise('P0933-Q01',[
 ('Three integrated, sensitivity-weighted responses for the illustrated light/material combination','The solid-color areas correspond to the receptor-response integrals, producing the tristimulus vector.'),
 ('Three wavelengths at which the receptor sensitivity curves reach their peaks','Peak wavelength locations are not the integrated responses represented by the vector.'),
 ('Three peak heights, one from each colored response curve','A peak height is a local curve value; the vector components are integrated areas, not merely the highest values.'),
 ('Three material constants unchanged when the incident illumination changes','The light/material combination determines the received spectrum. Changing illumination can change the response triple.')])
def cite(short,p,kind,locator,role='premise',evidence=None):
 ci=next(c for c in q(short)['citations'] if c['physicalPage']==p);ci.update(kind=kind,locator=locator,role=role)
 if evidence is not None:ci['evidenceText']=evidence
cite('P0932-Q04',932,'equation','Printed slide 12: three integrals of received spectrum L(λ) times receptor sensitivities M_r(λ), M_g(λ), M_b(λ).')
cite('P0932-Q04',933,'statement','Printed slide 13: first bullet identifies the response three-vector (ρ, γ, β) as the tristimulus value.')
cite('P0933-Q01',931,'equation','Printed slide 11: received light L(λ)=E(λ)R(λ), with separate illumination E and surface reflectance R factors.')
cite('P0933-Q01',932,'equation','Printed slide 12: response integrals weight received light L(λ) by the three receptor sensitivity functions.')
cite('P0933-Q01',933,'figure','Printed slide 13: upper-right filled red, green and blue response regions for the red-brick example; adjacent prose identifies their areas with the integrals.')
cite('P0934-Q03',934,'statement','Printed slide 14: prose beneath the imaging pipeline describes the regular light-sensitive silicon photosite array and retina analogy.')
q('P0943-Q04')['citations']=[c for c in q('P0943-Q04')['citations'] if c['physicalPage']==943]
q('P0943-Q04')['stem']='A camera has no rotation and its origin is t=(−0.5,0,0) m in the world frame. What camera coordinates represent the world point (0.3,0.4,5) m?'
q('P0943-Q06')['solution']['steps']=['Normalize the original: (6/3,3/3)=(2,1).','The vectors (2,1,1)ᵀ and (−4,−2,−2)ᵀ both normalize to (2,1).','The vectors (6,3,1)ᵀ and (2,3,3)ᵀ normalize to (6,3) and (2/3,1), respectively, so neither is equivalent.']
item=q('P0949-Q03')
item['stem']='A frontal 3×3 grid has total side length 0.2 m and is centered at camera-frame point (0,0,1) m, with its rows and columns parallel to the camera X and Y axes. With focal length 1500 pixels and principal point (640,512) pixels, what are its horizontal image coordinates?'
item['assumptions']=['The grid is centered at X=Y=0 and all its points have camera depth Z=1 m. Its three samples on each axis include both ends of the total 0.2 m span.','Use ideal undistorted perspective projection with no rounding.']
item['solution']['steps']=['The centered total width 0.2 m gives X∈{−0.1,0,0.1} m.','Use u=u₀+fₓX/Z, with u₀=640 pixels, fₓ=1500 pixels and Z=1 m.','The displacements are {−150,0,150} pixels; adding 640 gives {490,640,790} pixels.']
item['solution']['formulas']=[dict(expression='u=u₀+fₓX/Z',variables={'u':'horizontal projected image coordinate','u₀':'horizontal principal-point coordinate','fₓ':'horizontal focal length expressed in pixels','X':'horizontal point coordinate in the camera frame','Z':'point depth in the camera frame'},units={'u,u₀,fₓ':'pixels','X,Z':'m'},assumptions=['Ideal zero-skew undistorted perspective camera; X and Z refer to the same camera frame; Z>0.'])]
cite('P0949-Q03',949,'code','Printed slide 29: comment states the grid center (0,0,1); mkgrid(n=3, side=0.2, pose=SE3(0,0,1)) constructs the centered frontal grid.')
# Add the one independently identified missing interpretation angle, not another generic tristimulus definition.
gap=copy.deepcopy(q('P0933-Q01'));gap.update(id=B+'-P0933-Q02',version=1,status='draft',reviewIds=[],type='diagram',difficulty='easy',origin='generated');gap.pop('revisionAuthors',None)
gap['stem']='On printed slide 12 the three normalized cone-sensitivity curves have peaks near one. In the red-brick response plot on printed slide 13, which comparison is supported?'
gap['assumptions']=['Interpret the displayed red-brick illumination/material example, not every possible red object or illuminant.','Compare integrated weighted-response areas, not pixel colors sampled from the rendered slide.']
gap['options']=[{'id':'o2','text':'The three responses are equal because their normalized sensitivity curves have equal peak heights'},{'id':'o1','text':'The L-cone response is largest, although equal normalized sensitivity peaks do not imply equal weighted areas'},{'id':'o4','text':'The S-cone response is largest because its normalized sensitivity curve has the narrowest peak'},{'id':'o3','text':'The L-cone response is largest because its normalized sensitivity peak alone is higher than the other two'}]
gap['correctOptionIds']=['o1']
why={'o1':'The red-brick slide explicitly identifies the dominant L-cone response. The colored response areas incorporate the received spectrum and sensitivity; the separately normalized sensitivity peaks do not determine equal response integrals.','o2':'Equal normalized peak heights do not make the areas under the illumination-weighted sensitivity products equal. The displayed red-brick areas are unequal.','o3':'L dominance in this example is a weighted-area statement, not evidence of a uniquely higher normalized sensitivity peak; all three normalized peaks are near one.','o4':'A narrower normalized sensitivity peak does not imply a larger weighted response. The displayed S response is not dominant.'}
gap['solution'].update(justification=why['o1'],simpleExplanation=why['o1'],optionExplanations={k:('Correct. ' if k=='o1' else 'Incorrect. ')+v for k,v in why.items()},steps=['Distinguish the normalized sensitivity curves on printed slide 12 from the filled weighted-response curves on printed slide 13.','Use the displayed response areas and the source’s explicit dominant-L statement, not sensitivity-peak normalization.'],formulas=[],misconceptions=[why[k] for k in ('o2','o3','o4')])
def newcite(p,kind,locator,evidence,role='premise'):
 return dict(slideId=f'lectures-p{p:04d}',sourceId='lectures',sourceSha256='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c',physicalPage=p,kind=kind,locator=locator,evidenceText=evidence,role=role,region=None)
gap['citations']=[newcite(932,'figure','Printed slide 12: upper-right spectral-sensitivity plot, normalized peaks near 1 for L, M and S cones.','The vertical axis reads Normalized Cone’s Response M(λ); the three sensitivity curves peak near 1.'),newcite(932,'equation','Printed slide 12: three receptor responses integrate the received spectrum multiplied by the corresponding sensitivity.','ρ=∫L(λ)M_r(λ)dλ; γ=∫L(λ)M_g(λ)dλ; β=∫L(λ)M_b(λ)dλ.'),newcite(933,'figure','Printed slide 13: upper-right filled red-brick weighted-response areas, with the red region dominant.','The colored filled regions represent the response-integral areas for the red-brick example.'),newcite(933,'statement','Printed slide 13: third bullet explicitly identifies the dominant L-cone response.','The dominant response is from the L cone.','explicit')]
b['questions'].append(gap);qm[gap['id']]=gap
for c in b['concepts']:
 for item in b['questions']:
  if item['id'] not in flags:continue
  prev=next(x for x in old['questions'] if x['id']==item['id']);c['examinationAngles']=[item['stem'] if x==prev['stem'] else x for x in c.get('examinationAngles',[])]
 if c['id']=='W07-L31-P0933-C01':
  c['questionIds'].append(gap['id']);c['examinationAngles'].append(gap['stem']);c['description']='Interpret weighted-response areas as tristimulus components, identify the example’s dominant L response, and distinguish these areas from normalized sensitivity peaks.'
# Conservative prose-only spacing cleanup on revised objects, never accepted objects or source transcriptions.
def clean(s):
 replacements={'point(':'point (','direction(':'direction (','original:(':'original: (','gives(':'gives (','to(':'to (','Compute(':'Compute (','origin:0.3':'origin: 0.3','coordinates−':'coordinates −','obtain{':'obtain {','point(640':'point (640','side0.2':'side 0.2','and1.1':'and 1.1','plane3':'plane 3','page949':'page 949'}
 for a,z in replacements.items():s=s.replace(a,z)
 return s
for item in [qm[i] for i in flags]+[gap]:
 item['stem']=clean(item['stem']);item['assumptions']=[clean(x) for x in item['assumptions']]
 for key in ('justification','simpleExplanation'):item['solution'][key]=clean(item['solution'][key])
 for key in ('steps','misconceptions'):item['solution'][key]=[clean(x) for x in item['solution'][key]]
 item['solution']['optionExplanations']={k:clean(v) for k,v in item['solution']['optionExplanations'].items()}
 for ci in item['citations']:ci['locator']=clean(ci['locator'])
# Author checks of every changed numerical answer and foil, plus invariants and gap reasoning.
checks=[]
def ck(name,ok,detail):
 assert ok,name;checks.append(dict(name=name,passed=True,detail=detail,independent=False))
ck('64 accepted objects and review-bound hashes preserved',all(prev==qm[prev['id']] and qhash(prev)==qhash(qm[prev['id']]) for prev in accepted),'No accepted content or status fields were changed.')
ck('108 existing answer sets unchanged',all(prev['correctOptionIds']==qm[prev['id']]['correctOptionIds'] for prev in old['questions']),'The grid key is now supported by an explicit center premise.')
ck('12 source issues and external issue file unchanged',b['sourceIssues']==old['sourceIssues'] and fhash(f'audits/source-disputes-{B}.json')==sourcehash,'Original source defects and qualifications remain visible.')
ck('All 44 flagged versions revised',all(qm[i]['version']==2 and qm[i]['status']=='draft' and not qm[i]['reviewIds'] for i in flags),'Re-review required for every changed object.')
ck('41 comparable distractor sets supplied',len(changed_sets)==41,'39 requested sets plus two citation-flagged spectral objects improved without changing their keys.')
ck('Camera translation answer',F(3,10)-(-F(1,2))==F(4,5),'P_C=P_W−t=(0.8,0.4,5) m.')
ck('Translation foil sign',F(3,10)+(-F(1,2))==-F(1,5),'Adding instead of subtracting gives x=−0.2 m; other two options put the 0.5 m correction on the wrong axis.')
normal=lambda v:(F(v[0],v[2]),F(v[1],v[2]))
ck('Homogeneous correct representatives',normal((6,3,3))==normal((2,1,1))==normal((-4,-2,-2))==(2,1),'Both positive and negative nonzero common scales preserve the normalized point.')
ck('Homogeneous distractors',normal((6,3,1))==(6,3) and normal((2,3,3))==(F(2,3),1),'Both differ from (2,1); explanation names vectors rather than displayed positions.')
xs=[-F(1,10),F(0),F(1,10)];us=[640+1500*x for x in xs]
ck('Centered-grid correct coordinates',us==[490,640,790],'Total side 0.2 m centered at X=0, Z=1 m; u=640+1500X/Z.')
ck('Grid double-half-width foil',[640+1500*x for x in [-F(1,5),0,F(1,5)]]==[340,640,940],'Treating total side 0.2 m as half-width doubles offsets.')
ck('Grid unit-mixing foil',[640+x for x in xs]==[F(6399,10),640,F(6401,10)],'639.9,640,640.1 mix metre coordinates into pixel offsets.')
ck('Grid missing-principal-point foil',[1500*x for x in xs]==[-150,0,150],'Correct relative displacements but missing 640-pixel principal point.')
# A declared discrete illustration checks the conceptual distinction without inventing values for the slide plot.
sens=[[1,0],[0,1],[F(1,2),1]];spectrum=[1,2];weighted=[sum(a*c for a,c in zip(spectrum,row)) for row in sens]
ck('Equal sensitivity maxima do not imply equal weighted responses',all(max(row)==1 for row in sens) and weighted==[1,2,F(5,2)],'Author-supplied two-band illustration only; not a numerical reading of the red-brick plot.')
ck('One bounded interpretation gap added',gap['id']=='W07-L31-P0933-Q02' and gap['version']==1,'The new object distinguishes the source’s dominant L weighted area from sensitivity-curve normalization.')
assert len(b['questions'])==109
b['authorChecks']=old['authorChecks']+checks
b['coverageNote']='All 33 source pages retain their actual visual inspection records. Version 2 revises the 44 independently flagged questions and adds one red-brick dominant-L/normalized-sensitivity interpretation question, preserving all 64 accepted whole objects/hashes and all 12 source issues. Author checks are not independent approval.'
write(f'data/question-batches/{B}.json',b)
changed=[qm[i] for i in flags]+[gap]
blind=[{**{k:x[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions')},'citations':[{k:v for k,v in c.items() if k!='evidenceText'} for c in x['citations']]} for x in changed]
write(f'audits/blind-{B}-v2.json',blind);packetsha=fhash(f'audits/blind-{B}-v2.json')
write(manifest,dict(batchId=B,blindPacket=f'audits/blind-{B}-v2.json',blindPacketSha256=packetsha,questionSha256={x['id']:qhash(x) for x in changed},preservedAcceptedCount=64,preservedAcceptedHashes={x['id']:qhash(x) for x in accepted},sourceIssuesSha256=sourcehash,revisedCount=44,newQuestionIds=[gap['id']],independentReviewPending=True))
write(f'audits/{B}-v2-author-repair.json',dict(recordedAt=datetime.now(timezone.utc).isoformat(),authorId=A,independentReview=False,checks=checks,sourceRevisits='audits/L31-v2-source-revisits.json',actualPagesRevisited=sorted(map(int,read('audits/L31-v2-source-revisits.json')['pages'])),acceptedCountPreserved=64,sourceIssuesUnchanged=True,toolboxRuntimeExecuted=False))
(R/f'audits/handoffs/{B}-v2.md').write_text(f'# L31 v2 frozen\n\n44 revised drafts plus one new red-brick interpretation question; total 109 questions. All 64 accepted objects and exact review-bound hashes are preserved. All 108 earlier keys and 12 source issues are unchanged. Twenty-one affected source pages were actually revisited.\n\nPacket: audits/blind-{B}-v2.json\nSHA256: {packetsha}\nManifest: {manifest}\nArchive: {archive}\nScript: scripts/repair_W07_L31_v2.py\nAuthor checks: audits/{B}-v2-author-repair.json\n\nRepairs include explicit grid center, shuffle-safe vector explanations, precise citation kinds/locations and comparable distractors. The bounded red-brick gap distinguishes weighted response areas from normalized sensitivity peaks. Fifteen author-check groups pass; these are not independent verification. Toolbox runtime remains unexecuted; no install was retried. No self-approval, canonical or Git writes. Do not regenerate this frozen script.\n')
print('FROZEN',len(changed),packetsha)
