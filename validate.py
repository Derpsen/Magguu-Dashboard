#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parent

class HomeAssistantLoader(yaml.SafeLoader):
    pass

def construct_unknown(loader: HomeAssistantLoader, tag_suffix: str, node: yaml.Node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)

HomeAssistantLoader.add_multi_constructor("!", construct_unknown)

errors: list[str] = []
files = sorted([*ROOT.rglob("*.yaml"), *ROOT.rglob("*.yml")])
for path in files:
    try:
        with path.open("r", encoding="utf-8") as handle:
            yaml.load(handle, Loader=HomeAssistantLoader)
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")

if errors:
    print("YAML-Prüfung fehlgeschlagen:")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)

print(f"YAML-Prüfung erfolgreich: {len(files)} Dateien")
