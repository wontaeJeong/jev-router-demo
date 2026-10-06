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
    jev_api_mode: str = "systemone"
    jev_endpoint_url: str = ""
    jev_api_key: str = ""

    def __post_init__(self) -> None:
        # Ollama exposes System One; retain the old mode name as an alias.
        if self.jev_api_mode == "ollama":
            object.__setattr__(self, "jev_api_mode", "systemone")

    @property
    def jev_url(self) -> str:
        if self.jev_endpoint_url:
            return self.jev_endpoint_url
        path = {"systemone": "/v1/systemone", "decisions": "/alpha/decisions"}[self.jev_api_mode]
        return self.jev_base_url + path


def load_config() -> Config:
    """Load .env.local from the working directory; environment takes precedence."""
    load_dotenv(".env.local", override=False)
    mode = os.getenv("JEV_API_MODE", "systemone").strip().lower()
    if mode == "ollama":
        mode = "systemone"
    if mode not in {"ollama", "systemone", "decisions"}:
        raise ValueError("JEV_API_MODE must be systemone, decisions or ollama.")
    keys = ["LLM_BASE_URL", "LLM_MODEL", "JEV_BASE_URL", "JEV_MODEL", "JEV_ENDPOINT_URL", "JEV_API_KEY"]
    values = {key: os.getenv(key, "").strip() for key in keys}
    required = ["LLM_BASE_URL", "LLM_MODEL", "JEV_MODEL"]
    if not values["JEV_ENDPOINT_URL"]:
        required.append("JEV_BASE_URL")
    missing = [key for key in required if not values[key]]
    if missing:
        raise ValueError(
            "Missing configuration: " + ", ".join(missing)
            + "\nCopy .env.example to .env.local and configure the endpoints."
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
                raise ValueError("invalid scheme, hostname or port")
        except ValueError as exc:
            raise ValueError(f"{key} must be a valid http:// or https:// endpoint URL: {exc}") from exc
    endpoint_host = urlsplit(values["JEV_ENDPOINT_URL"] or values["JEV_BASE_URL"]).hostname
    if endpoint_host == "openrouter.ai" and not values["JEV_API_KEY"]:
        raise ValueError("Missing configuration: JEV_API_KEY is required for OpenRouter System One / Decisions.")
    try:
        timeout = float(os.getenv("REQUEST_TIMEOUT", "60"))
    except ValueError as exc:
        raise ValueError("REQUEST_TIMEOUT must be a positive number of seconds.") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("REQUEST_TIMEOUT must be a finite positive number of seconds.")
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
