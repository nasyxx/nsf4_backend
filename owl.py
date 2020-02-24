#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
Life's pathetic, have fun ("▔□▔)/hi~♡ Nasy.

Excited without bugs::

    |             *         *
    |                  .                .
    |           .
    |     *                      ,
    |                   .
    |
    |                               *
    |          |\___/|
    |          )    -(             .              ·
    |         =\ -   /=
    |           )===(       *
    |          /   - \
    |          |-    |
    |         /   -   \     0.|.0
    |  NASY___\__( (__/_____(\=/)__+1s____________
    |  ______|____) )______|______|______|______|_
    |  ___|______( (____|______|______|______|____
    |  ______|____\_|______|______|______|______|_
    |  ___|______|______|______|______|______|____
    |  ______|______|______|______|______|______|_
    |  ___|______|______|______|______|______|____

author   : Nasy https://nasy.moe
date     : Feb 23, 2020
email    : Nasy <nasyxx+python@gmail.com>
filename : owl.py
project  : nsf_es_backend
license  : GPL-3.0+

At pick'd leisure
  Which shall be shortly, single I'll resolve you,
Which to you shall seem probable, of every
  These happen'd accidents
                          -- The Tempest
"""
# Standard Library
import re
from functools import lru_cache
from itertools import groupby

# Others
from rdflib import Graph, Literal, URIRef

# Config
from config import OWLF

# Types
from typing import Dict, List, NamedTuple, Optional, Set, Union

CACHE_SIZE = 0  # 2 << 16  # noqa: WPS432
EMPTYS = ""
G = Graph().parse(OWLF.as_posix(), format="n3")  # noqa: WPS111

PO = NamedTuple("PO", [("name", str), ("url", str)])

Person = NamedTuple(
    "Person",
    [
        ("firstname", str),
        ("lastname", str),
        ("job_title", str),
        ("homepage", str),
        ("works_at", Optional[PO]),
        ("works_on", Optional[PO]),
    ],
)


def person_to_dict(person: Person) -> Dict[str, Union[str, Dict[str, str]]]:
    """Person to dict."""
    return dict(
        person._asdict(),
        works_at=person._asdict()["works_at"]._asdict(),
        works_on=person._asdict()["works_on"]._asdict(),
    )


@lru_cache(maxsize=CACHE_SIZE)
def build_project_organization() -> Dict[URIRef, PO]:
    """Build project and organization informatino."""
    return dict(
        map(
            lambda ans: (
                ans.pid,
                PO(
                    str(ans.asdict().get("name", EMPTYS)),
                    str(ans.asdict().get("url", EMPTYS)),
                ),
            ),
            G.query(
                "select ?pid ?id ?name ?label ?url "
                "where {"
                "{?pid rdf:type foaf:Organization} "
                "UNION "
                "{?pid rdf:type <http://vivoweb.org/ontology/core#Project>} . "
                "?pid terms:identifier ?id . "
                "?pid foaf:name ?name . "
                "?pid rdfs:label ?label "
                "OPTIONAL {?pid vocab:hasURL ?url} "
                "}"
            ),
        )
    )


@lru_cache(maxsize=CACHE_SIZE)
def build_person() -> List[Dict[str, Union[URIRef, Literal]]]:
    """Build person infomation."""
    return list(
        map(
            lambda ans: ans.asdict(),
            G.query(
                "select distinct ?pid ?id "
                "?firstname ?lastname ?job_title "
                "?homepage ?label ?works_on ?works_at "
                "where {"
                "?pid rdf:type foaf:Person . "
                "?pid terms:identifier ?id "
                "OPTIONAL {?pid sdso:holdsJobTitle ?job_title } "
                "OPTIONAL {?pid sdso:worksAt ?works_at } "
                "OPTIONAL {?pid sdso:worksOn ?works_on } "
                "OPTIONAL {?pid foaf:firstName ?firstname } "
                "OPTIONAL {?pid foaf:homepage ?homepage } "
                "OPTIONAL {?pid foaf:lastName ?lastname } "
                "OPTIONAL {?pid rdfs:label ?label } "
                "} "
                "order by ?pid"
            ),
        )
    )


@lru_cache(maxsize=CACHE_SIZE)
def person_cache() -> Dict[str, Set[Person]]:
    """Generate person caches."""
    return dict(
        map(
            lambda keygroup: (
                keygroup[0],
                set(
                    map(
                        lambda person: Person(
                            str(person.get("firstname", EMPTYS)),
                            str(person.get("lastname", EMPTYS)),
                            re.sub(  # handle
                                # Scientist-Ecosystem or
                                # ScientistEcosystem to
                                r".*#([^-]*).*?([A-Z])",
                                #  Scientist Ecosystem
                                r"\1 \2",
                                str(person.get("job_title", EMPTYS)),
                            ).strip(),
                            str(person.get("homepage", EMPTYS)),
                            build_project_organization().get(
                                person.get("works_at"), PO(EMPTYS, EMPTYS),
                            ),
                            build_project_organization().get(
                                person.get("works_on"), PO(EMPTYS, EMPTYS)
                            ),
                        ),
                        keygroup[1],
                    )
                ),
            ),
            groupby(
                build_person(),
                lambda person: re.sub(
                    r"(.+?)(0{2}[0-9]{2})?$", r"\1", person.get("pid", EMPTYS)
                ),
            ),
        )
    )


@lru_cache(maxsize=CACHE_SIZE)
def query(query_str: str) -> Set[Person]:
    """Query owl graph."""
    return set(
        *map(
            lambda ans: person_cache().get(str(ans[0])),
            G.query(
                "select ?collection where { "
                # Find the query text id as `qid`.
                f'?qid sdso:ntkText "{query_str}"^^xsd:string . '
                # Find the base `collection` of the `qid`
                "?qid sdso:collectionInstrument ?collection "
                "}"
            ),
        ),
    )
