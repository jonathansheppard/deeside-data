#!/opt/homebrew/bin/python3.11
"""Deeside in Data: Flintshire's 12 Members of the Senedd and how often they speak in Plenary (1 Nov 2026).

Writes ~/deeside-data/senedd.json, keyed by Senedd constituency, plus a map from UK Parliament constituency
code to Senedd constituency (each 2026 Senedd constituency is two Westminster seats joined together).
Activity comes from the Senedd's Record of Proceedings (Plenary transcripts, XML) for the Seventh Senedd
(elected 7 May 2026). Transcripts are cached in ~/deeside-data/src/senedd/xml. New sittings are found by
trying meeting IDs above the highest one already known. Rebuilt weekly (Mondays 07:07).
Member details are kept by hand below (same list as the Senedd category page); check after any change.
"""
import json, re, sys, time, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
SRC = HOME / "deeside-data" / "src" / "senedd"
XML = SRC / "xml"
OUT = HOME / "deeside-data" / "senedd.json"
URL = "https://record.assembly.wales/XMLExport/Download?meetingID={}&xmlDownloadType=EnglishTranscript"
UA = {"User-Agent": "Deeside.com data (news@deeside.com)"}
ASSEMBLY = "7"
WESTMINSTER_TO_SENEDD = {"W07000082": "Fflint Wrecsam", "W07000094": "Clwyd"}

PARTY = {"reform": ("Reform UK", "#12B6CF"), "plaid": ("Plaid Cymru", "#005B54"),
         "con": ("Welsh Conservatives", "#0087DC"), "lab": ("Welsh Labour", "#E4003B")}
MEMBERS = {
    "Fflint Wrecsam": [
        ("Cristiana Emsley", "reform", "Chair of the Senedd Legislation Committee", "Cristiana.Emsley-MS@senedd.wales", "0300 200 6353"),
        ("Nigel Williams", "reform", "Member of the Health and Social Care Committee", "Nigel.Williams-AS@senedd.cymru", "0300 200 6364"),
        ("Carrie Harper", "plaid", "Chair of the Constitution, Justice and External Affairs Committee", "Carrie.Harper-AS@senedd.cymru", "0300 200 7545"),
        ("Marc Jones", "plaid", "Member of the Local Government, Housing and Planning Committee", "Marc.Jones-AS@senedd.cymru", "0300 200 7465"),
        ("Sam Rowlands", "con", "Chair of the Senedd Finance Committee", "Sam.Rowlands-MS@senedd.wales", "0300 200 7267"),
        ("Ken Skates", "lab", "Leader of Welsh Labour", "Ken.Skates-MS@senedd.wales", "01978 869 058"),
    ],
    "Clwyd": [
        ("Adrian Mason", "reform", "Member of the Legislation Committee", "", ""),
        ("Louise Emery", "reform", "Member of the Culture, Communications, Cymraeg and Sport Committee", "", ""),
        ("Tom Montgomery", "reform", "Member of the Economy, Energy and Connectivity Committee", "", ""),
        ("Llyr Gruffydd", "plaid", "Cabinet Minister for Rural Resilience and Sustainability", "Llyr.Gruffydd-MS@senedd.wales", "01824 703 593"),
        ("Becca Martin", "plaid", "Member of the Health and Social Care Committee", "", "0300 200 7558"),
        ("Darren Millar", "con", "Leader of the Welsh Conservatives", "Darren.Millar-MS@senedd.wales", "0300 200 6206"),
    ],
}
CHAIR_TITLES = ("Llywydd", "Presiding Officer", "Deputy Presiding Officer", "Dirprwy Lywydd")


def fetch(mid):
    f = XML / f"{mid}.xml"
    if f.exists():
        return f.read_bytes()
    try:
        b = urllib.request.urlopen(urllib.request.Request(URL.format(mid), headers=UA), timeout=60).read()
    except Exception:
        return b""
    time.sleep(0.15)
    if b"<XML_Plenary_English>" in b and re.search(rb"<Assembly>" + ASSEMBLY.encode() + rb"</Assembly>", b):
        f.write_bytes(b)
        return b
    return b""


def main():
    XML.mkdir(parents=True, exist_ok=True)
    known = sorted(int(p.stem) for p in XML.glob("*.xml"))
    probe = SRC / "probe_15800.json"
    if probe.exists():
        for mid, (asm, date, size) in json.load(open(probe)).items():
            if asm == ASSEMBLY and int(mid) not in known:
                fetch(int(mid))
    known = sorted(int(p.stem) for p in XML.glob("*.xml"))
    start = (max(known) + 1) if known else 16000
    for mid in range(start, start + 250):     # look for new sittings
        fetch(mid)
    sittings = sorted(int(p.stem) for p in XML.glob("*.xml"))
    if not sittings:
        sys.exit("no Plenary transcripts")

    stats = {}       # member id -> dict
    dates = {}
    for mid in sittings:
        root = ET.fromstring(fetch(mid))
        for r in root.findall("XML_Plenary_English"):
            dates[mid] = (r.findtext("MeetingDate") or "")[:10]
            pid, name = r.findtext("Member_Id"), (r.findtext("Member_name_English") or "").strip()
            if not pid or not name:
                continue
            title = r.findtext("Member_job_title_English") or ""
            text = re.sub(r"<[^>]+>", " ", r.findtext("Contribution_English") or r.findtext("contribution_translated") or "")
            s = stats.setdefault(pid, {"name": name, "n": 0, "words": 0, "sittings": set(), "chair": 0, "last": []})
            s.setdefault("names", set()).add(name)   # the record occasionally misspells a name, so keep every spelling
            s["n"] += 1
            s["words"] += len(text.split())
            s["sittings"].add(mid)
            if any(t in title for t in CHAIR_TITLES):
                s["chair"] += 1
            s["last"].append((dates[mid], mid, r.findtext("Contribution_ID"), (r.findtext("Agenda_item_english") or "").strip()))
    import collections
    by_name_count = collections.Counter(n for s in stats.values() for n in s["names"])
    # rank by contributions, leaving out anyone who mainly chairs
    ranked = sorted((p for p, s in stats.items() if s["chair"] < s["n"] / 2), key=lambda p: -stats[p]["n"])
    by_name = {n: p for p, s in stats.items() for n in s["names"] if not (n in by_name_count and by_name_count[n] > 1)}

    out = {}
    for seat, members in MEMBERS.items():
        rows = []
        for name, party, role, email, phone in members:
            pid = by_name.get(name)
            s = stats.get(pid) if pid else None
            act = None
            if s:
                last, seen = [], set()
                for d, mid, cid, item in sorted(s["last"], reverse=True):
                    if item and item not in seen:
                        seen.add(item)
                        last.append({"date": d, "item": re.sub(r"^\d+\.\s*", "", item), "url": f"https://record.senedd.wales/Plenary/{mid}#C{cid}"})
                    if len(last) == 3:
                        break
                act = {"contributions": s["n"], "words": s["words"], "sittings": len(s["sittings"]),
                       "rank": ranked.index(pid) + 1 if pid in ranked else None, "latest": last}
            rows.append({"name": name, "party": PARTY[party][0], "colour": PARTY[party][1], "role": role,
                         "email": email, "phone": phone, "activity": act})
        out[seat] = rows
    data = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": "Senedd Record of Proceedings (Plenary), Seventh Senedd",
            "sittings": len(sittings), "first": dates[sittings[0]], "last": dates[sittings[-1]], "ranked_of": len(ranked),
            "westminster_to_senedd": WESTMINSTER_TO_SENEDD, "seats": out}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"{datetime.now():%F %R} {len(sittings)} sittings {data['first']} to {data['last']}, {len(ranked)} members ranked")
    for seat, rows in out.items():
        for r in rows:
            a = r["activity"] or {}
            print(f"  {seat}: {r['name']}: {a.get('contributions')} contributions, {a.get('sittings')} sittings, rank {a.get('rank')}")


if __name__ == "__main__":
    main()
