import pytest

from jev_router_demo.config import load_config


KEYS = ["LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL", "JEV_BASE_URL", "JEV_MODEL", "REQUEST_TIMEOUT", "JEV_API_MODE", "JEV_ENDPOINT_URL", "JEV_API_KEY"]


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    for key in KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_missing_config_is_readable(clean_env):
    with pytest.raises(ValueError, match="Missing configuration:.*LLM_BASE_URL"):
        load_config()


def test_dotenv_optional_key_and_environment_precedence(clean_env, monkeypatch):
    (clean_env / ".env.local").write_text(
        "LLM_BASE_URL=http://localhost:4000/v1/\nLLM_MODEL=baseline\n"
        "JEV_BASE_URL=http://localhost:11434\nJEV_MODEL=jev-like\nLLM_API_KEY=\n"
    )
    monkeypatch.setenv("LLM_MODEL", "override")
    config = load_config()
    assert config.llm_model == "override"
    assert config.llm_api_key == ""
    assert config.llm_base_url == "http://localhost:4000/v1"
    assert config.request_timeout == 60


@pytest.mark.parametrize("timeout", ["0", "-1", "nan", "inf", "oops"])
def test_invalid_timeout(clean_env, monkeypatch, timeout):
    for key in ["LLM_BASE_URL", "JEV_BASE_URL"]:
        monkeypatch.setenv(key, "http://localhost")
    for key in ["LLM_MODEL", "JEV_MODEL"]:
        monkeypatch.setenv(key, "model")
    monkeypatch.setenv("REQUEST_TIMEOUT", timeout)
    with pytest.raises(ValueError, match="REQUEST_TIMEOUT"):
        load_config()


@pytest.mark.parametrize("url", ["http://localhost:bad", "http://localhost:70000", "http://[broken"])
def test_invalid_endpoint_has_setting_name(clean_env, monkeypatch, url):
    monkeypatch.setenv("LLM_BASE_URL", url)
    monkeypatch.setenv("LLM_MODEL", "model")
    monkeypatch.setenv("JEV_BASE_URL", "http://localhost")
    monkeypatch.setenv("JEV_MODEL", "model")
    with pytest.raises(ValueError, match="LLM_BASE_URL"):
        load_config()


@pytest.mark.parametrize("mode", ["systemone", "decisions"])
def test_typed_mode_accepts_full_url_without_base(clean_env, monkeypatch, mode):
    settings = {"LLM_BASE_URL": "http://llm/v1", "LLM_MODEL": "baseline", "JEV_MODEL": "typesafe/jev-1.13",
                "JEV_API_MODE": mode, "JEV_ENDPOINT_URL": "https://openrouter.ai/api/alpha/decisions", "JEV_API_KEY": "test-key"}
    for key, value in settings.items():
        monkeypatch.setenv(key, value)
    config = load_config()
    assert config.jev_api_mode == mode
    assert config.jev_endpoint_url == "https://openrouter.ai/api/alpha/decisions"
    assert config.jev_base_url == ""


def test_unknown_api_mode_is_rejected(clean_env, monkeypatch):
    monkeypatch.setenv("JEV_API_MODE", "guess")
    with pytest.raises(ValueError, match="JEV_API_MODE"):
        load_config()


def test_openrouter_typed_endpoint_requires_its_own_key(clean_env, monkeypatch):
    for key, value in {"LLM_BASE_URL": "http://llm/v1", "LLM_MODEL": "baseline", "JEV_MODEL": "typesafe/jev-1.13",
                       "JEV_API_MODE": "systemone", "JEV_ENDPOINT_URL": "https://openrouter.ai/api/v1/systemone"}.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(ValueError, match="JEV_API_KEY"):
        load_config()
