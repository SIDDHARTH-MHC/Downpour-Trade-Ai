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
from api.routes.batch import router as batch_router
from api.routes.backtest_stats import router as backtest_router
from api.routes.calibrate import router as calibrate_router
from api.routes.confidence_history import router as confidence_history_router
from api.routes.flows import router as flows_router
from api.routes.macro import router as macro_router
from api.routes.health import router as health_router
from api.routes.history import router as history_router
from api.routes.trust import router as trust_router
from api.routes.pairs import router as pairs_router
from api.routes.scan import router as scan_router
from api.routes.alerts import router as alerts_router
from api.routes.coach import router as coach_router
from api.routes.compare import router as compare_router
from api.routes.context import router as context_router
from api.routes.copilot import router as copilot_router
from api.routes.integrations import router as integrations_router
from api.routes.journal import router as journal_router
from api.routes.portfolio import router as portfolio_router
from api.routes.replay import router as replay_router
from api.routes.status import router as status_router
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
        allow_origins=origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLogMiddleware)
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(health_router)
    app.include_router(analyze_router)
    app.include_router(batch_router)
    app.include_router(scan_router)
    app.include_router(history_router)
    app.include_router(backtest_router)
    app.include_router(calibrate_router)
    app.include_router(pairs_router)
    app.include_router(trust_router)
    app.include_router(confidence_history_router)
    app.include_router(flows_router)
    app.include_router(macro_router)
    app.include_router(status_router)
    app.include_router(replay_router)
    app.include_router(copilot_router)
    app.include_router(alerts_router)
    app.include_router(context_router)
    app.include_router(compare_router)
    app.include_router(coach_router)
    app.include_router(journal_router)
    app.include_router(portfolio_router)
    app.include_router(integrations_router)

    @app.get("/")
    def root() -> dict:
        return {"app": "Downpour Trade AI", "docs": "/docs"}

    return app


app = create_app()
