"""파이프라인 실행 래퍼."""

import logging
from typing import Optional, List

from .config import GRAPH_RECURSION_LIMIT
from .db import init_db
from .graph import build_graph, PipelineState

logger = logging.getLogger(__name__)


def run_full_pipeline(
    option_ids: Optional[List[str]] = None,
    skip_processed: bool = True,
) -> None:
    """전체 파이프라인 실행."""
    logger.info("파이프라인 시작")

    # DB 초기화
    init_db()

    # 그래프 빌드
    graph = build_graph()

    # 초기 상태
    initial_state: PipelineState = {
        "options": [],
        "processed_option_ids": [],
        "current_option": None,
        "papers": [],
        "extracted_data": [],
        "logs": [],
    }

    # 특정 옵션만 처리하는 경우
    if option_ids:
        from .survey_options import get_all_options

        all_options = get_all_options()
        filtered_options = [opt for opt in all_options if opt["option_id"] in option_ids]
        initial_state["options"] = filtered_options
        logger.info(f"특정 옵션만 처리: {len(filtered_options)}개")

    # 이미 처리된 옵션 건너뛰기
    if skip_processed:
        from .db import get_db_session
        from .models import SurveyOption

        with get_db_session() as session:
            processed = session.query(SurveyOption.option_id).all()
            processed_ids = [row[0] for row in processed]
            initial_state["processed_option_ids"] = processed_ids
            logger.info(f"이미 처리된 옵션 {len(processed_ids)}개 건너뛰기")

    # 그래프 실행
    try:
        logger.info("그래프 실행 시작...")
        final_state = graph.invoke(
            initial_state,
            config={"recursion_limit": GRAPH_RECURSION_LIMIT},
        )

        # 로그 출력
        logs = final_state.get("logs", [])
        logger.info("=== 파이프라인 실행 로그 ===")
        for log in logs:
            logger.info(log)

        logger.info("파이프라인 완료")

    except Exception as e:
        logger.error(f"파이프라인 실행 중 오류: {e}", exc_info=True)
        raise


async def run_full_pipeline_async(
    option_ids: Optional[List[str]] = None,
    skip_processed: bool = True,
) -> None:
    """전체 파이프라인 실행 (비동기 버전)."""
    logger.info("파이프라인 시작 (비동기)")

    # DB 초기화
    init_db()

    # 그래프 빌드
    graph = build_graph()

    # 초기 상태
    initial_state: PipelineState = {
        "options": [],
        "processed_option_ids": [],
        "current_option": None,
        "papers": [],
        "extracted_data": [],
        "logs": [],
    }

    # 특정 옵션만 처리하는 경우
    if option_ids:
        from .survey_options import get_all_options

        all_options = get_all_options()
        filtered_options = [opt for opt in all_options if opt["option_id"] in option_ids]
        initial_state["options"] = filtered_options
        logger.info(f"특정 옵션만 처리: {len(filtered_options)}개")

    # 이미 처리된 옵션 건너뛰기
    if skip_processed:
        from .db import get_db_session
        from .models import SurveyOption

        with get_db_session() as session:
            processed = session.query(SurveyOption.option_id).all()
            processed_ids = [row[0] for row in processed]
            initial_state["processed_option_ids"] = processed_ids
            logger.info(f"이미 처리된 옵션 {len(processed_ids)}개 건너뛰기")

    # 그래프 실행 (비동기)
    try:
        logger.info("그래프 실행 시작 (비동기)...")
        final_state = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": GRAPH_RECURSION_LIMIT},
        )

        # 로그 출력
        logs = final_state.get("logs", [])
        logger.info("=== 파이프라인 실행 로그 ===")
        for log in logs:
            logger.info(log)

        logger.info("파이프라인 완료")

    except Exception as e:
        logger.error(f"파이프라인 실행 중 오류: {e}", exc_info=True)
        raise

