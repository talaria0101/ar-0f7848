#!/usr/bin/env python3
"""Capture one extra page for a provider, as evidence for a fact.

Usage: python3 scripts/snap.py <slug> <label> <url> [accept]
Writes data/snapshots/<slug>/extra-<label>.{gz,txt} and records the capture
(URL, HTTP status, bytes, sha256, UTC time) under "extra" in meta.json.
"""
import gzip, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import SNAP, get, render

slug, label, url = sys.argv[1:4]
accept = sys.argv[4] if len(sys.argv) > 4 else "text/html,text/plain,application/json,*/*"
assert re.fullmatch(r"[a-z0-9-]+", label), "label must be [a-z0-9-]+"
d = os.path.join(SNAP, slug)
res = get(url, accept)
raw = res.pop("_raw")
with gzip.open(os.path.join(d, f"extra-{label}.gz"), "wb", compresslevel=9) as f:
    f.write(raw)
txt = render(raw, res["content_type"])
with open(os.path.join(d, f"extra-{label}.txt"), "w") as f:
    f.write(txt)
res["text_bytes"] = len(txt)
mp = os.path.join(d, "meta.json")
meta = json.load(open(mp))
meta.setdefault("extra", {})[label] = res
json.dump(meta, open(mp, "w"), indent=1)
print(f"{slug}/extra-{label}: HTTP {res['status']} {res['bytes']}B text={len(txt)}B sha256={res['sha256'][:12]}")
