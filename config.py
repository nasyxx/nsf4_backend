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
date     : Jan 28, 2020
email    : Nasy <nasyxx+python@gmail.com>
filename : config.py
project  : nsf_es_backend
license  : GPL-3.0+

At pick'd leisure
  Which shall be shortly, single I'll resolve you,
Which to you shall seem probable, of every
  These happen'd accidents
                          -- The Tempest
"""
# Standard Library
from itertools import chain
from pathlib import Path

# Types
from typing import Iterable, NamedTuple

Paths = Iterable[Path]
FD = NamedTuple("FD", [("f", Paths), ("d", Paths)])
Docs = NamedTuple("Docs", [("normal", FD), ("csv", FD)])


# Editable below:

RETURN_SIZE = 100
COOKIE_LENGTH = 16
DB_PATH = "db"

INDEX = "all"

BASE = Path("../data")

DOCS = Docs(
    normal=FD(
        f=map(
            lambda path: BASE / path,
            chain(
                # Add txt/docx/pdf files here.
                # They Should be iterable objects.
                # For example:
                # map(
                #     lambda path: "docs" / path,
                #     (
                #         "Pacific-Northwe...sign_June15-1.txt",
                #         "CCLC-Targets-KE...1.txt",
                #         "WORKING LANDS A...Chehalis_2Nov2018.txt",
                #         "CONSERVATIONAND...rch2019.txt",
                #         "PlanningToolsAs....txt",
                #     ),
                # ),
            ),
        ),
        d=map(
            lambda path: BASE / path,
            chain(
                # Add txt/docx/pdf folders here.
                # They Should be iterable objects.
                (
                    "docs",
                    "drive-download-20200127T161340Z-001",
                    "gis-wildfire",
                ),
            ),
        ),
    ),
    csv=FD(
        f=map(
            lambda path: BASE / path,
            chain(
                # Add csv files here.
                # They Should be iterable objects.
                # For example:
                ("water_quality.csv",)
            ),
        ),
        d=map(
            lambda path: BASE / path,
            chain(
                # Add csv folders here.
                # They Should be iterable objects.
                # For example:
                # ("water_quality",)
            ),
        ),
    ),
)
