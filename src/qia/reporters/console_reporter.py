from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text

from qia.models.triage import ReleaseRisk, Severity, TriageReport

console = Console()

_SEVERITY_COLORS = {
    Severity.critical: "bold red",
    Severity.high: "red",
    Severity.medium: "yellow",
    Severity.low: "green",
}

_RISK_COLORS = {
    ReleaseRisk.blocker: "bold red",
    ReleaseRisk.high: "red",
    ReleaseRisk.medium: "yellow",
    ReleaseRisk.low: "green",
}


def print_report(report: TriageReport) -> None:
    sev_color = _SEVERITY_COLORS.get(report.severity, "white")
    risk_color = _RISK_COLORS.get(report.release_risk, "white")

    # Header panel
    header = Text()
    header.append("Quality Intelligence Agent  ", style="bold cyan")
    header.append(f"[{report.severity.value.upper()}]", style=sev_color)
    console.print(Panel(header, box=box.DOUBLE_EDGE))

    # Summary — escape Claude output before injecting into Rich markup
    console.print(f"\n[bold]Summary:[/bold] {escape(report.failure_summary)}")
    console.print(f"[bold]Category:[/bold] {report.category.value.replace('_', ' ').title()}")
    console.print(f"[bold]Component:[/bold] {escape(report.affected_component)}")
    console.print(f"[bold]Owner:[/bold] {escape(report.predicted_owner)}")
    console.print(f"[bold]Flaky:[/bold] {'[yellow]Yes[/yellow]' if report.is_flaky else 'No'}")
    console.print(
        f"[bold]Release Risk:[/bold] [{risk_color}]{report.release_risk.value.upper()}[/{risk_color}]"
    )
    console.print(f"[bold]Confidence:[/bold] {report.confidence:.0%}")

    # Root cause — plain text panel, no markup parsing needed
    console.print(Panel(escape(report.root_cause), title="Root Cause Analysis", border_style="blue"))

    # Suggested actions
    if report.suggested_actions:
        table = Table(title="Suggested Actions", box=box.SIMPLE, show_lines=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Action")
        table.add_column("Description")
        for action in sorted(report.suggested_actions, key=lambda a: a.priority):
            table.add_row(
                str(action.priority),
                f"[bold]{escape(action.title)}[/bold]",
                escape(action.description),
            )
        console.print(table)

    # Similar patterns
    if report.similar_failure_patterns:
        console.print("\n[bold]Similar Failure Patterns:[/bold]")
        for pattern in report.similar_failure_patterns:
            console.print(f"  • {escape(pattern)}")

    console.print()
