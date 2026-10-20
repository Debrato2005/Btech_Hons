# Bounded offline-artifact test review

Classification: static/unit checks only. No browser was launched; interaction, visual, PDF, download and file:// runtime verification remain separate pending work.

## Result

- Repaired scanner passes the five actual-artifact gates on the entire 280,893,510-byte HTML, without skipping any test. Elapsed time: 2.211 seconds. Peak process RSS: 306,944 KiB, including mapped file pages.
- Eleven isolated scanner regression tests pass. Python compilation and targeted diff whitespace checks pass.
- Files edited: tests/test_app_offline.py and new tests/test_artifact_scanner.py. No app, content bank, policy, asset or source file was edited.

## Material findings and repairs

1. The initial closing-tag regex accepted only a plain closing script tag. The active HTMLParser also ends raw text on forms such as `</script data-x>` and `</script/>`. A JSON payload followed by an external image and a second script could therefore hide the image from the gate. The scanner now derives the delimiter from the active parser and preserves DOM after all forms it recognizes.
2. A script-shaped string in a comment, quoted attribute or style is not necessarily a script element. The scanner now checks parser raw-text state before consuming a candidate body, preventing a false opener from buffering a later giant JSON payload.
3. Whole-file strict UTF-8 validation is retained through an incremental decoder. Invalid sequences in skipped JSON and sequences split across validation chunks are covered.
4. Full-artifact CSS checks still inspect every byte, including JSON outside the header/trailer. UTF-8 byte patterns preserve the earlier Unicode whitespace and case-insensitive I/S behavior; regressions compare against the original string expressions across every Unicode whitespace character.
5. JSON opening and closing tags still reach HTMLParser. DOM IDs, duplicate IDs and script src dependencies therefore remain checked. Non-JSON JavaScript is retained for the original service-worker expression.

## Scope preservation

The original language/viewport, duplicate DOM ID, resource dependency, full-artifact CSS and service-worker assertions are retained. File identity is not weakened: the LFS marker check now covers the first 2,048 bytes instead of the first 200, and the doctype/trailer must appear in the header/trailer buffers instead of merely anywhere. Unterminated scripts now fail explicitly. These are stricter checks, not exemptions.

The tests do not prove browser behavior. They also retain the original static gate's dependency vocabulary rather than claiming a complete browser network policy audit. mmap avoids whole-file Unicode/lowercase copies; non-JSON scripts still need memory proportional to the code being tested. A 4 MiB JSON fixture confirms that its payload never reaches HTMLParser, whose largest feed remains under 1 KiB for that fixture.

## Reproduction and receipts

- `python -m unittest discover -s tests -p 'test_app_offline.py' -v`
- `python -m unittest discover -s tests -p 'test_artifact_scanner.py' -v`
- `python -m py_compile tests/test_app_offline.py tests/test_artifact_scanner.py`
- `git diff --check -- tests/test_app_offline.py tests/test_artifact_scanner.py`

See results.json for artifact/source hashes and measured resource usage. See real-artifact-offline-tests.log and scanner-regressions.log for exact test output.
