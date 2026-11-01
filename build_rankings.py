#!/usr/bin/env python3
"""Deeside in Data: "Where Flintshire ranks" (1 Nov 2026).
Figures copied from StatsWales and Nomis on 1 Nov 2026. Re-run with new figures when each source updates.
Rank 1 = best for residents (lowest council tax, highest recycling, highest attendance, highest employment, cleanest air)."""
import json
M = [
 {"key": "council_tax", "label": "Band D council tax", "period": "2026/27", "unit": "£", "dp": 2, "better": "low",
  "note": "Average Band D bill including police and community councils",
  "source": "Welsh Government (StatsWales)", "wales": 2283.08,
  "v": {"Isle of Anglesey": 2260.73, "Gwynedd": 2468.77, "Conwy": 2472.82, "Denbighshire": 2339.03, "Flintshire": 2376.17,
        "Wrexham": 2308.88, "Powys": 2351.72, "Ceredigion": 2419.45, "Pembrokeshire": 2166.15, "Carmarthenshire": 2351.20,
        "Swansea": 2238.29, "Neath Port Talbot": 2541.39, "Bridgend": 2477.99, "Vale of Glamorgan": 2231.54,
        "Rhondda Cynon Taf": 2289.43, "Merthyr Tydfil": 2593.60, "Caerphilly": 2082.88, "Blaenau Gwent": 2531.26,
        "Torfaen": 2155.68, "Monmouthshire": 2416.50, "Newport": 2088.48, "Cardiff": 2013.18}},
 {"key": "recycling", "label": "Waste reused, recycled or composted", "period": "2024/25", "unit": "%", "dp": 1, "better": "high",
  "note": "Statutory recycling rate. The Welsh target is 70%",
  "source": "Welsh Government (StatsWales)", "wales": 68.39,
  "v": {"Isle of Anglesey": 65.00, "Gwynedd": 65.31, "Conwy": 70.69, "Denbighshire": 68.55, "Flintshire": 63.18, "Wrexham": 65.09,
        "Powys": 70.49, "Ceredigion": 70.29, "Pembrokeshire": 73.53, "Carmarthenshire": 71.38, "Swansea": 71.73,
        "Neath Port Talbot": 71.40, "Bridgend": 71.42, "Vale of Glamorgan": 71.10, "Cardiff": 64.01, "Rhondda Cynon Taf": 71.01,
        "Merthyr Tydfil": 66.33, "Caerphilly": 61.64, "Blaenau Gwent": 68.89, "Torfaen": 65.43, "Monmouthshire": 72.27, "Newport": 71.40}},
 {"key": "attendance", "label": "Secondary school attendance", "period": "2024/25", "unit": "%", "dp": 1, "better": "high",
  "note": "Share of possible half-day sessions attended by secondary-age pupils",
  "source": "Welsh Government (StatsWales)", "wales": None,
  "v": {"Isle of Anglesey": 88.2, "Gwynedd": 88.8, "Conwy": 88.0, "Denbighshire": 87.6, "Flintshire": 90.3, "Wrexham": 89.0,
        "Powys": 89.8, "Ceredigion": 90.0, "Pembrokeshire": 89.0, "Carmarthenshire": 87.2, "Swansea": 90.0, "Neath Port Talbot": 88.3,
        "Bridgend": 89.0, "Vale of Glamorgan": 89.1, "Rhondda Cynon Taf": 88.0, "Merthyr Tydfil": 88.8, "Caerphilly": 89.5,
        "Blaenau Gwent": 89.1, "Torfaen": 89.0, "Monmouthshire": 89.5, "Newport": 89.3, "Cardiff": 90.0}},
 {"key": "employment", "label": "People aged 16 to 64 in work", "period": "July 2025 to June 2026", "unit": "%", "dp": 1, "better": "high",
  "note": "Employment rate from the Annual Population Survey, a sample survey, so small changes may not be meaningful",
  "source": "ONS Annual Population Survey (Nomis)", "wales": None,
  "v": {"Isle of Anglesey": 76.7, "Gwynedd": 74.2, "Conwy": 71.2, "Denbighshire": 73.6, "Flintshire": 78.4, "Wrexham": 70.8,
        "Powys": 78.9, "Ceredigion": 74.6, "Pembrokeshire": 75.7, "Carmarthenshire": 75.0, "Swansea": 68.4, "Neath Port Talbot": 73.5,
        "Bridgend": 68.6, "Vale of Glamorgan": 74.0, "Cardiff": 75.0, "Rhondda Cynon Taf": 69.7, "Merthyr Tydfil": 68.4,
        "Caerphilly": 72.1, "Blaenau Gwent": 65.1, "Torfaen": 75.7, "Monmouthshire": 77.0, "Newport": 76.3}},
 {"key": "pm25", "label": "Fine particle air pollution (PM2.5)", "period": "2024", "unit": "µg/m³", "dp": 2, "better": "low",
  "note": "Average population exposure to PM2.5",
  "source": "Welsh Government (StatsWales)", "wales": 5.07,
  "v": {"Isle of Anglesey": 4.20, "Gwynedd": 4.26, "Conwy": 4.74, "Denbighshire": 4.89, "Flintshire": 5.52, "Wrexham": 5.55,
        "Ceredigion": 3.97, "Pembrokeshire": 3.93, "Carmarthenshire": 4.26, "Swansea": 4.81, "Neath Port Talbot": 4.83,
        "Bridgend": 4.91, "Vale of Glamorgan": 5.09, "Cardiff": 5.92, "Rhondda Cynon Taf": 5.18, "Caerphilly": 5.48,
        "Blaenau Gwent": 5.15, "Torfaen": 5.66, "Monmouthshire": 5.37, "Newport": 5.97, "Powys": 4.47, "Merthyr Tydfil": 5.06}},
]
out = []
for m in M:
    v = m.pop("v")
    assert len(v) == 22, (m["key"], len(v))
    rev = m["better"] == "high"
    order = sorted(v.items(), key=lambda kv: kv[1], reverse=rev)
    def rank(x): return 1 + sum(1 for _, y in v.items() if (y > x if rev else y < x))
    f = v["Flintshire"]; r = rank(f); joint = sum(1 for y in v.values() if y == f) > 1
    m.update({"flintshire": f, "rank": r, "joint": joint, "of": 22,
              "best": {"name": order[0][0], "value": order[0][1]}, "worst": {"name": order[-1][0], "value": order[-1][1]},
              "values": sorted(v.values(), reverse=rev)})
    out.append(m)
    print(m["key"], f, "rank", r, "joint" if joint else "")
json.dump({"updated": "2026-11-01", "measures": out}, open("rankings.json", "w"), ensure_ascii=False, indent=1)
