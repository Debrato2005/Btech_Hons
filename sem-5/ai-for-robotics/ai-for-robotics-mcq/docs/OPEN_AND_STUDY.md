# Open and use the offline study app

## Open

Download the HTML directly, or extract `ai-for-robotics-mcq.html` from the ZIP.
Open that HTML in an existing desktop browser.
The HTML contains the application, question bank, reviewed question inputs and both full source PDFs.
No server, account or Internet connection is needed by the application.
The ZIP's other files are instructions and optional verification tools, not runtime dependencies.

Actual offline browser acceptance is still pending in the supplied environment.
The file is large because it preserves the full source evidence; final load time and memory use have not been measured in a permitted browser.
Do not bypass a browser security warning or change system security settings.

## Practice

Use the sidebar or filters to select a week, lecture, topic or difficulty.
Choose one answer for a single-select question.
For a multiple-select question, choose every correct option and press **Submit answer**.
The solution explains the correct answer and each distractor.
Use the source buttons to inspect the cited physical PDF page.
Printed slide numbers and physical PDF page numbers are not interchangeable.
If the browser does not display embedded PDFs, save the source and open it in an existing offline PDF reader.

## Run an exam

Open **Exam simulator** and choose the scope, question count, duration and scoring.
The scoring is a practice setting, not an asserted official examination scheme.
Check the displayed settings, then start the exam.
Required diagrams and code premises remain available, but solutions and full source evidence stay hidden until submission.
The saved deadline does not restart on reload.
A source or input mismatch blocks the attempt rather than silently replacing its questions.

## Save progress

Open **Progress & backups** and export a JSON backup regularly.
Keep the backup outside the browser's storage.
Use backup import to move your study record to another browser or computer.
Browser file-origin storage can differ between applications and devices.
A storage warning means progress may not be saved; export a backup before closing the file.

## Print or export

Use the export menu for structured questions/results, a question paper, a separate answer key or worked solutions.
Use the browser's normal print-to-PDF option to save printable versions.
Actual printed layout and source readability still require the pending visual checks.

## Rebuild and review

Read `RESUME.md`, the recorded restrictions and `sources/README.md` first.
Restore source PDFs through the authorized source links and check their exact hashes.
Run `python3 scripts/record_validated_milestone.py` in the prepared project environment.
Do not use a wildcard command that includes browser runners.
Use `docs/FINAL_OFFLINE_QA.md` only in a permitted environment for the separate downloaded-file browser checks.

This material preserves source disagreements and qualifications.
Independent source review is not a guarantee against every possible error or a prediction of the examination.
