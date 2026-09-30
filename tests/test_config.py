import pytest

from jev_router_demo.config import load_config


KEYS = ["LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL", "JEV_BASE_URL", "JEV_MODEL", "REQUEST_TIMEOUT"]


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
