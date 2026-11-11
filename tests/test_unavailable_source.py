"""One source for "nicht erreichbar": sensor count == listed entity_ids (templates run with jinja2 when installed)."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

try:
    import jinja2
except ImportError:  # pragma: no cover - CI installs jinja2 from requirements-dev.txt
    jinja2 = None

from validate import load_yaml

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = load_yaml(ROOT / "packages" / "magguu_dashboard.yaml")
EXCLUDED = {"light.badezimmer_licht_bad", "light.sonstiges_festavia_string_lights"}


def sensor() -> dict:
    for block in PACKAGE["template"]:
        for entry in block.get("sensor", []):
            if entry.get("unique_id") == "magguu_nicht_verfuegbar":
                return entry
    raise AssertionError("sensor magguu_nicht_verfuegbar fehlt")


class State:
    def __init__(self, entity_id: str, state: str) -> None:
        self.entity_id = entity_id
        self.state = state


class States:
    def __init__(self, items: dict[str, str]) -> None:
        self._items = [State(k, v) for k, v in items.items()]

    def __getattr__(self, domain: str) -> list[State]:
        return [s for s in self._items if s.entity_id.split(".", 1)[0] == domain]


class StructureTest(unittest.TestCase):
    def test_state_and_attribute_share_the_filter(self) -> None:
        entry = sensor()
        state = entry["state"]
        attr = entry["attributes"]["entity_ids"]
        for part in ("states.light", "states.switch", "states.climate", "states.cover", "states.media_player",
                     "'unavailable'", *sorted(EXCLUDED)):
            self.assertIn(part, state)
            self.assertIn(part, attr)


@unittest.skipUnless(jinja2, "jinja2 not installed")
class RenderTest(unittest.TestCase):
    def render(self, template: str, items: dict[str, str]):
        env = jinja2.Environment()
        return env.from_string(template).render(states=States(items)).strip()

    def test_count_equals_listed_entities(self) -> None:
        items = {
            "light.a": "unavailable", "light.b": "on", "switch.c": "unavailable", "climate.d": "unavailable",
            "cover.e": "unknown", "media_player.f": "unavailable", "weather.forecast_home": "unavailable",
            "sensor.x": "unavailable", "light.badezimmer_licht_bad": "unavailable",
            "light.sonstiges_festavia_string_lights": "unavailable",
        }
        entry = sensor()
        listed = ast.literal_eval(self.render(entry["attributes"]["entity_ids"], items))
        self.assertEqual(listed, ["climate.d", "light.a", "media_player.f", "switch.c"])
        self.assertEqual(int(self.render(entry["state"], items)), len(listed))

    def test_nothing_unavailable(self) -> None:
        entry = sensor()
        items = {"light.a": "on", "light.badezimmer_licht_bad": "unavailable"}
        self.assertEqual(self.render(entry["state"], items), "0")
        self.assertEqual(self.render(entry["attributes"]["entity_ids"], items), "[]")


if __name__ == "__main__":
    unittest.main()
