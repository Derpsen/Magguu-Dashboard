"""Regression tests for the 2026-10-23 security audit fixes."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest

from validate import load_yaml

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


if __name__ == "__main__":
    unittest.main()
