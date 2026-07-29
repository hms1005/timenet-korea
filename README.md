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
| `timenet_program.html` | 행사 프로그램 시간표 (2026. 10. 15.) | 홈페이지에서 링크해 사용 중 |
| `timenet_background_toggle.html` | 추진배경 및 목표 (국문/영문 토글) | 미사용 — 아래 참고 |

`timenet_background_toggle.html`은 현재 행사 홈페이지에서 사용하지 않습니다.
추후 추진배경·목표를 별도 페이지로 정리하거나 국·영문 병기가 필요해질 경우를 대비해
미리 만들어 둔 예비 파일이며, 필요해지면 그대로 가져다 쓸 수 있습니다.

각 파일은 CSS를 내부에 포함한 단일 파일로, 외부 의존성 없이 그대로 열어볼 수 있습니다.

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

## 참고

- 프로그램의 연사와 일정은 확정 전 상태(`TBD`)인 항목이 있으며, 사정에 따라 변경될 수 있습니다.
- 아직 확정되지 않아 표시하지 않을 세션은 해당 `<tr>` 블록 전체를 `<!-- -->`로 주석 처리해 두면
  나중에 주석만 해제해 되살릴 수 있습니다.
