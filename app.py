import math
import sqlite3

from flask import Flask, render_template, request

from analyzer import analyze_code
from history import DB_PATH, historical_data
from prompts import ai_suggestions


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze() -> str:
    code = (request.form.get("code") or "").strip()
    language = request.form.get("language", "python")

    if not code:
        return render_template("index.html", error="Please submit code to analyze.")

    findings, risk = analyze_code(code)

    try:
        historical_data(code, findings, language)
    except Exception:
        pass

    suggestion = ai_suggestions(code, findings, language) if findings else None

    return render_template(
        "results.html",
        code=code,
        language=language,
        findings=findings,
        len_findings=len(findings),
        risk=risk,
        suggestion=suggestion,
    )


@app.route("/history", methods=["GET"])
def history() -> str:
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()

        cursor.execute(
            "SELECT COUNT(DISTINCT scans.id) FROM scans JOIN findings ON scans.id = findings.scan_id"
        )
        total_rows = cursor.fetchone()[0] or 0

        cursor.execute(
            """
            SELECT
                scans.id,
                scans.language,
                scans.code,
                scans.created_at,
                findings.id,
                findings.scan_id,
                findings.title,
                findings.severity,
                findings.line,
                findings.explanation
            FROM scans
            JOIN findings ON scans.id = findings.scan_id
            ORDER BY scans.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (per_page, offset),
        )

        history_rows = cursor.fetchall()

    total_pages = math.ceil(total_rows / per_page) if total_rows else 1

    return render_template("history.html", history=history_rows, page=page, total_pages=total_pages)


if __name__ == "__main__":
    app.run(debug=True)
