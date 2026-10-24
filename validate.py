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


# ---------------------------------------------------------------------------
# Dashboard structure (offline schema checks, resolved through the !include
# tags). Sources for the allowed keys/values: home-assistant.io/dashboards
# (sections, views, heading, tile, features, badges) and the frontend types
# `src/data/lovelace/config/view.ts` / `section.ts`; see MEMORY.md.
# ---------------------------------------------------------------------------
DASHBOARD_DIR = ("dashboard", "magguu-dashboard")
DASHBOARD_URLS = {"mobile": "magguu-mobile", "tablet": "magguu-tablet"}
VIEW_TYPES = {None, "sections", "masonry", "panel", "sidebar", "custom:grid-layout"}
VIEW_KEYS = {
    "title", "path", "icon", "show_icon_and_title", "theme", "panel", "background",
    "visible", "subview", "back_path", "max_columns", "dense_section_placement",
    "top_margin", "type", "badges", "cards", "sections", "header", "footer", "sidebar",
    "layout",  # layout-card view options (custom:grid-layout)
}
SECTION_KEYS = {
    "type", "cards", "badges", "sections", "visibility", "disabled", "column_span",
    "row_span", "background", "theme", "title",
}
VIEW_PATH_PATTERN = re.compile(r"[a-z][a-z0-9_-]*")
# Built-in card types (home-assistant.io/dashboards/cards) plus the custom cards
# that are already documented as dependencies in README.md. New custom cards
# must be added here AND to the README on purpose (no silent new dependency).
BUILTIN_CARD_TYPES = {
    "alarm-panel", "area", "button", "calendar", "clock", "conditional", "distribution",
    "entities", "entity", "entity-filter", "gauge", "glance", "grid", "heading",
    "history-graph", "horizontal-stack", "humidifier", "light", "map", "markdown",
    "media-control", "picture", "picture-elements", "picture-entity", "picture-glance",
    "plant-status", "sensor", "shortcut", "statistic", "statistics-graph", "thermostat",
    "tile", "todo-list", "vertical-stack", "weather-forecast", "webpage",
}
ALLOWED_CUSTOM_CARDS = {
    "custom:button-card", "custom:grid-layout", "custom:layout-card",
    "custom:mini-graph-card", "custom:mushroom-template-card",
    "custom:navbar-card", "custom:stack-in-card",
    "custom:auto-entities",
}
# Tile features listed on home-assistant.io/dashboards/features.
TILE_FEATURE_TYPES = {
    "alarm-modes", "bar-gauge", "button", "climate-fan-modes", "climate-hvac-modes",
    "climate-preset-modes", "climate-swing-modes", "climate-swing-horizontal-modes",
    "counter-actions", "cover-open-close", "cover-position", "cover-position-favorite",
    "cover-tilt", "cover-tilt-favorite", "cover-tilt-position", "date-set",
    "fan-direction", "fan-oscillate", "fan-preset-modes", "fan-speed",
    "humidifier-modes", "humidifier-toggle", "lawn-mower-commands", "light-brightness",
    "light-color-favorites", "light-color-temp", "light-effect", "lock-commands",
    "lock-open-door", "media-player-playback", "media-player-sound-mode",
    "media-player-source", "media-player-volume-buttons", "media-player-volume-slider",
    "numeric-input", "select-options", "target-humidity", "target-temperature",
    "timer-actions", "timer-presets", "toggle", "trend-graph", "update-actions",
    "vacuum-commands", "vacuum-fan-speed", "valve-open-close", "valve-position",
    "valve-position-favorite", "water-heater-operation-modes", "area-controls",
    "temperature-forecast", "precipitation-forecast",
}
HEADING_STYLES = {"title", "subtitle"}
HEADING_KEYS = {
    "type", "heading", "heading_style", "icon", "tap_action", "badges", "view_layout",
    "grid_options", "card_mod", "visibility",
}
HEADING_BADGE_TYPES = {"entity", "button"}
CARD_CONTAINER_KEYS = ("cards", "card")
THEME_MODES = {"light", "dark"}
MAG_TOKEN_PATTERN = re.compile(r"var\(--(mag-[a-z0-9-]+)")


def _resolve_include_dir(directory: Path, tag: str, root: Path, seen: tuple[Path, ...]) -> Any:
    files = sorted(
        p for p in directory.rglob("*")
        if p.is_file() and p.suffix.lower() in YAML_SUFFIXES
        and not any(part.startswith(".") for part in p.relative_to(directory).parts)
    )
    loaded = [(p, load_resolved(p, root, seen)) for p in files]
    if tag == "include_dir_list":
        return [doc for _, doc in loaded]
    if tag == "include_dir_named":
        return {p.stem: doc for p, doc in loaded}
    if tag == "include_dir_merge_list":
        merged: list[Any] = []
        for _, doc in loaded:
            merged.extend(doc if isinstance(doc, list) else [doc])
        return merged
    merged_named: dict[Any, Any] = {}
    for _, doc in loaded:
        if isinstance(doc, Mapping):
            merged_named.update(doc)
    return merged_named


def load_resolved(path: Path, root: Path, seen: tuple[Path, ...] = ()) -> Any:
    """Load YAML and replace `!include*` tags by the included content."""
    path = path.resolve()
    if path in seen:
        raise ValueError(f"zyklisches Include: {path.name}")
    if root.resolve() not in path.parents and path != root.resolve():
        raise ValueError(f"Include außerhalb des Repos: {path}")
    chain = (*seen, path)

    class _Loader(HomeAssistantLoader):
        pass

    def include(tag: str):
        def construct(loader: yaml.Loader, node: yaml.Node) -> Any:
            target = (path.parent / str(loader.construct_scalar(node)).strip()).resolve()
            if tag == "include":
                return load_resolved(target, root, chain)
            return _resolve_include_dir(target, tag, root, chain)
        return construct

    for tag in INCLUDE_TAGS:
        _Loader.add_constructor(f"!{tag}", include(tag))
    with path.open("r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=_Loader)


def _iter_cards(node: Any) -> Iterable[Mapping[str, Any]]:
    """Yield every card mapping below `node` (stacks, conditionals, sections, layout-card)."""
    if isinstance(node, Mapping):
        if isinstance(node.get("type"), str) and (
            "entity" in node or "cards" in node or "card" in node or "heading" in node
            or node["type"] in BUILTIN_CARD_TYPES or node["type"].startswith("custom:")
        ):
            yield node
        for key in CARD_CONTAINER_KEYS + ("sections", "badges", "header", "footer"):
            if key in node:
                yield from _iter_cards(node[key])
    elif isinstance(node, list):
        for child in node:
            yield from _iter_cards(child)


def _dashboard_views(root: Path, device: str) -> tuple[list[Mapping[str, Any]], list[str]]:
    path = root.joinpath(*DASHBOARD_DIR, device, "dashboard.yaml")
    if not path.is_file():
        return [], []
    rel = path.relative_to(root)
    try:
        document = load_resolved(path, root)
    except Exception as exc:  # reported with context
        return [], [f"{rel}: Includes nicht auflösbar: {exc}"]
    views = document.get("views") if isinstance(document, Mapping) else None
    if not isinstance(views, list):
        return [], [f"{rel}: views muss eine Liste sein"]
    return [v for v in views if isinstance(v, Mapping)], []


def theme_definitions(root: Path) -> dict[str, Any]:
    themes: dict[str, Any] = {}
    themes_dir = root / "themes"
    for path in sorted(themes_dir.glob("*.yaml")) if themes_dir.is_dir() else []:
        document = load_yaml(path)
        if isinstance(document, Mapping):
            themes.update(document)
    return themes


def validate_themes(root: Path) -> list[str]:
    errors: list[str] = []
    for name, theme in theme_definitions(root).items():
        if not isinstance(theme, Mapping):
            errors.append(f"themes: Theme {name} muss eine Map sein")
            continue
        modes = theme.get("modes")
        if modes is None:
            continue
        if not isinstance(modes, Mapping) or not modes or set(modes) - THEME_MODES:
            errors.append(f"themes: {name}.modes darf nur {sorted(THEME_MODES)} enthalten")
            continue
        for mode, values in modes.items():
            if not isinstance(values, Mapping) or not values:
                errors.append(f"themes: {name}.modes.{mode} muss Variablen enthalten")
    return errors


def _theme_tokens(theme: Mapping[str, Any]) -> set[str]:
    tokens = {k for k in theme if k != "modes"}
    modes = theme.get("modes")
    for values in modes.values() if isinstance(modes, Mapping) else []:
        if isinstance(values, Mapping):
            tokens |= set(values)
    return tokens


def validate_dashboards(root: Path) -> list[str]:
    errors: list[str] = []
    themes = theme_definitions(root)
    for device, url in DASHBOARD_URLS.items():
        views, load_errors = _dashboard_views(root, device)
        errors.extend(load_errors)
        paths: dict[str, int] = {}
        for index, view in enumerate(views):
            where = f"{device}/view {index} ({view.get('path') or view.get('title')})"
            vpath = view.get("path")
            if not isinstance(vpath, str) or not VIEW_PATH_PATTERN.fullmatch(vpath):
                errors.append(f"{where}: path muss mit Buchstabe beginnen und nur a-z 0-9 _ - enthalten")
            elif vpath in paths:
                errors.append(f"{where}: doppelter View-Pfad {vpath}")
            else:
                paths[vpath] = index
            if not isinstance(view.get("title"), str) or not view.get("title"):
                errors.append(f"{where}: title fehlt")
            vtype = view.get("type")
            if vtype not in VIEW_TYPES:
                errors.append(f"{where}: unbekannter View-Typ {vtype!r}")
            for key in sorted(set(view) - VIEW_KEYS):
                errors.append(f"{where}: unbekannter View-Schlüssel {key}")
            theme = view.get("theme")
            if theme is not None and theme not in themes:
                errors.append(f"{where}: Theme {theme!r} existiert nicht in themes/")
            if vtype == "sections":
                if not isinstance(view.get("sections"), list) or not view["sections"]:
                    errors.append(f"{where}: sections-View braucht eine nicht leere sections-Liste")
                if "cards" in view or "layout" in view:
                    errors.append(f"{where}: sections-View darf weder cards noch layout (layout-card) setzen")
                maxc = view.get("max_columns")
                if maxc is not None and (isinstance(maxc, bool) or not isinstance(maxc, int) or maxc < 1):
                    errors.append(f"{where}: max_columns muss eine ganze Zahl >= 1 sein")
                for s_index, section in enumerate(view.get("sections") or []):
                    swhere = f"{where}/section {s_index}"
                    if not isinstance(section, Mapping):
                        errors.append(f"{swhere}: Section muss eine Map sein")
                        continue
                    for key in sorted(set(section) - SECTION_KEYS):
                        errors.append(f"{swhere}: unbekannter Section-Schlüssel {key}")
                    if section.get("type", "grid") != "grid":
                        errors.append(f"{swhere}: Section-Typ muss grid sein")
                    if not isinstance(section.get("cards"), list) or not section["cards"]:
                        errors.append(f"{swhere}: Section braucht eine nicht leere cards-Liste")
                    span = section.get("column_span")
                    if span is not None and (isinstance(span, bool) or not isinstance(span, int) or span < 1):
                        errors.append(f"{swhere}: column_span muss eine ganze Zahl >= 1 sein")
                    elif isinstance(span, int) and isinstance(maxc, int) and span > maxc:
                        errors.append(f"{swhere}: column_span {span} größer als max_columns {maxc}")
            elif vtype == "custom:grid-layout" and "sections" in view:
                errors.append(f"{where}: grid-layout-View darf keine sections setzen")
            for card in _iter_cards(view):
                errors.extend(_validate_card(card, where))
        # Navigation targets inside this dashboard must exist.
        for index, view in enumerate(views):
            for target in _navigation_targets(view):
                prefix = f"/{url}/"
                if target.startswith("/magguu-") and not target.startswith(prefix):
                    errors.append(f"{device}: navigation_path {target} zeigt auf das andere Dashboard")
                elif target.startswith(prefix) and target[len(prefix):].split("/")[0] not in paths:
                    errors.append(f"{device}: navigation_path {target} zeigt auf keinen View")
            for route in _navbar_routes(view):
                if route not in paths:
                    errors.append(f"{device}: navbar-Route {route} zeigt auf keinen View")
    errors.extend(_validate_theme_tokens(root, themes))
    return sorted(set(errors))


def _validate_card(card: Mapping[str, Any], where: str) -> list[str]:
    errors: list[str] = []
    ctype = card.get("type")
    if not isinstance(ctype, str):
        return errors
    if ctype not in BUILTIN_CARD_TYPES and ctype not in ALLOWED_CUSTOM_CARDS:
        errors.append(
            f"{where}: Kartentyp {ctype} ist keine dokumentierte Abhängigkeit "
            "(neue Custom-Cards nur bewusst in validate.py + README ergänzen)"
        )
    if ctype == "tile":
        if not isinstance(card.get("entity"), str):
            errors.append(f"{where}: tile ohne entity")
        for feature in card.get("features") or []:
            ftype = feature.get("type") if isinstance(feature, Mapping) else None
            if ftype not in TILE_FEATURE_TYPES:
                errors.append(f"{where}: unbekanntes Tile-Feature {ftype!r}")
        position = card.get("features_position")
        if position is not None and position not in {"bottom", "inline"}:
            errors.append(f"{where}: features_position muss bottom oder inline sein")
    if ctype == "heading":
        for key in sorted(set(card) - HEADING_KEYS):
            errors.append(f"{where}: heading-Karte kennt {key} nicht")
        if not isinstance(card.get("heading"), str) or not card["heading"].strip():
            errors.append(f"{where}: heading-Karte braucht einen Text (heading)")
        style = card.get("heading_style")
        if style is not None and style not in HEADING_STYLES:
            errors.append(f"{where}: heading_style muss title oder subtitle sein")
        for badge in card.get("badges") or []:
            if not isinstance(badge, Mapping) or badge.get("type") not in HEADING_BADGE_TYPES:
                errors.append(f"{where}: heading-badges nur vom Typ entity oder button")
    return errors


def _walk(node: Any) -> Iterable[Any]:
    yield node
    if isinstance(node, Mapping):
        for child in node.values():
            yield from _walk(child)
    elif isinstance(node, list):
        for child in node:
            yield from _walk(child)


def _navigation_targets(view: Any) -> Iterable[str]:
    for node in _walk(view):
        if isinstance(node, Mapping) and isinstance(node.get("navigation_path"), str):
            yield node["navigation_path"]


def _navbar_routes(view: Any) -> Iterable[str]:
    for node in _walk(view):
        if isinstance(node, Mapping) and node.get("type") == "custom:navbar-card":
            for route in node.get("routes") or []:
                url = route.get("url") if isinstance(route, Mapping) else None
                if isinstance(url, str) and not url.startswith(("/", "http")):
                    yield url


def _validate_theme_tokens(root: Path, themes: Mapping[str, Any]) -> list[str]:
    """Every `var(--mag-*)` used in dashboards/packages must exist in each used theme."""
    if not themes:
        return []
    used: set[str] = set()
    for path in yaml_files(root / DASHBOARD_DIR[0]) if (root / DASHBOARD_DIR[0]).is_dir() else []:
        used |= set(MAG_TOKEN_PATTERN.findall(path.read_text(encoding="utf-8")))
    errors = []
    for name, theme in themes.items():
        if not isinstance(theme, Mapping):
            continue
        for token in sorted(used - _theme_tokens(theme)):
            errors.append(f"themes: Theme {name} definiert --{token} nicht (in Dashboards verwendet)")
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
    errors.extend(validate_themes(root))
    errors.extend(validate_dashboards(root))
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
