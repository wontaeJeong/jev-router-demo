import os
import subprocess
import sys


def test_cli_missing_config_and_interactive_navigation(tmp_path):
    env = os.environ.copy()
    for key in ["LLM_BASE_URL", "LLM_MODEL", "JEV_BASE_URL", "JEV_MODEL", "LLM_API_KEY", "REQUEST_TIMEOUT", "JEV_API_MODE", "JEV_ENDPOINT_URL", "JEV_API_KEY"]:
        env.pop(key, None)
    command = [sys.executable, "-m", "jev_router_demo"]
    missing = subprocess.run(command, cwd=tmp_path, env=env, text=True, capture_output=True, timeout=10)
    assert missing.returncode == 1
    assert "필수 설정 누락" in missing.stdout
    assert "Traceback" not in missing.stdout + missing.stderr
    # Only configuration is provided; navigation must not trigger health calls.
    (tmp_path / ".env.local").write_text(
        "LLM_BASE_URL=http://127.0.0.1:1/v1\nLLM_MODEL=baseline\n"
        "JEV_BASE_URL=http://127.0.0.1:1\nJEV_MODEL=jev-like\nREQUEST_TIMEOUT=0.1\n"
    )
    session = subprocess.run(
        command, cwd=tmp_path, env=env, input="n\np\nv\n\ne\nCustom inspect request\no\n\nq\n",
        text=True, capture_output=True, timeout=10,
    )
    assert session.returncode == 0
    assert "FastAPI 동시성 오류" in session.stdout
    assert "Python 간단한 활용" in session.stdout
    assert "Custom inspect request" in session.stdout
    assert "먼저 요청을 실행" in session.stdout
    assert "Traceback" not in session.stdout + session.stderr


def test_cli_run_errors_remain_interactive(tmp_path):
    env = os.environ | {
        "LLM_BASE_URL": "http://127.0.0.1:1/v1", "LLM_MODEL": "baseline",
        "JEV_BASE_URL": "http://127.0.0.1:1", "JEV_MODEL": "jev",
        "REQUEST_TIMEOUT": "0.1", "LLM_API_KEY": "",
        "JEV_API_MODE": "ollama", "JEV_ENDPOINT_URL": "", "JEV_API_KEY": "",
    }
    result = subprocess.run(
        [sys.executable, "-m", "jev_router_demo"], cwd=tmp_path, env=env,
        input="r\no\n\nn\nq\n", text=True, capture_output=True, timeout=10,
    )
    assert result.returncode == 0
    assert "연결할 수 없습니다" in result.stdout
    assert "FastAPI 동시성 오류" in result.stdout
    assert "오류 수" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr
