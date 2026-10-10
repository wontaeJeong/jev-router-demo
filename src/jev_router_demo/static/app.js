"use strict";
const $ = (id) => document.getElementById(id);
let socket, scenarios = [], models = {}, snapshot = null, selected = 0, request = "", router = "LLM", section = "request", full = false, pending = false;
const fmt = (value, digits = 0) => value == null ? "—" : Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });
const node = (tag, className, text) => { const el = document.createElement(tag); el.className = className; if (text != null) el.textContent = text; return el; };
const tiers = {fast: "빠른 처리", standard: "일반 처리", reasoning: "심층 추론"};
const states = {idle: "대기", running: "라우팅 중", success: "완료", error: "오류", cancelled: "중단"};
const outputKinds = {generated: "텍스트 생성", typed: "구조화된 결정", unknown: "알 수 없음"};
const tierLabel = value => tiers[value.toLowerCase()] || value;
function toast(message) { $("toast").textContent = message; $("toast").hidden = false; clearTimeout(toast.timer); toast.timer = setTimeout(() => $("toast").hidden = true, 3500); }
function busy() { return pending || Boolean(snapshot?.running); }
function controls() {
  const locked = busy(), online = socket?.readyState === WebSocket.OPEN;
  $("run").disabled = locked || !online;
  $("edit").disabled = $("custom").disabled = locked || !online;
  document.querySelectorAll(".scenario-button").forEach((button) => button.disabled = locked);
  $("run").firstChild.textContent = locked ? "● 라우팅 중… " : "▶ 비교 실행 ";
}
function chooseScenario(index) {
  if (busy()) return;
  selected = index; request = scenarios[index].request;
  clearCurrentResults(); renderRequest(); renderCards(); renderInspector();
}
function clearCurrentResults() {
  if (snapshot) {
    snapshot.results = {}; snapshot.states = {LLM: "idle", JEV: "idle"}; snapshot.comparison = {latency_ratio: null, output_token_difference: null};
    for (const row of snapshot.decision_rows) {
      row.different = false;
      for (const candidates of Object.values(row.routers)) for (const candidate of candidates) {
        candidate.selected = false; candidate.probability = null;
      }
    }
  }
  $("run-state").textContent = "이 요청을 비교할 준비가 되었습니다";
}
function renderRequest() {
  $("scenario-title").textContent = selected == null ? "직접 입력 요청" : scenarios[selected]?.label || "요청";
  $("request-preview").textContent = request;
  document.querySelectorAll(".scenario-button").forEach((button, index) => { button.classList.toggle("selected", index === selected); button.setAttribute("aria-pressed", String(index === selected)); });
  const s = scenarios[selected];
  $("request-summary").hidden = false;
  $("summary-text").textContent = s?.summary || request.trim().replace(/\s+/g, " ").slice(0, 120);
  $("expected").textContent = s ? `참고용 예상 경로 · ${s.expected_tiers.map(tierLabel).join(" / ")} · 웹 검색 ${s.expected_web ? "필요" : "불필요"} · 승인 ${s.expected_approval ? "필요" : "불필요"}` : "직접 입력 · 예상 경로 없음";
}
function renderCards() {
  for (const name of ["LLM", "JEV"]) {
    const card = $("card-" + name), result = snapshot?.results[name], state = snapshot?.states[name] || "idle";
    const top = node("div", "card-top");
    top.append(node("h2", "router-name", name), node("span", "state " + state, states[state]));
    const mode = snapshot?.api_modes?.[name];
    card.replaceChildren(top, node("div", "router-role", name === "LLM" ? "텍스트 생성 라우터" : "구조화된 결정 라우터"),
      node("div", "model-name", (models[name] || "연결 중…") + (mode ? " · " + mode : "")));
    const metrics = $("key-metrics-" + name), latency = node("div", ""), tokens = node("div", "");
    const latencyValue = node("div", "metric-value", fmt(result?.latency_ms, 1) + " "); latencyValue.append(node("small", "", "ms"));
    latency.append(node("div", "metric-label", "전체 응답 시간"), latencyValue);
    tokens.append(node("div", "metric-label", "출력 토큰"), node("div", "metric-value", fmt(result?.output_tokens)));
    metrics.replaceChildren(node("div", "metric-router", name), latency, tokens);
    if (result?.error) metrics.append(node("div", "error-message", result.error));
    const details = node("dl", "details");
    for (const [label, value] of [["입력 / 전체 토큰", `${fmt(result?.input_tokens)} / ${fmt(result?.total_tokens)}`], ["생성 바이트", fmt(result?.generated_bytes)], ["결정 출력 방식", outputKinds[result?.output_kind] || result?.output_kind || "—"], ["결정 파싱", result ? result.parse_required ? result.parse_success === true ? "성공" : result.parse_success === false ? "실패" : "측정값 없음" : "불필요" : "—"], ["파싱 시간", `${fmt(result?.parse_ms, 2)} ms`]]) details.append(node("dt", "", label), node("dd", "", value));
    $("execution-" + name).replaceChildren(node("h3", "metric-router", name), details);
  }
  renderDecisions();
  const c = snapshot?.comparison;
  const differences = (snapshot?.decision_rows || []).filter(row => row.different);
  const complete = ["LLM", "JEV"].every(name => snapshot?.results[name]?.decision);
  $("comparison-title").textContent = differences.length ? "≠ 다른 선택: " + differences.map(row => row.label).join(" · ") : complete ? "세 가지 판단 일치" : busy() ? "두 모델의 결정을 기다리는 중" : Object.values(snapshot?.states || {}).some(state => ["error", "cancelled"].includes(state)) ? "비교 불가 · 일부 결정 미제공" : "시나리오를 실행해 두 모델의 판단을 비교하세요.";
  $("comparison").textContent = `응답 시간 LLM / JEV  ${fmt(c?.latency_ratio, 2)}배  ·  출력 토큰 LLM − JEV  ${fmt(c?.output_token_difference)}`;
}
function renderDecisions() {
  const container = $("decision-rows"); container.replaceChildren();
  for (const [index, row] of (snapshot?.decision_rows || []).entries()) {
    const question = node("section", "comparison-question" + (row.different ? " different" : ""));
    question.dataset.field = row.field;
    const title = node("h3", "question-title", `${String(index + 1).padStart(2, "0")}  ${row.label}`);
    if (row.different) title.append(node("span", "difference", "≠ 다른 선택"));
    const pair = node("div", "candidate-pair");
    for (const name of ["LLM", "JEV"]) {
      const cell = node("div", "candidate-cell " + name.toLowerCase());
      cell.dataset.router = name;
      cell.setAttribute("aria-label", `${name} ${row.label} 후보와 선택`);
      cell.append(node("div", "candidate-router", name));
      for (const candidate of row.routers[name]) {
        const choice = node("div", "candidate" + (candidate.selected ? " chosen" : ""));
        choice.dataset.value = candidate.value;
        const marker = node("span", "choice-marker", candidate.selected ? "●" : "○");
        marker.setAttribute("aria-hidden", "true");
        const probability = node("span", "candidate-probability", candidate.probability == null ? "미제공" : `${(candidate.probability * 100).toFixed(1)}%`);
        const track = node("span", "probability-track"); track.setAttribute("aria-hidden", "true");
        if (candidate.probability != null) {
          const fill = node("span", "probability-fill"); fill.style.width = `${candidate.probability * 100}%`; track.append(fill);
        } else track.classList.add("unavailable");
        choice.append(marker, node("span", "candidate-label", candidate.label), track, probability,
          node("span", "choice-badge", candidate.selected ? "선택" : ""));
        cell.append(choice);
      }
      pair.append(cell);
    }
    question.append(title, pair); container.append(question);
  }
}
function inspectorEntry() { return snapshot?.results[router]?.inspector[section]; }
function highlight(text, isJson) {
  const code = $("json-code"); code.replaceChildren();
  if (!isJson) { code.textContent = text; return; }
  const regex = /"(?:\\.|[^"\\])*"\s*:|"(?:\\.|[^"\\])*"|\b(?:true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g;
  let offset = 0;
  for (const match of text.matchAll(regex)) {
    code.append(document.createTextNode(text.slice(offset, match.index)));
    const value = match[0], kind = value.startsWith('"') ? value.trimEnd().endsWith(":") ? "key" : "string" : /^(true|false|null)$/.test(value) ? "literal" : "number";
    code.append(node("span", "json-" + kind, value)); offset = match.index + value.length;
  }
  code.append(document.createTextNode(text.slice(offset)));
}
function renderInspector() {
  const result = snapshot?.results[router], entry = inspectorEntry();
  $("copy").disabled = $("download").disabled = !entry;
  $("full-toggle").textContent = full ? "축약 보기" : "전체 보기";
  $("http-meta").textContent = result?.http ? `${result.http.method} ${result.http.url} · HTTP ${result.http.status_code ?? "응답 없음"}` : `${router} · ${states[snapshot?.states[router] || "idle"]}`;
  $("preview-label").textContent = full ? "전체 보기 · 복사와 저장은 항상 원문을 사용합니다" : `축약 표시 · ${entry?.omitted || 0}개 중략 · 원본 변경 없음`;
  highlight(entry ? entry[full ? "full" : "preview"] : "라우터를 실행하면 HTTP 통신 기록을 확인할 수 있습니다.", entry?.is_json);
  $("json-view").scrollTop = $("json-view").scrollLeft = 0;
}
function renderMetrics() {
  const body = $("metrics"); body.replaceChildren();
  const usage = (metric, key) => metric?.observations[key] ? fmt(metric.totals[key]) + (metric.observations[key] !== metric.requests ? ` (${metric.observations[key]}/${metric.requests})` : "") : "—";
  const rows = [["요청 수", m => fmt(m?.requests)], ["성공 수", m => fmt(m?.successes)], ["오류 수", m => fmt(m?.errors)], ["평균 응답 시간 · 성공", m => `${fmt(m?.average_latency_ms, 1)} ms`], ["입력 토큰", m => usage(m,"input_tokens")], ["출력 토큰", m => usage(m,"output_tokens")], ["전체 토큰", m => usage(m,"total_tokens")], ["생성 바이트", m => usage(m,"generated_bytes")], ["파싱 실패", m => m?.parse_attempts ? fmt(m.parse_failures) : "—"]];
  for (const [label, value] of rows) { const row = node("tr", ""); row.append(node("td", "", label), node("td", "", value(snapshot?.metrics.LLM)), node("td", "", value(snapshot?.metrics.JEV))); body.append(row); }
}
function connect() {
  if (socket) socket.close();
  pending = false; $("connection").textContent = "연결 중…"; $("reconnect").hidden = true;
  socket = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
  const current = socket;
  current.onmessage = (message) => {
    if (current !== socket) return;
    const event = JSON.parse(message.data);
    if (event.type === "init") {
      models = event.models; scenarios = event.scenarios; snapshot = event.snapshot;
      $("backend-note").textContent = `Jev는 ${snapshot.api_modes.JEV} 구조화 API를 사용합니다. 출력 토큰은 실제 반환값을 표시합니다.`;
      $("scenarios").replaceChildren();
      scenarios.forEach((scenario, index) => { const button = node("button", "scenario-button"); const label = node("span", "", scenario.label); label.append(node("small", "", scenario.expected_tiers.map(tierLabel).join(" / ") + (scenario.expected_web ? " · 웹 검색" : "") + (scenario.expected_approval ? " · 승인" : ""))); button.append(node("span", "ordinal", String(index + 1).padStart(2,"0")), label); button.onclick = () => chooseScenario(index); $("scenarios").append(button); });
      $("connection").textContent = "● 연결됨 · 로컬 세션"; $("connection").classList.remove("offline");
      selected = 0; request = scenarios[0].request; renderRequest();
      $("run-state").textContent = "첫 비교를 실행할 준비가 되었습니다";
    } else if (event.type === "error") { toast(event.message); }
    else {
      if (event.type !== "started" && event.run_id !== snapshot?.run_id) return;
      snapshot = event.snapshot; pending = false;
      $("run-state").textContent = event.type === "finished" ? `${event.run_id}번째 비교 완료` : `${event.run_id}번째 비교 · 백엔드 ${Object.values(snapshot.states).filter(s => s !== "running").length}/2개 완료`;
    }
    controls(); renderCards(); renderInspector(); renderMetrics();
  };
  current.onclose = () => {
    if (current !== socket) return;
    pending = false;
    if (snapshot) {
      snapshot.running = false;
      for (const name of ["LLM", "JEV"]) if (snapshot.states[name] === "running") snapshot.states[name] = "cancelled";
    }
    $("connection").textContent = "● 연결 끊김"; $("connection").classList.add("offline"); $("reconnect").hidden = false;
    $("run-state").textContent = "연결이 끊겼습니다. 다시 연결해 새 세션을 시작하세요."; controls(); renderCards(); renderInspector();
  };
  current.onerror = () => current.close();
  controls();
}
function editRequest() { if (busy() || socket?.readyState !== WebSocket.OPEN) return; $("request-editor").value = request; $("request-dialog").showModal(); $("request-editor").focus(); }
$("run").onclick = () => { if (busy() || socket?.readyState !== WebSocket.OPEN) return; pending = true; controls(); socket.send(JSON.stringify({type:"run", request, scenario_id:selected})); };
$("edit").onclick = $("custom").onclick = editRequest;
$("cancel-edit").onclick = () => $("request-dialog").close();
$("request-form").onsubmit = (event) => { event.preventDefault(); if (!$("request-editor").value.trim()) return; request = $("request-editor").value; selected = null; $("request-dialog").close(); clearCurrentResults(); renderRequest(); renderCards(); renderInspector(); };
$("full-toggle").onclick = () => { full = !full; renderInspector(); };
document.querySelectorAll("[data-router]").forEach(button => button.onclick = () => { router = button.dataset.router; document.querySelectorAll("[data-router]").forEach(b => { b.classList.toggle("selected", b === button); b.setAttribute("aria-pressed", String(b === button)); }); renderInspector(); });
document.querySelectorAll("[data-section]").forEach(button => button.onclick = () => { section = button.dataset.section; document.querySelectorAll("[data-section]").forEach(b => { b.classList.toggle("selected", b === button); b.setAttribute("aria-selected", String(b === button)); }); renderInspector(); });
$("copy").onclick = async () => { try { await navigator.clipboard.writeText(inspectorEntry().full); toast("축약하지 않은 원문을 복사했습니다."); } catch { toast("클립보드를 사용할 수 없습니다. 원문 저장을 이용하세요."); } };
$("download").onclick = () => { const entry = inspectorEntry(); if (!entry) return; const blob = new Blob([entry.full], {type:entry.is_json ? "application/json;charset=utf-8" : "text/plain;charset=utf-8"}); const url = URL.createObjectURL(blob), link = node("a", ""); link.href = url; link.download = `${router.toLowerCase()}-${section}-run${snapshot.run_id}-${Date.now()}.${entry.is_json ? "json" : "txt"}`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); toast("원문을 저장했습니다."); };
$("reconnect").onclick = connect;
document.addEventListener("keydown", event => { if (event.ctrlKey || event.metaKey || event.altKey || $("request-dialog").open || /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName)) return; if (event.key.toLowerCase() === "r") $("run").click(); if (event.key.toLowerCase() === "e") editRequest(); });
connect();
