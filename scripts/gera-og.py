# -*- coding: utf-8 -*-
"""
Gera os cartoes de compartilhamento (o "link preview" que o WhatsApp desenha).

    assets/marca/og.png           1200x630  (1,91:1) - o do `og:image`
    assets/marca/og-quadrado.png  1080x1080 (1:1)    - onde o quadrado e' a regra

⚠️ **1,91:1 e' o mais largo que sobrevive, e isso NAO e' escolha de gosto.** O
cartao grande do WhatsApp e do Facebook e' recortado nessa proporcao: uma arte
3:1 entra e sai com o topo e a base cortados - some justamente a margem que faz
a marca respirar. Por isso o `og:image` aponta para o 1,91:1, e o 1:1 existe so'
para onde o quadrado e' imposto.

O desenho e' o cabecalho do site reduzido a marca: degrade linear da marca a 140
graus, a camada verde do canto de baixo-direita, a cunha clara em veu, e o logo.
Os hex vem do design system do app (`ds-laveco.ts`); mudou la, muda aqui.

Uso:
    python scripts/gera-og.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARCA = os.path.join(RAIZ, "assets", "marca")

AZUL900, AZUL800, AZUL700, AZUL500 = "#063A7A", "#0A57C2", "#0B63DC", "#2C9FEA"
AZUL100, AZUL950 = "#C9EBFC", "#04305F"
VERDE500 = "#12B183"

BOLD = r"C:\Windows\Fonts\Montserrat-Bold.otf"

# o quanto a mascara e' desenhada maior antes de encolher: e' o que da' borda lisa
# a uma forma curva desenhada por poligono
FINURA = 4


def hexa(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def entre(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def na_rampa(paradas, t):
    for (p0, c0), (p1, c1) in zip(paradas, paradas[1:]):
        if t <= p1:
            f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
            return entre(c0, c1, f)
    return paradas[-1][1]


def eixo(L, A, angulo):
    """O eixo de um degrade linear na convencao do CSS: 0 grau aponta para cima."""
    rad = math.radians(angulo)
    dx, dy = math.sin(rad), -math.cos(rad)
    return dx, dy, abs(L * dx) + abs(A * dy)


def linear(img, angulo, paradas):
    L, A = img.size
    dx, dy, comp = eixo(L, A, angulo)
    px = img.load()
    cx, cy = L / 2, A / 2
    for y in range(A):
        for x in range(L):
            t = (((x - cx) * dx + (y - cy) * dy) / comp) + 0.5
            px[x, y] = na_rampa(paradas, min(1.0, max(0.0, t)))


def canto_verde(img, cor, centro, raio, ate_onde):
    """A camada radial do canto - a mesma do GRADIENTE.marca.cantoAcento."""
    L, A = img.size
    cx, cy = centro[0] * L, centro[1] * A
    rx, ry = raio[0] * L, raio[1] * A
    px = img.load()
    for y in range(A):
        for x in range(L):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            if d < ate_onde:
                px[x, y] = entre(px[x, y], cor, 1 - d / ate_onde)


def cunha(img, opacidade=0.12):
    """O veu claro a 118 graus - o mesmo do GRADIENTE.cunha."""
    L, A = img.size
    dx, dy, comp = eixo(L, A, 118)
    px = img.load()
    cx, cy = L / 2, A / 2
    for y in range(A):
        for x in range(L):
            t = (((x - cx) * dx + (y - cy) * dy) / comp) + 0.5
            if t <= 0.38:
                px[x, y] = entre(px[x, y], (255, 255, 255), opacidade)


def contorno_da_gota(r, altura):
    """
    O contorno EXATO da gota: bico em cima, base circular, e os dois lados sao as
    tangentes do bico ao circulo - nao curva desenhada a olho.

    Do bico P=(0,-H) ao circulo de raio r na origem, o ponto de tangencia T
    satisfaz P·T = r², e com T=(r·sen φ, -r·cos φ) isso da' cos φ = r/H. Dai' o
    contorno e': bico, tangencia da direita, arco por baixo, tangencia da esquerda.
    """
    fi = math.acos(r / altura)
    pontos = [(0.0, -altura)]
    passos = 96
    for i in range(passos + 1):
        a = fi + (2 * math.pi - 2 * fi) * i / passos
        pontos.append((r * math.sin(a), -r * math.cos(a)))
    return pontos


def desenha_marca(cartao, cx, cy, lado, empilhado):
    """
    O logo: a gota na caixa de veu, e o wordmark. Deitado no cartao largo,
    empilhado no quadrado - a mesma marca, dois arranjos.

    A forma e' desenhada numa mascara %dx maior e encolhida: poligono desenhado no
    tamanho final serrilha, e serrilha num logo aparece antes de qualquer outra
    coisa.
    """ % FINURA
    f = FINURA
    mascara = Image.new("L", (lado * f, lado * f), 0)
    m = ImageDraw.Draw(mascara)

    e = lado * f / 100.0  # a mesma regua de 0-100 do `gota.svg`
    r, altura = 20 * e, 32 * e
    centro_gota = (50 * e, 51 * e)
    m.polygon([(centro_gota[0] + x, centro_gota[1] + y)
               for x, y in contorno_da_gota(r, altura)], fill=255)

    # a gota recebe o degrade branco->azul100. Calculado pequeno e ampliado: um
    # degrade linear nao perde nada nessa troca, e evita repetir a conta em alta
    # resolucao dentro da mascara inteira.
    tinta = Image.new("RGB", (60, 60))
    linear(tinta, 160, [(0.0, (255, 255, 255)), (1.0, hexa(AZUL100))])
    tinta = tinta.resize((lado, lado), Image.LANCZOS)

    caixa = Image.new("L", (lado * f, lado * f), 0)
    ImageDraw.Draw(caixa).rounded_rectangle([0, 0, lado * f - 1, lado * f - 1],
                                            radius=int(24 * e), fill=255)

    x0, y0 = int(cx - lado / 2), int(cy - lado / 2)
    veu = Image.new("RGB", (lado, lado), (255, 255, 255))
    cartao.paste(veu, (x0, y0), caixa.resize((lado, lado), Image.LANCZOS).point(lambda v: v * 41 // 255))
    cartao.paste(tinta, (x0, y0), mascara.resize((lado, lado), Image.LANCZOS))

    # o filete verde sob a gota: acento, e nunca portador unico de significado
    filete = Image.new("L", (lado * f, lado * f), 0)
    ImageDraw.Draw(filete).line([(34 * e, 80 * e), (66 * e, 80 * e)],
                                fill=255, width=int(6 * e))
    verde = Image.new("RGB", (lado, lado), hexa(VERDE500))
    cartao.paste(verde, (x0, y0), filete.resize((lado, lado), Image.LANCZOS))


def cartao(L, A, arquivo, empilhado):
    img = Image.new("RGB", (L, A))
    linear(img, 140, [(0.0, hexa(AZUL900)), (0.4, hexa(AZUL800)),
                      (0.68, hexa(AZUL700)), (1.0, hexa(AZUL500))])
    # ⚠️ o raio do canto e' fracao da CAIXA: o cartao quadrado precisa do seu, ou o
    # verde sobe pela lateral inteira em vez de ficar no canto. Copia e' do que se ve.
    raio = (1.44, 1.08) if L > A else (1.15, 0.86)
    canto_verde(img, hexa(VERDE500), (1.08, 1.12), raio, 0.62)
    cunha(img)

    lado = int(min(L, A) * (0.30 if empilhado else 0.34))
    fonte = ImageFont.truetype(BOLD, int(lado * (0.42 if empilhado else 0.60)))
    d = ImageDraw.Draw(img)
    palavra = "Lav.eco"
    larg = d.textlength(palavra, font=fonte)

    if empilhado:
        alt_texto = fonte.size * 1.0
        vao = int(lado * 0.30)
        topo = (A - (lado + vao + alt_texto)) / 2
        desenha_marca(img, L / 2, topo + lado / 2, lado, True)
        d.text((L / 2, topo + lado + vao + alt_texto / 2), palavra, font=fonte,
               fill=(255, 255, 255), anchor="mm")
    else:
        vao = int(lado * 0.34)
        total = lado + vao + larg
        x = (L - total) / 2
        desenha_marca(img, x + lado / 2, A / 2, lado, False)
        d.text((x + lado + vao, A / 2), palavra, font=fonte,
               fill=(255, 255, 255), anchor="lm")

    caminho = os.path.join(MARCA, arquivo)
    img.save(caminho, optimize=True)
    print("gravado: %s  %dx%d  %d bytes" % (caminho, L, A, os.path.getsize(caminho)))


os.makedirs(MARCA, exist_ok=True)
cartao(1200, 630, "og.png", empilhado=False)
cartao(1080, 1080, "og-quadrado.png", empilhado=True)
