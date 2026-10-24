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
