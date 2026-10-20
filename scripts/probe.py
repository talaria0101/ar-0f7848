#!/usr/bin/env python3
"""Capture each provider's docs page and one live API call.

Writes data/snapshots/<slug>/{docs,probe}.gz (raw bytes), a .txt rendering
(HTML stripped) and meta.json (URL, final URL, HTTP status, content type,
bytes, sha256, UTC fetch time, rate-limit response headers).

Usage: python3 scripts/probe.py [slug ...]
"""
import concurrent.futures as cf, datetime, gzip, hashlib, html, json, os, re, sys, time
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "data", "snapshots")
UA = "ar-research/0.1 (public API inventory; +https://github.com/talaria0101/ar-0f7848)"
MAX = 1_500_000
RL = re.compile(r"(ratelimit|rate-limit|retry-after|x-api|quota)", re.I)
STRIP = re.compile(r"<(script|style|svg|noscript)\b.*?</\1>|<!--.*?-->", re.S | re.I)


def render(raw: bytes, ctype: str) -> str:
    s = raw.decode("utf-8", "replace")
    if "html" in ctype.lower() or s[:300].lstrip().lower().startswith(("<!doctype", "<html")):
        s = STRIP.sub(" ", s)
        s = re.sub(r"<[^>]+>", " ", s)
        s = html.unescape(s)
        s = re.sub(r"[ \t\r\f\v]+", " ", s)
        s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def get(url: str, accept: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "en"})
    t = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    hdrs = {}
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw, status, ctype, final = r.read(MAX + 1), r.status, r.headers.get("Content-Type", ""), r.geturl()
            hdrs = {k: v for k, v in r.headers.items() if RL.search(k)}
    except urllib.error.HTTPError as e:
        raw = e.read(MAX) if e.fp else b""
        status, ctype, final = e.code, (e.headers.get("Content-Type", "") if e.headers else ""), url
        hdrs = {k: v for k, v in (e.headers.items() if e.headers else []) if RL.search(k)}
    except Exception as e:  # noqa: BLE001
        raw, status, ctype, final = f"{type(e).__name__}: {e}".encode(), 0, "", url
    trunc = len(raw) > MAX
    raw = raw[:MAX]
    return {"url": url, "final_url": final, "status": status, "content_type": ctype,
            "bytes": len(raw), "truncated": trunc, "sha256": hashlib.sha256(raw).hexdigest(),
            "fetched_at": t, "ratelimit_headers": hdrs, "_raw": raw}


def work(p: dict) -> str:
    d = os.path.join(SNAP, p["slug"])
    os.makedirs(d, exist_ok=True)
    meta = {"slug": p["slug"], "name": p["name"]}
    for kind, url, acc in (("docs", p["docs"], "text/html,text/plain,*/*"), ("probe", p["probe"], p["accept"])):
        res = get(url, acc)
        raw = res.pop("_raw")
        with gzip.open(os.path.join(d, kind + ".gz"), "wb", compresslevel=9) as f:
            f.write(raw)
        txt = render(raw, res["content_type"])
        with open(os.path.join(d, kind + ".txt"), "w") as f:
            f.write(txt)
        res["text_bytes"] = len(txt)
        meta[kind] = res
        time.sleep(0.1)
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    return f"{p['slug']:22s} docs={meta['docs']['status']:3d} probe={meta['probe']['status']:3d} {meta['probe']['bytes']}B"


def main():
    provs = json.load(open(os.path.join(ROOT, "data", "providers.json")))
    want = set(sys.argv[1:])
    if want:
        provs = [p for p in provs if p["slug"] in want]
    with cf.ThreadPoolExecutor(8) as ex:
        for line in ex.map(work, provs):
            print(line, flush=True)


if __name__ == "__main__":
    main()
