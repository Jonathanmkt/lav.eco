# -*- coding: utf-8 -*-
"""
Gera o cartao de compartilhamento (assets/marca/og.png), 1200x630.

Existe porque rede social nao desenha SVG: o `og:image` precisa ser bitmap. O
desenho aqui e' o mesmo do cabecalho do site - degrade linear da marca a 140
graus, a camada verde do canto de baixo-direita e a cunha clara em veu.

Os hex vem do design system do app (`ds-laveco.ts`); mudou la, muda aqui.

Uso:
    python scripts/gera-og.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

L, A = 1200, 630
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "assets", "marca", "og.png")

AZUL900, AZUL800, AZUL700, AZUL500 = "#063A7A", "#0A57C2", "#0B63DC", "#2C9FEA"
VERDE500 = "#12B183"
AZUL100 = "#C9EBFC"

FONTES = r"C:\Windows\Fonts"
BOLD = os.path.join(FONTES, "Montserrat-Bold.otf")
MEDIO = os.path.join(FONTES, "Montserrat-Medium.otf")
SEMI = os.path.join(FONTES, "Montserrat-SemiBold.otf")


def hexa(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def entre(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def na_rampa(paradas, t):
    """Cor num degrade de paradas [(posicao, cor)], com t de 0 a 1."""
    for (p0, c0), (p1, c1) in zip(paradas, paradas[1:]):
        if t <= p1:
            f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
            return entre(c0, c1, f)
    return paradas[-1][1]


def linear(img, angulo, paradas):
    """Degrade linear no sentido do CSS: 0 grau aponta para cima, cresce no horario."""
    rad = math.radians(angulo)
    dx, dy = math.sin(rad), -math.cos(rad)
    # comprimento da projecao da caixa sobre o eixo do degrade (a conta do CSS)
    comp = abs(L * dx) + abs(A * dy)
    px = img.load()
    cx, cy = L / 2, A / 2
    for y in range(A):
        for x in range(L):
            t = (((x - cx) * dx + (y - cy) * dy) / comp) + 0.5
            px[x, y] = na_rampa(paradas, min(1.0, max(0.0, t)))


def canto_verde(img, cor, centro, raio, ate_onde):
    """A camada radial do canto - a mesma do GRADIENTE.marca.cantoAcento."""
    cx, cy = centro[0] * L, centro[1] * A
    rx, ry = raio[0] * L, raio[1] * A
    px = img.load()
    for y in range(A):
        for x in range(L):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            if d >= ate_onde:
                continue
            a = 1 - d / ate_onde
            px[x, y] = entre(px[x, y], cor, a)


def cunha(img):
    """O veu claro a 118 graus, 12% - o mesmo do GRADIENTE.cunha."""
    rad = math.radians(118)
    dx, dy = math.sin(rad), -math.cos(rad)
    comp = abs(L * dx) + abs(A * dy)
    px = img.load()
    cx, cy = L / 2, A / 2
    branco = (255, 255, 255)
    for y in range(A):
        for x in range(L):
            t = (((x - cx) * dx + (y - cy) * dy) / comp) + 0.5
            if t <= 0.38:
                px[x, y] = entre(px[x, y], branco, 0.12)


img = Image.new("RGB", (L, A))
linear(img, 140, [
    (0.0, hexa(AZUL900)),
    (0.4, hexa(AZUL800)),
    (0.68, hexa(AZUL700)),
    (1.0, hexa(AZUL500)),
])
canto_verde(img, hexa(VERDE500), (1.08, 1.12), (1.44, 1.08), 0.62)
cunha(img)

d = ImageDraw.Draw(img, "RGBA")

# ── a marca: a gota, o mesmo vetor do favicon, desenhada em bitmap ──
gx, gy, gl = 80, 74, 76
d.rounded_rectangle([gx, gy, gx + gl, gy + gl], radius=18, fill=(255, 255, 255, 41))
e = gl / 100.0
gota = [(50, 18), (58, 27), (65, 36), (70, 45), (70, 51), (66, 62), (58, 69), (50, 71),
        (42, 69), (34, 62), (30, 51), (30, 45), (35, 36), (42, 27)]
d.polygon([(gx + x * e, gy + y * e) for x, y in gota], fill=hexa(AZUL100))
d.line([(gx + 36 * e, gy + 82 * e), (gx + 64 * e, gy + 82 * e)],
       fill=hexa(VERDE500), width=int(5 * e), joint="curve")

d.text((gx + gl + 20, gy + gl / 2), "Lav.eco", font=ImageFont.truetype(BOLD, 40),
       fill=(255, 255, 255), anchor="lm")

# ── o selo "EM BREVE" ──
selo = ImageFont.truetype(SEMI, 20)
sx, sy = 80, 236
larg = d.textlength("EM BREVE", font=selo)
d.rounded_rectangle([sx, sy, sx + larg + 66, sy + 46], radius=23,
                    fill=(4, 48, 95, 87), outline=(255, 255, 255, 71), width=2)
d.ellipse([sx + 22, sy + 19, sx + 30, sy + 27], fill=hexa(VERDE500))
d.text((sx + 44, sy + 23), "EM BREVE", font=selo, fill=(255, 255, 255), anchor="lm")

# ── o slogan e a linha de apoio ──
d.text((80, 320), "Carro limpo,", font=ImageFont.truetype(BOLD, 66), fill=(255, 255, 255))
d.text((80, 392), "consciência também.", font=ImageFont.truetype(BOLD, 66), fill=(255, 255, 255))
d.text((80, 492), "Lavagem ecológica a seco, onde o seu carro já está.",
       font=ImageFont.truetype(MEDIO, 26), fill=(255, 255, 255))
d.line([(80, 552), (128, 552)], fill=hexa(VERDE500), width=4)

os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
img.save(SAIDA, optimize=True)
print("gravado:", SAIDA, img.size, os.path.getsize(SAIDA), "bytes")
