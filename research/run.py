"""CLI: python -m research.run walk-forward --variant T3 --symbols BTC/USDT,ETH/USDT"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from research.runner import compare_r0_variants, run_r0_walk_forward
from research.variants import R0_VARIANTS

app = typer.Typer(name="research", help="Research experiments (walk-forward before promotion)")
console = Console()


@app.command("walk-forward")
def walk_forward_cmd(
    variant: str = typer.Option("T3", help=f"R0 variant: {', '.join(R0_VARIANTS)}"),
    symbols: str = typer.Option("BTC/USDT,ETH/USDT", help="Comma-separated pairs"),
    months: int = typer.Option(12, "--months", min=1, max=18),
    compare: bool = typer.Option(False, "--compare", help="Run all R0 variants for each symbol"),
) -> None:
    """Walk-forward OOS evaluation for EXP-R0 (technical orthogonalization)."""
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    if compare:
        console.print(f"[bold]R0 compare[/bold] — {months}m — {', '.join(sym_list)}")
        results = compare_r0_variants(sym_list, months=months)
    else:
        results = [run_r0_walk_forward(variant, sym, months) for sym in sym_list]

    table = Table(title="Walk-forward results")
    table.add_column("Variant")
    table.add_column("Symbol")
    table.add_column("OOS PF", justify="right")
    table.add_column("OOS trades", justify="right")
    table.add_column("WF pass")
    table.add_column("config_hash")
    for r in results:
        table.add_row(
            r.variant,
            r.symbol,
            f"{r.out_of_sample_profit_factor:.3f}",
            str(r.out_of_sample_trades),
            "yes" if r.accepted else "no",
            r.config_hash,
        )
    console.print(table)


if __name__ == "__main__":
    app()
