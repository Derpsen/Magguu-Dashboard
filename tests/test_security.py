"""Regression tests for the 2026-10-23 security audit fixes."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest

import tempfile

from validate import load_yaml, validate_repository, validate_shell_commands, validate_updater

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "dashboard" / "magguu-dashboard" / "shared" / "templates" / "button_card.yaml"
PACKAGE = ROOT / "packages" / "magguu_dashboard.yaml"
PAYLOAD = "<img src=x onerror=alert(1)>"
ESCAPED = "&lt;img src=x onerror=alert(1)&gt;"


def js_body(template: str) -> str:
    text = template.strip()
    assert text.startswith("[[[") and text.endswith("]]]"), text[:40]
    return text[3:-3]


def run_template(template: str, entity: dict, variables: dict | None = None, states: dict | None = None) -> str:
    """Run a button-card JS template the way button-card does (function body)."""
    script = (
        "const [entity, variables, states] = JSON.parse(process.argv[1]);"
        f"const fn = new Function('entity','variables','states', {json.dumps(js_body(template))});"
        "process.stdout.write(String(fn(entity, variables, states)));"
    )
    result = subprocess.run(
        ["node", "-e", script, json.dumps([entity, variables or {}, states or {}])],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout


@unittest.skipUnless(shutil.which("node"), "node not installed")
class ButtonCardEscapingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.templates = load_yaml(TEMPLATES)

    def test_calendar_title_is_escaped(self) -> None:
        event = self.templates["next_event_v5"]["custom_fields"]["event"]
        out = run_template(event, {"state": "on", "attributes": {"message": PAYLOAD}}, {"empty": "Kein Eintrag"})
        self.assertEqual(out, ESCAPED)

    def test_calendar_title_plain_text_unchanged(self) -> None:
        event = self.templates["next_event_v5"]["custom_fields"]["event"]
        out = run_template(event, {"state": "on", "attributes": {"message": "Zahnarzt – Dr. Müller"}}, {})
        self.assertEqual(out, "Zahnarzt – Dr. Müller")
        self.assertEqual(run_template(event, {"state": "off", "attributes": {}}, {"empty": "Kein Eintrag"}), "Kein Eintrag")

    def test_unparseable_start_time_is_escaped(self) -> None:
        for name in ("next_event_v5", "waste_event_v6"):
            label = self.templates[name]["label"]
            out = run_template(label, {"state": "on", "attributes": {"start_time": PAYLOAD}}, {})
            self.assertEqual(out, ESCAPED, name)

    def test_hero_states_are_escaped(self) -> None:
        hero = self.templates["hero_v5"]["custom_fields"]
        weather = run_template(
            hero["weather"], {}, {"show_weather": True}, {"weather.forecast_home": {"state": PAYLOAD, "attributes": {}}}
        )
        self.assertNotIn("<img", weather)
        self.assertIn(ESCAPED, weather)
        chips = run_template(
            hero["chips"],
            {},
            {},
            {
                "sensor.magguu_durchschnittstemperatur": {"state": PAYLOAD},
                "sensor.iphone_von_marco_battery_level": {"state": PAYLOAD},
            },
        )
        self.assertNotIn("<img", chips)
        self.assertIn(ESCAPED, chips)


class UpdateScriptAdminGateTest(unittest.TestCase):
    def test_first_step_is_admin_only_service(self) -> None:
        script = load_yaml(PACKAGE)["script"]["magguu_dashboard_aktualisieren"]
        self.assertEqual(script["sequence"][0], {"action": "homeassistant.reload_custom_templates"})


class ShellCommandLockdownTest(unittest.TestCase):
    """shell_command is callable by any HA user: fixed command, no templates, updater reads no args/env."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def check(self, yaml_text: str) -> list[str]:
        path = self.root / "packages" / "p.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml_text, encoding="utf-8")
        return validate_shell_commands({path: load_yaml(path)}, self.root)

    def test_repo_is_clean(self) -> None:
        _, errors = validate_repository(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(load_yaml(PACKAGE)["shell_command"], {"magguu_dashboard_update": "sh /config/magguu-dashboard-update.sh"})

    def test_fixed_command_accepted(self) -> None:
        self.assertEqual(self.check('shell_command:\n  magguu_dashboard_update: "sh /config/magguu-dashboard-update.sh"\n'), [])

    def test_templates_rejected(self) -> None:
        for cmd in ("sh /config/x.sh {{ repo }}", "sh {% if a %}x{% endif %}", "sh x {# c #}"):
            errors = self.check(f'shell_command:\n  magguu_dashboard_update: "{cmd}"\n')
            self.assertTrue(any("Templates" in e for e in errors), (cmd, errors))

    def test_other_commands_rejected(self) -> None:
        errors = self.check('shell_command:\n  evil: "rm -rf /config"\n')
        self.assertTrue(any("nicht erlaubt" in e for e in errors), errors)

    def write_updater(self, text: str) -> list[str]:
        (self.root / "update-ha.sh").write_text(text, encoding="utf-8")
        return validate_updater(self.root)

    def test_repo_updater_is_fixed(self) -> None:
        self.assertEqual(validate_updater(ROOT), [])

    def test_updater_env_and_args_rejected(self) -> None:
        fixed = (ROOT / "update-ha.sh").read_text(encoding="utf-8")
        self.assertTrue(any("HA_CONFIG_DIR" in e for e in self.write_updater(fixed + 'X="${HA_CONFIG_DIR:-/config}"\n')))
        self.assertTrue(any("Argumente" in e for e in self.write_updater(fixed + 'echo "$1"\n')))
        self.assertTrue(any("Argumente" in e for e in self.write_updater(fixed + 'echo "$@"\n')))
        broken = fixed.replace("CONFIG_DIR=/config\n", 'CONFIG_DIR="${HA_CONFIG_DIR:-/config}"\n')
        self.assertTrue(any("feste Zeile" in e for e in self.write_updater(broken)))


if __name__ == "__main__":
    unittest.main()
