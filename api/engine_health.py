"""Dependency probes for engine health."""

from __future__ import annotations

from datetime import datetime, timezone

from api.db import Database
from api.scheduler import calibration_status, scan_status
from engine.config import load_config
from engine.data import DataLayer


def probe_health() -> dict:
    db = Database()
    config = load_config()
    data = DataLayer(config)
    checks: dict[str, dict] = {}

    def ok(name: str, detail: str = "ok") -> None:
        checks[name] = {"status": "ok", "detail": detail}

    def fail(name: str, detail: str) -> None:
        checks[name] = {"status": "error", "detail": detail}

    try:
        data.get_ticker("BTC/USDT")
        ok("binance_spot")
    except Exception as exc:  # noqa: BLE001
        fail("binance_spot", str(exc))

    try:
        funding = data.get_funding("BTC/USDT")
        if funding.get("current"):
            ok("funding")
        else:
            fail("funding", "no current rate")
    except Exception as exc:  # noqa: BLE001
        fail("funding", str(exc))

    try:
        book = data.get_book("BTC/USDT", limit=20)
        if book.get("bids"):
            ok("order_book")
        else:
            fail("order_book", "empty book")
    except Exception as exc:  # noqa: BLE001
        fail("order_book", str(exc))

    try:
        snap = data.get_macro_snapshot()
        if snap.get("error"):
            fail("macro_coingecko", snap["error"])
        else:
            ok("macro_coingecko", snap.get("updated_at", "cached"))
    except Exception as exc:  # noqa: BLE001
        fail("macro_coingecko", str(exc))

    try:
        db.set_meta("_health_ping", datetime.now(timezone.utc).isoformat())
        ok("database")
    except Exception as exc:  # noqa: BLE001
        fail("database", str(exc))

    cal = calibration_status()
    checks["calibration"] = {
        "status": "ok" if not cal.get("last_error") else "warn",
        "detail": f"last={cal.get('last_calibrated_utc')} running={cal.get('running')}",
    }

    scan = scan_status()
    checks["scanner"] = {
        "status": "ok",
        "detail": f"last_scan={scan.get('last_scan_utc')} running={scan.get('running')}",
    }

    overall = "ok" if all(c.get("status") == "ok" for c in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}
