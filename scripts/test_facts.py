#!/usr/bin/env python3
"""Integrity tests for data/facts/*.json.

Rules enforced:
- every provider in data/providers.json has a facts file, and no stray files exist;
- required fields are present and enumerations are valid;
- every evidence quote appears verbatim (whitespace-normalised) in the snapshot it names;
- every auth / rate_limit / cost / data_license value other than "not established"
  is backed by at least one evidence entry with that claim name;
- the probe_status recorded in facts equals the HTTP status in the captured meta.json.

Run: python3 scripts/test_facts.py -v
"""
import json, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH = {"none", "key-free", "key-approval", "key-paid", "oauth", "ip-allowlist", "unreachable"}
COST = {"free", "freemium", "paid", "institutional", "not established"}
CLAIMS = ("auth", "rate_limit", "cost", "data_license")
NE = "not established"
REQ = ["slug", "auth", "auth_note", "cost", "rate_limit", "data_license", "bulk_access",
       "probe_status", "probe_observation", "evidence", "not_established"]


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def jload(path):
    with open(path) as fh:
        return json.load(fh)


def providers():
    return jload(os.path.join(ROOT, "data", "providers.json"))


def facts():
    d = os.path.join(ROOT, "data", "facts")
    if not os.path.isdir(d):
        return {}
    return {f[:-5]: jload(os.path.join(d, f)) for f in sorted(os.listdir(d)) if f.endswith(".json")}


class T(unittest.TestCase):
    def test_exact_provider_coverage(self):
        want = {p["slug"] for p in providers()}
        have = set(facts())
        self.assertEqual([], sorted(want - have), "providers without facts")
        self.assertEqual([], sorted(have - want), "facts without provider")

    def test_fields_and_enums(self):
        bad = []
        for s, r in facts().items():
            for k in REQ:
                if k not in r:
                    bad.append(f"{s}: missing {k}")
            if r.get("slug") != s:
                bad.append(f"{s}: slug field is {r.get('slug')!r}")
            if r.get("auth") not in AUTH:
                bad.append(f"{s}: auth {r.get('auth')!r}")
            if r.get("cost") not in COST:
                bad.append(f"{s}: cost {r.get('cost')!r}")
            if not isinstance(r.get("evidence"), list):
                bad.append(f"{s}: evidence not a list")
        self.assertEqual([], bad)

    def test_quotes_verbatim(self):
        bad = []
        for s, r in facts().items():
            for e in r.get("evidence", []):
                q, sp = (e.get("quote") or "").strip(), e.get("snapshot") or ""
                if not q or not sp or e.get("claim") not in CLAIMS + ("probe", "bulk_access", "other"):
                    bad.append(f"{s}: malformed evidence {e.get('claim')!r}")
                    continue
                path = os.path.join(ROOT, sp)
                if not sp.startswith(f"data/snapshots/{s}/") or not os.path.exists(path):
                    bad.append(f"{s}: snapshot {sp!r} not under own dir or absent")
                    continue
                with open(path, encoding="utf-8", errors="replace") as fh:
                    txt = norm(fh.read())
                for frag in [f for f in re.split(r"\s*(?:\.\.\.|\u2026)\s*", q) if f.strip()]:
                    if norm(frag) not in txt:
                        bad.append(f"{s}: {frag[:70]!r} not in {sp}")
                        break
        self.assertEqual([], bad)

    def test_claims_have_evidence(self):
        bad = []
        for s, r in facts().items():
            have = {e.get("claim") for e in r.get("evidence", [])}
            for c in CLAIMS:
                v = r.get(c)
                if v and v != NE and c not in have:
                    bad.append(f"{s}: {c}={str(v)[:40]!r} has no evidence entry")
        self.assertEqual([], bad)

    def test_probe_status_matches_capture(self):
        bad = []
        for s, r in facts().items():
            m = jload(os.path.join(ROOT, "data", "snapshots", s, "meta.json"))
            if r.get("probe_status") != m["probe"]["status"]:
                bad.append(f"{s}: facts {r.get('probe_status')} vs capture {m['probe']['status']}")
        self.assertEqual([], bad)

    def test_snapshot_bytes_match_recorded_sha256(self):
        import gzip, hashlib
        bad = []
        for p in providers():
            s = p["slug"]
            d = os.path.join(ROOT, "data", "snapshots", s)
            m = jload(os.path.join(d, "meta.json"))
            caps = {k: m[k] for k in ("docs", "probe")}
            caps.update({"extra-" + k: v for k, v in m.get("extra", {}).items()})
            for name, cap in caps.items():
                path = os.path.join(d, name + ".gz")
                if not os.path.exists(path):
                    bad.append(f"{s}: {name}.gz absent")
                    continue
                with gzip.open(path) as gz:
                    raw = gz.read()
                if hashlib.sha256(raw).hexdigest() != cap["sha256"] or len(raw) != cap["bytes"]:
                    bad.append(f"{s}: {name} bytes differ from meta.json")
        self.assertEqual([], bad)

    def test_every_extra_snapshot_is_recorded(self):
        bad = []
        for p in providers():
            d = os.path.join(ROOT, "data", "snapshots", p["slug"])
            m = jload(os.path.join(d, "meta.json"))
            on_disk = {f[6:-3] for f in os.listdir(d) if f.startswith("extra-") and f.endswith(".gz")}
            if on_disk != set(m.get("extra", {})):
                bad.append(f"{p['slug']}: disk {sorted(on_disk)} vs meta {sorted(m.get('extra', {}))}")
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
