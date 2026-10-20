#!/usr/bin/env python3
"""Classify what each captured probe returned, from the captured bytes.

data        HTTP 200 and the body parses as JSON, or is XML/CSV/text with records
unreachable status 0 (the sandbox proxy refused the connection)
challenge   a bot-wall page (Cloudflare "Just a moment", Anubis, reCAPTCHA, ChallengeRequired)
refused     401/403/429 with an API-level message (key missing, quota, IP denied, inactive)
other       anything else (wrong endpoint, SPA shell, 200 with an error body)

Rules read the body; the status code alone never yields "data".
"""
import gzip, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHALLENGE = re.compile(r"just a moment|anubis|protected by anubis|making sure you're not a bot|ChallengeRequiredError|recaptcha|Vercel Security", re.I)


def classify(slug):
    m = json.load(open(os.path.join(ROOT, "data", "snapshots", slug, "meta.json")))["probe"]
    body = gzip.open(os.path.join(ROOT, "data", "snapshots", slug, "probe.gz")).read().decode("utf-8", "replace")
    st = m["status"]
    if st == 0 or (st == 502 and m["bytes"] == 0):
        return "unreachable"
    if CHALLENGE.search(body[:4000]):
        return "challenge"
    if st in (401, 403, 429):
        return "refused"
    if st == 200:
        s = body.strip()
        try:
            j = json.loads(s)
        except ValueError:
            j = None
        if j is not None:
            low = json.dumps(j)[:600].lower()
            if isinstance(j, dict) and ("error" in j and len(j) <= 2):
                return "refused" if "denied" in json.dumps(j).lower() else "other"
            return "data" if low not in ("{}", "[]") else "other"
        lines = [l for l in s.splitlines() if l.strip()]
        if lines and all(l.lstrip().startswith("{") for l in lines[:2]):
            try:
                json.loads(lines[0])
                return "data"
            except ValueError:
                pass
        if m.get("truncated") and s[:1] in "[{":
            return "data"
        if s.startswith("<?xml") or s.startswith("<feed") or s.startswith("<response"):
            return "data" if "<error" not in s[:500].lower() else "other"
    return "other"


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    for p in json.load(open(os.path.join(ROOT, "data", "providers.json"))):
        print(f"{p['slug']:22s} {classify(p['slug'])}")
