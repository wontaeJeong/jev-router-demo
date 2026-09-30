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


def load_config() -> Config:
    """Load .env.local from the working directory; environment takes precedence."""
    load_dotenv(".env.local", override=False)
    required = ["LLM_BASE_URL", "LLM_MODEL", "JEV_BASE_URL", "JEV_MODEL"]
    values = {key: os.getenv(key, "").strip() for key in required}
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise ValueError(
            "Missing configuration: " + ", ".join(missing)
            + "\nCopy .env.example to .env.local and configure the endpoints."
        )
    for key in ["LLM_BASE_URL", "JEV_BASE_URL"]:
        try:
            url = urlsplit(values[key])
            # Accessing port validates numeric value and range; splitting alone
            # accepts malformed ports that HTTPX would reject at request time.
            port = url.port
            if url.scheme not in {"http", "https"} or not url.hostname or port == 0:
                raise ValueError("invalid scheme, hostname or port")
        except ValueError as exc:
            raise ValueError(f"{key} must be a valid http:// or https:// endpoint URL: {exc}") from exc
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
    )
