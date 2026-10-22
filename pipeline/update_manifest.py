"""
update_manifest.py — add raw-data checksums to pipeline/data-manifest.sha256 without ever dropping one.

data/ is gitignored and a CI runner starts with none of it, so the manifest cannot be rebuilt from the
directory: that would erase every historical entry. This merges instead. Existing lines are kept as they
are; each given file that exists is added; a file whose hash differs from its recorded one is a conflict
and aborts the run (raw archives are immutable provenance, so a changed one must be looked at, not
silently re-recorded). The file stays sorted by path, so a no-change run writes nothing.

Verify with, from the repo root:  sha256sum -c pipeline/data-manifest.sha256
"""

import hashlib
from pathlib import Path

ROOT = Path(__file__).parent.parent
MANIFEST = Path(__file__).parent / "data-manifest.sha256"


class ManifestConflict(Exception):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(manifest: Path = MANIFEST) -> dict[str, str]:
    entries = {}
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            if line.strip():
                digest, rel = line.split("  ", 1)
                entries[rel] = digest
    return entries


def update_manifest(paths, manifest: Path = MANIFEST, root: Path = ROOT) -> list[str]:
    """Merge the checksums of `paths` (files that exist) into the manifest. Returns the relative
    paths newly added. Raises ManifestConflict, writing nothing, if any recorded hash differs."""
    entries = read_manifest(manifest)
    added, conflicts = [], []
    for p in paths:
        p = Path(p)
        if not p.is_file():
            continue
        rel = p.resolve().relative_to(root.resolve()).as_posix()
        digest = sha256(p)
        if rel not in entries:
            entries[rel] = digest
            added.append(rel)
        elif entries[rel] != digest:
            conflicts.append(f"{rel}: manifest {entries[rel][:12]}… != file {digest[:12]}…")
    if conflicts:
        raise ManifestConflict("raw file differs from its recorded checksum:\n  " + "\n  ".join(conflicts))
    if added:
        manifest.write_text("".join(f"{entries[r]}  {r}\n" for r in sorted(entries)))
    return added
