# -*- coding: utf-8 -*-
"""
Passo 2 de 2 da medida de contraste: A CONTA.

Le o que o `confere-contraste.js` capturou em `medidas/` e responde uma pergunta
so': todo texto da pagina passa no piso da WCAG contra o fundo que esta' DE FATO
atras dele?

Onde ha' letra e' o que os DOIS quadros dizem: o pixel que muda quando o tipo e'
apagado. A caixa sozinha nao serve - dentro dela mora tambem o filete verde do
rotulo e o ponto do selo, e medir a caixa inteira reprova o rotulo pelo proprio
acento decorativo dele.

Do que sobra, o que vale e' o PIOR pixel, nao a media - e' onde a cunha clara
cruza o slogan branco que o contraste cai, e a media esconde exatamente esse
ponto.

Piso: 4,5:1 no texto normal; 3,0:1 no texto grande (>= 24px, ou >= 18,66px em
negrito), como manda a WCAG 2.1 AA.

Uso:
    python -m http.server 8102 --directory .
    node scripts/confere-contraste.js
    python scripts/confere-contraste.py
"""
import json
import os
import re
import sys

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIDAS = os.path.join(RAIZ, "medidas")
PASSO = 1  # pixel a pixel: a letra e' fina, e amostrar de 2 em 2 perde traco
# quanto um pixel precisa mudar entre os dois quadros para contar como letra.
# 24 por canal deixa de fora a borda suavizada, que e' meio fundo e meio letra -
# e' justamente ela que produzia reprovacao falsa nas quatro tentativas do app.
LIMIAR = 24


def canal(v):
    v /= 255.0
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def lumin(c):
    return 0.2126 * canal(c[0]) + 0.7152 * canal(c[1]) + 0.0722 * canal(c[2])


def razao(a, b):
    x, y = sorted((lumin(a), lumin(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


if not os.path.isdir(MEDIDAS):
    sys.exit("nada em medidas/ - rode antes o `node scripts/confere-contraste.js`")

reprovas = 0
for arquivo in sorted(f for f in os.listdir(MEDIDAS) if f.endswith(".json")):
    nome = arquivo[:-5]
    textos = json.load(open(os.path.join(MEDIDAS, arquivo), encoding="utf-8"))
    quadro = Image.open(os.path.join(MEDIDAS, nome + "-fundo.png")).convert("RGB")
    normal = Image.open(os.path.join(MEDIDAS, nome + ".png")).convert("RGB")
    px, pn = quadro.load(), normal.load()
    lar, alt = quadro.size
    if normal.size != quadro.size:
        sys.exit("os dois quadros de %s tem tamanhos diferentes" % nome)

    pior_da_largura = (99.0, "")
    for t in textos:
        cor = tuple(int(n) for n in re.findall(r"\d+", t["cor"])[:3])
        grande = t["tamanho"] >= 24 or (t["tamanho"] >= 18.66 and t["peso"] >= 700)
        piso = 3.0 if grande else 4.5

        x, y, w, h = t["caixa"]
        pior, fundo, pixels = 99.0, None, 0
        for py in range(max(0, int(y)), min(alt, int(y + h)), PASSO):
            for pxx in range(max(0, int(x)), min(lar, int(x + w)), PASSO):
                a, b = px[pxx, py], pn[pxx, py]
                if max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2])) < LIMIAR:
                    continue  # aqui nao ha' letra: e' fundo, ou e' acento decorativo
                pixels += 1
                r = razao(cor, a)
                if r < pior:
                    pior, fundo = r, a
        if fundo is None:
            print("  ATENCAO %s  nenhuma letra encontrada em \"%s\"" % (nome, t["texto"]))
            continue
        if pior < pior_da_largura[0]:
            pior_da_largura = (pior, t["texto"])
        if pior < piso:
            reprovas += 1
            print("  REPROVA %s  %.2f:1 (piso %.1f)  \"%s\"  fundo rgb%s"
                  % (nome, pior, piso, t["texto"], fundo))

    print("%-8s %2d textos medidos · pior par: %.2f:1 em \"%s\""
          % (nome, len(textos), pior_da_largura[0], pior_da_largura[1]))

print("contraste: tudo passa" if not reprovas else "%d reprovacoes" % reprovas)
sys.exit(1 if reprovas else 0)
