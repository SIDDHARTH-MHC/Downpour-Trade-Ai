"""Session scope for research DB operations."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session, sessionmaker

from research_platform.db.engine import get_research_engine

_session_factory: sessionmaker[Session] | None = None


def _get_session_factory() -> sessionmaker[Session] | None:
    global _session_factory
    engine = get_research_engine()
    if engine is None:
        return None
    if _session_factory is None:
        _session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return _session_factory


@contextmanager
def research_session() -> Iterator[Session | None]:
    factory = _get_session_factory()
    if factory is None:
        yield None
        return
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
