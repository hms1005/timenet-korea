# Time-Net Korea — 행사 페이지 소스

**Time-Net Korea 2026** 행사 홈페이지의 일부 섹션을 별도 HTML로 작성해 두는 저장소입니다.

행사 홈페이지는 Google Sites로 운영되고 있으나, 프로그램 표처럼 레이아웃이 복잡하거나 자주 수정되는 부분은
Google Sites 편집기로 다루기 번거롭습니다. 그래서 해당 부분만 독립된 HTML로 작성하고,
GitHub Pages로 게시한 뒤 홈페이지에서 링크하거나 삽입(embed)하는 방식으로 관리합니다.

- 행사 홈페이지: https://sites.google.com/view/time-net-korea
- 게시 위치(GitHub Pages): https://hms1005.github.io/timenet-korea/

## 파일 구성

| 파일 | 내용 | 게시 주소 |
|---|---|---|
| `timenet_program.html` | 행사 프로그램 시간표 (2026. 10. 15.) | https://hms1005.github.io/timenet-korea/timenet_program.html |
| `timenet_background_toggle.html` | 추진배경 및 목표 (국문/영문 토글) | https://hms1005.github.io/timenet-korea/timenet_background_toggle.html |

각 파일은 CSS를 내부에 포함한 단일 파일로, 외부 의존성 없이 그대로 열어볼 수 있습니다.

## 수정 및 반영 방법

1. HTML 파일을 수정합니다.
2. 커밋 후 푸시합니다.
   ```bash
   git add *.html
   git commit -m "변경 내용 설명"
   git push
   ```
3. GitHub Pages가 자동으로 다시 게시합니다 (보통 1분 내외).
   Google Sites 쪽은 링크만 걸려 있으므로 별도 수정이 필요 없습니다.

## 참고

- 프로그램의 연사와 일정은 확정 전 상태(`TBD`)인 항목이 있으며, 사정에 따라 변경될 수 있습니다.
- 아직 확정되지 않아 표시하지 않을 세션은 해당 `<tr>` 블록 전체를 `<!-- -->`로 주석 처리해 두면
  나중에 주석만 해제해 되살릴 수 있습니다.
