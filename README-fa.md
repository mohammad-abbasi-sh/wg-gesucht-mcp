# wg-gesucht-mcp 🏠

mcp-name: io.github.mohammad-abbasi-sh/wg-gesucht-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **[wg-gesucht.de](https://www.wg-gesucht.de)** — آگهی‌های مسکن WG-Gesucht از wg-gesucht.de (رایگان، بدون کلید): اتاق‌های اشتراکی و آپارتمان در ۳۴ شهر آلمانی‌زبان، با قیمت، متراژ، تاریخ در دسترس بودن و جزئیات کامل آگهی. بدون کلید، بدون ورود.

> ساختهٔ محمد عباسی، بخشی از «کارخانهٔ MCP آلمان». وابسته به wg-gesucht.de نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی MCP کلاینت اضافه کنید (stdio):

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

یا به‌صورت محلی اجرا کنید: `python -m wg_gesucht_mcp.server` (نیازمند `mcp<2` و `httpx`).

## ابزارها

| ابزار | توضیح |
|------|-------|
| `wg_search_rooms` | جست‌وجوی اتاق اشتراکی در یک شهر |
| `wg_search_flats` | جست‌وجوی آپارتمان در یک شهر |
| `wg_listing_detail` | جزئیات کامل یک آگهی |
| `wg_cities` | فهرست شهرهای پشتیبانی‌شده |
| `wg_health` | بررسی دسترس‌پذیری (ok / blocked / error) — یک درخواست مؤدبانه |

## توسعه

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## لایسنس

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
