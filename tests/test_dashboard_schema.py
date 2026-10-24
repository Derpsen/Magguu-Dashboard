from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validate import load_resolved, load_yaml, validate_dashboards, validate_themes

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
        # HA begrenzt column_span auf die sichtbare Spaltenzahl (hui-sections-view): kein Fehler.
        self.assertEqual(self.errors(), [])

    def test_mushroom_in_section_needs_rows_auto(self) -> None:
        self.view(
            "- title: A\n  path: a\n  type: sections\n  sections:\n"
            "    - cards:\n"
            "        - {type: custom:mushroom-template-card, primary: X}\n"
            "        - {type: conditional, conditions: [{condition: state, entity: sensor.a, state: 'on'}], card: {type: custom:mushroom-template-card, primary: Y}}\n"
            "        - {type: custom:mushroom-template-card, primary: Z, grid_options: {columns: 12, rows: auto}}\n"
        )
        self.assertEqual(sum("rows: auto" in e for e in self.errors()), 2, self.errors())

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

    def test_real_theme_has_dark_and_light_mode(self) -> None:
        from validate import theme_definitions

        theme = theme_definitions(REPO_ROOT)["Magguu Midnight"]
        self.assertEqual(set(theme), {"modes"})
        self.assertEqual(set(theme["modes"]), {"dark", "light"})
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
            # button-card has its own default width in sections; without `full` the hero fills only one column.
            self.assertEqual(hero["cards"][0]["grid_options"], {"columns": "full"}, path.name)
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
        cards = REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "sections"
        system = load_resolved(cards / "system.yaml", REPO_ROOT)
        link = [c for c in _flatten(system) if c.get("navigation_path") == "dienste"]
        self.assertEqual(len(link), 1)
        guarded = [
            c for c in _flatten(system)
            if c.get("type") == "conditional" and c.get("card", {}).get("tap_action", {}).get("navigation_path") == "dienste"
        ]
        self.assertEqual(len(guarded), 1)
        calendar = [c for s in load_resolved(cards / "kalender.yaml", REPO_ROOT) for c in s.get("cards", [])]
        for card in calendar:
            if card.get("type") == "calendar":
                self.fail("Kalenderkarte außerhalb einer Bedingung")
        variants = [c for c in calendar if c.get("type") == "conditional" and c["card"].get("type") == "calendar"]
        self.assertEqual(len(variants), 2)
        with_missing = [c for c in variants if "calendar.erinnerungen" in c["card"]["entities"]]
        self.assertEqual(len(with_missing), 1)
        self.assertIn("state_not", with_missing[0]["conditions"][0])

    def test_missing_entities_of_the_live_check_are_hidden_not_removed(self) -> None:
        """These entities were absent in the real HA (v6.6.0 check); they stay in the repo but are guarded."""
        dead = {
            "light.badezimmer_licht_bad", "light.sonstiges_festavia_string_lights", "button.vordereingang_tur_offnen",
        }
        found: dict[str, int] = {}

        def guarded_by(conditions) -> set[str]:
            return {c.get("entity") for c in _flatten(conditions) if isinstance(c, dict) and c.get("entity")}

        def visit(node, guard: set[str]) -> None:
            if isinstance(node, dict):
                here = set(guard)
                if node.get("type") == "conditional":
                    here |= guarded_by(node.get("conditions"))
                if "visibility" in node:
                    here |= guarded_by(node["visibility"])
                entity = node.get("entity")
                if node.get("type") in {"tile", "custom:button-card", "custom:mushroom-template-card"} and entity in dead:
                    found[entity] = found.get(entity, 0) + 1
                    self.assertIn(entity, here, f"{entity} ungeschützt")
                for key, value in node.items():
                    visit(value, here if key in {"card", "cards"} or node.get("type") != "conditional" else guard)
            elif isinstance(node, list):
                for value in node:
                    visit(value, guard)

        for path in (REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared").rglob("*.yaml"):
            visit(load_resolved(path, REPO_ROOT), set())
        self.assertEqual(set(found), dead)

    def test_every_real_view_is_native_sections_with_one_navbar_in_the_first_section(self) -> None:
        from validate import _dashboard_views
        for device in ("mobile", "tablet"):
            views, errors = _dashboard_views(REPO_ROOT, device)
            self.assertEqual(errors, [])
            self.assertGreaterEqual(len(views), 15)
            for view in views:
                where = f"{device}/{view['path']}"
                self.assertEqual(view.get("type"), "sections", where)
                sections = view["sections"]
                navbars = [(i, c) for i, s in enumerate(sections) for c in s.get("cards", []) if c.get("type") == "custom:navbar-card"]
                if view["path"] in {"overview", "raeume", "klima", "system", "kalender", "sicherheit", "medien", "energie", "dienste"}:
                    self.assertEqual([i for i, _ in navbars], [0], where)
                    self.assertEqual(navbars[0][1]["grid_options"], {"columns": "full", "rows": "auto"}, where)
                for card in _flatten(view):
                    self.assertNotIn("view_layout", card, where)
                    self.assertNotEqual(card.get("type"), "custom:layout-card", where)

    def test_entity_card_titles_use_the_heading_card_font(self) -> None:
        sections = REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "sections"
        seen = 0
        for path in sections.glob("*.yaml"):
            for card in _flatten(load_resolved(path, REPO_ROOT)):
                if card.get("type") == "entities" and card.get("title"):
                    seen += 1
                    self.assertIn("--ha-heading-card-title-font-size", str(card.get("card_mod")), f"{path.name}: {card['title']}")
        self.assertGreaterEqual(seen, 4)

    def test_tiles_carry_the_matching_feature(self) -> None:
        """Dimmer, Rollladen-Position und Zieltemperatur direkt auf der Kachel (Tile-Features)."""
        wanted = {"light.": "light-brightness", "climate.": "target-temperature", "cover.": "cover-position"}
        shared = REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared"
        checked = 0
        for path in list((shared / "rooms").glob("*.yaml")) + list((shared / "sections").glob("*.yaml")):
            for card in _flatten(load_resolved(path, REPO_ROOT)):
                if card.get("type") != "tile":
                    continue
                for prefix, feature in wanted.items():
                    if str(card.get("entity", "")).startswith(prefix):
                        checked += 1
                        types = [f.get("type") for f in card.get("features", [])]
                        self.assertIn(feature, types, f"{path.name}: {card['entity']}")
        self.assertGreater(checked, 20)

    def test_unreachable_list_skips_permanently_unavailable_optional_lights(self) -> None:
        system = load_resolved(REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "sections" / "system.yaml", REPO_ROOT)
        lists = [c for c in _flatten(system) if c.get("type") == "custom:auto-entities" and c.get("card", {}).get("title") == "Nicht erreichbar"]
        self.assertEqual(len(lists), 1)
        excluded = {rule["entity_id"] for rule in lists[0]["filter"]["exclude"]}
        self.assertEqual(excluded, {"light.badezimmer_licht_bad", "light.sonstiges_festavia_string_lights"})

    def test_backup_card_says_no_backup_yet_when_the_sensor_is_unknown(self) -> None:
        system = load_resolved(REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "sections" / "system.yaml", REPO_ROOT)
        cards = [c for c in _flatten(system) if c.get("entity") == "sensor.backup_last_successful_automatic_backup"]
        self.assertEqual(len(cards), 1)
        self.assertIn("== 'unknown' %}", cards[0]["secondary"])
        self.assertIn("Noch kein Backup", cards[0]["secondary"])
        self.assertNotIn("Noch kein Zeitpunkt", cards[0]["secondary"])

    def test_tile_texts_wrap_instead_of_overflowing_the_tile(self) -> None:
        templates = load_yaml(REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "templates" / "button_card.yaml")
        for name in ("quick_v5", "next_event_v5", "room_action_v5"):
            columns = [rule for rule in templates[name]["styles"]["grid"] if "grid-template-columns" in rule]
            self.assertTrue(columns and "minmax(0, 1fr)" in columns[0]["grid-template-columns"], name)
        event = {k: v for rule in templates["next_event_v5"]["styles"]["custom_fields"]["event"] for k, v in rule.items()}
        self.assertEqual(event["white-space"], "normal")
        self.assertEqual(event["max-width"], "100%")
        self.assertEqual(event["-webkit-line-clamp"], 2)
        overview = (REPO_ROOT / "dashboard" / "magguu-dashboard" / "mobile" / "views" / "01-overview.yaml").read_text(encoding="utf-8")
        self.assertIn(".name-state .state", overview)

    def test_nested_grid_cards_in_sections_use_the_full_section_width(self) -> None:
        """Ein Grid-Card hat Standardbreite 12 und füllt in einer 2-Spalten-Section (24 Spalten) nur die Hälfte."""
        shared = REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared"
        checked = 0
        for path in list((shared / "sections").glob("*.yaml")) + [shared / "cards" / "status-shortcuts.yaml", shared / "cards" / "home-quick.yaml"]:
            for card in _flatten_outside_stacks(load_resolved(path, REPO_ROOT)):
                if card.get("type") == "grid" and "columns" in card:
                    checked += 1
                    self.assertEqual(card.get("grid_options"), {"columns": "full", "rows": "auto"}, f"{path.name}: grid columns={card['columns']}")
        self.assertGreaterEqual(checked, 9)

    def test_security_tile_rows_adapt_to_the_available_width(self) -> None:
        sections = load_resolved(REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "sections" / "sicherheit.yaml", REPO_ROOT)
        rows = [c for c in _flatten(sections) if c.get("type") == "grid" and c.get("columns") == 3]
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertIn("auto-fit", row["card_mod"]["style"])

    def test_room_cards_have_no_half_empty_tile_rows(self) -> None:
        """Ungerade Kachelzahl: die letzte Kachel liegt als volle Zeile außerhalb des 2-Spalten-Grids."""
        cards = REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "cards"
        checked = 0
        for path in sorted(cards.glob("room-*.yaml")):
            room = load_resolved(path, REPO_ROOT)
            grids = [c for c in room["cards"] if c.get("type") == "grid"]
            self.assertEqual(len(grids), 1, path.name)
            inner = grids[0]["cards"]
            if any(c.get("type") == "conditional" for c in inner):
                continue  # dynamische Anzahl (Flur): nicht statisch prüfbar
            checked += 1
            self.assertEqual(len(inner) % 2, 0, f"{path.name}: {len(inner)} Kacheln im 2-Spalten-Grid")
        self.assertGreaterEqual(checked, 6)

    def test_tablet_overview_puts_scenes_into_the_right_column(self) -> None:
        from validate import _dashboard_views
        views, _ = _dashboard_views(REPO_ROOT, "tablet")
        overview = next(v for v in views if v["path"] == "overview")
        modes = [s for s in overview["sections"] if any(c.get("heading") == "Szenen & Modi" for c in s.get("cards", []))]
        self.assertEqual([s.get("column_span") for s in modes], [1])
        rooms = [v for v in _dashboard_views(REPO_ROOT, "tablet")[0] if v["path"] == "raeume"][0]
        self.assertEqual([s.get("column_span") for s in rooms["sections"] if any(c.get("heading") == "Szenen & Modi" for c in s.get("cards", []))], [2])


def _flatten_outside_stacks(node):
    """Wie _flatten, steigt aber nicht in stack-in-card ein (dort bestimmt der Stack die Breite)."""
    if isinstance(node, dict):
        yield node
        if node.get("type") == "custom:stack-in-card":
            return
        for value in node.values():
            yield from _flatten_outside_stacks(value)
    elif isinstance(node, list):
        for value in node:
            yield from _flatten_outside_stacks(value)


def _flatten(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _flatten(value)
    elif isinstance(node, list):
        for value in node:
            yield from _flatten(value)
