# Source inventory and recovery

This corpus contains **2,012 physical pages**: 1,953 in the lecture PDF and 59 in the separate assignment-solutions PDF. The stated 1,953-page expectation refers only to the lecture PDF. Current Drive folder inventory was checked on 19 October 2026 and contained these two PDFs.

## Durable files

- `manifest.json`: exact filenames, provider IDs, source URLs, file sizes, local SHA-256 fingerprints, measured page counts, provider modified timestamps, local paths and original-PDF assets.
- `lecture_map.json`: 60 chronological lectures and physical-page boundaries.
- `week_map.json`: 12 weeks, supported by the lecture PDF course outline at physical pages3–14 and matched lecture title pages.
- `assignment_map.json`: 12 weekly assignments, pagination separate from lectures.
- `page_maps/*.jsonl`: every physical page, canonical v1 slide records. Full extracted text lives at `localTextPath`; `text` remains empty here to avoid duplicating the corpus in mapping metadata. A builder can hydrate it when required.
- `visual_inspections.json`: actual source-hash-bound visual inspection records. Rendering and extraction do **not** create inspection credit. Re-running ingestion reapplies only matching-source records.
- `preview_manifest.json`: render count, size and settings, once rendering completes.

## Retrieval and reproduction

1. Use the connected Google Drive metadata action on the two `providerFileId` values in `manifest.json`. Confirm MIME type is `application/pdf` and record any new modified timestamp/size. List the source folder to catch additions.
2. Use connected Drive `fetch` with each canonical URL, `download_raw_file:true`, `include_base64:false`. These are stored PDFs, not native Docs exports. The response supplies an authenticated file reference/download URL. Never commit that temporary URL or credentials.
3. Materialize the returned bytes into `sources/raw/` using the filenames from the manifest. A supported download tool or `curl -L --fail` against the freshly returned URL works. The lecture PDF exceeds the generic 32MiB Sediment downloader limit, so streaming the returned authenticated URL is necessary if that limit still applies.
4. Install/reuse PyMuPDF and Pillow, then run `python scripts/ingest_sources.py`. Optional fresh references can be supplied with `--lecture-url` and `--assignment-url`; they are not saved. The script verifies PDF signatures for new downloads and recomputes all hashes and physical page counts.
5. Run `python scripts/ingest_sources.py --render --workers 4` for complete faithful WebP page previews. Default scale2.5 means 1800×1013 pixels for the common 720×405pt lecture pages; nonstandard page sizes preserve their own geometry. Quality88 balances readable equations/diagrams with size. Use original embedded PDFs when greater zoom is needed.
6. Compare hashes with `manifest.json` from the prior checkpoint. Changed hashes invalidate prior inspection/review bindings. Do not silently recycle old verification.

The raw PDFs, extracted corpus text and previews may be ignored by Git to control repository size. Their absence does not mean the source mappings are complete evidence: retrieve the exact sources before rebuilding an offline deliverable. A final app must embed readable evidence, not just online links or these metadata files.

## Pagination cautions

- Physical PDF pages are one-based and unique within each separate file.
- `lectureRelativePage` and `printedSlideNumber` are different. Printed numbers come from actual footer glyphs, never arithmetic.
- Fuzzy Logic Control is chronological `L40`, physical pages1231–1262, week8. Its title actually prints “Lecture Number45”. Preserve that misprint separately. The distinct Mapping/SLAM lecture `L45` starts at physical1405 and also prints45.
- Lecture physical page1380 (`L44`, relative page11) prints9. Preserve the printed9 rather than replacing it with11.
- Lecture physical pages27,56,610,641,1598 visibly have no printed slide number. Store `null`/`absent`, not inferred values.
- Assignment printed page numbers restart in each weekly section. All59 physical pages remain separately indexed.

## Review status

The ingestion worker visually inspected all60 lecture title pages, all12 week-outline slides, six pages with pagination anomalies, and all60 lecture-ending pages (59 thank-you pages and one bibliography). Title/outline/ending pages have specific administrative exclusions. Independent audit observations are also merged with their original inspector identities. Other visual inspection and concept coverage remain assigned to subject and coverage reviewers; source inventory is not proof of comprehensive question coverage.
