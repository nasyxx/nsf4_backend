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

# Others
from elasticsearch import Elasticsearch, NotFoundError
from tqdm import tqdm

# Config
from config import BASE, DOCS, INDEX

# Types
from typing import Dict, Generator, Tuple


def index(es: Elasticsearch, body: Dict[str, str]) -> Dict[str, str]:
    """Index `body` content."""
    return es.index(index=INDEX, doc_type="doc", body=body)


def paragraph(
    base: str, docs: Tuple[str, ...],
) -> Generator[Tuple[str, str], None, None]:
    """Get paragraph of docs."""
    for doc in docs:
        with open(os.path.join(base, doc), errors="ignore") as f:
            for para in f:
                yield (para, os.path.basename(doc).rstrip(".txt"))


def main() -> None:
    """Main function."""
    es = Elasticsearch()
    es.indices.exists(INDEX) and es.indices.delete(INDEX)

    for para, title in tqdm(paragraph(BASE, DOCS)):
        para and index(es, {"content": para, "title": title})

    es.indices.refresh(INDEX)


if __name__ == "__main__":
    main()
