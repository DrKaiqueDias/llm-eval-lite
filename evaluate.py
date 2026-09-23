"""Deterministic, offline checks for JSONL model responses."""
import argparse
import json
import sys
from pathlib import Path


def evaluate_case(case: dict) -> dict:
    """Evaluate one case. These checks do not measure truth or semantic quality."""
    if not isinstance(case, dict):
        raise ValueError("each case must be an object")
    if not isinstance(case.get("id"), str) or not case["id"].strip():
        raise ValueError("each case requires a non-empty string id")
    if not isinstance(case.get("response"), str):
        raise ValueError(f"{case['id']}: response must be a string")
    rules = case.get("rules")
    if not isinstance(rules, dict) or not rules:
        raise ValueError(f"{case['id']}: rules must be a non-empty object")
    allowed = {"contains", "excludes", "max_chars", "valid_json"}
    if set(rules) - allowed:
        raise ValueError(f"{case['id']}: unknown rules: {sorted(set(rules) - allowed)}")
    response = case["response"]
    checks = {}
    for rule in ("contains", "excludes"):
        if rule in rules:
            terms = rules[rule]
            if not isinstance(terms, list) or not terms or any(
                not isinstance(t, str) or not t.strip() for t in terms
            ):
                raise ValueError(f"{rule} must be a non-empty list of non-empty strings")
            present = [term.casefold() in response.casefold() for term in terms]
            checks[rule] = all(present) if rule == "contains" else not any(present)
    if "max_chars" in rules:
        limit = rules["max_chars"]
        if type(limit) is not int or limit < 0:
            raise ValueError("max_chars must be a non-negative integer")
        checks["max_chars"] = len(response) <= limit
    if "valid_json" in rules:
        if rules["valid_json"] is not True:
            raise ValueError("valid_json must be true when supplied")
        try:
            json.loads(response, parse_constant=reject_constant)
            checks["valid_json"] = True
        except (ValueError, json.JSONDecodeError):
            checks["valid_json"] = False
    return {"id": case["id"], "passed": all(checks.values()), "checks": checks}


def reject_constant(value: str):
    raise ValueError(f"non-standard JSON constant: {value}")


def evaluate_file(path: Path) -> dict:
    results, ids = [], set()
    with path.open(encoding="utf-8-sig") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                case = json.loads(line, parse_constant=reject_constant)
                result = evaluate_case(case)
                if result["id"] in ids:
                    raise ValueError("duplicate case id")
                ids.add(result["id"])
                results.append(result)
            except (ValueError, TypeError) as error:
                raise ValueError(f"line {line_no}: {error}") from error
    if not results:
        raise ValueError("input contains no cases")
    passed = sum(item["passed"] for item in results)
    return {"total": len(results), "passed": passed,
            "pass_rate": passed / len(results), "cases": results}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSONL test cases")
    args = parser.parse_args(argv)
    try:
        report = evaluate_file(args.input)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
