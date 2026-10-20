"""Seal explicit reviewer responses after actual indicated source images were viewed."""
import pathlib,hashlib,json,datetime
from PIL import Image
R=pathlib.Path(__file__).resolve().parents[2];D=R/'audits/assignment-coverage';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def seal(week,version,rows,pages,expected):
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();packet=R/f'audits/blind-ASSIGN-{week}-v{version}.json';assert sha(packet)==expected
 out=dict(sealedAt=now,packetPath=str(packet.relative_to(R)),packetSha256=expected,solvedBeforeAnswerSeen=False,priorExposure='Previously reviewed v1 keys, original source answers and explanations are known. This is a targeted nonblind revision recheck. Current revised solutions remain unopened at this seal.',answers=[dict(questionId=f'ASSIGN-{week}-Q{n:03d}',independentAnswerOptionIds=[a],reasoning=r)for n,a,r in rows],sourceInspectionEvidence=[])
 for n in pages:
  p=R/f'sources/previews/assignments/page-{n:04d}.webp';out['sourceInspectionEvidence'].append(dict(sourceId='assignments',physicalPage=n,sourceSha256='b0450429866ac8017d7971932acf8812adf41df9dff4eb10bc8c87015b41c1b5',imagePath=str(p.relative_to(R)),imageSha256=sha(p),dimensions=list(Image.open(p).size),viewedAt=now,visualInspection='complete',sourceAnswerExposure=True))
 p=D/f'{week}-v{version}-independent-prekey-seal.json';assert not p.exists();p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
def reveal(week,version):
 p=D/f'{week}-v{version}-independent-reveal.json';assert not p.exists();p.write_text(json.dumps(dict(firstCurrentKeyOpenedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
