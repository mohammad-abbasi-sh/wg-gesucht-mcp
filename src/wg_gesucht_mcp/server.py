"""MCP server: unofficial read-only access to WG-Gesucht housing
listings via wg-gesucht.de search + detail pages. No key, no login.
Only OFFER listings (no "gesucht" seeking ads)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import domain as _dom
from . import http as _http

INSTRUCTIONS = """\
Unofficial read-only MCP server for WG-Gesucht housing listings via \
wg-gesucht.de search and detail pages (no key, no login): WG rooms \
and flats in 34 German-speaking cities, with price, size, \
availability and full listing details. Only offer listings — no \
"gesucht" (seeking) ads, no login, no contacting landlords. City \
names accept umlauts or transliteration ("München" / "Muenchen" / \
"muenchen"). Built by Mohammad Abbasi (mohammad-abbasi-sh) — \
https://almanibama.ir · https://mabbasi.ir — Germany MCP factory.\
"""

_SOURCE = "wg-gesucht.de"
_DISCLAIMER = "Unofficial read-only data from wg-gesucht.de listing pages; verify on the site before acting on it."


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


mcp = FastMCP("wg-gesucht-mcp", instructions=INSTRUCTIONS)


def _search(city: str, kind: str, limit: int,
            max_rent_eur: float | None) -> str:
    try:
        lim = _dom.validate_limit(limit)
        url = _dom.search_url(city, kind)
        items = _dom.parse_search(_http.fetch_text(url))
        if max_rent_eur is not None:
            if max_rent_eur <= 0:
                raise ValueError("max_rent_eur must be positive")
            items = [i for i in items
                     if i["price_eur"] is not None
                     and i["price_eur"] <= max_rent_eur]
    except (_http.WgGesuchtMcpError, ValueError) as e:
        return _err(e)
    return _ok({"city": _dom.normalize_city(city),
                "city_name": _dom.CITIES[_dom.normalize_city(city)][0],
                "kind": kind, "url": url,
                "total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def wg_search_rooms(city: str, limit: int = 10,
                    max_rent_eur: float | None = None) -> str:
    """WG rooms (WG-Zimmer) in a city. city: e.g. "berlin",
    "muenchen", "München", "hamburg". limit: 1..20 (default 10).
    max_rent_eur: optional ceiling on the monthly rent."""
    return _search(city, "rooms", limit, max_rent_eur)


@mcp.tool()
def wg_search_flats(city: str, limit: int = 10,
                    max_rent_eur: float | None = None) -> str:
    """Flats (Mietwohnungen) in a city. city: e.g. "berlin",
    "muenchen", "hamburg". limit: 1..20 (default 10).
    max_rent_eur: optional ceiling on the monthly rent."""
    return _search(city, "flats", limit, max_rent_eur)


@mcp.tool()
def wg_listing_detail(listing: str) -> str:
    """Full details of one WG-Gesucht listing. listing: a full
    wg-gesucht.de listing URL, e.g.
    https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Neukoelln.14346775.html
    (get URLs from wg_search_rooms / wg_search_flats)."""
    try:
        u = _dom.listing_url(listing)
        out = _dom.parse_listing(_http.fetch_text(u))
        if not out["title"] and not out["description"]:
            raise ValueError("no listing content found at that URL "
                             "(it may be expired or removed)")
    except (_http.WgGesuchtMcpError, ValueError) as e:
        return _err(e)
    return _ok({"url": u, "title": out["title"],
                "key_facts": out["key_facts"],
                "details": out["details"],
                "description": out["description"][:6000]})


@mcp.tool()
def wg_cities() -> str:
    """The 34 supported cities (from the WG-Gesucht city-hub
    sitemap): slug, display name and numeric city id."""
    cities = [{"slug": slug, "name": display, "city_id": cid}
              for slug, (display, _url_name, cid)
              in sorted(_dom.CITIES.items())]
    return _ok({"total_results": len(cities), "cities": cities})


@mcp.tool()
def wg_health() -> str:
    """Check whether wg-gesucht.de is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    sys.exit(main())
