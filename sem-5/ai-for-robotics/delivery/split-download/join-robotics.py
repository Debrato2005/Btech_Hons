#!/usr/bin/env python3
"""Join the exact nine Robotics download parts. No network, extraction or app launch."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

MANIFEST = json.loads(r'''{
  "output": "ai-for-robotics-mcq.zip",
  "bytes": 157242751,
  "sha256": "aac4755a332ff9164ff18b4b59265c8120d2740e1e0fdce8605e4bad596e5709",
  "htmlSha256": "ef7ef2723af4c55176ed2f1cd8211182c0369224a6e8e71152320c5f34b0ac84",
  "parts": [
    {
      "name": "ai-for-robotics-mcq.zip.part001",
      "bytes": 19000000,
      "sha256": "92a77ce6e97b9da3e9541ca9fe0085efbeac62c5e52da6b4fda15b75ce4ad50f"
    },
    {
      "name": "ai-for-robotics-mcq.zip.part002",
      "bytes": 19000000,
      "sha256": "71e6ec383ad5b5dd22c001f405bbec792473309d6e898226d6da9ccf3c262233"
    },
    {
      "name": "ai-for-robotics-mcq.zip.part003",
      "bytes": 19000000,
      "sha256": "78b0d614e1fd008e495c044482c3b3cb7549d81d1cdc494c685ddfeba3014684"
    },
    {
      "name": "ai-for-robotics-mcq.zip.part004",
      "bytes": 19000000,
      "sha256": "9544d4ecb6ae230d8c177d2074b8988bf64eb390dc3e3c9af49809c569952546"
    },
    {
      "name": "ai-for-robotics-mcq.zip.part005",
      "bytes": 19000000,
      "sha256": "c3a45cfbfed8c2502607460e12bb0880b138ae2460ec56215221ad3e47cc62e3"
    },
    {
      "name": "ai-for-robotics-mcq.zip.part006",
      "bytes": 19000000,
      "sha256": "6e32fea78fe5a3a4883d1bc93511e68abf4235e8768a0538fcf2ae474dd40440"
    },
    {
      "name": "ai-for-robotics-mcq.zip.part007",
      "bytes": 19000000,
      "sha256": "d4fd641a8d01466e93271ee37bcb593063210f253f02a6fda94c6493c5b1ada2"
    },
    {
      "name": "ai-for-robotics-mcq.zip.part008",
      "bytes": 19000000,
      "sha256": "a811863239ad46eb0d25ac6143621f6b4801d1cbe7cc6ede8ac0bdd0d0912d4a"
    },
    {
      "name": "ai-for-robotics-mcq.zip.part009",
      "bytes": 5242751,
      "sha256": "18c7882e271223285fa07e424fd6cd7363e204524e4fe66372294e3c551e7cf8"
    }
  ]
}''')

def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()

def main():
    folder = Path(__file__).resolve().parent
    output = folder / MANIFEST["output"]
    if output.exists():
        raise RuntimeError("Output already exists; nothing was overwritten: " + str(output))
    for part in MANIFEST["parts"]:
        path = folder / part["name"]
        if not path.is_file():
            raise RuntimeError("Missing part: " + part["name"])
        if path.stat().st_size != part["bytes"] or digest(path) != part["sha256"]:
            raise RuntimeError("Wrong size or SHA-256: " + part["name"])
    created = False
    try:
        # Exclusive creation prevents overwriting any existing ZIP.
        with output.open("xb") as target:
            created = True
            for part in MANIFEST["parts"]:
                with (folder / part["name"]).open("rb") as source:
                    shutil.copyfileobj(source, target, 1024 * 1024)
        if output.stat().st_size != MANIFEST["bytes"] or digest(output) != MANIFEST["sha256"]:
            raise RuntimeError("Reconstructed ZIP failed size or SHA-256 verification.")
    except BaseException:
        if created:
            output.unlink()
        raise
    print("SUCCESS: all nine parts and the complete ZIP passed SHA-256 verification.")
    print(str(output))
    print("ZIP SHA-256: " + MANIFEST["sha256"])
    print("Now extract this ZIP yourself, then open ai-for-robotics-mcq.html.")
    print("This script has not extracted or opened any file.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as error:
        print("STOP: " + str(error), file=sys.stderr)
        sys.exit(1)
