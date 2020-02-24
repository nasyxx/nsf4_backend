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
import sys
from secrets import token_urlsafe

# Others
import aiohttp_cors
import db
from aiohttp import web
from aiohttp.web import Request, Response
from elasticsearch import Elasticsearch
from loguru import logger
from owl import person_to_dict
from owl import query as owl_query

# Config
from config import COOKIE_LENGTH, INDEX, RETURN_SIZE, STOPWORDS

# Types
from typing import Any, Dict

EMPTY = ""
COOKIEN = "who"

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time}</green>\t<level>{message}</level>",
)
logger.add("logs", format="{time}\t{message}")


async def search(key: str, filter_: str = EMPTY) -> Dict[str, Any]:
    """Search function."""
    es = Elasticsearch()
    return (
        lambda res, db_res: {
            "total": res["hits"]["total"],
            "results": db_res[1]
            + list(
                filter(
                    lambda hit: (
                        hit.get("_id") in db_res[0]
                        and hit.get("_source", {}).get("title", "") == filter_
                    )
                    or not filter_,
                    res["hits"]["hits"],
                )
            ),
            "query": key,
        }
    )(
        es.search(
            index=INDEX,
            body={"size": RETURN_SIZE, "query": {"match": {"content": key}}},
        ),
        await db.load(key),
    )


async def who(req: Request) -> Response:
    """Handle who is it."""
    user = req.cookies.get(COOKIEN, token_urlsafe(COOKIE_LENGTH))
    res = web.Response(text=f"Hello, {user}")
    res.set_cookie(COOKIEN, user)
    return res


async def rate(req: Request) -> Response:
    """Handle rate request."""
    rate_data = await req.json()
    logger.info(
        f"{req.cookies.get('who', 'Unknow User')}\trate\t"
        f"|{rate_data.get('query', EMPTY)}|\t{rate_data.get('rate', 0)}",
    )
    return web.json_response(
        {
            "status": (
                await db.save(
                    rate_data.get("query", EMPTY),
                    rate_data.get("ans", {}),
                    rate_data.get("rate", 0),
                    req.cookies.get(COOKIEN),
                )
            )
            and 0
            or 1
        }
    )


async def get_query_handle(req: Request) -> Response:
    """Handle request."""
    query = req.rel_url.query
    no_stop_words = query.get("nsw", "false")
    filter_text = query.get("filter", EMPTY)
    key = (
        lambda kw: " ".join(
            filter(lambda word: word.lower() not in STOPWORDS, kw.split())
        )
        if no_stop_words == "true"
        else kw
    )(query.get("key", EMPTY))
    logger.info(
        f"{req.cookies.get(COOKIEN, 'Unknow User')}"
        f"\tsearch\t|{key}|\t{filter_text}"
    )
    return web.json_response(await search(key, filter_text))


async def get_person_query_handle(req: Request) -> Response:
    """Handle person query."""
    key = req.rel_url.query.get("key", EMPTY)
    logger.info(
        f"{req.cookies.get(COOKIEN, 'Unknow User')}" f"\tsearch_person\t|{key}"
    )
    return web.json_response(list(map(person_to_dict, owl_query(key))))


async def post_query_handle(req: Request) -> Response:
    """Handle request."""
    query_data = await req.json()
    return web.json_response(
        await search(
            query_data.get("key", EMPTY), query_data.get("filter", EMPTY)
        )
    )


def main() -> None:
    """Main function."""
    app = web.Application()
    app.add_routes(
        [
            web.post("/", post_query_handle),
            web.get("/q", get_query_handle),
            web.get("/pq", get_person_query_handle),
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
