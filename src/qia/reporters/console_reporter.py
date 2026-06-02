from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text

from qia.models.triage import Severity, TriageReport

console = Console()

_SEVERITY_COLORS = {
    Severity.critical: "bold red",
    Severity.high: "red",
    Severity.medium: "yellow",
    Severity.low: "green",
}

_RISK_COLORS = {
    "blocker": "bold red",
    "high": "red",
    "medium": "yellow",
    "low": "green",
}


def print_report(report: TriageReport) -> None:
    sev_color = _SEVERITY_COLORS.get(report.severity, "white")
    risk_color = _RISK_COLORS.get(report.release_risk.lower(), "white")

    # Header panel
    header = Text()
    header.append("Quality Intelligence Agent  ", style="bold cyan")
    header.append(f"[{report.severity.upper()}]", style=sev_color)
    console.print(Panel(header, box=box.DOUBLE_EDGE))

    # Summary
    console.print(f"\n[bold]Summary:[/bold] {report.failure_summary}")
    console.print(f"[bold]Category:[/bold] {report.category.value.replace('_', ' ').title()}")
    console.print(f"[bold]Component:[/bold] {report.affected_component}")
    console.print(f"[bold]Owner:[/bold] {report.predicted_owner}")
    console.print(f"[bold]Flaky:[/bold] {'[yellow]Yes[/yellow]' if report.is_flaky else 'No'}")
    console.print(
        f"[bold]Release Risk:[/bold] [{risk_color}]{report.release_risk.upper()}[/{risk_color}]"
    )
    console.print(f"[bold]Confidence:[/bold] {report.confidence:.0%}")

    # Root cause
    console.print(Panel(report.root_cause, title="Root Cause Analysis", border_style="blue"))

    # Suggested actions
    if report.suggested_actions:
        table = Table(title="Suggested Actions", box=box.SIMPLE, show_lines=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Action")
        table.add_column("Description")
        for action in sorted(report.suggested_actions, key=lambda a: a.priority):
            table.add_row(str(action.priority), f"[bold]{action.title}[/bold]", action.description)
        console.print(table)

    # Similar patterns
    if report.similar_failure_patterns:
        console.print("\n[bold]Similar Failure Patterns:[/bold]")
        for pattern in report.similar_failure_patterns:
            console.print(f"  • {pattern}")

    console.print()
