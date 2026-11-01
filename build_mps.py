#!/opt/homebrew/bin/python3.11
"""Deeside in Data: Flintshire's MPs for the "Your area" lookup (1 Nov 2026).

Writes ~/deeside-data/mps.json keyed by ONS constituency code (as postcodes.io returns it).
Sources: UK Parliament Members API and Commons Votes API. Rebuilt weekly (Mondays 07:06).
Voting record: Commons divisions the MP voted in since the 2024 general election, out of all Commons divisions.
"""
import json, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path.home() / "deeside-data" / "mps.json"
SINCE = "2024-07-17"   # first sitting day of the 2024 Parliament
# Constituencies covering Flintshire (ONS code: name as Parliament spells it)
SEATS = {"W07000082": "Alyn and Deeside", "W07000094": "Clwyd East"}
UA = {"User-Agent": "Deeside.com data (news@deeside.com)", "Accept": "application/json"}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))


def main():
    out = {}
    total = get(f"https://commonsvotes-api.parliament.uk/data/divisions.json/searchTotalResults?queryParameters.startDate={SINCE}")
    for code, name in SEATS.items():
        s = get("https://members-api.parliament.uk/api/Location/Constituency/Search?searchText=" + urllib.parse.quote(name))
        seat = next(i["value"] for i in s["items"] if i["value"]["name"] == name)
        m = seat["currentRepresentation"]["member"]["value"]
        mid = m["id"]
        contact = get(f"https://members-api.parliament.uk/api/Members/{mid}/Contact")["value"]
        bio = get(f"https://members-api.parliament.uk/api/Members/{mid}/Biography")["value"]
        posts = [p["name"] for k in ("governmentPosts", "oppositionPosts", "otherPosts") for p in bio.get(k, []) if not p.get("endDate")]
        cttees = [p["name"] for p in bio.get("committeeMemberships", []) if not p.get("endDate")]
        voted = get(f"https://commonsvotes-api.parliament.uk/data/divisions.json/searchTotalResults?queryParameters.startDate={SINCE}&queryParameters.memberId={mid}")
        recent = get(f"https://commonsvotes-api.parliament.uk/data/divisions.json/membervoting?queryParameters.memberId={mid}&queryParameters.take=5")
        office = next((c for c in contact if c.get("type") == "Constituency office"), None)
        parl = next((c for c in contact if c.get("type") == "Parliamentary office"), None)
        web = next((c["line1"] for c in contact if c.get("isWebAddress") and "twitter" not in (c.get("line1") or "").lower() and "x.com" not in (c.get("line1") or "")), "")
        out[code] = {
            "constituency": name,
            "id": mid,
            "name": m["nameDisplayAs"],
            "party": (m.get("latestParty") or {}).get("name", ""),
            "colour": "#" + ((m.get("latestParty") or {}).get("backgroundColour") or "888888"),
            "photo": m.get("thumbnailUrl", ""),
            "posts": posts,
            "committees": cttees,
            "email": (parl or {}).get("email") or "",
            "phone": (office or {}).get("phone") or (parl or {}).get("phone") or "",
            "office": ", ".join(x for x in [(office or {}).get("line1"), (office or {}).get("line2"), (office or {}).get("postcode")] if x) if (office or {}).get("postcode") else "",
            "website": web,
            "profile": f"https://members.parliament.uk/member/{mid}/contact",
            "votes": {"voted": voted, "of": total, "since": SINCE},
            "recent": [{"title": v["PublishedDivision"]["Title"], "date": v["PublishedDivision"]["Date"][:10],
                        "vote": "Aye" if v.get("MemberVotedAye") else "No",
                        "teller": bool(v.get("MemberWasTeller")),
                        "url": f"https://votes.parliament.uk/votes/commons/division/{v['PublishedDivision']['DivisionId']}"} for v in recent],
        }
        print(f"{name}: {out[code]['name']} ({out[code]['party']}), voted in {voted} of {total}")
    if len(out) != len(SEATS):
        sys.exit("missing a constituency, not writing")
    OUT.write_text(json.dumps({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               "source": "UK Parliament Members API and Commons Votes API", "seats": out}, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
