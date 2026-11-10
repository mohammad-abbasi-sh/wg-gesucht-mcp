# wg-gesucht-mcp 🏠

mcp-name: io.github.mohammad-abbasi-sh/wg-gesucht-mcp

Unofficial **read-only** MCP server for **[wg-gesucht.de](https://www.wg-gesucht.de)** — WG-Gesucht flatshare listings from wg-gesucht.de (free, no key, no login): WG rooms and flats in 34 German-speaking cities, with price, size, availability and full listing details. No key, no login.

> Built by Mohammad Abbasi as part of the "Germany MCP factory". Not affiliated with wg-gesucht.de.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "wg-gesucht": {
      "command": "uvx",
      "args": ["wg-gesucht-mcp==0.1.0"]
    }
  }
}
```

Or run locally: `python -m wg_gesucht_mcp.server` (needs `mcp<2`, `httpx`).

## Tools

| Tool | Description |
|------|-------------|
| `wg_search_rooms` | WG rooms (WG-Zimmer) in a city — `city` (e.g. berlin, muenchen, hamburg), `limit` 1..20, optional `max_rent_eur` |
| `wg_search_flats` | Flats (Mietwohnungen) in a city — `city`, `limit` 1..20, optional `max_rent_eur` |
| `wg_listing_detail` | Full listing details — `listing` (a wg-gesucht.de listing URL, e.g. https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Neukoelln.14346775.html) |
| `wg_cities` | The 34 supported cities (from the WG-Gesucht city-hub sitemap) — no params |
| `wg_health` | Reachability probe (ok / blocked / error) — one polite request |

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
