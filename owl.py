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
from functools import lru_cache, reduce
from operator import or_

# Others
from rdflib import Graph

# Config
from config import DISTINCT, OWLF

# Types
from typing import Dict, NamedTuple, Set

CACHE_SIZE = 2 << 16  # noqa: WPS432
EMPTY = ""
PID = "pid"

G = Graph().parse(OWLF.as_posix(), format="n3")  # noqa: WPS111

Other = NamedTuple(
    "Other", [(PID, str), ("name", str), ("url", str), ("decs", str)],
)

EO = Other(EMPTY, EMPTY, EMPTY, EMPTY)

Person = NamedTuple(
    "Person",
    [
        (PID, str),
        ("firstname", str),
        ("lastname", str),
        ("job_title", str),
        ("homepage", str),
        ("works_at_name", str),
        ("works_at_url", str),
        ("works_on_name", str),
        ("works_on_url", str),
        ("works_on_decs", str),
        ("from_", str),
    ],
)

EP = Person(
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY
)


@lru_cache(maxsize=CACHE_SIZE)
def build_others() -> Dict[str, Other]:
    """Build others cache."""
    return dict(
        map(
            lambda other: (
                lambda otherd: (
                    str(otherd.get(PID, EMPTY)),
                    Other(
                        str(otherd.get(PID, EMPTY)),
                        str(
                            otherd.get(
                                "name",
                                otherd.get(
                                    "title", otherd.get("label", EMPTY)
                                ),
                            )
                        ),
                        str(otherd.get("url", otherd.get("url2", EMPTY))),
                        str(otherd.get("desc", EMPTY)),
                    ),
                )
            )(other.asdict()),
            G.query(
                "select distinct ?pid ?name ?title ?label ?url ?url2 ?desc "
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
                "optional {?pid sdso:mayAnswer ?qid} "
                "optional {?pid <http://xmlns.com/foaf/0.1/name> ?name} "
                "optional {?pid <http://purl.org/dc/terms/title> ?title} "
                "optional {?pid rdfs:label ?label} "
                "optional {"
                "?pid <http://dev.poderopedia.com/vocab/hasURL> ?url"
                "} "
                "optional {"
                "?pid sdso:hasDocumentURL ?url2"
                "} "
                "optional {"
                "?pid <http://purl.org/dc/terms/description> ?desc"
                "} "
                "}",
            ),
        )
    )


@lru_cache(maxsize=CACHE_SIZE)
def get_works(works_at_id: str, works_on_id: str) -> Dict[str, str]:
    """Get works information by works pid."""
    return (
        lambda works_at, works_on: {
            "works_at_name": works_at.name,
            "works_at_url": works_at.url,
            "works_on_name": works_on.name,
            "works_on_url": works_on.url,
            "works_on_decs": works_on.decs,
        }
    )(build_others().get(works_at_id, EO), build_others().get(works_on_id, EO))


@lru_cache(maxsize=CACHE_SIZE)
def build_persons() -> Dict[str, Person]:
    """Build persons cache."""
    return dict(
        map(
            lambda person: (
                lambda persond: (
                    str(persond.get(PID, EMPTY)),
                    (
                        Person(
                            str(persond.get(PID, EMPTY)),
                            str(persond.get("firstname", EMPTY)),
                            str(persond.get("lastname", EMPTY)),
                            " ".join(
                                re.findall(  # handle
                                    # Scientist-Ecosystem or
                                    # ScientistEcosystem to
                                    r"([A-Z][a-z,]*)",
                                    #  Scientist Ecosystem
                                    str(persond.get("job_title", EMPTY)),
                                )
                            ),
                            str(persond.get("homepage", EMPTY)),
                            from_=EMPTY,
                            **get_works(
                                str(persond.get("works_at", EMPTY)),
                                str(persond.get("works_on", EMPTY)),
                            ),
                        )
                    ),
                )
            )(person.asdict()),
            G.query(
                "select ?pid "
                "?firstname ?lastname ?job_title "
                "?homepage ?works_on ?works_at ?qid "
                "where {"
                "?pid rdf:type <http://xmlns.com/foaf/0.1/Person> . "
                "optional {?pid sdso:holdsJobTitle ?job_title } "
                "optional {?pid sdso:worksAt ?works_at } "
                "optional {?pid sdso:worksOn ?works_on } "
                "optional {"
                "?pid <http://xmlns.com/foaf/0.1/firstName> ?firstname "
                "} "
                "optional {"
                "?pid <http://xmlns.com/foaf/0.1/homepage> ?homepage "
                "} "
                "optional {"
                "?pid <http://xmlns.com/foaf/0.1/lastName> ?lastname "
                "} "
                "} "
                "order by ?pid"
            ),
        )
    )


def by_person(text: str) -> Set[Person]:
    """Query persons by Person may_answer."""
    return set(
        map(
            lambda person: Person(
                **dict(
                    build_persons()
                    .get(str(person.asdict().get(PID, EMPTY)), EP)
                    ._asdict(),
                    from_="self may answer",
                ),
            ),
            G.query(
                "select distinct ?pid where {"
                f'?pidt ?is "{text}"^^xsd:string .'
                "?pid sdso:mayAnswer ?pidt . "
                "?pid rdf:type <http://xmlns.com/foaf/0.1/Person>"
                "}"
            ),
        )
    )


def by_other(text: str) -> Set[Person]:
    """Query persons by Other may_answer."""
    return set(
        map(
            lambda ans: (
                lambda pid, pido: Person(
                    **dict(
                        build_persons().get(pid, EP)._asdict(),
                        from_=f"from {build_others().get(pido, EO).name}",
                    ),
                )
            )(
                str(ans.asdict().get(PID, EMPTY)),
                str(ans.asdict().get("pido", EMPTY)),
            ),
            G.query(
                "select distinct ?pid ?pido where {"
                f'?pidt ?is "{text}"^^xsd:string . '
                "?pido sdso:mayAnswer ?pidt . "
                "{?pid sdso:worksAt ?pido} "
                "union"
                "{?pid sdso:worksOn ?pido} "
                "}"
            ),
        )
    )


def by_address(text: str) -> Set[Person]:
    """Query persons by Person may answer address."""
    return reduce(
        or_,
        map(
            lambda pida: (lambda qtext: by_other(qtext) | by_person(qtext))(
                pida.asdict().get("text", "")
            ),
            G.query(
                "select distinct ?text where {"
                f'?pidt ?is "{text}"^^xsd:string . '
                "?pida sdso:addresses ?pidt . "
                "{?pida sdso:ntkText ?text} "
                "union"
                "{?pida sdso:journalisticQuestion ?text}"
                "}"
            ),
        ),
        set(),
    )


def query(text: str) -> Set[Person]:
    """Query owl graph."""
    return set(
        map(
            lambda person: DISTINCT
            and Person(**dict(person._asdict(), from_=""))
            or person,
            reduce(
                or_,
                map(
                    lambda func: func(text), (by_person, by_other, by_address)
                ),
                set(),
            ),
        )
    )
