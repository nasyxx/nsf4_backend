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
date     : Dec 25, 2019
email    : Nasy <nasyxx+python@gmail.com>
filename : build_index.py
project  : nsf_es_backend
license  : GPL-3.0+

At pick'd leisure
  Which shall be shortly, single I'll resolve you,
Which to you shall seem probable, of every
  These happen'd accidents
                          -- The Tempest
"""
# Standard Library
import os
from csv import DictReader
from pathlib import Path

# Others
from elasticsearch import Elasticsearch
from tika import parser
from tqdm import tqdm

# Config
from config import BASE, DOCS, FD, INDEX

# Types
from typing import Dict, Generator, Set, Tuple

Doc = Tuple[str, str, str]
DONE = set()  # type: Set[Tuple[str, str]]
EMPTY = ""


def index(es: Elasticsearch, body: Dict[str, str]) -> Dict[str, str]:
    """Index `body` content."""
    return es.index(index=INDEX, doc_type="doc", body=body)


def walk(paths: FD) -> Generator[str, None, None]:
    """Walk though dir."""
    yield from map(lambda path: path.as_posix(), paths.f)
    for dir_path in paths.d:
        for (dirpath, dirnames, filenames) in os.walk(dir_path):
            yield from (
                os.sep.join([dirpath, filename]) for filename in filenames
            )


def wq_para(docs: FD) -> Generator[Doc, None, None]:
    """Water quality para generator."""
    for doc in filter(lambda path: path.endswith(".csv"), walk(docs)):
        print(f"\n{doc}", end="", file=tqdm)
        with open(doc, errors="ignore") as doc_file:
            yield from (
                (
                    doc_item.get("Abstract", EMPTY),
                    doc_item.get("Title", EMPTY),
                    Path(doc).relative_to(BASE).as_posix(),
                )
                for doc_item in DictReader(doc_file)
            )


def all_para(docs: FD) -> Generator[Doc, None, None]:
    """All para generator with tika."""
    for doc in filter(
        lambda path: path.endswith(".docx")
        or path.endswith(".txt")
        or path.endswith(".pdf"),
        walk(docs),
    ):
        print(f"{doc}", end="", file=tqdm)
        yield from (
            (
                para,
                os.path.basename(doc)
                .rstrip(".docx")
                .rstrip(".txt")
                .rstrip(".pdf"),
                Path(doc).relative_to(BASE).as_posix(),
            )
            for para in str(
                parser.from_file(doc).get("content", EMPTY)
            ).splitlines()
        )


def read_docs() -> Generator[Doc, None, None]:
    """Read all docs as single paragraph."""
    yield from all_para(DOCS.normal)
    yield from wq_para(DOCS.csv)


def main() -> None:
    """Main function."""
    es = Elasticsearch()
    es.indices.exists(INDEX) and es.indices.delete(INDEX)  # noqa: WPS428

    for para, title, path in tqdm(
        read_docs(),
        desc="Elasticsearch Index",
        unit="paragraph",
        total=1603143,  # noqa: WPS432
    ):
        if (para, title) not in DONE:
            para and index(  # noqa: WPS428
                es, {"content": para, "title": title, "path": path}
            )
        DONE.add((para, title))

    es.indices.refresh(INDEX)


if __name__ == "__main__":
    main()
