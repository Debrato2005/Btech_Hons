#!/usr/bin/env python3
"""Author-side prefreeze quality refinement, never approval or postreview regeneration."""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];B='W11-L52';p=R/f'data/question-batches/{B}.json'
if (R/f'audits/{B}-review-manifest.json').exists():raise SystemExit('Frozen')
x=json.loads(p.read_text());Q={q['id'].removeprefix(B+'-'):q for q in x['questions']}
def wrong(k,start,text,reason):
 q=Q[k];o=next(o for o in q['options']if o['text'].startswith(start));assert o['id']not in q['correctOptionIds'];o['text']=text;q['solution']['optionExplanations'][o['id']]='Incorrect. '+reason
# Replace unrelated filler with plausible nearby technical confusions.
wrong('P1623-Q02','Localization: directly','Localization: estimate contact force; manipulation: estimate global pose only','This exchanges the immediate measurement roles of localization and contact manipulation.')
wrong('P1623-Q02','Localization: measure','Localization: determine pose solely from a target command; manipulation: infer actual contact solely from commanded torque','Commands are not observations of actual pose or contact under disturbances.')
wrong('P1624-Q01','LiDAR obstacle','LiDAR obstacle range; joint encoder angle','This places external range before internal joint state, reversing the requested order.')
wrong('P1624-Q02','Every force','A joint torque sensor must always be exteroceptive, even when used only to estimate internal actuator loading','The measured role and use matter; the force-related name does not force that classification.')
wrong('P1624-Q02','Every torque','A tactile contact sensor must be proprioceptive because it is mounted on the robot','Physical mounting does not turn an external-contact observation into internal configuration.')
wrong('P1627-Q01','The ground','The voltage between the two fixed track endpoints, rather than the wiper','With a fixed supply, the end-to-end voltage does not vary with wiper position.')
wrong('P1627-Q02','Only the serial','A linear scale inferred from supply voltage alone, with no angular endpoint calibration','The voltage rails alone do not establish the angular travel or mounting offset.')
wrong('P1627-Q02','A digital threshold','A calibration that ignores the input impedance loading the wiper','Loading can change the divider voltage and invalidate an unloaded calibration.')
wrong('P1628-Q01','Wiper to digital','Wiper to A0; digitalRead returns only HIGH or LOW; Serial.println sends that state','The source uses analogRead and retains a multi-level ADC count, not just a digital threshold state.')
wrong('P1630-Q03','The shaft','Each slot directly supplies a unique absolute angular code independent of any count history','A repeating slotted track produces pulses; absolute encoding needs a distinguishable position code.')
wrong('P1630-Q03','Every opaque','The receiver measures a steady light level and derives angle solely from that level','The illustrated incremental mechanism uses transitions as slots pass, not a static calibrated intensity-angle relation.')
wrong('P1631-Q01','A supply','A change in pulse amplitude that uniquely determines the angle without counting','The stated direction information is in relative timing, not a calibrated amplitude-to-angle mapping.')
wrong('P1632-Q03','To make','To prevent the compiler from caching count, with volatile playing no role','Volatile concerns optimization; the interrupt-masked region addresses the separate atomic-snapshot problem.')
wrong('P1633-Q01','The serial','The float division always uses integer arithmetic before the print cast','The explicit float cast in the calculation preserves fractional rotations until printing.')
wrong('P1634-Q01','The photodiode','The photodiode emits infrared light; the LED measures the returned intensity','This reverses the emitter and receiver roles.')
wrong('P1634-Q01','Both components','The LED measures ambient light only; the photodiode compares that reading with a stored distance','The LED is an active emitter and the receiver detects reflected light, not that two-stage ambient comparison.')
wrong('P1635-Q02','Keep the condition','Change INPUT to INPUT_PULLUP but leave the HIGH-detection comparison unchanged','A pull-up mode does not by itself invert a compatible module’s documented active-LOW output meaning.')
wrong('P1635-Q02','Only change','Reduce the loop delay while leaving the detection condition unchanged','Faster polling preserves the same inverted interpretation unless the branch logic is corrected.')
wrong('P1636-Q01','An illuminated','A displayed binary state is sufficient to distinguish every obstacle distance within range','Many distances and reflectivities can produce the same comparator state.')
wrong('P1638-Q01','Resistance is','Resistance rises with illumination, as in a positive-temperature-coefficient response','That reverses the decreasing illumination-resistance trend actually plotted.')
wrong('P1638-Q02','Illumination changes the number','Illumination directly produces a photodiode current while the element’s resistance is unchanged','That confuses an LDR with a photodiode transduction model.')
wrong('P1638-Q02','A moving magnetic','Illumination is measured only through a temperature-induced resistance change','The stated mechanism is photoconductive response, not a thermistor measuring temperature.')
wrong('P1639-Q01','It stays','It rises from2.5V to4.0V','Those values do not follow the supplied top-LDR, lower-fixed-resistor divider at40kΩ and10kΩ.')
wrong('P1639-Q02','Only replacing','Only a counts-to-voltage conversion using the ADC reference','Voltage calibration is necessary but does not alone supply the circuit’s voltage-to-illumination relationship.')
wrong('P1639-Q02','Only setting','Only the statement that LDR resistance decreases with brightness','A monotonic qualitative trend does not specify an absolute lux calibration.')
wrong('P1642-Q01','The ball changes','The output varies continuously with the ball’s position along a resistive track','The sketch shows a binary contact closure, not a potentiometer track.')
wrong('P1646-Q01','Light falling','A change in orientation that rolls a conducting ball onto both terminals','That is the tilt-switch mechanism, not the illustrated magnetic reed actuation.')
wrong('P1646-Q01','An ultrasonic','Mechanical contact between the external magnet and the electrical terminals','The magnetic field can actuate the enclosed contacts without the external magnet bridging the terminals.')
wrong('P1647-Q01','Pin9 cannot','Every loop iteration is counted as one wheel revolution while the switch stays closed','Repeated samples of a single closure are not distinct passage events.')
wrong('P1647-Q01','Serial.println','INPUT_PULLUP automatically debounces and counts distinct wheel passages','The pull-up establishes an idle electrical level; it does not add event-history logic or debouncing.')
wrong('P1648-Q01','The lit LED','The two states alone determine a unique distance-to-field calibration curve','Two qualitative states with unspecified geometry and field strength cannot determine that curve.')
wrong('P1648-Q01','The next page','The difference proves the code polarity changed between stills','Changing physical field/orientation or timing can change state without any demonstrated software change.')
wrong('P1653-Q01','206and','The displayed206/207 values prove the arithmetic uses exactly343m/s rather than340m/s','Without a supplied pulse duration or ground truth, those values do not distinguish the two coefficients.')
wrong('P1653-Q01','A monitor','The line-separated output proves a300ms update interval exactly','A static screenshot does not establish exact temporal spacing; execution also has overhead.')
wrong('P1654-Q01','The40kHz','The smaller range proves the sensor’s error decreased by the same amount','A change in measured range is not a measured change in error without ground truth.')
wrong('P1655-Q01','Absolute water','Ambient temperature and absolute humidity in grams per cubic meter','The example reports relative humidity in percent, not absolute vapor density.')
wrong('P1655-Q01','Temperature and','Dew-point temperature and soil water content','These are not the two directly printed channels in the DHT example.')
wrong('P1657-Q01','analogRead','Initialize Serial only → read humidity/temperature → initialize DHT after acquisition','The DHT device is initialized in setup before the loop reads it.')
wrong('P1657-Q02','A second label','A check only for values equal to zero','NaN is not equivalent to zero, and zero can be valid for some measured quantities.')
wrong('P1657-Q02','A conversion','Averaging the failed NaN with valid readings without first excluding it','NaN can propagate through arithmetic; averaging is not a substitute for validity handling.')
wrong('P1658-Q01','Yes for','Yes, provided the same rounded value repeats on several lines','Repeatability of formatted values does not establish calibration accuracy.')
wrong('P1660-Q01','Whether changing','Whether the board-level VCC label is being mistaken for a direct5V rating of the bare chip, without checking its regulator','The label alone does not establish the allowed input; the board’s actual design/rating must be checked.')
# Keep exactly one positive choice: the replacement above is phrased as a proposed distinction too.
q=Q['P1660-Q01'];o=next(o for o in q['options']if o['text'].startswith('Whether the board-level'));o['text']='Assume every board labeled VCC accepts5V, regardless of its regulator or level shifting';q['solution']['optionExplanations'][o['id']]='Incorrect. A VCC label alone does not establish an input rating or protective circuitry.'
wrong('P1660-Q01','Whether lowering','Assume the Mega’s5V supply makes every connected peripheral5V compatible','The controller supply does not determine the peripheral’s absolute electrical limits.')
wrong('P1660-Q02','20and21 are two','20and21 select two separate I2C devices;0x68 is an acceleration register','SDA/SCL are bus lines, while0x68 addresses the device rather than its acceleration register.')
wrong('P1661-Q01','Write0x3B','Select the gyroscope data block and interpret all six bytes as acceleration without changing the start register','The source selects the acceleration start register0x3B, not the gyro block.')
wrong('P1664-Q01','Only the serial','Beam direction alone, with sensor position/orientation omitted while constructing a world-frame map','Sensor-relative rays still need the sensor pose to be placed in a common world frame.')
wrong('P1664-Q01','Only the number','Sensor position alone, with beam direction and sensor orientation omitted','A range defines a sphere of possible points unless ray direction is known.')
wrong('P1664-Q02','Changing the console','Collecting repeated ranges along one unchanged beam and treating time as scan angle','Time alone does not establish a changing ray direction.')
wrong('P1664-Q02','Increasing Serial','Treating the sensor’s finite field of view as individually resolved angular bins without an angular output','An acceptance cone is not automatically a spatially resolved angular scan.')
wrong('P1669-Q01','Temperature and','Range and signal strength, with no angular position','Signal strength does not replace the directional coordinate needed to locate the return in a planar scan.')
wrong('P1669-Q01','Only range','Angular position and rotation rate, with no range measurement','Direction and timing alone do not give the point’s radial coordinate.')
wrong('P1670-Q01','Set the output','Select the application’s default COM port without confirming which device is connected','An unrelated default port may not address the scanner.')
wrong('P1670-Q01','Enter the angular','Select the port belonging to a different serial peripheral because both use USB','USB attachment does not make distinct serial ports interchangeable.')
wrong('P1671-Q02','Hertz and','416RPM implies416complete scans each second','RPM is per minute, so this omits the factor60 conversion.')
wrong('P1672-Q02','Stereo reports','Stereo estimates depth from image brightness alone; an event camera reports fixed-rate complete frames','Stereo relies on correspondence/disparity, while the stated event output is asynchronous changes.')
wrong('P1673-Q01','Lens light → final','Lens light → digital ADC code → photodiode charge → image processing','The charge signal must precede its digitization.')
wrong('P1673-Q02','It gives each','It makes every individual photodiode directly measure allRGB bands independently at once','A conventional color mosaic filters spectral samples; full color is reconstructed rather than measured in all bands at each site.')
wrong('P1673-Q02','It eliminates','It replaces the ADC by encoding colors as purely optical labels','Optical filtering does not remove the need for electrical readout and digitization.')
wrong('P1675-Q02','A direct metric','A guaranteed calibrated probability of correctness for this deployment','Calibration under deployment conditions has not been established.')
wrong('P1676-Q01','600frames','An exact universal600-entry taxonomy; the installed0–600index range excludes one endpoint','The inspected YAML includes both endpoints, giving601entries.')
wrong('P1676-Q03','The returned','The returned dimensions are the model’s internal tensor shape, not camera properties','These cap.get calls query the capture object, not the model preprocessing tensor.')
wrong('P1677-Q01','Keep a1280','Change only cap.set requests to1280×720, keeping the writer and forced640×480 resize unchanged','The writer/processed-frame mismatch remains because the forced resize still produces640×480.')
wrong('P1677-Q01','Change confidence','Keep the writer at1280×720 and rely on VideoWriter.write to resize every640×480 frame automatically','The documented contract requires matching frame size; automatic resizing is not guaranteed.')
wrong('P1677-Q02','Treatret','Infer on the original frame → write it → apply resizing only to the display copy','The actual source resizes before inference and writes the annotated result.')
wrong('P1677-Q05','The key changes','Only the display window closes; the loop continues to capture and write','The code executes break and then releases both capture and writer.')
wrong('P1678-Q01','A guarantee','The writer’s20fps setting proves that the displayed0 must be a rendering error','The independently computed counter can legitimately produce0 while writer metadata stays20fps.')
wrong('P1679-Q02','0.005','0.005m','This usesB×d/f instead off×B/d, reversing the disparity dependence.')
wrong('P1679-Q02','8m','800m','This multipliesf×B×d rather than dividing by disparity; it also fails the pixel-unit cancellation.')
wrong('P1682-Q02','Strain gauge: optical','Strain gauge: capacitance change; piezoelectric: resistance bridge; capacitive: generated charge','These are credible transducer mechanisms assigned to the wrong families.')
wrong('P1682-Q02','Strain gauge: charge','Strain gauge: resistance bridge; piezoelectric: capacitance change; capacitive: generated charge','The strain-gauge role is right, but the piezoelectric and capacitive mechanisms are interchanged.')
wrong('P1682-Q03','Static force','A static force can be inferred indefinitely from the initial piezoelectric peak without accounting for leakage','The initial dynamic response does not guarantee a stable long-termDC measurement.')
wrong('P1683-Q05','Only increase','Only zero the sensor once, assuming its gain can never drift','A zero adjustment does not validate gain or later changes across the operating range.')
# Final prefreeze author quality pass: parallel mechanisms, not unrelated filler.
wrong('P1627-Q01','Either fixed endpoint','The potentiometer housing, treating its mechanical rotation as an electrical terminal','The housing is not the movable electrical contact that taps the resistive track.')
wrong('P1635-Q01','A numerical range','No output until the input changes state','The printed loop reports the current level; it does not wait for an edge.')
wrong('P1643-Q02','Both states print','Both states print Tilt Not Detected! because INPUT_PULLUP keeps the pin HIGH even when grounded','A closed compatible contact to ground pulls the input LOW; a pull-up is not an overriding logic assignment.')
wrong('P1652-Q01','Both pins are analog','Pin 9 is the echo input; pin 10 supplies a 10 µs HIGH trigger','The interval is right, but the trigger and echo pin roles are reversed.')
wrong('P1655-Q01','Dew-point temperature','Ambient temperature and water-vapor partial pressure in pascals','The temperature channel is right, but relative humidity in percent is not pressure in pascals.')
wrong('P1672-Q03','A reflective','Active near-infrared reflected-light imaging for emitted heat; fisheye optics for wide field','The wide-field choice is suitable, but near-infrared reflectance is not the same as thermal emission imaging.')
wrong('P1672-Q03','Fisheye optics','Thermal imaging for heat; a long-focal-length narrow-angle lens for wide field','The thermal choice fits, but a narrow field does not supply the requested wide coverage.')
wrong('P1673-Q01','ADC code →','Lens light → photodiode charge → image processing → ADC conversion','For the described digital pipeline, digitization precedes digital image processing.')
wrong('P1677-Q05','Only the model','The loop exits, but capture and writer are released only when a later frame read fails','The cleanup follows the loop unconditionally, including the normal q exit.')
wrong('P1681-Q01','The title proves','The depth colormap can be identified as the separate infrared-intensity stream solely from its colors','A depth display uses a value-to-color mapping; that does not identify an infrared-intensity panel.')
wrong('P1623-Q03','Safety is guaranteed','Perception gives direct motor torque; feedback means storing labeled examples; learning means comparing current error with a target','This confuses interpretation, error-driven actuation and data-based learning rather than preserving their roles.')
wrong('P1642-Q02','Any change without','The initial level calibration removes every later acceleration-induced contact change','A stored reference cannot cancel changing mechanical forces on the ball.')
wrong('P1647-Q02','Zero falling','Five falling edges, because every observed transition is a new closure','Only HIGH-to-LOW transitions are falling edges; the two LOW-to-HIGH transitions are reopening events.')
q=Q['P1660-Q01'];q['stem']='The slide lists a 5 V connection for an MPU6500 module. Which electrical assumption is justified before wiring it?'
o=next(o for o in q['options']if o['id']in q['correctOptionIds']);o['text']='Use 5 V only if the actual breakout input circuitry is rated for it; do not apply that rating to the bare chip'
Q['P1631-Q02']['stem']=Q['P1631-Q02']['stem'].replace('Both A and B use interrupt-capable pins','A is wired to pin 2 and B to pin 3, both interrupt-capable pins')
Q['P1652-Q02']['solution']['formulas']=[dict(expression='d_int=trunc(t_echo c_sound/2)',variables={'d_int':'Assigned integer distance','t_echo':'Measured echo duration','c_sound':'Printed sound-speed coefficient'},units={'d_int':'cm','t_echo':'µs','c_sound':'cm/µs'},assumptions=['Positive representable input; c_sound=0.034 cm/µs; integer conversion truncates toward zero.'])]

Q['P1677-Q04']['difficulty']='easy'
# Readable prose, preserving literal source code, URLs, IDs and mathematical expressions.
manual={'counttofloat':'count to float','ofdistance':'of distance','theCPU':'the CPU','onCPU':'on CPU','withconf':'with conf ','usesmp4v':'uses mp4v','pathmax_objects_cpu.mp4':'path max_objects_cpu.mp4','Withprev_time':'With prev_time','equalsord(q)':'equals ord(q)','wristF/T':'wrist F/T','sustainedDC':'sustained DC','visibleRGB':'visible RGB','separateIR':'separate IR','ground-truth3D':'ground-truth 3D','theRGB':'the RGB','theI2C':'the I2C','reflectiveIR':'reflective IR','fromcount':'from count','cap.getcalls':'cap.get calls','loop-FPS':'loop FPS','theifbranch':'the if branch','inwhile':'in while','status==':'status ==','RISINGA':'RISING A','theLOWbranch':'the LOW branch','PPR600':'PPR 600','outofrange':'out of range'}
manual.update({'onA0':'on A0','convertV':'convert V','ofstatus':'of status','allRGB':'all RGB','Runcap.release':'Run cap.release','displayedFPS':'displayed FPS','withf':'with f','andd':'and d','usesB':'uses B','instead off×':'instead of f×','identifiableIR':'identifiable IR','haveN·m':'have N·m','long-termDC':'long-term DC','orsub-mN':'or sub-mN','forceF':'force F','WithM':'With M','ofHIGH':'of HIGH','causesLOW':'causes LOW','intoLOW':'into LOW','InitialHIGHtofirstLOW':'Initial HIGH to first LOW','subsequentHIGHtoLOW':'subsequent HIGH to LOW','Totalthree':'Total three','modelC':'model C','gapg':'gap g','withεandA':'with ε and A','fixedAandε':'fixed A and ε','Replaceg byg/2':'Replace g by g/2','0xFFand0x00':'0xFF and 0x00','stores+12°':'stores +12°','gives+37°':'gives +37°'})
manual.update({'toint':'to int','gives−':'gives −','Compute−':'Compute −','changes+':'changes +','along+x':'along +x','toward+y':'toward +y'})
def prose(s):
 for a,b in manual.items():s=s.replace(a,b)
 s=re.sub(r'(?<=[A-Za-z])(?=0x)',' ',s)
 # Protect common identifiers/code-like tokens before separating adjoining quantities/words.
 tokens={}
 def keep(m):
  k=f'ZZPROTECT{chr(65+len(tokens)//26)}{chr(65+len(tokens)%26)}ZZ';tokens[k]=m.group();return k
 s=re.sub(r'0x[0-9A-Fa-f]+|(?:I2C|DHT11|MPU6500|VL53L0X|YOLOv8|OpenCV|cv2|mp4v|A0|A1|Q\d+|P\d+|readTilt|lightValue|RangeStatus|RangeMilliMeter|INPUT_PULLUP|Serial\.\w+|cap\.\w+|out\.\w+|dht\.\w+|prev_time|fps_display|max_objects_cpu\.mp4)',keep,s)
 s=re.sub(r'(?<=[A-Za-z])(?=\d)', ' ',s)
 s=re.sub(r'(?<=\d)(?=[A-Za-zµΩ])', ' ',s)
 s=re.sub(r'(?<=[°%])(?=[A-Za-z])',' ',s)
 s=re.sub(r'([,;])(?=[A-Za-z])',r'\1 ',s)
 s=s.replace('2 D','2D').replace('3 D','3D').replace('6 D','6D').replace('° C','°C')
 s=re.sub(r'([,;])(?=[0-9−+])',r'\1 ',s)
 s=re.sub(r'\)(?=(?:m|N)(?:[·/]|$|\b))',') ',s)
 for k,v in tokens.items():s=s.replace(k,v)
 return s
for q in Q.values():
 for k in ['stem','subtopic']:q[k]=prose(q[k])
 q['assumptions']=[prose(s)for s in q['assumptions']]
 for o in q['options']:o['text']=prose(o['text'])
 sol=q['solution'];sol['optionExplanations']={k:prose(v)for k,v in sol['optionExplanations'].items()};sol['steps']=[prose(s)for s in sol['steps']]
 sol['justification']=' '.join(sol['optionExplanations'][k].removeprefix('Correct. ')for k in q['correctOptionIds']);sol['simpleExplanation']=sol['justification'];sol['misconceptions']=[v.removeprefix('Incorrect. ')for k,v in sol['optionExplanations'].items()if k not in q['correctOptionIds']]
 for f in sol['formulas']:
  f['assumptions']=[prose(s)for s in f['assumptions']]
  f['variables']={k:prose(v)for k,v in f['variables'].items()}
 for c in q['citations']:c['locator']=prose(c['locator'])
 if 'conflictResolution'in q:
  for k in ['sourceClaim','basis','method','scope']:q['conflictResolution'][k]=prose(q['conflictResolution'][k])
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
print('Refined',len(Q),'prefreeze drafts; no approval assigned')
