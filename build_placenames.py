#!/opt/homebrew/bin/python3.11
"""Deeside in Data: historic place names for Flintshire -> placenames/<tile>.json for placenames.html

Source: List of Historic Place Names of Wales (RCAHMW), via DataMap Wales WFS, OGL.
Historic county of Flintshire (so it includes Maelor and the Rhuddlan area).
Split into 0.05-degree tiles so the lookup page only loads the area around a postcode.
"""
import json, math, urllib.parse, urllib.request, collections
from pathlib import Path

WFS = "https://datamap.gov.wales/geoserver/ows"
OUT = Path(__file__).with_name("placenames")
TILE = 0.05
TYPES = {"Field": "field", "Settlement": "settlement", "Topographic feature": "feature",
         "Unclassified": "other", "Other administrative area": "area", "Civil Parish": "parish"}

feats, start = [], 0
while True:
    q = {"service": "WFS", "version": "2.0.0", "request": "GetFeature",
         "typeNames": "geonode:rcahmw_historicplacenames_wales_recordednames", "count": 5000, "startIndex": start,
         "outputFormat": "application/json", "srsName": "EPSG:4326", "CQL_FILTER": "county='Flintshire'",
         "sortBy": "enw_name",
         "propertyName": "enw_name,place_type,blwgyn_eye,discy_pdes,parish,prim_srce,url_en,loc_conf,geom"}
    with urllib.request.urlopen(WFS + "?" + urllib.parse.urlencode(q), timeout=120) as r:
        page = json.load(r)["features"]
    feats += page
    print("fetched", len(feats))
    if len(page) < 5000:
        break
    start += 5000

tiles = collections.defaultdict(list)
for f in feats:
    p, g = f["properties"], f.get("geometry")
    if not g or p.get("loc_conf") == "Within 10km":
        continue
    lon, lat = g["coordinates"][:2]
    key = f"{math.floor(lat / TILE)}_{math.floor(lon / TILE)}"
    tiles[key].append([round(lat, 5), round(lon, 5), p["enw_name"], TYPES.get(p["place_type"], "other"),
                       p.get("discy_pdes") or "", p.get("parish") or "", p.get("prim_srce") or "",
                       (p.get("url_en") or "").rsplit("/", 1)[-1]])
OUT.mkdir(exist_ok=True)
for old in OUT.glob("*.json"):
    old.unlink()
for k, rows in tiles.items():
    (OUT / f"{k}.json").write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")))
(OUT / "index.json").write_text(json.dumps({"updated": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"), "tile": TILE, "count": sum(map(len, tiles.values())), "tiles": sorted(tiles)}))
print(len(feats), "names,", len(tiles), "tiles")
