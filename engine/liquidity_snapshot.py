"""Current order-book liquidity snapshot (not historical replay)."""

from __future__ import annotations

from engine.config import load_config
from engine.data import DataLayer
from engine.lanes.structure import detect_walls


def liquidity_snapshot(symbol: str, book_limit: int = 200) -> dict:
    cfg = load_config()
    data = DataLayer(cfg)
    book = data.get_book(symbol, limit=book_limit)
    try:
        price = data.get_mid_price(symbol)
    except Exception:
        price = float(book["bids"][0][0]) if book.get("bids") else 0.0

    walls = detect_walls(book, price, symbol, cfg.structure)
    wall_rows = [
        {"side": w.side, "price": w.price, "notional_usd": round(w.notional_usd, 2)} for w in walls[:8]
    ]

    def top_levels(side: str, n: int = 8):
        levels = book.get(side, [])[:n]
        return [{"price": float(p), "amount": float(a), "notional_usd": round(float(p) * float(a), 2)} for p, a in levels]

    return {
        "symbol": symbol,
        "mid_price": price,
        "walls": wall_rows,
        "bids": top_levels("bids"),
        "asks": top_levels("asks"),
        "disclaimer": "Current book snapshot — walls may be spoofed; structure lane caps wall influence.",
    }
