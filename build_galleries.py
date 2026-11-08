#!/opt/homebrew/bin/python3.11
"""Geograph photo galleries for the town guides -> ~/deeside-data/galleries/<slug>/*.jpg and <slug>.json

Geograph photos are CC BY-SA 2.0: reusable for any purpose if each photo credits its photographer and says it is
CC licensed (https://www.geograph.org.uk/faq3.php?q=reuse). We copy the small thumbnails to our own site rather than
loading them from Geograph's servers, and link every photo to its Geograph page.

  build_galleries.py            build all
  build_galleries.py mold       build one
"""
import collections, json, sys, time, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(__file__).with_name("galleries")
API = "https://api.geograph.org.uk/api-facetql.php"
UA = {"User-Agent": "Deeside.com town guides (contact jon@deeside.com)"}
PER_GUIDE, PER_SQUARE = 9, 2
KEYLEN = 25  # heritage guides use the whole title
GUIDES = {  # slug: (search words, accepted Geograph place names start with...)
    "mold": (["Mold"], ["Mold"]),
    "flint": (["Flint"], ["Flint/", "Flint"]),
    "shotton-queensferry": (["Shotton", "Queensferry"], ["Shotton", "Queensferry", "Garden City"]),
    "connahs-quay": (["Connah's Quay"], ["Connah's Quay"]),
    "buckley": (["Buckley"], ["Buckley"]),
    "hawarden-ewloe": (["Hawarden", "Ewloe"], ["Har", "Haw", "Ewloe"]),
    "broughton": (["Broughton"], ["Broughton"]),
    "saltney": (["Saltney"], ["Saltney"]),
}


def fix(t):
    try:
        return t.encode("latin-1").decode("utf-8") if "â" in t else t
    except UnicodeError:
        return t


def get(params):
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def thumb_url(pid, h):
    pid = int(pid)
    ab, cd = f"{(pid % 1000000) // 10000:02d}", f"{(pid % 10000) // 100:02d}"
    if pid < 1000000:
        return f"https://s0.geograph.org.uk/photos/{ab}/{cd}/{pid:06d}_{h}_213x160.jpg"
    return f"https://s0.geograph.org.uk/geophotos/{pid // 1000000:02d}/{ab}/{cd}/{pid:06d}_{h}_213x160.jpg"


GOOD = ("church", "castle", "high street", "station", "park", "memorial", "market", "river", "hall", "library", "square",
        "chapel", "inn", "pub", "bridge", "dee", "view", "town", "centre", "cross", "clock", "theatre", "museum", "lake",
        "wood", "estuary", "airfield", "airport", "school", "street", "lane", "hill", "garden", "shop", "mill", "dock")
BAD = ("benchmark", "bench mark", "leeswood", "milestone", "layby", "lay-by", "cut mark", "trig", "slip road", "sliproad", "junction", "flush bracket",
       "bolt", "pillar", "car park", "parking", "petrol", "solicitor", "dental", "polling", "fly-tip", "deceased", "grave", "tattoo", "crossing", "barber", "footpath", "service road", "street light", "#", "rear of", "destruction", "demolition", "roadworks", "sign", "manhole", "post box", "postbox", "bus stop", "rivet", "boundary stone", "a55", "a494")


def score(r, words):
    t = (r.get("title") or "").lower() + " " + (r.get("imageclass") or "").lower()
    if any(b in t for b in BAD):
        return None
    sc = sum(2 for g in GOOD if g in t)
    sc += 3 if any(w.lower() in (r.get("title") or "").lower() for w in words) else 0
    sc += 1 if r.get("format") == "landscape" else 0
    yr = int(r.get("takenyear") or 0)
    sc += 2 if yr >= 2015 else (1 if yr >= 2005 else 0)
    return sc


def build(slug):
    words, places = GUIDES[slug]
    rows = {}
    for w in words:
        got = []
        for off in (0, 500):
            d = get({"select": "id,title,realname,hash,takenyear,place,county,grid_reference,format,imageclass", "match": f"{w} @county Flintshire", "limit": 500, "offset": off})
            got += d.get("rows", [])
            if len(d.get("rows", [])) < 500:
                break
            time.sleep(1)
        for r in got:
            inplace = any((r.get("place") or "").startswith(p) for p in places)
            t = fix(r.get("title") or "")
            r["title"] = t
            others = [x for g, (ws, _) in GUIDES.items() if g != slug for x in ws]
            intitle = w.lower() in t.lower() and not any(o.lower() in t.lower() for o in others)
            if r.get("county") == "Flintshire" and r.get("hash") and (inplace or intitle):
                rows[r["id"]] = r
        time.sleep(1)
    scored = [(score(r, words), r) for r in rows.values()]
    ranked = [r for sc, r in sorted([x for x in scored if x[0] is not None], key=lambda x: (x[0], int(x[1]["id"])), reverse=True)]
    picked, per_sq, seen = [], collections.Counter(), set()
    for r in ranked:
        key = (r.get("title") or "").lower().split(",")[0][:KEYLEN] if KEYLEN < 100 else (r.get("title") or "").lower()
        if per_sq[r["grid_reference"]] >= PER_SQUARE or key in seen:
            continue
        per_sq[r["grid_reference"]] += 1
        seen.add(key)
        picked.append(r)
        if len(picked) == PER_GUIDE:
            break
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.jpg"):
        old.unlink()
    items = []
    for r in picked:
        req = urllib.request.Request(thumb_url(r["id"], r["hash"]), headers=UA)
        with urllib.request.urlopen(req, timeout=60) as resp:
            (d / f'{r["id"]}.jpg').write_bytes(resp.read())
        items.append({"id": r["id"], "title": r["title"], "by": r["realname"], "year": r.get("takenyear"),
                      "img": f"https://jonathansheppard.github.io/deeside-data/galleries/{slug}/{r['id']}.jpg",
                      "link": f"https://www.geograph.org.uk/photo/{r['id']}"})
        time.sleep(0.5)
    (OUT / f"{slug}.json").write_text(json.dumps({"slug": slug, "found": len(rows), "photos": items}, indent=1, ensure_ascii=False))
    print(f"{slug}: {len(rows)} Flintshire photos found, {len(items)} picked")


if __name__ == "__main__":
    for s in (sys.argv[1:] or GUIDES):
        build(s)
