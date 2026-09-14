"""Day 1562 checks for unsafe publication-status drift in the research snapshot."""

from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


PROFILE = Path(__file__).resolve().parents[1] / "contracts" / "standards-profile.v1.json"


class StandardsProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        cls.sources = {row["id"]: row for row in cls.profile["sources"]}

    def test_all_sources_have_distinct_qualified_official_identifiers(self) -> None:
        rows = self.profile["sources"]
        self.assertEqual(len(rows), len(self.sources))
        self.assertEqual(len(rows), len({row["url"] for row in rows}))
        self.assertEqual(
            set(self.sources),
            {
                "NIST-FIPS-203", "NIST-FIPS-204", "NIST-FIPS-205",
                "NIST-SP-800-227", "NIST-CSWP-39upd1", "NIST-IR-8547",
            },
        )
        for row in rows:
            parsed = urlparse(row["url"])
            with self.subTest(source=row["id"]):
                self.assertEqual((parsed.scheme, parsed.hostname), ("https", "csrc.nist.gov"))
                self.assertTrue(parsed.path.startswith("/pubs/"))
                self.assertTrue(row["qualification"])
                self.assertLessEqual(date.fromisoformat(row["publication_date"]), date.fromisoformat(row["checked_on"]))

    def test_draft_timeline_cannot_be_labeled_final(self) -> None:
        self.assertEqual(self.sources["NIST-IR-8547"]["publication_status"], "initial_public_draft")
        self.assertTrue(self.sources["NIST-IR-8547"]["url"].endswith("/ipd"))
        for source_id, row in self.sources.items():
            if source_id != "NIST-IR-8547":
                self.assertEqual(row["publication_status"], "final")
                self.assertTrue(row["url"].endswith("/final"))

    def test_updated_agility_guidance_replaces_older_identifier(self) -> None:
        self.assertEqual(self.sources["NIST-CSWP-39upd1"]["supersedes"], "NIST-CSWP-39")
        self.assertNotIn("NIST-CSWP-39", self.sources)
        self.assertEqual(self.profile["checked_on"], "2026-09-14")


if __name__ == "__main__":
    unittest.main()
