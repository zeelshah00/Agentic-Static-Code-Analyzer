import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Vulnerability:
    pattern: str
    title: str
    severity: str
    category: str
    explanation: str
    pattern_re: re.Pattern


RULES_CSV = Path(__file__).with_name("vulnerabilities.csv")

# Severity levels as integers so findings can be compared and aggregated.
SEVERITY_ORDER = {"Safe": 0, "Low": 1, "Medium": 2, "High": 3}


@lru_cache(maxsize=1)
def load_vulnerabilities(csv_path: str = None) -> List[Vulnerability]:
    """Load and compile vulnerability rules from CSV. Result is cached."""
    path = Path(csv_path) if csv_path else RULES_CSV
    rules: List[Vulnerability] = []

    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pattern_text = (row.get("pattern") or "").strip()
            rules.append(
                Vulnerability(
                    pattern=pattern_text,
                    title=row.get("title", "").strip(),
                    severity=row.get("severity", "Low").strip(),
                    category=row.get("category", "").strip(),
                    explanation=row.get("explanation", "").strip(),
                    # Patterns are literal substrings, not regexes — escape before compiling.
                    pattern_re=re.compile(re.escape(pattern_text)),
                )
            )

    return rules


def analyze_code(code: str) -> Tuple[List[Dict], str]:
    """Scan `code` line-by-line against all loaded rules.

    Returns (findings, overall_risk). Each finding dict includes the matched
    rule metadata and the offending line number and snippet.
    """
    rules = load_vulnerabilities()
    findings: List[Dict] = []
    overall_level = SEVERITY_ORDER["Safe"]

    for line_number, line in enumerate(code.splitlines(), start=1):
        for rule in rules:
            if rule.pattern_re.search(line):
                findings.append(
                    {
                        "pattern": rule.pattern,
                        "category": rule.category,
                        "title": rule.title,
                        "severity": rule.severity,
                        "line": line_number,
                        "explanation": rule.explanation,
                        "snippet": line.strip(),
                    }
                )
                overall_level = max(overall_level, SEVERITY_ORDER.get(rule.severity, 1))

    level_map = {v: k for k, v in SEVERITY_ORDER.items()}
    return findings, level_map.get(overall_level, "Safe")
