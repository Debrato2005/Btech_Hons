"""Read legacy and lazy embedded payloads with bounded asset decoding."""
import base64
import gzip
import hashlib
import json
import mmap
from pathlib import Path


def bank_bytes(data):
    for kind in ('application/json', 'application/gzip'):
        marker = f'<script type="{kind}" id="bank-data">'.encode()
        start = data.find(marker)
        if start >= 0:
            start += len(marker)
            raw = data[start:data.find(b'</script>', start)]
            return gzip.decompress(base64.b64decode(raw, validate=True)) if kind.endswith('gzip') else raw
    raise ValueError('Missing embedded bank.')


def assets(data):
    marker = b'<script type="application/json" id="asset-data">'
    start = data.find(marker)
    if start < 0:
        raise ValueError('Missing embedded asset metadata.')
    start += len(marker)
    end = data.find(b'</script>', start)
    if end < 0:
        raise ValueError('Unterminated asset metadata.')
    cursor = start + 1
    while cursor < end and data[cursor:cursor + 1] != b'}':
        if data[cursor:cursor + 1] == b',':
            cursor += 1
        header = data.find(b':{', cursor, end) + 1
        if header <= 0:
            raise ValueError('Invalid embedded asset entry.')
        # Metadata can contain literal braces in quoted descriptions.
        pos, quoted, escaped, depth = header, False, False, 0
        while pos < end:
            char = data[pos]
            if quoted:
                if escaped:
                    escaped = False
                elif char == 92:
                    escaped = True
                elif char == 34:
                    quoted = False
            elif char == 34:
                quoted = True
            elif char == 123:
                depth += 1
            elif char == 125:
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        entry_end = pos + 1
        encoded_at = data.find(b'"data":"', header, entry_end)
        if encoded_at >= 0:
            encoded_at += 8
            encoded_end = data.find(b'"', encoded_at, entry_end)
            metadata = json.loads(data[header:encoded_at] + b'"}')
        else:
            metadata = json.loads(data[header:entry_end])
            marker = f'<script type="application/octet-stream" id="{metadata["payloadId"]}">'.encode()
            encoded_at = data.find(marker)
            if encoded_at < 0:
                raise ValueError('Missing payload: ' + metadata['id'])
            encoded_at += len(marker)
            encoded_end = data.find(b'</script>', encoded_at)
        if encoded_end < encoded_at:
            raise ValueError('Unterminated asset payload.')
        yield metadata, encoded_at, encoded_end
        cursor = entry_end


def decoded_chunks(data, start, end):
    for offset in range(start, end, 4 * 16384):
        yield base64.b64decode(data[offset:min(offset + 4 * 16384, end)], validate=True)


def recover(html, root):
    root = Path(root).resolve()
    results = []
    with Path(html).open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
        bank = bank_bytes(data)
        parsed = json.loads(bank)
        # A production projection cannot replace the canonical review bank.
        target = root / ('dist/recovered-practice-bank.json' if parsed.get('scope') == 'practice-only' else 'data/bank.json')
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if json.loads(target.read_bytes()) != parsed:
                raise ValueError('Existing bank differs: ' + str(target))
        else:
            target.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        for a, start, end in assets(data):
            target = (root / a['path']).resolve()
            if not target.is_relative_to(root):
                raise ValueError('Asset path escapes project.')
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            # Existing source bytes must agree before any replacement.
            if target.exists():
                with target.open('rb') as f:
                    for chunk in iter(lambda: f.read(1024 * 1024), b''):
                        digest.update(chunk)
                if digest.hexdigest() != a['sha256']:
                    raise ValueError('Existing asset differs: ' + str(target))
            else:
                temporary = target.with_suffix(target.suffix + '.recovering')
                with temporary.open('wb') as f:
                    for chunk in decoded_chunks(data, start, end):
                        digest.update(chunk)
                        f.write(chunk)
                if digest.hexdigest() != a['sha256']:
                    temporary.unlink()
                    raise ValueError('Recovered asset hash differs: ' + a['id'])
                temporary.replace(target)
            results.append({'id': a['id'], 'sha256': digest.hexdigest()})
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = recover(args.html, args.root)
    print(json.dumps({'recoveredAssets': len(result), 'hashesMatch': True}))
