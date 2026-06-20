import sqlite3
from pathlib import Path
from typing import Dict, Iterable


DB_PATH = Path(__file__).with_name("scans.db")


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT,
            code TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            title TEXT,
            severity TEXT,
            line INTEGER,
            explanation TEXT,
            FOREIGN KEY(scan_id) REFERENCES scans(id)
        )
        """
    )
    conn.commit()


def historical_data(code: str, findings: Iterable[Dict], language: str) -> None:
    """Persist a completed scan and its findings to SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        _ensure_schema(conn)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO scans (language, code) VALUES (?, ?)", (language, code)
        )
        scan_id = cursor.lastrowid

        rows = [
            (scan_id, f.get("title"), f.get("severity"), f.get("line"), f.get("explanation"))
            for f in findings
        ]
        if rows:
            cursor.executemany(
                "INSERT INTO findings (scan_id, title, severity, line, explanation) VALUES (?, ?, ?, ?, ?)",
                rows,
            )

        conn.commit()
