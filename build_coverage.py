#!/opt/homebrew/bin/python3.11
"""Deeside in Data: mobile and broadband coverage from Ofcom Connected Nations (1 Nov 2026).

Inputs: Ofcom Connected Nations zips unpacked in ~/deeside-data/src/ofcom (spring 2026 update, January 2026 data).
Outputs in ~/deeside-data:
  coverage.json          Flintshire v Wales and rank among the 22 Welsh councils, mobile and broadband
  broadband/<DISTRICT>.json   broadband by postcode for Flintshire's postcode districts, for the postcode checkers
Re-run when Ofcom publishes a new update (three times a year), after changing RELEASE and the file names below.
Note: Ofcom publishes mobile coverage by council area, not by postcode, so the postcode checker covers broadband only.
"""
import csv, json
from pathlib import Path

HOME = Path.home()
SRC = HOME / "deeside-data" / "src" / "ofcom"
OUT = HOME / "deeside-data"
RELEASE = "January 2026 (Ofcom Connected Nations spring 2026 update)"
MOB = SRC / "202601_mobile_coverage" / "202601_mobile_coverage_laua_r01.csv"
FIXED_DIR = SRC / "202601_fixed_broadband_coverage_and_full_fibre_take-up (v2)"
FIX = FIXED_DIR / "202601_fixed_laua_coverage_r1" / "202601_fixed_laua_coverage_r1.csv"
PC_FILES = [FIXED_DIR / "202601_fixed_pc_coverage" / "postcode_files_r2" / f"202601_fixed_pc_coverage_r2_{a}.csv" for a in ("CH", "LL")]
# Postcode districts that are wholly or partly in Flintshire
DISTRICTS = ("CH4", "CH5", "CH6", "CH7", "CH8", "LL11", "LL12", "LL18", "LL19")


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))


def welsh(rs, code_key="laua"):
    return [r for r in rs if r[code_key].startswith("W06")]


def measure(rs, name_key, weight_key, fn, better="high"):
    """Flintshire value, Wales premises-weighted value, rank among the 22 councils."""
    vals = {r[name_key].title(): fn(r) for r in rs}
    w = {r[name_key].title(): num(r[weight_key]) for r in rs}
    wales = sum(vals[k] * w[k] for k in vals) / sum(w.values())
    f = vals["Flintshire"]
    rank = 1 + sum(1 for v in vals.values() if (v > f if better == "high" else v < f))
    order = sorted(vals.items(), key=lambda kv: kv[1], reverse=(better == "high"))
    return {"flintshire": round(f, 1), "wales": round(wales, 1), "rank": rank, "of": len(vals),
            "best": {"name": order[0][0], "value": round(order[0][1], 1)},
            "worst": {"name": order[-1][0], "value": round(order[-1][1], 1)}}


def main():
    mob = welsh(rows(MOB))
    fix = welsh(rows(FIX))
    assert len(mob) == 22 and len(fix) == 22, (len(mob), len(fix))
    m = {
        "4g_in_all": dict(label="Homes and businesses with indoor 4G from all four networks", unit="%",
                          **measure(mob, "laua_name", "prem_count", lambda r: num(r["4G_prem_in_4"]))),
        "4g_in_none": dict(label="Homes and businesses with no indoor 4G from any network", unit="%",
                           **measure(mob, "laua_name", "prem_count", lambda r: num(r["4G_prem_in_0"]), better="low")),
        "4g_geo_all": dict(label="Land area with outdoor 4G from all four networks", unit="%",
                           **measure(mob, "laua_name", "pixel_count", lambda r: num(r["4G_geo_out_4"]))),
        "5g_out_any": dict(label="Homes and businesses with outdoor 5G from at least one network", unit="%",
                           **measure(mob, "laua_name", "prem_count", lambda r: 100 - num(r["5G_high_confidence_prem_out_0"]))),
        "gigabit": dict(label="Homes and businesses that can get gigabit broadband", unit="%",
                        **measure(fix, "laua_name", "All Premises", lambda r: num(r["Gigabit availability (% premises)"]))),
        "full_fibre": dict(label="Homes and businesses that can get full fibre", unit="%",
                           **measure(fix, "laua_name", "All Premises", lambda r: num(r["Full Fibre availability (% premises)"]))),
        "under_10": dict(label="Homes and businesses that cannot get 10Mbit/s broadband", unit="%",
                         **measure(fix, "laua_name", "All Premises", lambda r: num(r["% of premises unable to receive 10Mbit/s"]), better="low")),
    }
    fl = [r for r in fix if r["laua_name"].title() == "Flintshire"][0]
    fm = [r for r in mob if r["laua_name"].title() == "Flintshire"][0]
    counts = {"premises": int(num(fl["All Premises"])),
              "under_10_premises": int(num(fl["Number of premises unable to receive 10Mbit/s"])),
              "no_decent_premises": int(num(fl["Number of premises unable to receive decent broadband from fixed or FWA"])),
              "gigabit_premises": int(num(fl["Number of premises with Gigabit availability"])),
              "no_4g_indoor_premises": round(num(fm["4G_prem_in_0"]) / 100 * num(fm["prem_count"]))}
    json.dump({"release": RELEASE, "source": "Ofcom Connected Nations", "measures": m, "counts": counts},
              open(OUT / "coverage.json", "w"), ensure_ascii=False, indent=1)
    print("coverage:", {k: (v["flintshire"], v["wales"], v["rank"]) for k, v in m.items()}, counts)

    # Broadband by postcode, split by district: {postcode: [gigabit %, superfast (30Mbit/s+) %, % unable to get 10Mbit/s, % >=300Mbit/s]}
    (OUT / "broadband").mkdir(exist_ok=True)
    by = {d: {} for d in DISTRICTS}
    for p in PC_FILES:
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            pc = r["postcode_space"].strip().upper()
            d = pc.split(" ")[0]
            if d in by:
                by[d][pc.replace(" ", "")] = [round(num(r["Gigabit availability (% premises)"])), round(num(r["SFBB availability (% premises)"])),
                                              round(num(r["% of premises unable to receive 10Mbit/s"])),
                                              round(num(r["% of premises with >=300Mbit/s download speed"]))]
    for d, pcs in by.items():
        json.dump({"release": RELEASE, "fields": ["gigabit", "superfast", "under10", "300plus"], "postcodes": pcs},
                  open(OUT / "broadband" / f"{d}.json", "w"), separators=(",", ":"))
    print("broadband postcodes:", {d: len(v) for d, v in by.items()})


if __name__ == "__main__":
    main()
