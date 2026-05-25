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
- Add local DBpedia `owl:sameAs` URI links.
- Compute artist similarity relationships.
- Add Python-based inferred triples.
- Serialize RDF outputs.

Current outputs:

```text
music_kg_project/data/music_kg.nt
music_kg_project/data/music_kg.rdf
music_kg_project/data/ontology.ttl
music_kg_project/data/stats.json
```

Required TP2 outputs still to add:

```text
music_kg_project/data/facts_only.nt
music_kg_project/data/music_kg_integrated.rdf
music_kg_project/data/spin_rules.ttl
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

Important required fix:

- `rdf_store.py` imports `requests`, but `music_kg_project/requirements.txt` currently does not include `requests`. Add it before running the backend on a fresh environment.

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
pandas
numpy
scipy
tqdm
```

Future TP2 requirement:

```text
SPARQLWrapper
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
```

Required fix:

```text
requests
```

Future TP2 requirement:

```text
SPARQLWrapper
```

### 5.3 Generate RDF

From project root:

```bash
python convert_to_rdf.py --csv spotify_songs.csv --data-dir music_kg_project/data/
```

Current expected outputs:

```text
music_kg_project/data/music_kg.nt
music_kg_project/data/music_kg.rdf
music_kg_project/data/ontology.ttl
music_kg_project/data/stats.json
```

Future expected outputs:

```text
music_kg_project/data/facts_only.nt
music_kg_project/data/music_kg_integrated.rdf
music_kg_project/data/spin_rules.ttl
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
3. `music_kg_project/data/spin_rules.ttl` after it is implemented

Current limitation:

- `facts_only.nt` and `spin_rules.ttl` are not generated yet.

Current fallback:

- Import `music_kg_project/data/music_kg.nt` to load the existing full graph.
- Import `music_kg_project/data/ontology.ttl` separately if testing ontology behavior.

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

Current file:

```text
music_kg_project/data/ontology.ttl
```

Future integrated file:

```text
music_kg_project/data/music_kg_integrated.rdf
```

Recommended workflow:

1. Open Protégé.
2. Load `ontology.ttl`.
3. Check classes, properties, labels, domains, ranges, and restrictions.
4. Load/open the integrated graph file after it is generated.
5. Run reasoner checks where applicable.
6. Document results in `tp2_report.md`.

## 8. SPIN Integration Plan

Current status:

- Inference is implemented in Python inside `convert_to_rdf.py`.
- This is not enough for TP2 because SPIN rules must be explicitly defined in an independent Python module.

Required module:

```text
music_kg_project/music_graph/spin_rules.py
```

Required output:

```text
music_kg_project/data/spin_rules.ttl
```

Candidate rules:

- Infer `music:performs` from artist-album-track relationships.
- Infer symmetric `music:similarTo`.
- Infer `music:sharedGenreWith` for tracks sharing a genre.
- Classify high-energy tracks.
- Classify popular tracks.
- Classify albums/tracks by decade.

## 9. DBpedia/Wikidata Integration Plan

Current status:

- DBpedia URIs are generated locally as `owl:sameAs`.
- No real SPARQL endpoint call exists.

Required dependency:

```text
SPARQLWrapper
```

Recommended module:

```text
music_kg_project/music_graph/linked_data.py
```

or:

```text
enrich_linked_data.py
```

Required behavior:

- Query DBpedia and/or Wikidata programmatically.
- Add external enrichment triples.
- Store results in RDF.
- Surface enrichment in API/UI.

Possible enrichment outputs:

```text
music_kg_project/data/enrichment.ttl
music_kg_project/data/music_kg_enriched.ttl
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
stats.json
```

### 11.2 RDF Parse Checks

Use `rdflib` or command-line tools to confirm files parse and contain triples.

Example:

```bash
python - <<'PY'
from rdflib import Graph
for path, fmt in [
    ("music_kg_project/data/ontology.ttl", "turtle"),
    ("music_kg_project/data/facts_only.nt", "nt"),
    ("music_kg_project/data/music_kg_integrated.rdf", "xml"),
]:
    g = Graph()
    g.parse(path, format=fmt)
    print(path, len(g))
PY
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

