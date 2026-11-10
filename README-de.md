# wg-gesucht-mcp 🏠

mcp-name: io.github.mohammad-abbasi-sh/wg-gesucht-mcp

Inoffizieller **nur lesender** MCP-Server für **[wg-gesucht.de](https://www.wg-gesucht.de)** — WG-Gesucht-Angebote von wg-gesucht.de (kostenlos, kein Schlüssel, kein Login): WG-Zimmer und Wohnungen in 34 deutschsprachigen Städten, mit Preis, Größe, Verfügbarkeit und vollständigen Anzeigendetails. Kein Schlüssel, keine Anmeldung.

> Gebaut von Mohammad Abbasi als Teil der "Germany MCP factory". Nicht mit wg-gesucht.de verbunden.

## Für KI-Agenten

Zur MCP-Client-Konfiguration hinzufügen (stdio):

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

Oder lokal starten: `python -m wg_gesucht_mcp.server` (benötigt `mcp<2`, `httpx`).

## Tools

| Tool | Beschreibung |
|------|-------------|
| `wg_search_rooms` | WG-Zimmer in einer Stadt suchen |
| `wg_search_flats` | Wohnungen in einer Stadt suchen |
| `wg_listing_detail` | Vollständige Details einer Anzeige |
| `wg_cities` | Unterstützte Städte auflisten |
| `wg_health` | Erreichbarkeitsprüfung (ok / blocked / error) — eine höfliche Anfrage |

## Entwicklung

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## Lizenz

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
