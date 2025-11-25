"""커맨드라인 진입점."""

import argparse
import logging
import sys
from .pipeline import run_full_pipeline

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def main():
    """메인 CLI 함수."""
    parser = argparse.ArgumentParser(description="논문 영양소 추출 파이프라인")
    parser.add_argument(
        "command",
        choices=["run"],
        help="실행할 명령어",
    )
    parser.add_argument(
        "--option-ids",
        nargs="+",
        help="처리할 특정 option_id 목록 (지정하지 않으면 모든 옵션 처리)",
    )
    parser.add_argument(
        "--no-skip-processed",
        action="store_true",
        help="이미 처리된 옵션도 다시 처리",
    )

    args = parser.parse_args()

    if args.command == "run":
        try:
            run_full_pipeline(
                option_ids=args.option_ids,
                skip_processed=not args.no_skip_processed,
            )
            logger.info("프로그램 종료")
        except KeyboardInterrupt:
            logger.info("사용자에 의해 중단됨")
            sys.exit(1)
        except Exception as e:
            logger.error(f"오류 발생: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    main()

