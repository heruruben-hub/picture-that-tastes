#!/usr/bin/env python3
"""Steaming Bakso Bowl -- one delicious picture of food from a single ingredient.

Draws a 1024x1024 PNG of a steaming bowl of bakso (Indonesian meatball
noodle soup) with a hand-rolled pure-stdlib PNG encoder. No PIL, no network.
Run:  python3 main.py   -> writes /output/entry.png (or ./output/entry.png)
"""

import math
import os
import random
import struct
import zlib

W = H = 1024

# ---------------------------------------------------------------- PNG encoder
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, px, w, h):
    """Write a flat RGB bytearray as a truecolour PNG (level 9).

    Tries filter 0 (none) and filter 2 (up) per image and keeps the
    smaller compressed stream -- photographic gradients compress far
    better with the Up filter.
    """
    stride = w * 3
    raw0 = bytearray()
    raw2 = bytearray()
    prev = bytes(stride)
    for y in range(h):
        row = bytes(px[y * stride:(y + 1) * stride])
        raw0.append(0)
        raw0 += row
        raw2.append(2)
        raw2 += bytes((b - p) & 0xFF for b, p in zip(row, prev))
        prev = row
    comp0 = zlib.compress(bytes(raw0), 9)
    comp2 = zlib.compress(bytes(raw2), 9)
    comp = comp0 if len(comp0) <= len(comp2) else comp2
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", comp) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def _idx(x, y):
    return (y * W + x) * 3


def put(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = _idx(x, y)
        px[i] = r
        px[i + 1] = g
        px[i + 2] = b


def blend(x, y, r, g, b, a):
    """Alpha-blend one pixel (a in 0..1)."""
    if 0 <= x < W and 0 <= y < H and a > 0:
        if a >= 1:
            put(x, y, r, g, b)
            return
        i = _idx(x, y)
        px[i] = int(px[i] * (1 - a) + r * a)
        px[i + 1] = int(px[i + 1] * (1 - a) + g * a)
        px[i + 2] = int(px[i + 2] * (1 - a) + b * a)


def lerp(c1, c2, t):
    return tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))


def disc(cx, cy, r, color, alpha=1.0):
    """Soft-edged filled disc."""
    r = int(r)
    x0, x1 = max(0, cx - r - 1), min(W - 1, cx + r + 1)
    y0, y1 = max(0, cy - r - 1), min(H - 1, cy + r + 1)
    for y in range(y0, y1 + 1):
        dy = (y - cy) / (r + 0.5)
        for x in range(x0, x1 + 1):
            dx = (x - cx) / (r + 0.5)
            d2 = dx * dx + dy * dy
            if d2 <= 1.0:
                a = alpha * (1.0 - d2 * d2 * 0.55)
                blend(x, y, color[0], color[1], color[2], a)


def fill_ellipse(cx, cy, rx, ry, c_top, c_bot):
    """Ellipse filled with a vertical gradient."""
    for y in range(max(0, cy - ry), min(H - 1, cy + ry) + 1):
        t = (y - (cy - ry)) / max(1, 2 * ry)
        col = lerp(c_top, c_bot, t)
        ny = (y - cy) / ry
        half = rx * math.sqrt(max(0.0, 1.0 - ny * ny))
        x0, x1 = int(cx - half), int(cx + half)
        for x in range(max(0, x0), min(W - 1, x1) + 1):
            put(x, y, col[0], col[1], col[2])


def radial_disc(cx, cy, r, c_centre, c_edge):
    """Disc shaded from a bright centre to a darker rim (a glossy sphere)."""
    for y in range(max(0, cy - r), min(H - 1, cy + r) + 1):
        for x in range(max(0, cx - r), min(W - 1, cx + r) + 1):
            dx, dy = (x - cx) / r, (y - cy) / r
            d2 = dx * dx + dy * dy
            if d2 <= 1.0:
                t = math.sqrt(d2)
                # light falls from upper-left: brighten that side
                light = 1.0 - 0.55 * t * t - 0.18 * (dx * 0.5 + dy * 0.5)
                col = lerp(c_edge, c_centre, max(0.0, min(1.0, light)))
                put(x, y, col[0], col[1], col[2])


# ------------------------------------------------------- warm wooden table
def draw_table():
    # vertical warm gradient, darker at the top, glowing near the bowl
    for y in range(H):
        t = y / H
        col = lerp((74, 47, 28), (122, 80, 44), t)
        for x in range(W):
            put(x, y, col[0], col[1], col[2])
    # soft warm pool of light behind the bowl
    disc(512, 560, 470, (214, 158, 96), 0.16)
    disc(512, 560, 320, (232, 178, 112), 0.10)
    # wood plank seams, gently wavy
    for k, yb in enumerate((180, 400, 760, 940)):
        for x in range(W):
            y = yb + int(6 * math.sin(x / 170.0 + k * 1.7))
            for dy in range(2):
                blend(x, y + dy, 52, 32, 18, 0.45)
    # faint grain streaks
    rnd = random.Random(7)
    for _ in range(260):
        x = rnd.randint(0, W - 1)
        y = rnd.randint(0, H - 1)
        ln = rnd.randint(40, 160)
        tone = rnd.choice(((96, 62, 34), (150, 102, 58)))
        for s in range(ln):
            blend(x + s, y + int(2 * math.sin(s / 30.0)), tone[0], tone[1], tone[2], 0.10)

# ------------------------------------------------------- bowl, broth, noodles
BOWL_CX, BOWL_CY = 512, 650
BOWL_RX, BOWL_RY = 392, 196
BROTH_RX, BROTH_RY = 338, 148


def draw_bowl():
    # soft contact shadow under the bowl
    disc(512, 868, 380, (30, 18, 10), 0.45)
    disc(512, 868, 320, (30, 18, 10), 0.30)
    # outer ceramic body: cream with warm shading, darker rim at bottom
    fill_ellipse(BOWL_CX, BOWL_CY, BOWL_RX, BOWL_RY,
                 (248, 240, 224), (196, 168, 132))
    # gentle shadow crescent hugging the very bottom rim
    for ry in range(BOWL_RY - 26, BOWL_RY):
        ny = 1.0 - (ry / BOWL_RY) ** 2
        half = BOWL_RX * math.sqrt(max(0.0, ny))
        for x in range(int(BOWL_CX - half), int(BOWL_CX + half) + 1):
            y = BOWL_CY + ry
            if 0 <= y < H:
                blend(x, y, 140, 108, 76, 0.35)
    # teal rim stripe
    for ry in range(BOWL_RY - 14, BOWL_RY - 6):
        ny = 1.0 - (ry / BOWL_RY) ** 2
        half = BOWL_RX * math.sqrt(max(0.0, ny))
        for x in range(int(BOWL_CX - half), int(BOWL_CX + half) + 1):
            y = BOWL_CY - ry
            if 0 <= y < H:
                blend(x, y, 42, 110, 108, 0.85)
    # glossy highlight on the rim, upper left
    disc(330, 540, 90, (255, 252, 240), 0.14)
    disc(300, 528, 46, (255, 255, 250), 0.15)


def draw_broth():
    # rich golden broth, brighter toward the light (upper left)
    for y in range(max(0, BOWL_CY - BROTH_RY), min(H - 1, BOWL_CY + BROTH_RY) + 1):
        ny = (y - BOWL_CY) / BROTH_RY
        half = BROTH_RX * math.sqrt(max(0.0, 1.0 - ny * ny))
        for x in range(int(BOWL_CX - half), int(BOWL_CX + half) + 1):
            nx = (x - BOWL_CX) / BROTH_RX
            t = (ny + 1) / 2
            col = lerp((214, 138, 52), (168, 96, 30), t)
            # warm glow toward upper-left light
            glow = max(0.0, 1.0 - ((nx + 0.35) ** 2 + (ny + 0.4) ** 2) * 0.9)
            col = lerp(col, (240, 178, 84), glow * 0.45)
            put(x, y, col[0], col[1], col[2])
    # oily sheen patches floating on the broth
    rnd = random.Random(21)
    for _ in range(26):
        x = BOWL_CX + rnd.randint(-280, 280)
        y = BOWL_CY + rnd.randint(-95, 95)
        nx, ny = (x - BOWL_CX) / BROTH_RX, (y - BOWL_CY) / BROTH_RY
        if nx * nx + ny * ny < 0.85:
            disc(x, y, rnd.randint(10, 26), (246, 196, 110), 0.28)


def in_broth(x, y):
    nx = (x - BOWL_CX) / (BROTH_RX - 12)
    ny = (y - BOWL_CY) / (BROTH_RY - 10)
    return nx * nx + ny * ny < 1.0


def noodle_strand(y0, amp, wavelength, phase, color, thick):
    """One wavy noodle strand across the broth, clipped to the bowl."""
    x = BOWL_CX - BROTH_RX + 16
    while x < BOWL_CX + BROTH_RX - 16:
        y = int(y0 + amp * math.sin(2 * math.pi * (x - 300) / wavelength + phase)
                + 6 * math.sin(x / 47.0 + phase * 2))
        if in_broth(x, y):
            disc(x, y, thick, color, 0.95)
        x += 2


def draw_noodles():
    rnd = random.Random(42)
    shades = [(246, 214, 138), (238, 198, 110), (252, 226, 158),
              (228, 182, 92), (244, 206, 122)]
    for k in range(15):
        y0 = BOWL_CY - 88 + k * 13 + rnd.randint(-4, 4)
        noodle_strand(y0, rnd.randint(10, 22), rnd.randint(120, 220),
                      rnd.random() * 6.28, shades[k % len(shades)],
                      rnd.randint(6, 8))
    # a lifted tangle of noodles piled in the middle (the hero mound)
    for k in range(9):
        y0 = BOWL_CY - 30 + k * 11
        noodle_strand(y0, 16 + k, 150 + k * 12, k * 0.9,
                      shades[(k + 2) % len(shades)], 8)
    # glossy highlights on the noodle mound
    disc(470, 600, 60, (255, 240, 190), 0.18)
    disc(560, 618, 44, (255, 236, 180), 0.14)

# ------------------------------------------------------- meatballs & garnish
def meatball(cx, cy, r):
    """A glossy brown meatball with a bright specular highlight."""
    radial_disc(cx, cy, r, (196, 128, 74), (112, 62, 30))
    # bumpy texture: small darker/lighter speckles
    rnd = random.Random(cx * 3 + cy)
    for _ in range(r * 2):
        a = rnd.random() * 6.283
        d = rnd.random() * 0.85
        x = int(cx + math.cos(a) * d * r)
        y = int(cy + math.sin(a) * d * r)
        tone = rnd.choice(((150, 92, 48), (222, 158, 96), (128, 72, 36)))
        disc(x, y, rnd.randint(2, 5), tone, 0.5)
    # crisp specular gloss, upper-left -- smaller and softer, not an eye
    disc(cx - int(r * 0.38), cy - int(r * 0.42), int(r * 0.20),
         (255, 244, 220), 0.55)
    disc(cx - int(r * 0.32), cy - int(r * 0.36), int(r * 0.10),
         (255, 255, 250), 0.65)


def draw_meatballs():
    meatball(430, 612, 74)
    meatball(600, 600, 82)
    meatball(516, 668, 66)
    meatball(690, 668, 52)


def herb_leaf(cx, cy, angle, size, color=(52, 128, 58)):
    """A small pointed green leaf (daun bawang / seledri)."""
    for s in range(-size, size + 1):
        w = int(size * 0.42 * (1 - abs(s) / size))
        dx = int(math.cos(angle) * s)
        dy = int(math.sin(angle) * s)
        for t in range(-w, w + 1):
            px_, py_ = cx + dx - int(math.sin(angle) * t), cy + dy + int(math.cos(angle) * t)
            blend(px_, py_, color[0], color[1], color[2], 0.95)


def draw_garnish():
    rnd = random.Random(99)
    # chopped spring onion + celery leaves scattered on the broth
    for _ in range(26):
        x = BOWL_CX + rnd.randint(-300, 300)
        y = BOWL_CY + rnd.randint(-100, 100)
        if in_broth(x, y):
            herb_leaf(x, y, rnd.random() * 6.283, rnd.randint(7, 13),
                      rnd.choice(((46, 122, 52), (74, 158, 60), (34, 100, 48))))
    # bright red chilli slivers -- the glint of heat
    for (cx, cy, ang) in ((392, 566, 0.5), (648, 690, -0.4), (452, 700, 1.1)):
        for s in range(-26, 27):
            w = 6 - abs(s) // 6
            x = int(cx + math.cos(ang) * s)
            y = int(cy + math.sin(ang) * s + 3 * math.sin(s / 9.0))
            for t in range(-w, w + 1):
                blend(x - int(math.sin(ang) * t), y + int(math.cos(ang) * t),
                      214, 52, 34, 0.95)
        disc(cx, cy, 4, (255, 120, 90), 0.8)
    # fried shallot crunch
    for _ in range(40):
        x = BOWL_CX + rnd.randint(-290, 290)
        y = BOWL_CY + rnd.randint(-95, 95)
        if in_broth(x, y):
            disc(x, y, rnd.randint(2, 4), (196, 128, 52), 0.8)


# ------------------------------------------------------- steam, spoon, finish
def steam_wisp(cx, y_top, y_bot, phase, alpha):
    """One translucent curl of steam rising from the bowl."""
    steps = 46
    for k in range(steps):
        t = k / steps
        y = int(y_bot - (y_bot - y_top) * t)
        x = int(cx + 46 * math.sin(t * 6.0 + phase) * (0.35 + 0.65 * t)
                + 26 * t * t)
        r = int(16 + 30 * t)
        a = alpha * (0.55 + 0.45 * math.sin(t * 3.14159)) * (1.0 - t * 0.55)
        disc(x, y, r, (255, 250, 244), a)


def draw_steam():
    steam_wisp(430, 180, 520, 0.0, 0.16)
    steam_wisp(520, 150, 510, 2.1, 0.18)
    steam_wisp(610, 190, 520, 4.2, 0.15)
    steam_wisp(480, 210, 530, 5.6, 0.11)


def draw_spoon():
    """A ceramic spoon resting on the table at the bowl's right edge."""
    # handle, angled down-right
    for s in range(0, 150, 2):
        x = 816 + s
        y = 836 - int(s * 0.22)
        disc(x, y, 8, (228, 216, 194), 0.95)
    # spoon bowl
    fill_ellipse(852, 812, 44, 32, (244, 236, 220), (198, 182, 156))
    fill_ellipse(852, 810, 33, 23, (232, 222, 200), (214, 200, 174))
    disc(838, 800, 10, (255, 255, 250), 0.4)


def finish():
    """Vignette + subtle grain for a warm photographic feel."""
    rnd = random.Random(1234)
    cx, cy = W / 2, H / 2
    for y in range(H):
        for x in range(W):
            i = _idx(x, y)
            dx, dy = (x - cx) / cx, (y - cy) / cy
            d2 = dx * dx + dy * dy
            vig = 1.0 - 0.22 * max(0.0, d2 - 0.55)
            n = rnd.randint(-2, 2)
            px[i] = max(0, min(255, int(px[i] * vig) + n))
            px[i + 1] = max(0, min(255, int(px[i + 1] * vig) + n))
            px[i + 2] = max(0, min(255, int(px[i + 2] * vig) + n))


def output_path():
    if os.environ.get("OUTPUT_PATH"):
        return os.environ["OUTPUT_PATH"]
    try:
        os.makedirs("/output", exist_ok=True)
        probe = "/output/.write_test"
        with open(probe, "wb") as f:
            f.write(b"")
        os.remove(probe)
        return "/output/entry.png"
    except OSError:
        os.makedirs("output", exist_ok=True)
        return "output/entry.png"


def main():
    draw_table()
    draw_bowl()
    draw_broth()
    draw_noodles()
    draw_meatballs()
    draw_garnish()
    draw_steam()
    finish()
    path = output_path()
    size = write_png(path, px, W, H)
    print(f"wrote {path} ({W}x{H}, {size} bytes)")


if __name__ == "__main__":
    main()
