# TP2 Checklist

## Current status

- Milestone 1 dependency updates are complete for the local RDF/GraphDB path.
- Milestone 2 RDF delivery exports are complete:
  - ontology-only Turtle
  - facts-only N-Triples
  - integrated ontology + facts RDF/XML for Protégé
- Milestone 4 ontology expansion is complete:
  - added derived classes for audio profiles, high-energy tracks, popular tracks, release eras, modern tracks, and classic tracks
  - added ontology properties for audio profiles, release eras, energy levels, and popularity levels
  - added labels, comments, subclass links, domain/range declarations, inverse properties, and symmetric property declarations
- Milestone 5 SPIN rules are complete:
  - generated independent SPIN-compatible rules in `music_kg_project/data/spin_rules.ttl`
  - rules cover `music:performs`, symmetric `music:similarTo`, high-energy track classification, popular-track classification, and release-era classification
- Deferred for later milestones:
  - DBpedia/Wikidata live enrichment through SPARQLWrapper
  - RDFa/microformats

## Generated files

Generated under `music_kg_project/data/`:

- `ontology.ttl` - ontology/schema only.
- `facts_only.nt` - facts/data only, excluding the ontology named graph.
- `music_kg_integrated.rdf` - ontology + facts in RDF/XML for Protégé.
- `music_kg.nt` - existing full graph N-Triples export, preserved.
- `music_kg.rdf` - existing full graph RDF/XML export, preserved.
- `stats.json` - generation statistics, preserved.
- `spin_rules.ttl` - SPIN-compatible rule definitions for TP2 inference.

## Regenerate RDF

From the project root:

```bash
.venv/bin/python convert_to_rdf.py --csv spotify_songs.csv --data-dir music_kg_project/data/
```

Latest result:

```text
total_triples: 761580
ontology triples: 173
artists graph triples: 71930
albums graph triples: 103640
tracks graph triples: 585837
similarity_links: 30948
inference_triples_added: 51387
```

## Generate SPIN rules

From the project root:

```bash
.venv/bin/python music_kg_project/music_graph/spin_rules.py --output music_kg_project/data/spin_rules.ttl
```

Latest result:

```text
Wrote music_kg_project/data/spin_rules.ttl (30 triples)
```

## Parse verification

From the project root:

```bash
.venv/bin/python - <<'PY'
from rdflib import Graph

checks = [
    ("music_kg_project/data/ontology.ttl", "turtle"),
    ("music_kg_project/data/spin_rules.ttl", "turtle"),
    ("music_kg_project/data/music_kg_integrated.rdf", "xml"),
]

for path, fmt in checks:
    graph = Graph()
    graph.parse(path, format=fmt)
    print(f"{path}: {len(graph)} triples")
PY
```

Latest result:

```text
music_kg_project/data/ontology.ttl: 173 triples
music_kg_project/data/spin_rules.ttl: 30 triples
music_kg_project/data/music_kg_integrated.rdf: 761580 triples
```
