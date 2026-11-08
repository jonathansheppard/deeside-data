#!/usr/bin/env python3
"""Geograph galleries for the heritage guides (castles, abbey, wells, crosses).

Uses build_galleries.build() with its own list, so a photo of "Flint Castle" is not thrown out for
mentioning a town that has its own town guide. Photos must name the site in the title.

  build_heritage.py            build all
  build_heritage.py flint-castle
"""
import sys
import build_galleries as B

HERITAGE = {  # slug: (search phrases, place prefixes; empty = title must name the site)
    "talacre-lighthouse": (['"Talacre"', '"Point of Ayr"'], []),
    "flint-castle": (['"Flint Castle"'], []),
    "greenfield-valley": (['"Greenfield Valley"'], []),
    "st-winefrides-well": (['"St Winefride"', '"Winefride\'s Well"'], []),
    "basingwerk-abbey": (['"Basingwerk"'], []),
    "hawarden-old-castle": (['"Hawarden Castle"', '"Hawarden Old Castle"'], []),
    "ewloe-castle": (['"Ewloe Castle"'], []),
    "caergwrle-castle": (['"Caergwrle Castle"'], []),
    "bailey-hill-mold": (['"Bailey Hill"'], []),
    "wats-dyke": (['"Wat\'s Dyke"', '"Wats Dyke"'], []),
    "maen-achwyfan": (['"Maen Achwyfan"'], []),
}

# build() checks the title for the search word without quotes
B.PER_SQUARE, B.KEYLEN = 9, 999
B.GUIDES = {k: ([w.strip('"') for w in ws], p) for k, (ws, p) in HERITAGE.items()}
_get = B.get


def get(params):
    m = params.get("match", "")
    w = m.replace(" @county Flintshire", "")
    if " " in w and not w.startswith('"'):
        params = {**params, "match": f'"{w}" @county Flintshire'}
    return _get(params)


B.get = get

# Per-site tuning: titles with BOOST words rank higher, titles with SKIP words are dropped
BOOST = {"talacre-lighthouse": ("lighthouse", "beach", "dunes", "point of ayr"), "hawarden-old-castle": ("old castle", "keep", "ruin"),
         "basingwerk-abbey": ("abbey",), "flint-castle": ("castle", "tower"), "wats-dyke": ("dyke",)}
SKIP = {"talacre-lighthouse": ("train", "station", "smuggler", "colliery"), "hawarden-old-castle": ("b5125", "glynne arms", "mushroom", "millstone"),
        "basingwerk-abbey": ("llanasa",), "wats-dyke": ("avenue", "bungalow")}
_score, _build = B.score, B.build
CUR = {"slug": None}


def score(r, words):
    t = (r.get("title") or "").lower()
    if any(x in t for x in SKIP.get(CUR["slug"], ())):
        return None
    sc = _score(r, words)
    if sc is None:
        return None
    return sc + sum(4 for x in BOOST.get(CUR["slug"], ()) if x in t)


def build(slug):
    CUR["slug"] = slug
    return _build(slug)


B.score, B.build = score, build

if __name__ == "__main__":
    for s in (sys.argv[1:] or B.GUIDES):
        B.build(s)
