from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validate import validate_repository


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
        self.write_yaml(
            "packages/magguu_dashboard.yaml",
            "template:\n"
            "  - sensor:\n"
            "      - unique_id: magguu_dashboard_version\n"
            '        state: "9.9.9-dev"\n',
        )

        _, errors = validate_repository(self.root)

        self.assertTrue(any("Version drift" in error for error in errors))

    def test_accepts_matching_version(self) -> None:
        (self.root / "VERSION").write_text("1.0.0-dev\n", encoding="utf-8")
        self.write_yaml(
            "packages/magguu_dashboard.yaml",
            "template:\n"
            "  - sensor:\n"
            "      - unique_id: magguu_dashboard_version\n"
            '        state: "1.0.0-dev"\n',
        )
        self.write_yaml("cards/item.yaml", "entity: sensor.documented\n")

        _, errors = validate_repository(self.root)

        self.assertEqual(errors, [])

if __name__ == "__main__":
    unittest.main()
