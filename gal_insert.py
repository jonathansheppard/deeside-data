#!/opt/homebrew/bin/python3.11
"""Insert/replace the Geograph gallery in each town guide, just before 'Questions people ask'.
   gal_insert.py mold   |  gal_insert.py all"""
import re, sys
from pathlib import Path
sys.path.insert(0, "/tmp")
import wp
sys.path.insert(0, str(Path.home() / "deeside-data"))
from gal_html import block, CSS

PAGES = {"mold": 301422, "flint": 301443, "shotton-queensferry": 301447, "connahs-quay": 301423, "buckley": 301444,
         "hawarden-ewloe": 301448, "broughton": 301446, "saltney": 301445}
START, END = "<!-- dgal start -->", "<!-- dgal end -->"


def run(slug):
    pid = PAGES[slug]
    c = wp.call(f"pages/{pid}?context=edit&_fields=content")["content"]["raw"]
    css = " ".join(CSS.split())
    new = START + css + block(slug).replace("\n", "") + END + "\n\n"
    if START in c:
        c = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\s*", lambda m: new, c, flags=re.S)
    else:
        m = re.search(r"<h2>Questions people ask</h2>", c)
        if not m:
            print(slug, "NO ANCHOR"); return
        c = c[:m.start()] + new + c[m.start():]
    wp.call(f"pages/{pid}", {"content": c})
    print(slug, pid, "done")


if __name__ == "__main__":
    for s in (PAGES if sys.argv[1] == "all" else sys.argv[1:]):
        run(s)
