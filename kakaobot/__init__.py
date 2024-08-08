import logging

logging.basicConfig(
    level=logging.INFO,  # 로깅의 기본 수준을 INFO로 설정
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 로그 메시지 형식 설정
    handlers=[
        logging.FileHandler("library.log"),  # 로그를 파일에 저장
        logging.StreamHandler()  # 로그를 콘솔에도 출력
    ]
)

logger = logging.getLogger(__name__)  # 로거 인스턴스를 만듦
