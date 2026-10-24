from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validate import validate_repository

REPO_ROOT = Path(__file__).resolve().parents[1]


class ValidateRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "entities.md").write_text(
            "- `sensor.documented`\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_yaml(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_package(self, version: str) -> None:
        """Repo package with its version sensor set to `version` (entities documented like the repo)."""
        docs = self.root / "docs" / "entities.md"
        docs.write_text(
            docs.read_text(encoding="utf-8") + (REPO_ROOT / "docs" / "entities.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        text = (REPO_ROOT / "packages" / "magguu_dashboard.yaml").read_text(encoding="utf-8")
        current = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.write_yaml("packages/magguu_dashboard.yaml", text.replace(f'state: "{current}"', f'state: "{version}"'))

    def test_accepts_home_assistant_tags_and_documented_entities(self) -> None:
        self.write_yaml("cards/item.yaml", "entity: sensor.documented\n")
        self.write_yaml("dashboard.yaml", "cards: !include cards/item.yaml\n")

        file_count, errors = validate_repository(self.root)

        self.assertEqual(file_count, 2)
        self.assertEqual(errors, [])

    def test_reports_invalid_yaml(self) -> None:
        self.write_yaml("broken.yaml", "items: [unterminated\n")

        _, errors = validate_repository(self.root)

        self.assertTrue(any("broken.yaml" in error for error in errors))

    def test_reports_missing_include(self) -> None:
        self.write_yaml("dashboard.yaml", "cards: !include cards/missing.yaml\n")

        _, errors = validate_repository(self.root)

        self.assertIn(
            "dashboard.yaml: !include-Ziel fehlt: cards/missing.yaml",
            errors,
        )

    def test_reports_undocumented_entity_references(self) -> None:
        self.write_yaml("dashboard.yaml", "entity: light.not_documented\n")

        _, errors = validate_repository(self.root)

        self.assertIn(
            "Nicht dokumentierte Entität light.not_documented: dashboard.yaml",
            errors,
        )



    def test_reports_version_drift(self) -> None:
        (self.root / "VERSION").write_text("1.0.0-dev\n", encoding="utf-8")
        self.write_package("9.9.9-dev")

        _, errors = validate_repository(self.root)

        self.assertTrue(any("Version drift" in error for error in errors))

    def test_reports_stale_version_in_readme(self) -> None:
        (self.root / "VERSION").write_text("1.0.0-dev\n", encoding="utf-8")
        self.write_package("1.0.0-dev")
        self.write_yaml("cards/item.yaml", "entity: sensor.documented\n")
        (self.root / "README.md").write_text("Beispiel `0.9.0-dev · abc1234`\n", encoding="utf-8")

        _, errors = validate_repository(self.root)

        self.assertIn("README.md: nennt Version 0.9.0-dev, VERSION ist 1.0.0-dev", errors)

    def test_accepts_matching_version(self) -> None:
        (self.root / "VERSION").write_text("1.0.0-dev\n", encoding="utf-8")
        self.write_package("1.0.0-dev")
        self.write_yaml("cards/item.yaml", "entity: sensor.documented\n")

        _, errors = validate_repository(self.root)

        self.assertEqual(errors, [])

    def test_reports_invalid_version_format(self) -> None:
        (self.root / "VERSION").write_text("v1\n", encoding="utf-8")
        self.write_package("v1")

        _, errors = validate_repository(self.root)

        self.assertTrue(any("kein gültiges Format" in error for error in errors))

    def test_reports_unguarded_button_card_js_access(self) -> None:
        self.write_yaml(
            "dashboard/magguu-dashboard/shared/templates/bad.yaml",
            "t:\n  styles:\n    icon:\n"
            "      - color: '[[[ return variables.accent; ]]]'\n"
            "      - background: '[[[ return `x ${variables?.accent} y`; ]]]'\n"
            "      - border: '[[[ return states[variables?.e]?.state; ]]]'\n"
            "      - fill: '[[[ return entity.state; ]]]'\n",
        )

        _, errors = validate_repository(self.root)

        found = [e for e in errors if "ungeschütztes JS-Template" in e]
        self.assertEqual(len(found), 4, errors)

    def test_accepts_guarded_button_card_js_access(self) -> None:
        self.write_yaml(
            "dashboard/magguu-dashboard/shared/templates/ok.yaml",
            "t:\n  styles:\n    icon:\n"
            "      - color: '[[[ return variables?.accent || \"#fff\"; ]]]'\n"
            "      - fill: '[[[ return states?.[variables?.e]?.state ?? entity?.state; ]]]'\n",
        )

        _, errors = validate_repository(self.root)

        self.assertFalse(any("ungeschütztes JS-Template" in e for e in errors), errors)

    def test_reports_duplicate_yaml_mapping_keys(self) -> None:
        self.write_yaml(
            "dashboard/magguu-dashboard/shared/cards/dup.yaml",
            "type: tile\nentity: sensor.documented\ncard_mod: {style: a}\ncard_mod: {style: b}\n",
        )

        _, errors = validate_repository(self.root)

        self.assertTrue(any("doppelter Schlüssel 'card_mod'" in error for error in errors), errors)

    def test_allows_yaml_merge_keys_and_anchors(self) -> None:
        self.write_yaml(
            "dashboard/magguu-dashboard/shared/cards/merge.yaml",
            "base: &b {a: 1}\nmerged:\n  <<: *b\n  a: 2\n",
        )

        _, errors = validate_repository(self.root)

        self.assertFalse(any("doppelter Schlüssel" in error for error in errors), errors)

    def test_reports_missing_mobile_navbar_clearance_token(self) -> None:
        self.write_yaml(
            "dashboard/magguu-dashboard/mobile/views/01-overview.yaml",
            "- title: Home\n"
            "  type: custom:grid-layout\n"
            "  layout:\n"
            "    padding: var(--mag-space-page-mobile, 10px)\n"
            "  cards: []\n",
        )

        _, errors = validate_repository(self.root)

        self.assertTrue(
            any("mag-space-navbar-clearance" in error for error in errors)
        )

    def test_accepts_mobile_shell_tokens(self) -> None:
        self.write_yaml(
            "dashboard/magguu-dashboard/mobile/views/01-overview.yaml",
            "- title: Home\n"
            "  type: custom:grid-layout\n"
            "  layout:\n"
            "    max-width: var(--mag-content-max-width-narrow, 760px)\n"
            "    padding: var(--mag-space-page-mobile, 10px) "
            "var(--mag-space-page-mobile, 10px) "
            "var(--mag-space-navbar-clearance, 96px)\n"
            "  cards:\n"
            "    - entity: sensor.documented\n",
        )

        _, errors = validate_repository(self.root)

        self.assertFalse(
            any("Theme-Token" in error or "navbar-clearance" in error or "max-width hart" in error for error in errors)
        )

if __name__ == "__main__":
    unittest.main()
