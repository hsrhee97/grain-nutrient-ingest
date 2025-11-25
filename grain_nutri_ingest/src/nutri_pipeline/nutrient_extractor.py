"""LLM 기반 영양소 추출 모듈 (LangChain v1 사용)."""

from typing import Dict, List, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from .config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE

logger = logging.getLogger(__name__)


class NutrientList(BaseModel):
    """영양소 리스트 스키마."""

    good_nutrients: List[str] = Field(
        description="논문에서 언급된 좋은 영양소 목록 (최대 5개, 실제로 논문에 언급된 것만)"
    )
    bad_nutrients: List[str] = Field(
        description="논문에서 언급된 나쁜 영양소 목록 (최대 5개, 실제로 논문에 언급된 것만)"
    )


class NutrientExtractor:
    """영양소 추출기 클래스."""

    def __init__(self):
        """초기화."""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            api_key=OPENAI_API_KEY,
        )

        # 구조화된 출력 파서
        self.parser = JsonOutputParser(pydantic_object=NutrientList)

        # 프롬프트 템플릿
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 영양학 논문을 분석하는 전문가입니다.
논문의 제목과 초록을 읽고, 논문에서 실제로 언급된 영양소만 추출하세요.

중요 규칙:
1. 논문에서 실제로 언급된 영양소만 추출 (추측하지 마세요)
2. good_nutrients: 논문에서 긍정적으로 언급된 영양소 (최대 5개)
3. bad_nutrients: 논문에서 부정적으로 언급되거나 부족하면 문제가 되는 영양소 (최대 5개)
4. 없으면 빈 배열로 반환
5. 영양소 이름은 논문에서 사용된 정확한 용어를 사용하세요

출력 형식은 JSON이어야 합니다.""",
                ),
                (
                    "human",
                    """다음 논문의 제목과 초록을 분석하여 영양소를 추출하세요:

제목: {title}

초록:
{abstract}

JSON 형식으로 good_nutrients와 bad_nutrients를 반환하세요.""",
                ),
            ]
        )

        # 체인 구성
        self.chain = self.prompt | self.llm.with_structured_output(NutrientList)

    def extract_nutrients_from_paper(self, title: str, abstract: Optional[str] = None) -> Dict[str, List[str]]:
        """논문에서 영양소 추출."""
        if not abstract:
            abstract = "초록 정보 없음"

        try:
            logger.info(f"영양소 추출 중: '{title[:50]}...'")
            result = self.chain.invoke({"title": title, "abstract": abstract})

            # Pydantic 모델을 dict로 변환
            nutrients = {
                "good_nutrients": result.good_nutrients if result.good_nutrients else [],
                "bad_nutrients": result.bad_nutrients if result.bad_nutrients else [],
            }

            logger.info(
                f"추출 완료 - 좋은 영양소: {len(nutrients['good_nutrients'])}개, "
                f"나쁜 영양소: {len(nutrients['bad_nutrients'])}개"
            )
            return nutrients

        except Exception as e:
            logger.error(f"영양소 추출 중 오류 발생: {e}")
            return {"good_nutrients": [], "bad_nutrients": []}


# 전역 인스턴스 (필요시)
_extractor_instance: Optional[NutrientExtractor] = None


def get_extractor() -> NutrientExtractor:
    """영양소 추출기 싱글톤 인스턴스 반환."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = NutrientExtractor()
    return _extractor_instance


def extract_nutrients_from_paper(title: str, abstract: Optional[str] = None) -> Dict[str, List[str]]:
    """논문에서 영양소 추출 (편의 함수)."""
    extractor = get_extractor()
    return extractor.extract_nutrients_from_paper(title, abstract)

