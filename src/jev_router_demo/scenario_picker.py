from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, OptionList, Select, Static
from textual.widgets.option_list import Option

from jev_router_demo.scenarios import CATEGORIES, FILTERS, SCENARIOS, scenario_indices


class ScenarioPicker(ModalScreen[tuple[int, str, str] | None]):
    BINDINGS = [("escape", "cancel", "취소")]

    def __init__(self, current, category="recommended", query=""):
        super().__init__()
        self.current, self.category, self.search_query = current, category, query
        self.indices = []

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Static("시나리오 선택 · 제목·요약 검색 · Enter 선택 · Esc 취소", id="picker-title")
            with Horizontal(id="picker-filters"):
                yield Select([(label, key) for key, label in FILTERS.items()], value=self.category,
                             allow_blank=False, id="scenario-category")
                yield Input(value=self.search_query, placeholder="제목·요약 검색", id="scenario-search")
            yield Static(id="picker-count")
            with Horizontal(id="picker-body"):
                yield OptionList(id="scenario-list")
                with VerticalScroll(id="picker-preview-scroll"):
                    yield Static(id="picker-preview")
            with Horizontal(id="picker-actions"):
                yield Button("선택", id="choose-scenario", variant="primary")
                yield Button("직접 입력", id="pick-custom")
                yield Button("취소", id="picker-cancel")

    def on_mount(self):
        self.rebuild()
        self.query_one("#scenario-search", Input).focus()
        self.set_class(self.size.width < 80, "picker-narrow")
        self.set_class(self.size.height < 30, "picker-short")

    def on_resize(self, event):
        self.set_class(event.size.width < 80, "picker-narrow")
        self.set_class(event.size.height < 30, "picker-short")

    def rebuild(self):
        self.category = self.query_one("#scenario-category", Select).value
        self.search_query = self.query_one("#scenario-search", Input).value
        self.indices = scenario_indices(self.category, self.search_query)
        options = self.query_one(OptionList)
        options.clear_options()
        options.add_options(Option(Text(f"{index + 1:02}  {SCENARIOS[index].label}\n"
                                        f"{CATEGORIES[SCENARIOS[index].category]} · {len(SCENARIOS[index].request):,}자"), id=str(index))
                            for index in self.indices)
        options.highlighted = self.indices.index(self.current) if self.current in self.indices else 0 if self.indices else None
        self.query_one("#picker-count", Static).update(f"{FILTERS[self.category]} · {len(self.indices)}개 / 전체 {len(SCENARIOS)}개")
        self.query_one("#choose-scenario", Button).disabled = not self.indices
        self.preview()

    def preview(self):
        options = self.query_one(OptionList)
        if options.highlighted is None:
            text = Text("검색 결과가 없습니다. 검색어를 지우거나 다른 분류를 선택하세요.")
        else:
            item = SCENARIOS[int(options.get_option_at_index(options.highlighted).id)]
            text = Text(item.label + "\n", style="bold cyan")
            text.append(f"{CATEGORIES[item.category]} · 본문 {len(item.request):,}자\n\n", style="dim")
            text.append(item.summary + "\n\n", style="")
            text.append("선택 후 실행 상세 [x]에서 요청 전문을 확인할 수 있습니다.", style="dim")
        self.query_one("#picker-preview", Static).update(text)

    def on_input_changed(self, event: Input.Changed):
        if self.is_mounted:
            self.rebuild()

    def on_select_changed(self, event: Select.Changed):
        if self.is_mounted:
            self.rebuild()

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted):
        self.preview()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        self.choose()

    def on_input_submitted(self, event: Input.Submitted):
        self.choose()

    def choose(self):
        options = self.query_one(OptionList)
        if options.highlighted is not None:
            index = int(options.get_option_at_index(options.highlighted).id)
            self.dismiss((index, self.category, self.search_query))

    def action_cancel(self):
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed):
        event.stop()
        if event.button.id == "choose-scenario":
            self.choose()
        elif event.button.id == "pick-custom":
            self.dismiss((-1, self.category, self.search_query))
        else:
            self.action_cancel()
