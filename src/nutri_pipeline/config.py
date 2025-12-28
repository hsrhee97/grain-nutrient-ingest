"""환경변수 및 설정 관리."""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "nutri_papers.sqlite"

# 환경변수
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
CROSSREF_API_EMAIL = os.getenv("CROSSREF_API_EMAIL", "user@example.com")

# LLM 설정
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))

# 논문 검색 설정
MAX_PAPERS_PER_OPTION = int(os.getenv("MAX_PAPERS_PER_OPTION", "10"))

# LangGraph 설정
GRAPH_RECURSION_LIMIT = int(os.getenv("GRAPH_RECURSION_LIMIT", "200"))

# 로그 최대 길이 (메모리 보호용)
MAX_LOG_ENTRIES = int(os.getenv("MAX_LOG_ENTRIES", "500"))

# 데이터 디렉토리 생성
DATA_DIR.mkdir(parents=True, exist_ok=True)

