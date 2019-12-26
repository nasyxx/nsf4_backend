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
filename : server.py
project  : nsf_es_backend
license  : GPL-3.0+

At pick'd leisure
  Which shall be shortly, single I'll resolve you,
Which to you shall seem probable, of every
  These happen'd accidents
                          -- The Tempest
"""

# Others
from aiohttp import web
from aiohttp.web import Request, Response
from elasticsearch import Elasticsearch

# Types
from typing import Any, Callable, Dict


async def search(key: str) -> Dict[str, Any]:
    """Search function."""
    es = Elasticsearch()
    return es.search(index="nsf4", body={"query": {"match": {"content": key}}})


async def handle(req: Request) -> Response:
    """Handle request."""
    data = await req.post()
    return web.json_response(await search(data.get("key", "")))


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.post("/", handle)])
    web.run_app(app)
