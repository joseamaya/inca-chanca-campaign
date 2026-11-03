#!/usr/bin/env python3
"""Validate the mod without launching 0 A.D."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")
VERSION_RE = re.compile(r"^[0-9]+(\.[0-9]+){0,2}$")
DEP_RE = re.compile(r"^[a-zA-Z0-9_-]+(?:<=|>=|<|>|=)[0-9]+(\.[0-9]+){0,2}$")

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def check_mod_json() -> dict:
    path = ROOT / "mod.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        fail(f"mod.json: {exc}")
        return {}
    for key in ("name", "version", "label", "description", "dependencies"):
        if not data.get(key):
            fail(f"mod.json: missing or empty {key!r}")
    if data.get("name") and not NAME_RE.fullmatch(data["name"]):
        fail(f"mod.json: invalid name {data['name']!r}")
    if data.get("version") and not VERSION_RE.fullmatch(data["version"]):
        fail(f"mod.json: invalid version {data['version']!r}")
    for dep in data.get("dependencies", []):
        if not (NAME_RE.fullmatch(dep) or DEP_RE.fullmatch(dep)):
            fail(f"mod.json: invalid dependency {dep!r}")
    if not (ROOT / "thumbnail.png").is_file():
        fail("thumbnail.png is missing")
    return data


def check_xml() -> int:
    count = 0
    for path in ROOT.rglob("*.xml"):
        try:
            ET.parse(path)
            count += 1
        except Exception as exc:
            fail(f"{path.relative_to(ROOT)}: {exc}")
    return count


def check_json() -> int:
    count = 0
    for path in ROOT.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
            count += 1
        except Exception as exc:
            fail(f"{path.relative_to(ROOT)}: {exc}")
    return count


def check_js() -> None:
    node = shutil.which("node")
    if not node:
        warnings.append("node not found; skipping JavaScript syntax checks")
        return
    for path in sorted((ROOT / "maps/scenarios").glob("*.js")):
        proc = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
        if proc.returncode:
            fail(f"{path.relative_to(ROOT)}: {proc.stderr.strip()}")


def check_campaign() -> None:
    path = ROOT / "campaigns/inca_chanca.json"
    try:
        campaign = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"campaigns/inca_chanca.json: {exc}")
        return
    levels = campaign.get("Levels", {})
    order = campaign.get("Order", [])
    for index, name in enumerate(order):
        level = levels.get(name)
        if not level:
            fail(f"campaign: missing level {name!r}")
            continue
        map_path = ROOT / "maps" / level.get("Map", "")
        if not map_path.is_file():
            fail(f"campaign {name}: missing map {level.get('Map')}")
        preview = ROOT / "art/textures/ui" / level.get("Preview", "")
        if not preview.is_file():
            fail(f"campaign {name}: missing preview {level.get('Preview')}")
        expected = None if index == 0 else order[index - 1]
        if level.get("Requires") != expected:
            fail(f"campaign {name}: Requires={level.get('Requires')!r}, expected {expected!r}")


def check_audio() -> None:
    for path in (ROOT / "audio/voice/quechua/civ").glob("*.xml"):
        try:
            root = ET.parse(path).getroot()
        except Exception:
            continue
        base = ROOT / (root.findtext("Path") or "")
        for sound in root.findall("Sound"):
            if sound.text and not (base / sound.text).is_file():
                fail(f"{path.relative_to(ROOT)}: missing {sound.text}")


def main() -> int:
    data = check_mod_json()
    xml_count = check_xml()
    json_count = check_json()
    check_js()
    check_campaign()
    check_audio()
    if warnings:
        for message in warnings:
            print(f"WARNING: {message}")
    if errors:
        for message in errors:
            print(f"ERROR: {message}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print(f"OK: {data.get('name')} {data.get('version')} | {xml_count} XML | {json_count} JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
