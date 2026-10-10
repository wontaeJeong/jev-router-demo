from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    label: str
    request: str
    expected_tiers: tuple[str, ...] = ()
    expected_web: bool | None = None
    expected_approval: bool | None = None
    summary: str | None = None
    category: str = "custom"
    recommended: bool = False


CATEGORIES = {"work": "업무·문서", "coding": "코딩·디버깅", "research": "최신 정보",
              "analysis": "분석·설계", "operations": "실행·변경"}
FILTERS = {"recommended": "추천 데모", "all": "전체 시나리오", **CATEGORIES}


def _request(name):
    return (Path(__file__).parent / "scenario_requests" / f"{name}.txt").read_text(encoding="utf-8").strip()


# Expectations are reference metadata only; routers never read or enforce them.
SCENARIOS = [
    Scenario(
        "Python 간단한 활용",
        _request("python-list"),
        ("fast",), False, False,
        "원본 리스트를 변경하지 않고 순서를 뒤집는 간단한 Python 방법과, 슬라이싱이 새 리스트를 만드는지 설명해 달라는 요청입니다.",
        "coding", True,
    ),
    Scenario(
        "FastAPI 동시성 오류",
        _request("fastapi-concurrency"),
        ("standard",), False, False,
        "동시 요청 시 간헐적으로 발생하는 HTTP 500 오류를 조사하고, 백그라운드 작업의 공유 딕셔너리 등 동시성 문제를 먼저 점검할 부분을 제안해 달라는 요청입니다.",
        "coding", True,
    ),
    Scenario(
        "vLLM / CUDA 호환성",
        _request("vllm-cuda"),
        ("standard", "reasoning"), True, False,
        "H100 환경을 CUDA 13으로 업그레이드하기 전에 최신 안정 버전 vLLM의 공식 지원 여부, 설치 제약과 컨테이너 이미지 변경 필요성을 확인해 달라는 요청입니다.",
        "research", True,
    ),
    Scenario(
        "저장소 구조 개선",
        _request("repository-refactor"),
        ("reasoning",), False, False,
        "저장소 구조를 분석해 인프라 연동과 핵심 도메인 로직을 분리하는 점진적 리팩터링 계획을 제안하되, 기존 호환성과 CLI 인터페이스를 유지해 달라는 요청입니다.",
        "analysis", True,
    ),
    Scenario(
        "운영 DB 정리",
        _request("production-db-delete"),
        ("standard",), False, True,
        "스테이징 마이그레이션 검증 후 운영 PostgreSQL에 연결해 legacy_users 테이블과 관련 인덱스를 삭제해 달라는 요청입니다.",
        "operations", True,
    ),
    Scenario(
        "Kubernetes 추론 성능 저하",
        _request("kubernetes-inference"),
        ("reasoning",), True, False,
        "새 Kubernetes 노드로 이전한 뒤 느려진 추론의 원인을 GPU·CUDA·이미지·vLLM 설정 및 최신 릴리스 노트와 비교해 분석하되, 클러스터는 변경하지 말라는 요청입니다.",
        "analysis",
    ),
    Scenario("회의록에서 할 일 추출", _request("meeting-actions"), ("fast", "standard"), False, False,
             "긴 회의록에 명시된 담당자·기한·할 일만 표로 추출하고, 결정되지 않은 내용은 추측하지 않는 요청입니다.", "work", True),
    Scenario("고객 안내 메일 초안", _request("customer-email"), ("standard",), False, False,
             "긴 고객 문의와 제공된 계약·지원 이력을 바탕으로 답장 초안을 작성하되, 메일 발송이나 환불 처리는 하지 않는 요청입니다.", "work"),
    Scenario("운영 안내 문서 번역", _request("document-translation"), ("fast", "standard"), False, False,
             "제공된 운영 안내 문서를 한국어로 번역하며 표·코드·고유 식별자는 유지하고, 새로운 정보를 조사하지 않는 요청입니다.", "work"),
    Scenario("로그를 JSON으로 변환", _request("log-format"), ("fast",), False, False,
             "긴 설명과 로그에서 지정된 세 줄만 정해진 JSON 형식으로 변환하며, 장애 원인 분석이나 시스템 변경은 하지 않는 요청입니다.", "coding"),
    Scenario("최신 API 요금 비교", _request("latest-pricing"), ("standard",), True, False,
             "실제 공급자의 최신 공식 API 요금과 과금 조건을 조사해 비용을 비교하되, 가입이나 결제는 하지 않는 요청입니다.", "research"),
    Scenario("최신 보안 공지 확인", _request("security-advisory"), ("standard", "reasoning"), True, False,
             "제공된 패키지 목록과 최신 공식 보안 공지를 대조해 영향과 대응 우선순위를 정리하되, 패키지를 업데이트하지 않는 요청입니다.", "research"),
    Scenario("제공된 요금표로 비용 계산", _request("supplied-pricing"), ("standard",), False, False,
             "요청에 포함된 가상 요금표와 사용량만으로 비용을 계산하며, 현재 실제 요금 조회나 구매 결정은 하지 않는 요청입니다.", "analysis"),
    Scenario("제약이 있는 출시 계획", _request("release-plan"), ("reasoning",), False, False,
             "일정·인력·의존성·제외 조건을 모두 고려해 출시 계획과 대안을 설계하되, 실제 배포나 티켓 수정은 하지 않는 요청입니다.", "analysis"),
    Scenario("운영 DB 삭제 계획 검토", _request("database-audit"), ("reasoning",), False, False,
             "제공된 스키마와 의존성 자료로 운영 DB 삭제 계획의 위험을 검토하되, 접속·SQL 실행·삭제는 명시적으로 금지한 요청입니다.", "analysis"),
    Scenario("운영 배포와 권한 변경", _request("production-deploy"), ("reasoning",), False, True,
             "제공된 배포 계획에 따라 운영 서비스를 실제 배포하고 서비스 계정 권한·트래픽 비율을 변경해 달라는 요청입니다.", "operations"),
]


def scenario_indices(category="recommended", query=""):
    query = query.strip().casefold()
    return [index for index, item in enumerate(SCENARIOS)
            if (category == "all" or category == "recommended" and item.recommended or item.category == category)
            and query in f"{item.label} {item.summary or ''}".casefold()]
