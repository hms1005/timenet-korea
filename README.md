# Time-Net Korea — 행사 페이지 소스

**Time-Net Korea 2026** 행사 홈페이지의 일부 섹션을 별도 HTML로 작성해 두는 저장소입니다.

행사 홈페이지는 Google Sites로 운영되고 있으나, 프로그램 표처럼 레이아웃이 복잡하거나 자주 수정되는 부분은
Google Sites 편집기로 다루기 번거롭습니다. 그래서 해당 부분만 독립된 HTML로 작성하고,
GitHub Pages로 게시한 뒤 홈페이지에서 그 주소로 링크하는 방식으로 관리합니다.

- 행사 홈페이지: https://sites.google.com/view/time-net-korea
- 홈페이지의 프로그램 부분에서 링크하고 있는 주소:
  https://hms1005.github.io/timenet-korea/timenet_program.html

이 주소를 홈페이지에서 직접 링크하고 있으므로 **`timenet_program.html` 파일명은 바꾸지 않습니다.**
(포스터 파일들은 2026-09-03에 `timenet2026_poster_*` 로 정리했지만, 이 파일만 예외로 둡니다.)

즉 GitHub Pages를 활용하되, 홈페이지에서 실제로 링크하고 있는 것은 위의 프로그램 페이지 하나뿐입니다.
저장소 최상위 주소(https://hms1005.github.io/timenet-korea/)는 사용하지 않습니다.
`index.html`을 두지 않았으므로 이 주소는 열리지 않습니다.

## 파일 구성

| 파일 | 내용 | 사용 여부 |
|---|---|---|
| `timenet_program.html` | 행사 프로그램 시간표 (2026. 10. 29.) | 홈페이지에서 링크해 사용 중 — 이름 고정 |
| `timenet_background_toggle.html` | 추진배경 및 목표 (국문/영문 토글) | 미사용 — 아래 참고 |
| `timenet2026_poster_schedule.html` | 행사 포스터 — 전체 시간표 판 (다크, 한글 전용) | 홍보·인쇄용 PDF/PNG/GIF 로 출력 |
| `timenet2026_poster_summary.svg` | 행사 포스터 — 요약 판 (세션 단위) | Inkscape 로 편집, PDF/PNG 동봉 |
| `tools/build_assets.py` | PDF·PNG·GIF 자동 생성 스크립트 | 아래 참고 |

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
| 솔루션 | `SOLUTIONS` | | 금융 | `FINANCE` |
| 네트워크 | `NETWORK` | | 항공우주 | `AEROSPACE` |
| 전력 | `POWER GRID` | | 데이터센터 | `DATA CENTER` |
| 항법 | `NAVIGATION` | | 서비스 | `SERVICE` |
| 원자시계 | `CLOCKS` | | 광통신 | `FIBER` |
| 위성 | `SATELLITE` | | | |

대분류와 소분류는 자유롭게 조합합니다. 예를 들어 상용 솔루션을 개별 제품이 아니라 전체 조망으로
다루는 발표는 `솔루션/원자시계`가 아니라 `총론/솔루션`(`OVERVIEW / SOLUTIONS`)으로 답니다.

표는 대분류에 맞춰 세션 배너(`<tr class="session">`)로 나뉩니다 — `총론 / OVERVIEW`,
`국가 기반시설과 시각동기 / TIMING AND THE NATIONAL INFRASTRUCTURES`,
`시각 솔루션 / COMMERCIAL SOLUTIONS for TIMING`.

## 연사 이름 정렬

연사 칸에 두 사람 이상이 들어가는 행에서는 이름 길이가 달라 소속이 들쭉날쭉해 보입니다.
이름을 `.spk-name`으로 감싸고 글자를 낱자로 쪼개면, 두 글자든 세 글자든 같은 폭(`3em`) 안에서
양끝 정렬되어 뒤따르는 직함·소속의 시작 위치가 맞습니다.

```html
<td class="speaker">
  <span class="spk-line"><span class="spk-name"><span>이</span><span>호</span><span>성</span></span>원장(한국표준과학연구원)</span>
  <span class="spk-line"><span class="spk-name"><span>이</span><span>식</span></span>원장(한국과학기술정보연구원)</span>
</td>
```

- `.spk-line`은 한 사람을 한 줄로 잡아 줍니다. 좁은 화면(640px 이하)에서는 줄바꿈을 허용합니다.
- 낱자를 `<span>`으로 하나씩 감싸야 `justify-content:space-between`이 글자 사이를 벌립니다.
- 이 정렬 때문에 연사 열이 넓어야 해서 `col.speaker`를 225px에서 320px로 넓혔습니다.
- 한 사람만 들어가는 행은 지금처럼 `<td class="speaker">허명선 (KRISS)</td>`로 두면 됩니다.

## 시간 표기

시간 열은 발표마다 시작–종료 시각을 적습니다. 예전에는 세션 첫 행에만 시간대를 묶어 적고
나머지는 비워 두었으나, 지금은 모든 행을 개별 시간으로 채워 두었습니다.
붙임표는 en dash(`–`)로 통일합니다.

## 배포 자산 자동 생성 (PDF · PNG · GIF)

프로그램표와 포스터는 홈페이지 링크 말고도 공문·메일·SNS 에 붙일 파일 형태로 자주 필요합니다.
매번 브라우저에서 손으로 인쇄하면 여백과 배율이 달라지므로, `tools/build_assets.py` 가
headless Chrome 으로 렌더해 항상 같은 결과를 만듭니다.

```bash
python3 tools/build_assets.py          # 대조 + 전체 렌더
python3 tools/build_assets.py auto     # 내용이 바뀐 것만 다시 렌더 (평소 이걸 씁니다)
python3 tools/build_assets.py check    # 프로그램 <-> 포스터 대조만
python3 tools/build_assets.py program  # 프로그램 PDF+PNG 만
python3 tools/build_assets.py poster   # 포스터 PDF+PNG+GIF (다크+라이트)
python3 tools/build_assets.py poster-dark    # 다크 확대판만
python3 tools/build_assets.py poster         # 포스터만
```

| 원본 | 만들어지는 파일 |
|---|---|
| `timenet_program.html` | `timenet_program.pdf` (1페이지), `.png` (2x) |
| `timenet2026_poster_schedule.html` | 같은 이름의 `.pdf` (1페이지), `.png` (2x), `.gif` (30프레임 6초 루프) |

요약 판 `timenet2026_poster_summary.svg` 는 이 스크립트가 다루지 않습니다. Inkscape 로 편집하고
PDF/PNG 는 따로 뽑습니다.

**HTML 원본은 건드리지 않습니다.** 출력 전용 CSS(여백 확보, 애니메이션 정지, 배경색 강제)를
입힌 사본을 임시 폴더에 만들어 캡처하는 방식이라, 화면용 스타일과 문서용 스타일이 서로
간섭하지 않습니다.

몇 가지 알아 둘 점:

- **`check` 는 시간·국문 제목·영문 제목·연사를 모두 대조합니다.** 프로그램만 고치고 포스터를
  잊는 일이 실제로 있어 제목까지 봅니다. 포스터가 지면 때문에 일부러 줄여 쓰는 자리는
  스크립트의 `ALLOWED` 에 이유와 함께 적어 두고 예외로 넘깁니다.
- **`auto` 는 `tools/.build-stamp` 의 해시로 변경을 판단합니다.** 이 파일도 함께 커밋해야
  다음에 받아 쓸 때 헛돌지 않습니다.
- **GIF 는 포스터 배경의 광섬유 애니메이션을 프레임 단위로 얼려 캡처합니다.** 원본은 주기가
  제각각(빔 4.8~7.4초, 펄스 3.4초)이라 그대로 이어붙이면 루프 이음매가 튑니다. 렌더할 때만
  각 주기를 6초의 약수로 스냅해 맞춥니다. 포스터의 애니메이션 주기를 바꾸면 이 부분
  (`gif_frame_css`)도 같이 확인하세요.
- **포스터 렌더는 GIF 30프레임 때문에 1~2분 걸립니다.** 프로그램만 고쳤으면 `auto` 가
  프로그램만 다시 만들므로 몇 초면 끝납니다.
- **포스터는 국·영문 병기 인쇄용 확대판 두 벌(다크·라이트)만 씁니다.** 글자 배율은
  `tools/fit_large.py` 가 정하므로, 표 내용을 고쳤으면 그것부터 돌립니다.
  구판(병기 아님 / 확대 아님)은 `old/` 로 옮겨 두었고 저장소에는 올리지 않습니다.
  스크립트의 `POSTERS` 목록에
  정의돼 있고, `auto` 는 둘을 따로 추적해 바뀐 쪽만 다시 렌더합니다. 둘 다 바뀌면 GIF 를
  두 번 굽느라 3~4분 걸립니다.
- `page` 값은 포스터 바깥에 깔리는 색입니다. 캡처가 1px 어긋나도 반대색 테두리가 비치지
  않도록 각 포스터의 바탕색에 맞춰 둡니다.
- `check` 는 두 포스터를 모두 프로그램과 대조합니다.

필요한 것: macOS 의 Google Chrome, 그리고 Pillow (`python3 -m pip install pillow`).

## 프로그램을 고치면 포스터도 같이 고칩니다

프로그램표와 포스터는 같은 내용을 두 벌로 들고 있습니다. 한쪽만 고치면 곧바로 어긋나므로,
`timenet_program.html` 의 시간·연사·제목을 손댔으면 포스터의
`<table class="prog">` 에서 같은 행을 찾아 함께 고친 뒤 `check` 로 확인합니다.
요약 판 SVG 도 같은 내용을 들고 있으니 함께 봐야 합니다.

포스터는 한글만 싣습니다. 해외 연사 발표는 국문 없이 영문 제목만 쓰며(`<span class="en-only">`),
`check` 는 이렇게 한쪽을 비워 둔 자리를 의도된 예외로 넘깁니다. 분야 태그는 포스터에서
`총론` 표시로만 쓰므로, 소분류만 바뀐 수정이면 포스터는 그대로 두어도 됩니다.

## 기관 로고 넣기 (.ai -> 벡터)

포스터 하단의 KRISS·KISTI 로고는 기관 CI 의 `.ai` 원본에서 뽑아 **인라인 SVG 로** 넣었습니다.
벡터라 인쇄용 PDF 에서 확대해도 깨지지 않고, 같은 로고의 base64 PNG 보다 오히려 작습니다.

Illustrator 가 "PDF 호환 파일 만들기" 로 저장한 `.ai` 는 속이 그냥 PDF 라 그대로 변환됩니다.
파일 앞 9바이트가 `%PDF` 면 됩니다.

```bash
head -c 9 로고.ai                      # %PDF-1.6 이면 변환 가능
pdftocairo -svg 로고.ai out.svg         # 벡터로
pdftocairo -png -r 600 -transp -singlefile 로고.ai out   # 확인용 래스터
```

`.ai` 는 보통 A4 페이지 한가운데에 로고가 놓인 형태입니다. 그래서 변환한 SVG 의 루트
`<svg>` 의 `width`/`height`/`viewBox` 를 로고의 실제 경계로 바꿔 잘라내야 합니다. 경계는
600dpi 로 렌더한 PNG 의 알파 채널에서 재고 `72/600` 을 곱해 pt 로 환산하면 정확합니다.

두 기관의 CI 는 구조가 달라서 다루는 법도 달랐습니다.

- **KRISS** 는 파일 하나가 로고 하나입니다. `kriss-무배경.ai` (워드마크 단독) 를 썼습니다.
  기관명이 들어간 변형을 쓰면 바로 아래 글자와 중복됩니다.
- **KISTI** 는 파일 하나에 크기별 시그니처 5종이 한 페이지에 들어 있고, 모든 조합에
  `www.kisti.re.kr` 과 기관명이 붙어 있습니다. URL 이 궤도 안쪽에 겹쳐 있어 사각형으로는
  잘라낼 수 없습니다. 대신 **색으로 갈라냅니다** — 마크는 파랑(`#1279CA`)·빨강(`#DB1E26`),
  기관명과 URL 은 검정이라, 파랑·빨강 경로만 남기면 마크만 떨어집니다. 그중 가장 큰
  시그니처(경로 9개)를 골랐습니다.

다크 포스터용 KRISS 는 회색 글자만 흰색으로 바꾸고 오렌지 포인트는 남깁니다. 원본 색이
남색 배경에서 거의 보이지 않기 때문입니다. 벡터라 색 값만 바꾸면 되고, 래스터처럼 픽셀을
판별할 필요가 없습니다.

제대로 벡터로 들어갔는지는 PDF 안의 래스터 이미지 개수로 확인합니다. 로고를 PNG 로 넣으면
투명도 때문에 하나당 `/Image` + `/SMask` 로 2개씩 늘어납니다.

```bash
python3 -c "import re;d=open('timenet2026_poster_schedule.pdf','rb').read();print(len(re.findall(rb'/Subtype\s*/Image',d)))"
```

기관 CI 원본 묶음은 `.gitignore` 로 제외했습니다. 공개 저장소이고, 포스터에는 필요한 로고가
이미 벡터로 박혀 있어 저장소에 둘 이유가 없습니다.

## 수정 및 반영 방법

1. HTML 파일을 수정하고, 브라우저로 열어 결과를 확인합니다.
   프로그램을 고쳤으면 포스터의 같은 행도 함께 고칩니다 (바로 위 항목 참고).
2. 배포 자산을 다시 만듭니다. 바뀐 것만 골라 렌더합니다.
   ```bash
   python3 tools/build_assets.py auto
   ```
3. 커밋 후 푸시해 이력을 남깁니다. 생성물과 `.build-stamp` 도 같이 커밋합니다.
   ```bash
   git add *.html *.pdf *.png *.gif tools/
   git commit -m "변경 내용 설명"
   git push
   ```
4. GitHub Pages가 자동으로 다시 게시합니다 (보통 1분 내외).
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
