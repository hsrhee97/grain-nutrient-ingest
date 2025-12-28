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
논문의 제목과 초록(또는 제목만)을 분석하여 영양소를 추출하세요.

중요 규칙:
1. 제목과 초록에서 언급된 영양소, 비타민, 미네랄, 식이섬유, 항산화물질 등을 찾으세요
2. good_nutrients: 논문에서 긍정적으로 언급되거나 건강에 도움이 되는 영양소 (예: fiber, vitamin C, iron, calcium, omega-3, antioxidants 등) - 최대 5개
3. bad_nutrients: 논문에서 부정적으로 언급되거나 과다 섭취 시 문제가 되는 영양소 (예: saturated fat, cholesterol, sodium, trans fat 등) - 최대 5개
4. 제목만 있어도 제목에서 추론 가능한 영양소를 추출하세요
5. 영양소 이름은 영어로 표준 용어를 사용하세요 (예: "fiber" not "fibre", "vitamin C" not "vit C")
6. 논문이 잡곡(whole grain) 관련이면 일반적인 잡곡 영양소도 포함 가능합니다

출력 형식은 JSON이어야 합니다.""",
                ),
                (
                    "human",
                    """다음 논문의 제목과 초록을 분석하여 영양소를 추출하세요:

제목: {title}

초록:
{abstract}

JSON 형식으로 good_nutrients와 bad_nutrients를 반환하세요. 각각 최대 5개까지 추출하세요.""",
                ),
            ]
        )

        # 체인 구성
        self.chain = self.prompt | self.llm.with_structured_output(NutrientList)

    def extract_nutrients_from_paper(self, title: str, abstract: Optional[str] = None) -> Dict[str, List[str]]:
        """논문에서 영양소 추출."""
        # 초록이 없거나 너무 짧으면 제목만으로 추출 시도
        if not abstract or len(abstract.strip()) < 20:
            abstract = "초록 정보 없음. 제목만으로 분석해주세요."
            logger.warning(f"초록이 없거나 짧음. 제목만으로 추출 시도: '{title[:50]}...'")
        else:
            logger.info(f"영양소 추출 중: '{title[:50]}...'")

        try:
            result = self.chain.invoke({"title": title, "abstract": abstract})

            # Pydantic 모델을 dict로 변환
            nutrients = {
                "good_nutrients": result.good_nutrients if result.good_nutrients else [],
                "bad_nutrients": result.bad_nutrients if result.bad_nutrients else [],
            }

            # 결과가 비어있으면 재시도 (더 적극적인 프롬프트로)
            if not nutrients["good_nutrients"] and not nutrients["bad_nutrients"]:
                logger.warning(f"영양소 추출 실패, 재시도 중: '{title[:50]}...'")
                # 재시도 시 더 적극적인 프롬프트 사용
                retry_prompt = ChatPromptTemplate.from_messages([
                    ("system", "당신은 영양학 논문 분석 전문가입니다. 제목과 초록에서 영양소를 적극적으로 찾아주세요. 잡곡(whole grain) 논문이라면 일반적인 잡곡 영양소(fiber, B vitamins, minerals 등)도 포함하세요."),
                    ("human", "제목: {title}\n초록: {abstract}\n\n이 논문에서 언급되거나 추론 가능한 영양소를 찾아주세요. good_nutrients와 bad_nutrients를 JSON 형식으로 반환하세요.")
                ])
                retry_chain = retry_prompt | self.llm.with_structured_output(NutrientList)
                retry_result = retry_chain.invoke({"title": title, "abstract": abstract})
                nutrients = {
                    "good_nutrients": retry_result.good_nutrients if retry_result.good_nutrients else [],
                    "bad_nutrients": retry_result.bad_nutrients if retry_result.bad_nutrients else [],
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

