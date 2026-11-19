"""Suggests tomorrow's quantity from the daily records in data.csv.

Usage:
    python suggest.py tuesday
    python suggest.py tuesday --buffer 0.15 --data data.csv
"""
import argparse
import csv
from statistics import mean

WEEKDAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


def load(path):
    """Read data.csv. Bad rows are skipped and reported, never silently used."""
    rows, skipped = [], 0
    with open(path, newline="") as f:
        for line_no, r in enumerate(csv.DictReader(f), start=2):
            try:
                made = float(r["quantity_made"])
                left = float(r["quantity_left"])
                weekday = r["weekday"].strip().lower()
                if weekday not in WEEKDAYS:
                    raise ValueError("bad weekday")
                if made < 0 or left < 0 or left > made:
                    raise ValueError("impossible numbers")
                rows.append({"date": r["date"], "weekday": weekday, "sold": made - left, "left": left})
            except (ValueError, KeyError, AttributeError, TypeError) as e:
                skipped += 1
                print(f"  SKIPPED row {line_no}: {e} -> {dict(r)}")
    return rows, skipped


def suggest(rows, weekday, buffer):
    same_day = [r["sold"] for r in rows if r["weekday"] == weekday]
    basis = "same weekday"
    used = same_day
    if len(same_day) < 2:  # too little data for this weekday, fall back to all days
        used = [r["sold"] for r in rows]
        basis = "all days (fewer than 2 records for this weekday)"
    if not used:
        raise SystemExit("No valid rows in data file.")
    return mean(used) * (1 + buffer), len(used), basis


def main():
    p = argparse.ArgumentParser()
    p.add_argument("weekday", help="weekday to plan for, e.g. tuesday")
    p.add_argument("--data", default="data.csv")
    p.add_argument("--buffer", type=float, default=0.10, help="extra fraction on top of average (default 0.10)")
    a = p.parse_args()

    rows, skipped = load(a.data)
    print(f"Valid rows: {len(rows)}, skipped: {skipped}")
    if len(rows) < 20:
        print("WARNING: fewer than 20 valid rows. Treat the suggestion as weak.")
    amount, n, basis = suggest(rows, a.weekday.lower(), a.buffer)
    print(f"Suggested quantity for {a.weekday}: {amount:.1f} (based on {n} records, {basis}, buffer {a.buffer:.0%})")


if __name__ == "__main__":
    main()
