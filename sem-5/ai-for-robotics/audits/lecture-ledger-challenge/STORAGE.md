# Generated audit ledger storage

The concept and page ledgers are stored as lossless .json.gz files to keep remote checkpoint transfers bounded. Decompress with Python gzip or a standard archive tool to recover the exact UTF-8 JSON. Their uncompressed local forms are ignored by Git. The companion audit scripts reproduce the ledgers from the question, review, source and concept records. A compressed snapshot is evidence for its recorded bank version, not a claim about later edits.
