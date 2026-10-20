#!/usr/bin/env python3
"""Write data/providers.json from the table below.

Each row: slug | name | category | docs URL | probe URL | probe Accept header.
The probe is one real, minimal, keyless API call. A provider whose API needs
a key still gets a probe: the refusal (401/403) is itself evidence of the gate.
"""
import json, os

J = "application/json"
ROWS = """
wayback-cdx|Wayback Machine CDX Server|archive|https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md|http://web.archive.org/cdx/search/cdx?url=example.com&limit=2&output=json|
wayback-availability|Wayback Machine Availability API|archive|https://archive.org/help/wayback_api.php|https://archive.org/wayback/available?url=example.com|
wayback-spn2|Wayback Save Page Now 2 API|archive|https://docs.google.com/document/d/1Nsv52MvSjbLb2PCpHlat0gkzw0EvtSgpKHu4mk0MnrA/export?format=txt|https://web.archive.org/save/status/system|
ia-advancedsearch|Internet Archive Advanced Search|archive|https://archive.org/advancedsearch.php|https://archive.org/advancedsearch.php?q=mediatype%3Atexts&fl%5B%5D=identifier&rows=1&output=json|
ia-metadata|Internet Archive Metadata API|archive|https://archive.org/developers/metadata.html|https://archive.org/metadata/nasa|
ia-scholar|Internet Archive Scholar / fatcat|archive|https://guide.fatcat.wiki/http_api.html|https://api.fatcat.wiki/v0/release/lookup?doi=10.1038/nature12373|
commoncrawl|Common Crawl Index|archive|https://commoncrawl.org/get-started|https://index.commoncrawl.org/collinfo.json|
memento|Memento Time Travel|archive|http://timetravel.mementoweb.org/guide/api/|http://timetravel.mementoweb.org/timemap/json/http://example.com/|
arquivo-pt|Arquivo.pt Web Archive|archive|https://github.com/arquivo/pwa-technologies/wiki/Arquivo.pt-API|https://arquivo.pt/wayback/cdx?url=example.com&limit=2&output=json|
software-heritage|Software Heritage Archive|archive|https://archive.softwareheritage.org/api/|https://archive.softwareheritage.org/api/1/origin/https://github.com/torvalds/linux/get/|
loc|Library of Congress API|library|https://www.loc.gov/apis/|https://www.loc.gov/search/?q=test&fo=json&c=1|
europeana|Europeana Search API|library|https://pro.europeana.eu/page/search|https://api.europeana.eu/record/v2/search.json?wskey=api2demo&query=test&rows=1|
hathitrust|HathiTrust Bibliographic API|library|https://www.hathitrust.org/member-libraries/resources-for-librarians/data-resources/bib-api/|https://catalog.hathitrust.org/api/volumes/brief/oclc/424023.json|
dpla|Digital Public Library of America|library|https://pro.dp.la/developers/api-codex|https://api.dp.la/v2/items?q=test&page_size=1|
openlibrary|Open Library API|library|https://openlibrary.org/developers/api|https://openlibrary.org/search.json?q=test&limit=1|
googlebooks|Google Books API|library|https://developers.google.com/books/docs/v1/using|https://www.googleapis.com/books/v1/volumes?q=test&maxResults=1|
gutendex|Gutendex (Project Gutenberg)|library|https://gutendex.com/|https://gutendex.com/books/?search=dickens|
gallica|Gallica SRU (BnF)|library|https://api.bnf.fr/api-sru-gallica|https://gallica.bnf.fr/SRU?operation=searchRetrieve&version=1.2&query=%28gallica%20all%20%22test%22%29&maximumRecords=1|
nara|US National Archives Catalog API|library|https://catalog.archives.gov/api/v2/api-docs|https://catalog.archives.gov/api/v2/records/search?q=test&limit=1|
smithsonian|Smithsonian Open Access API|library|https://edan.si.edu/openaccess/apidocs/|https://api.si.edu/openaccess/api/v1.0/search?q=test&rows=1&api_key=DEMO_KEY|
wikipedia|MediaWiki Action API (Wikipedia)|encyclopedia|https://www.mediawiki.org/wiki/API:Main_page|https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=test&srlimit=1&format=json|
wikidata|Wikidata API / SPARQL|encyclopedia|https://www.wikidata.org/wiki/Wikidata:Data_access|https://www.wikidata.org/w/api.php?action=wbsearchentities&search=Marie%20Curie&language=en&limit=1&format=json|
openalex|OpenAlex|scholarly|https://docs.openalex.org/|https://api.openalex.org/works?per-page=1|
crossref|Crossref REST API|scholarly|https://www.crossref.org/documentation/retrieve-metadata/rest-api/|https://api.crossref.org/works?rows=1|
datacite|DataCite REST API|scholarly|https://support.datacite.org/docs/api|https://api.datacite.org/dois?page%5Bsize%5D=1|
semanticscholar|Semantic Scholar Academic Graph|scholarly|https://api.semanticscholar.org/api-docs/|https://api.semanticscholar.org/graph/v1/paper/DOI:10.1038/nature12373?fields=title|
core|CORE API|scholarly|https://core.ac.uk/services/api|https://api.core.ac.uk/v3/search/works?q=test&limit=1|
arxiv|arXiv API|preprint|https://info.arxiv.org/help/api/index.html|https://export.arxiv.org/api/query?search_query=all:test&max_results=1|
pubmed-eutils|NCBI E-utilities (PubMed)|biomed|https://www.ncbi.nlm.nih.gov/books/NBK25497/|https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=test&retmax=1&retmode=json|
europepmc|Europe PMC REST API|biomed|https://europepmc.org/RestfulWebService|https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=test&format=json&pageSize=1|
pmc-idconv|PMC ID Converter API|biomed|https://pmc.ncbi.nlm.nih.gov/tools/id-converter-api/|https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?ids=10.1038/nature12373&format=json|
unpaywall|Unpaywall REST API|oa|https://unpaywall.org/products/api|https://api.unpaywall.org/v2/10.1038/nature12373?email=research@example.org|
doaj|Directory of Open Access Journals API|oa|https://doaj.org/api/v4/docs|https://doaj.org/api/search/articles/test?pageSize=1|
openaire|OpenAIRE Graph API|scholarly|https://graph.openaire.eu/docs/apis/graph-api/|https://api.openaire.eu/graph/v1/researchProducts?search=test&pageSize=1|
base|BASE (Bielefeld Academic Search Engine)|oa|https://www.base-search.net/about/en/about_develop.php|https://api.base-search.net/cgi-bin/BaseHttpSearchInterface.fcgi?func=PerformSearch&query=test&hits=1&format=json|
biorxiv|bioRxiv / medRxiv API|preprint|https://api.biorxiv.org/|https://api.biorxiv.org/details/biorxiv/2024-01-01/2024-01-02/0|
hal|HAL Search API|oa|https://api.archives-ouvertes.fr/docs/search|https://api.archives-ouvertes.fr/search/?q=test&rows=1&wt=json|
orcid|ORCID Public API|identifier|https://info.orcid.org/documentation/features/public-api/|https://pub.orcid.org/v3.0/search/?q=test&rows=1|application/json
ror|Research Organization Registry API|identifier|https://ror.readme.io/docs/rest-api|https://api.ror.org/v2/organizations?query=harvard|
inspirehep|INSPIRE HEP API|scholarly|https://github.com/inspirehep/rest-api-doc|https://inspirehep.net/api/literature?size=1&q=test&fields=titles|
nasa-ads|NASA Astrophysics Data System API|scholarly|https://ui.adsabs.harvard.edu/help/api/|https://api.adsabs.harvard.edu/v1/search/query?q=test&rows=1|
dblp|dblp API|scholarly|https://dblp.org/faq/How+to+use+the+dblp+search+API.html|https://dblp.org/search/publ/api?q=test&format=json&h=1|
opencitations|OpenCitations Index API|scholarly|https://opencitations.net/index/api/v2|https://opencitations.net/index/api/v2/citations/doi:10.1038/nature12373|
crossref-events|Crossref Event Data API|scholarly|https://www.crossref.org/documentation/event-data/|https://api.eventdata.crossref.org/v1/events?rows=1|
altmetric|Altmetric Details Page API|scholarly|https://details-page-api-docs.altmetric.com/|https://api.altmetric.com/v1/doi/10.1038/nature12373|
orkg|Open Research Knowledge Graph|scholarly|https://orkg.org/api/swagger-ui/index.html|https://orkg.org/api/resources?size=1|application/json
oabutton|Open Access Button API|oa|https://openaccessbutton.org/api|https://api.openaccessbutton.org/find?id=10.1038/nature12373|
oapen|OAPEN Library (DSpace REST)|oa|https://library.oapen.org/|https://library.oapen.org/rest/search?query=test&limit=1|
zbmath|zbMATH Open API|scholarly|https://api.zbmath.org/|https://api.zbmath.org/v1/document/_search?search_string=test&page=0&results_per_page=1|
openreview|OpenReview API|scholarly|https://docs.openreview.net/|https://api2.openreview.net/notes?limit=1|
scielo|SciELO ArticleMeta API|oa|https://github.com/scieloorg/articlemeta|https://articlemeta.scielo.org/api/v1/journal/?limit=1|
jstage|J-STAGE WebAPI|oa|https://www.jstage.jst.go.jp/static/pages/WebAPI/-char/en|https://api.jstage.jst.go.jp/searchapi/do?service=3&text=test&count=1|
zenodo|Zenodo REST API|repository|https://developers.zenodo.org/|https://zenodo.org/api/records?size=1|
figshare|Figshare API|repository|https://docs.figshare.com/|https://api.figshare.com/v2/articles?page_size=1|
osf|Open Science Framework API|repository|https://developer.osf.io/|https://api.osf.io/v2/nodes/?page%5Bsize%5D=1|
dryad|Dryad API|repository|https://datadryad.org/api|https://datadryad.org/api/v2/search?q=test&per_page=1|
dataverse|Harvard Dataverse Search API|repository|https://guides.dataverse.org/en/latest/api/search.html|https://dataverse.harvard.edu/api/search?q=test&per_page=1|
mendeley-data|Mendeley Data API|repository|https://data.mendeley.com/api/docs/|https://data.mendeley.com/public-api/datasets?query=test|
gbif|GBIF API|science|https://techdocs.gbif.org/en/openapi/|https://api.gbif.org/v1/species/search?q=puma&limit=1|
clinicaltrials|ClinicalTrials.gov API v2|biomed|https://clinicaltrials.gov/data-api/api|https://clinicaltrials.gov/api/v2/studies?pageSize=1|
pubchem|PubChem PUG REST|science|https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest|https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/property/MolecularFormula/JSON|
springer|Springer Nature API|publisher|https://dev.springernature.com/|https://api.springernature.com/meta/v2/json?q=test&p=1&api_key=invalid|
elsevier|Elsevier Developer Portal (Scopus/ScienceDirect)|publisher|https://dev.elsevier.com/|https://api.elsevier.com/content/search/scopus?query=test&count=1|application/json
ieee|IEEE Xplore API|publisher|https://developer.ieee.org/|https://ieeexploreapi.ieee.org/api/v1/search/articles?querytext=test&max_records=1|
wos|Web of Science API|publisher|https://developer.clarivate.com/apis|https://api.clarivate.com/apis/wos-starter/v1/documents?q=TS%3Dtest&limit=1|
lens|The Lens API|scholarly|https://docs.api.lens.org/|https://api.lens.org/scholarly/search|
dimensions|Dimensions Analytics API|scholarly|https://docs.dimensions.ai/dsl/|https://app.dimensions.ai/api/auth|
scite|scite API|scholarly|https://api.scite.ai/docs|https://api.scite.ai/tallies/10.1038/nature12373|
trove|Trove API (NLA)|library|https://trove.nla.gov.au/about/create-something/using-api|https://api.trove.nla.gov.au/v3/result?q=test&category=newspaper|
""".strip().splitlines()

out = []
for r in ROWS:
    s, n, c, d, p, a = r.split("|")
    out.append({"slug": s, "name": n, "category": c, "docs": d, "probe": p, "accept": a or J})
slugs = [o["slug"] for o in out]
assert len(slugs) == len(set(slugs)), "duplicate slug"
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(root, "data", "providers.json"), "w") as f:
    json.dump(out, f, indent=1)
print(len(out), "providers")
