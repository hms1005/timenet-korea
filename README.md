# Time-Net Korea — 행사 페이지 소스

**Time-Net Korea 2026** 행사 홈페이지의 일부 섹션을 별도 HTML로 작성해 두는 저장소입니다.

행사 홈페이지는 Google Sites로 운영되고 있으나, 프로그램 표처럼 레이아웃이 복잡하거나 자주 수정되는 부분은
Google Sites 편집기로 다루기 번거롭습니다. 그래서 해당 부분만 독립된 HTML로 작성하고,
GitHub Pages로 게시한 뒤 홈페이지에서 그 주소로 링크하는 방식으로 관리합니다.

- 행사 홈페이지: https://sites.google.com/view/time-net-korea
- 홈페이지의 프로그램 부분에서 링크하고 있는 주소:
  https://hms1005.github.io/timenet-korea/timenet_program.html

즉 GitHub Pages를 활용하되, 홈페이지에서 실제로 링크하고 있는 것은 위의 프로그램 페이지 하나뿐입니다.
저장소 최상위 주소(https://hms1005.github.io/timenet-korea/)는 사용하지 않습니다.
`index.html`을 두지 않았으므로 이 주소는 열리지 않습니다.

## 파일 구성

| 파일 | 내용 | 사용 여부 |
|---|---|---|
| `timenet_program.html` | 행사 프로그램 시간표 (2026. 10. 29.) | 홈페이지에서 링크해 사용 중 |
| `timenet_background_toggle.html` | 추진배경 및 목표 (국문/영문 토글) | 미사용 — 아래 참고 |

`timenet_background_toggle.html`은 현재 행사 홈페이지에서 사용하지 않습니다.
추후 추진배경·목표를 별도 페이지로 정리하거나 국·영문 병기가 필요해질 경우를 대비해
미리 만들어 둔 예비 파일이며, 필요해지면 그대로 가져다 쓸 수 있습니다.

각 파일은 CSS를 내부에 포함한 단일 파일로, 외부 의존성 없이 그대로 열어볼 수 있습니다.

## 프로그램 표의 분류 체계

프로그램 표의 각 발표에는 분야 태그가 붙습니다. 국문 제목 앞에는 `.field`,
영문 제목 앞에는 `.field-en`으로 같은 내용을 국·영문으로 표시합니다.

```html
<span class="t-ko"><span class="field">기반시설/전력</span>대한민국 표준시로 연결되는 전력계통…</span>
<span class="t-en"><span class="field-en">INFRASTRUCTURE / POWER GRID</span>Linking the Power Grid to KST…</span>
```

대분류는 "그 발표를 어떤 관점에서 다루는가"를, 소분류는 "어떤 영역인가"를 나타냅니다.

| 대분류 | English | 성격 |
|---|---|---|
| 총론 | `OVERVIEW` | 시각동기가 왜 중요한가 — 정책·제도·산업 관점의 총론 |
| 기반시설 | `INFRASTRUCTURE` | 어디에 쓰이는가 — 국가 기반시설별 적용 사례 |
| 솔루션 | `SOLUTIONS` | 누가 공급하는가 — 상용 장비·서비스 |

소분류는 아래 어휘 안에서 골라 씁니다. 같은 개념에 다른 이름을 쓰지 않도록 새 항목이
필요하면 이 표에 먼저 추가합니다.

| 소분류 | English | | 소분류 | English |
|---|---|---|---|---|
| 개요 | `INTRODUCTION` | | 천문 | `ASTRONOMY` |
| 정책 | `POLICY` | | 양자 | `QUANTUM` |
| 산업 | `INDUSTRY` | | 통신 | `TELECOM` |
| 네트워크 | `NETWORK` | | 금융 | `FINANCE` |
| 전력 | `POWER GRID` | | 항공우주 | `AEROSPACE` |
| 항법 | `NAVIGATION` | | 데이터센터 | `DATA CENTER` |
| 원자시계 | `CLOCKS` | | 서비스 | `SERVICE` |

표는 대분류에 맞춰 세션 배너(`<tr class="session">`)로 나뉩니다 — `총론 / OVERVIEW`,
`국가 기반시설과 시각동기 / TIMING AND THE NATIONAL INFRASTRUCTURES`,
`시각 솔루션 / COMMERCIAL SOLUTIONS for TIMING`.

## 수정 및 반영 방법

1. HTML 파일을 수정하고, 브라우저로 열어 결과를 확인합니다.
2. 커밋 후 푸시해 이력을 남깁니다.
   ```bash
   git add *.html
   git commit -m "변경 내용 설명"
   git push
   ```
3. GitHub Pages가 자동으로 다시 게시합니다 (보통 1분 내외).
   행사 홈페이지에는 주소만 링크되어 있으므로, Google Sites 쪽은 손댈 필요가 없습니다.

배포가 오래 걸릴 때가 있습니다. GitHub 러너가 밀리면 큐에서 10분 넘게 대기하기도 하는데,
실패는 아니므로 기다리면 됩니다. 굳이 다시 돌리고 싶으면 빈 커밋을 만들 필요 없이
아래 명령으로 재빌드를 요청할 수 있습니다.

```bash
gh api -X POST repos/hms1005/timenet-korea/pages/builds   # 재빌드 요청
gh api repos/hms1005/timenet-korea/pages/builds/latest -q '.status'   # 상태 확인
```

## 참고

- 프로그램의 연사와 일정은 확정 전 상태(`TBD`)인 항목이 있으며, 사정에 따라 변경될 수 있습니다.
- 아직 확정되지 않아 표시하지 않을 세션은 해당 `<tr>` 블록 전체를 `<!-- -->`로 주석 처리해 두면
  나중에 주석만 해제해 되살릴 수 있습니다. 주석 안의 행에도 분야 태그를 미리 붙여 두었으므로
  주석만 해제하면 바로 표시됩니다.
- 주석 처리한 행은 `<tr>`과 `</tr>`이 짝을 이루는지 확인하세요. 짝이 맞지 않으면 주석을
  해제했을 때 표 전체가 어긋납니다.
