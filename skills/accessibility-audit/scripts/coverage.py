#!/usr/bin/env python3
"""Create or validate a WCAG 2.2 criterion-by-state evidence ledger. No network calls."""

import argparse
import collections
import csv
import json
from pathlib import Path
import re
import sys

FIELDS = ["location", "state", "criterion", "level", "name", "required", "status", "evidence", "environment", "notes"]
STATUSES = {"not-tested", "pass", "fail", "not-applicable", "blocked", "needs-review"}
FINISHED = {"pass", "fail", "not-applicable"}
LEVELS = {"A": 1, "AA": 2, "AAA": 3}


def criteria():
    source = Path(__file__).resolve().parent.parent / "references" / "wcag-22-matrix.md"
    rows = []
    for line in source.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.fullmatch(r"\d+\.\d+\.\d+", cells[0]):
            rows.append(tuple(cells[:3]))
    counts = collections.Counter(row[1] for row in rows)
    if counts != {"A": 31, "AA": 24, "AAA": 31} or len({r[0] for r in rows}) != 86:
        raise ValueError("The bundled WCAG matrix is incomplete or invalid.")
    return rows


def scope_pairs(path):
    scope = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(scope, list) or not scope:
        raise ValueError("Scope must be a nonempty list of location/states objects.")
    pairs = []
    for item in scope:
        if not isinstance(item, dict) or set(item) != {"location", "states"}:
            raise ValueError("Each scope entry must contain only location and states.")
        location, states = item["location"], item["states"]
        if not isinstance(location, str) or not location.strip() or not isinstance(states, list) or not states:
            raise ValueError("Each location needs a nonempty string and a nonempty states list.")
        for state in states:
            if not isinstance(state, str) or not state.strip():
                raise ValueError("States must be nonempty strings.")
            # CSV output may be opened by a spreadsheet; reject formula/control prefixes.
            if any(v.lstrip().startswith(("=", "+", "-", "@")) or any(ord(c) < 32 for c in v) for v in (location, state)):
                raise ValueError("Location/state must not contain control characters or spreadsheet formula prefixes.")
            pairs.append((location, state))
    if len(set(pairs)) != len(pairs):
        raise ValueError("Duplicate location/state pair in scope.")
    return pairs


def expected_rows(scope, target):
    return {(location, state, number): (level, name, "yes" if LEVELS[level] <= LEVELS[target] else "no")
            for location, state in scope for number, level, name in criteria()}


def create(path, expected):
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(FIELDS)
        for key, metadata in expected.items():
            writer.writerow([*key, *metadata, "not-tested", "", "", ""])
    print(f"Created {len(expected)} untested WCAG 2.2 criterion/state rows.")


def summarize(path, expected):
    counts = {"yes": collections.Counter(), "no": collections.Counter()}
    seen = set()
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError("Ledger columns do not match the generated format.")
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Malformed ledger row.")
            key = tuple(row[field] for field in FIELDS[:3])
            if key not in expected or key in seen:
                raise ValueError("Unexpected or duplicate criterion/state row.")
            if tuple(row[field] for field in FIELDS[3:6]) != expected[key]:
                raise ValueError("Criterion metadata or target differs from the scope/matrix.")
            status = row["status"]
            if status not in STATUSES:
                raise ValueError("Unknown ledger status.")
            if status in FINISHED and not row["evidence"].strip():
                raise ValueError("Pass/fail needs evidence; not-applicable needs a reason.")
            seen.add(key)
            counts[row["required"]][status] += 1
    if seen != set(expected):
        raise ValueError("Ledger is missing criterion/state rows from the supplied scope.")
    for required, label in (("yes", "Target criteria"), ("no", "Supplemental criteria")):
        print(label + ": " + ", ".join(f"{status}={counts[required][status]}" for status in sorted(STATUSES)))
    unresolved = sum(value for key, value in counts["yes"].items() if key not in {"pass", "not-applicable"})
    print("WCAG 2.2 ledger validation only; site inventory, test execution, and conformance are not independently verified.")
    return 1 if unresolved else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--target", choices=LEVELS, default="AA")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--summary", type=Path)
    args = parser.parse_args()
    try:
        expected = expected_rows(scope_pairs(args.scope), args.target)
        if args.output:
            create(args.output, expected)
            return 0
        return summarize(args.summary, expected)
    except (OSError, ValueError, csv.Error) as error:
        # Do not echo paths or input content that may contain private URLs.
        message = str(error) if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError) else "Could not read/write valid input; check paths, JSON/CSV, permissions, and existing output."
        print("Coverage error: " + message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
