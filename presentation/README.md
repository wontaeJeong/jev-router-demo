# Jev Presentation

15분 발표용 슬라이드 10장을 Reveal.js와 Slidev로 각각 제공합니다.
두 구현은 독립 실행하며 CLI Agent Router는 터미널에서 별도로 실행합니다.

## Presentation implementations

Repository root에서 각 패키지를 별도로 설치·실행합니다:

### Reveal.js

```bash
cd presentation/reveal
npm install
npm run dev
```

기본 URL: `http://127.0.0.1:5173/`. 실행·speaker view·PDF·배포 방법은 아래에 있습니다.

### Slidev

```bash
cd presentation/slidev
npm install
npm run dev
```

기본 URL: `http://localhost:3030/1`. [Slidev README](slidev/README.md)에 presenter mode,
static build, PDF/PPTX export, offline 준비 및 GitHub Pages base 설정을 정리했습니다.

공유 원고는 **`talk.md`**입니다. Reveal은 직접 렌더링하고 Slidev의 `slides.md`는
같은 논리를 압축한 별도 visual adaptation입니다. 두 deck의 핵심 메시지와 실제
demo 계약은 동일합니다. Runtime이나 rendering 구현은 서로 의존하지 않습니다.

---

아래는 기존 **Reveal.js** workflow입니다.

## Development

Node.js 22.12+와 npm이 필요합니다. Repository root에서:

```bash
cd presentation/reveal
npm install
npm run dev
```

표시된 local URL을 엽니다 (기본 `http://127.0.0.1:5173/`).

## Production build

`presentation/reveal`에서:

```bash
npm run build
```

정적 결과물은 `presentation/reveal/dist/`입니다. 설치·빌드 이후 발표와 speaker view는 인터넷 연결이 필요 없습니다. `file://` 대신 로컬 HTTP 서버로 실행하세요.

## Preview

```bash
npm run preview
```

기본 `http://127.0.0.1:4173/`. Offline 발표 전 이 URL에서 확인하세요.

## Content

기존 발표 원고가 없어 **`presentation/talk.md`를 발표 내용의 단일 source of truth**로 만들었습니다. Reveal Markdown plugin이 이 파일을 직접 렌더링합니다. `---`는 slide delimiter, `Note:` 이후는 speaker notes입니다. Diagram만 semantic HTML을 사용하며 별도 HTML 원고는 없습니다.

`reveal/src/theme.css`는 화면 구성, `reveal/src/main.js`는 Reveal 설정을 담당합니다. Notes의 권장 시간 합계는 15분이며 CLI demo 3분이 포함됩니다.

## Speaker notes

**S**를 눌러 speaker view를 엽니다. 팝업을 허용하세요. 현재/다음 slide, notes, timer를 확인할 수 있습니다. 발표용 화면과 speaker view를 각각 프로젝터/노트북에 배치합니다.

## Keyboard

- **→ / Space**: 다음 fragment 또는 slide
- **←**: 이전 fragment 또는 slide
- **F**: fullscreen
- **Esc / O**: slide overview
- **S**: speaker view

Named hash는 새로고침 후에도 위치를 유지합니다:

- `/#/demo`: Slide 09, 터미널 전환 anchor
- `/#/takeaway`: Slide 10, 마무리 / Q&A

## Live demo

Repository root에서 기존 [CLI 설정 방법](../README.md#configure)에 따라 `.env.local`과 LiteLLM/Ollama를 준비한 뒤:

```bash
uv run jev-router-demo
```

Slide 09 → 터미널 → `r` + Enter로 두 Router 실행 → latency/tokens/parsing/decision 비교 → `q`로 종료 → 브라우저 복귀 → **→ 한 번**으로 Slide 10.

추천 scenario: Python Utility → `n` 두 번 → vLLM / CUDA Compatibility → `n` 두 번 → Production DB Cleanup. 각 scenario에서 `r`로 실행합니다. `v`는 입력 전문, `o`는 generated output/raw response입니다. 발표 전 넓은 터미널과 endpoint 연결을 확인하세요.

현재 Ollama Jev-like adapter도 `/api/generate`로 JSON을 생성·parse합니다. Native typed decision 성능을 입증하는 데모가 아닙니다. Confidence는 현재 미제공이고, routing 결과만 표시하며 실제 웹 검색이나 production 변경은 실행하지 않습니다. 슬라이드의 `LIVE`는 실측 예정, `N/A`는 미제공을 뜻합니다.

## PDF

Presentation URL에 **`?print-pdf`**를 붙입니다 (예: `http://127.0.0.1:4173/?print-pdf`).

Chrome/Chromium에서 **Cmd/Ctrl+P → Save as PDF**:

- Layout: Landscape
- Margins: None
- Background graphics: 활성화
- Headers and footers: 비활성화

모든 fragment를 한 페이지에 표시하며, 10장으로 출력합니다. Speaker notes는 PDF에 포함하지 않습니다.

## Static deployment / GitHub Pages

`npm run build` 후 **dist 내부 전체**를 정적 호스팅의 배포 root로 업로드합니다. 상대 asset 경로(`base: './'`)를 사용하므로 `https://username.github.io/jev-router-demo/` 같은 sub-path에서도 동작합니다. URL은 끝에 `/`를 포함하세요.

GitHub Pages에서 Actions 방식으로 배포한다면 Node setup → `npm ci` → `npm run build` (working-directory: `presentation/reveal`) → `actions/upload-pages-artifact` (path: `presentation/reveal/dist`) → `actions/deploy-pages` 순서입니다. 현재 저장소에는 Pages workflow를 추가하지 않았습니다.
