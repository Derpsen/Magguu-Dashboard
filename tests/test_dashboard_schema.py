from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validate import load_resolved, validate_dashboards, validate_themes

REPO_ROOT = Path(__file__).resolve().parents[1]
DASH = "dashboard/magguu-dashboard"
THEME = "Magguu Midnight:\n  primary-color: '#fff'\n  mag-surface: '#000'\n"


class DashboardSchemaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.write("themes/t.yaml", THEME)
        for device in ("mobile", "tablet"):
            self.write(f"{DASH}/{device}/dashboard.yaml", "views: !include_dir_merge_list views/\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, rel: str, content: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def view(self, body: str, device: str = "mobile", name: str = "01-a.yaml") -> None:
        self.write(f"{DASH}/{device}/views/{name}", body)

    def errors(self) -> list[str]:
        return validate_dashboards(self.root)

    def assertError(self, fragment: str) -> None:
        errors = self.errors()
        self.assertTrue(any(fragment in e for e in errors), errors)

    def test_valid_masonry_and_sections_views_pass(self) -> None:
        self.view("- title: A\n  path: a\n  theme: Magguu Midnight\n  type: custom:grid-layout\n  cards: []\n")
        self.view(
            "- title: B\n  path: b\n  type: sections\n  max_columns: 2\n  sections:\n"
            "    - type: grid\n      column_span: 2\n      cards:\n"
            "        - type: heading\n          heading: Titel\n          heading_style: title\n"
            "        - type: tile\n          entity: light.x\n          features:\n            - type: light-brightness\n",
            name="02-b.yaml",
        )
        self.assertEqual(self.errors(), [])

    def test_includes_are_resolved_through_directories_and_files(self) -> None:
        self.write("inc/cards.yaml", "- type: tile\n  entity: light.x\n  features:\n    - type: bogus-feature\n")
        self.view("- title: A\n  path: a\n  cards: !include ../../../../inc/cards.yaml\n")
        self.assertError("unbekanntes Tile-Feature 'bogus-feature'")

    def test_duplicate_and_invalid_paths_are_reported(self) -> None:
        self.view("- title: A\n  path: a\n- title: B\n  path: a\n- title: C\n  path: 3bad\n")
        self.assertError("doppelter View-Pfad a")
        self.assertError("path muss mit Buchstabe beginnen")

    def test_unknown_view_type_theme_and_key(self) -> None:
        self.view("- title: A\n  path: a\n  type: foo\n  theme: Nope\n  surprise: 1\n")
        self.assertError("unbekannter View-Typ 'foo'")
        self.assertError("Theme 'Nope' existiert nicht")
        self.assertError("unbekannter View-Schlüssel surprise")

    def test_sections_view_rules(self) -> None:
        self.view(
            "- title: A\n  path: a\n  type: sections\n  max_columns: 0\n  cards: []\n  sections:\n"
            "    - type: masonry\n      cards: []\n      bogus: 1\n"
            "    - cards: [{type: tile, entity: light.x}]\n      column_span: 3\n"
        )
        for fragment in (
            "darf weder cards noch layout",
            "max_columns muss eine ganze Zahl >= 1",
            "Section-Typ muss grid sein",
            "unbekannter Section-Schlüssel bogus",
            "nicht leere cards-Liste",
        ):
            self.assertError(fragment)

    def test_column_span_bigger_than_max_columns(self) -> None:
        self.view(
            "- title: A\n  path: a\n  type: sections\n  max_columns: 2\n  sections:\n"
            "    - column_span: 3\n      cards: [{type: heading, heading: X}]\n"
        )
        self.assertError("column_span 3 größer als max_columns 2")

    def test_grid_layout_view_must_not_define_sections(self) -> None:
        self.view("- title: A\n  path: a\n  type: custom:grid-layout\n  sections: []\n")
        self.assertError("grid-layout-View darf keine sections setzen")

    def test_new_custom_card_dependency_is_rejected(self) -> None:
        self.view("- title: A\n  path: a\n  cards:\n    - type: custom:shiny-new-card\n")
        self.assertError("custom:shiny-new-card ist keine dokumentierte Abhängigkeit")

    def test_heading_card_rules(self) -> None:
        self.view(
            "- title: A\n  path: a\n  cards:\n"
            "    - {type: heading}\n"
            "    - {type: heading, heading: X, heading_style: huge, subtitle: no}\n"
            "    - {type: heading, heading: X, badges: [{type: nope}]}\n"
        )
        for fragment in (
            "heading-Karte braucht einen Text",
            "heading_style muss title oder subtitle sein",
            "heading-Karte kennt subtitle nicht",
            "heading-badges nur vom Typ entity oder button",
        ):
            self.assertError(fragment)

    def test_navigation_targets_and_navbar_routes(self) -> None:
        self.view(
            "- title: A\n  path: a\n  cards:\n"
            "    - {type: custom:button-card, tap_action: {action: navigate, navigation_path: /magguu-mobile/a}}\n"
            "    - {type: custom:button-card, tap_action: {action: navigate, navigation_path: /magguu-mobile/missing}}\n"
            "    - {type: custom:button-card, tap_action: {action: navigate, navigation_path: /magguu-tablet/a}}\n"
            "    - {type: custom:navbar-card, routes: [{url: a}, {url: gone}, {url: /config/dashboard}]}\n"
        )
        errors = self.errors()
        self.assertFalse(any("/magguu-mobile/a " in e for e in errors), errors)
        self.assertError("/magguu-mobile/missing zeigt auf keinen View")
        self.assertError("/magguu-tablet/a zeigt auf das andere Dashboard")
        self.assertError("navbar-Route gone zeigt auf keinen View")
        self.assertFalse(any("/config/dashboard" in e for e in errors), errors)

    def test_theme_token_drift(self) -> None:
        self.view("- title: A\n  path: a\n  cards:\n    - type: markdown\n      card_mod: 'x: var(--mag-missing, 1)'\n")
        self.assertError("--mag-missing nicht")

    def test_theme_modes_are_validated(self) -> None:
        self.write("themes/t.yaml", "T:\n  primary-color: '#fff'\n  modes:\n    dark:\n      mag-a: '#000'\n    sepia:\n      x: y\n")
        self.assertTrue(any("modes darf nur" in e for e in validate_themes(self.root)))
        self.write("themes/t.yaml", "T:\n  modes:\n    dark: {}\n")
        self.assertTrue(any("modes.dark muss Variablen enthalten" in e for e in validate_themes(self.root)))
        self.write("themes/t.yaml", "T:\n  primary-color: '#fff'\n  modes:\n    dark:\n      mag-a: '#000'\n")
        self.assertEqual(validate_themes(self.root), [])

    def test_modes_tokens_count_for_token_drift(self) -> None:
        self.write("themes/t.yaml", "T:\n  modes:\n    dark:\n      mag-a: '#000'\n")
        self.view("- title: A\n  path: a\n  cards:\n    - type: markdown\n      card_mod: 'x: var(--mag-a, 1)'\n")
        self.assertEqual(self.errors(), [])

    def test_include_cycle_is_reported(self) -> None:
        self.write("loop.yaml", "a: !include loop.yaml\n")
        with self.assertRaises(ValueError):
            load_resolved(self.root / "loop.yaml", self.root)

    def test_real_repository_dashboards_are_valid(self) -> None:
        self.assertEqual(validate_dashboards(REPO_ROOT), [])
        self.assertEqual(validate_themes(REPO_ROOT), [])

    def test_real_theme_is_based_on_dark_mode(self) -> None:
        from validate import theme_definitions

        theme = theme_definitions(REPO_ROOT)["Magguu Midnight"]
        self.assertEqual(set(theme), {"modes"})
        self.assertEqual(set(theme["modes"]), {"dark"})
        dark = theme["modes"]["dark"]
        for token in ("primary-color", "primary-background-color", "ha-card-background", "lovelace-background",
                      "mag-surface", "mag-accent-media", "mag-accent-danger"):
            self.assertIn(token, dark)

    def test_mushroom_title_card_is_no_longer_allowed(self) -> None:
        from validate import ALLOWED_CUSTOM_CARDS

        self.assertNotIn("custom:mushroom-title-card", ALLOWED_CUSTOM_CARDS)
        for path in (REPO_ROOT / "dashboard").rglob("*.yaml"):
            self.assertNotIn("mushroom-title-card", path.read_text(encoding="utf-8"), str(path))

    def test_room_detail_views_use_sections_with_full_width_hero(self) -> None:
        from validate import load_resolved

        rooms = sorted((REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "rooms").glob("*.yaml"))
        self.assertEqual(len(rooms), 6)
        for path in rooms:
            view = load_resolved(path, REPO_ROOT)
            self.assertEqual(view["type"], "sections", path.name)
            self.assertTrue(view["subview"], path.name)
            hero = view["sections"][0]
            self.assertEqual(hero["column_span"], 2, path.name)
            self.assertEqual(hero["cards"][0]["template"], "room_detail_header_v7", path.name)
            self.assertNotIn("view_layout", path.read_text(encoding="utf-8"), path.name)
            for section in view["sections"][1:]:
                self.assertEqual(section["cards"][0]["type"], "heading", path.name)

    def test_condition_and_grid_option_rules(self) -> None:
        self.view(
            "- title: A\n  path: a\n  type: sections\n  sections:\n    - type: grid\n      cards:\n"
            "        - type: conditional\n          conditions: []\n          card: {type: heading, heading: X}\n"
            "        - type: heading\n          heading: Y\n          visibility:\n            - condition: bogus\n"
            "            - entity: light.x\n"
            "        - type: tile\n          entity: light.x\n          grid_options: {columns: 13, foo: 1}\n"
        )
        for fragment in (
            "Bedingungen müssen eine nicht leere Liste sein",
            "unbekannte Bedingung 'bogus'",
            "Legacy-Bedingung braucht entity und state oder state_not",
            "grid_options.columns muss 1-12 oder full sein",
            "grid_options kennt foo nicht",
        ):
            self.assertError(fragment)

    def test_valid_conditions_pass(self) -> None:
        self.view(
            "- title: A\n  path: a\n  type: sections\n  sections:\n    - type: grid\n      cards:\n"
            "        - type: conditional\n          conditions:\n            - condition: or\n              conditions:\n"
            "                - {condition: state, entity: sensor.a, state_not: unknown}\n"
            "                - {entity: sensor.b, state: [on, off]}\n"
            "          card: {type: heading, heading: X}\n"
            "        - {type: tile, entity: light.x, grid_options: {columns: full}, visibility: [{condition: state, entity: light.x, state_not: [unknown, unavailable]}]}\n"
        )
        self.assertEqual(self.errors(), [])

    def test_optional_package_entities_are_only_used_behind_conditions(self) -> None:
        """calendar.erinnerungen and the Dienste sensors may be missing in a real HA (console errors)."""
        cards = REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "cards"
        system = load_resolved(cards / "system.yaml", REPO_ROOT)
        link = [c for c in _flatten(system) if c.get("navigation_path") == "dienste"]
        self.assertEqual(len(link), 1)
        guarded = [
            c for c in _flatten(system)
            if c.get("type") == "conditional" and c.get("card", {}).get("tap_action", {}).get("navigation_path") == "dienste"
        ]
        self.assertEqual(len(guarded), 1)
        calendar = load_resolved(cards / "calendar.yaml", REPO_ROOT)
        for card in calendar:
            if card.get("type") == "calendar":
                self.fail("Kalenderkarte außerhalb einer Bedingung")
        variants = [c for c in calendar if c.get("type") == "conditional" and c["card"].get("type") == "calendar"]
        self.assertEqual(len(variants), 2)
        with_missing = [c for c in variants if "calendar.erinnerungen" in c["card"]["entities"]]
        self.assertEqual(len(with_missing), 1)
        self.assertIn("state_not", with_missing[0]["conditions"][0])


def _flatten(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _flatten(value)
    elif isinstance(node, list):
        for value in node:
            yield from _flatten(value)
