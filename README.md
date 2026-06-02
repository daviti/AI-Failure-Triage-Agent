# Quality Intelligence Agent (QIA)

> AI-powered CI failure triage, root cause analysis, and release risk intelligence — built with Claude Opus 4.8.

---

## The Problem

On any team that ships software continuously, CI failures are a daily tax. Engineers spend **30–90 minutes per incident** doing the same manual work over and over:

1. Open the failed job and scroll through 5,000 lines of logs
2. Figure out *what* failed and *why* — environment issue? flaky test? real bug?
3. Decide who should fix it
4. Assess whether it blocks the release
5. Write a Slack message explaining it to the team

This is repetitive, high-context, slow work. It compounds fast: a team running 500 CI jobs/day with a 5% failure rate burns **25+ engineer-hours per week** on triage alone — before anyone writes a single line of fix.

---

## What QIA Does

QIA replaces manual triage with a **structured AI analysis** powered by Claude Opus 4.8. Feed it a CI log (and optionally a failure screenshot), and it returns a complete, actionable report in seconds:

| Output Field | What It Tells You |
|---|---|
| **Failure Summary** | One-sentence description of what broke |
| **Root Cause** | Deep analysis quoting exact log lines and stack traces |
| **Category** | Classified failure type (see below) |
| **Severity** | `critical` / `high` / `medium` / `low` |
| **Affected Component** | The module, service, or screen that failed |
| **Flaky Detection** | Whether this is a non-deterministic/intermittent failure |
| **Suggested Actions** | Prioritized list of steps to investigate or fix |
| **Predicted Owner** | Team or person most likely responsible |
| **Similar Patterns** | Known failure patterns this resembles |
| **Release Risk** | `blocker` / `high` / `medium` / `low` — safe to ship? |
| **Confidence Score** | How certain the analysis is (0–100%) |

### Failure Categories

QIA classifies every failure into one of eight categories:

| Category | Examples |
|---|---|
| `environment` | Device farm offline, emulator crash, missing env var |
| `flaky_test` | Timing issue, race condition, non-deterministic selector |
| `assertion_failure` | Wrong value returned, UI element mismatch |
| `compilation_error` | Build failure, missing symbol, type error |
| `dependency` | Package version conflict, network timeout on artifact fetch |
| `timeout` | Test exceeded time limit, slow device, stuck process |
| `infrastructure` | CI runner crash, disk full, memory OOM |
| `unknown` | Cannot be classified with available information |

---

## Demo

### CLI — formatted report

```bash
qia triage --log ci_failure.log --test "LoginFlowTest" --context "PR #482 — auth refactor"
```

```
╔══════════════════════════════════════════════════════╗
║  Quality Intelligence Agent   [HIGH]                 ║
╚══════════════════════════════════════════════════════╝

Summary:   NullPointerException in LoginActivity.onResume() caused by
           uninitialized auth token after recent refactor
Category:  Assertion Failure
Component: com.example.app.LoginActivity (Android)
Owner:     Mobile Auth Team
Flaky:     No
Release Risk: HIGH
Confidence:   91%

╭─ Root Cause Analysis ──────────────────────────────────╮
│ The failure originates at LoginActivity.kt:142 inside  │
│ onResume(). The auth token accessor was changed in     │
│ PR #480 to return null before the session is restored|
│ but the calling code in onResume() was not updated to  │
│ guard against null. This is not a flaky failure —      │
│ it reproduces 100% on fresh installs.                  │
│                                                        │
│ Relevant log lines:                                    │
│  java.lang.NullPointerException                        │
│    at LoginActivity.onResume(LoginActivity.kt:142)     │
╰────────────────────────────────────────────────────────╯

 Suggested Actions
 # │ Action                  │ Description
───┼─────────────────────────┼──────────────────────────────────────────
 1 │ Add null guard          │ Add `?: return` before the token access
   │                         │ in onResume() at line 142
 2 │ Add unit test           │ Cover the null-token case in
   │                         │ LoginActivityTest
 3 │ Review PR #480 changes│ Audit all callers of the new auth
   │                         │ token accessor for similar gaps

Similar Failure Patterns:
  • Android activity lifecycle null state after back-stack restore
  • Token accessor contract change without callsite audit
```

### CLI — JSON output (for pipelines)

```bash
cat ci.log | qia triage --test "CheckoutTest" --json
```

```json
{
  "failure_summary": "NullPointerException in LoginActivity.onResume() ...",
  "root_cause": "The failure originates at LoginActivity.kt:142 ...",
  "category": "assertion_failure",
  "severity": "high",
  "affected_component": "com.example.app.LoginActivity",
  "is_flaky": false,
  "suggested_actions": [
    { "title": "Add null guard", "description": "...", "priority": 1 },
    { "title": "Add unit test",  "description": "...", "priority": 2 }
  ],
  "predicted_owner": "Mobile Auth Team",
  "similar_failure_patterns": ["Android activity lifecycle null state ..."],
  "release_risk": "high",
  "confidence": 0.91
}
```

### With screenshot (vision analysis)

```bash
qia triage --log appium.log --screenshot failure_screen.png --test "OnboardingFlow"
```

QIA combines the log analysis with visual inspection of the screenshot — useful for UI automation failures where the log alone doesn't show what the screen looked like when it crashed.

---

## Installation

**Requirements:** Python 3.12+, [`uv`](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/quality-intelligence-agent.git
cd quality-intelligence-agent

# 2. Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Install dependencies
uv sync

# 4. Run
uv run qia triage --help
```

### `.env` configuration

```env
ANTHROPIC_API_KEY=sk-ant-...   # required

# Optional — defaults shown
MODEL=claude-opus-4-8
MAX_TOKENS=8192
EFFORT=high
```

---

## Usage

### From a log file

```bash
uv run qia triage --log path/to/ci_failure.log
```

### From stdin (pipe from CI script)

```bash
cat artifacts/job.log | uv run qia triage --test "SmokeTest"
```

### With all options

```bash
uv run qia triage \
  --log      ci.log           \   # path to log file
  --test     "LoginFlowTest"  \   # test or job name
  --screenshot failure.png    \   # screenshot at time of failure (optional)
  --context  "PR #482, branch: auth-refactor" \  # extra context
  --json                          # output JSON instead of formatted report
```

### All flags

| Flag | Short | Description |
|---|---|---|
| `--log PATH` | `-l` | Path to CI log file |
| `--text TEXT` | `-t` | Raw log text inline (alternative to `--log`) |
| `--test NAME` | `-n` | Test or job name |
| `--screenshot PATH` | `-s` | Screenshot captured at failure |
| `--context TEXT` | `-c` | Extra context: PR title, branch, environment |
| `--json` | | Output raw JSON instead of formatted report |

---

## How It Works

```
CI Log + Screenshot
       │
       ▼
  ┌──────────────────────────────────────────┐
  │          Triage Agent                    │
  │                                          │
  │  • Claude Opus 4.8 (most capable model)  │
  │  • Adaptive thinking — Claude decides    │
  │    how deeply to reason per failure      │
  │  • Prompt caching — system prompt is     │
  │    cached; saves ~90% on repeated calls  │
  │  • Vision — screenshot analyzed with     │
  │    the log for full-context understanding│
  │  • Structured output — Pydantic model    │
  │    guarantees a valid, typed report      │
  └──────────────────────────────────────────┘
       │
       ▼
  TriageReport (typed, validated)
       │
       ├── Console (Rich formatted)
       └── JSON (for CI pipelines / dashboards)
```

### Architecture choices

| Decision | Choice | Reason |
|---|---|---|
| Model | `claude-opus-4-8` | Highest reasoning capability; best at connecting subtle log signals to root causes |
| Thinking | `adaptive` | Claude decides when multi-step reasoning is worth the tokens — deep for complex failures, fast for obvious ones |
| Effort | `high` | Correct analysis matters more than speed for triage |
| Prompt caching | System prompt cached (`ephemeral`) | System prompt is identical across every call; caching saves ~90% of those tokens after the first request |
| Structured output | `messages.parse()` + Pydantic | Guarantees a valid, typed `TriageReport` — no regex parsing, no JSON errors |
| Screenshot vision | Base64 inline | Works with any image from any CI artifact store without an upload step |

---

## Metrics QIA Produces

Every `TriageReport` gives you data you can track over time:

| Metric | Type | Use |
|---|---|---|
| `severity` | `critical / high / medium / low` | Alert routing, SLA thresholds |
| `category` | 8 categories | Track which failure type is trending up |
| `is_flaky` | `bool` | Measure flaky test rate over time |
| `release_risk` | `blocker / high / medium / low` | Go/no-go gate automation |
| `confidence` | `0.0 – 1.0` | Filter low-confidence reports for human review |
| `predicted_owner` | `string` | Automatically route tickets to the right team |
| `affected_component` | `string` | Identify hotspot components with repeated failures |

### Example dashboard KPIs you can derive

- **Flaky test rate** — `count(is_flaky=true) / total_failures` per week
- **Time-to-triage** — seconds from CI failure to `TriageReport` in hand
- **Failure category breakdown** — pie chart of `category` distribution
- **Release blocker rate** — `count(release_risk="blocker") / total_failures`
- **High-confidence auto-close rate** — failures resolved without human review
- **Top failing components** — `affected_component` ranked by failure count

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| AI | [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) — Claude Opus 4.8 |
| Data models | [Pydantic v2](https://docs.pydantic.dev/) |
| Configuration | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| CLI | [Typer](https://typer.tiangolo.com/) |
| Terminal output | [Rich](https://rich.readthedocs.io/) |
| Linting | [Ruff](https://docs.astral.sh/ruff/) |
| Tests | [pytest](https://pytest.org/) |

---

## Project Structure

```
quality-intelligence-agent/
├── src/qia/
│   ├── agents/
│   │   └── triage_agent.py      # Claude Opus 4.8 + caching + structured output
│   ├── models/
│   │   └── triage.py            # Pydantic TriageReport model
│   ├── reporters/
│   │   └── console_reporter.py  # Rich terminal output
│   ├── cli.py                   # Typer CLI entry point
│   └── config.py                # pydantic-settings config
├── tests/
│   └── conftest.py
├── pyproject.toml
├── .env.example
└── .python-version
```

---

## Roadmap

- [ ] `qia cluster` — group similar failures across a CI run to surface patterns
- [ ] `qia risk` — release risk report across all failures in a pipeline
- [ ] GitHub Actions integration — comment triage report on failed PRs automatically
- [ ] Jira / Linear integration — auto-create tickets with pre-filled triage data
- [ ] History store — compare new failures against a local database of past reports
- [ ] Slack reporter — post formatted triage summaries to a channel
- [ ] Smart test selection — predict which tests to run given a diff

---

## What Problem This Solves (for hiring managers)

This project demonstrates the ability to build **AI-assisted quality engineering systems** — the intersection of:

- Deep QA/SDET domain knowledge (CI pipelines, failure patterns, automation frameworks)
- Applied AI engineering (prompt design, structured outputs, vision, caching strategy)
- Production-quality Python (typed, validated, testable, extensible)

The kind of internal tooling that saves engineering teams hours every week and doesn't exist off the shelf.

---

## License

MIT
