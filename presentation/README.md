# Jev Presentation

개발자·AI 엔지니어 대상 **Slidev 발표**입니다. 본문 **15장 / 약 15분**(CLI 데모
3분 포함), 보충 **3장**으로 구성합니다. 발표 내용과 노트의 단일 원본은
[`slidev/slides.md`](slidev/slides.md)입니다.

## Quick start

Node.js 24 LTS와 npm을 준비한 뒤 repository root에서:

```bash
cd presentation/slidev
npm ci
npm run dev
```

Audience: `http://localhost:3030/1` · Presenter: `http://localhost:3030/presenter/1`.
실행·키보드 조작·PDF/PPTX 출력·offline 준비는 [Slidev README](slidev/README.md)를 참고하세요.

## Story

| 구간 | 슬라이드 | 내용 |
| --- | --- | --- |
| 문제 | 1–3 | 구체적인 Agent 요청과 generation 기반 판단 경로 |
| 관점·계약 | 4–7 | 생성 vs 판단, Jev 정의, 타입, 확률과 실행 정책 |
| 설계 | 8–9 | Agent의 판단·생성·실행 계층과 도구 선택 기준 |
| 데모 | 10–13 | 현재 구현 범위, 비교 harness, 세 scenario, 터미널 전환 |
| 해석·결론 | 14–15 | 관측과 추가 검증, takeaway / Q&A |
| 보충 | 16–18 | 상세 비교, 측정 정의, native endpoint 연결 지점 |

현재 LiteLLM adapter는 JSON 생성 후 parse/validate하고, 로컬 Ollama를 포함한
Jev adapter는 System One typed API를 사용합니다. 이 데모만으로 성능 우위를 입증하지 않습니다.
개념도·설명용 값과 실제 구현·측정값을 구분합니다.

## GitHub Pages

`.github/workflows/presentation-pages.yml`이 `main`의 presentation 변경 또는
수동 실행 시 Slidev를 빌드하고 GitHub Pages에 배포합니다.

1. GitHub repository **Settings → Pages → Source: GitHub Actions** 선택.
2. Workflow가 포함된 PR을 `main`에 merge.
3. Actions의 **Deploy presentation to GitHub Pages** 실행 결과 확인.

예상 URL: **https://wontaejeong.github.io/jev-router-demo/**.
실제 배포 URL은 Actions environment에 표시됩니다. 로컬에서 같은 경로를 확인하려면:

```bash
cd presentation/slidev
npm run build -- --base /jev-router-demo/
npm run preview -- --base /jev-router-demo/
```

Hash routing으로 `#/13`(데모), `#/14`(해석), `#/15`(Q&A)를 직접 열거나 새로고침할 수 있습니다.
Pages에서는 웹 슬라이드를 제공하며 CLI는 발표자의 로컬 터미널에서 별도로 실행합니다.
