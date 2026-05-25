# Integration Guide: Music Knowledge Graph TP2

## 1. Purpose

This guide explains how the current Music Knowledge Graph project is structured, how its parts integrate, and what still needs to be implemented to satisfy TP2. It should be updated as the project evolves.

The final TP2 system must integrate:

- Python/Django web application.
- React frontend.
- RDF data files.
- RDFS/OWL ontology.
- GraphDB triplestore.
- SPARQL queries and updates.
- SPIN inference rules.
- DBpedia/Wikidata enrichment through SPARQLWrapper.
- RDFa/microformats in rendered web pages.
- Protégé validation.

## 2. Current Architecture

```text
spotify_songs.csv
  -> convert_to_rdf.py
  -> music_kg_project/data/*.rdf|*.nt|*.ttl
  -> music_kg_project/music_graph/linked_data.py (optional DBpedia enrichment)
  -> GraphDB repository when available
  -> rdflib fallback when GraphDB is unavailable
  -> Django REST API
  -> React/Vite frontend
```

## 3. Current Runtime Components

### 3.1 ETL

File:

```text
convert_to_rdf.py
```

Current responsibilities:

- Read `spotify_songs.csv`.
- Clean and normalize music data.
- Build ontology triples.
- Build artist, album, track, genre, and audio-feature triples.
- Build derived TP2 classification triples for audio profiles, energy, popularity, and release eras.
- Add local DBpedia `owl:sameAs` URI links.
- Add ontology properties used by optional linked-data enrichment.
- Compute artist similarity relationships.
- Add Python-based inferred triples.
- Serialize RDF outputs.

Current outputs:

```text
music_kg_project/data/facts_only.nt
music_kg_project/data/music_kg.nt
music_kg_project/data/music_kg.rdf
music_kg_project/data/music_kg_integrated.rdf
music_kg_project/data/music_kg_enriched.ttl
music_kg_project/data/ontology.ttl
music_kg_project/data/enrichment.ttl
music_kg_project/data/spin_rules.ttl
music_kg_project/data/stats.json
```

Output meaning:

- `facts_only.nt` contains data facts only from the artist, album, and track named graphs.
- `ontology.ttl` contains ontology/schema triples only.
- `music_kg_integrated.rdf` contains ontology plus facts in RDF/XML for Protégé.
- `enrichment.ttl` contains optional DBpedia/Wikidata enrichment triples.
- `music_kg_enriched.ttl` contains the integrated graph plus optional enrichment triples in Turtle.
- `spin_rules.ttl` contains independent SPIN-compatible inference rules.
- `music_kg.nt` and `music_kg.rdf` are preserved full-graph exports for existing behavior.

### 3.1.1 Linked-Data Enrichment

File:

```text
music_kg_project/music_graph/linked_data.py
```

Current status:

- Done for Milestone 6.
- Runs independently from Django startup and from the normal RDF generation command.
- Reads local RDF from `facts_only.nt` or `music_kg_integrated.rdf`.
- Uses existing local DBpedia `owl:sameAs` URIs to select a controlled subset of artists/genres.
- Uses `SPARQLWrapper` to query DBpedia at `https://dbpedia.org/sparql`.
- Adds available external metadata:
  - `music:dbpediaAbstract`
  - `music:originPlace`
  - `music:officialWebsite`
  - `music:wikidataEntity`
  - additional Wikidata `owl:sameAs` links when DBpedia exposes them
- Supports `--limit` and `--timeout`.
- Handles endpoint/resource failures per resource and still writes a valid Turtle output.

Usage:

```bash
.venv/bin/python music_kg_project/music_graph/linked_data.py --input music_kg_project/data/music_kg_integrated.rdf --output music_kg_project/data/enrichment.ttl --limit 20
```

Optional combined graph:

```bash
.venv/bin/python music_kg_project/music_graph/linked_data.py --input music_kg_project/data/music_kg_integrated.rdf --output music_kg_project/data/enrichment.ttl --limit 20 --enriched-output music_kg_project/data/music_kg_enriched.ttl
```

Latest result:

```text
Linked-data enrichment summary
  candidates: 20
  queried: 20
  enriched resources: 9
  triples added: 25
  failures: 0
  output: music_kg_project/data/enrichment.ttl
  enriched graph: music_kg_project/data/music_kg_enriched.ttl
```

### 3.2 Backend

Path:

```text
music_kg_project/
```

Main files:

```text
music_kg_project/music_graph/rdf_store.py
music_kg_project/music_graph/sparql_queries.py
music_kg_project/music_graph/views.py
music_kg_project/music_graph/urls.py
music_kg_project/music_graph/similarity.py
music_kg_project/music_graph/timeline.py
```

Backend responsibilities:

- Load/query graph data.
- Use GraphDB if available.
- Fall back to `rdflib` if GraphDB is unavailable.
- Expose REST endpoints for frontend usage.
- Execute SPARQL SELECT.
- Execute SPARQL UPDATE.
- Serve search, graph, analytics, timeline, and recommendations data.

### 3.3 GraphDB Store

File:

```text
music_kg_project/music_graph/rdf_store.py
```

Current behavior:

- Attempts to connect to GraphDB at:

```text
http://localhost:7200
```

- Uses repository:

```text
music-kg
```

- If GraphDB is reachable:
  - checks repository list,
  - creates repository if missing,
  - uploads `music_kg.nt` if repository appears empty,
  - routes SPARQL SELECT and UPDATE through GraphDB HTTP endpoints.
- If GraphDB is not reachable:
  - loads `music_kg.nt` into an in-memory `rdflib.ConjunctiveGraph`.

Dependency status:

- `requests` is included in `music_kg_project/requirements.txt` because `rdf_store.py` imports it.
- `SPARQLWrapper` is included in both root and backend requirements and is used by `music_kg_project/music_graph/linked_data.py` for DBpedia/Wikidata enrichment.

### 3.4 Frontend

Path:

```text
music-kg-frontend/
```

Main files:

```text
music-kg-frontend/src/App.jsx
music-kg-frontend/src/api/index.js
music-kg-frontend/src/pages/
music-kg-frontend/src/components/
```

Current routes:

```text
/                 Home
/search           Search
/artist/:slug     Artist detail
/album/:slug      Album detail
/timeline         Timeline
/graph            Graph explorer
/analytics        Analytics
```

Current frontend API base URL:

```js
baseURL: 'http://localhost:8000/api'
```

Recommended later improvement:

- Move API base URL to an environment variable such as `VITE_API_BASE_URL`.

## 4. Backend API Contract

Base URL:

```text
http://localhost:8000/api
```

### 4.1 Query Endpoints

```http
GET /api/stats/
GET /api/artists/
GET /api/artists/<slug>/
GET /api/albums/<slug>/
GET /api/tracks/
GET /api/search/
GET /api/timeline/
GET /api/timeline/<genre>/
GET /api/genre-landscape/
GET /api/audio-distribution/
GET /api/similar-edges/
GET /api/recommendations/<slug>/
GET /api/sparql-templates/
```

### 4.2 SPARQL SELECT

```http
POST /api/sparql/
Content-Type: application/json

{
  "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
}
```

Expected use:

- User-facing or developer-facing read-only query execution.

### 4.3 SPARQL UPDATE

```http
POST /api/sparql/update/
Content-Type: application/json

{
  "update": "INSERT DATA { <http://example/s> <http://example/p> <http://example/o> . }"
}
```

Expected use:

- Admin/development semantic data operations.

TP2 note:

- This helps demonstrate SPARQL modification operations.
- It should be documented carefully because unrestricted update access is unsafe in production.

### 4.4 Data Mutation Endpoints

```http
POST /api/artists/create/
POST /api/songs/bulk-create/
POST /api/tracks/update-album/
POST /api/albums/update-year/
POST /api/tracks/delete/
```

Purpose:

- Provide UI-friendly operations backed by SPARQL UPDATE.
- Demonstrate new operations over semantic data.

## 5. Local Setup

### 5.1 Python ETL Dependencies

From project root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Current root requirements:

```text
rdflib
SPARQLWrapper
pandas
numpy
scipy
tqdm
```

### 5.2 Backend Dependencies

```bash
cd music_kg_project
pip install -r requirements.txt
```

Current backend requirements:

```text
Django
djangorestframework
django-cors-headers
rdflib
requests
SPARQLWrapper
```

### 5.3 Generate RDF

From project root:

```bash
.venv/bin/python convert_to_rdf.py --csv spotify_songs.csv --data-dir music_kg_project/data/
```

Expected outputs:

```text
music_kg_project/data/facts_only.nt
music_kg_project/data/music_kg.nt
music_kg_project/data/music_kg.rdf
music_kg_project/data/music_kg_integrated.rdf
music_kg_project/data/ontology.ttl
music_kg_project/data/stats.json
```

Generate SPIN rules:

```bash
.venv/bin/python music_kg_project/music_graph/spin_rules.py --output music_kg_project/data/spin_rules.ttl
```

### 5.4 Start Backend

```bash
cd music_kg_project
python manage.py migrate
python manage.py runserver
```

Backend URL:

```text
http://localhost:8000
```

API URL:

```text
http://localhost:8000/api
```

### 5.5 Start Frontend

```bash
cd music-kg-frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

## 6. GraphDB Integration

### 6.1 Install and Start GraphDB

Install GraphDB locally from Ontotext and start it without Docker.

Expected local URL:

```text
http://localhost:7200
```

Open the Workbench in a browser:

```text
http://localhost:7200
```

### 6.2 Repository

Repository ID expected by the code:

```text
music-kg
```

The current `rdf_store.py` can attempt to create this repository automatically. For TP2 submission, document and test manual creation as well.

Recommended repository settings:

- Repository ID: `music-kg`
- Ruleset: choose an appropriate GraphDB ruleset for OWL/RDFS testing, or document if using `empty`.
- Base URI: `http://musickg.org/`

### 6.3 Import Order for TP2

For GraphDB validation, import in this order:

1. `music_kg_project/data/facts_only.nt`
2. `music_kg_project/data/ontology.ttl`
3. `music_kg_project/data/spin_rules.ttl`

Current note:

- `facts_only.nt` is generated and excludes ontology/schema triples.
- `ontology.ttl` includes the expanded TP2 ontology with audio-profile, popularity, energy, and release-era classes/properties.
- `spin_rules.ttl` is generated from `music_kg_project/music_graph/spin_rules.py`.
- `music_kg.nt` remains available as the existing full-graph import option.

### 6.4 Confirm GraphDB Use

Start GraphDB, then start Django.

Check:

```bash
curl http://localhost:8000/api/stats/
```

Expected:

- Response includes `"backend": "GraphDB"` when GraphDB is being used.
- Response includes `"backend": "rdflib"` when GraphDB is unavailable and fallback is used.

## 7. Protégé Integration

Protégé should be used to validate the ontology and integrated data.

Ontology-only file:

```text
music_kg_project/data/ontology.ttl
```

Integrated ontology plus facts file:

```text
music_kg_project/data/music_kg_integrated.rdf
```

Recommended workflow:

1. Open Protégé.
2. Load `ontology.ttl`.
3. Check classes, properties, labels, comments, subclasses, domains, ranges, inverse properties, and symmetric properties.
4. Load/open `music_kg_integrated.rdf`.
5. Check generated classification triples such as `music:HighEnergyTrack`, `music:PopularTrack`, `music:ModernTrack`, `music:ClassicTrack`, and `music:belongsToEra`.
6. Run reasoner checks where applicable.
7. Document results in `tp2_report.md`.

## 8. SPIN Integration

Current status:

- Done for Milestone 5.
- Practical inference/classification triples are generated in Python inside `convert_to_rdf.py`.
- SPIN-compatible rule definitions are generated independently by `music_kg_project/music_graph/spin_rules.py`.

Module:

```text
music_kg_project/music_graph/spin_rules.py
```

Output:

```text
music_kg_project/data/spin_rules.ttl
```

Generation command:

```bash
.venv/bin/python music_kg_project/music_graph/spin_rules.py --output music_kg_project/data/spin_rules.ttl
```

Latest result:

```text
Wrote music_kg_project/data/spin_rules.ttl (30 triples)
```

Implemented rules:

- Infer `music:performs` from artist-album-track relationships.
- Infer symmetric `music:similarTo`.
- Classify high-energy tracks.
- Classify popular tracks.
- Classify albums/tracks into broad release eras.

## 9. DBpedia/Wikidata Integration

Current status:

- DBpedia URIs are generated locally as `owl:sameAs`.
- Done for Milestone 6.
- `music_kg_project/music_graph/linked_data.py` performs real DBpedia SPARQL endpoint calls with `SPARQLWrapper`.
- Enrichment remains optional and separate from app startup.

Dependency:

```text
SPARQLWrapper
```

Module:

```text
music_kg_project/music_graph/linked_data.py
```

Implemented behavior:

- Query DBpedia programmatically using existing local DBpedia `owl:sameAs` links.
- Add external enrichment triples for DBpedia abstracts, origin/birth places, official websites, and associated Wikidata entities when available.
- Store results in RDF Turtle.
- Limit external requests by default with `--limit 20`.
- Support request timeout with `--timeout`.
- Skip missing fields and continue after per-resource endpoint failures.
- Surface enrichment in API/UI.

Outputs:

```text
music_kg_project/data/enrichment.ttl
music_kg_project/data/music_kg_enriched.ttl
```

Latest network note:

```text
Initial sandboxed network attempt could not resolve dbpedia.org:
<urlopen error [Errno 8] nodename nor servname provided, or not known>

After explicit network approval, DBpedia enrichment completed successfully with 25 triples.
```

## 10. RDFa and Microformats Plan

Current status:

- React pages do not include RDFa or microformat/microdata annotations.

Required pages/components:

- `music-kg-frontend/src/pages/ArtistDetailPage.jsx`
- `music-kg-frontend/src/pages/AlbumDetailPage.jsx`
- Track list components inside artist/album pages.

Recommended annotations:

- Artist:
  - `typeof="schema:MusicGroup"` or `typeof="music:Artist"`
  - `property="schema:name"`
  - `resource` pointing to the artist URI
- Album:
  - `typeof="schema:MusicAlbum"`
  - `property="schema:name"`
  - `property="schema:datePublished"`
- Track:
  - `typeof="schema:MusicRecording"`
  - `property="schema:name"`
  - `property="schema:byArtist"`

Also consider microdata:

```html
itemscope
itemtype="https://schema.org/MusicGroup"
itemprop="name"
```

Verification:

- Inspect rendered HTML in the browser.
- Confirm semantic attributes appear in the DOM.

## 11. Required Verification Checks

### 11.1 File Checks

```bash
ls -lh music_kg_project/data
```

Expected final files:

```text
facts_only.nt
ontology.ttl
music_kg_integrated.rdf
spin_rules.ttl
enrichment.ttl
music_kg_enriched.ttl
stats.json
```

Current generated TP2 files:

```text
facts_only.nt
ontology.ttl
music_kg_integrated.rdf
spin_rules.ttl
enrichment.ttl
music_kg_enriched.ttl
```

### 11.2 RDF Parse Checks

Use `rdflib` or command-line tools to confirm files parse and contain triples.

Example:

```bash
.venv/bin/python - <<'PY'
from rdflib import Graph
for path, fmt in [
    ("music_kg_project/data/ontology.ttl", "turtle"),
    ("music_kg_project/data/enrichment.ttl", "turtle"),
    ("music_kg_project/data/spin_rules.ttl", "turtle"),
    ("music_kg_project/data/music_kg_integrated.rdf", "xml"),
    ("music_kg_project/data/music_kg_enriched.ttl", "turtle"),
]:
    g = Graph()
    g.parse(path, format=fmt)
    print(path, len(g))
PY
```

Latest verification results:

```text
music_kg_project/data/ontology.ttl: 193 triples
music_kg_project/data/enrichment.ttl: 25 triples
music_kg_project/data/spin_rules.ttl: 30 triples
music_kg_project/data/music_kg_integrated.rdf: 761600 triples
music_kg_project/data/music_kg_enriched.ttl: 761625 triples
```

### 11.3 Backend Checks

```bash
curl http://localhost:8000/api/stats/
curl "http://localhost:8000/api/artists/?limit=5"
curl "http://localhost:8000/api/search/?q=drake"
curl http://localhost:8000/api/genre-landscape/
curl http://localhost:8000/api/similar-edges/
```

### 11.4 Frontend Checks

```bash
cd music-kg-frontend
npm run build
```

Manual browser checks:

- Home page loads.
- Search works.
- Artist detail loads.
- Album detail loads.
- Graph explorer renders artist/genre/similarity relationships.
- Analytics charts render.
- RDFa/microdata attributes appear after implementation.

## 12. Final TP2 Report Integration

Recommended report file:

```text
tp2_report.md
```

The report must follow this order:

1. Introduction to the topic.
2. Definition of the ontology (RDFS and OWL).
3. Set of inferences (SPIN).
4. New operations on the data (SPARQL).
5. Use and integration of data from Wikidata and/or DBpedia.
6. Publication of semantic data through RDFa and microformats.
7. Application functionalities not present in TP1 or complementary to it.
8. Conclusions.
9. Configuration to run the application.

Each implementation milestone should update the report or add notes that can be copied into it.
