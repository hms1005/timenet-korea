#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""확대판 포스터의 글자 배율(--s)을 A0 상자에 들어가는 최대치로 다시 맞춘다.

    python3 tools/fit_large.py            # 등록된 포스터 전부
    python3 tools/fit_large.py schedule   # 시간표 판만

timenet2026_poster_schedule.html 은 인쇄용이라 글자를
최대한 키운 판이다. 크기는 :root 의 --s 하나로 정해지는데, 표에 행이
늘거나 제목이 길어지면 내용이 상자 밖으로 밀려 하단(주관 로고·QR)이
잘린다. 이 스크립트가 표 아래 여유(slack)를 재면서 이진탐색으로 최대
배율을 찾아 HTML 에 써 넣는다. 내용을 고쳤으면 build_assets.py 를
돌리기 전에 이걸 먼저 실행할 것.
"""

import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_assets as B

TARGET = 16      # 표와 하단 블록 사이에 남길 여유(px). 0 이면 딱 붙어 답답하다.
LO, HI = 1.00, 3.20
STEPS = 7

POSTERS = {p['key'].replace('poster_', ''): p['name'] + '.html' for p in B.POSTERS}


def poster_path(variant):
    return os.path.join(B.ROOT, POSTERS[variant])

PROBE = """
<style>html,body{background:#000 !important;} body{padding:0 !important; display:block !important;}
.poster{margin:0 !important;} *,*::before,*::after{animation:none !important; transition:none !important;}</style>
<script>
window.addEventListener('load', function(){ setTimeout(function(){
  var p = document.querySelector('.poster').getBoundingClientRect();
  var c = document.querySelector('.content');
  var bl = document.querySelector('.content > .bottom');
  var cb = c.getBoundingClientRect().bottom;
  var b = bl ? bl.getBoundingClientRect() : {top: cb, bottom: cb};
  var t = document.querySelector('.table-card').getBoundingClientRect();
  document.body.setAttribute('data-r', Math.round(b.top - t.bottom) + ',' + Math.round(p.bottom - b.bottom));
}, 400); });
</script>"""


def knob(poster):
    """맞출 변수 이름. 표 배율을 히어로와 분리한 판(--t)은 그쪽을 맞춘다."""
    src = io.open(poster, encoding='utf-8').read()
    return 't' if re.search(r'--t:\s*[\d.]+;', src) else 's'


def slack(poster, scale):
    """배율을 scale 로 놓고 렌더해 (표 아래 여유, 상자 아래 여유) 를 잰다."""
    k = knob(poster)
    src = re.sub(r'--%s:\s*[\d.]+;' % k, '--%s:%.4f;' % (k, scale),
                 io.open(poster, encoding='utf-8').read(), count=1)
    path = os.path.join(B.BUILD, 'fit_large.html')
    io.open(path, 'w', encoding='utf-8').write(src.replace('</head>', PROBE + '</head>', 1))
    dom = B.chrome(['--virtual-time-budget=8000',
                    '--window-size=%d,2600' % (B.poster_width(poster) + 40),
                    '--dump-dom', 'file://' + path], timeout=30).decode('utf-8', 'replace')
    m = re.search(r'data-r="(-?\d+),(-?\d+)"', dom)
    if not m:
        raise SystemExit('크기 측정 실패: ' + path)
    return int(m.group(1)), int(m.group(2))


def fit(variant):
    poster = poster_path(variant)
    print('%s 확대판:' % variant)
    lo, hi = LO, HI
    for _ in range(STEPS):
        mid = (lo + hi) / 2
        sl, tail = slack(poster, mid)
        print('  --%s=%.4f -> 표 아래 %dpx, 상자 아래 %dpx' % (knob(poster), mid, sl, tail))
        if sl >= TARGET and tail >= 0:
            lo = mid
        else:
            hi = mid

    best = round(lo, 3)
    sl, _ = slack(poster, best)
    k = knob(poster)
    src = io.open(poster, encoding='utf-8').read()
    now = re.search(r'--%s:\s*([\d.]+);' % k, src).group(1)
    io.open(poster, 'w', encoding='utf-8').write(
        re.sub(r'--%s:\s*[\d.]+;' % k, '--%s:%.3f;' % (k, best), src, count=1))
    print('  --%s: %s -> %.3f (표 아래 여유 %dpx)' % (k, now, best, sl))


def main():
    if not os.path.exists(B.CHROME):
        raise SystemExit('Chrome 을 찾을 수 없습니다: ' + B.CHROME)
    os.makedirs(B.BUILD, exist_ok=True)
    want = sys.argv[1:] or sorted(POSTERS)
    for variant in want:
        if variant not in POSTERS:
            raise SystemExit('%s 만 됩니다: %s' % (', '.join(sorted(POSTERS)), variant))
        fit(variant)


if __name__ == '__main__':
    main()
