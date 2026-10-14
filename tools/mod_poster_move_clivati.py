#!/usr/bin/env python3
"""디자이너 제작 MOD 포스터(JPG)에서 Clivati 발표를 '시각 솔루션' -> '국가 기반시설과 시각동기' 로 옮긴다.

  MOD_poster_01.jpg -> MOD_poster_01_rev1.jpg   (3단 세로 배치)
  MOD_poster_02.jpg -> MOD_poster_02_rev1.jpg   (한 줄 목록 배치)

원본은 건드리지 않는다. 래스터라서 글자를 색으로 떼어낸다:
  1) 영역 안에서 글자(흰색·주황·하늘색)를 soft alpha 로 키잉
  2) 글자 자리를 확산 인페인팅으로 메워 깨끗한 배경을 만들고
  3) 글자 레이어를 새 위치에 다시 합성한다.

    python3 tools/mod_poster_move_clivati.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        """원본 좌표의 글자 조각 (alpha, color)."""
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

    def write(self, img):
        h, w = self.out.shape[:2]
        img[self.y0:self.y0 + h, self.x0:self.x0 + w] = np.clip(self.out, 0, 255).round().astype(np.uint8)


def save(img, src, dst):
    info = Image.open(src).info
    Image.fromarray(img).save(dst, quality=95, subsampling=0, dpi=info.get('dpi', (150, 150)))
    print('->', os.path.relpath(dst, ROOT))


def poster_01():
    src = os.path.join(ROOT, 'MOD_poster_01.jpg')
    img = np.array(Image.open(src).convert('RGB'))
    # 2단(기반시설): 제목 2줄짜리 첫 항목(높이 168) + 109 높이 항목 3개, 3단(솔루션): 109 높이 5개
    col2 = Region(img, 1000, 2015, 1640, 2900)
    col3 = Region(img, 1760, 2015, 2320, 2860)
    H, M = 109, 12
    c3_tops = [2037, 2210, 2383, 2556, 2729]
    cecilia = col3.cut(c3_tops[0] - M, c3_tops[0] + H + M)
    for src_top, dst_top in zip(c3_tops[1:], c3_tops[:-1]):         # 나머지 4개를 한 칸씩 위로
        col3.paste(col3.cut(src_top - M, src_top + H + M), dst_top - M)
    c2_tops = [2037, 2299, 2502, 2706]
    c2_h = [168, H, H, H]
    new_tops = [2037, 2265, 2434, 2603]                              # 간격 60 으로 5개 수용
    for top, h, nt in zip(c2_tops, c2_h, new_tops):
        col2.paste(col2.cut(top - M, top + h + M), nt - M)
    col2.paste(cecilia, 2772 - M, dx=1028 - 1788)                    # 글자 왼쪽 맞춤
    col3.write(img)
    col2.write(img)
    save(img, src, os.path.join(ROOT, 'MOD_poster_01_rev1.jpg'))


def poster_02():
    src = os.path.join(ROOT, 'MOD_poster_02.jpg')
    img = np.array(Image.open(src).convert('RGB'))
    infra = Region(img, 1040, 2050, 2250, 2470)
    sol = Region(img, 1040, 2585, 2250, 2995)
    H, M = 44, 14
    s_tops = [2610, 2690, 2770, 2851, 2931]
    cecilia = sol.cut(s_tops[0] - M, s_tops[0] + H + M)
    for src_top, dst_top in zip(s_tops[1:], s_tops[:-1]):
        sol.paste(sol.cut(src_top - M, src_top + H + M), dst_top - M)
    for top in [2076, 2156, 2236, 2316]:
        infra.paste(infra.cut(top - M, top + H + M), top - M)
    infra.paste(cecilia, 2396 - M)
    sol.write(img)
    infra.write(img)
    save(img, src, os.path.join(ROOT, 'MOD_poster_02_rev1.jpg'))


if __name__ == '__main__':
    poster_01()
    poster_02()
