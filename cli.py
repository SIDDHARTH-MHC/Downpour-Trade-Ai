#!/usr/bin/env python3
"""Downpour Trade AI — CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from engine.analyzer import analyze_symbol
from engine.backtest import run_backtest
from engine.calibration import rebuild_calibration
from engine.config import load_config

app = typer.Typer(name="downpour", help="Downpour Trade AI — deterministic crypto signal engine")
console = Console()


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


if __name__ == "__main__":
    app()
