#!/usr/bin/env python3
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
import re
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
YAML_SUFFIXES = {".yaml", ".yml"}
INCLUDE_TAGS = {
    "include",
    "include_dir_list",
    "include_dir_merge_list",
    "include_dir_named",
    "include_dir_merge_named",
}
INCLUDE_PATTERN = re.compile(
    r"!(?P<tag>include(?:_dir_(?:merge_)?(?:list|named))?)\s+"
    r"(?P<target>[^#\r\n]+)"
)
ENTITY_ID_PATTERN = re.compile(
    r"\b(?:alarm_control_panel|automation|binary_sensor|button|calendar|camera|"
    r"climate|cover|device_tracker|event|fan|group|input_boolean|input_button|"
    r"input_datetime|input_number|input_select|light|lock|media_player|number|"
    r"person|remote|scene|script|select|sensor|sun|switch|timer|update|vacuum|"
    r"weather)\.[a-zA-Z0-9_]+\b"
)
STATE_REFERENCE_PATTERN = re.compile(r"states\[['\"]([^'\"]+)['\"]\]")
DOCUMENTED_ENTITY_PATTERN = re.compile(r"`([^`]+\.[^`]+)`")
ENTITY_REFERENCE_KEYS = {"entity", "entity_id", "entities"}


class HomeAssistantLoader(yaml.SafeLoader):
    """Safe YAML loader that preserves values of Home Assistant tags."""


def construct_unknown(
    loader: HomeAssistantLoader,
    _tag_suffix: str,
    node: yaml.Node,
) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


HomeAssistantLoader.add_multi_constructor("!", construct_unknown)


def yaml_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in YAML_SUFFIXES and ".git" not in path.parts
    )


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=HomeAssistantLoader)


def validate_yaml(paths: Iterable[Path], root: Path) -> tuple[dict[Path, Any], list[str]]:
    documents: dict[Path, Any] = {}
    errors: list[str] = []
    for path in paths:
        try:
            documents[path] = load_yaml(path)
        except Exception as exc:  # PyYAML exposes multiple useful parser error types.
            errors.append(f"{path.relative_to(root)}: {exc}")
    return documents, errors


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def validate_includes(paths: Iterable[Path], root: Path) -> list[str]:
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for match in INCLUDE_PATTERN.finditer(text):
            tag = match.group("tag")
            if tag not in INCLUDE_TAGS:
                continue
            target_text = _unquote(match.group("target"))
            target = (path.parent / target_text).resolve()
            if not target.exists():
                errors.append(
                    f"{path.relative_to(root)}: !{tag}-Ziel fehlt: {target_text}"
                )
    return errors


def _entity_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield from ENTITY_ID_PATTERN.findall(value)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            yield from _entity_values(item)


def _referenced_entities(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str) and (
                key in ENTITY_REFERENCE_KEYS or key.endswith("_entity")
            ):
                yield from _entity_values(child)
            yield from _referenced_entities(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            yield from _referenced_entities(child)
    elif isinstance(value, str):
        for candidate in STATE_REFERENCE_PATTERN.findall(value):
            if ENTITY_ID_PATTERN.fullmatch(candidate):
                yield candidate


def documented_entities(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return {
        candidate
        for candidate in DOCUMENTED_ENTITY_PATTERN.findall(text)
        if ENTITY_ID_PATTERN.fullmatch(candidate)
    }


def validate_entities(
    documents: Mapping[Path, Any],
    documentation_path: Path,
    root: Path,
) -> list[str]:
    documented = documented_entities(documentation_path)
    referenced: dict[str, set[Path]] = {}
    for path, document in documents.items():
        for entity_id in _referenced_entities(document):
            referenced.setdefault(entity_id, set()).add(path)

    errors: list[str] = []
    for entity_id in sorted(set(referenced) - documented):
        locations = ", ".join(
            str(path.relative_to(root)) for path in sorted(referenced[entity_id])
        )
        errors.append(f"Nicht dokumentierte Entität {entity_id}: {locations}")
    return errors


VERSION_SENSOR_PATTERN = re.compile(
    r"unique_id:\s*magguu_dashboard_version\b.*?^\s*state:\s*[\"']([^\"']+)[\"']",
    re.MULTILINE | re.DOTALL,
)


def validate_version(root: Path) -> list[str]:
    package_path = root / "packages" / "magguu_dashboard.yaml"
    if not package_path.is_file():
        return []
    version_path = root / "VERSION"
    if not version_path.is_file():
        return ["VERSION fehlt"]
    version = version_path.read_text(encoding="utf-8").replace("\ufeff", "").strip()
    if not version:
        return ["VERSION ist leer"]
    match = VERSION_SENSOR_PATTERN.search(package_path.read_text(encoding="utf-8"))
    if match is None:
        return [
            "packages/magguu_dashboard.yaml: Sensor magguu_dashboard_version ohne state"
        ]
    if match.group(1) != version:
        return [
            "Version drift: VERSION="
            f"{version} vs packages/magguu_dashboard.yaml={match.group(1)}"
        ]
    return []


def validate_view_shell_tokens(root: Path) -> list[str]:
    """Ensure mobile/tablet grid-layout shells keep layout spacing on theme tokens."""
    errors: list[str] = []
    for device in ("mobile", "tablet"):
        views_dir = root / "dashboard" / "magguu-dashboard" / device / "views"
        if not views_dir.is_dir():
            continue
        for path in sorted(views_dir.glob("*.yaml")):
            text = path.read_text(encoding="utf-8")
            if "type: custom:grid-layout" not in text:
                continue
            rel = path.relative_to(root)
            if "padding:" in text and "var(--mag-space-page-" not in text:
                errors.append(
                    f"{rel}: Layout-padding ohne Theme-Token (--mag-space-page-*)"
                )
            if device == "mobile" and "padding:" in text and (
                "var(--mag-space-navbar-clearance" not in text
            ):
                errors.append(
                    f"{rel}: Mobile-Bottom-Padding ohne --mag-space-navbar-clearance"
                )
            if device == "tablet" and re.search(
                r"(?m)^\s*max-width:\s*1460px\s*$", text
            ):
                errors.append(
                    f"{rel}: Tablet max-width hart 1460px statt --mag-content-max-width"
                )
            if device == "mobile" and re.search(
                r"(?m)^\s*max-width:\s*760px\s*$", text
            ):
                errors.append(
                    f"{rel}: Mobile max-width hart 760px statt --mag-content-max-width-narrow"
                )
    return errors


def validate_repository(root: Path = ROOT) -> tuple[int, list[str]]:
    paths = yaml_files(root)
    documents, errors = validate_yaml(paths, root)
    errors.extend(validate_includes(paths, root))

    documentation_path = root / "docs" / "entities.md"
    if documentation_path.is_file():
        errors.extend(validate_entities(documents, documentation_path, root))
    else:
        errors.append("docs/entities.md fehlt")

    errors.extend(validate_version(root))
    errors.extend(validate_view_shell_tokens(root))
    return len(paths), errors


def main() -> int:
    file_count, errors = validate_repository()
    if errors:
        print("Dashboard-Prüfung fehlgeschlagen:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(
        f"Dashboard-Prüfung erfolgreich: {file_count} YAML-Dateien, "
        "Includes und Entitätsreferenzen"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
