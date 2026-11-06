#!/usr/bin/env python3
"""Offline validation for the portable AYA spatial-composition/v1 manifest.

Structural checks are intentionally dependency-free. This DOES NOT read assets;
a production host must separately verify file contents, hashes, MIME, symlinks
and explicit user permission before any share.
"""
import argparse
import json
import math
from pathlib import Path
import re
import sys

IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
FILE = re.compile(r"^(source|references|overlays)/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_.-]+)*\.(jpg|jpeg|png|webp)$")
SHA = re.compile(r"^[a-f0-9]{64}$")
MIMES = {"image/jpeg": {".jpg", ".jpeg"}, "image/png": {".png"}, "image/webp": {".webp"}}
KINDS = {"replace", "add", "remove", "clean", "modify"}
ANGLES = {"front", "rear", "left", "right", "three-quarter", "detail", "other"}


def validate(packet):
    errors = []

    def fail(message):
        errors.append(message)

    def fields(obj, required, allowed, where):
        if not isinstance(obj, dict):
            fail(f"{where}: expected object")
            return False
        for key in required - obj.keys():
            fail(f"{where}: missing {key}")
        for key in obj.keys() - allowed:
            fail(f"{where}: unknown {key}")
        return True

    def ident(value, where):
        if not isinstance(value, str) or not IDENT.fullmatch(value):
            fail(f"{where}: invalid identifier")

    def bounded_string(value, where, maximum, nonempty=True):
        if not isinstance(value, str) or len(value) > maximum or (nonempty and not value.strip()):
            fail(f"{where}: invalid text")

    def coordinate(x, where):
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or not 0 <= x <= 1:
            fail(f"{where}: coordinate outside [0,1]")
            return False
        return True

    paths = set()
    total = 0
    def picture(pic, where, prefix):
        nonlocal total
        if not fields(pic, {"path", "mime", "sha256", "bytes", "width", "height"},
                  {"path", "mime", "sha256", "bytes", "width", "height"}, where):
            return
        path, mime = pic.get("path"), pic.get("mime")
        if not isinstance(path, str) or not FILE.fullmatch(path) or not path.startswith(prefix + "/"):
            fail(f"{where}: unsafe/incorrect relative path")
        else:
            if path in paths:
                fail(f"{where}: duplicate attachment path")
            paths.add(path)
            if mime not in MIMES or Path(path).suffix.lower() not in MIMES[mime]:
                fail(f"{where}: MIME and extension mismatch")
        digest = pic.get("sha256")
        if not isinstance(digest, str) or not SHA.fullmatch(digest):
            fail(f"{where}: invalid sha256")
        for k, low, high in (("bytes", 1, 20 * 1024 * 1024), ("width", 1, 32768), ("height", 1, 32768)):
            v = pic.get(k)
            if type(v) is not int or not low <= v <= high:
                fail(f"{where}: invalid {k}")
            elif k == "bytes":
                total += v

    if not fields(packet, {"format", "source", "annotations", "assets", "operations", "constraints", "instructions"},
                  {"format", "source", "overlay", "annotations", "assets", "operations", "constraints", "instructions"}, "manifest"):
        return errors
    if packet.get("format") != "aya-spatial-composition/v1":
        fail("manifest: unsupported format version")
    picture(packet.get("source"), "source", "source")
    if "overlay" in packet:
        picture(packet["overlay"], "overlay", "overlays")
        src, overlay = packet.get("source"), packet["overlay"]
        if isinstance(src, dict) and isinstance(overlay, dict):
            if (src.get("width"), src.get("height")) != (overlay.get("width"), overlay.get("height")):
                fail("overlay: dimensions must match source")

    ids, labels, assets, targeted = set(), set(), set(), set()
    annotations = packet.get("annotations")
    if not isinstance(annotations, list) or not 1 <= len(annotations) <= 200:
        fail("annotations: expected 1..200 items")
        annotations = []
    for i, a in enumerate(annotations):
        at = f"annotations[{i}]"
        if not fields(a, {"id", "label", "geometry"}, {"id", "label", "geometry"}, at):
            continue
        ident(a.get("id"), at + ".id")
        if isinstance(a.get("id"), str):
            if a["id"] in ids: fail(at + ": duplicate id")
            ids.add(a["id"])
        bounded_string(a.get("label"), at + ".label", 80)
        if isinstance(a.get("label"), str):
            label = a["label"].strip().casefold()
            if label in labels: fail(at + ": duplicate label")
            labels.add(label)
        g = a.get("geometry")
        if not isinstance(g, dict):
            fail(at + ": invalid geometry")
            continue
        kind = g.get("kind")
        fields(g, {"kind", {"point":"point","polygon":"vertices","rect":"x"}.get(kind,"kind")} if kind != "rect" else {"kind","x","y","width","height"},
               {"kind","point"} if kind == "point" else {"kind","vertices"} if kind == "polygon" else {"kind","x","y","width","height"}, at + ".geometry")
        if kind == "point":
            pt = g.get("point")
            if fields(pt, {"x","y"}, {"x","y"}, at + ".point"):
                coordinate(pt.get("x"), at + ".x")
                coordinate(pt.get("y"), at + ".y")
        elif kind == "polygon":
            vv = g.get("vertices")
            if not isinstance(vv, list) or not 3 <= len(vv) <= 500:
                fail(at + ": polygon needs 3..500 vertices")
            else:
                coords = []
                for j, p in enumerate(vv):
                    if fields(p, {"x","y"}, {"x","y"}, at + f".vertices[{j}]"):
                        if coordinate(p.get("x"), at + ".x") and coordinate(p.get("y"), at + ".y"):
                            coords.append((p["x"], p["y"]))
                if len(coords) == len(vv):
                    area = sum(coords[j][0]*coords[(j+1)%len(coords)][1] - coords[(j+1)%len(coords)][0]*coords[j][1] for j in range(len(coords)))
                    if abs(area) < 1e-8: fail(at + ": degenerate polygon")
        elif kind == "rect":
            if all(coordinate(g.get(k), at + "." + k) for k in ("x","y","width","height")):
                if g["width"] <= 0 or g["height"] <= 0 or g["x"] + g["width"] > 1 or g["y"] + g["height"] > 1:
                    fail(at + ": invalid or out-of-frame rect")
        else:
            fail(at + ": unknown geometry kind")

    catalog = packet.get("assets")
    if not isinstance(catalog, list) or len(catalog) > 100:
        fail("assets: expected 0..100 items")
        catalog = []
    for i, a in enumerate(catalog):
        at = f"assets[{i}]"
        if not fields(a, {"id","name","category","views"}, {"id","name","category","views","dimensionsMm"}, at):
            continue
        ident(a.get("id"), at + ".id")
        if isinstance(a.get("id"), str):
            if a["id"] in assets: fail(at + ": duplicate asset id")
            assets.add(a["id"])
        bounded_string(a.get("name"), at + ".name", 200)
        bounded_string(a.get("category"), at + ".category", 120)
        dimensions = a.get("dimensionsMm")
        if dimensions is not None and fields(dimensions, {"width","height","depth"}, {"width","height","depth"}, at + ".dimensionsMm"):
            for k, v in dimensions.items():
                if isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) or v <= 0:
                    fail(at + ": nonpositive dimension " + k)
        views = a.get("views")
        if not isinstance(views, list) or not 1 <= len(views) <= 12:
            fail(at + ": expected 1..12 reference views")
            continue
        for j, view in enumerate(views):
            where = f"{at}.views[{j}]"
            if fields(view, {"angle","image"}, {"angle","image"}, where):
                if view.get("angle") not in ANGLES: fail(where + ": invalid view angle")
                picture(view.get("image"), where + ".image", "references")

    ops = packet.get("operations")
    if not isinstance(ops, list) or not 1 <= len(ops) <= 200:
        fail("operations: expected 1..200 items")
        ops = []
    protected = set()
    cons = packet.get("constraints")
    if fields(cons, {"preserveUnmarked","engineeringVerified"}, {"preserveUnmarked","engineeringVerified","protectedAnnotationIds"}, "constraints"):
        if cons.get("preserveUnmarked") is not True: fail("constraints: preserveUnmarked must be true")
        if cons.get("engineeringVerified") is not False: fail("constraints: engineeringVerified must be false")
        p = cons.get("protectedAnnotationIds", [])
        if not isinstance(p, list) or any(not isinstance(v,str) for v in p) or len(p) != len(set(p)):
            fail("constraints: invalid protectedAnnotationIds")
        else:
            protected = set(p)
            if not protected <= ids: fail("constraints: unknown protected annotation")
    for i, op in enumerate(ops):
        at = f"operations[{i}]"
        if not fields(op, {"targetAnnotationId","kind"}, {"targetAnnotationId","kind","assetId","detail"}, at):
            continue
        target, kind, asset = op.get("targetAnnotationId"), op.get("kind"), op.get("assetId")
        if target not in ids: fail(at + ": unresolved target")
        if target in protected: fail(at + ": protected target cannot be changed")
        if target in targeted: fail(at + ": conflicting duplicate target")
        targeted.add(target)
        if kind not in KINDS: fail(at + ": invalid operation")
        if kind in ("replace","add") and not asset: fail(at + ": missing required asset")
        if asset is not None and asset not in assets: fail(at + ": unknown asset")
        if "detail" in op: bounded_string(op["detail"], at + ".detail", 2000, False)
    bounded_string(packet.get("instructions"), "instructions", 12000)
    if len(paths) > 24: fail("attachments: exceeds recommended hard limit of 24")
    if total > 100 * 1024 * 1024: fail("attachments: exceeds 100 MiB")
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", type=Path)
    args = ap.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        errors = validate(data)
    except (OSError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print("INVALID:", error, file=sys.stderr)
        return 1
    print("VALID: structural manifest checks passed; file hashes and permissions NOT verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
