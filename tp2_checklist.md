# TP2 Checklist

## Current status

- Milestone 1 dependency updates are complete for the local RDF/GraphDB path.
- Milestone 2 RDF delivery exports are complete:
  - ontology-only Turtle
  - facts-only N-Triples
  - integrated ontology + facts RDF/XML for Protégé
- Deferred for later milestones:
  - SPIN rules
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

## Regenerate RDF

From the project root:

```bash
python convert_to_rdf.py --csv spotify_songs.csv --data-dir music_kg_project/data/
```

## Parse verification

From the project root:

```bash
python - <<'PY'
from rdflib import Graph

checks = [
    ("music_kg_project/data/ontology.ttl", "turtle"),
    ("music_kg_project/data/facts_only.nt", "nt"),
    ("music_kg_project/data/music_kg_integrated.rdf", "xml"),
]

for path, fmt in checks:
    graph = Graph()
    graph.parse(path, format=fmt)
    print(f"{path}: {len(graph)} triples")
PY
```
