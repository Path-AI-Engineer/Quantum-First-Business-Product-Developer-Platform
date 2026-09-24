"""Explicit CLI commands match the Project 55 handoff contract."""

import json

import typer

from venture_evidence.reporting import build_reports, export_handoff, export_schemas, verify_handoff
from venture_evidence.repository import load_corpus, load_protocol
from venture_evidence.scoring import compare, sensitivity
from venture_evidence.validation import validate

app = typer.Typer(no_args_is_help=True)
evidence_app = typer.Typer()
opportunity_app = typer.Typer()
report_app = typer.Typer()
handoff_app = typer.Typer()
app.add_typer(evidence_app, name="evidence")
app.add_typer(opportunity_app, name="opportunity")
app.add_typer(report_app, name="report")
app.add_typer(handoff_app, name="handoff")


def emit(value: object) -> None:
    typer.echo(json.dumps(value, ensure_ascii=False, indent=2))


@evidence_app.command("validate")
def evidence_validate() -> None:
    emit(validate(load_corpus(), load_protocol()))


@evidence_app.command("lint")
def evidence_lint() -> None:
    evidence_validate()


@opportunity_app.command("score")
def opportunity_score(scenario: str = "base") -> None:
    if scenario not in ("conservative", "base", "aggressive"):
        raise typer.BadParameter("scenario must be conservative, base or aggressive")
    if scenario == "conservative":
        rows = compare(load_corpus(), load_protocol(), "conservative")
    elif scenario == "aggressive":
        rows = compare(load_corpus(), load_protocol(), "aggressive")
    else:
        rows = compare(load_corpus(), load_protocol(), "base")
    emit([r.model_dump() for r in rows])


@opportunity_app.command("sensitivity")
def opportunity_sensitivity() -> None:
    emit(sensitivity(load_corpus(), load_protocol()))


@report_app.command("build")
def report_build() -> None:
    room = build_reports()
    export_schemas()
    emit({"status": "built", "audit": room["audit"]})


@handoff_app.command("export")
def handoff_export(version: str = "company-vision-v1") -> None:
    emit({"directory": str(export_handoff(version)), "approval": "pending_human_review"})


@handoff_app.command("verify")
def handoff_verify(version: str = "company-vision-v1") -> None:
    emit(verify_handoff(version))


if __name__ == "__main__":
    app()
