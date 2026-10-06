"""Korean display labels; API values and original payloads stay unchanged."""

TIERS = {"fast": "빠른 처리", "standard": "일반 처리", "reasoning": "심층 추론"}
STATES = {"idle": "대기", "running": "라우팅 중", "success": "완료", "error": "오류", "cancelled": "중단"}
FIELDS = {"model_tier": "모델 등급", "needs_web": "웹 검색", "needs_approval": "사용자 승인"}
OUTPUT_KINDS = {"generated": "텍스트 생성", "typed": "구조화된 결정", "unknown": "알 수 없음"}


def tier_label(value: str) -> str:
    return TIERS.get(value.lower(), value)


def candidate_label(field: str, value: str) -> str:
    if field == "model_tier":
        return tier_label(value)
    return {"true": "필요", "false": "불필요"}.get(value.lower(), value)
