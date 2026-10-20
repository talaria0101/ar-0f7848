# 02 Findings

All counts are over the 69 providers in `data/providers.json`, computed by `scripts/build_reports.py`. Capture date and machine are in each `meta.json` (`fetched_at`).

## 1. What one anonymous call returned

| Verdict | Count | Providers |
|---|---|---|
| data | 45 | wayback-cdx, wayback-availability, ia-advancedsearch, ia-metadata, commoncrawl, arquivo-pt, software-heritage, europeana, hathitrust, openlibrary, gutendex, smithsonian, wikipedia, wikidata, openalex, crossref, datacite, semanticscholar, core, arxiv, pubmed-eutils, europepmc, pmc-idconv, unpaywall, doaj, openaire, biorxiv, hal, orcid, ror, inspirehep, opencitations, orkg, zbmath, scielo, jstage, zenodo, figshare, osf, dryad, dataverse, gbif, clinicaltrials, pubchem, scite |
| refused | 13 | wayback-spn2, dpla, googlebooks, base, nasa-ads, altmetric, oapen, springer, elsevier, ieee, wos, lens, trove |
| challenge | 4 | loc, gallica, dblp, openreview |
| unreachable | 4 | ia-scholar, memento, crossref-events, oabutton |
| other | 3 | nara, mendeley-data, dimensions |

`data` = HTTP 200 and a parseable record body. `refused` = 401/403/429 with an API-level message. `challenge` = bot-wall page. `unreachable` = the capture machine's egress proxy refused the host (status 0 or an empty 502); this says nothing about whether the service is up. `other` = wrong endpoint, SPA shell or 200 with an error body.

## 2. Access model (from documentation or refusal text)

| auth | Count |
|---|---|
| none | 44 |
| key-free | 9 |
| key-approval | 8 |
| key-paid | 1 |
| ip-allowlist | 1 |
| unreachable | 6 |

Keyless providers whose live probe was NOT `data` (their `none` rests on documentation, not on an observed response): loc (challenge), mendeley-data (other).

## 3. What the pages did not say

| Claim | Providers with a documented value | Providers where it is not established |
|---|---|---|
| auth | 63 | 6 |
| rate_limit | 33 | 36 |
| cost | 24 | 45 |
| data_license | 29 | 40 |

A page that did not state a value is a gap in the capture, not evidence the provider has no limit, cost or license. Every `not established` has its reason in the provider's `not_established` field in `data/facts/<slug>.json`.

## 4. Rate-limit headers observed on the probe response

Headers matching `ratelimit|retry-after|quota` on the probe response, beside the limit the documentation was captured stating. The probe ran from one shared egress IP, so these describe that path, not every client.

| Provider | Observed headers | Documented (captured) |
|---|---|---|
| arquivo-pt | X-RateLimit-Limit=250, X-RateLimit-Reset=t=1792459889215718, RateLimit-Limit=250, RateLimit-Reset=60, X-RateLimit-Policy=250;w=60, X-RateLimit-Scop... | Rate limit listed as 250 a 400 on dados.gov.pt (unit and window not stated there) |
| software-heritage | X-Ratelimit-Limit=120, X-Ratelimit-Remaining=119, X-Ratelimit-Reset=1792463490 | 120 requests per hour for anonymous users, 1200 per hour for authenticated users (per origin IP for anonymous). |
| europeana | ratelimit="project";r=991579;t=1711, ratelimit-policy="project";q=1000000;w=3600 | not established |
| smithsonian | X-Ratelimit-Limit=10, X-Ratelimit-Remaining=9 | api.data.gov defaults: 1,000 requests per hour per key; DEMO_KEY 30 per IP per hour and 50 per IP per day. Probe resp... |
| openalex | X-RateLimit-Cost-USD=0.0001, X-RateLimit-Credits-Used=1, X-RateLimit-Limit=1000, X-RateLimit-Limit-USD=0.1, X-RateLimit-Onetime-Remaining=0, X-Rate... | Anonymous: shared $0.10 per day per IP; free key: $1 per day, resets midnight UTC; probe header X-RateLimit-Limit 100... |
| core | x-ratelimit-limit=10, x-ratelimit-remaining=9, x-ratelimit-retry-after=2026-10-20T01:32:01+0000 | One batch request or five single requests per 10 seconds; registered users get a faster rate, VIP rate on request. |
| pubmed-eutils | X-Ratelimit-Limit=3, X-Ratelimit-Remaining=2 | 3 requests/second per IP without an API key; 10 requests/second per key with one (NCBI Insights post). |
| openaire | x-ratelimit-used=2, x-ratelimit-limit=7199 | Unauthenticated up to 60 requests per hour; authenticated up to 7200 requests per hour. |
| altmetric | X-HourlyRateLimit-Limit=720, X-HourlyRateLimit-Remaining=719, X-DailyRateLimit-Limit=1200, X-DailyRateLimit-Remaining=1199 | not established |
| openreview | x-ratelimit-limit=180, x-ratelimit-remaining=179, x-ratelimit-reset=1792459962, ratelimit-policy=180;w=60, ratelimit-limit=180, ratelimit-remaining... | not established |
| zenodo | x-ratelimit-limit=30, x-ratelimit-remaining=29, x-ratelimit-reset=1792459964, retry-after=59 | not established |
| scite | RateLimit-Reset=9, X-RateLimit-Limit-Minute=60, X-RateLimit-Remaining-Minute=59, RateLimit-Limit=60, RateLimit-Remaining=59 | Without an Authentication Token: up to 10 requests per second, up to 40 requests per minute; tallies and papers endpo... |

Where the two disagree, the capture shows both and neither is overridden: documentation can be stale and a header can describe a different tier than the one the docs name. `openaire` (header 7199 on an anonymous call, docs say 60 per hour anonymous), `scite` (header 60 per minute, docs 40 per minute without a token) and `smithsonian` (header 10, docs 30 per hour for DEMO_KEY) disagree in this capture.

## 5. Providers that returned 200 but not records

- `nara`: The probe returned HTTP 200 with a 5454-byte text/html page (Swagger/SPA shell) that rendered to empty text, so no JSON search result was captured.
- `base`: Probe returned HTTP 200 with a JSON body {"error": "Access denied for IP address ... and user agent ar-research/0.1 ..."}, i.e. an application-level refusal, no search results.

## 6. Per-provider limits recorded by the evidence pass

Each of these is a `not_established` field quoted from `data/facts/`:

- `wayback-cdx`: Numeric rate limits, data license and cost of the hosted web.archive.org service are not stated in the CDX README. Extra pages tried: archive.org/about/terms.php (Anubis/JS shell, 93 bytes), archive.org/developers/wayback-cdx-server.html (404), archive.org/developers/index-apis.html (only a table...
- `wayback-availability`: Rate limits, data license and cost are not stated in the docs page (last updated Sept 2013 per page). archive.org/about/terms.php returned an Anubis/JS shell (93 bytes) with no terms text.
- `wayback-spn2`: Whether the account/keys are free is not stated in the SPN2 docs (account sign-up page archive.org returned an Anubis/JS shell, 93 bytes; spn-api details page 404); key-free is inferred from self-serve S3 key page only. Cost, data license, and concurrent-session number not established.
- `ia-advancedsearch`: No documented numeric rate limit, license of returned metadata, or cost statement on the captured advancedsearch page or the Bots page; no bulk dump route documented (the captured Tools and APIs page was also checked).
- `ia-metadata`: No numeric rate limit, metadata license, or explicit cost statement found in the metadata docs, Read page or Bots page; no bulk route documented.
- `ia-scholar`: Read-access auth (probe host api.fatcat.wiki and guide.fatcat.wiki blocked by sandbox egress, 502); cost; rate limits (none in captured fatcat guide pages); whether Bearer tokens are free.
- `commoncrawl`: No numeric rate limit is documented (only 'do not overload the URL index server'). No data license stated: Terms of Use say Crawled Content may be subject to the separate terms of its owners, no CC0/CC-BY-style grant was found in docs, terms, FAQ or index page.
- `memento`: Auth, cost, rate limits, data license and bulk access of the Time Travel API: timetravel.mementoweb.org is unreachable from this sandbox (502 proxy, DNS did not resolve) for docs, probe and https retry; mementoweb.org/depot and the GitHub raw README guesses returned 404; mementoweb.org/guide/ gav...
- `arquivo-pt`: Data license of archived content/metadata not found in wiki, OpenAPI, FAQ or dados.gov.pt (arquivo.pt/termsofuse and the CDX wiki page snapshot returned 404/empty form). Rate limit unit/window not in docs text; the probe response headers (in meta.json, not a text snapshot) show X-RateLimit-Policy...
- `software-heritage`: Cost/pricing statement (no free/paid wording captured); license of API metadata (docs only say archived source files keep their own licenses); the api-terms-of-use page on softwareheritage.org was unreachable from the sandbox (HTTP 0 proxy error, extra-terms).
- `loc`: Cost statement and data license/rights of returned metadata (not in captured pages; rights are per item). Live anonymous access unverified because the probe got a Cloudflare challenge (403). URL of the MARC Open Access dataset not captured.
- `europeana`: Numeric rate limits (docs captured give only a fair use policy and say personal key limits were reduced until April 2026; the numeric policy appears only in a response header, not in docs); explicit cost/pricing wording; the original docs page (pro.europeana.eu/page/search) and get-api page retur...
- `hathitrust`: All official hathitrust.org docs pages (docs, bibliographic-api, old.www bib_api/data_api, integrate-records, hathifiles) returned a Cloudflare 403 block page from this sandbox, so cost, documented rate limits, data license and bulk dump URLs are not established from official text. A third-party ...
- `dpla`: pro.dp.la pages (api-codex, policies, terms-of-service, bulk-download) and dp.la guides returned CloudFront 403 'Request blocked' from this sandbox, so rate limits, data license and bulk download route are not established. The key-request text comes from the old dpla/platform GitHub README and an...
- `openlibrary`: No explicit named license (CC0 etc.) for the data was found on the captured pages. Cost of the API is inferred from free anonymous access and 'free' dumps wording; docs state no price page. Docs say violations may bring blocking but give no numeric quota beyond the two per-second figures.
- `googlebooks`: Numeric default quota and pricing are not in the captured docs (extra-quota snapshot, the getting_started page, is a generic page without them); whether a key costs anything is not stated. Content license of returned metadata not stated (page CC BY 4.0 licence covers the docs page only). No bulk ...
- `gutendex`: No rate limit, cost statement, or data license for the returned metadata is in the docs or GitHub README (the repo MIT license covers the code, not the data). Anonymous access worked, but no cost is documented.
- `gallica`: Whether SRU needs auth: the live endpoint returned a 403 challenge to the sandbox, and the captured docs (extra-doc, api.bnf.fr/api-gallica-de-recherche) do not mention a key. Rate limits, cost and data license not stated; the licence page (gallica.bnf.fr/conditions-dutilisation..., extra-terms) ...
- `nara`: Cost/pricing is not stated in captured text. Whether key approval is automatic or discretionary is not stated (key-approval chosen because issuance is by email request to engineers). docs.txt and probe.txt are empty JS shells; the OpenAPI JSON route (extra-api) also rendered to 10 bytes. No live ...
- `smithsonian`: Cost is not stated in captured text. The Smithsonian-specific limit is not documented in captured text (api.data.gov generic defaults quoted; the Smithsonian service may override them). docs.txt is a 'Loading...' JS shell and si.edu/openaccess/devtools returned 403 (challenge), so the Smithsonian...
- `wikipedia`: Numeric limits for anonymous reads are not documented (docs say none hard). Licence of other content types (images, Wikidata) not covered. Cost 'free' rests on the Terms of Use statement about hosting content free of charge.
- `wikidata`: No numeric request-rate limit found in the captured Data_access, User-Agent policy or api.wikimedia.org rate-limits pages.
- `openalex`: Whether anonymous access remains available beyond the $0.10 shared daily budget; per-second request caps not captured.
- `crossref`: Numeric rate limits for the polite pool and exact license name; the Metadata Plus fee; URL of the annual public data file not captured.
- `datacite`: Cost of API use: no captured page states pricing or says the public API is free. CC0 is documented for the Public Data File metadata; no captured page states the licence of API responses explicitly. OAI-PMH guide page (guessed .md URL) returned 404; DataCite terms page returned 403 from the sandb...
- `semanticscholar`: The captured docs.txt (api-docs) is a 103-byte SPA shell; limits and licence come from the product overview page and API License Agreement. Which licence applies to which endpoint's data is not stated in captured text (only 'such as CC BY-NC or ODC-BY'). Whether API key issuance is automatic or n...
- `core`: Exact licence of API-returned metadata: Terms say ODC-By applies to specific datasets and that other datasets and the API need a licence, but the captured text does not give the API data licence by name. The rate-limit detail page (api.core.ac.uk/docs/v3, an SPA) captured only 22 bytes, so the re...
- `arxiv`: Nothing material; Amazon S3/Kaggle full-text terms were not read in detail.
- `pubmed-eutils`: No formal data license: only a statement that NLM does not claim copyright on abstracts (publishers or authors may); FTP terms are in a README.txt not captured. The configured docs page (NBK25497) was a reCAPTCHA 'Checking your browser' challenge, so the official usage-guidelines page was not cap...
- `europepmc`: Cost, rate limits, data license and bulk routes: europepmc.org pages (RestfulWebService, downloads, Copyright, about, Help) returned HTTP 403 with a 16-byte challenge body (Cloudflare-style challenge to the sandbox, not an outage); ebi.ac.uk/europepmc/webservices/rest/ root and openapi.json retur...
- `pmc-idconv`: Cost (no statement on API pricing), numeric rate limit (docs captured give none; only 200 IDs per request), and license of the returned ID mappings (copyright notice covers articles, not the API output).
- `unpaywall`: Cost, rate limit, data license, bulk/snapshot route, and whether an email param is mandatory: unpaywall.org/products/api (and /api/v2, /products, /faq, /data-format, oadoi.org/api/v2) is a JS SPA shell whose captured text is 9 bytes; GitHub README via raw and api.github.com returned empty bodies;...
- `doaj`: Cost/pricing of API use is not stated on captured pages (docs, FAQ, terms, data-dump page); whether anonymous rate limit differs from keyed is not stated; OAI-PMH endpoint URL not captured.
- `openaire`: Nothing major. Note: the probe response headers reported x-ratelimit-limit 7199 (meta.json only, not in a snapshot text), which differs from the documented 60/hour anonymous figure; not reconciled.
- `base`: Cost, rate limits and the license of returned data are not stated in the captured docs (the interface guide is a PDF not captured). The main docs page snapshot (docs.txt) is an Anubis proof-of-work challenge page, not content; content came from extra-apidoc and extra-oai. Probe denial text mentio...
- `biorxiv`: Rate limits are not documented in the API page, TDM page or FAQ captured. The 'free' cost rests on the site statement about free access to articles; the API page itself has no pricing statement. Data license is per record, no single license for the metadata as a whole.
- `hal`: Cost, numeric rate limit and a named data license were not found in the captured search docs, OAI page, API index or doc.hal.science home (tried docs.txt, extra-oai, extra-swagger, extra-docs; legal-notice, hal-data and droits URLs returned 404). The OAI page only says metadata is usable within i...
- `orcid`: Cost and a numeric request rate limit were not found (tried docs.txt, extra-pubtos, extra-pubdata; tos, limits, faq, public-data-file and usage-limits URLs returned 404). The CC0 license is documented for the Public Data File, not stated for API responses. Docs say search needs a /read-public tok...
- `ror`: A separate terms page (ror.org/about/terms) was not captured: it returned HTTP 429 (Vercel Security Checkpoint challenge). The meta.json docs capture shows x-ratelimit-limit 100 headers, which differs from the documented 2000 per 5 minutes; not resolved. The CC0 license is documented for the data...
- `inspirehep`: Cost/pricing is not stated in the docs (anonymous access works, but no explicit free statement captured). No bulk dump or OAI-PMH route is mentioned in the captured docs.
- `nasa-ads`: Docs page https://ui.adsabs.harvard.edu/help/api/ returned 202 with empty text (challenge); evidence comes from the GitHub README and terms page. Cost is not stated explicitly (key is self-serve). The actual default quota is only an example header value (5000/day), not a stated policy. Data licen...
- `dblp`: Search API auth, cost and rate limits: dblp.org docs/FAQ/terms pages and the probe all returned an Anubis challenge (202) to the sandbox; routes tried: FAQ page, licence FAQ, GitHub raw docs (404). Challenge is not an API outage.
- `opencitations`: Nothing material. Cost is inferred from the free token statement and the CC0 data statement; no pricing page exists in the capture.
- `crossref-events`: Auth, cost, rate limit and data license: the probe host is blocked by sandbox egress (502, not evidence the API is down), the docs URL captured only a redirect to https://www.crossref.org/deprecated/, and the event-data terms-of-use and GitHub docs URLs returned 404. The deprecation page says the...
- `altmetric`: Cost (no pricing page; docs mention a commercial key and a subscription but no free tier is stated); numeric rate limits (docs only say to read X-HourlyRateLimit-Limit and X-DailyRateLimit-Limit headers; meta.json recorded 720 hourly and 1200 daily on the 403 response, but that is not in a text s...
- `orkg`: Cost, rate limits, data license and bulk dump not established. The documented swagger-ui URL returned 404, api-docs paths returned 404, the GitLab docs host returned a 403 challenge, raw GitHub README paths returned 404, and the orkg.org about/help pages are a JavaScript shell with no body text.
- `oabutton`: Auth, cost, rate limit and license not established: the API host was unreachable from this sandbox (proxy 502, not evidence of outage) and the provider's own page states the Open Access Button was retired on 2025-11-18, with Unpaywall recommended instead. The OA.Works blog snapshot (extra-blog) h...
- `oapen`: REST API (/rest) refused this sandbox address (403) so its output, auth model beyond that refusal, and rate limits are unknown; the 403 may be a sandbox-IP block rather than a documented allowlist. No documentation of cost or API rate limits found (docs page only gives UI export caps of 500/15000...
- `zbmath`: Cost statement not found in captured pages. Numeric rate limits not found: OpenAPI text only says 'Each API endpoint's documentation may detail more specific usage limits'. The terms page is an unrendered agreement stub (122 bytes), so terms text was not captured. Some records carry a different l...
- `openreview`: Whether sign-up is free is not stated in captured pages (cost not established); signup page notes public-email domains can take up to 2 weeks to activate. Rate limit: meta.json shows response headers ratelimit-policy 180;w=60 on the challenge response, but no captured docs page states a limit. Da...
- `scielo`: Documented rate limit, cost statement, and metadata-specific license not found. Configured docs URL github.com/scieloorg/articlemeta is a 404 (status 404 in meta.json); the repo scieloorg/articles_meta README only covers docker deployment. Tried articlemeta.scielo.org /api/v1/, /api/v1/docs, /oai...
- `jstage`: Cost statement, numeric rate limit and data license were not found: the configured docs URL returns 404, the English WebAPI page has no limits or license, and the Japanese manual PDF capture (extra-manual) is undecoded binary. Terms of Use page (Japanese only) not captured. Meaning of WARN_002 no...
- `zenodo`: Numeric rate limit is not in any captured page (docs only list HTTP 429 for rate limiting; the probe response headers in meta.json show x-ratelimit-limit 30 with retry-after 59, but headers are not in a snapshot text file). Whether the service stays free for downloads at volume is not stated.
- `figshare`: Cost and data license of returned metadata are not stated in the captured docs; the terms-of-service URL tried (info.figshare.com user-guide) returned 404 and no other terms page was captured.
- `osf`: Cost of API use stated only as 'shares with the public free of charge any data marked as Public' in terms, not an API pricing statement, so cost left unestablished. developer.osf.io docs.txt is a 23-byte SPA shell (JS-rendered); rate limits come from source code settings, not documentation prose,...
- `dryad`: Numeric rate limits (docs only say API accounts get 'higher rates'); explicit API pricing statement; bulk dump route (only the reports API and a dryad-data GitHub repo are mentioned, not captured).
- `dataverse`: Harvard Dataverse's actual rate limits (the Dataverse software makes limits per-installation configurable, no default numbers given, none captured for Harvard); cost; data license (per-dataset, set by depositors); bulk/OAI-PMH route not found in captured pages.
- `mendeley-data`: docs.txt is a JS shell (530 bytes) so no documented rate limits or API terms captured; /terms and /terms-of-use gave Cloudflare block (403) or 404 from this sandbox. Cost statement concerns the repository service, not API pricing specifically. Metadata licence not established: dataset licences ar...
- `gbif`: Cost/pricing statement not found in captured pages (gbif.org/terms returned HTTP 403 challenge from this sandbox, 16 bytes text, so the data user agreement and any licence-of-metadata terms were not captured). Licence is per dataset, no single API-wide licence established. Numeric rate limit not ...
- `clinicaltrials`: docs page, about-api, terms-conditions and migration pages are a JS single-page shell (183 bytes of text), so rate limit, cost and data licence text were not captured; the OpenAPI spec (extra-oas) has no rate or licence text; NLM web policies page has no ClinicalTrials.gov licence statement. A bu...
- `pubchem`: The official docs pages (pubchem.ncbi.nlm.nih.gov/docs/*, pubchemdocs, NCBI scripting guidelines) return a reCAPTCHA browser challenge to the sandbox (HTTP 200, 169-byte body), so the docs were read from the pcfe/docs/markdown/*.md paths instead. The dynamic-request-throttling page (400 req/min, ...
- `springer`: Data license of returned metadata/full text not found in captured pages. The dev.springernature.com portal is a JS single-page app: its rate-limit, API-access and terms pages captured as 200-byte shells, so the limits come from the datasolutions.springernature.com product pages and cover the Open...
- `elsevier`: Data license/reuse terms of returned data not found in captured pages (the API Service Agreement and Use Policies were not captured). Price of the commercial API license not stated. Whether any free institutional-entitlement route exists for individual researchers was not captured. No bulk dump o...
- `ieee`: Numeric rate limits (shown only during registration, not captured). Data license of returned metadata (terms grant only a limited non-commercial license; no data license named). Whether any fee applies beyond being a current IEEE customer. Docs home is a thin page; the Getting Started and Terms p...
- `wos`: Numeric rate limits per plan (plan pages 404 or require login: tried developer.clarivate.com/apis/wos-starter/plans 404, swagger.json 401, GitHub client README has no limits). Data license of returned metadata. Whether the free plan is approval-gated vs instant (docs only say approval may take a ...
- `lens`: Numeric rate limits (docs describe x-rate-limit-* headers and per-minute/per-month quotas but give no numbers). Cost/plans and whether approval is free (no pricing page captured). Data license (terms pages docs.api.lens.org/terms-scholarly.html and bulk.html 404, about.lens.org/policies 403 from ...
- `dimensions`: Data license of returned data not found (the Reasonable Use page guessed at docs.dimensions.ai/dsl/limits.html and reasonable_use.html returned 404; terms page not captured). Exact criteria for the free scientometric-research access not captured. Probe was a GET on the auth endpoint without crede...
- `scite`: Cost/pricing of tokens not found (scite.ai/api returned CloudFront 403 from this sandbox; OpenAPI says contact sales@scite.ai or use self-service keys, prices not stated). Data license not found in the OpenAPI doc (only a link to https://scite.ai/terms, not captured). Docs page api.scite.ai/docs ...
- `trove`: Cost not stated on captured pages. Data license and documented numeric rate limit not found: API terms of use, technical guide and bulk download pages all returned an Anubis proof-of-work challenge (HTTP 200 body 'Making sure you're not a bot!') so no content was captured. The 200m figure in Tabl...

