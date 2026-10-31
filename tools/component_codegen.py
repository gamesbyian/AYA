#!/usr/bin/env python3
"""Validate AYA component/v1 configuration and emit a Kotlin Android snippet.

This is build-time configuration, NEVER a runtime parser, user-data reader or
share transport. Static validity cannot prove that an APK contains the
exact-version guide: run the independent reference audit and Android tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import quoteattr
from typing import Any

ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{1,79}$")
ASSET = re.compile(r"^(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.md$")
ROOT_KEYS = {"component", "id", "operation", "guideAsset", "screenName", "presentation"}
CARD_KEYS = {"kind", "title", "description", "attachmentDisclosure", "outputInstructions", "density"}
ACTION_KEYS = {"kind", "askQuestion"}
CARD_LIMITS = {"title": 100, "description": 500, "attachmentDisclosure": 500, "outputInstructions": 600}


class ComponentError(ValueError):
    pass


def _keys(value: Any, allowed: set[str], required: set[str], where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ComponentError(f"{where} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - allowed
    if missing:
        raise ComponentError(f"{where} missing: {', '.join(sorted(missing))}")
    if unknown:
        raise ComponentError(f"{where} unsupported fields: {', '.join(sorted(unknown))}")
    return value


def _string(value: Any, name: str, length: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > length or "\x00" in value:
        raise ComponentError(f"{name} must be nonblank UTF-8 text (maximum {length} characters)")
    return value


def validate(manifest: Any) -> dict[str, Any]:
    m = _keys(manifest, ROOT_KEYS,
              {"component", "id", "operation", "guideAsset", "presentation"}, "component")
    if m["component"] != "aya-component/v1":
        raise ComponentError("Unsupported component schema version")
    if not isinstance(m["id"], str) or not ID.fullmatch(m["id"]):
        raise ComponentError("Invalid stable component ID")
    if m["operation"] != "help":
        raise ComponentError("Component manifest v1 only supports help; use typed Kotlin for other tasks")
    asset = _string(m["guideAsset"], "guideAsset", 160)
    if not ASSET.fullmatch(asset) or asset.startswith("/") or any(
        segment in ("", ".", "..") for segment in asset.split("/")
    ):
        raise ComponentError("guideAsset must be a relative Markdown APK asset path without traversal")
    if "screenName" in m:
        _string(m["screenName"], "screenName", 200)

    p = m["presentation"]
    if not isinstance(p, dict):
        raise ComponentError("presentation must be an object")
    kind = p.get("kind")
    if kind == "card":
        _keys(p, CARD_KEYS, CARD_KEYS, "presentation(card)")
        for field, maximum in CARD_LIMITS.items():
            _string(p[field], f"presentation.{field}", maximum)
        if p["density"] not in ("standard", "compact"):
            raise ComponentError("presentation.density must be standard or compact")
    elif kind == "action":
        _keys(p, ACTION_KEYS, ACTION_KEYS, "presentation(action)")
        if type(p["askQuestion"]) is not bool:
            raise ComponentError("presentation.askQuestion must be a boolean")
    else:
        raise ComponentError("presentation.kind must be card or action")
    return m


def kotlin_quote(value: str) -> str:
    """Produce a safe Kotlin string literal, including escaping interpolation."""
    escapes = {'\\': '\\\\', '"': '\\"', '$': '\\$', '\n': '\\n', '\r': '\\r', '\t': '\\t'}
    body = ''.join(escapes.get(ch, f"\\u{ord(ch):04x}" if ord(ch) < 32 else ch) for ch in value)
    return '"' + body + '"'


def kotlin_function_name(prefix: str, component_id: str) -> str:
    """Stable and collision-resistant across independent component manifests."""
    normalized = re.sub(r"[^A-Za-z0-9_]", "_", component_id)
    suffix = hashlib.sha256(component_id.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}AyaComponent_{normalized}_{suffix}"


def kotlin_snippet(m: dict[str, Any]) -> str:
    m = validate(m)
    p = m["presentation"]
    card_function = kotlin_function_name("install", m["id"])
    action_function = kotlin_function_name("launch", m["id"])
    screen = f",\n        screenName = {kotlin_quote(m['screenName'])}" if "screenName" in m else ""
    if p["kind"] == "card":
        return (
            "// AYA component: " + m["id"] + "\n"
            "import android.app.Activity\n"
            "import android.view.ViewGroup\n"
            "import dev.aya.android.AyaCardDensity\n"
            "import dev.aya.android.AyaCardView\n\n"
            "fun " + card_function + "(activity: Activity, container: ViewGroup): AyaCardView {\n"
            "    val card = AyaCardView(\n"
            "        context = activity,\n"
            "        activity = activity,\n"
            "        guideAsset = " + kotlin_quote(m["guideAsset"]) + screen + ",\n"
            "        title = " + kotlin_quote(p["title"]) + ",\n"
            "        description = " + kotlin_quote(p["description"]) + ",\n"
            "        attachmentDisclosure = " + kotlin_quote(p["attachmentDisclosure"]) + ",\n"
            "        outputInstructions = " + kotlin_quote(p["outputInstructions"]) + ",\n"
            "        densityMode = AyaCardDensity." + p["density"].upper() + "\n"
            "    )\n"
            "    container.addView(card)\n"
            "    return card\n"
            "}\n"
        )
    return (
        "// AYA component: " + m["id"] + "\n"
        "import android.app.Activity\n"
        "import dev.aya.android.AyaBundledLaunchResult\n"
        "import dev.aya.android.AyaComponentAction\n\n"
        "fun " + action_function + "(activity: Activity, question: String?): AyaBundledLaunchResult {\n"
        "    return AyaComponentAction.Help(\n"
        "        guideAsset = " + kotlin_quote(m["guideAsset"]) + screen + ",\n"
        "        askQuestion = " + str(p["askQuestion"]).lower() + "\n"
        "    ).launch(activity, text = question)\n"
        "}\n"
    )


def compose_snippet(m: dict[str, Any]) -> str:
    """Emit a source-only Compose wrapper without changing SDK handoff semantics."""
    m = validate(m)
    p = m["presentation"]
    function = kotlin_function_name("compose", m["id"])
    screen = f",\n        screenName = {kotlin_quote(m['screenName'])}" if "screenName" in m else ""
    if p["kind"] == "card":
        return (
            "// AYA Compose component: " + m["id"] + "\n"
            "import android.app.Activity\n"
            "import androidx.compose.runtime.Composable\n"
            "import androidx.compose.ui.Modifier\n"
            "import dev.aya.android.AyaCardDensity\n"
            "import dev.aya.compose.AyaCard\n\n"
            "@Composable\n"
            "fun " + function + "(activity: Activity, modifier: Modifier = Modifier) {\n"
            "    AyaCard(\n"
            "        activity = activity,\n"
            "        modifier = modifier,\n"
            "        guideAsset = " + kotlin_quote(m["guideAsset"]) + screen + ",\n"
            "        title = " + kotlin_quote(p["title"]) + ",\n"
            "        description = " + kotlin_quote(p["description"]) + ",\n"
            "        attachmentDisclosure = " + kotlin_quote(p["attachmentDisclosure"]) + ",\n"
            "        outputInstructions = " + kotlin_quote(p["outputInstructions"]) + ",\n"
            "        densityMode = AyaCardDensity." + p["density"].upper() + "\n"
            "    )\n"
            "}\n"
        )
    return (
        "// AYA Compose component: " + m["id"] + "\n"
        "import android.app.Activity\n"
        "import androidx.compose.runtime.Composable\n"
        "import dev.aya.android.AyaComponentAction\n"
        "import dev.aya.compose.AyaLauncher\n"
        "import dev.aya.compose.rememberAyaLauncher\n\n"
        "@Composable\n"
        "fun " + function + "(activity: Activity, onRejected: ((String) -> Unit)? = null): AyaLauncher {\n"
        "    return rememberAyaLauncher(\n"
        "        activity = activity,\n"
        "        action = AyaComponentAction.Help(\n"
        "            guideAsset = " + kotlin_quote(m["guideAsset"]) + screen + ",\n"
        "            askQuestion = " + str(p["askQuestion"]).lower() + "\n"
        "        ),\n"
        "        onRejected = onRejected\n"
        "    )\n"
        "}\n"
    )


def android_xml_snippet(m: dict[str, Any]) -> str:
    """Generate an Android Studio layout element with stable, unique view IDs."""
    m = validate(m)
    p = m["presentation"]
    if p["kind"] != "card":
        raise ComponentError("android-xml output only supports visible cards; actions need a host button")

    def quote(value: str) -> str:
        # AAPT parses resource sigils and backslashes specially in raw XML
        # attributes. Refuse ambiguous expressions instead of silently
        # changing the developer's configured disclosure/instructions.
        if any(ch in value for ch in (chr(13), chr(10), chr(9), chr(92))):
            raise ComponentError("XML card copy must be single-line and omit backslashes; use resources otherwise")
        if value.startswith(("@", "?")):
            raise ComponentError("XML card copy may not start with a resource sigil")
        return quoteattr(value)

    suffix = hashlib.sha256(m["id"].encode("utf-8")).hexdigest()[:8]
    stem = re.sub(r"[^a-z0-9_]", "_", m["id"].lower())
    card_id = f"aya_card_{stem}_{suffix}"
    input_id = f"aya_question_{stem}_{suffix}"
    attributes = [
        'xmlns:android="http://schemas.android.com/apk/res/android"',
        'xmlns:app="http://schemas.android.com/apk/res-auto"',
        f'android:id="@+id/{card_id}"',
        'android:layout_width="match_parent"',
        'android:layout_height="wrap_content"',
        'app:ayaQuestionInputId="@+id/' + input_id + '"',
        'app:ayaGuideAsset=' + quote(m["guideAsset"]),
    ]
    if "screenName" in m:
        attributes.append('app:ayaScreenName=' + quote(m["screenName"]))
    for key, attr in (
        ("title", "ayaTitle"), ("description", "ayaDescription"),
        ("attachmentDisclosure", "ayaAttachmentDisclosure"),
        ("outputInstructions", "ayaOutputInstructions")
    ):
        attributes.append(f'app:{attr}=' + quote(p[key]))
    attributes.append('app:ayaDensity=' + quote(p["density"]))
    return "<dev.aya.android.AyaXmlCardView" + chr(10) + "    " + (chr(10) + "    ").join(attributes) + " />" + chr(10)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="static component JSON configuration")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="validate configuration without generating code")
    group.add_argument("--format", choices=("kotlin", "compose", "android-xml"), help="emit deterministic Android Kotlin source")
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.manifest.read_text(encoding="utf-8"))
        validate(config)
    except (OSError, UnicodeError, json.JSONDecodeError, ComponentError) as exc:
        print(f"AYA component invalid: {exc}", file=sys.stderr)
        return 2
    try:
        if args.format == "kotlin":
            print(kotlin_snippet(config), end="")
        elif args.format == "android-xml":
            print(android_xml_snippet(config), end="")
        elif args.format == "compose":
            print(compose_snippet(config), end="")
        else:
            print(f"Valid AYA component/v1: {config['id']} ({config['presentation']['kind']})")
    except ComponentError as exc:
        print(f"AYA component invalid: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
