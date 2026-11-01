#!/opt/homebrew/bin/python3.11
"""Deeside in Data: councillors by ward for the "Your area" lookup (1 Nov 2026).

Reads Flintshire's ModernGov web service (GetCouncillorsByWard) and writes ~/deeside-data/councillors.json.
Only work details are kept: name, party, key posts, council email, photo and profile link.
Home phone numbers and addresses are left out on purpose.
Ward keys are normalised (lower case, letters and spaces only, "and" dropped) so they can be
matched to the ward names postcodes.io returns ("Pen-y-ffordd" and "Penyffordd" both become "penyffordd").
"""
import html, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

URL = "https://committeemeetings.flintshire.gov.uk/mgWebService.asmx/GetCouncillorsByWard"
BASE = "https://committeemeetings.flintshire.gov.uk"
OUT = Path.home() / "deeside-data" / "councillors.json"


def key(name):
    s = html.unescape(name).lower().replace("&", " and ")
    s = re.sub(r"[^a-z ]", " ", s.replace("'", "").replace("’", ""))
    return "".join(w for w in s.split() if w != "and")


def txt(el, tag):
    v = el.findtext(tag) or ""
    return html.unescape(html.unescape(v)).strip()


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Deeside.com data (news@deeside.com)"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=60).read())
    wards = {}
    for w in root.iter("ward"):
        title = txt(w, "wardtitle")
        if not title:
            continue
        cllrs = []
        for c in w.iter("councillor"):
            cid = txt(c, "councillorid")
            name = re.sub(r"^Cllr\.?\s+", "", txt(c, "fullusername"))
            photo = txt(c, "photosmallurl").replace("http://", "https://")
            cllrs.append({
                "name": name,
                "party": txt(c, "politicalpartytitle"),
                "posts": txt(c, "keyposts"),
                "email": (c.findtext("workaddress/email") or "").strip(),
                "photo": photo,
                "url": f"{BASE}/mgUserInfo.aspx?UID={cid}" if cid else "",
            })
        wards[key(title)] = {"ward": title, "councillors": cllrs}
    if len(wards) < 30:
        print(f"only {len(wards)} wards, not writing", file=sys.stderr)
        sys.exit(1)
    OUT.write_text(json.dumps({
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Flintshire County Council (ModernGov)",
        "wards": wards,
    }, ensure_ascii=False, indent=1) + "\n")
    print(f"{datetime.now():%F %R} wrote {len(wards)} wards, {sum(len(w['councillors']) for w in wards.values())} councillors")


if __name__ == "__main__":
    main()
