import json

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from jev_router_demo.metrics import RouterMetrics
from jev_router_demo.models import RoutingResult
from jev_router_demo.labels import FIELDS, OUTPUT_KINDS, candidate_label, tier_label
from jev_router_demo.scenarios import SCENARIOS, Scenario


COMMANDS = "[r] 실행  [n] 다음  [p] 이전  [e] 직접 입력  [v] 요청 보기  [o] 출력 원문  [q] 종료"


def literal_text(value: str, style: str = "") -> Text:
    """Keep malformed Unicode inspectable without changing stored measurements."""
    return Text(value.encode("utf-8", errors="backslashreplace").decode("utf-8"), style=style)


def number(value: int | float | None, suffix: str = "") -> str:
    if value is None:
        return "-"
    return f"{value:,.2f}{suffix}" if isinstance(value, float) else f"{value:,}{suffix}"


def route_line(result: RoutingResult) -> str:
    if result.decision is None:
        return "경로 없음"
    decision = result.decision
    web = "웹 검색 사용" if decision.needs_web else "웹 검색 미사용"
    action = "사용자 승인 필요" if decision.needs_approval else "실행 (시뮬레이션)"
    return f"{tier_label(decision.model_tier)} 모델 ──► {web} ──► {action}"


def result_panel(result: RoutingResult) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="dim")
    table.add_column()
    decision = result.decision
    table.add_row("모델", tier_label(decision.model_tier) if decision else "-")
    table.add_row("웹 검색", ("필요" if decision.needs_web else "불필요") if decision else "-")
    approval = Text("필요", style="bold yellow") if decision and decision.needs_approval else Text("불필요" if decision else "-")
    table.add_row("사용자 승인", approval)
    table.add_row("", "")
    table.add_row("응답 시간", number(result.latency_ms, " ms"))
    table.add_row("입력 토큰", number(result.input_tokens))
    table.add_row("출력 토큰", number(result.output_tokens))
    table.add_row("전체 토큰", number(result.total_tokens))
    table.add_row("생성 바이트", number(result.generated_bytes))
    table.add_row("결정 출력 방식", Text(OUTPUT_KINDS.get(result.output_kind, result.output_kind)))
    parsed = "불필요" if not result.parse_required else {True: "성공", False: "실패", None: "-"}[result.parse_success]
    table.add_row("파싱", parsed)
    table.add_row("파싱 시간", number(result.parse_ms, " ms"))
    items = [table, Text("\n" + route_line(result), style="bold cyan")]
    if result.error:
        items.append(literal_text("\n오류: " + result.error, style="bold red"))
    if result.probabilities:
        items.append(Text("\nAPI가 반환한 후보 확률", style="bold"))
        for field, candidates in result.probabilities.items():
            items.append(Text(FIELDS.get(field, field)))
            for candidate, probability in candidates.items():
                bar = "█" * round(probability * 20)
                items.append(Text(f"{candidate_label(field, candidate):<10} {bar:<20} {probability:.0%}"))
    return Panel(Group(*items), title=f"{result.router_name} 라우터", border_style="cyan")


def cumulative_panel(metrics: dict[str, RouterMetrics]) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    table.add_column("", style="dim")
    for name in metrics:
        table.add_column(name, justify="right")
    values = list(metrics.values())
    table.add_row("요청 수", *(number(item.requests) for item in values))
    table.add_row("성공 수", *(number(item.successes) for item in values))
    table.add_row("평균 응답 시간 (성공)", *(number(item.average_latency_ms, " ms") for item in values))
    for key, label in [
        ("input_tokens", "입력 토큰"), ("output_tokens", "출력 토큰"),
        ("total_tokens", "전체 토큰"), ("generated_bytes", "생성 바이트"),
    ]:
        cells = []
        for item in values:
            observed = item.observations[key]
            cell = number(item.totals[key]) if observed else "-"
            if observed and observed != item.requests:
                cell += f" ({observed}/{item.requests})"
            cells.append(cell)
        table.add_row(label, *cells)
    table.add_row("파싱 실패", *(str(item.parse_failures) if item.parse_attempts else "-" for item in values))
    table.add_row("오류 수", *(number(item.errors) for item in values))
    return Panel(
        Group(table, Text("부분 집계: (측정된 요청 수/전체 요청 수). '-' = 측정값 없음.", style="dim")),
        title="누적 측정값", border_style="blue",
    )


def render_screen(
    console: Console,
    scenario: Scenario,
    index: int,
    results: tuple[RoutingResult, RoutingResult] | None,
    metrics: dict[str, RouterMetrics],
    message: str = "",
) -> None:
    if console.is_terminal:
        console.clear()
    console.print(Panel(Text("JEV 에이전트 라우터 데모", justify="center", style="bold cyan")))
    console.print(Text("시뮬레이션 · 라우팅 결정만 수행하며 후속 작업은 실행하지 않습니다", style="dim"))
    label = f"시나리오 {index + 1}/{len(SCENARIOS)}" if scenario is SCENARIOS[index] else "직접 입력 요청"
    console.print(Text(f"\n{label} · {scenario.label}", style="bold"))
    if scenario.summary:
        console.print(Panel(Text(scenario.summary), title="요청 요약", border_style="cyan"))
    width = max(console.width - 4, 10)
    lines = Text(scenario.request).wrap(console, width)
    preview = list(lines[:4])
    if len(lines) > 4:
        preview[-1].truncate(width - 1)
        preview[-1].append("…")
    console.print(Panel(Text("\n").join(preview), title="실제 전송 요청", border_style="white"))
    if results:
        panels = [result_panel(result) for result in results]
        if console.width >= 100:
            columns = Table.grid(expand=True, padding=(0, 1))
            columns.add_column(ratio=1)
            columns.add_column(ratio=1)
            columns.add_row(*panels)
            console.print(columns)
        else:
            for panel in panels:
                console.print(panel)
    console.print(cumulative_panel(metrics))
    console.print(Text(COMMANDS, style="bold"))
    if message:
        console.print(Text(message, style="yellow"))


def show_raw_outputs(console: Console, results: tuple[RoutingResult, RoutingResult]) -> None:
    for result in results:
        console.print(Text(f"\n{result.router_name} 생성 라우팅 출력", style="bold cyan"))
        console.print(literal_text(result.generated_text if result.generated_text is not None else "-"))
        if result.thinking_text is not None:
            console.print(Text("반환된 추론 내용", style="bold"))
            console.print(literal_text(result.thinking_text))
        console.print(Text(f"{result.router_name} API 응답 원문", style="dim"))
        raw = result.raw_response
        console.print(literal_text(json.dumps(raw, ensure_ascii=False, indent=2) if not isinstance(raw, str) else raw))
