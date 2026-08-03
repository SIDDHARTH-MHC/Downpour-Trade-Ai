#!/usr/bin/env python3
"""Downpour Trade AI — CLI entry point."""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from engine.analyzer import analyze_symbol
from engine.backtest import run_backtest
from engine.calibration import rebuild_calibration
from engine.config import load_config

app = typer.Typer(name="downpour", help="Downpour Trade AI — deterministic crypto signal engine")
db_app = typer.Typer(help="Production SQLite (API); schema via CREATE IF NOT EXISTS")
app.add_typer(db_app, name="db")
console = Console()


def _research_enable_if_requested(enable: bool, database_url: str) -> None:
    if not enable:
        return
    from research_platform.cli_workflow import enable_research_env

    enable_research_env(database_url or None)


def _render_verdict(verdict, json_only: bool = False) -> None:
    if json_only:
        console.print_json(json.dumps(verdict.to_dict(), indent=2))
        return

    console.print(f"\n[bold cyan]{verdict.symbol}[/bold cyan] · {verdict.timeframe} · {verdict.timestamp}")
    console.print(f"regime: [yellow]{verdict.regime.regime}[/yellow] (tradeable={verdict.regime.tradeable})\n")

    table = Table(title="Lanes", show_header=True, header_style="bold")
    table.add_column("LANE", style="dim")
    table.add_column("SCORE", justify="right")
    table.add_column("EVIDENCE")

    for lane in verdict.lanes:
        ev = " · ".join(lane.evidence[:4])
        if len(lane.evidence) > 4:
            ev += " · ..."
        table.add_row(lane.name, f"{lane.score:+.1f}", ev)

    console.print(table)
    console.print(f"\nWEIGHTED SCORE: [bold]{verdict.weighted_score:+.1f}[/bold]        VERDICT: [bold magenta]{verdict.action}[/bold magenta]")
    console.print(f"Confidence: {verdict.confidence}\n")

    if verdict.reasons:
        console.print("Reason: " + "; ".join(verdict.reasons))

    if verdict.explanation:
        exp = verdict.explanation
        if exp.why:
            console.print("\n[green]Why:[/green]")
            for line in exp.why[:6]:
                console.print(f"  ✓ {line}")
        if exp.why_not:
            console.print("\n[yellow]Why not stronger:[/yellow]")
            for line in exp.why_not[:6]:
                console.print(f"  ✗ {line}")
        if exp.risk:
            console.print("\n[bold]Risk:[/bold]")
            for line in exp.risk:
                console.print(f"  {line}")

    if verdict.trade_plan:
        tp = verdict.trade_plan
        console.print(
            f"\nTrade plan: entry={tp.entry:.4f} SL={tp.stop_loss:.4f} TP1={tp.tp1:.4f} TP2={tp.tp2:.4f} "
            f"R:R={tp.reward_risk:.2f} size={tp.size_coin:.6f} (${tp.size_usd:.2f})"
        )


@app.command()
def analyze(
    symbol: str = typer.Argument("BTC/USDT", help="Trading pair"),
    tf: str = typer.Option("1h", "--tf", help="Timeframe"),
    json_output: bool = typer.Option(False, "--json", help="JSON output only"),
    patient: bool = typer.Option(False, "--patient", help="Use S/R retest entry"),
    equity: float = typer.Option(10_000.0, "--equity", help="Account equity USD for sizing"),
) -> None:
    """Run full multi-lane analysis on a symbol."""
    config = load_config()
    console.print(f"[bold]Downpour Trade AI[/bold] — analyzing {symbol} @ {tf}")
    verdict = analyze_symbol(symbol, tf, patient=patient, equity_usd=equity, config=config)
    _render_verdict(verdict, json_only=json_output)


@app.command()
def backtest(
    symbol: str = typer.Argument("BTC/USDT"),
    tf: str = typer.Option("1h", "--tf"),
    months: int = typer.Option(12, "--months"),
) -> None:
    """Replay engine over historical OHLCV."""
    console.print(f"[bold]Downpour Trade AI[/bold] — backtesting {symbol} @ {tf} ({months} months)")
    result = run_backtest(symbol, tf, months)
    summary = result.summary()
    console.print_json(json.dumps(summary, indent=2))
    if result.structure_degraded:
        console.print("[dim]Note: structure lane degraded to S/R-only in backtest (no historical order books)[/dim]")
    if result.flow_degraded:
        console.print("[dim]Note: flow lane degraded in backtest (limited historical funding/OI)[/dim]")


@app.command()
def calibrate(
    symbols: str = typer.Option("BTC/USDT,ETH/USDT", help="Comma-separated symbols"),
    tf: str = typer.Option("1h", "--tf"),
    months: int = typer.Option(12, "--months"),
) -> None:
    """Rebuild confidence calibration tables."""
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    console.print(f"[bold]Downpour Trade AI[/bold] — calibrating on {', '.join(sym_list)}")
    stats = rebuild_calibration(sym_list, tf, months)
    out = Path("data/calibration.json")
    console.print(f"Saved calibration to {out}")
    console.print_json(json.dumps(stats, indent=2))


@app.command()
def scan(
    top: int = typer.Option(20, "--top"),
    tf: str = typer.Option("1h", "--tf"),
    json_output: bool = typer.Option(False, "--json"),
    workers: int = typer.Option(5, "--workers", help="Parallel scan workers"),
) -> None:
    """Scan top-volume pairs for non-NO-TRADE verdicts (parallel)."""
    from engine.data import DataLayer
    from engine.scan import scan_pairs

    config = load_config()
    data = DataLayer(config)
    pairs = data.get_top_volume_pairs(top)
    console.print(f"[bold]Downpour Trade AI[/bold] — scanning top {top} pairs @ {tf} ({workers} workers)\n")

    hits = scan_pairs(pairs, tf, config=config, max_workers=workers, light=False, actionable_only=True)

    if json_output:
        console.print_json(json.dumps([v.to_dict() for v in hits], indent=2))
        return

    if not hits:
        console.print("No actionable signals found (NO-TRADE on all scanned pairs).")
        return

    for verdict in hits:
        _render_verdict(verdict)
        console.print("-" * 60)


@db_app.command("init")
def production_db_init() -> None:
    """Create or upgrade production SQLite tables (same as API startup)."""
    from api.db import Database

    db = Database()
    db.init()
    console.print(f"[green]SQLite schema ready at[/green] {db.path}")


research_app = typer.Typer(help="Walk-forward experiments (see Research_Roadmap.md)")
app.add_typer(research_app, name="research")

research_db_app = typer.Typer(help="Research MDS database (PostgreSQL/Timescale; optional)")
research_app.add_typer(research_db_app, name="db")

research_run_app = typer.Typer(help="Run scheduled research jobs once (manual trigger)")
research_app.add_typer(research_run_app, name="run")


@research_app.command("automation-status")
def research_automation_status_cmd() -> None:
    """Show last run metadata for scheduled research + calibration policy."""
    import json

    from research_platform.jobs import research_automation_status

    console.print(json.dumps(research_automation_status(), indent=2))


@research_run_app.command("collector")
def research_run_collector() -> None:
    from research_platform.jobs import job_collect_historical_data

    console.print(job_collect_historical_data())


@research_run_app.command("dq")
def research_run_dq() -> None:
    from research_platform.jobs import job_daily_data_quality_scan

    console.print(job_daily_data_quality_scan())


@research_run_app.command("walk-forward")
def research_run_walk_forward() -> None:
    from research_platform.jobs import job_weekly_walk_forward

    console.print(job_weekly_walk_forward())


@research_app.command("scheduler")
def research_scheduler_service(
    foreground: bool = typer.Option(
        False,
        "--foreground",
        help="Run dedicated APScheduler loop (otherwise use API scheduler on uvicorn)",
    ),
) -> None:
    """Run research automation scheduler in foreground (optional)."""
    from research_platform.cli_workflow import enable_research_env
    from research_platform.config import get_research_settings

    enable_research_env()
    if not get_research_settings().research_scheduler_enabled:
        console.print("[yellow]Set RESEARCH_SCHEDULER_ENABLED=true[/yellow]")
        raise typer.Exit(1)
    if not foreground:
        console.print(
            "Production: enable RESEARCH_SCHEDULER_ENABLED and run [bold]uvicorn api.main:app[/bold]. "
            "Jobs attach to the API BackgroundScheduler."
        )
        console.print("Dev-only foreground loop: [bold]python cli.py research scheduler --foreground[/bold]")
        return
    from research_platform.scheduler_service import run_blocking_scheduler

    run_blocking_scheduler()


@research_db_app.command("status")
def research_db_status(
    enable: bool = typer.Option(False, "--enable", help="Enable RESEARCH_DB_* for this command only"),
    database_url: str = typer.Option("", help="Override RESEARCH_DATABASE_URL"),
) -> None:
    """Show research DB configuration and connectivity."""
    _research_enable_if_requested(enable, database_url)
    from research_platform.cli_db import print_status

    print_status()


@research_db_app.command("current")
def research_db_current(
    enable: bool = typer.Option(False, "--enable", help="Enable RESEARCH_DB_* for this command only"),
    database_url: str = typer.Option("", help="Override RESEARCH_DATABASE_URL"),
) -> None:
    """Print Alembic revision for the research database."""
    _research_enable_if_requested(enable, database_url)
    from research_platform.cli_db import cmd_current

    code = cmd_current()
    if code != 0:
        raise typer.Exit(code=code)


@research_db_app.command("migrate")
def research_db_migrate(
    enable: bool = typer.Option(False, "--enable", help="Enable RESEARCH_DB_* for this command only"),
    database_url: str = typer.Option("", help="Override RESEARCH_DATABASE_URL"),
) -> None:
    """Apply Alembic migrations to the research database."""
    _research_enable_if_requested(enable, database_url)
    from research_platform.cli_db import cmd_migrate

    code = cmd_migrate()
    if code != 0:
        raise typer.Exit(code=code)
    console.print("[green]Research DB migrations applied (head).[/green]")


@research_db_app.command("update")
def research_db_update(
    enable: bool = typer.Option(
        True,
        "--enable/--no-enable",
        help="Enable RESEARCH_DB_* for this process (default: on)",
    ),
    db_up: bool = typer.Option(False, "--db-up", help="Start local Timescale via docker compose"),
    database_url: str = typer.Option("", help="Override RESEARCH_DATABASE_URL"),
) -> None:
    """Start DB (optional), apply Alembic head, print status — run after pulling schema changes."""
    from research_platform.cli_db import cmd_migrate, print_status
    from research_platform.cli_workflow import docker_db_up, enable_research_env

    if enable:
        enable_research_env(database_url or None)
    if db_up:
        code = docker_db_up()
        if code != 0:
            raise typer.Exit(code=code)
        console.print("[green]Docker database started.[/green]")
    code = cmd_migrate()
    if code != 0:
        raise typer.Exit(code=code)
    console.print("[green]Research schema at Alembic head.[/green]")
    print_status()


@research_db_app.command("up")
def research_db_up() -> None:
    """Start local TimescaleDB via deploy/research/docker-compose.yml."""
    from research_platform.cli_workflow import docker_db_up

    code = docker_db_up()
    if code != 0:
        raise typer.Exit(code=code)
    console.print("[green]Research database container started (port 5433).[/green]")
    console.print("Run: [bold]python cli.py research db update --enable[/bold]")


@research_db_app.command("down")
def research_db_down() -> None:
    """Stop local TimescaleDB container."""
    from research_platform.cli_workflow import docker_db_down

    code = docker_db_down()
    if code != 0:
        raise typer.Exit(code=code)
    console.print("[dim]Research database container stopped.[/dim]")


@research_app.command("guide")
def research_guide() -> None:
    """Print the full research MDS CLI workflow."""
    from research_platform.cli_workflow import guide_text

    console.print(guide_text())


@research_app.command("setup")
def research_setup(
    enable: bool = typer.Option(False, "--enable", help="Set RESEARCH_DB_* for this process only"),
    db_up: bool = typer.Option(False, "--db-up", help="docker compose up -d"),
    migrate: bool = typer.Option(False, "--migrate", help="Run Alembic migrations"),
    database_url: str = typer.Option("", help="Override RESEARCH_DATABASE_URL"),
) -> None:
    """Bootstrap research DB (optional docker up + migrate)."""
    from research_platform.cli_workflow import enable_research_env, print_env_hint
    from research_platform.cli_db import cmd_migrate, print_status
    from research_platform.cli_workflow import docker_db_up

    if enable:
        enable_research_env(database_url or None)
        console.print("[green]Research DB enabled for this CLI session.[/green]")
    else:
        console.print("[yellow]Tip:[/yellow] pass [bold]--enable[/bold] or export RESEARCH_DB_ENABLED=true")
        print_env_hint()

    if db_up:
        code = docker_db_up()
        if code != 0:
            raise typer.Exit(code=code)
        console.print("[green]Docker database started.[/green]")

    if migrate:
        if not enable and not os.environ.get("RESEARCH_DB_ENABLED", "").lower() in ("1", "true", "yes"):
            console.print("[red]Enable research DB first (--enable or export).[/red]")
            raise typer.Exit(1)
        code = cmd_migrate()
        if code != 0:
            raise typer.Exit(code=code)
        console.print("[green]Migrations applied.[/green]")

    print_status()


@research_app.command("quickstart")
def research_quickstart(
    skip_docker: bool = typer.Option(False, "--skip-docker", help="Assume DB already running"),
) -> None:
    """Enable research env, start DB, migrate, collect BTC/ETH, run DQ scan."""
    from research_platform.cli_workflow import run_quickstart

    code = run_quickstart(db_up=not skip_docker, migrate=True, collect=True, dq=True)
    if code != 0:
        raise typer.Exit(code=code)


@research_app.command("walk-forward")
def research_walk_forward(
    variant: str = typer.Option("T3", help="R0 variant: B0, T1, T2, T3"),
    symbols: str = typer.Option("BTC/USDT,ETH/USDT", help="Comma-separated pairs"),
    months: int = typer.Option(12, "--months", min=1, max=18),
    compare: bool = typer.Option(False, "--compare", help="Run all R0 variants"),
    record: bool = typer.Option(False, "--record", help="Write reproducibility artifact bundle"),
) -> None:
    """EXP-R0: technical orthogonalization walk-forward."""
    from research.runner import compare_r0_variants, run_r0_walk_forward

    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    if compare:
        results = compare_r0_variants(sym_list, months=months)
    else:
        results = [run_r0_walk_forward(variant, sym, months) for sym in sym_list]

    if record:
        from research_platform.experiments.registry import ExperimentRegistry

        reg = ExperimentRegistry()
        for r in results:
            reg.create_run_bundle(
                experiment_code="EXP-2026-001",
                variant=r.variant,
                run_kind="walk_forward",
                symbols=[r.symbol],
                timeframe="1h",
                months=months,
                metrics=r.to_dict(),
            )
        console.print("[dim]Recorded experiment artifacts under research/artifacts/[/dim]")

    table = Table(title="Walk-forward (research)")
    table.add_column("Variant")
    table.add_column("Symbol")
    table.add_column("OOS PF", justify="right")
    table.add_column("OOS trades", justify="right")
    table.add_column("WF pass")
    for r in results:
        table.add_row(
            r.variant,
            r.symbol,
            f"{r.out_of_sample_profit_factor:.3f}",
            str(r.out_of_sample_trades),
            "yes" if r.accepted else "no",
        )
    console.print(table)


@research_app.command("collect")
def research_collect(
    symbols: str = typer.Option("BTC/USDT,ETH/USDT", help="Comma-separated pairs"),
    timeframe: str = typer.Option("1h", help="Bar timeframe"),
    bars: int = typer.Option(500, help="OHLCV bars per symbol"),
    flows: bool = typer.Option(True, help="Also ingest funding/OI/L-S"),
) -> None:
    """Incremental MDS ingest via DataLayer (requires RESEARCH_DB_ENABLED)."""
    from research_platform.collector.mds_collector import MdsCollector

    coll = MdsCollector()
    for sym in [s.strip() for s in symbols.split(",") if s.strip()]:
        out = coll.ingest_symbol_candles(sym, timeframe=timeframe, bars=bars)
        console.print(out)
        if flows:
            console.print(coll.ingest_flows(sym, timeframe=timeframe))


@research_app.command("dq-scan")
def research_dq_scan(
    symbol: str = typer.Option("BTC/USDT"),
    timeframe: str = typer.Option("1h"),
    bars: int = typer.Option(500),
) -> None:
    """Run OHLCV data quality scan (reporting only; uses live fetch)."""
    import json

    from engine.config import load_config
    from engine.data import DataLayer
    from research_platform.dq.scanner import scan_ohlcv_frame

    df = DataLayer(load_config()).get_ohlcv_history(symbol, timeframe, bars=bars, validate=False)
    report = scan_ohlcv_frame(df, symbol=symbol, timeframe=timeframe)
    console.print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    app()
