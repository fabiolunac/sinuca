"""Gera os ícones do app (bola 8 sobre o pano verde). Uso: python3 make_icon.py"""
import struct
import zlib


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))


def cover(d):
    """Cobertura anti-aliased a partir da distância com sinal (em pixels)."""
    return max(0.0, min(1.0, 0.5 - d))


def icon(n):
    felt_light, felt_dark = (46, 160, 90), (8, 70, 36)
    ball_light, ball_dark = (70, 70, 78), (6, 6, 8)
    white, ink = (250, 250, 245), (12, 12, 14)

    bx, by, br = 0.5 * n, 0.53 * n, 0.33 * n          # bola
    wx, wy, wr = 0.455 * n, 0.47 * n, 0.135 * n       # disco branco do 8
    sw = 0.022 * n                                     # espessura do traço do "8"
    top = (wx, wy - 0.045 * n, 0.036 * n)             # anel de cima do "8"
    bot = (wx, wy + 0.038 * n, 0.045 * n)             # anel de baixo do "8"

    rows = []
    for y in range(n):
        row = bytearray([0])
        for x in range(n):
            px, py = x + 0.5, y + 0.5

            # pano: gradiente radial a partir do canto superior esquerdo
            t = ((px - 0.3 * n) ** 2 + (py - 0.25 * n) ** 2) ** 0.5 / (0.95 * n)
            c = mix(felt_light, felt_dark, t)

            # sombra da bola no pano
            ds = ((px - bx - 0.03 * n) ** 2 + ((py - by - 0.06 * n) * 1.25) ** 2) ** 0.5
            c = mix(c, (0, 30, 12), 0.55 * max(0.0, 1 - max(0.0, ds - br * 0.85) / (0.12 * n)))

            # bola preta com sombreamento
            db = ((px - bx) ** 2 + (py - by) ** 2) ** 0.5
            a = cover(db - br)
            if a > 0:
                hl = ((px - 0.38 * n) ** 2 + (py - 0.36 * n) ** 2) ** 0.5 / (0.5 * n)
                c = mix(c, mix(ball_light, ball_dark, hl), a)

                # disco branco
                dw = ((px - wx) ** 2 + (py - wy) ** 2) ** 0.5
                c = mix(c, white, cover(dw - wr))

                # "8" como dois anéis
                for cx, cy, r in (top, bot):
                    d = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
                    c = mix(c, ink, cover(abs(d - r) - sw / 2))

                # brilho especular
                dh = ((px - 0.31 * n) ** 2 + ((py - 0.33 * n) * 1.6) ** 2) ** 0.5
                c = mix(c, (255, 255, 255), 0.35 * max(0.0, 1 - dh / (0.06 * n)) * a)

            row += bytes(int(round(v)) for v in c)
        rows.append(bytes(row))

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', n, n, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b''.join(rows), 9))
            + chunk(b'IEND', b''))


for size in (180, 512):
    with open(f'icon-{size}.png', 'wb') as f:
        f.write(icon(size))
