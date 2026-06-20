# CodeProtect AI

A static analysis tool that detects common security vulnerabilities in source code and augments deterministic findings with AI-generated remediation guidance.

Built to explore a core AI engineering principle: use deterministic systems where you need reliability, and generative AI where you need natural language — never let the model make the security call.

---

## What It Does

Paste a code snippet into the web UI, select the language, and CodeProtect AI will:

1. Scan every line against a compiled set of known-bad patterns (eval, shell injection, hardcoded secrets, XSS sinks, etc.)
2. Score each finding by severity and compute an overall risk level
3. Send the confirmed findings to an LLM to generate a concise, targeted remediation suggestion
4. Persist the scan and findings to a local SQLite database for historical review

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Web framework | Flask | Three routes, no complex state — heavier frameworks would add friction |
| Rule engine | CSV + compiled regex | Human-readable, version-controllable, zero infrastructure |
| LLM | OpenAI gpt-4o-mini | Low latency and low cost for short-context summarization tasks; model is swappable via `OPENAI_MODEL` env var |
| Persistence | SQLite | Self-contained for a local tool; no migration tooling needed |
| Frontend | Bootstrap 5 + Jinja2 | Server-rendered keeps the stack simple and avoids a JS build step |

---

## AI Engineering Design

This is where the interesting decisions live.

**Stochastic vs deterministic: use the right tool for each job.**
The scanner never asks the LLM whether code is vulnerable. LLMs hallucinate — a security tool that invents findings or silently misses real ones is worse than no tool at all. Detection is fully deterministic: the ruleset is a versioned CSV file, findings are reproducible, and every result is auditable. The LLM is brought in only *after* real findings exist, to do what it is good at: translating structured data into clear natural language.

**System/user message separation.**
The LLM call splits instructions from variable content. The system message establishes the assistant persona and constraints once. The user message contains only the per-request data: language, fenced code block, and a formatted findings list. This follows the standard chat completions pattern and keeps the model's instruction context clean across requests.

**Structured context, not raw Python repr.**
Findings are formatted as a human-readable numbered list before entering the prompt — not passed as raw `[{...}]` Python dict output. Structured, readable context measurably improves LLM output quality because the model is tokenizing natural-language text, not parsing interpreter output.

**`temperature=0` for consistent remediation.**
Remediation suggestions should be reproducible for the same input. Creativity adds no value here — the model is summarising and suggesting, not generating. Setting `temperature=0` makes the output consistent across identical scans and easier to evaluate.

**Token budget: 400 max tokens.**
A targeted fix suggestion for 1–3 findings fits comfortably in ~300 words. Raising the limit would cost more per call without improving quality for this task. The budget is explicit so it is easy to tune if the ruleset grows.

**Stateless single-turn inference.**
Each scan is a fresh, self-contained request. No conversation history is maintained because none is needed — the full context (code + findings) is present in every call. This keeps latency low and avoids accumulating tokens across turns.

**Prompt injection surface: acknowledged.**
User-submitted code enters the prompt directly, creating a prompt injection vector. For a local developer tool this is an acceptable risk; the threat model is a single trusted user. A production deployment would require input sanitization or a sandboxed prompt template that keeps user content clearly delimited.

**Graceful degradation.**
The OpenAI SDK is an optional dependency. If it is absent or the API call fails, the app returns a safe fallback string and continues normally. The core scanner is never blocked by the AI layer.

---

## Architecture

```
User submits code
       │
       ▼
  analyzer.py          ← deterministic, always runs
  (regex scanner)
       │
  findings + risk
       │
       ├──────────────► history.py (SQLite persist)
       │
       ▼
  prompts.py           ← stochastic, optional
  (LLM call)
       │
  suggestion
       │
       ▼
  results.html
```

---

## Quickstart

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set your OpenAI key (optional — the scanner runs without it):

```bash
export OPENAI_API_KEY=sk-...    # Windows: set OPENAI_API_KEY=sk-...
```

Run the app:

```bash
flask run
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) and paste code to scan.

---

## Project Structure

```
.
├── app.py               # Flask routes (index, analyze, history)
├── analyzer.py          # Rule loader and line-by-line scanner
├── history.py           # SQLite persistence (scans + findings tables)
├── prompts.py           # LLM integration for remediation suggestions
├── vulnerabilities.csv  # Pattern ruleset — add rows to extend coverage
├── templates/           # Jinja2 templates (base, index, results, history)
└── static/styles.css    # Minimal custom styles on top of Bootstrap
```

---

## Extending the Ruleset

Add a row to `vulnerabilities.csv` to detect a new pattern:

```
pattern,title,severity,category,explanation
os.system(,Direct OS command execution,High,Injection Risk,os.system() passes input directly to the shell without sanitisation.
```

The scanner picks up new rules on the next request (cache is per-process).

---

## Potential Next Steps

- **RAG over CVE/NIST advisories** — embed vulnerability advisories as vector context so the LLM can surface CVE references and known exploit patterns in its suggestions
- **Eval harness** — measure suggestion quality against a labeled set of known-good fixes to catch prompt regressions when the model or prompt changes
- **Streaming responses** — use the OpenAI streaming API to progressively render suggestions for large code blocks
- **Multi-model support** — abstract the LLM call behind an interface to support Claude, Gemini, or local Ollama models for offline/private scanning
- **Agentic refinement loop** — re-scan the AI's proposed fix and prompt it to self-correct if the suggestion still contains vulnerable patterns
- **AST-based detection** — replace regex with AST traversal to eliminate false positives from patterns that appear in comments or string literals
- **CLI and CI integration** — expose the scanner as a command-line tool for GitHub Actions to block merges on high-severity findings
