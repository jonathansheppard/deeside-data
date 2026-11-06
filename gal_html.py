#!/opt/homebrew/bin/python3.11
"""Writes galleries/<slug>.html (block to paste into a WP guide) and galleries.html (preview of all)."""
import html, json
from pathlib import Path

G = Path(__file__).with_name("galleries")
NAMES = {"mold": "Mold", "flint": "Flint", "shotton-queensferry": "Shotton and Queensferry", "connahs-quay": "Connah's Quay",
         "buckley": "Buckley", "hawarden-ewloe": "Hawarden and Ewloe", "broughton": "Broughton", "saltney": "Saltney"}
CSS = """<style>.dgal{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:12px 0}
.dgal figure{margin:0;background:#f4f4f2;border-radius:6px;overflow:hidden}
.dgal img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}
.dgal figcaption{font:13px/1.35 system-ui,sans-serif;padding:6px 8px;color:#333}
.dgal figcaption small{display:block;color:#666;font-size:11.5px;margin-top:2px}
.dgal-note{font:12px/1.4 system-ui,sans-serif;color:#666}</style>"""


def block(slug):
    d = json.loads((G / f"{slug}.json").read_text())
    figs = []
    for p in d["photos"]:
        t, by = html.escape(p["title"]), html.escape(p["by"])
        figs.append(f'<figure><a href="{p["link"]}" target="_blank" rel="noopener"><img src="{p["img"]}" alt="{t}" loading="lazy" width="213" height="160"></a>'
                    f'<figcaption>{t}<small>&copy; {by}, <a href="https://creativecommons.org/licenses/by-sa/2.0/" target="_blank" rel="noopener license">CC BY-SA 2.0</a>, via <a href="{p["link"]}" target="_blank" rel="noopener">Geograph</a></small></figcaption></figure>')
    return (f'<h2>Photos of {html.escape(NAMES[slug])}</h2>\n<div class="dgal">' + "".join(figs) + "</div>\n"
            '<p class="dgal-note">Photos from the <a href="https://www.geograph.org.uk/" target="_blank" rel="noopener">Geograph</a> project, '
            "shared under a Creative Commons licence. Tap a photo to see it full size. Got a better one of your area? Send it to us.</p>")


if __name__ == "__main__":
    parts = []
    for slug in NAMES:
        b = block(slug)
        (G / f"{slug}.html").write_text(CSS + "\n" + b)
        parts.append(b)
    (G.parent / "galleries.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex"><title>Town guide galleries (preview)</title>' + CSS +
        '<body style="max-width:960px;margin:20px auto;padding:0 16px;font-family:system-ui,sans-serif">' + "\n".join(parts))
    print("ok")
