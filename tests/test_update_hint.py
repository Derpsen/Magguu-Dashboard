"""Version/commit display and update hint (templates executed with jinja2 when installed)."""
from __future__ import annotations

from pathlib import Path
import re
import tempfile
import unittest

from validate import load_yaml, validate_update_hint, validate_updater

try:
    import jinja2
except ImportError:  # CI installs PyYAML only; the structural checks live in validate.py
    jinja2 = None

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = load_yaml(ROOT / "packages" / "magguu_dashboard.yaml")
SYSTEM = load_yaml(ROOT / "dashboard" / "magguu-dashboard" / "shared" / "cards" / "system.yaml")
SHA_A = "a" * 40
SHA_B = "b" * 40


def template_sensor(unique_id: str) -> dict:
    for block in PACKAGE["template"]:
        for sensor in block.get("sensor", []):
            if sensor.get("unique_id") == unique_id:
                return sensor
    raise AssertionError(unique_id)


def version_card() -> dict:
    for item in SYSTEM:
        for card in item.get("cards", []):
            for inner in card.get("cards", []):
                if inner.get("primary") == "Dashboard-Version":
                    return inner
    raise AssertionError("Dashboard-Version card")


def render(template: str, states: dict[str, str], value_json=None) -> str:
    env = jinja2.Environment()
    env.filters["regex_match"] = lambda value, find: re.match(find, str(value)) is not None
    env.tests["regex_match"] = env.filters["regex_match"]
    context = {
        "states": lambda entity_id: states.get(entity_id, "unknown"),
        "is_state": lambda entity_id, value: states.get(entity_id) == value,
        "value_json": value_json,
    }
    context["entity"] = "sensor.magguu_dashboard_update_hinweis"
    return " ".join(env.from_string(template).render(**context).split())


class StructureTest(unittest.TestCase):
    def test_installed_commit_default_is_unknown(self) -> None:
        self.assertEqual(template_sensor("magguu_dashboard_commit")["state"], "unbekannt")

    def test_update_script_refreshes_after_success(self) -> None:
        script = PACKAGE["script"]["magguu_dashboard_aktualisieren"]["sequence"]
        success = next(step for step in script if "if" in step)["then"]
        actions = [step["action"] for step in success]
        self.assertIn("template.reload", actions)
        self.assertIn("homeassistant.update_entity", actions)
        for step in success:
            if step["action"] in {"template.reload", "homeassistant.update_entity"}:
                self.assertTrue(step.get("continue_on_error"))


class ValidatorEnforcesUpdateHintTest(unittest.TestCase):
    """validate.py rejects a tampered update-hint setup (mutated copies of the real files)."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.package = (ROOT / "packages" / "magguu_dashboard.yaml").read_text(encoding="utf-8")
        self.system = (ROOT / "dashboard" / "magguu-dashboard" / "shared" / "cards" / "system.yaml").read_text(encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def errors(self, package: str | None = None, system: str | None = None) -> list[str]:
        (self.root / "packages").mkdir(exist_ok=True)
        (self.root / "packages" / "magguu_dashboard.yaml").write_text(package or self.package, encoding="utf-8")
        card = self.root / "dashboard" / "magguu-dashboard" / "shared" / "cards" / "system.yaml"
        card.parent.mkdir(parents=True, exist_ok=True)
        card.write_text(system or self.system, encoding="utf-8")
        return validate_update_hint(self.root)

    def assert_rejected(self, package: str | None, fragment: str, system: str | None = None) -> None:
        errors = self.errors(package, system)
        self.assertTrue(any(fragment in e for e in errors), (fragment, errors))

    def mutate(self, old: str, new: str) -> str:
        self.assertIn(old, self.package)
        return self.package.replace(old, new, 1)

    def test_repo_is_accepted(self) -> None:
        self.assertEqual(self.errors(), [])
        self.assertEqual(validate_update_hint(ROOT), [])

    def test_rest_url_must_be_fixed(self) -> None:
        url = "https://api.github.com/repos/Derpsen/Magguu-Dashboard/commits/main"
        self.assert_rejected(self.mutate(url, "https://example.invalid/x"), "GitHub-main-Commit-URL")

    def test_polling_at_most_hourly(self) -> None:
        self.assert_rejected(self.mutate("scan_interval: 3600", "scan_interval: 60"), "scan_interval")

    def test_no_secrets_or_auth(self) -> None:
        self.assert_rejected(self.mutate("User-Agent: magguu-dashboard", "Authorization: !secret x"), "ohne Secrets")
        self.assert_rejected(self.mutate("    timeout: 15\n", "    timeout: 15\n    authentication: basic\n"), "ohne Secrets")

    def test_extra_rest_keys_and_headers_rejected(self) -> None:
        self.assert_rejected(self.mutate("    timeout: 15\n", "    timeout: 15\n    verify_ssl: false\n"), "verify_ssl")
        self.assert_rejected(self.mutate("User-Agent: magguu-dashboard", "X-Evil: 1"), "headers")

    def test_main_commit_only_reads_sha_with_fallback(self) -> None:
        self.assert_rejected(self.mutate("value_json.sha | string", "value_json.commit.message | string"), "value_json.sha")
        self.assert_rejected(self.mutate("else 'unbekannt' }}", "else 'x' }}"), "Fallback")

    def test_installed_commit_sensor_state_validated(self) -> None:
        self.assert_rejected(self.mutate('state: "unbekannt"', 'state: "abc; rm -rf /"'), "40-stellige SHA")
        self.assertEqual(self.errors(self.mutate('state: "unbekannt"', f'state: "{SHA_A}"')), [])

    def test_hint_must_validate_both_shas(self) -> None:
        self.assert_rejected(self.mutate("not (main | regex_match('^[0-9a-f]{40}$'))", "false"), "regex_match")

    def test_missing_sensors_rejected(self) -> None:
        self.assert_rejected(self.mutate("unique_id: magguu_dashboard_commit", "unique_id: other"), "magguu_dashboard_commit fehlt")
        self.assert_rejected(self.mutate("unique_id: magguu_dashboard_update_hinweis", "unique_id: other"), "update_hinweis fehlt")

    def test_card_must_show_sensors(self) -> None:
        self.assert_rejected(None, "Versionskarte", self.system.replace("sensor.magguu_dashboard_commit", "sensor.x"))


class UpdaterHardeningTest(unittest.TestCase):
    def test_download_must_stay_https_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixed = (ROOT / "update-ha.sh").read_text(encoding="utf-8")
            for old in ("CURL_PROTO='=https'", '--proto "$CURL_PROTO"', "--max-time 120"):
                self.assertIn(old, fixed)
                (root / "update-ha.sh").write_text(fixed.replace(old, "", 1), encoding="utf-8")
                self.assertTrue(validate_updater(root), old)


@unittest.skipUnless(jinja2, "jinja2 not installed")
class TemplateTest(unittest.TestCase):
    hint = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.hint = template_sensor("magguu_dashboard_update_hinweis")["state"]
        cls.rest = PACKAGE["rest"][0]["sensor"][0]["value_template"]

    def hint_for(self, installed: str, main: str) -> str:
        return render(
            self.hint,
            {"sensor.magguu_dashboard_commit": installed, "sensor.magguu_dashboard_main_commit": main},
        )

    def test_hint_states(self) -> None:
        self.assertEqual(self.hint_for(SHA_A, SHA_A), "aktuell")
        self.assertEqual(self.hint_for(SHA_A, SHA_B), "verfuegbar")

    def test_hint_unknown_is_fail_safe(self) -> None:
        for installed, main in (
            ("unbekannt", SHA_A),
            (SHA_A, "unbekannt"),
            (SHA_A, "unavailable"),
            ("unknown", "unavailable"),
            (SHA_A, "<img src=x onerror=alert(1)>"),
            (SHA_A, SHA_A[:7]),
        ):
            self.assertEqual(self.hint_for(installed, main), "unbekannt", (installed, main))

    def test_rest_value_template(self) -> None:
        self.assertEqual(render(self.rest, {}, {"sha": SHA_B}), SHA_B)
        self.assertEqual(render(self.rest, {}, {"sha": SHA_B + "x" * 300}), SHA_B)
        for bad in ({"message": "API rate limit exceeded"}, [], "x", None):
            self.assertEqual(render(self.rest, {}, bad), "unbekannt", bad)

    def card_text(self, installed: str, main: str, hint: str, version: str = "6.5.0-dev") -> str:
        return render(
            version_card()["secondary"],
            {
                "sensor.magguu_dashboard_commit": installed,
                "sensor.magguu_dashboard_main_commit": main,
                "sensor.magguu_dashboard_update_hinweis": hint,
                "sensor.magguu_dashboard_version": version,
            },
        )

    def test_card_shows_version_sha_and_hint(self) -> None:
        self.assertEqual(self.card_text(SHA_A, SHA_A, "aktuell"), "6.5.0-dev · aaaaaaa · aktuell mit main")
        out = self.card_text(SHA_A, SHA_B, "verfuegbar")
        self.assertIn("6.5.0-dev · aaaaaaa", out)
        self.assertIn("Neuer Stand auf main (bbbbbbb)", out)
        out = self.card_text("unbekannt", "unavailable", "unbekannt")
        self.assertIn("Commit unbekannt", out)
        self.assertIn("Update-Prüfung unbekannt", out)


if __name__ == "__main__":
    unittest.main()
