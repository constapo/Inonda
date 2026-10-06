"""Document integrity: hash manifests so later tampering or AI-regenerated
'replacement' documents are detectable. Pair with C2PA for media where available."""
import hashlib
import json
import pathlib
from . import Finding


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(root):
    root = pathlib.Path(root)
    return {str(p.relative_to(root)): sha256(p) for p in sorted(root.rglob("*")) if p.is_file()}


def verify(root, manifest):
    now = build_manifest(root)
    out = []
    for name, digest in manifest.items():
        if name not in now:
            out.append(Finding("provenance.missing", "high", f"{name} missing", {}))
        elif now[name] != digest:
            out.append(Finding("provenance.modified", "high", f"{name} changed since manifest", {}))
    for name in now.keys() - manifest.keys():
        out.append(Finding("provenance.unexpected", "medium", f"{name} not in manifest", {}))
    return out


def dump(manifest):
    return json.dumps(manifest, indent=2, sort_keys=True)
