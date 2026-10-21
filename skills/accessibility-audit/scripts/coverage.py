#!/usr/bin/env python3
"""Create or validate a WCAG 2.2 criterion-by-state evidence ledger. No network calls."""

import argparse
import collections
import csv
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

SLICE_FIELDS = ["location", "state", "criterion", "status", "evidence", "environment", "notes"]
FIELDS = ["location", "state", "criterion", "level", "name", "required", "status", "evidence", "environment", "notes"]
STATUSES = {"not-tested", "pass", "fail", "not-applicable", "blocked", "needs-review"}
FINISHED = {"pass", "fail", "not-applicable"}
RESOLVED = {"pass", "not-applicable"}
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


def read_ledger(path, expected):
    rows = []
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
            if row["status"] not in STATUSES:
                raise ValueError("Unknown ledger status.")
            if row["status"] in FINISHED and not row["evidence"].strip():
                raise ValueError("Pass/fail needs evidence; not-applicable needs a reason.")
            seen.add(key)
            rows.append(row)
    if seen != set(expected):
        raise ValueError("Ledger is missing criterion/state rows from the supplied scope.")
    return rows


def summarize(rows):
    counts = {"yes": collections.Counter(), "no": collections.Counter()}
    for row in rows:
        counts[row["required"]][row["status"]] += 1
    for required, label in (("yes", "Target criteria"), ("no", "Supplemental criteria")):
        print(label + ": " + ", ".join(f"{status}={counts[required][status]}" for status in sorted(STATUSES)))
    unresolved = sum(value for key, value in counts["yes"].items() if key not in RESOLVED)
    print("WCAG 2.2 ledger validation only; site inventory, test execution, and conformance are not independently verified.")
    return 1 if unresolved else 0


def report(path, rows, target):
    """Write a Markdown coverage rollup. It names criteria, never locations or evidence."""
    order = ["fail", "blocked", "needs-review", "not-tested", "pass", "not-applicable"]
    by_criterion = collections.OrderedDict()
    for row in rows:
        entry = by_criterion.setdefault(row["criterion"], [row["level"], row["name"], row["required"], collections.Counter()])
        entry[3][row["status"]] += 1
    states = len({(row["location"], row["state"]) for row in rows})
    lines = [
        "# WCAG 2.2 coverage summary",
        "",
        f"Target: Level {target}. Location/state pairs: {states}. Rows: {len(rows)}.",
        "",
        "| Group | " + " | ".join(order) + " |",
        "|---|" + "---|" * len(order),
    ]
    for required, label in (("yes", f"Target (A–{target})" if target != "A" else "Target (A)"), ("no", "Supplemental")):
        totals = collections.Counter()
        for level, name, req, counter in by_criterion.values():
            if req == required:
                totals.update(counter)
        if sum(totals.values()):
            lines.append(f"| {label} | " + " | ".join(str(totals[s]) for s in order) + " |")
    for required, heading in (("yes", "Target criteria needing action"), ("no", "Supplemental criteria needing action")):
        open_rows = [(number, entry) for number, entry in by_criterion.items()
                     if entry[2] == required and any(entry[3][s] for s in order[:4])]
        lines += ["", f"## {heading}", ""]
        if not open_rows:
            lines.append("None. Every row is pass or not-applicable with recorded evidence.")
            continue
        lines += ["| Criterion | Level | Name | fail | blocked | needs-review | not-tested |", "|---|---|---|---|---|---|---|"]
        for number, (level, name, req, counter) in open_rows:
            lines.append(f"| {number} | {level} | {name} | " + " | ".join(str(counter[s]) for s in order[:4]) + " |")
    lines += ["", "This summary validates ledger completeness only. It does not verify that evidence is truthful, "
              "that the inventory covers the whole product, or that the product conforms.", ""]
    with path.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
    print(f"Wrote coverage summary for {len(by_criterion)} criteria.")


def merge(path, rows, inputs):
    """Fill ledger rows from subagent slice files. Refuses conflicts and writes atomically."""
    index = {tuple(row[f] for f in FIELDS[:3]): row for row in rows}
    incoming = {}
    for source in inputs:
        with source.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != SLICE_FIELDS:
                raise ValueError("Slice columns must be: " + ",".join(SLICE_FIELDS))
            for item in reader:
                if None in item or any(value is None for value in item.values()):
                    raise ValueError("Malformed slice row.")
                key = tuple(item[f] for f in SLICE_FIELDS[:3])
                if key not in index:
                    raise ValueError("A slice row is outside the scope or names an unknown criterion.")
                if key in incoming:
                    raise ValueError("The same criterion/state appears more than once across slices.")
                if item["status"] not in STATUSES:
                    raise ValueError("Unknown slice status.")
                if item["status"] in FINISHED and not item["evidence"].strip():
                    raise ValueError("Pass/fail needs evidence; not-applicable needs a reason.")
                for field in SLICE_FIELDS[4:]:
                    # Neutralize spreadsheet formulas in free text written by other agents.
                    if item[field].lstrip(" ").startswith(("=", "+", "-", "@", "\t", "\r")):
                        item[field] = "'" + item[field]
                incoming[key] = item
    conflicts = 0
    for key, item in incoming.items():
        current = index[key]
        if current["status"] != "not-tested" and any(current[f] != item[f] for f in SLICE_FIELDS[3:]):
            conflicts += 1
    if conflicts:
        raise ValueError(f"{conflicts} slice rows conflict with rows already recorded; resolve them in the ledger first.")
    for key, item in incoming.items():
        index[key].update({f: item[f] for f in SLICE_FIELDS[3:]})
    if path.is_symlink():
        raise ValueError("The ledger must be a regular file, not a symlink.")
    stream = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False)
    temporary = Path(stream.name)
    try:
        with stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        shutil.copymode(path, temporary)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Merged {len(incoming)} rows from {len(inputs)} slice file(s).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--target", choices=LEVELS, default="AA")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--summary", type=Path)
    action.add_argument("--merge", type=Path, help="Ledger to fill from --input slice files (location,state,criterion,status,evidence,environment,notes)")
    parser.add_argument("--input", type=Path, nargs="+", help="With --merge, one or more subagent slice CSV files")
    parser.add_argument("--report", type=Path, help="With --summary, also write a Markdown rollup (refuses to overwrite)")
    args = parser.parse_args()
    if args.report and not args.summary:
        parser.error("--report requires --summary")
    if bool(args.merge) != bool(args.input):
        parser.error("--merge and --input are used together")
    try:
        expected = expected_rows(scope_pairs(args.scope), args.target)
        if args.output:
            create(args.output, expected)
            return 0
        if args.merge:
            merge(args.merge, read_ledger(args.merge, expected), args.input)
            return 0
        rows = read_ledger(args.summary, expected)
        if args.report:
            report(args.report, rows, args.target)
        return summarize(rows)
    except (OSError, ValueError, csv.Error) as error:
        # Do not echo paths or input content that may contain private URLs.
        message = str(error) if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError) else "Could not read/write valid input; check paths, JSON/CSV, permissions, and existing output."
        print("Coverage error: " + message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
