"""Verbatim notebook premises, distinct from PDF pixels; never execute code."""
import hashlib
import json
from pathlib import Path
import re


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_path(root, name):
    if not isinstance(name, str) or not name.startswith(('sources/supplemental/', 'audits/review-snapshots/')) or ':' in name or '..' in Path(name).parts:
        return None
    target = (Path(root) / name).resolve()
    return target if any(target.is_relative_to((Path(root) / folder).resolve()) for folder in ('sources/supplemental', 'audits/review-snapshots')) else None


def load_artifacts(root, snippets):
    result = {}
    for snippet in snippets:
        if not isinstance(snippet, dict):
            continue
        for key in ('sourceArtifact', 'notebookArtifact'):
            name = snippet.get(key)
            path = file_path(root, name)
            if path is not None and path.is_file():
                try:
                    data = path.read_bytes()
                    result[name] = {'sha256': hashlib.sha256(data).hexdigest(), 'rawText': data.decode('utf-8')}
                except (UnicodeDecodeError, OSError):
                    pass
    return result


def lines(text, start, end):
    if type(start) is not int or type(end) is not int or not 1 <= start <= end:
        raise ValueError('Invalid one-based inclusive snippet line range.')
    # Physical source lines use only CR/LF; Unicode separators can be literal code data.
    values = re.findall(r'[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$', text)
    if end > len(values):
        raise ValueError('Snippet line range is outside the artifact/cell.')
    return ''.join(values[start-1:end])


def joined(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return ''.join(value)
    raise ValueError('Notebook source/output field is not exact text.')


def snippet_reasons(snippet, artifacts, root, *, check_files):
    try:
        s = snippet
        if not isinstance(s.get('id'), str) or not s['id'].strip() or s.get('kind') not in ('verbatim_source_code', 'verbatim_saved_output'):
            raise ValueError('Unsupported supplemental input identity/kind.')
        if not isinstance(s.get('authorId'), str) or not s['authorId'].strip() or not isinstance(s.get('revisionAuthors', []), list) or any(not isinstance(a, str) or not a.strip() for a in s.get('revisionAuthors', [])):
            raise ValueError('Supplemental input authorship is missing or malformed.')
        output = s['kind'] == 'verbatim_saved_output'
        if s.get('language') != ('text' if output else 'python') or s.get('notebookRepresentation') not in ('verbatim', 'output_stripped'):
            raise ValueError('Supplemental language or notebook representation is missing/invalid.')
        if output and s['notebookRepresentation'] != 'verbatim':
            raise ValueError('Saved output requires a verbatim notebook representation.')
        for name, key in [('sourceArtifact', 'sourceSha256'), ('notebookArtifact', 'notebookSha256')]:
            path = file_path(root, s.get(name)); artifact = artifacts.get(s.get(name), {})
            if path is None or not re.fullmatch('[a-f0-9]{64}', s.get(key, '')) or artifact.get('sha256') != s[key] or not isinstance(artifact.get('rawText'), str) or hashlib.sha256(artifact['rawText'].encode()).hexdigest() != s[key]:
                raise ValueError('Supplemental exact local-file hash is missing/stale: ' + name)
            if check_files and (not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != s[key]):
                raise ValueError('Supplemental local source bytes changed: ' + name)
        status = s.get('upstreamPinStatus')
        if status in ('pinned', 'commit_only'):
            if not re.fullmatch('[a-f0-9]{40}', s.get('upstreamCommit') or '') or (status == 'pinned' and not re.fullmatch('[a-f0-9]{40}', s.get('upstreamGitBlobSha') or '')) or (status == 'commit_only' and s.get('upstreamGitBlobSha') is not None) or not isinstance(s.get('sourceUrl'), str) or not s['sourceUrl'].startswith('https://github.com/') or '/blob/' + s['upstreamCommit'] + '/' not in s['sourceUrl']:
                raise ValueError('Pinned upstream provenance lacks exact commit/blob URL identity.')
        elif status != 'local_only' or s.get('upstreamCommit') is not None or s.get('upstreamGitBlobSha') is not None:
            raise ValueError('Unpinned supplemental evidence must explicitly use local_only and null upstream identities.')
        if not isinstance(s.get('transformation'), str) or not s['transformation'].strip():
            raise ValueError('Supplemental transformation qualification is missing.')
        notebook = json.loads(artifacts[s['notebookArtifact']]['rawText'])
        index = s.get('cellIndexZeroBased')
        if type(index) is not int or index < 0 or not isinstance(notebook.get('cells'), list) or index >= len(notebook['cells']):
            raise ValueError('Notebook cell index is outside the exact artifact.')
        cell = notebook['cells'][index]
        if s.get('cellId') != (cell.get('id') if 'id' in cell else cell.get('metadata', {}).get('id')) or (s.get('cellId') is not None and not isinstance(s['cellId'], str)):
            raise ValueError('Notebook cell ID does not match the exact indexed cell.')
        if output:
            oi, field = s.get('notebookOutputIndex'), s.get('notebookOutputField')
            if cell.get('cell_type') != 'code' or type(oi) is not int or oi < 0 or oi >= len(cell.get('outputs', [])) or field not in ('text', 'data.text/plain'):
                raise ValueError('Invalid historical saved-output selector.')
            value = cell['outputs'][oi]
            selected = value.get('text') if field == 'text' else value.get('data', {}).get('text/plain')
        else:
            if cell.get('cell_type') != 'code' or s.get('notebookOutputIndex') is not None or s.get('notebookOutputField') is not None:
                raise ValueError('Code premises must select only a code cell source, never saved output.')
            selected = cell.get('source')
        expected = lines(joined(selected), s.get('cellLineStart'), s.get('cellLineEnd'))
        if s.get('text') != expected or not re.fullmatch('[a-f0-9]{64}', s.get('textSha256', '')) or hashlib.sha256(expected.encode()).hexdigest() != s['textSha256']:
            raise ValueError('Supplemental text is not the exact selected notebook substring.')
        if s['sourceArtifact'] == s['notebookArtifact']:
            if s.get('lineStart') is not None or s.get('lineEnd') is not None:
                raise ValueError('Notebook-as-source uses cell ranges, not misleading global code line numbers.')
        elif output or lines(artifacts[s['sourceArtifact']]['rawText'], s.get('lineStart'), s.get('lineEnd')) != expected:
            raise ValueError('Supplemental text differs from its extracted source-file line range.')
        return []
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as error:
        return [str(error)]


def prepare(snippets, artifacts, root, *, check_files):
    errors, bindings, by_id = {}, {}, {}
    if not isinstance(snippets, list) or not isinstance(artifacts, dict):
        return {}, {}, {'*': ['Malformed supplemental inputs/artifacts.']}
    for s in snippets:
        if not isinstance(s, dict):
            errors['*'] = ['Malformed supplemental input record.']; continue
        sid = s.get('id')
        if sid in by_id:
            errors[sid] = ['Duplicate supplemental input ID.']; continue
        by_id[sid] = s
        errors[sid] = snippet_reasons(s, artifacts, root, check_files=check_files)
        bindings[sid] = {'id': sid, 'inputSha256': digest(s), 'rawJSON': canonical(s)}
    return by_id, bindings, errors
