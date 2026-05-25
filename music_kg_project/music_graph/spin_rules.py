"""
Generate SPIN-compatible inference rules for the Music Knowledge Graph.

The rules are exported as Turtle and kept independent from the ETL script so
they can be inspected, imported into GraphDB/Protégé, or regenerated on demand.
"""

from __future__ import annotations

import argparse
import os

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef


MUSIC = Namespace("http://musickg.org/ontology#")
SPIN = Namespace("http://spinrdf.org/spin#")
SP = Namespace("http://spinrdf.org/sp#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")


DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "spin_rules.ttl",
)


def add_construct_rule(
    graph: Graph,
    owner_class: URIRef,
    rule_uri: URIRef,
    label: str,
    comment: str,
    construct_text: str,
) -> None:
    graph.add((owner_class, SPIN.rule, rule_uri))
    graph.add((rule_uri, RDF.type, SPIN.Rule))
    graph.add((rule_uri, RDF.type, SP.Construct))
    graph.add((rule_uri, RDFS.label, Literal(label)))
    graph.add((rule_uri, RDFS.comment, Literal(comment)))
    graph.add((rule_uri, SP.text, Literal(construct_text.strip())))


def build_spin_rules() -> Graph:
    graph = Graph()
    graph.bind("music", MUSIC)
    graph.bind("spin", SPIN)
    graph.bind("sp", SP)
    graph.bind("xsd", XSD)
    graph.bind("rdfs", RDFS)

    add_construct_rule(
        graph,
        MUSIC.Artist,
        MUSIC.InferPerformsFromAlbumTracksRule,
        "Infer performs from albums and tracks",
        "Infers music:performs when an artist has an album and that album has a track.",
        """
        PREFIX music: <http://musickg.org/ontology#>
        CONSTRUCT {
          ?artist music:performs ?track .
        }
        WHERE {
          ?artist music:hasAlbum ?album .
          ?album music:hasTrack ?track .
        }
        """,
    )

    add_construct_rule(
        graph,
        MUSIC.Artist,
        MUSIC.InferSymmetricSimilarToRule,
        "Infer symmetric similarTo links",
        "Infers the reverse music:similarTo relation for artist similarity links.",
        """
        PREFIX music: <http://musickg.org/ontology#>
        CONSTRUCT {
          ?right music:similarTo ?left .
        }
        WHERE {
          ?left music:similarTo ?right .
          FILTER (?left != ?right)
        }
        """,
    )

    add_construct_rule(
        graph,
        MUSIC.Track,
        MUSIC.ClassifyHighEnergyTrackRule,
        "Classify high energy tracks",
        "Classifies tracks as music:HighEnergyTrack when their audio profile energy is at least 0.75.",
        """
        PREFIX music: <http://musickg.org/ontology#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        CONSTRUCT {
          ?track a music:HighEnergyTrack .
          ?profile music:energyLevel "High" .
        }
        WHERE {
          ?track music:hasAudioProfile ?profile .
          ?profile music:energy ?energy .
          FILTER (xsd:decimal(?energy) >= 0.75)
        }
        """,
    )

    add_construct_rule(
        graph,
        MUSIC.Track,
        MUSIC.ClassifyPopularTrackRule,
        "Classify popular tracks",
        "Classifies tracks as music:PopularTrack when their popularity score is at least 70.",
        """
        PREFIX music: <http://musickg.org/ontology#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        CONSTRUCT {
          ?track a music:PopularTrack .
          ?track music:popularityLevel "High" .
        }
        WHERE {
          ?track music:popularity ?popularity .
          FILTER (xsd:integer(?popularity) >= 70)
        }
        """,
    )

    add_construct_rule(
        graph,
        MUSIC.Track,
        MUSIC.ClassifyReleaseEraRule,
        "Classify release eras",
        "Classifies albums and tracks into broad release eras using album release years.",
        """
        PREFIX music: <http://musickg.org/ontology#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        CONSTRUCT {
          ?album music:belongsToEra ?era .
          ?track music:belongsToEra ?era .
          ?track a ?trackClass .
        }
        WHERE {
          ?album music:hasTrack ?track ;
                 music:releaseYear ?year .
          BIND(xsd:integer(?year) AS ?releaseYear)
          BIND(
            IF(?releaseYear >= 2010, <http://musickg.org/era/Modern_Era>,
              IF(?releaseYear < 2000, <http://musickg.org/era/Classic_Era>, <http://musickg.org/era/Transition_Era>)
            ) AS ?era
          )
          BIND(
            IF(?releaseYear >= 2010, music:ModernTrack,
              IF(?releaseYear < 2000, music:ClassicTrack, music:Track)
            ) AS ?trackClass
          )
        }
        """,
    )

    return graph


def write_spin_rules(output_path: str = DEFAULT_OUTPUT) -> int:
    graph = build_spin_rules()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    graph.serialize(destination=output_path, format="turtle")
    return len(graph)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Music KG SPIN rules")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output Turtle file")
    args = parser.parse_args()

    triple_count = write_spin_rules(args.output)
    print(f"Wrote {args.output} ({triple_count} triples)")


if __name__ == "__main__":
    main()
