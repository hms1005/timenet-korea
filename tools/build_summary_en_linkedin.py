#!/usr/bin/env python3
"""요약 포스터 영문판의 LinkedIn 용 변형판을 만든다.

  timenet2026_poster_summary_en.svg  ->  timenet2026_poster_summary_en_linkedin.svg / .png

원본 SVG 는 건드리지 않는다. 원본에서 머리글(로고·제목·부제), 날짜·장소 아이콘,
QR 코드, 배경 정의를 그대로 가져오고, 가운데 키 비주얼 그림은 빼서 세로를
1536 -> 1280 (4:5, LinkedIn 피드가 자르지 않는 비율) 으로 줄인다. 남는 자리에
발표 제목·연사 글자를 키우고(19.7/16.7px -> 27/21px), 시간 표시는 작은 라벨
(23px -> 16px) 로 세션 제목 오른쪽에 둔다.

    python3 tools/build_summary_en_linkedin.py

rsvg-convert 필요: brew install librsvg
"""

import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'timenet2026_poster_summary_en.svg')
OUT_SVG = os.path.join(ROOT, 'timenet2026_poster_summary_en_linkedin.svg')
OUT_PNG = os.path.join(ROOT, 'timenet2026_poster_summary_en_linkedin.png')

W, H = 1024, 1280
PNG_W, PNG_H = 2560, 3200          # 4:5, 2.5 배

# 글자 크기 (px, 1024 폭 기준)
TALK_PX, SPK_PX, TIME_PX, SESS_PX, DATE_PX = 27, 21, 16, 30, 27

LEFT, RIGHT = 72, 952              # 본문 좌우 여백
COL2 = 521                         # 2단 중 오른쪽 단 시작 x

FONT = ("font-family:'Helvetica Neue',Helvetica,'Apple SD Gothic Neo',"
        "'Noto Sans CJK KR',Arial,sans-serif")

SESSIONS = [
    ('OVERVIEW', '10:15–12:00', [
        ('KST as a Public Utility', 'Myoung-Sun Heo (KRISS)'),
        ('Time Services over KREONET', 'Buseung Cho (KISTI)'),
        ('Desynchronization in the AI Era', 'Jung-Hyun Yoon (INSS)'),
        ('Importance of Resilient Timing', 'Neil Pitman (Adtran/Oscilloquartz)'),
    ]),
    ('TIMING AND THE NATIONAL INFRASTRUCTURES', '13:30–15:55', [
        ('Power Grid Network Timing', 'Chung-Hyo Kim (KEPCO)'),
        ('Terrestrial Navigation Timing', 'Ki-Yeol Seo (KRISO)'),
        ('Timing for VLBI', 'Taehyun Jung (KASI)'),
        ('Quantum Cryptography Timing', 'Dahyun Yeom (IDQ)'),
        ('European Fiber Timing Network', 'Cecilia Clivati (INRiM)'),
    ]),
    ('TIMING SOLUTIONS', '16:00–17:45', [
        ('Clocks &amp; Timing Solutions', 'In-Seop Lee (Microchip)'),
        ('National Precision T&amp;F Network', 'Jeong-Dae Kim (Cisco)'),
        ('Optical Time Sync Solutions', 'Jeong-Ho Lee (SAFRAN)'),
        ('Time as a Service in Asia', 'Byung-Kook Yeom (KTsat)'),
    ]),
]


def element_by_id(svg, elem_id):
    """id 로 요소 하나를 통째로 꺼낸다 (<g> 는 중첩 깊이를 세어 닫는 태그까지)."""
    m = re.search(r'<(\w+)[^>]*\bid="%s"' % re.escape(elem_id), svg)
    if not m:
        raise SystemExit('id 없음: ' + elem_id)
    start, tag = m.start(), m.group(1)
    head_end = svg.index('>', start)
    if svg[head_end - 1] == '/':
        return svg[start:head_end + 1]
    depth, pos = 0, start
    pat = re.compile(r'<%s\b[^>]*?(/?)>|</%s\s*>' % (tag, tag))
    while True:
        m = pat.search(svg, pos)
        if m.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return svg[start:m.end()]
        elif not m.group(1):
            depth += 1
        pos = m.end()


def text(x, y, s, size, fill, weight='bold', anchor='start', extra=''):
    return ('<text x="%s" y="%s" text-anchor="%s" style="%s;font-size:%spx;'
            'font-weight:%s;fill:%s%s">%s</text>'
            % (x, y, anchor, FONT, size, weight, fill, extra, s))


def time_pill(y_top, label):
    """시간 라벨: 오른쪽 여백에 맞춰 끝을 정렬한 작은 주황 알약."""
    w, h = 118, 28
    x = RIGHT - w
    return ('<rect x="%d" y="%d" width="%d" height="%d" rx="5" fill="#ff8200"/>'
            % (x, y_top, w, h)
            + text(x + w / 2, y_top + h - 8, label, TIME_PX, '#ffffff', anchor='middle'))


def talk(x, y, title, speaker):
    return ('<g transform="translate(%d,%d)">'
            '<circle cx="0" cy="-8" r="4.5" fill="#ff8200"/>'
            % (x, y)
            + text(16, 0, title, TALK_PX, '#F3F4F7')
            + text(16, 30, speaker, SPK_PX, '#AEB5C2')
            + '</g>')


def build():
    src = open(SRC, encoding='utf-8').read()

    head = src[:src.index('</defs>') + len('</defs>')]
    head = re.sub(r'<svg\b[^>]*?width="1024"', '<svg width="%d"' % W, head, count=1)
    head = re.sub(r'height="1536"\s+viewBox="0 0 1024 1536"',
                  'height="%d" viewBox="0 0 %d %d"' % (H, W, H), head, count=1)
    head = head.replace('cy="1490" fx="30" fy="1490"', 'cy="%d" fx="30" fy="%d"' % (H - 46, H - 46))
    head = re.sub(r'<title[^>]*>[^<]*</title>',
                  '<title id="title1">Time-Net Korea 2026 — Summary Poster — English (LinkedIn)</title>',
                  head, count=1)
    head = re.sub(r'<desc[^>]*>[^<]*</desc>',
                  '<desc id="desc1">Derived from timenet2026_poster_summary_en.svg: key visual removed, '
                  '4:5 canvas, larger talk text, smaller time labels.</desc>', head, count=1)

    parts = [head]
    parts.append('<rect width="%d" height="%d" x="0" y="0" style="fill:url(#darkPosterBg)"/>' % (W, H))
    parts.append('<circle cx="970" cy="20" r="360" style="fill:url(#warmCornerGlow)"/>')
    parts.append('<circle cx="30" cy="%d" r="330" style="fill:url(#redCornerGlow)"/>' % (H - 46))
    parts.append('<rect width="%d" height="%d" x="0" y="0" style="fill:url(#pattern70)"/>' % (W, H))

    # 머리글: 주최 로고, 제목·부제, 시계 로고 (원본 그대로)
    for eid in ('organizers-top', 'header-4', 'official-logo'):
        parts.append(element_by_id(src, eid))

    # 날짜 · 장소
    y = 250
    cal = element_by_id(src, 'calendar-icon')
    cal = re.sub(r'transform="[^"]*"', 'transform="translate(%d,%d)"' % (LEFT + 4, y - 31), cal, count=1)
    loc = element_by_id(src, 'location-icon')
    loc = re.sub(r'transform="[^"]*"',
                 'transform="matrix(0.81396038,0,0,0.81396038,%s,%d)"' % (573.7, y - 31), loc, count=1)
    parts.append(cal)
    parts.append(text(LEFT + 53, y, '2026. 10. 29. (THU) 09:00–18:00', DATE_PX, '#F3F4F7'))
    parts.append(loc)
    parts.append(text(620, y + 3, 'ST Center, Conference Rm. 2', DATE_PX, '#F3F4F7'))

    # 등록
    y = 292
    parts.append(text(LEFT, y + 22, 'REGISTRATION', SESS_PX, '#FF8200'))
    parts.append(time_pill(y, '09:00–10:00'))
    y += 50
    parts.append('<path d="M %d,%d H %d" stroke="#313b50"/>' % (LEFT, y, RIGHT))

    # 세션 세 개
    ROW = 82          # 발표 한 줄(제목+연사) 간격
    for title, when, talks in SESSIONS:
        y += 46
        parts.append(text(LEFT, y + 22, title, SESS_PX, '#FF8200'))
        parts.append(time_pill(y - 1, when))
        y += 62
        for i, (t, sp) in enumerate(talks):
            x = LEFT if i % 2 == 0 else COL2
            parts.append(talk(x, y, t, sp))
            if i % 2 == 1 and i < len(talks) - 1:
                y += ROW
        y += 52
        if title != SESSIONS[-1][0]:
            parts.append('<path d="M %d,%d H %d" stroke="#313b50"/>' % (LEFT, y, RIGHT))

    # QR: 마지막 세션 아래 오른쪽 구석 (마지막 줄이 2단 모두 차서 같은 줄에는 못 둔다)
    qr_top = H - 96 - 32
    qr = element_by_id(src, 'qr-code')
    qr = re.sub(r'transform="[^"]*"', 'transform="translate(%d,%d)"' % (RIGHT - 96, qr_top), qr, count=1)
    cap = element_by_id(src, 'qr-caption')
    cap = re.sub(r'<text ', '<text style="%s" ' % FONT, cap)
    cap = cap.replace('x="832"', 'x="%d"' % (RIGHT - 96 - 16))
    cap = cap.replace('font-size="15"', 'font-size="18"').replace('font-size="12.5"', 'font-size="15"')
    cap = cap.replace('y="1452"', 'y="%d"' % (qr_top + 32)).replace('y="1478"', 'y="%d"' % (qr_top + 60)) \
             .replace('y="1498"', 'y="%d"' % (qr_top + 84))
    parts.append(cap)
    parts.append(qr)
    parts.append('</svg>\n')

    open(OUT_SVG, 'w', encoding='utf-8').write('\n'.join(parts))
    subprocess.run(['rsvg-convert', '-w', str(PNG_W), '-h', str(PNG_H), '-o', OUT_PNG, OUT_SVG], check=True)
    print('->', os.path.relpath(OUT_SVG, ROOT))
    print('->', os.path.relpath(OUT_PNG, ROOT), '%dx%d' % (PNG_W, PNG_H))


if __name__ == '__main__':
    build()
