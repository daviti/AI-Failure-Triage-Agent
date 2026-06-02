"""QIA CLI — Quality Intelligence Agent command-line interface."""

import json
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from qia.agents import triage_agent
from qia.reporters.console_reporter import print_report

app = typer.Typer(
    name="qia",
    help="Quality Intelligence Agent — AI-powered CI failure triage and root cause analysis.",
    add_completion=False,
)
console = Console()
err = Console(stderr=True)


@app.command()
def triage(
    log_file: Annotated[
        Optional[Path],
        typer.Option("--log", "-l", help="Path to CI log file"),
    ] = None,
    log_text: Annotated[
        Optional[str],
        typer.Option("--text", "-t", help="Raw log text (alternative to --log)"),
    ] = None,
    test_name: Annotated[
        Optional[str],
        typer.Option("--test", "-n", help="Test or job name"),
    ] = None,
    screenshot: Annotated[
        Optional[Path],
        typer.Option("--screenshot", "-s", help="Screenshot captured at failure"),
    ] = None,
    context: Annotated[
        Optional[str],
        typer.Option("--context", "-c", help="Extra context (PR title, branch, etc.)"),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON instead of formatted report"),
    ] = False,
) -> None:
    """Triage a CI failure using Claude Opus 4.8 with adaptive thinking."""
    # Resolve log content
    if log_file:
        if not log_file.exists():
            err.print(f"[red]Error:[/red] Log file not found: {log_file}")
            raise typer.Exit(1)
        log_content = log_file.read_text(encoding="utf-8", errors="replace")
    elif log_text:
        log_content = log_text
    elif not sys.stdin.isatty():
        log_content = sys.stdin.read()
    else:
        err.print("[red]Error:[/red] Provide a log via --log, --text, or stdin.")
        raise typer.Exit(1)

    if not log_content.strip():
        err.print("[red]Error:[/red] Log content is empty.")
        raise typer.Exit(1)

    with console.status("[cyan]Analyzing failure with QIA…[/cyan]"):
        try:
            report = triage_agent.analyze(
                log_content=log_content,
                test_name=test_name,
                screenshot_path=screenshot,
                extra_context=context,
            )
        except Exception as exc:
            err.print(f"[red]Analysis failed:[/red] {exc}")
            raise typer.Exit(1) from exc

    if output_json:
        console.print_json(json.dumps(report.model_dump(), indent=2))
    else:
        print_report(report)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
