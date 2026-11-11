"""Optional Dienste package: public GitHub queries go without any token/Authorization."""
from __future__ import annotations

from pathlib import Path
import unittest

from validate import load_yaml

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "docs" / "optional" / "magguu_dienste.yaml"


class PublicGithubWithoutTokenTest(unittest.TestCase):
    def test_github_requests_have_no_authorization(self) -> None:
        rest = load_yaml(PATH)["rest"]
        github = [r for r in rest if isinstance(r.get("resource"), str) and r["resource"].startswith("https://api.github.com/")]
        self.assertEqual(len(github), 2)
        for entry in github:
            headers = {k.lower() for k in (entry.get("headers") or {})}
            self.assertNotIn("authorization", headers, entry["resource"])
        self.assertNotIn("github_status_auth", PATH.read_text(encoding="utf-8").replace("Secret github_status_auth wird nicht mehr", ""))


if __name__ == "__main__":
    unittest.main()
