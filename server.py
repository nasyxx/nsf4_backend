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
import aiohttp_cors
from aiohttp import web
from aiohttp.web import Request, Response
from elasticsearch import Elasticsearch

# Types
from typing import Any, Dict


async def search(key: str, filter_: str = "",) -> Dict[str, Any]:
    """Search function."""
    es = Elasticsearch()
    return (
        lambda res: {
            "total": res["hits"]["total"],
            "results": list(
                filter(
                    lambda hit: hit.get("_source", {}).get("title", "")
                    == filter_
                    or not filter_,
                    res["hits"]["hits"],
                )
            ),
        }
    )(
        es.search(
            index="nsf4",
            body={"size": 10000, "query": {"match": {"content": key}}},
        )
    )


async def get_handle(req: Request) -> Response:
    """Handle request."""
    query = req.rel_url.query
    key = query.get("key", "")
    filter = query.get("filter", "")
    print(key)
    return web.json_response(await search(key, filter))


async def post_handle(req: Request) -> Response:
    """Handle request."""
    data = await req.post()
    return web.json_response(
        await search(data.get("key", ""), data.get("filter", ""))
    )


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.post("/", post_handle), web.get("/q", get_handle)])
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*",
            )
        },
    )
    for route in app.router.routes():
        cors.add(route)
    web.run_app(app)
