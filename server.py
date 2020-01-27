#!/usr/bin/env python
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
# Standard Library
from secrets import token_urlsafe

# Others
import aiohttp_cors
from aiohttp import web
from aiohttp.web import Request, Response
from db import load, save
from elasticsearch import Elasticsearch

# Config
from config import INDEX, RETURN_SIZE

# Types
from typing import Any, Dict


async def search(key: str, filter_: str = "",) -> Dict[str, Any]:
    """Search function."""
    es = Elasticsearch()
    return (
        lambda res, db: {
            "total": res["hits"]["total"],
            "results": db[1]
            + list(
                filter(
                    lambda hit: (
                        hit.get("_id") in db[0]
                        and hit.get("_source", {}).get("title", "") == filter_
                    )
                    or not filter_,
                    res["hits"]["hits"],
                )
            ),
        }
    )(
        es.search(
            index=INDEX,
            body={"size": RETURN_SIZE, "query": {"match": {"content": key}}},
        ),
        await load(key),
    )


async def who(req: Request) -> Response:
    """Handle who is it."""
    c = req.cookies.get("who", token_urlsafe(16))
    res = web.Response(text="Hello, " + c)
    res.set_cookie("who", c)
    return res


async def rate(req: Request) -> Response:
    """Handle rate request."""
    data = await req.json()
    return web.json_response(
        {
            "status": (
                await save(
                    data.get("query", ""),
                    data.get("ans", {}),
                    data.get("rate", 0),
                    req.cookies.get("who"),
                )
            )
            and 0
            or 1
        }
    )


async def get_query_handle(req: Request) -> Response:
    """Handle request."""
    query = req.rel_url.query
    key = query.get("key", "")
    filter = query.get("filter", "")
    print(key)
    return web.json_response(await search(key, filter))


async def post_query_handle(req: Request) -> Response:
    """Handle request."""
    data = await req.json()
    return web.json_response(
        await search(data.get("key", ""), data.get("filter", ""))
    )


def main() -> None:
    """Main function."""
    app = web.Application()
    app.add_routes(
        [
            web.post("/", post_query_handle),
            web.get("/q", get_query_handle),
            web.get("/", who),
            web.post("/rate", rate),
        ]
    )
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


if __name__ == "__main__":
    main()
