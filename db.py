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
date     : Jan 10, 2020
email    : Nasy <nasyxx+python@gmail.com>
filename : db.py
project  : nsf_es_backend
license  : GPL-3.0+

At pick'd leisure
  Which shall be shortly, single I'll resolve you,
Which to you shall seem probable, of every
  These happen'd accidents
                          -- The Tempest

-----------

Save:

{
 "query":
  {para_id:
   [
    {
     "_id": para_id,
     "rate": ...,
     "user": ...,
     ... other things in elasticsearch returns.
    }
   ]
  }
}

-----------

Load:

(
 set(para_ids),
 list[para with the calculated score.]
)

"""
# Standard Library
import shelve

# Config
from config import DB_PATH

# Types
from typing import Any, Dict, List, Set, Tuple, Union


async def save(query: str, ans: Dict[str, Any], rate: int, user: str) -> bool:
    """Save the query and rate."""
    print(f"{query, ans, user, rate=}")
    if query and ans and user and (rate > 0):
        with shelve.open(DB_PATH) as db:
            datum = db.get(query, {ans["_id"]: []})
            datum[ans["_id"]].append({**ans, **{"rate": rate, "user": user}})
            db[query] = datum
        return True
    else:
        return False


def calc(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculated score."""
    return {
        **data[0],
        **{"rate": sum(map(lambda d: d["rate"], data)) / len(data)},
    }


async def load(query: str) -> Tuple[Set[str], List[Dict[str, Any]]]:
    """Load saved query ans."""
    with shelve.open(DB_PATH) as db:
        return (
            lambda d: (
                set(d.keys()),
                sorted(map(calc, d.values()), key=lambda q: q["rate"]),
            )
        )(db.get(query, {}))
