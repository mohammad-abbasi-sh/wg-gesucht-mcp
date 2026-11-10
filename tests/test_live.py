"""Live tests — hit the real wg-gesucht.de search + detail pages.
Cautious: few requests.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set WG_SKIP_LIVE=1)
"""
import json
import os
import pathlib
import sys
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from wg_gesucht_mcp import server as srv

pytestmark = pytest.mark.live
SKIP = os.environ.get("WG_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="WG_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_search_rooms_live(self):
        out = json.loads(srv.wg_search_rooms("berlin", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 10)
        self.assertTrue(all(i["price_eur"] for i in out["items"]))
        print(f"\nLIVE berlin rooms: {out['total_results']} — {out['items'][0]['title'][:60]} "
              f"({out['items'][0]['price_eur']} €)")

    def test_search_flats_live(self):
        out = json.loads(srv.wg_search_flats("hamburg", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        print(f"\nLIVE hamburg flats: {out['total_results']} — {out['items'][0]['title'][:60]}")

    def test_listing_detail_live(self):
        out = json.loads(srv.wg_listing_detail(
            "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Neukoelln.14346775.html"))
        self.assertNotIn("error", out)
        self.assertTrue(out["title"])
        self.assertTrue(out["key_facts"])
        print(f"\nLIVE detail: {out['title'][:70]} — {out['key_facts']}")

    def test_health_live(self):
        out = json.loads(srv.wg_health())
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["http_status"], 200)
