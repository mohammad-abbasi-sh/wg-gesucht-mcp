"""Offline tests — parse real captured WG-Gesucht search + detail
pages, no network."""
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from wg_gesucht_mcp import domain as dom
from wg_gesucht_mcp import server as srv

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


class TestCities(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(dom.normalize_city("berlin"), "berlin")
        self.assertEqual(dom.normalize_city("München"), "muenchen")
        self.assertEqual(dom.normalize_city("Muenchen"), "muenchen")
        self.assertEqual(dom.normalize_city("  KÖLN "), "koeln")
        self.assertEqual(dom.normalize_city("Freiburg"), "freiburg")
        self.assertEqual(dom.normalize_city("Düsseldorf"), "duesseldorf")

    def test_invalid(self):
        for bad in ["", "paris", "london", "new york"]:
            with self.assertRaises(ValueError, msg=bad):
                dom.normalize_city(bad)

    def test_urls(self):
        self.assertEqual(dom.search_url("berlin", "rooms"),
                         "https://www.wg-gesucht.de/wg-zimmer-in-Berlin.8.0.1.0.html")
        self.assertEqual(dom.search_url("muenchen", "rooms"),
                         "https://www.wg-gesucht.de/wg-zimmer-in-Muenchen.90.0.1.0.html")
        self.assertEqual(dom.search_url("berlin", "flats"),
                         "https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1.0.html")
        self.assertEqual(dom.search_url("Freiburg", "rooms"),
                         "https://www.wg-gesucht.de/wg-zimmer-in-Freiburg-im-Breisgau.43.0.1.0.html")
        self.assertEqual(len(dom.CITIES), 34)

    def test_limit(self):
        self.assertEqual(dom.validate_limit(10), 10)
        with self.assertRaises(ValueError):
            dom.validate_limit(0)
        with self.assertRaises(ValueError):
            dom.validate_limit(21)

    def test_listing_url(self):
        u = "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Neukoelln.14346775.html"
        self.assertEqual(dom.listing_url(u), u)
        with self.assertRaises(ValueError):
            dom.listing_url("14346775")
        with self.assertRaises(ValueError):
            dom.listing_url("https://www.example.com/x.html")
        with self.assertRaises(ValueError):
            dom.listing_url("")


class TestFixtures(unittest.TestCase):
    def test_berlin_rooms(self):
        items = dom.parse_search(_read("search-berlin-rooms.html"))
        self.assertEqual(len(items), 28)
        first = items[0]
        self.assertEqual(first["id"], "14346775")
        self.assertEqual(first["title"], "WG Zimmer U Britz-Süd (2 Zimmer)")
        self.assertEqual(first["price_eur"], 600.0)
        self.assertEqual(first["size_sqm"], 14)
        self.assertEqual(first["available_from"], "01.12.2026")
        self.assertIn("Neukölln", first["details"])
        self.assertTrue(all(i["title"] and i["url"] and i["price_eur"] for i in items))
        self.assertTrue(all(i["size_sqm"] for i in items))

    def test_muenchen_rooms(self):
        items = dom.parse_search(_read("search-muenchen-rooms.html"))
        self.assertEqual(len(items), 28)
        self.assertEqual(items[0]["price_eur"], 940.0)
        self.assertIn("München", items[0]["details"])

    def test_berlin_flats(self):
        items = dom.parse_search(_read("search-berlin-flats.html"))
        self.assertEqual(len(items), 28)
        self.assertEqual(items[0]["price_eur"], 1260.0)
        self.assertEqual(items[0]["size_sqm"], 60)
        self.assertIn("Moabit", items[0]["details"])

    def test_detail(self):
        out = dom.parse_listing(_read("detail-14346775.html"))
        self.assertEqual(out["title"], "WG Zimmer U Britz-Süd (2 Zimmer)")
        self.assertEqual(out["key_facts"]["Zimmergröße"], "14m²")
        self.assertEqual(out["key_facts"]["Gesamtmiete"], "600€")
        self.assertEqual(out["details"]["Miete"], "600€")
        self.assertEqual(out["details"]["Kaution"], "600€")
        self.assertEqual(out["details"]["frei ab"], "01.12.2026")
        self.assertIn("Cozy Room in a Quiet WG", out["description"])
        self.assertGreater(len(out["description"]), 400)


class TestServerOffline(unittest.TestCase):
    """Server tools with fetch_text mocked to the fixtures."""

    def test_search_rooms(self):
        with mock.patch("wg_gesucht_mcp.server._http.fetch_text",
                        lambda url: _read("search-berlin-rooms.html")):
            out = json.loads(srv.wg_search_rooms("berlin", limit=5))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 28)
        self.assertEqual(out["count"], 5)
        self.assertEqual(out["city_name"], "Berlin")
        self.assertEqual(out["source"], "wg-gesucht.de")
        self.assertIn("fetched_at", out)

    def test_search_max_rent(self):
        with mock.patch("wg_gesucht_mcp.server._http.fetch_text",
                        lambda url: _read("search-berlin-rooms.html")):
            out = json.loads(srv.wg_search_rooms("berlin", limit=20, max_rent_eur=500))
        self.assertNotIn("error", out)
        self.assertTrue(all(i["price_eur"] <= 500 for i in out["items"]))
        self.assertLess(out["total_results"], 28)

    def test_search_bad_city(self):
        out = json.loads(srv.wg_search_rooms("paris"))
        self.assertIn("error", out)

    def test_search_flats(self):
        with mock.patch("wg_gesucht_mcp.server._http.fetch_text",
                        lambda url: _read("search-berlin-flats.html")):
            out = json.loads(srv.wg_search_flats("berlin", limit=3))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 28)
        self.assertEqual(out["kind"], "flats")

    def test_listing_detail(self):
        with mock.patch("wg_gesucht_mcp.server._http.fetch_text",
                        lambda url: _read("detail-14346775.html")):
            out = json.loads(srv.wg_listing_detail(
                "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Neukoelln.14346775.html"))
        self.assertNotIn("error", out)
        self.assertIn("Britz", out["title"])
        self.assertEqual(out["key_facts"]["Gesamtmiete"], "600€")

    def test_listing_detail_bare_id(self):
        out = json.loads(srv.wg_listing_detail("14346775"))
        self.assertIn("error", out)
        self.assertIn("full", out["error"])

    def test_cities(self):
        out = json.loads(srv.wg_cities())
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 34)
        slugs = [c["slug"] for c in out["cities"]]
        self.assertIn("muenchen", slugs)
        self.assertIn("wien", slugs)
        berlin = [c for c in out["cities"] if c["slug"] == "berlin"][0]
        self.assertEqual(berlin["city_id"], 8)

    def test_health_mocked(self):
        with mock.patch("wg_gesucht_mcp.server._http.health_check",
                        return_value={"status": "ok", "http_status": 200,
                                      "url": "https://www.wg-gesucht.de/wg-zimmer-in-Berlin.8.0.1.0.html"}):
            out = json.loads(srv.wg_health())
        self.assertEqual(out["status"], "ok")


if __name__ == "__main__":
    unittest.main()
