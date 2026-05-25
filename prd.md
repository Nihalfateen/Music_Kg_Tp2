# Product Requirements Document: Music Knowledge Graph TP2

## 1. Product Summary

Music Knowledge Graph is a semantic web application for exploring Spotify playlist data as RDF knowledge. The project combines a Django backend, a React frontend, RDF/OWL ontology files, SPARQL querying/updating, graph visualizations, analytics, and music discovery features.

The TP2 goal is to evolve the current project into a complete semantic information system that satisfies the assignment requirements:

- Use Python/Django as the web application.
- Use GraphDB as the triplestore.
- Use RDF, RDFS, OWL, SPARQL, SPIN, SPARQLWrapper, RDFa, and microformats.
- Provide deliverable data files for GraphDB and Protégé.
- Produce documentation and a report that clearly explain the semantic web implementation.

## 2. Current Project Structure

```text
music_kg/
├── convert_to_rdf.py
├── requirements.txt
├── spotify_songs.csv
├── prd.md
├── integration.md
├── music_kg_project/
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3
│   ├── data/
│   │   ├── music_kg.nt
│   │   ├── music_kg.rdf
│   │   ├── ontology.ttl
│   │   └── stats.json
│   ├── music_kg_project/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── music_graph/
│       ├── apps.py
│       ├── models.py
│       ├── rdf_store.py
│       ├── serializers.py
│       ├── similarity.py
│       ├── sparql_queries.py
│       ├── timeline.py
│       ├── urls.py
│       └── views.py
└── music-kg-frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── api/index.js
        ├── App.jsx
        ├── pages/
        ├── components/
        ├── context/
        ├── hooks/
        └── utils/
```

## 3. Current Implemented Capabilities

### Backend

- Django REST API under `/api/`.
- RDF store abstraction in `music_graph/rdf_store.py`.
- Dual backend behavior:
  - GraphDB mode when `http://localhost:7200` is reachable.
  - `rdflib` in-memory fallback when GraphDB is unavailable.
- SPARQL SELECT execution endpoint: `POST /api/sparql/`.
- SPARQL UPDATE execution endpoint: `POST /api/sparql/update/`.
- Artist, album, track, search, stats, timeline, analytics, recommendation, and similarity-edge endpoints.
- Data mutation endpoints for adding artists, adding songs, updating album metadata, updating album year, and deleting tracks.
- SQLite models for search logs and SPARQL query templates.

### Frontend

- React/Vite SPA.
- Pages currently routed:
  - `/`
  - `/search`
  - `/artist/:slug`
  - `/album/:slug`
  - `/timeline`
  - `/graph`
  - `/analytics`
- Graph explorer uses artist/genre data and similarity edges.
- Artist/album pages include edit/update flows.
- Frontend API wrapper in `music-kg-frontend/src/api/index.js`.

### Data and Semantics

- `convert_to_rdf.py` generates RDF graph files from `spotify_songs.csv`.
- Current generated files:
  - `music_kg_project/data/music_kg.nt`
  - `music_kg_project/data/music_kg.rdf`
  - `music_kg_project/data/ontology.ttl`
  - `music_kg_project/data/stats.json`
- Ontology includes core classes:
  - `music:Artist`
  - `music:Album`
  - `music:Track`
  - `music:Genre`
  - `music:AudioFeatures`
- Ontology includes object/data properties such as:
  - `music:hasAlbum`
  - `music:hasTrack`
  - `music:performedBy`
  - `music:performs`
  - `music:inGenre`
  - `music:hasAudioFeatures`
  - `music:similarTo`
  - `music:sharedGenreWith`
- Basic inference is implemented in Python inside `convert_to_rdf.py`.
- DBpedia `owl:sameAs` links are generated locally from artist/genre names.

## 4. TP2 Required Scope

The final project must satisfy all requirements from `ws.tp2.md`.

### 4.1 Ontology

The project must include an RDFS/OWL ontology that thoroughly describes the music domain. It should go beyond raw CSV fields and include meaningful domain concepts and classifications.

Required improvements:

- Expand the ontology beyond the current simple classes.
- Add classifications such as audio profile classes, popularity classes, release-era classes, or genre-based groupings.
- Add useful OWL/RDFS constraints where appropriate:
  - subclass relationships
  - inverse properties
  - symmetric properties
  - domain/range declarations
  - labels/comments
- Keep `ontology.ttl` as the ontology-only file.
- Ensure the ontology can be opened and validated in Protégé.

### 4.2 GraphDB

The project must use GraphDB as the triplestore repository.

Current status:

- Partial. `rdf_store.py` contains GraphDB connection and fallback logic.

Required improvements:

- Add missing dependency `requests` to `music_kg_project/requirements.txt`.
- Document GraphDB setup and repository creation.
- Confirm the Django app can query GraphDB when it is running.
- Keep `rdflib` fallback as a developer convenience, but make GraphDB the documented TP2 path.
- Provide import instructions for facts-only and ontology-only files.

### 4.3 SPARQL

The project must use SPARQL for data querying and modification.

Current status:

- Done/Partial. SELECT and UPDATE are implemented.

Required improvements:

- Document the main SPARQL queries and updates.
- Add examples of new operations over data:
  - create artist
  - add songs
  - update album/year
  - delete track
  - query inferred relations
- Ensure dangerous user-facing SPARQL UPDATE access is controlled or explained as development/admin functionality.

### 4.4 RDF Data Files

The project must provide clear data files for delivery.

Required files:

- `music_kg_project/data/facts_only.nt`
  - Data facts only for GraphDB import.
  - Should be separated from ontology schema triples.
- `music_kg_project/data/ontology.ttl`
  - Ontology only.
- `music_kg_project/data/music_kg_integrated.rdf` or `music_kg_project/data/music_kg_integrated.ttl`
  - Ontology plus facts for Protégé validation.

Current status:

- Missing `facts_only.nt`.
- Missing explicit `music_kg_integrated.*` filename.
- Existing `music_kg.rdf` likely contains integrated graph, but it should be exported with a clear TP2 filename.

### 4.5 SPIN Inference Rules

The assignment requires inference rules in SPIN, defined in a separate independent Python module.

Current status:

- Missing. Current inference is Python logic in `convert_to_rdf.py`, not SPIN.

Required improvements:

- Create a separate module such as:
  - `music_kg_project/music_graph/spin_rules.py`
  - or `spin_rules.py` at project root.
- Define SPIN-compatible rules for inferred relationships/classifications.
- Export SPIN rules to a clear RDF/Turtle file, for example:
  - `music_kg_project/data/spin_rules.ttl`
- The rules should be explicitly identifiable for assessment.

Candidate rules:

- Artist plus album plus track implies `music:performs`.
- Artist similarity symmetry for `music:similarTo`.
- Tracks in the same genre imply `music:sharedGenreWith`.
- Tracks with high energy imply `music:HighEnergyTrack`.
- Tracks with high popularity imply `music:PopularTrack`.
- Albums released within a decade imply decade classification.

### 4.6 DBpedia/Wikidata Enrichment

The assignment requires programmatic access to DBpedia and/or Wikidata SPARQL endpoints using `SPARQLWrapper`.

Current status:

- Partial. DBpedia links are generated locally, but no endpoint access exists.
- `SPARQLWrapper` is not in requirements.

Required improvements:

- Add `SPARQLWrapper` to the appropriate requirements file.
- Create an enrichment module, for example:
  - `music_kg_project/music_graph/linked_data.py`
  - or `enrich_linked_data.py`
- Query DBpedia and/or Wikidata for artist/genre metadata.
- Store enrichment triples in RDF.
- Surface enrichment data in the UI where useful.

Candidate enrichment fields:

- DBpedia abstract/description.
- Wikidata entity URI.
- Country/origin.
- Genre external URI.
- Official website where available.

### 4.7 RDFa and Microformats

The assignment requires semantic annotations to be published inside the web pages.

Current status:

- Missing. React pages do not currently include RDFa or microformat/microdata annotations.

Required improvements:

- Add RDFa and/or schema.org microdata to:
  - Artist detail page.
  - Album detail page.
  - Track listings.
- Use attributes such as:
  - `vocab`
  - `typeof`
  - `property`
  - `resource`
  - `itemscope`
  - `itemtype`
  - `itemprop`
- Verify rendered HTML contains semantic annotations.

### 4.8 Protégé Validation

The assignment requires ontology validation in Protégé.

Current status:

- Missing documentation.

Required improvements:

- Provide clear instructions for opening:
  - `ontology.ttl`
  - `music_kg_integrated.rdf` or `.ttl`
- Document expected classes/properties.
- Document expected inferred classifications/relations.

### 4.9 TP2 Report

The report is a major part of the evaluation and must follow the required order exactly.

Required report sections:

1. Introduction to the topic.
2. Definition of the ontology (RDFS and OWL).
3. Set of inferences (SPIN).
4. New operations on the data (SPARQL).
5. Use and integration of data from Wikidata and/or DBpedia.
6. Publication of semantic data through RDFa and microformats.
7. Application functionalities not present in TP1 or complementary to it.
8. Conclusions.
9. Configuration to run the application.

Recommended file:

- `tp2_report.md`

## 5. Functional Requirements

- Users can browse graph statistics from the home page.
- Users can search artists, albums, and tracks.
- Users can browse/filter by genre.
- Users can view artist details, albums, top tracks, and similar artists.
- Users can view album details and tracks.
- Users can explore artist/genre/similarity graph relationships.
- Users can view timeline and analytics charts.
- Users can run SPARQL SELECT queries.
- Admin/development users can perform SPARQL UPDATE-backed mutations.
- The application must use GraphDB as the main documented triplestore.
- The project must generate TP2-required RDF deliverable files.
- The application must publish semantic annotations in rendered web pages.

## 6. Non-Functional Requirements

- The project must run in a Python 3 virtual environment.
- Dependencies must be installable through `requirements.txt`.
- No Docker/container setup should be required for submission.
- GraphDB and Protégé setup must be documented for any machine where they are installed.
- Existing Django/React behavior should not be broken while adding TP2 compliance.
- Changes should be incremental and easy to review.
- Generated RDF files should be reproducible from `spotify_songs.csv`.

## 7. Current TP2 Status Summary

| Requirement | Status | Evidence / Notes |
|---|---|---|
| Python/Django app | Done | `music_kg_project/` exists with API views/routes. |
| React UI | Done | `music-kg-frontend/` exists with multiple routed pages. |
| RDF data | Done | `music_kg.nt`, `music_kg.rdf` exist. |
| RDFS/OWL ontology | Partial | `ontology.ttl` exists but needs expansion. |
| SPARQL SELECT | Done | `/api/sparql/` exists. |
| SPARQL UPDATE | Done/Partial | `/api/sparql/update/` exists; needs documentation/control. |
| GraphDB | Partial | Code exists in `rdf_store.py`; dependency/docs/testing missing. |
| Protégé workflow | Missing | No validation instructions yet. |
| Facts-only RDF file | Missing | `facts_only.nt` does not exist. |
| Integrated ontology+facts file | Partial | `music_kg.rdf` exists, but no explicit TP2 filename. |
| SPIN rules | Missing | Current inference is Python, not SPIN. |
| SPARQLWrapper | Missing | Not in requirements or code. |
| DBpedia integration | Partial | `owl:sameAs` generated locally; no endpoint query. |
| Wikidata integration | Missing | No evidence in code. |
| RDFa/microformats | Missing | No semantic markup in React pages. |
| TP2 report | Missing | No report file. |
| TP2 checklist | Missing | No checklist file. |

## 8. Milestones

### Milestone 1: Documentation and Submission Baseline

Goal: establish the project roadmap and produce the first deliverable checklist.

Tasks:

- Keep `prd.md` updated as source of truth.
- Keep `integration.md` updated as technical setup/integration guide.
- Create `tp2_checklist.md`.
- Add `requests` to backend requirements if GraphDB code uses it.
- Document current status and exact missing TP2 items.

### Milestone 2: RDF Deliverable Files

Goal: produce the required data files for GraphDB and Protégé.

Tasks:

- Update `convert_to_rdf.py` or add an export script.
- Generate:
  - `facts_only.nt`
  - `ontology.ttl`
  - `music_kg_integrated.rdf` or `.ttl`
- Verify files contain triples.
- Document generation commands.

### Milestone 3: GraphDB Runtime

Goal: make GraphDB the documented semantic repository.

Tasks:

- Verify GraphDB repository creation/import.
- Confirm API queries use GraphDB when available.
- Keep `rdflib` fallback documented as fallback only.
- Add smoke checks for GraphDB-backed endpoints.

### Milestone 4: Ontology Expansion and Protégé

Goal: improve the ontology and validate it in Protégé.

Tasks:

- Add richer classes/properties/classifications.
- Add labels and comments.
- Open and validate ontology/integrated graph in Protégé.
- Document validation steps.

### Milestone 5: SPIN Rules

Goal: implement required inference rules as SPIN in an independent module.

Tasks:

- Create SPIN module.
- Export `spin_rules.ttl`.
- Link rules to ontology/classes where applicable.
- Demonstrate inferred relationships/classifications in app or SPARQL queries.

### Milestone 6: DBpedia/Wikidata Enrichment

Goal: expand data using external SPARQL endpoints.

Tasks:

- Add `SPARQLWrapper`.
- Query DBpedia and/or Wikidata.
- Generate enrichment triples.
- Include external URIs and metadata in artist/genre pages.

### Milestone 7: RDFa and Microformats

Goal: publish semantic data in web pages.

Tasks:

- Add RDFa/microdata to artist, album, and track components.
- Validate rendered HTML includes semantic attributes.
- Document examples in the report.

### Milestone 8: Final Report and Verification

Goal: prepare final TP2 submission.

Tasks:

- Write `tp2_report.md` in the required order.
- Run backend smoke tests.
- Run frontend build.
- Verify GraphDB and Protégé instructions.
- Verify required files exist.

