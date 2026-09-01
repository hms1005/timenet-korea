#!/usr/bin/env python3
"""Time-Net Korea 2026 배포 자산 빌드.

  timenet_program.html            -> timenet_program.pdf / .png
  timenet_korea_poster_Hyun_dark.html  -> ..._dark.pdf / .png / .gif
  timenet_korea_poster_Hyun_light.html -> ..._light.pdf / .png / .gif

headless Chrome 으로 렌더링한다. 원본 HTML 은 건드리지 않고, 출력 전용
CSS(여백·애니메이션 정지 등)를 입힌 사본을 임시 폴더에 만들어 캡처한다.

    python3 tools/build_assets.py            # check + 전체 렌더
    python3 tools/build_assets.py auto       # 소스가 바뀐 것만 다시 렌더
    python3 tools/build_assets.py check      # 프로그램 <-> 포스터 대조만
    python3 tools/build_assets.py program    # 프로그램 pdf+png 만
    python3 tools/build_assets.py poster     # 포스터(다크+라이트) pdf+png+gif
    python3 tools/build_assets.py poster-dark   # 다크만
    python3 tools/build_assets.py poster-light  # 라이트만
    python3 tools/build_assets.py poster-bi     # 다크 한영병기만
    python3 tools/build_assets.py poster-light-bi  # 라이트 한영병기만
    python3 tools/build_assets.py poster-bi-large  # 다크 한영병기 확대판만
    python3 tools/build_assets.py poster-light-bi-large  # 라이트 한영병기 확대판만

Pillow 필요: python3 -m pip install pillow
"""

import html
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
BUILD  = os.path.join(tempfile.gettempdir(), 'timenet-build')

PROGRAM = os.path.join(ROOT, 'timenet_program.html')

# 다크·라이트 두 벌을 같은 방식으로 뽑는다. page 는 포스터 바깥 여백에 깔리는 색으로,
# 캡처가 1px 어긋나도 반대색 테두리가 비치지 않게 각 포스터의 바탕에 맞춘다.
POSTERS = [
    {'key': 'poster',       'name': 'timenet_korea_poster_Hyun_dark',  'page': '#05070d'},
    {'key': 'poster_light', 'name': 'timenet_korea_poster_Hyun_light', 'page': '#F8F7F4'},
    {'key': 'poster_bi',    'name': 'timenet_korea_poster_Hyun_dark_bilingual', 'page': '#05070d'},
    {'key': 'poster_light_bi', 'name': 'timenet_korea_poster_Hyun_light_bilingual', 'page': '#F8F7F4'},
    # 인쇄용 확대판. 내용은 병기판과 같고 글자만 키웠다(tools/fit_large.py 참고).
    {'key': 'poster_bi_large', 'name': 'timenet_korea_poster_Hyun_dark_bilingual_large', 'page': '#05070d'},
    {'key': 'poster_light_bi_large', 'name': 'timenet_korea_poster_Hyun_light_bilingual_large', 'page': '#F8F7F4'},
]
for _p in POSTERS:
    _p['src'] = os.path.join(ROOT, _p['name'] + '.html')

# 쓰지 않게 된 판은 old/ 로 옮겨 보관한다. 목록에서 지우는 대신 소스가
# 없으면 건너뛴다. 나중에 되돌려 놓으면 손댈 것 없이 다시 빌드된다.
_gone = [p for p in POSTERS if not os.path.exists(p['src'])]
POSTERS = [p for p in POSTERS if os.path.exists(p['src'])]
if _gone:
    print('건너뜀(소스 없음): ' + ', '.join(p['name'] for p in _gone))
if not POSTERS:
    raise SystemExit('포스터 소스를 하나도 찾지 못했습니다.')
POSTER = POSTERS[0]['src']          # 대조(check) 기준은 목록의 첫 포스터

PROGRAM_W = 1000          # 렌더 폭(px). 화면용 여백은 아래 CSS 로 넓힌다.
POSTER_W  = 920           # --poster-w 가 없는 옛 포스터의 기본 폭
GIF_LOOP  = 6.0           # GIF 한 바퀴(초)
GIF_N     = 30            # 프레임 수 -> 200ms/프레임
GIF_SCALE = 1             # GIF 배율(웹 공유용, 인쇄용 아님)


# --------------------------------------------------------------------------
# Chrome

def chrome(args, timeout=25, profile='profile'):
    """headless Chrome 1회 실행. 무한 CSS 애니메이션이 있으면 종료하지 않고
    매달리는 경우가 있어, 결과 파일은 이미 쓰인 뒤이므로 timeout 으로 끊는다."""
    cmd = [CHROME, '--headless', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
           '--force-color-profile=srgb', '--disable-lcd-text',
           '--user-data-dir=' + os.path.join(BUILD, profile)] + args
    try:
        return subprocess.run(cmd, timeout=timeout, capture_output=True).stdout
    except subprocess.TimeoutExpired as e:
        return e.stdout or b''


def measure(src, window_w, selector=None):
    """페이지를 띄워 실제 렌더 크기를 읽어온다. (w, h)"""
    probe = """
<script>
window.addEventListener('load', function(){
  setTimeout(function(){
    var el = %s;
    var r = el.getBoundingClientRect();
    document.body.setAttribute('data-w', Math.ceil(r.width));
    document.body.setAttribute('data-h', Math.ceil(el === document.documentElement
        ? document.documentElement.scrollHeight : r.height));
  }, 250);
});
</script>""" % ("document.querySelector('%s')" % selector if selector else 'document.documentElement')
    path = os.path.join(BUILD, 'measure.html')
    io.open(path, 'w', encoding='utf-8').write(src.replace('</head>', probe + '</head>', 1))
    dom = chrome(['--virtual-time-budget=8000', '--window-size=%d,1400' % window_w,
                  '--dump-dom', 'file://' + path], timeout=25).decode('utf-8', 'replace')
    m = re.search(r'data-w="(\d+)" data-h="(\d+)"', dom)
    if not m:
        raise SystemExit('크기 측정 실패: ' + path)
    return int(m.group(1)), int(m.group(2))


def screenshot(src, dst, w, h, scale=2, timeout=25):
    path = os.path.join(BUILD, 'shot_%s.html' % os.path.basename(dst))
    io.open(path, 'w', encoding='utf-8').write(src)
    chrome(['--screenshot=' + dst, '--window-size=%d,%d' % (w, h),
            '--force-device-scale-factor=%g' % scale,
            '--virtual-time-budget=12000', 'file://' + path], timeout=timeout)
    if not os.path.exists(dst):
        raise SystemExit('스크린샷 실패: ' + dst)


def pdf_pages(path):
    d = io.open(path, 'rb').read()
    return d.count(b'/Type /Page') - d.count(b'/Type /Pages')


def poster_width(path):
    """포스터마다 폭이 다르다. A0 비율을 쓰는 포스터는 --poster-w 로 폭을 선언하고,
    높이는 aspect-ratio 가 정한다. 선언이 없으면 옛 고정 폭을 쓴다."""
    m = re.search(r'--poster-w\s*:\s*(\d+)px', io.open(path, encoding='utf-8').read())
    return int(m.group(1)) if m else POSTER_W


def print_pdf(src, dst, w, h):
    """@page 를 콘텐츠 크기에 맞춰 1페이지로 뽑는다. 인쇄 레이아웃이 1~2px
    더 커져 빈 2페이지가 생기는 경우가 있어 높이를 조금씩 늘려 재시도한다."""
    for extra in (0, 4, 8, 16):
        page = '<style>@page{size:%dpx %dpx; margin:0;} @media print{html,body{overflow:hidden !important;}}</style>' % (w, h + extra)
        path = os.path.join(BUILD, 'print.html')
        io.open(path, 'w', encoding='utf-8').write(src.replace('</head>', page + '</head>', 1))
        chrome(['--print-to-pdf=' + dst, '--no-pdf-header-footer',
                '--window-size=%d,%d' % (w, h + extra),
                '--virtual-time-budget=12000', 'file://' + path])
        if os.path.exists(dst) and pdf_pages(dst) == 1:
            return h + extra
    raise SystemExit('PDF 를 1페이지로 만들지 못했습니다: ' + dst)


# --------------------------------------------------------------------------
# 출력용 CSS

FREEZE = '<style>*,*::before,*::after{animation:none !important; transition:none !important;}</style>'
EXACT  = '<style>*{-webkit-print-color-adjust:exact !important; print-color-adjust:exact !important;}</style>'

PROGRAM_CSS = EXACT + """
<style>
  html,body{background:#FFFFFF !important;}
  body{padding:36px 32px !important; width:%dpx !important;}   /* 화면용 8px 여백은 문서로는 너무 좁다 */
  .program{max-width:none !important; margin:0 !important;}
</style>""" % PROGRAM_W

def poster_css(page):
    return EXACT + """
<style>
  html,body{background:%s !important;}
  body{padding:0 !important; display:block !important;}         /* 포스터 가장자리에 딱 맞게 */
  .poster{margin:0 !important; box-shadow:none !important; border:none !important;}
</style>""" % page


def dress(path, css, extra=''):
    s = io.open(path, encoding='utf-8').read()
    return s.replace('</head>', css + extra + '</head>', 1)


# --------------------------------------------------------------------------
# GIF: 애니메이션을 프레임 단위로 정지시켜 캡처

def gif_frame_css(t):
    """t초 시점에서 애니메이션을 얼려 렌더한다.

    원본은 주기가 제각각(빔 4.8~7.4s, 펄스 3.4s)이라 그대로 이어붙이면 루프
    이음매가 튄다. 렌더할 때만 각 주기를 GIF_LOOP 의 약수로 스냅하고, 정지
    시점을 [0, 주기) 안의 음수 delay 로 정규화한다. 양수 delay 를 남기면
    '시작 전' 상태로 그려져 이음매가 깨진다."""
    return """
<script>
window.addEventListener('load', function(){
  var LOOP = %f, T = %f;
  document.querySelectorAll('.fiber-bg .beam, .fiber-bg .pulse').forEach(function(el){
    var cs  = getComputedStyle(el);
    var dur = parseFloat(cs.animationDuration) || LOOP;
    var del = parseFloat(cs.animationDelay) || 0;
    var snapped = LOOP / Math.max(1, Math.round(LOOP / dur));
    var L = ((T - del) %% snapped + snapped) %% snapped;
    el.style.animationDuration  = snapped + 's';
    el.style.animationPlayState = 'paused';
    el.style.animationDelay     = (-L) + 's';
  });
});
</script>""" % (GIF_LOOP, t)


def build_gif(poster, w, h, dst):
    from PIL import Image
    frames_dir = os.path.join(BUILD, 'frames')
    shutil.rmtree(frames_dir, ignore_errors=True)
    os.makedirs(frames_dir)

    for i in range(GIF_N):
        src = dress(poster['src'], poster_css(poster['page']), gif_frame_css(GIF_LOOP * i / GIF_N))
        io.open(os.path.join(BUILD, 'fr%03d.html' % i), 'w', encoding='utf-8').write(src)

    def shot(i):
        dstf = os.path.join(frames_dir, 'f%03d.png' % i)
        chrome(['--screenshot=' + dstf, '--window-size=%d,%d' % (w, h),
                '--force-device-scale-factor=%g' % GIF_SCALE,
                '--virtual-time-budget=12000',
                'file://' + os.path.join(BUILD, 'fr%03d.html' % i)],
               timeout=20, profile='p%d' % (i % 4))
        return os.path.exists(dstf)

    with ThreadPoolExecutor(max_workers=4) as ex:
        if not all(ex.map(shot, range(GIF_N))):
            raise SystemExit('GIF 프레임 렌더 실패')

    ims = [Image.open(os.path.join(frames_dir, 'f%03d.png' % i)).convert('RGB')
           for i in range(GIF_N)]
    # 디더링을 켜면 노이즈 때문에 용량이 5배로 뛴다. 어두운 그라데이션이라
    # 디더 없이도 밴딩이 눈에 띄지 않는다.
    pal = ims[0].quantize(colors=255, method=Image.MEDIANCUT)
    q = [i.quantize(palette=pal, dither=Image.Dither.NONE) for i in ims]
    q[0].save(dst, save_all=True, append_images=q[1:],
              duration=int(GIF_LOOP * 1000 / GIF_N), loop=0, optimize=True, disposal=1)


# --------------------------------------------------------------------------
# 프로그램 <-> 포스터 대조

def rows(path, table_start, cell_re):
    s = io.open(path, encoding='utf-8').read()
    s = re.sub(r'<!--.*?-->', '', s[s.index(table_start):], flags=re.S)
    body = s[:s.index('</table>') if '</table>' in s else len(s)]
    out = []
    for tr in re.findall(r'<tr\b.*?</tr>', body, re.S):
        cells = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', c))).strip()
                 for c in re.findall(cell_re, tr, re.S)]
        if cells:
            out.append(cells)
    return out


def check():
    """시간·연사만 대조한다. 제목은 포스터가 줄여 쓰므로 비교하지 않는다."""
    return all([check_one(p) for p in POSTERS])


def check_one(poster):
    prog = rows(PROGRAM, '<tbody>', r'<td\b[^>]*>(.*?)</td>')
    post = rows(poster['src'], '<table class="prog">', r'<t[dh]\b[^>]*>(.*?)</t[dh]>')

    def keyed(rs):
        d = {}
        for r in rs:
            if r and re.match(r'^\d{2}:\d{2}', r[0]):
                d[r[0]] = r[-1] if len(r) >= 3 else ''
        return d

    a, b = keyed(prog), keyed(post)
    problems = []
    for t in sorted(set(a) | set(b)):
        if t not in a:
            problems.append('%s  포스터에만 있음' % t)
        elif t not in b:
            problems.append('%s  프로그램에만 있음' % t)
        else:
            pa = a[t].replace('개회 ', '').replace(' ', '')
            pb = b[t].replace(' ', '')
            # 개회사 두 줄은 프로그램 쪽이 이름 정렬용 마크업이라 공백만 다르다
            if pa != pb:
                problems.append('%s  프로그램 "%s"  <->  포스터 "%s"' % (t, a[t], b[t]))
    label = poster['name'].replace('timenet_korea_poster_Hyun_', '')
    if problems:
        print('연사/시간 불일치 (%s):' % label)
        for p in problems:
            print('  - ' + p)
    else:
        print('연사/시간: 프로그램 <-> 포스터(%s) 일치 (%d행)' % (label, len(a)))
    return not problems


# --------------------------------------------------------------------------

def build_program():
    src = dress(PROGRAM, PROGRAM_CSS, FREEZE)
    w, h = measure(src, PROGRAM_W + 40)
    png = os.path.join(ROOT, 'timenet_program.png')
    pdf = os.path.join(ROOT, 'timenet_program.pdf')
    screenshot(src, png, PROGRAM_W, h, scale=2)
    used = print_pdf(src, pdf, PROGRAM_W, h)
    print('  timenet_program.png  %dx%d (2x)  %.1f KB' % (PROGRAM_W * 2, h * 2, os.path.getsize(png) / 1024))
    print('  timenet_program.pdf  1p %dx%dpx  %.1f KB' % (PROGRAM_W, used, os.path.getsize(pdf) / 1024))


def build_poster(poster):
    src = dress(poster['src'], poster_css(poster['page']), FREEZE)
    pw = poster_width(poster['src'])
    w, h = measure(src, pw + 40, selector='.poster')
    base = os.path.join(ROOT, poster['name'])
    png, pdf, gif = base + '.png', base + '.pdf', base + '.gif'
    screenshot(src, png, w, h, scale=2)
    used = print_pdf(src, pdf, w, h)
    build_gif(poster, w, h, gif)
    tag = poster['name'].replace('timenet_korea_poster_Hyun', '...')
    print('  %s.png  %dx%d (2x)  %.1f KB' % (tag, w * 2, h * 2, os.path.getsize(png) / 1024))
    print('  %s.pdf  1p %dx%dpx (1:%.4f)  %.1f KB' % (tag, w, used, used / float(w), os.path.getsize(pdf) / 1024))
    print('  %s.gif  %dx%d %d프레임 %.0f초 루프  %.1f KB'
          % (tag, w * GIF_SCALE, h * GIF_SCALE, GIF_N, GIF_LOOP, os.path.getsize(gif) / 1024))


STAMP = os.path.join(ROOT, 'tools', '.build-stamp')


def digest(path):
    import hashlib
    return hashlib.md5(io.open(path, 'rb').read()).hexdigest()


def read_stamp():
    prev = {}
    if os.path.exists(STAMP):
        for line in io.open(STAMP, encoding='utf-8'):
            if ' ' in line:
                h, n = line.strip().split(' ', 1)
                prev[n] = h
    return prev


def stale():
    """마지막 빌드 이후 내용이 바뀐 소스를 돌려준다."""
    prev = read_stamp()
    now = {'program': digest(PROGRAM)}
    for p in POSTERS:
        now[p['key']] = digest(p['src'])
    return [k for k, v in now.items() if prev.get(k) != v], now


def write_stamp(now, built):
    """이번에 실제로 다시 만든 것만 갱신한다. 전부 덮어쓰면 poster-bi 처럼
    일부만 렌더했을 때 나머지가 최신인 것처럼 기록돼 auto 가 건너뛴다."""
    merged = read_stamp()
    merged.update({k: v for k, v in now.items() if k in built})
    io.open(STAMP, 'w', encoding='utf-8').write(
        ''.join('%s %s\n' % (v, k) for k, v in sorted(merged.items())))


def main():
    if not os.path.exists(CHROME):
        raise SystemExit('Chrome 을 찾을 수 없습니다: ' + CHROME)
    os.makedirs(BUILD, exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    built = set()

    if what == 'auto':
        todo, now = stale()
        if not todo:
            print('변경 없음 - 다시 만들 자산이 없습니다.')
            return
        print('변경 감지: ' + ', '.join(todo))
        check()
        if 'program' in todo:
            print('프로그램 렌더링...')
            build_program()
        for p in POSTERS:
            if p['key'] in todo:
                print('포스터(%s) 렌더링... (GIF 30프레임, 1~2분)'
                      % p['name'].replace('timenet_korea_poster_Hyun_', ''))
                build_poster(p)
        write_stamp(now, todo)
        return

    if what in ('all', 'check'):
        ok = check()
        if what == 'check':
            sys.exit(0 if ok else 1)
    if what in ('all', 'program'):
        print('프로그램 렌더링...')
        build_program()
        built.add('program')
    if what in ('all', 'poster', 'poster-dark', 'poster-light', 'poster-bi', 'poster-light-bi', 'poster-bi-large', 'poster-light-bi-large'):
        want = {'poster-dark': ['poster'], 'poster-light': ['poster_light'],
                'poster-bi': ['poster_bi'],
                'poster-light-bi': ['poster_light_bi'],
                'poster-bi-large': ['poster_bi_large'],
                'poster-light-bi-large': ['poster_light_bi_large']}.get(what, [p['key'] for p in POSTERS])
        for p in POSTERS:
            if p['key'] in want:
                print('포스터(%s) 렌더링... (GIF 30프레임, 1~2분)'
                      % p['name'].replace('timenet_korea_poster_Hyun_', ''))
                build_poster(p)
                built.add(p['key'])
    if what in ('all', 'program', 'poster', 'poster-dark', 'poster-light', 'poster-bi', 'poster-light-bi', 'poster-bi-large', 'poster-light-bi-large'):
        _, now = stale()
        write_stamp(now, built)


if __name__ == '__main__':
    main()
