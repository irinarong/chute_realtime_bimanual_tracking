"""Inventory the public NVIDIA assets from the image's completed download layer."""
import hashlib
import json
from pathlib import Path

root = Path("/opt/isaac_assets")
rows = []
for path in sorted(root.rglob("*")):
    if path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        rows.append(dict(path=str(path.relative_to(root)), bytes=path.stat().st_size,
                         sha256=digest.hexdigest()))
assert len(rows) == 277
print(json.dumps(dict(source="https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/",
                     files=rows), indent=2))
