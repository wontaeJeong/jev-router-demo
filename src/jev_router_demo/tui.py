from pathlib import Path

import httpx
from rich.console import Group
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Label, RichLog, Select, Static, TabbedContent, TabPane, Tabs, Tab, TextArea

from jev_router_demo.config import Config
from jev_router_demo.comparison import selected_value
from jev_router_demo.inspection import SECTIONS, export_result, render_section
from jev_router_demo.labels import FIELDS, OUTPUT_KINDS, STATES, candidate_label
from jev_router_demo.scenarios import SCENARIOS, Scenario
from jev_router_demo.session import DemoSession, safe_display
from jev_router_demo.ui import cumulative_panel, number


class RequestEditor(ModalScreen[str | None]):
    BINDINGS = [("escape", "cancel", "취소"), ("ctrl+s", "save", "저장")]

    def __init__(self, request: str):
        super().__init__()
        self.request = request

    def compose(self) -> ComposeResult:
        with Vertical(id="editor-dialog"):
            yield Label("직접 입력 요청 · Ctrl+S 저장 · Esc 취소")
            yield TextArea(self.request, id="request-editor", soft_wrap=True)
            with Horizontal(classes="toolbar"):
                yield Button("요청 저장", id="save-request", variant="primary")
                yield Button("취소", id="cancel-request")

    def on_mount(self):
        self.query_one(TextArea).focus()

    def action_cancel(self):
        self.dismiss(None)

    def action_save(self):
        value = self.query_one(TextArea).text
        if value.strip():
            self.dismiss(value)
        else:
            self.notify("요청 내용을 입력해 주세요.", severity="warning")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save-request":
            self.action_save()
        else:
            self.action_cancel()


class RequestPreview(VerticalScroll):
    can_focus = True


def card_content(name, model, state):
    color = "cyan" if name == "LLM" else "green"
    heading = Text(f"{name}  ·  {STATES[state]}\n", style=f"bold {color}")
    heading.append("텍스트 생성 라우터\n" if name == "LLM" else "구조화된 결정 라우터\n", style=color)
    heading.append(model, style="dim")
    heading.no_wrap = True
    heading.overflow = "ellipsis"
    return heading


def candidate_content(name, candidates, stacked=False):
    color = "cyan" if name == "LLM" else "green"
    table = Table.grid(padding=(0, 1))
    table.add_column(width=1)
    table.add_column(min_width=9)
    table.add_column(justify="right", min_width=6)
    table.add_column(width=4)
    for candidate in candidates:
        chosen = candidate["selected"]
        style = f"bold {color} on #1b3445" if chosen else "dim"
        probability = candidate["probability"]
        table.add_row(Text("●" if chosen else "○", style=style),
                      Text(candidate["label"], style=style),
                      Text(f"{probability:.1%}" if probability is not None else "미제공", style=style),
                      Text("선택" if chosen else "", style=style))
    return Group(Text(name, style=f"bold {color}"), table) if stacked else table


def result_metrics(name, result):
    items = [Text(name, style="bold cyan" if name == "LLM" else "bold green"), Text(
        f"응답 시간  {number(result.latency_ms, ' ms') if result else '-'}\n출력 토큰  {number(result.output_tokens) if result else '-'}")]
    if result and result.error:
        items.append(Text("\n" + safe_display(result.error), style="bold red"))
    return Group(*items)


def execution_content(name, model, state, result):
    heading = Text(f"{name} / {model} · {STATES[state]}", style="bold")
    if not result:
        return Group(heading, Text("실행 후 측정값이 표시됩니다.", style="dim"))
    table = Table.grid(padding=(0, 2), expand=True)
    table.add_column(style="dim")
    table.add_column(justify="right")
    for label, value in [("응답 시간", number(result.latency_ms, " ms")), ("입력 / 출력 토큰", f"{number(result.input_tokens)} / {number(result.output_tokens)}"),
                         ("전체 토큰", number(result.total_tokens)), ("생성 바이트", number(result.generated_bytes)),
                         ("결정 출력 / 파싱", OUTPUT_KINDS.get(result.output_kind, result.output_kind) + " / " + ("실패" if result.parse_success is False else "성공" if result.parse_success else "불필요" if not result.parse_required else "측정값 없음")),
                         ("파싱 시간", number(result.parse_ms, " ms"))]:
        table.add_row(label, value)
    items = [heading, Text(""), table]
    if result.error:
        items.append(Text("\n" + safe_display(result.error), style="bold red"))
    return Group(*items)


def probability_content(name, model, state, result):
    color = "cyan" if name == "LLM" else "green"
    items = [Text(f"{name} / {model} · {STATES[state]}", style=f"bold {color}")]
    if not result:
        return Group(*items, Text("실행 후 선택과 후보 확률이 표시됩니다.", style="dim"))
    for index, (field, label) in enumerate(FIELDS.items(), 1):
        selected = selected_value(result.decision, field) if result.decision else None
        items.append(Text(f"\n{index:02}  {label}", style="bold"))
        if selected is not None:
            items.append(Text("선택 → " + candidate_label(field, selected), style=f"bold {color}"))
        else:
            items.append(Text("결정 미제공", style="dim"))
        candidates = (result.probabilities or {}).get(field, {})
        if not candidates:
            items.append(Text("후보 확률 미제공", style="dim"))
            continue
        table = Table.grid(padding=(0, 1))
        for _ in range(4):
            table.add_column()
        for candidate, probability in candidates.items():
            chosen = candidate == selected
            filled = round(max(0, min(1, probability)) * 12)
            bar = Text("█" * filled, style=color)
            bar.append("░" * (12 - filled), style="dim")
            table.add_row(Text("▶" if chosen else " ", style=f"bold {color}"),
                          Text(candidate_label(field, candidate), style="bold" if chosen else "dim"),
                          bar, Text(f"{probability:.1%}" + (" 선택" if chosen else "")))
        items.append(table)
    if result.error:
        items.append(Text("\n" + safe_display(result.error), style="bold red"))
    return Group(*items)


class RouterDemoApp(App):
    CSS_PATH = "tui.tcss"
    TITLE = "JEV / 라우터 실험실"
    BINDINGS = [("r", "run_compare", "실행"), ("n", "next", "다음"), ("p", "previous", "이전"),
                ("e", "edit", "수정"), ("c", "show_view('comparison')", "비교"),
                ("d", "show_view('decisions')", "선택"), ("x", "show_view('execution')", "실행 상세"),
                ("o", "inspect", "HTTP"), ("q", "quit", "종료")]

    def __init__(self, config: Config, client: httpx.AsyncClient | None = None):
        super().__init__()
        self.config = config
        self.client = client or httpx.AsyncClient()
        self.owns_client = client is None
        self.session = DemoSession(config, self.client)
        self.index = 0
        self.scenario = SCENARIOS[0]
        self.full = False
        self.section = "request"
        self.inspector_text = ""

    def compose(self) -> ComposeResult:
        yield Static(Text("JEV / 라우터 실험실   ·   실시간 결정 비교", style="bold cyan"), id="brand")
        backend_note = self.config.jev_api_mode.upper() + " 구조화 API"
        yield Static("라우팅 전용 시뮬레이션  ·  후속 작업 실행 없음  ·  Jev: " + backend_note, id="subtitle")
        with Horizontal(classes="toolbar"):
            yield Select([(f"{i+1:02}  {item.label}", i) for i, item in enumerate(SCENARIOS)] + [("직접 입력 요청", -1)], value=0, allow_blank=False, id="scenario")
            yield Button("실행  [r]", variant="primary", id="run")
            yield Button("수정  [e]", id="edit")
        with RequestPreview(id="request-preview-scroll"):
            yield Static(id="request-preview")
        with TabbedContent(id="views"):
            with TabPane("비교", id="comparison"):
                with Horizontal(id="cards"):
                    yield Static(id="card-LLM", classes="router-heading llm")
                    yield Static(id="card-JEV", classes="router-heading jev")
                with VerticalScroll(id="comparison-scroll"):
                    for field in FIELDS:
                        yield Static(id=f"question-{field}", classes="question-heading")
                        with Horizontal(id=f"pair-{field}", classes="decision-pair"):
                            for name in ("LLM", "JEV"):
                                yield Static(id=f"choices-{name}-{field}", classes=f"candidate-cell {name.lower()}")
                    with Horizontal(id="key-metrics", classes="decision-pair"):
                        yield Static(id="key-metrics-LLM", classes="candidate-cell llm")
                        yield Static(id="key-metrics-JEV", classes="candidate-cell jev")
                    yield Static(id="comparison-summary")
                    yield Static("● 실제 선택 · 미제공 ≠ 0% · 확률 막대 [d] · 실행 상세 [x]", classes="note")
            with TabPane("선택 상세", id="decisions"):
                yield Static("▶ 실제 선택  ·  막대는 API 반환 확률 그대로  ·  미제공 ≠ 0%", classes="note")
                with VerticalScroll():
                    with Horizontal(id="probability-cards"):
                        yield Static(id="probability-LLM", classes="result-card llm")
                        yield Static(id="probability-JEV", classes="result-card jev")
            with TabPane("실행 상세", id="execution"):
                with RequestPreview(id="request-original-scroll"):
                    yield Static(id="request-original")
                    with Horizontal(id="execution-cards"):
                        yield Static(id="execution-LLM", classes="result-card llm")
                        yield Static(id="execution-JEV", classes="result-card jev")
                    yield Static("모델·캐시·초기 로딩 차이의 영향을 받는 측정값입니다.\n'-'는 0이 아니라 측정값 없음을 뜻합니다. 예상 경로는 참고용 시나리오 정보입니다.", classes="note")
            with TabPane("HTTP 상세 보기", id="inspector"):
                with Horizontal(classes="toolbar"):
                    yield Select([("LLM", "LLM"), ("Jev", "JEV")], value="LLM", allow_blank=False, id="router")
                    yield Button("전체 보기", id="full-toggle")
                    yield Button("원문 저장", id="export")
                yield Static(id="http-meta")
                yield Tabs(*(Tab(label, id=key) for key, label in SECTIONS.items()), id="sections")
                yield Static(id="preview-label", classes="note")
                yield RichLog(id="json-log", wrap=False, auto_scroll=False, min_width=0)
            with TabPane("세션 측정값", id="metrics"):
                with VerticalScroll():
                    yield Static(id="metrics-table")
        yield Static("시나리오를 선택한 뒤 r을 누르세요. Enter 없이 바로 실행됩니다.", id="status")
        yield Footer()

    def on_mount(self):
        self.update_layout(self.size.width)
        self.refresh_request()
        self.refresh_results()

    def on_resize(self, event):
        if self.is_mounted and self.query("#cards"):
            self.update_layout(event.size.width)
            self.refresh_results()

    def update_layout(self, width):
        self.set_class(width < 100, "compact")
        self.set_class(width < 64, "stacked")
        for widget in self.query(".decision-pair"):
            widget.set_class(width < 64, "narrow")
        for selector in ("#probability-cards", "#execution-cards"):
            self.query_one(selector).set_class(width < 100, "narrow")

    def refresh_request(self):
        text = Text()
        text.append(self.scenario.label + "\n", style="bold")
        if self.scenario.summary:
            text.append("요청 요약 · ", style="bold cyan")
            text.append(self.scenario.summary)
        else:
            text.append(safe_display(" ".join(self.scenario.request.split())[:120]))
        self.query_one("#request-preview", Static).update(text)
        original = Text("실제 전송 요청 · 전문\n", style="bold")
        original.append(safe_display(self.scenario.request), style="")
        self.query_one("#request-original", Static).update(original)

    def refresh_results(self):
        snapshot = self.session.snapshot()
        rows = snapshot["decision_rows"]
        decisions = [self.session.results[name].decision for name in self.session.routers
                     if name in self.session.results and self.session.results[name].decision]
        differences = [row["field"] for row in rows if row["different"]]
        for index, row in enumerate(rows, 1):
            field = row["field"]
            self.query_one(f"#question-{field}", Static).update(Text(
                f"{index:02}  {row['label']}" + ("  ≠ 다른 선택" if row["different"] else ""),
                style="bold yellow" if row["different"] else "bold"))
            for name, candidates in row["routers"].items():
                self.query_one(f"#choices-{name}-{field}", Static).update(
                    candidate_content(name, candidates, self.size.width < 64))
        for name in self.session.routers:
            args = (name, self.session.models[name], self.session.states[name], self.session.results.get(name))
            self.query_one(f"#card-{name}", Static).update(card_content(*args[:3]))
            self.query_one(f"#key-metrics-{name}", Static).update(result_metrics(name, args[3]))
            self.query_one(f"#probability-{name}", Static).update(probability_content(*args))
            self.query_one(f"#execution-{name}", Static).update(execution_content(*args))
        comparison = snapshot["comparison"]
        ratio = comparison["latency_ratio"]
        delta = comparison["output_token_difference"]
        if len(decisions) == 2:
            agreement = "다른 판단: " + " · ".join(FIELDS[field] for field in differences) if differences else "세 가지 판단 일치"
        elif any(state == "running" for state in self.session.states.values()):
            agreement = "두 모델의 결정을 기다리는 중"
        elif any(state in ("error", "cancelled") for state in self.session.states.values()):
            agreement = "비교 불가 · 일부 결정 미제공"
        else:
            agreement = "시나리오를 실행해 두 모델의 판단을 비교하세요."
        summary = Text(agreement + "\n", style="bold yellow" if differences else "bold")
        summary.append(f"응답 시간 LLM / Jev: {number(ratio)}배  ·  출력 토큰 차이: {number(delta)}", style="dim")
        self.query_one("#comparison-summary", Static).update(summary)
        self.query_one("#metrics-table", Static).update(cumulative_panel(self.session.metrics))
        self.refresh_inspector()

    def refresh_inspector(self):
        name = self.query_one("#router", Select).value
        result = self.session.results.get(name)
        log = self.query_one("#json-log", RichLog)
        log.clear()
        if not result:
            self.inspector_text = "라우터를 실행하면 HTTP 통신 기록을 확인할 수 있습니다."
            self.query_one("#http-meta", Static).update(f"{name} · {STATES[self.session.states.get(name, 'idle')]}")
            self.query_one("#preview-label", Static).update("결과를 기다리는 중입니다.")
            log.write(self.inspector_text)
            return
        text, is_json, count = render_section(result, self.section, full=self.full)
        self.inspector_text = safe_display(text)
        exchange = result.http
        self.query_one("#http-meta", Static).update(Text(f"{exchange.method} {exchange.url} · HTTP {exchange.status_code or '응답 없음'}") if exchange else Text(name))
        self.query_one("#preview-label", Static).update("전체 보기 · 저장은 항상 원문을 사용합니다" if self.full else f"축약 표시 · {count}개 중략 · 원본 변경 없음")
        log.write(Syntax(self.inspector_text, "json" if is_json else "text", theme="monokai", line_numbers=True, word_wrap=False))

    def on_select_changed(self, event: Select.Changed):
        if event.select.id == "scenario" and not self.session.running:
            if event.value != -1:
                if self.scenario is SCENARIOS[int(event.value)]:
                    return
                self.index = int(event.value)
                self.scenario = SCENARIOS[self.index]
                self.session.results.clear()
                self.session.states = dict.fromkeys(self.session.routers, "idle")
                self.refresh_request()
                self.refresh_results()
            elif self.scenario.label != "직접 입력":
                self.action_edit()
        elif event.select.id == "router":
            self.refresh_inspector()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated):
        if event.tabs.id == "sections":
            self.section = event.tab.id
            self.refresh_inspector()

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated):
        self.set_class(self.query_one("#views", TabbedContent).active != "comparison", "detail-view")

    def on_button_pressed(self, event: Button.Pressed):
        actions = {"run": self.action_run_compare, "edit": self.action_edit, "full-toggle": self.toggle_full, "export": self.export_original}
        if event.button.id in actions:
            actions[event.button.id]()

    def toggle_full(self):
        self.full = not self.full
        self.query_one("#full-toggle", Button).label = "축약 보기" if self.full else "전체 보기"
        self.refresh_inspector()

    def export_original(self):
        result = self.session.results.get(self.query_one("#router", Select).value)
        if result:
            try:
                path = export_result(result, self.section, Path.cwd() / "exports")
                self.notify(f"원문 저장 완료: {path}", timeout=8)
            except OSError as exc:
                self.notify(f"저장할 수 없습니다: {exc}", severity="error")
        else:
            self.notify("먼저 요청을 실행해 주세요.", severity="warning")

    def action_next(self):
        if not self.session.running and not isinstance(self.screen, RequestEditor):
            self.query_one("#scenario", Select).value = (self.index + 1) % len(SCENARIOS)

    def action_previous(self):
        if not self.session.running and not isinstance(self.screen, RequestEditor):
            self.query_one("#scenario", Select).value = (self.index - 1) % len(SCENARIOS)

    def action_edit(self):
        if self.session.running or isinstance(self.screen, RequestEditor):
            return
        self.push_screen(RequestEditor(self.scenario.request), self.apply_custom)

    def apply_custom(self, request):
        if request is not None:
            self.scenario = Scenario("직접 입력", request)
            self.query_one("#scenario", Select).value = -1
            self.session.results.clear()
            self.session.states = dict.fromkeys(self.session.routers, "idle")
            self.refresh_request()
            self.refresh_results()
        elif self.scenario.label != "직접 입력":
            self.query_one("#scenario", Select).value = self.index

    def action_inspect(self):
        self.action_show_view("inspector")

    def action_show_view(self, view):
        if not isinstance(self.screen, RequestEditor):
            self.query_one("#views", TabbedContent).active = view

    def action_run_compare(self):
        if self.session.running or isinstance(self.screen, RequestEditor):
            return
        # Disable synchronously, before the worker gets its first event-loop turn.
        self.set_busy(True)
        self.run_comparison()

    def set_busy(self, busy):
        for selector in ("#scenario", "#run", "#edit"):
            self.query_one(selector).disabled = busy

    @work(exclusive=True)
    async def run_comparison(self):
        try:
            async for event in self.session.run(self.scenario.request, None if self.scenario.label == "직접 입력" else self.index):
                self.refresh_results()
                self.query_one("#status", Static).update("라우팅 중… 다른 모델을 기다리는 동안 완료된 결과를 확인할 수 있습니다." if event["type"] != "finished" else "비교 완료. HTTP 상세 보기 [o]에서 요청과 응답을 확인하세요.")
        finally:
            self.set_busy(False)

    async def on_unmount(self):
        if self.owns_client:
            await self.client.aclose()
