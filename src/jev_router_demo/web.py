import asyncio
import json
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from jev_router_demo.config import Config
from jev_router_demo.scenarios import SCENARIOS
from jev_router_demo.session import DemoSession


class RunCommand(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    type: Literal["run"]
    request: str
    scenario_id: int | None = None

    @field_validator("request")
    @classmethod
    def nonempty(cls, value):
        if not value.strip():
            raise ValueError("요청 내용을 입력해 주세요")
        return value

    @field_validator("scenario_id")
    @classmethod
    def valid_scenario(cls, value):
        if value is not None and not 0 <= value < len(SCENARIOS):
            raise ValueError("알 수 없는 시나리오입니다")
        return value


def create_app(config: Config, client: httpx.AsyncClient | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        app.state.client = client or httpx.AsyncClient()
        try:
            yield
        finally:
            if client is None:
                await app.state.client.aclose()

    app = FastAPI(lifespan=lifespan)
    static = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static), name="static")

    @app.get("/")
    async def index():
        return FileResponse(static / "index.html")

    @app.websocket("/ws")
    async def session_socket(socket: WebSocket):
        await socket.accept()
        session = DemoSession(config, app.state.client)
        send_lock = asyncio.Lock()
        run_task = None

        async def send(event):
            async with send_lock:
                await socket.send_text(json.dumps(event, ensure_ascii=True))

        async def run(command):
            try:
                async for event in session.run(command.request, command.scenario_id):
                    await send(event)
            except ValueError as exc:
                await send({"type": "error", "message": str(exc)})

        try:
            await send({"type": "init", "models": session.models, "scenarios": [asdict(item) for item in SCENARIOS], "snapshot": session.snapshot()})
            while True:
                text = await socket.receive_text()
                try:
                    command = RunCommand.model_validate_json(text)
                except ValidationError:
                    await send({"type": "error", "message": "잘못된 명령입니다. 요청 내용과 유효한 시나리오를 지정해 주세요."})
                    continue
                if run_task and not run_task.done():
                    await send({"type": "error", "message": "이미 비교가 실행 중입니다."})
                    continue
                run_task = asyncio.create_task(run(command))
        except WebSocketDisconnect:
            pass
        finally:
            if run_task:
                run_task.cancel()
                await asyncio.gather(run_task, return_exceptions=True)

    return app
