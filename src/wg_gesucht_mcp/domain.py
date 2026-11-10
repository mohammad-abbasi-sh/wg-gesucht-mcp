"""Domain logic: build WG-Gesucht search URLs and shape listing
HTML into compact dicts (stdlib only).

Data source: wg-gesucht.de search + detail pages — free, no key,
no login.

URL scheme (verified live 2026-11-10):
- WG rooms:  /wg-zimmer-in-{CityName}.{id}.0.1.0.html
- Flats:     /wohnungen-in-{CityName}.{id}.2.1.0.html
- 1-room flats: /1-zimmer-wohnungen-in-{CityName}.{id}.1.1.0.html
City ids were read off each city's hub page
(https://www.wg-gesucht.de/wg-zimmer/{slug} links to its numeric
search URL). NOTE: the slug hub pages (/wg-zimmer/muenchen etc.)
are SEO landing pages with NO listings — only the numeric search
URLs carry cards. Freiburg's URL name is "Freiburg-im-Breisgau".

Search cards: <a class="wgg-list-card offer_list_item"
data-id="..." href="..." aria-label="..."> with price
<span class="card-main-text">600 &euro;</span>, title
<span class="card-main-text card-title-text">, details
<div class="card-subtitle card-details-text" title="2er WG ·
Berlin Neukölln · Grüner Weg 70">, size "14 m²" and available
date "01.12.2026" in the card text.

Detail page: key facts <span class="key_fact_detail"> +
<b class="key_fact_value">, section panels
<span class="section_panel_detail">LABEL:</span> +
<span class="section_panel_value">, description in
<div id="ad_description_text"> freitext <p>s.
"""
from __future__ import annotations

import html as _html
import re

BASE = "https://www.wg-gesucht.de"

# slug -> (display name, URL city name, numeric city id).
# Ids verified 2026-11-10 from each city's hub page.
CITIES = {
    "aachen": ("Aachen", "Aachen", 1),
    "augsburg": ("Augsburg", "Augsburg", 2),
    "bamberg": ("Bamberg", "Bamberg", 5),
    "berlin": ("Berlin", "Berlin", 8),
    "bielefeld": ("Bielefeld", "Bielefeld", 10),
    "bonn": ("Bonn", "Bonn", 13),
    "braunschweig": ("Braunschweig", "Braunschweig", 16),
    "dortmund": ("Dortmund", "Dortmund", 26),
    "dresden": ("Dresden", "Dresden", 27),
    "duesseldorf": ("Düsseldorf", "Duesseldorf", 30),
    "frankfurt": ("Frankfurt am Main", "Frankfurt", 41),
    "freiburg": ("Freiburg im Breisgau", "Freiburg-im-Breisgau", 43),
    "goettingen": ("Göttingen", "Goettingen", 49),
    "hamburg": ("Hamburg", "Hamburg", 55),
    "hannover": ("Hannover", "Hannover", 57),
    "heidelberg": ("Heidelberg", "Heidelberg", 59),
    "innsbruck": ("Innsbruck", "Innsbruck", 161),
    "jena": ("Jena", "Jena", 66),
    "karlsruhe": ("Karlsruhe", "Karlsruhe", 68),
    "kassel": ("Kassel", "Kassel", 69),
    "kiel": ("Kiel", "Kiel", 71),
    "koeln": ("Köln", "Koeln", 73),
    "konstanz": ("Konstanz", "Konstanz", 74),
    "leipzig": ("Leipzig", "Leipzig", 77),
    "mainz": ("Mainz", "Mainz", 84),
    "mannheim": ("Mannheim", "Mannheim", 85),
    "marburg": ("Marburg", "Marburg", 86),
    "muenchen": ("München", "Muenchen", 90),
    "muenster": ("Münster", "Muenster", 91),
    "nuernberg": ("Nürnberg", "Nuernberg", 96),
    "stuttgart": ("Stuttgart", "Stuttgart", 124),
    "tuebingen": ("Tübingen", "Tuebingen", 127),
    "wien": ("Wien", "Wien", 163),
    "wuerzburg": ("Würzburg", "Wuerzburg", 141),
}

_UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})

_CARD_RE = re.compile(
    r'<a[^>]*class="wgg-list-card offer_list_item[^>]*'
    r'data-id="(\d+)"[^>]*href="([^"]+)"[^>]*aria-label="([^"]*)"[^>]*>'
    r'(.*?)</a>', re.S)
_PRICE_RE = re.compile(r'<span class="card-main-text">\s*([\d.,]+)\s*&euro;\s*</span>')
_TITLE_RE = re.compile(
    r'<span class="card-main-text card-title-text"[^>]*>\s*(.*?)\s*</span>', re.S)
_DETAILS_RE = re.compile(
    r'<div class="card-subtitle card-details-text[^>]*>(.*?)</div>', re.S)
_SIZE_RE = re.compile(r'(\d+)\s*m&sup2;|(\d+)\s*m²')
_DATE_RE = re.compile(r'(\d{2}\.\d{2}\.\d{4})')
_TAG_RE = re.compile(r'<[^>]+>')
_KEY_FACT_RE = re.compile(
    r'<span class="key_fact_detail">\s*([^<]+?)\s*</span>'
    r'.*?<b class="key_fact_value">\s*([^<]+?)\s*</b>', re.S)
_PANEL_LABEL_RE = re.compile(
    r'<span class="section_panel_detail">\s*([^<]+?)\s*:?\s*</span>')
_PANEL_VALUE_RE = re.compile(
    r'<span class="section_panel_value">\s*(.*?)\s*</span>', re.S)
_DESC_RE = re.compile(
    r'<div id="ad_description_text".*?<div id="freitext_0"[^>]*>(.*?)</div>\s*</div>',
    re.S)
_P_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.S)
_TITLE_TAG_RE = re.compile(r'<title>(.*?)</title>', re.S)


def _clean(text: str) -> str:
    txt = _html.unescape(_TAG_RE.sub("", text)).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", txt).strip()


def normalize_city(city: str) -> str:
    """Accept 'München', 'Muenchen', 'muenchen', 'Berlin' etc. -> slug."""
    key = (city or "").strip().lower()
    key = key.translate(_UMLAUT).replace(" ", "").replace("-", "")
    if key in CITIES:
        return key
    # allow the display name without the suffix, e.g. "freiburg"
    raise ValueError(
        f"unsupported city: {city!r} "
        f"(use one of: {', '.join(sorted(CITIES))})"
    )


def validate_limit(limit: int) -> int:
    if not 1 <= limit <= 20:
        raise ValueError(f"limit out of range: {limit} (expected 1..20)")
    return limit


def search_url(city: str, kind: str) -> str:
    slug = normalize_city(city)
    _display, url_name, city_id = CITIES[slug]
    if kind == "rooms":
        return f"{BASE}/wg-zimmer-in-{url_name}.{city_id}.0.1.0.html"
    if kind == "flats":
        return f"{BASE}/wohnungen-in-{url_name}.{city_id}.2.1.0.html"
    raise ValueError(f"unknown kind: {kind!r}")


def _parse_price(raw: str | None) -> float | None:
    if not raw:
        return None
    try:
        return float(raw.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def parse_search(html_text: str) -> list[dict]:
    """[{id, url, title, price_eur, details, size_sqm, available_from}]."""
    out = []
    for ad_id, href, _label, body in _CARD_RE.findall(html_text):
        price_m = _PRICE_RE.search(body)
        title_m = _TITLE_RE.search(body)
        details_m = _DETAILS_RE.search(body)
        text = _clean(body)
        size_m = _SIZE_RE.search(body)
        date_m = _DATE_RE.search(text)
        size = None
        if size_m:
            size = int(size_m.group(1) or size_m.group(2))
        out.append({
            "id": ad_id,
            "url": href if href.startswith("http") else BASE + href,
            "title": _clean(title_m.group(1)) if title_m else "",
            "price_eur": _parse_price(price_m.group(1)) if price_m else None,
            "details": _clean(details_m.group(1)) if details_m else "",
            "size_sqm": size,
            "available_from": date_m.group(1) if date_m else "",
        })
    return out


def listing_url(listing: str) -> str:
    """Accept a full wg-gesucht.de listing URL. A bare numeric id
    cannot be resolved to a URL (the id alone carries no city or
    category), so it is rejected with a clear message."""
    u = (listing or "").strip()
    if not u:
        raise ValueError("listing must not be empty")
    if u.startswith("https://www.wg-gesucht.de/") and u.endswith(".html"):
        return u
    if u.isdigit():
        raise ValueError(
            "a bare listing id cannot be resolved — pass the full "
            "wg-gesucht.de listing URL (e.g. from wg_search_rooms)"
        )
    raise ValueError("listing must be a wg-gesucht.de listing URL "
                     "(https://www.wg-gesucht.de/...html)")


def parse_listing(html_text: str) -> dict:
    """Extract title, key facts, section panels and description."""
    title = ""
    m = _TITLE_TAG_RE.search(html_text)
    if m:
        title = _clean(m.group(1)).split(" - ")[0]
    facts = {}
    for label, value in _KEY_FACT_RE.findall(html_text):
        facts[_clean(label)] = _clean(value)
    panels = {}
    # Labels and values alternate in document order; pair them by
    # position (a single combined regex backtracks catastrophically
    # when a label has no following value).
    labels = [(m.start(), _clean(m.group(1)).rstrip(":"))
              for m in _PANEL_LABEL_RE.finditer(html_text)]
    values = [(m.start(), _clean(m.group(1)))
              for m in _PANEL_VALUE_RE.finditer(html_text)]
    vi = 0
    for lpos, label in labels:
        while vi < len(values) and values[vi][0] < lpos:
            vi += 1
        if vi < len(values):
            panels[label] = values[vi][1]
            vi += 1
    description = ""
    dm = _DESC_RE.search(html_text)
    if dm:
        paras = [_clean(p) for p in _P_RE.findall(dm.group(1))]
        description = "\n\n".join(p for p in paras if p)
    return {"title": title, "key_facts": facts, "details": panels,
            "description": description}
