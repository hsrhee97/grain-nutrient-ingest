# 논문 영양소 추출 파이프라인

LangChain v1과 LangGraph v1을 사용한 논문 영양소 자동 추출 및 DB 저장 파이프라인입니다.

## 프로젝트 개요

잡곡/영양 관련 설문 보기(option) 목록을 입력으로 받아, 각 option에 대해 관련 학술 논문을 자동으로 검색/수집하고, 각 논문에서 "좋은 영양소(good_nutrients)" / "나쁜 영양소(bad_nutrients)"를 LLM으로 추출하여 구조화된 형태로 SQLite DB에 저장하는 파이프라인입니다.

## 기술 스택

- Python 3.11+
- LangChain v1
- LangGraph v1
- SQLAlchemy (SQLite)
- httpx (HTTP 클라이언트)
- OpenAI API

## 설치 방법

### 1. 가상환경 생성

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
cd grain_nutri_ingest
pip install -r requirements.txt

# 또는 개발 모드로 설치
pip install -e .
```

### 3. 환경변수 설정

`env.example` 파일을 참고하여 `.env` 파일을 생성하고 필요한 환경변수를 설정하세요:

```bash
# Windows PowerShell
Copy-Item env.example .env

# Linux/Mac
cp env.example .env

# .env 파일 편집 (OPENAI_API_KEY 필수)
# OPENAI_API_KEY=your_openai_api_key_here
# LLM_MODEL=gpt-4o-mini
# MAX_PAPERS_PER_OPTION=10
# GRAPH_RECURSION_LIMIT=200
```

## 사용 방법

### 기본 실행 (모든 옵션 처리)

```bash
python -m nutri_pipeline.cli run
```

### 특정 옵션만 처리

```bash
python -m nutri_pipeline.cli run --option-ids diabetes hypertension
```

### 이미 처리된 옵션도 다시 처리

```bash
python -m nutri_pipeline.cli run --no-skip-processed
```

## 프로젝트 구조

```
grain_nutri_ingest/
├── src/
│   └── nutri_pipeline/
│       ├── __init__.py
│       ├── config.py              # 환경변수 및 설정
│       ├── models.py              # SQLAlchemy ORM 모델
│       ├── db.py                  # DB 세션 관리
│       ├── survey_options.py     # 설문 옵션 정의
│       ├── paper_search.py        # 논문 검색 모듈
│       ├── nutrient_extractor.py # LLM 기반 영양소 추출
│       ├── graph.py               # LangGraph 그래프 정의
│       ├── pipeline.py            # 파이프라인 실행 래퍼
│       └── cli.py                 # 커맨드라인 진입점
├── data/                          # DB 파일 저장 위치
│   └── nutri_papers.sqlite
├── env.example                    # 환경변수 예시 파일
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 데이터베이스 스키마

### SurveyOption
- 설문 옵션 정보 저장

### Paper
- 논문 메타데이터 저장 (제목, URL, DOI, 초록 등)

### Nutrient
- 논문에서 추출된 영양소 정보 (좋은 영양소/나쁜 영양소 구분)

## 파이프라인 흐름

1. **load_options_node**: 설문 옵션 로드
2. **select_next_option_node**: 다음 처리할 옵션 선택
3. **search_papers_node**: 옵션에 대한 관련 논문 검색 (Semantic Scholar/CrossRef)
4. **extract_nutrients_node**: 각 논문에서 LLM으로 영양소 추출
5. **save_to_db_node**: DB에 저장
6. 모든 옵션 처리 완료까지 2-5 반복

## 논문 검색

기본적으로 Semantic Scholar API를 사용하며, 실패 시 CrossRef API를 대체로 사용합니다.

- Semantic Scholar API 키는 선택사항입니다 (무료 API 사용 가능)
- CrossRef API는 이메일 주소만 필요합니다

## 영양소 추출

OpenAI GPT 모델을 사용하여 논문의 제목과 초록에서 영양소를 추출합니다.

- 좋은 영양소(good_nutrients): 논문에서 긍정적으로 언급된 영양소
- 나쁜 영양소(bad_nutrients): 논문에서 부정적으로 언급되거나 부족하면 문제가 되는 영양소
- 각각 최대 5개까지 추출

## 라이선스

이 프로젝트는 내부 사용 목적으로 작성되었습니다.

