"""논문 검색 및 메타데이터 수집 모듈."""

from dataclasses import dataclass
from typing import List, Dict, Optional
import httpx
import logging
from .config import SEMANTIC_SCHOLAR_API_KEY, CROSSREF_API_EMAIL, MAX_PAPERS_PER_OPTION

logger = logging.getLogger(__name__)


@dataclass
class PaperCandidate:
    """논문 후보 데이터 클래스."""

    title: str
    url: str
    doi: Optional[str] = None
    abstract: Optional[str] = None
    source: str = "semantic_scholar"
    raw_metadata: Optional[Dict] = None


def build_search_query(option: Dict[str, str]) -> str:
    """옵션 정보를 기반으로 검색 쿼리 생성."""
    option_label = option.get("option_label", "")
    question_label = option.get("question_label", "")

    # 한국어 키워드를 영어로 변환하는 간단한 매핑 (실제로는 더 정교한 변환이 필요할 수 있음)
    keyword_map = {
        "남 위주": "male",
        "여 위주": "female",
        "임산부": "pregnant",
        "0~10대": "children",
        "20-30대": "young adults",
        "40~50대": "middle-aged",
        "60대 이상": "elderly",
        "고슬밥": "dry rice",
        "찰진밥": "sticky rice",
        "콩없는 밥": "rice without beans",
        "당뇨병": "diabetes",
        "고혈압": "hypertension",
        "암 예방": "cancer prevention",
        "비만": "obesity",
        "피로 회복": "fatigue recovery",
        "체내 염증 감소": "inflammation reduction",
        "항산화": "antioxidant",
        "변비": "constipation",
        "면역 강화": "immune enhancement",
        "간 건강": "liver health",
        "혈중 콜레스테롤": "cholesterol",
        "골다공증": "osteoporosis",
        "치매 예방": "dementia prevention",
        "불면증": "insomnia",
    }

    # 기본 쿼리: 잡곡/영양 관련
    base_query = "whole grain nutrition"
    translated_keyword = keyword_map.get(option_label, option_label)

    # 검색 쿼리 조합
    query = f"{base_query} {translated_keyword}"
    return query


def search_semantic_scholar(query: str, max_results: int = 10) -> List[PaperCandidate]:
    """Semantic Scholar API를 사용한 논문 검색."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

    params = {
        "query": query,
        "limit": min(max_results, 100),
        "fields": "title,url,doi,abstract,authors,year",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        papers = []
        for item in data.get("data", [])[:max_results]:
            paper = PaperCandidate(
                title=item.get("title", ""),
                url=item.get("url", ""),
                doi=item.get("doi"),
                abstract=item.get("abstract"),
                source="semantic_scholar",
                raw_metadata=item,
            )
            papers.append(paper)

        logger.info(f"Semantic Scholar에서 {len(papers)}개 논문 검색: '{query}'")
        return papers

    except httpx.HTTPError as e:
        logger.error(f"Semantic Scholar API 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"논문 검색 중 예외 발생: {e}")
        return []


def search_crossref(query: str, max_results: int = 10) -> List[PaperCandidate]:
    """CrossRef API를 사용한 논문 검색 (대체 옵션)."""
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": min(max_results, 100),
        "mailto": CROSSREF_API_EMAIL,
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        papers = []
        for item in data.get("message", {}).get("items", [])[:max_results]:
            # DOI URL 생성
            doi = item.get("DOI")
            url_str = f"https://doi.org/{doi}" if doi else ""

            paper = PaperCandidate(
                title=" ".join(item.get("title", [])),
                url=url_str,
                doi=doi,
                abstract=None,  # CrossRef는 초록을 직접 제공하지 않음
                source="crossref",
                raw_metadata=item,
            )
            papers.append(paper)

        logger.info(f"CrossRef에서 {len(papers)}개 논문 검색: '{query}'")
        return papers

    except httpx.HTTPError as e:
        logger.error(f"CrossRef API 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"논문 검색 중 예외 발생: {e}")
        return []


def search_papers_for_option(option: Dict[str, str], max_results: int = None) -> List[PaperCandidate]:
    """옵션에 대한 관련 논문 검색."""
    if max_results is None:
        max_results = MAX_PAPERS_PER_OPTION

    query = build_search_query(option)
    logger.info(f"옵션 '{option.get('option_label')}'에 대한 논문 검색: '{query}'")

    # Semantic Scholar 우선 사용, 실패 시 CrossRef 시도
    papers = search_semantic_scholar(query, max_results)
    if not papers:
        logger.warning("Semantic Scholar 검색 실패, CrossRef 시도...")
        papers = search_crossref(query, max_results)

    return papers

