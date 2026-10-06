from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    label: str
    request: str
    expected_tiers: tuple[str, ...] = ()
    expected_web: bool | None = None
    expected_approval: bool | None = None
    summary: str | None = None


# Expectations are reference metadata only; routers never read or enforce them.
SCENARIOS = [
    Scenario(
        "Python 간단한 활용",
        "I'm working on a small Python utility and need to reverse a list "
        "without modifying the original object. Please show me the simplest "
        "idiomatic Python approach and briefly explain whether slicing creates "
        "a new list or mutates the existing one.",
        ("fast",), False, False,
        "원본 리스트를 변경하지 않고 순서를 뒤집는 간단한 Python 방법과, 슬라이싱이 새 리스트를 만드는지 설명해 달라는 요청입니다.",
    ),
    Scenario(
        "FastAPI 동시성 오류",
        "Our FastAPI service occasionally returns HTTP 500 when several clients "
        "submit requests at the same time. The stack trace points to a shared "
        "dictionary used by a background task, but the issue cannot be reproduced "
        "consistently. Review the symptoms and suggest what parts of the code "
        "should be inspected first to identify a possible concurrency problem.",
        ("standard",), False, False,
        "동시 요청 시 간헐적으로 발생하는 HTTP 500 오류를 조사하고, 백그라운드 작업의 공유 딕셔너리 등 동시성 문제를 먼저 점검할 부분을 제안해 달라는 요청입니다.",
    ),
    Scenario(
        "vLLM / CUDA 호환성",
        "We currently run vLLM on H100 GPUs and are planning to upgrade the host "
        "environment to CUDA 13. Check whether the latest stable vLLM release "
        "officially supports CUDA 13, identify any relevant installation "
        "constraints, and tell me whether an image upgrade would likely be "
        "required.",
        ("standard", "reasoning"), True, False,
        "H100 환경을 CUDA 13으로 업그레이드하기 전에 최신 안정 버전 vLLM의 공식 지원 여부, 설치 제약과 컨테이너 이미지 변경 필요성을 확인해 달라는 요청입니다.",
    ),
    Scenario(
        "저장소 구조 개선",
        "Analyze the architecture of this repository and propose a refactoring "
        "plan that separates infrastructure-specific integrations from the core "
        "domain logic. Preserve backward compatibility, avoid changing the public "
        "CLI interface, and prioritize changes that can be implemented "
        "incrementally without blocking existing development.",
        ("reasoning",), False, False,
        "저장소 구조를 분석해 인프라 연동과 핵심 도메인 로직을 분리하는 점진적 리팩터링 계획을 제안하되, 기존 호환성과 CLI 인터페이스를 유지해 달라는 요청입니다.",
    ),
    Scenario(
        "운영 DB 정리",
        "The staging migration has already been verified and I now want to clean "
        "up the production database. Connect to the production PostgreSQL instance, "
        "drop the legacy_users table, and remove any related indexes so we don't "
        "need to maintain the old schema anymore.",
        ("standard",), False, True,
        "스테이징 마이그레이션 검증 후 운영 PostgreSQL에 연결해 legacy_users 테이블과 관련 인덱스를 삭제해 달라는 요청입니다.",
    ),
    Scenario(
        "Kubernetes 추론 성능 저하",
        "We're seeing significantly slower inference after moving our model "
        "serving workload to a new Kubernetes node. Compare the current GPU, "
        "CUDA, container image, vLLM configuration, and recent release notes, "
        "then determine whether the slowdown is more likely caused by our "
        "deployment configuration or by a known software regression. "
        "Do not make any changes to the cluster.",
        ("reasoning",), True, False,
        "새 Kubernetes 노드로 이전한 뒤 느려진 추론의 원인을 GPU·CUDA·이미지·vLLM 설정 및 최신 릴리스 노트와 비교해 분석하되, 클러스터는 변경하지 말라는 요청입니다.",
    ),
]
