"""설문 보기(option) 정의."""

from typing import List, Dict

survey_options: List[Dict[str, str]] = [
    {
        "question_id": "gender",
        "question_label": "주 섭취 대상 성별",
        "option_id": "male_major",
        "option_label": "남 위주",
    },
    {
        "question_id": "gender",
        "question_label": "주 섭취 대상 성별",
        "option_id": "female_major",
        "option_label": "여 위주",
    },
    {
        "question_id": "gender",
        "question_label": "주 섭취 대상 성별",
        "option_id": "mixed",
        "option_label": "혼성",
    },
    {
        "question_id": "gender",
        "question_label": "주 섭취 대상 성별",
        "option_id": "pregnant",
        "option_label": "임산부",
    },
    {
        "question_id": "age",
        "question_label": "주 섭취 대상 나이",
        "option_id": "age_0_10",
        "option_label": "0~10대",
    },
    {
        "question_id": "age",
        "question_label": "주 섭취 대상 나이",
        "option_id": "age_20_30",
        "option_label": "20-30대",
    },
    {
        "question_id": "age",
        "question_label": "주 섭취 대상 나이",
        "option_id": "age_40_50",
        "option_label": "40~50대",
    },
    {
        "question_id": "age",
        "question_label": "주 섭취 대상 나이",
        "option_id": "age_60_plus",
        "option_label": "60대 이상",
    },
    {
        "question_id": "texture",
        "question_label": "선호식감",
        "option_id": "dry_rice",
        "option_label": "고슬밥",
    },
    {
        "question_id": "texture",
        "question_label": "선호식감",
        "option_id": "sticky_rice",
        "option_label": "찰진밥",
    },
    {
        "question_id": "texture",
        "question_label": "선호식감",
        "option_id": "no_beans",
        "option_label": "콩없는 밥",
    },
    {
        "question_id": "texture",
        "question_label": "선호식감",
        "option_id": "no_preference",
        "option_label": "선호없음",
    },
    {
        "question_id": "disease",
        "question_label": "질병 보유",
        "option_id": "diabetes",
        "option_label": "당뇨병",
    },
    {
        "question_id": "disease",
        "question_label": "질병 보유",
        "option_id": "hypertension",
        "option_label": "고혈압",
    },
    {
        "question_id": "disease",
        "question_label": "질병 보유",
        "option_id": "cancer_prevention",
        "option_label": "암 예방",
    },
    {
        "question_id": "disease",
        "question_label": "질병 보유",
        "option_id": "none",
        "option_label": "해당 없음",
    },
    {
        "question_id": "constitution1",
        "question_label": "체질 개선1",
        "option_id": "obesity",
        "option_label": "비만",
    },
    {
        "question_id": "constitution1",
        "question_label": "체질 개선1",
        "option_id": "fatigue",
        "option_label": "피로 회복",
    },
    {
        "question_id": "constitution1",
        "question_label": "체질 개선1",
        "option_id": "inflammation",
        "option_label": "체내 염증 감소",
    },
    {
        "question_id": "constitution1",
        "question_label": "체질 개선1",
        "option_id": "antioxidant",
        "option_label": "항산화",
    },
    {
        "question_id": "constitution1",
        "question_label": "체질 개선1",
        "option_id": "none",
        "option_label": "해당 없음",
    },
    {
        "question_id": "constitution2",
        "question_label": "체질 개선2",
        "option_id": "constipation",
        "option_label": "변비",
    },
    {
        "question_id": "constitution2",
        "question_label": "체질 개선2",
        "option_id": "immunity",
        "option_label": "면역 강화",
    },
    {
        "question_id": "constitution2",
        "question_label": "체질 개선2",
        "option_id": "liver",
        "option_label": "간 건강",
    },
    {
        "question_id": "constitution2",
        "question_label": "체질 개선2",
        "option_id": "cholesterol",
        "option_label": "혈중 콜레스테롤",
    },
    {
        "question_id": "constitution2",
        "question_label": "체질 개선2",
        "option_id": "none",
        "option_label": "해당 없음",
    },
    {
        "question_id": "expected_effect",
        "question_label": "효과 기대",
        "option_id": "osteoporosis",
        "option_label": "골다공증",
    },
    {
        "question_id": "expected_effect",
        "question_label": "효과 기대",
        "option_id": "dementia",
        "option_label": "치매 예방",
    },
    {
        "question_id": "expected_effect",
        "question_label": "효과 기대",
        "option_id": "insomnia",
        "option_label": "불면증",
    },
    {
        "question_id": "expected_effect",
        "question_label": "효과 기대",
        "option_id": "none",
        "option_label": "해당 없음",
    },
]


def get_all_options() -> List[Dict[str, str]]:
    """모든 설문 옵션 반환."""
    return survey_options


def get_option_by_id(option_id: str) -> Dict[str, str] | None:
    """option_id로 옵션 조회."""
    for option in survey_options:
        if option["option_id"] == option_id:
            return option
    return None

