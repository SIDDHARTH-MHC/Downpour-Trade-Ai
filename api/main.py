from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.limiter import limiter
from api.db import Database
from api.middleware import RequestLogMiddleware
from api.routes.analyze import router as analyze_router
from api.routes.backtest_stats import router as backtest_router
from api.routes.health import router as health_router
from api.routes.history import router as history_router
from api.routes.pairs import router as pairs_router
from api.routes.scan import router as scan_router
from api.scheduler import start_scheduler, stop_scheduler
from api.settings import get_settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database()
    db.init()
    start_scheduler()
    yield
    stop_scheduler()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLogMiddleware)
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(health_router)
    app.include_router(analyze_router)
    app.include_router(scan_router)
    app.include_router(history_router)
    app.include_router(backtest_router)
    app.include_router(pairs_router)

    @app.get("/")
    def root() -> dict:
        return {"app": "Downpour Trade AI", "docs": "/docs"}

    return app


app = create_app()
