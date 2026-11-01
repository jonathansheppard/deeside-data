#!/opt/homebrew/bin/python3.11
"""Deeside in Data: build numbers.json for the "Flintshire in numbers" strip (1 Nov 2026).

Reads data we already collect on the Mini, plus manual.json for yearly figures kept by hand.
Writes ~/deeside-data/numbers.json. Any source that is missing or stale is left out (logged),
so one broken feed never blanks the whole strip.
"""
import json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
OUT_DIR = HOME / "deeside-data"
NOW = datetime.now(timezone.utc)
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
# Flintshire fuel stations: postcode districts CH5 to CH8, plus Broughton (CH4 0) and Saltney (CH4 8)
FLINTS_PC = ("CH5 ", "CH6 ", "CH7 ", "CH8 ", "CH4 0", "CH4 8")


def log(*a):
    print(f"{NOW:%Y-%m-%d %H:%M}", *a, file=sys.stderr, flush=True)


def load(p):
    return json.loads(Path(p).read_text())


def nice_date(iso):
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def pct(a, b):
    return round(a / b * 100) if b else 0


def council_tax(m):
    ct = m["council_tax"]
    return {"key": "council_tax", "label": "Band D council tax", "value": f"£{ct['band_d']:,.2f}",
            "context": ct["context"], "date": ct["date"], "source": ct["source"], "link": ct["link"]}


def planning():
    d = load(HOME / "deeside-planning/data/planning.json")
    apps = d["applications"]
    app = sum(1 for a in apps if a.get("outcome") == "approved")
    ref = sum(1 for a in apps if a.get("outcome") == "refused")
    if app + ref < 20:
        raise ValueError(f"too few decisions ({app + ref})")
    return {"key": "planning", "label": "Planning applications approved", "value": f"{pct(app, app + ref)}%",
            "context": f"{app} approved and {ref} refused in the last 90 days, from {d['count']} applications",
            "date": nice_date(d["updated"]), "source": "Flintshire County Council planning register",
            "link": "https://planning.deeside.com/"}


def hygiene():
    d = load(HOME / "deeside-food-hygiene/data/fhrs.json")
    rated = [p for p in d["premises"] if p["r"] in ("0", "1", "2", "3", "4", "5")]
    five = sum(1 for p in rated if p["r"] == "5")
    low = sum(1 for p in rated if p["r"] in ("0", "1", "2"))
    return {"key": "hygiene", "label": "Food outlets rated 5", "value": f"{pct(five, len(rated))}%",
            "context": f"{five:,} of {len(rated):,} rated places in Flintshire; {low} are rated 2 or below",
            "date": nice_date(d["updated"]), "source": "Food Standards Agency",
            "link": "https://hygiene.deeside.com/"}


def fuel():
    d = load(HOME / "deeside-fuel-prices/stations.json")
    fresh = NOW - timedelta(days=30)  # "updated" is when the price last changed, so allow a month
    st = [s for s in d["stations"]
          if (s.get("postcode") or "").upper().startswith(FLINTS_PC) and s.get("unleaded")
          and datetime.fromisoformat(s["updated"].replace("Z", "+00:00")) >= fresh]
    if not st:
        raise ValueError("no Flintshire stations with a price from the last 30 days")
    best = min(st, key=lambda s: s["unleaded"])
    name = best["name"].title().strip()
    return {"key": "fuel", "label": "Cheapest unleaded in Flintshire", "value": f"{best['unleaded']:.1f}p",
            "context": f"At {name}. UK average {d['nationalAvg']['unleaded']:.1f}p",
            "date": nice_date(d["lastUpdated"]), "source": "GOV.UK Fuel Finder scheme",
            "link": "https://www.deeside.com/fuel-price-map/"}


def crime():
    d = load(HOME / "deeside-crime-dashboard/data/index.json")
    months = {m["month"]: m["total"] for m in d["months"]}
    latest = d["latest_available"]
    y, mo = map(int, latest.split("-"))
    tot = months[latest]
    prev = months.get(f"{y - 1}-{mo:02d}")
    ctx = f"Crimes and anti-social behaviour reported in Flintshire in {MONTHS[mo - 1]} {y}"
    if prev:
        diff = tot - prev
        ctx += f", {abs(diff):,} {'more' if diff > 0 else 'fewer'} than a year earlier" if diff else ", the same as a year earlier"
    return {"key": "crime", "label": f"Crimes reported, {MONTHS[mo - 1]}", "value": f"{tot:,}",
            "context": ctx, "date": nice_date(d["updated"]), "source": "data.police.uk",
            "link": "https://www.deeside.com/police-and-crime/"}


def trains():
    d = load(HOME / "rail-tracker/export-hsp/widget.json")
    days = d["days"][-7:]
    tt = sum(x["timetabled"] for x in days)
    ran = sum(x["ran"] for x in days)
    w3 = sum(x["within_3"] for x in days)
    canc = sum(x["cancelled"] for x in days)
    if not tt:
        raise ValueError("no timetabled trains")
    return {"key": "trains", "label": "Borderlands trains on time", "value": f"{pct(w3, tt)}%",
            "context": f"Wrexham to Bidston trains within 3 minutes of time over the last 7 days; {canc} of {tt} cancelled",
            "date": nice_date(days[-1]["day"]), "source": "National Rail performance data",
            "link": "https://www.deeside.com/wrexham-bidston-line/"}


def main():
    manual = load(OUT_DIR / "manual.json")
    out = []
    for name, fn in [("council_tax", lambda: council_tax(manual)), ("planning", planning), ("hygiene", hygiene),
                     ("fuel", fuel), ("crime", crime), ("trains", trains)]:
        try:
            out.append(fn())
        except Exception as e:
            log(f"skipped {name}: {e}")
    if len(out) < 3:
        log("fewer than 3 numbers, not writing")
        sys.exit(1)
    data = {"updated": NOW.isoformat(timespec="seconds"), "numbers": out}
    (OUT_DIR / "numbers.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    log(f"wrote {len(out)} numbers")


if __name__ == "__main__":
    main()
