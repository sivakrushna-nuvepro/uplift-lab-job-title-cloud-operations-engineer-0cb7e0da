"""Run deterministic offline validation for an ALB operational record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "validation"
FIXTURES_DIR = VALIDATION_DIR / "fixtures"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_project.alb_validation import validate_operational_record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate an EC2/Application Load Balancer operational record "
            "against the frozen deployment, network, and incident cards."
        )
    )
    parser.add_argument(
        "--record",
        required=True,
        help="Repository-relative path to the operational record JSON file.",
    )
    parser.add_argument(
        "--report",
        help=(
            "Optional repository-relative output path for the JSON report. "
            "Defaults to a validation-report file beside the record."
        ),
    )
    return parser.parse_args()


def repository_path(value: str, label: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        raise ValueError(f"{label} must be a repository-relative path")

    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"{label} must remain inside the repository") from exc
    return resolved


def default_report_path(record_path: Path) -> Path:
    return record_path.with_name(f"{record_path.stem}.validation-report.json")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def failure_report(message: str) -> dict[str, Any]:
    return {
        "passed": False,
        "errors": ["VALIDATION_RUNNER_ERROR"],
        "runner_error": message,
        "components": {},
        "critical_gates": [],
    }


def main() -> int:
    args = parse_args()

    try:
        record_path = repository_path(args.record, "--record")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.report:
        try:
            report_path = repository_path(args.report, "--report")
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    else:
        report_path = default_report_path(record_path)

    try:
        record = read_json(record_path)
        deployment_brief = read_json(FIXTURES_DIR / "deployment_brief.json")
        network_card = read_json(FIXTURES_DIR / "network_card.json")
        incident_card = read_json(FIXTURES_DIR / "health_incident_card.json")
        report = validate_operational_record(
            record=record,
            deployment_brief=deployment_brief,
            network_card=network_card,
            incident_card=incident_card,
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
        report = failure_report(f"{type(exc).__name__}: {exc}")

    try:
        write_report(report_path, report)
    except OSError as exc:
        print(f"Unable to write validation report: {exc}", file=sys.stderr)
        return 1

    print(str(report_path.relative_to(ROOT)))
    return 0 if report.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())