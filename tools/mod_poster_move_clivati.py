#!/usr/bin/env python3
"""디자이너 제작 MOD 포스터(JPG)를 프로그램 변경에 맞춰 고친다. 원본은 건드리지 않는다.

  MOD_poster_01.jpg -> MOD_poster_01_rev1.jpg   (3단 세로 배치)
  MOD_poster_02.jpg -> MOD_poster_02_rev1.jpg   (한 줄 목록 배치)

하는 일
  1. Clivati 발표를 '시각 솔루션' -> '국가 기반시설과 시각동기' 로 이동
  2. 배치 균형을 위해 제목 두 개를 줄임
       국내외 광기반 시간·주파수 서비스  -> 국내외 광기반 시각주파수 서비스
       전력계통 네트워크 기반 시각동기    -> 전력계통 시각동기
  3. 02 의 일시 '2023' -> '2026'

래스터라서 글자를 색으로 떼어낸다: 영역 안의 글자(흰색·주황·하늘색)를 soft alpha 로
키잉하고, 글자 자리는 확산 인페인팅으로 메워 깨끗한 배경을 만든 뒤, 글자 레이어를
새 위치에 다시 합성한다. 새로 쓰는 제목은 포스터 글꼴과 대조해 맞춘 Pretendard
(01 제목: SemiBold 49px, 02 제목: Bold 46px, 자간 -1) 로 그린다. '6' 은 같은 줄의
'9' 를 180도 돌려 쓴다 (Pretendard 숫자는 Inter 계열이라 6/9 가 점대칭).

    python3 tools/mod_poster_move_clivati.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, 'tools', 'fonts')


def key_alpha(p):
    """글자 alpha. p: float (h,w,3)."""
    r, g, b = p[..., 0], p[..., 1], p[..., 2]
    white = (p.min(axis=2) - 110) / 70
    orange = ((r - b) - 40) / 80
    sky = (g - 115) / 50 * (b > 150)
    a = np.maximum.reduce([white, orange, sky])
    return np.clip(a, 0, 1)


def inpaint(p, mask, iters=1500):
    """mask 위 픽셀을 주변 확산으로 메운다 (가는 글자 획에는 충분)."""
    out = p.copy()
    out[mask] = p[~mask].mean(axis=0) if (~mask).any() else 0
    for _ in range(iters):
        blur = ndimage.uniform_filter(out, size=(3, 3, 1), mode='nearest')
        out[mask] = blur[mask]
    return out


class Region:
    """작업 영역 하나: 원본 글자 레이어(alpha, color)와 인페인팅한 배경을 가진다."""

    def __init__(self, img, x0, y0, x1, y1):
        self.x0, self.y0 = x0, y0
        p = img[y0:y1, x0:x1].astype(np.float64)
        a = key_alpha(p)
        mask = ndimage.binary_dilation(a > 0.02, iterations=8)   # JPEG 링잉 할로까지 포함
        self.bg = inpaint(p, mask)
        a3 = a[..., None]
        color = np.where(a3 >= 0.2, (p - (1 - a3) * self.bg) / np.maximum(a3, 1e-6), p)
        self.color = np.clip(color, 0, 255)
        self.alpha = a
        self.out = self.bg.copy()

    def cut(self, y_top, y_bot, x_left=None, x_right=None):
        """원본 좌표의 글자 조각 (alpha, color, x_left)."""
        ys = slice(y_top - self.y0, y_bot - self.y0)
        xs = slice((x_left - self.x0) if x_left else None, (x_right - self.x0) if x_right else None)
        return self.alpha[ys, xs], self.color[ys, xs], (x_left or self.x0)

    def paste(self, piece, y_top, dx=0):
        a, c, x_left = piece
        y = y_top - self.y0
        x = x_left + dx - self.x0
        h, w = a.shape
        dst = self.out[y:y + h, x:x + w]
        a3 = a[..., None]
        self.out[y:y + h, x:x + w] = a3 * c + (1 - a3) * dst

    def paste_ink(self, piece, ink_left, ink_bottom):
        """조각의 잉크 경계(왼쪽·아래)를 주어진 좌표에 맞춰 붙인다."""
        a, c, _ = piece
        ys, xs = np.where(a > 0.02)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1      # 잉크 경계(연한 AA 포함)
        a, c = a[y0:y1, x0:x1], c[y0:y1, x0:x1]
        ys, xs = np.where(a > 0.5)
        self.paste((a, c, ink_left - xs.min()), ink_bottom - (ys.max() + 1))

    def write(self, img):
        h, w = self.out.shape[:2]
        img[self.y0:self.y0 + h, self.x0:self.x0 + w] = np.clip(self.out, 0, 255).round().astype(np.uint8)


def render(text, font, size, color, track=0):
    """글자를 그려 (alpha, color, 0) 조각으로 만든다. track: 글자마다 더하는 자간(px)."""
    f = ImageFont.truetype(os.path.join(FONT_DIR, font), size)
    im = Image.new('L', (int(f.getlength(text)) + 80, size * 2), 0)
    d = ImageDraw.Draw(im)
    x = 20.0
    for ch in text:
        d.text((x, 20), ch, font=f, fill=255)
        x += f.getlength(ch) + track
    a = np.array(im) / 255.0
    c = np.empty(a.shape + (3,)); c[...] = color
    return a, c, 0


def rotated(piece):
    a, c, _ = piece
    return a[::-1, ::-1], c[::-1, ::-1], 0


def save(img, src, dst):
    info = Image.open(src).info
    Image.fromarray(img).save(dst, quality=95, subsampling=0, dpi=info.get('dpi', (150, 150)))
    print('->', os.path.relpath(dst, ROOT))


SKY = (40, 167, 225)
WHITE = (254, 254, 254)


def poster_01():
    src = os.path.join(ROOT, 'MOD_poster_01.jpg')
    img = np.array(Image.open(src).convert('RGB'))
    H, M = 109, 12                     # 항목 높이(제목 위~연사 아래), 여유

    # 1단: 두 번째 제목 줄임 (잉크 왼쪽 265, 아래 2283 에 맞춤)
    col1 = Region(img, 250, 2225, 920, 2300)
    col1.paste_ink(render('국내외 광기반 시각주파수 서비스', 'Pretendard-SemiBold.otf', 49, SKY), 265, 2283)
    col1.write(img)

    # 3단(솔루션): Clivati 를 떼고 나머지 4개를 한 칸씩 위로
    col3 = Region(img, 1760, 2015, 2320, 2860)
    tops = [2037, 2210, 2383, 2556, 2729]
    cecilia = col3.cut(tops[0] - M, tops[0] + H + M)
    for s, d in zip(tops[1:], tops[:-1]):
        col3.paste(col3.cut(s - M, s + H + M), d - M)
    col3.write(img)

    # 2단(기반시설): 첫 제목을 한 줄로 줄이고 5개를 3단과 같은 간격(173)으로
    col2 = Region(img, 1000, 2015, 1640, 2900)
    col2.paste_ink(render('전력계통 시각동기', 'Pretendard-SemiBold.otf', 49, SKY), 1029, 2080)
    col2.paste(col2.cut(2167 - M, 2205 + M), 2109 - M)               # 김충효 연사 줄 (제목 아래 72)
    for s, d in zip([2299, 2502, 2706], tops[1:4]):
        col2.paste(col2.cut(s - M, s + H + M), d - M)
    col2.paste(cecilia, tops[4] - M, dx=1028 - 1788)                 # 글자 왼쪽 맞춤
    col2.write(img)
    save(img, src, os.path.join(ROOT, 'MOD_poster_01_rev1.jpg'))


def shorten_line(img, y_top, y_bot, title_end, speaker_start, new_title):
    """목록 한 줄의 제목을 새로 쓰고 연사를 그만큼 왼쪽으로 당긴다 (02 용)."""
    reg = Region(img, 1060, y_top - 14, 2300, y_bot + 14)
    reg.paste(reg.cut(y_top - 14, y_bot + 14, x_right=1130), y_top - 14)                      # 불릿
    piece = render(new_title, 'Pretendard-Bold.otf', 46, WHITE, track=-1)
    a = piece[0]; xs = np.where(a > 0.5)[1]; new_w = xs.max() + 1 - xs.min()
    reg.paste_ink(piece, 1141, y_bot)
    reg.paste(reg.cut(y_top - 14, y_bot + 14, x_left=speaker_start - 6), y_top - 14,
              dx=-((title_end - 1141) - new_w))
    reg.write(img)


def poster_02():
    src = os.path.join(ROOT, 'MOD_poster_02.jpg')
    img = np.array(Image.open(src).convert('RGB'))
    H, M = 44, 14

    # 일시 2023 -> 2026: '3'(x 755–789) 을 지우고 '9'(x 962–997) 를 180도 돌려 넣는다
    date = Region(img, 600, 1110, 1120, 1190)
    date.paste(date.cut(1110, 1190, x_right=752), 1110)
    date.paste(date.cut(1110, 1190, x_left=792), 1110)
    nine = date.cut(1120, 1180, x_left=958, x_right=1001)
    date.paste_ink(rotated(nine), 755, 1174)
    date.write(img)

    # 총론 2번째 줄 제목 줄임
    shorten_line(img, 1696, 1739, 1727, 1748, '국내외 광기반 시각주파수 서비스')
    # 기반시설 1번째 줄 제목 줄임
    shorten_line(img, 2076, 2120, 1712, 1736, '전력계통 시각동기')

    # Clivati 줄 이동
    infra = Region(img, 1040, 2050, 2250, 2470)
    sol = Region(img, 1040, 2585, 2250, 2995)
    s_tops = [2610, 2690, 2770, 2851, 2931]
    cecilia = sol.cut(s_tops[0] - M, s_tops[0] + H + M)
    for s, d in zip(s_tops[1:], s_tops[:-1]):
        sol.paste(sol.cut(s - M, s + H + M), d - M)
    for top in [2076, 2156, 2236, 2316]:
        infra.paste(infra.cut(top - M, top + H + M), top - M)
    infra.paste(cecilia, 2396 - M)
    sol.write(img)
    infra.write(img)
    save(img, src, os.path.join(ROOT, 'MOD_poster_02_rev1.jpg'))


if __name__ == '__main__':
    poster_01()
    poster_02()
