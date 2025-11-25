"""LangGraph v1 기반 파이프라인 그래프 정의."""

from typing import TypedDict, Annotated, Optional, List
from operator import add
import logging

from langgraph.graph import StateGraph, END

from .survey_options import get_all_options
from .paper_search import search_papers_for_option, PaperCandidate
from .nutrient_extractor import get_extractor
from .db import get_db_session
from .models import SurveyOption, Paper, Nutrient

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    """파이프라인 상태 정의."""

    options: List[dict]  # 모든 설문 옵션
    processed_option_ids: List[str]  # 이미 처리된 option_id 목록
    current_option: Optional[dict]  # 현재 처리 중인 option
    papers: List[PaperCandidate]  # 검색된 논문들
    extracted_data: List[dict]  # 추출된 영양소 데이터 (paper + nutrients)
    logs: Annotated[List[str], add]  # 진행 로그


def load_options_node(state: PipelineState) -> PipelineState:
    """설문 옵션을 로드하는 노드."""
    logger.info("설문 옵션 로드 중...")
    options = get_all_options()
    return {
        **state,
        "options": options,
        "processed_option_ids": state.get("processed_option_ids", []),
        "logs": state.get("logs", []) + [f"설문 옵션 {len(options)}개 로드 완료"],
    }


def select_next_option_node(state: PipelineState) -> PipelineState:
    """다음 처리할 옵션을 선택하는 노드."""
    options = state.get("options", [])
    processed_ids = state.get("processed_option_ids", [])

    # 아직 처리하지 않은 옵션 찾기
    next_option = None
    for option in options:
        if option["option_id"] not in processed_ids:
            next_option = option
            break

    if next_option:
        logger.info(f"다음 옵션 선택: {next_option['option_label']} ({next_option['option_id']})")
        return {
            **state,
            "current_option": next_option,
            "papers": [],
            "extracted_data": [],
            "logs": state.get("logs", []) + [f"옵션 선택: {next_option['option_label']}"],
        }
    else:
        logger.info("모든 옵션 처리 완료")
        return {
            **state,
            "current_option": None,
            "logs": state.get("logs", []) + ["모든 옵션 처리 완료"],
        }


def should_continue(state: PipelineState) -> str:
    """다음 노드로 진행할지 결정하는 조건 함수."""
    if state.get("current_option") is None:
        return "end"
    return "search_papers"


def search_papers_node(state: PipelineState) -> PipelineState:
    """논문 검색 노드."""
    current_option = state.get("current_option")
    if not current_option:
        return state

    logger.info(f"논문 검색 시작: {current_option['option_label']}")
    papers = search_papers_for_option(current_option)

    return {
        **state,
        "papers": papers,
        "logs": state.get("logs", []) + [f"논문 {len(papers)}개 검색 완료"],
    }


def extract_nutrients_node(state: PipelineState) -> PipelineState:
    """영양소 추출 노드."""
    papers = state.get("papers", [])
    if not papers:
        return state

    extractor = get_extractor()
    extracted_data = []

    for paper in papers:
        logger.info(f"영양소 추출 중: {paper.title[:50]}...")
        nutrients = extractor.extract_nutrients_from_paper(paper.title, paper.abstract)

        extracted_data.append(
            {
                "paper": paper,
                "nutrients": nutrients,
            }
        )

    logger.info(f"영양소 추출 완료: {len(extracted_data)}개 논문")
    return {
        **state,
        "extracted_data": extracted_data,
        "logs": state.get("logs", []) + [f"영양소 추출 완료: {len(extracted_data)}개 논문"],
    }


def save_to_db_node(state: PipelineState) -> PipelineState:
    """DB 저장 노드."""
    current_option = state.get("current_option")
    extracted_data = state.get("extracted_data", [])

    if not current_option or not extracted_data:
        return state

    try:
        with get_db_session() as session:
            # SurveyOption upsert
            option_record = session.query(SurveyOption).filter_by(option_id=current_option["option_id"]).first()
            if not option_record:
                option_record = SurveyOption(
                    question_id=current_option["question_id"],
                    question_label=current_option["question_label"],
                    option_id=current_option["option_id"],
                    option_label=current_option["option_label"],
                )
                session.add(option_record)
                session.flush()

            # Paper 및 Nutrient 저장
            saved_count = 0
            for item in extracted_data:
                paper_candidate = item["paper"]
                nutrients = item["nutrients"]

                # Paper upsert (DOI 기준)
                paper_record = None
                if paper_candidate.doi:
                    paper_record = session.query(Paper).filter_by(doi=paper_candidate.doi).first()

                if not paper_record:
                    paper_record = Paper(
                        option_id=current_option["option_id"],
                        title=paper_candidate.title,
                        url=paper_candidate.url,
                        source=paper_candidate.source,
                        doi=paper_candidate.doi,
                        abstract=paper_candidate.abstract,
                        raw_metadata=paper_candidate.raw_metadata,
                    )
                    session.add(paper_record)
                    session.flush()

                # Nutrient 저장 (기존 것 삭제 후 재생성)
                session.query(Nutrient).filter_by(paper_id=paper_record.id).delete()

                for nutrient_name in nutrients.get("good_nutrients", []):
                    nutrient = Nutrient(
                        paper_id=paper_record.id,
                        name=nutrient_name,
                        type="good",
                        extra_info=None,
                    )
                    session.add(nutrient)

                for nutrient_name in nutrients.get("bad_nutrients", []):
                    nutrient = Nutrient(
                        paper_id=paper_record.id,
                        name=nutrient_name,
                        type="bad",
                        extra_info=None,
                    )
                    session.add(nutrient)

                saved_count += 1

            session.commit()
            logger.info(f"DB 저장 완료: {saved_count}개 논문")

            # 처리된 옵션 ID 추가
            processed_ids = state.get("processed_option_ids", [])
            if current_option["option_id"] not in processed_ids:
                processed_ids.append(current_option["option_id"])

            return {
                **state,
                "processed_option_ids": processed_ids,
                "logs": state.get("logs", []) + [f"DB 저장 완료: {saved_count}개 논문"],
            }

    except Exception as e:
        logger.error(f"DB 저장 중 오류: {e}")
        return {
            **state,
            "logs": state.get("logs", []) + [f"DB 저장 오류: {str(e)}"],
        }


def build_graph() -> StateGraph:
    """LangGraph 그래프 빌드."""
    # 그래프 생성
    workflow = StateGraph(PipelineState)

    # 노드 추가
    workflow.add_node("load_options", load_options_node)
    workflow.add_node("select_next_option", select_next_option_node)
    workflow.add_node("search_papers", search_papers_node)
    workflow.add_node("extract_nutrients", extract_nutrients_node)
    workflow.add_node("save_to_db", save_to_db_node)

    # 엣지 설정
    workflow.set_entry_point("load_options")
    workflow.add_edge("load_options", "select_next_option")
    workflow.add_conditional_edges(
        "select_next_option",
        should_continue,
        {
            "search_papers": "search_papers",
            "end": END,
        },
    )
    workflow.add_edge("search_papers", "extract_nutrients")
    workflow.add_edge("extract_nutrients", "save_to_db")
    workflow.add_edge("save_to_db", "select_next_option")  # 루프

    # 그래프 컴파일
    app = workflow.compile()
    return app


def build_app() -> StateGraph:
    """앱 빌더 (build_graph의 별칭)."""
    return build_graph()

