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
from itertools import chain

# Others
from rdflib import Graph, URIRef

# Config
from config import OWLF

# Types
from typing import Dict, Generator, NamedTuple, Set, Union

CACHE_SIZE = 2 << 16  # noqa: WPS432
EMPTYS = ""
PID = "pid"
G = Graph().parse(OWLF.as_posix(), format="n3")  # noqa: WPS111

PO = NamedTuple(
    "PO",
    [
        (PID, str),
        ("label", str),
        ("url", str),
        ("may_answer", str),
        ("creator", str),
    ],
)
EPO = PO(EMPTYS, EMPTYS, EMPTYS, EMPTYS, EMPTYS)

Person = NamedTuple(
    "Person",
    [
        (PID, str),
        ("firstname", str),
        ("lastname", str),
        ("job_title", str),
        ("homepage", str),
        ("works_at", PO),
        ("works_on", PO),
        ("may_answer", str),
    ],
)


def person_to_dict(person: Person) -> Dict[str, Union[str, Dict[str, str]]]:
    """Person to dict."""
    return dict(
        person._asdict(),
        works_at=person.works_at._asdict(),
        works_on=person.works_on._asdict(),
    )


@lru_cache(maxsize=CACHE_SIZE)
def build_other() -> Dict[URIRef, PO]:
    """Build project and organization informatino."""
    return dict(
        map(
            lambda ans: (
                lambda ansd: (
                    ansd.get(PID, EMPTYS),
                    PO(
                        str(ansd.get(PID, EMPTYS)),
                        str(
                            ansd.get(
                                "name",
                                ansd.get("title", ansd.get("label", "")),
                            )
                        ),
                        str(ansd.get("url", EMPTYS)),
                        str(ansd.get("qid", EMPTYS)),
                        str(ansd.get("creator", EMPTYS)),
                    ),
                )
            )(ans.asdict()),
            G.query(
                "select distinct ?pid ?name ?title ?label ?url ?qid ?creator "
                "where {"
                "{?pid rdf:type <http://xmlns.com/foaf/0.1/Organization>} "
                "union {"
                "?pid rdf:type ?core "
                "filter "
                "(regex(str(?core), 'http://vivoweb.org/ontology/core'))"
                "} union {"
                "?pid rdf:type ?report "
                "filter "
                "(regex(str(?report), 'http://purl.org/ontology/bibo'))"
                "} union {"
                "?pid rdf:type ?other "
                "filter "
                "(regex(str(?other), 'http://semanticscience.org/resource'))"
                "} . "
                "?pid sdso:mayAnswer ?qid . "
                "OPTIONAL {?pid <http://xmlns.com/foaf/0.1/name> ?name} "
                "OPTIONAL {?pid <http://purl.org/dc/terms/title> ?title} "
                "OPTIONAL {?pid rdfs:label ?label} "
                "OPTIONAL {"
                "?pid <http://dev.poderopedia.com/vocab/hasURL> ?url"
                "} "
                "OPTIONAL {"
                "?pid <http://purl.org/dc/terms/creator> ?creator"
                "} "
                "}",
            ),
        )
    )


@lru_cache(maxsize=CACHE_SIZE)
def build_person() -> Set[Person]:
    """Build person infomation."""
    return set(
        map(
            lambda ans: (
                lambda person: Person(
                    str(person.get(PID, EMPTYS)),
                    str(person.get("firstname", EMPTYS)),
                    str(person.get("lastname", EMPTYS)),
                    " ".join(
                        re.findall(  # handle
                            # Scientist-Ecosystem or
                            # ScientistEcosystem to
                            r"([A-Z][a-z,]*)",
                            #  Scientist Ecosystem
                            str(person.get("job_title", EMPTYS)),
                        )
                    ),
                    str(person.get("homepage", EMPTYS)),
                    build_other().get(person.get("works_at"), EPO),
                    build_other().get(person.get("works_on"), EPO),
                    str(person.get("qid", EMPTYS)),
                )
            )(ans.asdict()),
            G.query(
                "select ?pid "
                "?firstname ?lastname ?job_title "
                "?homepage ?label ?works_on ?works_at ?qid "
                "where {"
                "?pid rdf:type <http://xmlns.com/foaf/0.1/Person> . "
                "OPTIONAL {?pid sdso:holdsJobTitle ?job_title } "
                "OPTIONAL {?pid sdso:worksAt ?works_at } "
                "OPTIONAL {?pid sdso:worksOn ?works_on } "
                "OPTIONAL {"
                "?pid <http://xmlns.com/foaf/0.1/firstName> ?firstname "
                "} "
                "OPTIONAL {"
                "?pid <http://xmlns.com/foaf/0.1/homepage> ?homepage "
                "} "
                "OPTIONAL {"
                "?pid <http://xmlns.com/foaf/0.1/lastName> ?lastname "
                "} "
                "OPTIONAL {?pid rdfs:label ?label} "
                "OPTIONAL {?pid sdso:mayAnswer ?qid}"
                "} "
                "order by ?pid"
            ),
        )
    )


def filter_other(other: PO) -> Generator[Person, None, None]:
    """Filter the person from others."""
    yield from filter(
        lambda person: person.works_at == other.pid
        or person.works_on == other.pid
        or person.pid == other.creator,
        build_person(),
    )


def filtered(qid: str) -> Generator[Person, None, None]:
    """Filtered persons."""
    yield from chain(
        filter(lambda person: person.may_answer == qid, build_person()),
        *map(
            filter_other,
            filter(
                lambda other: other.may_answer == qid, build_other().values()
            ),
        ),
    )


@lru_cache(maxsize=CACHE_SIZE)
def query_by_ntktext(text: str) -> Set[str]:
    """Query by ntk Text."""
    return set(
        map(
            lambda ans: str(ans.asdict().get(PID, EMPTYS)),
            G.query(
                "select distinct ?qid where {"
                # Find the query text id as `qid`.
                f'?qid ?ntkqc "{text}"^^xsd:string'
                "}"
            ),
        )
    )


@lru_cache(maxsize=CACHE_SIZE)
def query_by_address(qid: str) -> Set[str]:
    """Querry by ntkq address to."""
    return set(
        map(
            lambda ans: str(ans.asdict().get(PID, EMPTYS)),
            G.query("select ?qid where {" f"?qid sdso:addresses <{qid}>" "}"),
        )
    )


@lru_cache(maxsize=CACHE_SIZE)
def query(query_str: str) -> Set[Person]:
    """Query owl graph."""
    return set(
        chain.from_iterable(
            map(
                filtered,
                (
                    lambda ans: ans
                    | set(chain.from_iterable(map(query_by_address, ans)))
                )(query_by_ntktext(query_str)),
            )
        )
    )
