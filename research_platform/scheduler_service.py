"""Standalone research scheduler loop (optional; API scheduler also registers jobs)."""

from __future__ import annotations

import logging
import signal
import sys
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from research_platform.config import get_research_settings
from research_platform.jobs import (
    job_collect_historical_data,
    job_daily_data_quality_scan,
    job_weekly_walk_forward,
)

logger = logging.getLogger("downpour.research.scheduler")


def run_blocking_scheduler() -> None:
    settings = get_research_settings()
    if not settings.research_scheduler_enabled:
        raise SystemExit("Set RESEARCH_SCHEDULER_ENABLED=true")

    sched = BlockingScheduler(timezone="UTC")
    sched.add_job(
        job_collect_historical_data,
        "interval",
        hours=max(1, settings.research_collector_interval_hours),
        id="research_collector",
    )
    sched.add_job(
        job_daily_data_quality_scan,
        "cron",
        hour=settings.research_dq_hour_utc,
        id="research_dq_daily",
    )
    sched.add_job(
        job_weekly_walk_forward,
        "cron",
        day_of_week=settings.research_wf_day_of_week,
        hour=settings.research_wf_hour_utc,
        id="research_wf_weekly",
    )

    def _stop(_signum, _frame):
        sched.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    logger.info("research blocking scheduler started")
    sched.start()


def run_job_once(name: str) -> dict:
    jobs = {
        "collector": job_collect_historical_data,
        "dq": job_daily_data_quality_scan,
        "walk-forward": job_weekly_walk_forward,
    }
    fn = jobs.get(name)
    if fn is None:
        raise ValueError(f"Unknown job: {name}")
    return fn()
