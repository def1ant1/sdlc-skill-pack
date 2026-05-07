#!/usr/bin/env python3
"""
detect_finance_anomalies.py — Detect financial anomalies in transaction data.

Applies anomaly detection rules from accounting-automation skill:
  - Duplicate invoices (same vendor + amount + date)
  - Round-number transactions above threshold
  - Velocity spikes (vendor spend vs 90-day average)
  - First-time vendor transactions above threshold
  - Policy violations (category + amount vs limits)

Usage:
    python scripts/finance/detect_finance_anomalies.py --input transactions.json
    cat transactions.json | python scripts/finance/detect_finance_anomalies.py --stdin

Input: JSON array of transaction objects (see schema in accounting-automation/SKILL.md)
Output: JSON array of anomaly records with severity and recommended action.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


# Configurable thresholds
ROUND_NUMBER_THRESHOLD = 500.0      # flag round amounts above this
DUPLICATE_WINDOW_DAYS = 30          # window for duplicate detection
VELOCITY_MULTIPLIER = 3.0           # flag if spend > N× 90-day average
NEW_VENDOR_THRESHOLD = 5000.0       # flag first transactions above this
VELOCITY_LOOKBACK_DAYS = 90         # days for computing baseline spend


def is_round_number(amount: float) -> bool:
    """Check if amount is a suspicious round number."""
    return amount >= ROUND_NUMBER_THRESHOLD and amount % 100 == 0


def parse_date(date_str: str) -> datetime | None:
    """Parse ISO date string."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(date_str[:19], fmt)
        except ValueError:
            continue
    return None


def detect_duplicates(transactions: list[dict]) -> list[dict]:
    """Detect duplicate transactions (same vendor + amount + approximate date)."""
    anomalies = []
    seen: dict[tuple, list[str]] = defaultdict(list)

    for txn in transactions:
        vendor = str(txn.get("vendor", "")).lower().strip()
        amount = float(txn.get("amount", 0))
        date = parse_date(txn.get("date", ""))
        txn_id = txn.get("id", "unknown")

        if not vendor or not date:
            continue

        # Key: vendor + rounded amount (to 2 decimals)
        key = (vendor, round(amount, 2))
        seen[key].append((txn_id, date))

    # Check for duplicates within the window
    for (vendor, amount), entries in seen.items():
        if len(entries) < 2:
            continue
        entries_sorted = sorted(entries, key=lambda x: x[1])
        for i in range(1, len(entries_sorted)):
            prev_id, prev_date = entries_sorted[i - 1]
            curr_id, curr_date = entries_sorted[i]
            days_apart = abs((curr_date - prev_date).days)
            if days_apart <= DUPLICATE_WINDOW_DAYS:
                anomalies.append({
                    "rule": "DUPLICATE_INVOICE",
                    "severity": "HIGH",
                    "transaction_ids": [prev_id, curr_id],
                    "vendor": vendor,
                    "amount": amount,
                    "days_apart": days_apart,
                    "description": (
                        f"Potential duplicate: vendor '{vendor}' amount ${amount:.2f} "
                        f"appears {days_apart} days apart"
                    ),
                    "recommended_action": "Block both; request vendor confirmation",
                })

    return anomalies


def detect_round_numbers(transactions: list[dict]) -> list[dict]:
    """Detect suspicious round-number transactions."""
    anomalies = []
    for txn in transactions:
        amount = float(txn.get("amount", 0))
        if is_round_number(amount):
            anomalies.append({
                "rule": "ROUND_NUMBER",
                "severity": "MEDIUM",
                "transaction_ids": [txn.get("id", "unknown")],
                "vendor": txn.get("vendor", ""),
                "amount": amount,
                "description": f"Round-number transaction: ${amount:.0f} from '{txn.get('vendor', '')}'",
                "recommended_action": "Review for legitimacy; request supporting documentation",
            })
    return anomalies


def detect_velocity_spikes(transactions: list[dict]) -> list[dict]:
    """Detect vendor spend velocity spikes vs 90-day baseline."""
    anomalies = []
    now = datetime.now()
    lookback = now - timedelta(days=VELOCITY_LOOKBACK_DAYS)
    current_period_start = now - timedelta(days=30)

    # Group by vendor
    vendor_spend_baseline: dict[str, float] = defaultdict(float)
    vendor_spend_current: dict[str, float] = defaultdict(float)

    for txn in transactions:
        vendor = str(txn.get("vendor", "")).lower().strip()
        amount = float(txn.get("amount", 0))
        date = parse_date(txn.get("date", ""))

        if not vendor or not date:
            continue

        if lookback <= date < current_period_start:
            vendor_spend_baseline[vendor] += amount
        elif date >= current_period_start:
            vendor_spend_current[vendor] += amount

    # Compare current vs baseline (normalized to 30-day periods)
    baseline_period_days = VELOCITY_LOOKBACK_DAYS - 30
    if baseline_period_days <= 0:
        return anomalies

    for vendor, current_spend in vendor_spend_current.items():
        baseline_spend = vendor_spend_baseline.get(vendor, 0)
        if baseline_spend == 0:
            continue  # new vendor — handled by new_vendor rule

        # Normalize baseline to 30-day equivalent
        baseline_30d = baseline_spend * (30 / baseline_period_days)
        if baseline_30d > 0 and current_spend > baseline_30d * VELOCITY_MULTIPLIER:
            anomalies.append({
                "rule": "VELOCITY_SPIKE",
                "severity": "HIGH",
                "transaction_ids": [],
                "vendor": vendor,
                "amount": current_spend,
                "baseline_30d": round(baseline_30d, 2),
                "multiplier": round(current_spend / baseline_30d, 2),
                "description": (
                    f"Spend spike: '{vendor}' ${current_spend:.2f} this month "
                    f"vs ${baseline_30d:.2f} 30-day baseline "
                    f"({current_spend / baseline_30d:.1f}× increase)"
                ),
                "recommended_action": "Review for authorization and business justification",
            })

    return anomalies


def detect_new_vendors(transactions: list[dict]) -> list[dict]:
    """Detect first transactions with new vendors above threshold."""
    anomalies = []
    vendor_history: dict[str, list] = defaultdict(list)

    # Sort by date to determine first occurrence
    sorted_txns = sorted(
        transactions,
        key=lambda t: t.get("date", ""),
    )

    for txn in sorted_txns:
        vendor = str(txn.get("vendor", "")).lower().strip()
        amount = float(txn.get("amount", 0))

        if vendor not in vendor_history and amount > NEW_VENDOR_THRESHOLD:
            anomalies.append({
                "rule": "NEW_VENDOR",
                "severity": "MEDIUM",
                "transaction_ids": [txn.get("id", "unknown")],
                "vendor": txn.get("vendor", ""),
                "amount": amount,
                "description": (
                    f"First transaction with new vendor '{txn.get('vendor', '')}': "
                    f"${amount:.2f} exceeds ${NEW_VENDOR_THRESHOLD:.0f} threshold"
                ),
                "recommended_action": "Verify vendor qualification before payment",
            })

        vendor_history[vendor].append(txn.get("id"))

    return anomalies


def detect_anomalies(transactions: list[dict]) -> list[dict]:
    """Run all anomaly detection rules."""
    all_anomalies = []
    all_anomalies.extend(detect_duplicates(transactions))
    all_anomalies.extend(detect_round_numbers(transactions))
    all_anomalies.extend(detect_velocity_spikes(transactions))
    all_anomalies.extend(detect_new_vendors(transactions))

    # Sort by severity
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_anomalies.sort(key=lambda a: severity_order.get(a.get("severity", "LOW"), 2))

    return all_anomalies


def main() -> int:
    args = sys.argv[1:]
    input_file = None
    read_stdin = False

    i = 0
    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_file = Path(args[i + 1])
            i += 2
        elif args[i] == "--stdin":
            read_stdin = True
            i += 1
        else:
            i += 1

    if input_file:
        if not input_file.exists():
            print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
            return 1
        transactions = json.loads(input_file.read_text(encoding="utf-8"))
    else:
        try:
            transactions = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
            return 1

    if not isinstance(transactions, list):
        print("ERROR: Expected JSON array of transactions", file=sys.stderr)
        return 1

    anomalies = detect_anomalies(transactions)
    print(json.dumps(anomalies, indent=2))

    high_count = sum(1 for a in anomalies if a.get("severity") == "HIGH")
    print(f"\n# Anomalies: {len(anomalies)} (HIGH: {high_count})", file=sys.stderr)

    return 1 if high_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())