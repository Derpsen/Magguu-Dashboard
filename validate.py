#!/usr/bin/env python3
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
import json
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


VERSION_FORMAT_PATTERN = re.compile(r"\d+\.\d+\.\d+(?:-dev)?")


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
    if not VERSION_FORMAT_PATTERN.fullmatch(version):
        return [f"VERSION hat kein gültiges Format (X.Y.Z oder X.Y.Z-dev): {version}"]
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


# shell_command services can be called by any HA user (not admin-gated), so
# every entry must be a fixed command without templates (no service-data
# input) and the updater it runs must not read arguments or environment.
ALLOWED_SHELL_COMMANDS = {
    "magguu_dashboard_update": "sh /config/magguu-dashboard-update.sh",
}
TEMPLATE_MARKERS = ("{{", "{%", "{#")
UPDATER_FIXED_LINES = (
    "CONFIG_DIR=/config",
    "ARCHIVE_URL=https://github.com/Derpsen/Magguu-Dashboard/archive/refs/heads/main.tar.gz",
    "CURL_PROTO='=https'",
    'MAGGUU_COMMIT_SHA=""',
)
# The download must stay https-only (also after redirects) and time-boxed.
UPDATER_REQUIRED_SNIPPETS = (
    '--proto "$CURL_PROTO"',
    '--proto-redir "$CURL_PROTO"',
    "--max-time",
)
# Set by the sourced installer (scripts/install-dashboard.sh), not by the caller.
UPDATER_SOURCED_VARS = {"MAGGUU_BACKUP_DIR"}
SHELL_VAR_PATTERN = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*|[0-9@*#])")
SHELL_ASSIGN_PATTERN = re.compile(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)=")


def validate_shell_commands(documents: Mapping[Path, Any], root: Path) -> list[str]:
    errors: list[str] = []
    for path, document in documents.items():
        if not isinstance(document, Mapping) or "shell_command" not in document:
            continue
        rel = path.relative_to(root)
        commands = document["shell_command"]
        if not isinstance(commands, Mapping):
            errors.append(f"{rel}: shell_command muss eine Map sein")
            continue
        for name, command in commands.items():
            if not isinstance(command, str):
                errors.append(f"{rel}: shell_command.{name} muss ein fester String sein")
                continue
            if any(marker in command for marker in TEMPLATE_MARKERS):
                errors.append(f"{rel}: shell_command.{name} enthält Templates ({{{{ }}}}/{{% %}})")
            if ALLOWED_SHELL_COMMANDS.get(str(name)) != command:
                errors.append(
                    f"{rel}: shell_command.{name} ist nicht erlaubt "
                    "(nur der feste Update-Befehl, siehe ALLOWED_SHELL_COMMANDS)"
                )
    return errors


def validate_updater(root: Path) -> list[str]:
    path = root / "update-ha.sh"
    if not path.is_file():
        return []
    code = "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )
    errors: list[str] = []
    lines = set(code.splitlines())
    for fixed in UPDATER_FIXED_LINES:
        if fixed not in lines:
            errors.append(f"update-ha.sh: feste Zeile fehlt: {fixed}")
    for snippet in UPDATER_REQUIRED_SNIPPETS:
        if snippet not in code:
            errors.append(f"update-ha.sh: erforderlicher Teil fehlt: {snippet}")
    assigned = set(SHELL_ASSIGN_PATTERN.findall(code)) | UPDATER_SOURCED_VARS
    for name in sorted(set(SHELL_VAR_PATTERN.findall(code))):
        if name[0].isdigit() or name in {"@", "*", "#"}:
            errors.append(f"update-ha.sh: liest Argumente (${name})")
        elif name not in assigned:
            errors.append(f"update-ha.sh: liest Umgebungsvariable ${name}")
    return errors


# Installed version + commit and update hint (System page). The installed
# commit is stamped by the installer; the newest main commit comes from one
# unauthenticated REST call to the public GitHub API, polled at most hourly.
MAIN_COMMIT_URL = "https://api.github.com/repos/Derpsen/Magguu-Dashboard/commits/main"
MAIN_COMMIT_REST_KEYS = {"resource", "scan_interval", "timeout", "headers", "sensor"}
MAIN_COMMIT_HEADERS = {"Accept", "User-Agent"}
MIN_SCAN_INTERVAL_SECONDS = 3600
FULL_SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
VALUE_JSON_PATTERN = re.compile(r"value_json\.(\w+)")
HINT_STATES = ("aktuell", "verfuegbar", "unbekannt")
VERSION_CARD_SENSORS = (
    "sensor.magguu_dashboard_version",
    "sensor.magguu_dashboard_commit",
    "sensor.magguu_dashboard_main_commit",
    "sensor.magguu_dashboard_update_hinweis",
)


def _template_sensors(document: Any) -> dict[str, Mapping[str, Any]]:
    sensors: dict[str, Mapping[str, Any]] = {}
    templates = document.get("template") if isinstance(document, Mapping) else None
    for block in templates if isinstance(templates, list) else []:
        entries = block.get("sensor") if isinstance(block, Mapping) else None
        for sensor in entries if isinstance(entries, list) else []:
            if isinstance(sensor, Mapping) and isinstance(sensor.get("unique_id"), str):
                sensors[sensor["unique_id"]] = sensor
    return sensors


def validate_update_hint(root: Path) -> list[str]:
    package_path = root / "packages" / "magguu_dashboard.yaml"
    if not package_path.is_file():
        return []
    rel = "packages/magguu_dashboard.yaml"
    text = package_path.read_text(encoding="utf-8")
    try:
        document = load_yaml(package_path)
    except Exception:  # reported by validate_yaml
        return []
    errors: list[str] = []

    rest = document.get("rest") if isinstance(document, Mapping) else None
    entries = [e for e in rest if isinstance(e, Mapping)] if isinstance(rest, list) else []
    if "!secret" in text or re.search(
        r"(?i)authorization|authentication|bearer|token|password|username", json.dumps(entries, default=str)
    ):
        errors.append(f"{rel}: Update-Hinweis muss ohne Secrets/Token/Authorization auskommen")
    if len(entries) != 1 or entries[0].get("resource") != MAIN_COMMIT_URL:
        errors.append(f"{rel}: rest muss genau die öffentliche GitHub-main-Commit-URL abfragen ({MAIN_COMMIT_URL})")
    else:
        entry = entries[0]
        for key in sorted(set(entry) - MAIN_COMMIT_REST_KEYS):
            errors.append(f"{rel}: rest-Eintrag darf {key} nicht setzen")
        interval = entry.get("scan_interval")
        if not isinstance(interval, int) or interval < MIN_SCAN_INTERVAL_SECONDS:
            errors.append(f"{rel}: rest scan_interval muss mindestens {MIN_SCAN_INTERVAL_SECONDS} s sein")
        headers = entry.get("headers")
        if not isinstance(headers, Mapping) or set(headers) - MAIN_COMMIT_HEADERS:
            errors.append(f"{rel}: rest headers nur {sorted(MAIN_COMMIT_HEADERS)} erlaubt")
        sensors = entry.get("sensor")
        sensors = sensors if isinstance(sensors, list) else []
        main = [x for x in sensors if isinstance(x, Mapping) and x.get("unique_id") == "magguu_dashboard_main_commit"]
        if len(sensors) != 1 or len(main) != 1:
            errors.append(f"{rel}: rest braucht genau den Sensor magguu_dashboard_main_commit")
        else:
            template = str(main[0].get("value_template", ""))
            if set(VALUE_JSON_PATTERN.findall(template)) != {"sha"}:
                errors.append(f"{rel}: magguu_dashboard_main_commit liest nur value_json.sha")
            if "unbekannt" not in template or "mapping" not in template:
                errors.append(f"{rel}: magguu_dashboard_main_commit braucht Fallback 'unbekannt' bei fehlerhafter Antwort")

    template_sensors = _template_sensors(document)
    commit = template_sensors.get("magguu_dashboard_commit")
    if commit is None:
        errors.append(f"{rel}: Sensor magguu_dashboard_commit fehlt")
    else:
        state = str(commit.get("state", ""))
        if state != "unbekannt" and not FULL_SHA_PATTERN.fullmatch(state):
            errors.append(f"{rel}: magguu_dashboard_commit state muss 'unbekannt' oder eine 40-stellige SHA sein")
    hint = template_sensors.get("magguu_dashboard_update_hinweis")
    if hint is None:
        errors.append(f"{rel}: Sensor magguu_dashboard_update_hinweis fehlt")
    else:
        state = str(hint.get("state", ""))
        if state.count("regex_match") < 2 or not all(w in state for w in HINT_STATES):
            errors.append(
                f"{rel}: magguu_dashboard_update_hinweis muss beide SHAs per regex_match prüfen "
                f"und {'/'.join(HINT_STATES)} liefern"
            )
        for entity in ("sensor.magguu_dashboard_commit", "sensor.magguu_dashboard_main_commit"):
            if entity not in state:
                errors.append(f"{rel}: magguu_dashboard_update_hinweis nutzt {entity} nicht")

    system_path = root / "dashboard" / "magguu-dashboard" / "shared" / "cards" / "system.yaml"
    if system_path.is_file():
        system = system_path.read_text(encoding="utf-8")
        for entity in VERSION_CARD_SENSORS:
            if entity not in system:
                errors.append(f"shared/cards/system.yaml: Versionskarte nutzt {entity} nicht")
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
    errors.extend(validate_shell_commands(documents, root))
    errors.extend(validate_updater(root))
    errors.extend(validate_update_hint(root))
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
