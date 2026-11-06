#!/opt/homebrew/bin/python3.11
"""Deeside in Data: Flintshire road collisions (STATS19) -> collisions.json for collisions.html

Source: DfT road casualty statistics, collision and casualty files for the last 5 years
(https://www.data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-accidents-safety-data, OGL v3).
Injury collisions reported to police only: damage-only crashes aren't in it.

  cd ~/stats19 && curl -O .../dft-road-casualty-statistics-collision-last-5-years.csv  (and the casualty file)
  ~/deeside-data/build_collisions.py
"""
import csv, json, math, collections
from pathlib import Path

SRC = Path.home() / "stats19"
OUT = Path(__file__).with_name("collisions.json")
LA = "W06000005"  # Flintshire
ROAD_CLASS = {"1": "M", "2": "A", "3": "A", "4": "B", "5": "C"}
SEV = {"1": "fatal", "2": "serious", "3": "slight"}
MOTORCYCLE = {"2", "3", "4", "5", "23", "97"}

col = {r["collision_index"]: r for r in csv.DictReader(open(SRC / "collisions-5y.csv", encoding="utf-8-sig"))
       if r["local_authority_ons_district"] == LA}
cas = collections.defaultdict(list)
for r in csv.DictReader(open(SRC / "casualties-5y.csv", encoding="utf-8-sig")):
    if r["collision_index"] in col:
        cas[r["collision_index"]].append(r)


def road(cls, num):
    if cls in ROAD_CLASS and num not in ("0", "-1", ""):
        return ROAD_CLASS[cls] + num
    return "Minor road"


items = []
for cid, r in col.items():
    try:
        lat, lon = round(float(r["latitude"]), 5), round(float(r["longitude"]), 5)
    except ValueError:
        continue
    cs = cas.get(cid, [])
    d, m, y = r["date"].split("/")
    items.append({
        "y": int(r["collision_year"]), "d": f"{y}-{m}-{d}", "t": r["time"], "s": SEV.get(r["collision_severity"], "slight"),
        "lat": lat, "lon": lon, "road": road(r["first_road_class"], r["first_road_number"]),
        "road2": road(r["second_road_class"], r["second_road_number"]) if r["second_road_class"] not in ("-1", "0", "") else "",
        "limit": r["speed_limit"] if r["speed_limit"] not in ("-1", "99") else "",
        "veh": int(r["number_of_vehicles"]), "cas": int(r["number_of_casualties"]),
        "killed": sum(c["casualty_severity"] == "1" for c in cs),
        "seriously": sum(c["casualty_severity"] == "2" for c in cs),
        "ped": sum(c["casualty_class"] == "3" for c in cs),
        "cyc": sum(c["casualty_type"] == "1" for c in cs),
        "moto": sum(c["casualty_type"] in MOTORCYCLE for c in cs),
        "child": sum(c["age_of_casualty"].isdigit() and int(c["age_of_casualty"]) < 16 for c in cs),
    })
items.sort(key=lambda x: (x["d"], x["t"]))

years = sorted({x["y"] for x in items})
by_year = []
for y in years:
    xs = [x for x in items if x["y"] == y]
    by_year.append({"y": y, "collisions": len(xs), "fatal": sum(x["s"] == "fatal" for x in xs),
                    "serious": sum(x["s"] == "serious" for x in xs), "killed": sum(x["killed"] for x in xs),
                    "seriously": sum(x["seriously"] for x in xs), "casualties": sum(x["cas"] for x in xs)})

roads = collections.defaultdict(lambda: {"collisions": 0, "ksi": 0, "killed": 0})
for x in items:
    if x["road"] == "Minor road":
        continue
    rd = roads[x["road"]]
    rd["collisions"] += 1
    rd["ksi"] += x["s"] in ("fatal", "serious")
    rd["killed"] += x["killed"]
top_roads = sorted(({"road": k, **v} for k, v in roads.items()), key=lambda r: (-r["collisions"], -r["ksi"]))[:12]

# Hotspots: collisions within ~250 m of each other (greedy clustering), at least 4
pts = sorted(items, key=lambda x: (x["lat"], x["lon"]))
used, spots = set(), []
def dist(a, b):
    return math.hypot((a["lat"] - b["lat"]) * 111_000, (a["lon"] - b["lon"]) * 111_000 * math.cos(math.radians(53.2)))
for i, a in enumerate(pts):
    if i in used:
        continue
    group = [j for j, b in enumerate(pts) if j not in used and dist(a, b) <= 250]
    if len(group) < 4:
        continue
    lat = sum(pts[j]["lat"] for j in group) / len(group)
    lon = sum(pts[j]["lon"] for j in group) / len(group)
    group = [j for j, b in enumerate(pts) if j not in used and math.hypot((b["lat"] - lat) * 111_000, (b["lon"] - lon) * 66_600) <= 250]
    if len(group) < 4:
        continue
    used.update(group)
    gx = [pts[j] for j in group]
    rds = collections.Counter(r for x in gx for r in (x["road"], x["road2"]) if r and r != "Minor road")
    spots.append({"lat": round(lat, 5), "lon": round(lon, 5), "n": len(gx),
                  "ksi": sum(x["s"] in ("fatal", "serious") for x in gx),
                  "roads": [r for r, _ in rds.most_common(2)]})
spots.sort(key=lambda s: (-s["n"], -s["ksi"]))
import urllib.request
for sp in spots[:15]:
    try:
        u = f"https://api.postcodes.io/postcodes?lon={sp['lon']}&lat={sp['lat']}&limit=1&radius=1000"
        r = json.load(urllib.request.urlopen(u, timeout=20))["result"] or []
        sp["place"] = (r[0].get("parish") or r[0].get("admin_ward") or "").replace(" (Flintshire)", "") if r else ""
    except Exception:
        sp["place"] = ""

out = {"source": "Department for Transport road casualty statistics (STATS19), OGL v3",
       "area": "Flintshire", "years": [years[0], years[-1]], "by_year": by_year,
       "top_roads": top_roads, "hotspots": spots[:15], "collisions": items}
OUT.write_text(json.dumps(out, separators=(",", ":")))
print(len(items), "collisions;", by_year[-1], ";", len(spots), "hotspots; top", top_roads[:3])
