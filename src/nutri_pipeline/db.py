"""DB 세션 생성 및 초기화 유틸리티."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from .config import DB_PATH
from .models import Base

logger = logging.getLogger(__name__)

# SQLite 엔진 생성
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},  # SQLite는 단일 스레드 기본
    echo=False,
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """데이터베이스 테이블 생성."""
    logger.info(f"데이터베이스 초기화: {DB_PATH}")
    Base.metadata.create_all(bind=engine)
    logger.info("테이블 생성 완료")


@contextmanager
def get_db_session() -> Session:
    """DB 세션 컨텍스트 매니저."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Session:
    """DB 세션 반환 (컨텍스트 매니저 없이 사용 시)."""
    return SessionLocal()

