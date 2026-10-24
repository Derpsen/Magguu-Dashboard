"""Unseen media report card on the Dienste page: structure, no delete path, offline render with jinja2 (skipped without jinja2)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import unittest

from validate import load_yaml

try:
    import jinja2
except ImportError:  # CI installs PyYAML only
    jinja2 = None

ROOT = Path(__file__).resolve().parents[1]
VIEW_PATH = ROOT / "dashboard" / "magguu-dashboard" / "shared" / "views" / "dienste.yaml"
VIEW = load_yaml(VIEW_PATH)
OPTIONAL = (ROOT / "docs" / "optional" / "magguu_dienste.yaml").read_text(encoding="utf-8")


def walk(node):
    if isinstance(node, dict):
        yield node
        for child in node.values():
            yield from walk(child)
    elif isinstance(node, list):
        for child in node:
            yield from walk(child)


def report_card() -> dict:
    for node in walk(VIEW):
        if node.get("type") == "conditional" and "unseen" in json.dumps(node, default=str):
            return node
    raise AssertionError("conditional report card not found")


def reveal_card() -> dict:
    for node in walk(VIEW):
        if node.get("entity") == "script.magguu_ungesehen_bericht_anzeigen":
            return node
    raise AssertionError("reveal card not found")


def render(unseen, now_iso: str = "2026-10-25T10:00:00+00:00") -> str:
    sentinel = object()

    def as_timestamp(value, default=sentinel):
        # like Home Assistant: without a default an unparsable value is a template error
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
        except ValueError:
            if default is sentinel:
                raise RuntimeError(f"as_timestamp: invalid value {value!r} and no default") from None
            return default

    env = jinja2.Environment()
    env.filters["timestamp_custom"] = lambda ts, fmt="%c", local=True: datetime.fromtimestamp(ts, timezone.utc).strftime(fmt)
    context = {
        "state_attr": lambda entity, attr: unseen if (entity, attr) == ("sensor.magguu_bot_status", "unseen") else None,
        "as_timestamp": as_timestamp,
        "is_state": lambda e, v: False,
    }
    return env.from_string(report_card()["card"]["content"]).render(**context)


def block(items, **over):
    base = {"generatedAt": "2026-10-25T08:00:00.000Z", "topN": 25, "minAgeDays": 90, "staleDays": 365, "partial": False, "libraries": 2, "items": items}
    base.update(over)
    return base


def item(title="Big Movie (2019)", size=50_000_000_000, library="Filme", last=None):
    return {"title": title, "library": library, "type": "movie", "sizeBytes": size, "lastPlayedAt": last, "addedAt": "2024-01-01T00:00:00.000Z"}


class StructureTest(unittest.TestCase):
    def test_card_says_report_only_and_has_no_delete_path(self) -> None:
        text = VIEW_PATH.read_text(encoding="utf-8")
        self.assertIn("Nur Bericht – nichts wird gelöscht", text)
        self.assertIn("Ungesehene Medien (Bericht)", text)
        for node in walk(report_card()):
            for key in ("tap_action", "hold_action", "double_tap_action"):
                action = node.get(key)
                self.assertTrue(action is None or action in ({"action": "none"}, {"action": "more-info"}), (key, action))
        # the only service the whole card pair calls is the admin-gated reveal script
        services = [n for n in walk([report_card(), reveal_card()]) if "service" in n]
        self.assertEqual([n["target"]["entity_id"] for n in services], ["script.magguu_ungesehen_bericht_anzeigen"])

    def test_list_only_visible_when_the_admin_gated_boolean_is_on(self) -> None:
        conditions = report_card()["conditions"]
        self.assertEqual(conditions, [{"condition": "state", "entity": "input_boolean.magguu_ungesehen_bericht_offen", "state": "on"}])

    def test_sensor_attribute_is_forwarded(self) -> None:
        self.assertRegex(OPTIONAL, r"- unseen\n")

    def test_template_uses_item_access_not_the_dict_method(self) -> None:
        content = report_card()["card"]["content"]
        self.assertIn("u['items']", content)
        self.assertNotIn("u.items", content)


@unittest.skipUnless(jinja2, "jinja2 not installed")
class RenderTest(unittest.TestCase):
    def test_no_attribute_shows_no_data(self) -> None:
        out = render(None)
        self.assertIn("Nur Bericht – nichts wird gelöscht", out)
        self.assertIn("Keine Daten", out)

    def test_empty_report(self) -> None:
        out = render(block([]))
        self.assertIn("keine Titel gefunden", out)
        self.assertIn("25.10.2026", out)

    def test_data_lists_size_library_and_last_seen(self) -> None:
        out = render(block([
            item("Never Seen (2020)", 50_000_000_000),
            item("Old Show", 2_500_000_000_000, "Serien", "2024-03-12T10:00:00.000Z"),
        ]))
        self.assertIn("1. Never Seen (2020) · 50,0 GB · Filme · letzte Sicht: nie", out)
        self.assertIn("2. Old Show · 2,5 TB · Serien · letzte Sicht: 12.03.2024", out)
        self.assertIn("mindestens 365 Tagen", out)
        self.assertIn("mindestens 90 Tagen", out)
        self.assertIn("Tautulli-Verlauf", out)
        self.assertNotIn("unvollständig", out)
        self.assertRegex(out, r"letzte Sicht: 12\.03\.2024\n\n+„nie“")  # blank line: markdown must not fold the note into the last list item

    def test_partial_hint(self) -> None:
        self.assertIn("unvollständig", render(block([item()], partial=True)))

    def test_markdown_and_html_in_titles_is_neutralised(self) -> None:
        out = render(block([item("**bold** _it_ `code` [x](http://e) <img src=x onerror=1> | a")]))
        line = next(l for l in out.splitlines() if l.startswith("1."))
        for bad in ("*", "`", "[", "]", "<", ">", "|", "_"):
            title_part = line.split(" · ")[0]
            self.assertNotIn(bad, title_part, (bad, title_part))

    def test_missing_or_invalid_timestamps_do_not_raise_a_template_error(self) -> None:
        for bad in (None, "", "garbage", 12345, {"x": 1}):
            out = render(block([item()], generatedAt=bad))
            self.assertIn("Stand unbekannt", out, bad)
            self.assertIn("1. Big Movie (2019)", out)
        no_key = block([item()])
        del no_key["generatedAt"]
        self.assertIn("Stand unbekannt", render(no_key))
        self.assertIn("Stand unbekannt: keine Titel", render(block([], generatedAt="nope")))
        out = render(block([item("Played", 5_000_000_000, "Filme", "not-a-date"), item("Never", 4_000_000_000)]))
        self.assertIn("1. Played · 5,0 GB · Filme · letzte Sicht: unbekannt", out)
        self.assertIn("2. Never · 4,0 GB · Filme · letzte Sicht: nie", out)

    def test_library_name_is_as_strictly_cleaned_as_the_title(self) -> None:
        evil = "**Lib** _x_ `c` [l](http://e) <b>h</b> | z"
        out = render(block([item("Title", 5_000_000_000, evil)]))
        line = next(l for l in out.splitlines() if l.startswith("1."))
        library_part = line.split(" · ")[2]
        for bad in ("*", "_", "`", "[", "]", "<", ">", "|"):
            self.assertNotIn(bad, library_part, (bad, library_part))
        self.assertIn("Lib", library_part)

    def test_missing_wrong_or_oversized_attribute_is_handled(self) -> None:
        for weird in ("text", 5, [], {}, {"items": "abc"}, {"items": {"a": 1}}, {"items": None}, {"items": [None, "x", 7]}):
            out = render(weird)
            self.assertIn("Nur Bericht – nichts wird gelöscht", out, weird)
        self.assertIn("Keine Daten", render("text"))
        self.assertIn("keine Titel gefunden", render({"items": "abc", "generatedAt": "2026-10-25T08:00:00Z"}))
        garbage = render({"generatedAt": "2026-10-25T08:00:00Z", "items": [None, "x", 7, ["a"]]})
        self.assertIn("die 4 größten Titel", garbage)
        # more items than the card ever shows (attribute far too large): capped at 25
        many = render(block([item(f"T{i}", 1_000_000_000 + i) for i in range(80)]))
        self.assertIn("die 25 größten Titel", many)
        self.assertEqual(len([l for l in many.splitlines() if l[:1].isdigit()]), 25)

    def test_clipped_hint(self) -> None:
        self.assertIn("gekürzt", render(block([item()], clipped=True)))
        self.assertNotIn("gekürzt", render(block([item()])))

    def test_garbage_values_do_not_crash(self) -> None:
        out = render(block([{"title": "T", "library": "L", "sizeBytes": "abc", "lastPlayedAt": None}]))
        self.assertIn("0,0 GB", out)


if __name__ == "__main__":
    unittest.main()
