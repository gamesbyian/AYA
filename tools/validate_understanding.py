#!/usr/bin/env python3
"""Offline AYA-AUF concept-model/consultation consistency checks.

This confirms declared structure and provenance, not the authenticity of a
director's reply or the factual truth of code/test citations.
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

TRUTH = {"intention", "implemented", "observed", "expectation"}
DECISION_STATES = {"confirmed", "provisional", "delegated", "deferred", "superseded"}
AMBIGUITY_STATES = {"unresolved", "answered", "delegated", "deferred"}
ID_PATTERNS = {
    "concepts": r"CONCEPT-\d{3,}",
    "goals": r"GOAL-\d{3,}",
    "principles": r"PRINCIPLE-\d{3,}",
    "claims": r"CLAIM-\d{3,}",
    "ambiguities": r"AMB-\d{3,}",
    "decisions": r"DEC-\d{3,}",
}


class UnderstandingError(ValueError):
    pass


def required(item, keys, label):
    if not isinstance(item, dict):
        raise UnderstandingError(f"{label} must be an object")
    for key in keys:
        if not isinstance(item.get(key), str) or not item[key].strip():
            raise UnderstandingError(f"{label}: missing {key}")


def check_ids(items, kind):
    if not isinstance(items, list):
        raise UnderstandingError(f"{kind} must be an array")
    result = {}
    for item in items:
        required(item, ["id"], kind)
        identifier = item["id"]
        if not re.fullmatch(ID_PATTERNS[kind], identifier) or identifier in result:
            raise UnderstandingError(f"{kind}: invalid/duplicate ID {identifier}")
        result[identifier] = item
    return result


def validate(model, record):
    if model.get("schema_version") != "aya-understanding/v1":
        raise UnderstandingError("Unsupported concept model version")
    host = model.get("host")
    required(host, ["app_id", "app_version", "source_revision"], "host")
    thesis = model.get("thesis")
    required(thesis, ["statement", "source_ref", "truth_kind", "status"], "thesis")
    if thesis["truth_kind"] not in TRUTH or thesis["status"] not in {"confirmed", "provisional", "unknown"}:
        raise UnderstandingError("Invalid thesis status/kind")
    if record.get("schema_version") != "aya-director-decisions/v1":
        raise UnderstandingError("Unsupported decision ledger version")
    if (record.get("app_id"), record.get("source_revision")) != (host["app_id"], host["source_revision"]):
        raise UnderstandingError("Model and decision ledger identity mismatch")
    groups = {name: check_ids(model.get(name), name) for name in
              ("concepts", "goals", "principles", "claims", "ambiguities")}
    decisions = check_ids(record.get("decisions"), "decisions")
    all_ids = set().union(*(set(group) for group in groups.values()))
    for concept in groups["concepts"].values():
        required(concept, ["name", "definition", "evidence_ref"], concept["id"])
        for link in concept.get("related_concept_ids", []):
            if link not in groups["concepts"]:
                raise UnderstandingError(f"Unknown related concept {link}")
    for goal in groups["goals"].values():
        required(goal, ["intention", "evidence_ref", "success_evidence"], goal["id"])
        if not goal.get("concept_ids") or any(x not in groups["concepts"] for x in goal["concept_ids"]):
            raise UnderstandingError(f"Unknown/missing concepts for {goal['id']}")
    for principle in groups["principles"].values():
        required(principle, ["statement", "scope", "source_ref", "truth_kind"], principle["id"])
        if principle["truth_kind"] not in TRUTH:
            raise UnderstandingError("Invalid principle truth kind")
    for claim in groups["claims"].values():
        required(claim, ["statement", "truth_kind", "status", "applies_to", "source_ref"], claim["id"])
        if claim["truth_kind"] not in TRUTH:
            raise UnderstandingError("Invalid claim truth kind")
        for field, target in (("concept_ids", "concepts"), ("goal_ids", "goals")):
            for link in claim.get(field, []):
                if link not in groups[target]:
                    raise UnderstandingError(f"Unknown {field} link: {link}")
        if claim["truth_kind"] == "intention" and claim["status"] == "AVAILABLE":
            raise UnderstandingError(f"Intent alone cannot prove availability: {claim['id']}")
    for amb in groups["ambiguities"].values():
        required(amb, ["question", "impact", "status", "source_ref"], amb["id"])
        if amb["status"] not in AMBIGUITY_STATES:
            raise UnderstandingError("Invalid ambiguity status")
        if type(amb.get("consultation_needed")) is not bool:
            raise UnderstandingError("Missing consultation flag")
        for link in amb.get("affected_ids", []):
            if link not in all_ids:
                raise UnderstandingError(f"Unknown affected ID {link}")
    for decision in decisions.values():
        required(decision, ["ambiguity_id", "status", "question", "observed_evidence",
                            "provisional_interpretation", "response", "actor",
                            "actor_role", "recorded_at_utc", "source_ref", "scope",
                            "review_trigger"], decision["id"])
        if decision["status"] not in DECISION_STATES:
            raise UnderstandingError("Invalid decision status")
        amb = groups["ambiguities"].get(decision["ambiguity_id"])
        if amb is None:
            raise UnderstandingError("Decision references unknown ambiguity")
        try:
            stamp = dt.datetime.fromisoformat(decision["recorded_at_utc"].replace("Z", "+00:00"))
            if stamp.utcoffset() != dt.timedelta(0):
                raise ValueError("not UTC")
        except ValueError as err:
            raise UnderstandingError("Decision date must be UTC") from err
        for link in decision.get("affected_ids", []):
            if link not in all_ids:
                raise UnderstandingError(f"Decision has unknown affected ID {link}")
        if decision["status"] == "deferred" and amb["status"] == "answered":
            raise UnderstandingError("Deferred decision cannot resolve an ambiguity")
        if decision["status"] in ("confirmed", "provisional", "delegated"):
            if decision["actor_role"] in ("unanswered", "unknown"):
                raise UnderstandingError("Cannot attribute affirmative decision to unknown actor")
    for name in ("principles", "claims"):
        for item in groups[name].values():
            for link in item.get("decision_ids", []):
                decision = decisions.get(link)
                if not decision:
                    raise UnderstandingError(f"Unknown decision reference: {link}")
                if decision["status"] in ("deferred", "superseded") and item.get("truth_kind") == "intention":
                    raise UnderstandingError("Unresolved/superseded decision cannot authorize intention")
    return {"ok": True, "concepts": len(groups["concepts"]), "goals": len(groups["goals"]),
            "principles": len(groups["principles"]), "claims": len(groups["claims"]),
            "ambiguities": len(groups["ambiguities"]), "decisions": len(decisions),
            "unresolved": sorted(x["id"] for x in groups["ambiguities"].values()
                                 if x["status"] in ("unresolved", "deferred"))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.model.read_text(encoding="utf-8")),
                          json.loads(args.decisions.read_text(encoding="utf-8")))
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, UnicodeError) as err:
        parser.exit(1, f"AYA understanding validation failed: {err}\n")


if __name__ == "__main__":
    main()
