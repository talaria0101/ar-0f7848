# ar: academic and archival services with an API

An inventory of 69 academic, scholarly, library and web-archive services that expose an API (Wayback Machine CDX, OpenAlex, Crossref, arXiv, Europe PMC, Zenodo and others). Every value in the tables is tied to a captured page or a captured live API response.

## Contents

- `reports/01-inventory.md`: one table per category with auth model, cost, documented rate limit, data license and the result of one live probe.
- `reports/02-findings.md`: probe outcomes, access-model counts, what the pages did not say, rate-limit headers observed beside documented limits, and each provider's recorded gaps.
- `data/providers.json`: provider list with docs URL and probe URL (built by `scripts/build_providers.py`).
- `data/facts/<slug>.json`: one fact record per provider. Values other than `not established` carry verbatim quotes.
- `data/inventory.tsv`: the same facts as one flat table.
- `data/snapshots/<slug>/`: gzipped raw bytes, a text rendering, and `meta.json` (URL, final URL, HTTP status, bytes, sha256, UTC fetch time, rate-limit response headers) for the docs page, the probe, and any extra page captured as evidence.

## Method

1. Candidate list: 69 providers in six groups (web archives, libraries and archives, scholarly graphs and indexes, preprint/OA/repository services, biomedical and science data, publisher APIs), chosen for having a documented HTTP API.
2. Capture (`scripts/probe.py`): the docs page and one minimal anonymous API call per provider. A keyed API still gets a probe, because the refusal text is evidence of the gate.
3. Facts: for each provider, auth, cost, rate limit, data license, bulk route, probe observation. A value needs a verbatim quote from a snapshot of that provider. Where docs were a JS shell or blocked, a better page was captured with `scripts/snap.py`. Where nothing was found after several routes, the value is `not established` and the reason is written down.
4. Probe verdicts (`scripts/verdict.py`) are computed from the captured body, not from the HTTP status alone.
5. Reports are generated from the data (`scripts/build_reports.py`). No table cell is typed by hand.

## Re-verify

```sh
make probe     # recapture every docs page and probe (overwrites snapshots)
make reports   # rebuild inventory.tsv and both reports
make test      # integrity tests, warnings are errors
```

`scripts/test_facts.py` checks: every provider has a facts file; enumerations are valid; every evidence quote is verbatim in the snapshot it names, under that provider's own directory; every non-empty auth, rate limit, cost and license value has an evidence entry; `probe_status` equals the captured HTTP status; every snapshot's bytes match the recorded sha256; every extra snapshot on disk is recorded in `meta.json`. Each of these was shown to fail on a planted defect (altered quote, deleted evidence, wrong status, appended byte) and to pass on the real data.

## Limits

- All captures came from one machine behind an egress proxy that allows a subset of hosts. Four providers (`ia-scholar`, `memento`, `crossref-events`, `oabutton`) were unreachable from it, so their API behaviour is not observed. Unreachable here does not mean down.
- Four providers answered with a bot-wall page (`loc`, `gallica`, `dblp`, `openreview`). Their API behaviour is not observed either; auth rests on documentation where any was captured.
- One anonymous call per provider is not a test of limits, quotas or availability. A 429 (Semantic Scholar on the first probe, Google Books) describes that shared egress IP at capture time.
- A quote proves the page said it, not that the page is current or that the reading is right. Several documented limits disagree with response headers captured at the same time (see `reports/02-findings.md` section 4); both are shown.
- Cost and license are often not stated on captured pages. That is a capture gap, not evidence of no cost or no license.
- This is a technical inventory. It makes no claim that any use is permitted by a provider's terms.
- Some `auth: key-free` and `key-approval` values are the best-supported reading of a refusal plus a docs sentence; the provider's `auth_note` says which.

License: 0BSD (see `LICENSE`).
