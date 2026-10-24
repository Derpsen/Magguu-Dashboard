"""Runs the real redact_log function from ci-alarm.yml (between the redact-begin/end markers) in bash.

All secrets below are made-up fake values.
"""
import re
import subprocess
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci-alarm.yml"

FAKE = {
    "ghp": "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8",
    "pat": "github_pat_" + "11ABCDEFG0abcdefghijkl_mnopqrstuvwxyz0123456789ABCDEFGHIJ",
    "gho": "gho_" + "abcdefghijklmnopqrstuvwxyz0123456789",
    "ghs": "ghs_" + "ZYXWVUTSRQPONMLKJIHGFEDCBA9876543210",
    "jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmYWtlIn0.c2lnbmF0dXJlLWZha2U",
    "url": "https://hooks.example.invalid/services/T000/B000/XXXXFAKEXXXX",
    "hex": "deadbeef" * 8,
    "b64": "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVowMTIzNDU2Nzg5",
}


def redact(text: str) -> str:
    match = re.search(r"# redact-begin[^\n]*\n(.*?)# redact-end", WORKFLOW.read_text(), re.S)
    assert match, "redact block found in ci-alarm.yml"
    script = "\n".join(re.sub(r"^ {10}", "", line) for line in match.group(1).split("\n"))
    res = subprocess.run(["bash", "-c", script + "\nredact_log"], input=text, capture_output=True, text=True, check=True)
    return res.stdout


class RedactLogTest(unittest.TestCase):
    def test_bare_secrets_never_survive(self):
        for name, value in FAKE.items():
            out = redact(f"2026-10-24T10:00:00.000Z npm ERR! while calling {value} done\n")
            self.assertNotIn(value, out, name)
            self.assertNotIn(value[:20], out, name)
        out = redact("got bearer fakevalue123456 back\n")
        self.assertNotIn("fakevalue123456", out)

    def test_multiple_secrets_in_one_line(self):
        out = redact(f"error: request to {FAKE['url']} failed with {FAKE['ghp']} and {FAKE['jwt']}, exit 1\n")
        self.assertEqual(out, "error: request to [redacted-url] failed with [redacted-gh] and [redacted-jwt], exit 1\n")

    def test_keyword_lines_and_normal_lines(self):
        self.assertEqual(redact("API_KEY=whatever\n"), "[line redacted]\n")
        self.assertEqual(redact("Authorization: something short\n"), "[line redacted]\n")
        self.assertEqual(
            redact("2026-10-24T10:00:00.1234567Z \x1b[31mFAIL: expected 3 to equal 4\x1b[0m\n"),
            "FAIL: expected 3 to equal 4\n",
        )
        self.assertEqual(redact("tests/test_x.py failed\n"), "tests/test_x.py failed\n")


if __name__ == "__main__":
    unittest.main()
