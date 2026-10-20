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


def providers():
    return json.load(open(os.path.join(ROOT, "data", "providers.json")))


def facts():
    d = os.path.join(ROOT, "data", "facts")
    if not os.path.isdir(d):
        return {}
    return {f[:-5]: json.load(open(os.path.join(d, f))) for f in sorted(os.listdir(d)) if f.endswith(".json")}


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
                txt = norm(open(path, encoding="utf-8", errors="replace").read())
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
            m = json.load(open(os.path.join(ROOT, "data", "snapshots", s, "meta.json")))
            if r.get("probe_status") != m["probe"]["status"]:
                bad.append(f"{s}: facts {r.get('probe_status')} vs capture {m['probe']['status']}")
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
