import math
import os
from dataclasses import dataclass
from urllib.parse import urlsplit

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    llm_base_url: str
    llm_model: str
    jev_base_url: str
    jev_model: str
    llm_api_key: str = ""
    request_timeout: float = 60
    # Keep implicit legacy configurations compatible; new examples select System One.
    jev_api_mode: str = "ollama"
    jev_endpoint_url: str = ""
    jev_api_key: str = ""

    @property
    def jev_url(self) -> str:
        if self.jev_endpoint_url:
            return self.jev_endpoint_url
        path = {"ollama": "/api/generate", "systemone": "/v1/systemone", "decisions": "/alpha/decisions"}[self.jev_api_mode]
        return self.jev_base_url + path


def load_config() -> Config:
    """Load .env.local from the working directory; environment takes precedence."""
    load_dotenv(".env.local", override=False)
    mode = os.getenv("JEV_API_MODE", "ollama").strip().lower()
    if mode not in {"ollama", "systemone", "decisions"}:
        raise ValueError("JEV_API_MODE는 systemone, decisions, ollama 중 하나여야 합니다.")
    keys = ["LLM_BASE_URL", "LLM_MODEL", "JEV_BASE_URL", "JEV_MODEL", "JEV_ENDPOINT_URL", "JEV_API_KEY"]
    values = {key: os.getenv(key, "").strip() for key in keys}
    required = ["LLM_BASE_URL", "LLM_MODEL", "JEV_MODEL"]
    if not values["JEV_ENDPOINT_URL"]:
        required.append("JEV_BASE_URL")
    missing = [key for key in required if not values[key]]
    if missing:
        raise ValueError(
            "필수 설정 누락: " + ", ".join(missing)
            + "\n.env.example을 .env.local로 복사하고 엔드포인트를 설정해 주세요."
        )
    for key in ["LLM_BASE_URL", "JEV_BASE_URL", "JEV_ENDPOINT_URL"]:
        if not values[key]:
            continue
        try:
            url = urlsplit(values[key])
            # Accessing port validates numeric value and range; splitting alone
            # accepts malformed ports that HTTPX would reject at request time.
            port = url.port
            if url.scheme not in {"http", "https"} or not url.hostname or port == 0:
                raise ValueError("프로토콜, 호스트 이름 또는 포트가 잘못되었습니다")
        except ValueError as exc:
            raise ValueError(f"{key}에 유효한 http:// 또는 https:// 엔드포인트 URL을 지정해 주세요: {exc}") from exc
    endpoint_host = urlsplit(values["JEV_ENDPOINT_URL"] or values["JEV_BASE_URL"]).hostname
    if mode != "ollama" and endpoint_host == "openrouter.ai" and not values["JEV_API_KEY"]:
        raise ValueError("필수 설정 누락: OpenRouter System One / Decisions에는 JEV_API_KEY가 필요합니다.")
    try:
        timeout = float(os.getenv("REQUEST_TIMEOUT", "60"))
    except ValueError as exc:
        raise ValueError("REQUEST_TIMEOUT은 양수인 시간(초)이어야 합니다.") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("REQUEST_TIMEOUT은 유한한 양수인 시간(초)이어야 합니다.")
    return Config(
        llm_base_url=values["LLM_BASE_URL"].rstrip("/"),
        llm_model=values["LLM_MODEL"],
        jev_base_url=values["JEV_BASE_URL"].rstrip("/"),
        jev_model=values["JEV_MODEL"],
        llm_api_key=os.getenv("LLM_API_KEY", "").strip(),
        request_timeout=timeout,
        jev_api_mode=mode,
        jev_endpoint_url=values["JEV_ENDPOINT_URL"],
        jev_api_key=values["JEV_API_KEY"],
    )
