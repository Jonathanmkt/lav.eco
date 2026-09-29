#!/usr/bin/env python3
"""
Gera privacidade/index.html e termos/index.html a partir dos .md do assessor juridico.
  --so-excluir-conta gera excluir-conta/index.html a partir de scripts/excluir-conta.md.

  python scripts/gera-paginas-legais.py                     # procura os .md mais recentes
  python scripts/gera-paginas-legais.py --privacidade X.md --termos Y.md

Sem dependencia externa. Le um subconjunto de Markdown: titulos, paragrafos, listas
(com e sem numero), tabelas de pipe, citacao, regua, **negrito**, *italico*, `codigo`,
[texto](url) e <url>. Todo [PENDENTE: ...] vira destaque visual (caixa, se ocupar o
paragrafo inteiro; marca em linha, nos demais casos) e e listado ao fim da execucao.

🔴 O texto e do assessor juridico: este script so o veste. Nao reescreve nada.
⚠️ Saida em URL sem .html: cada pagina e <pasta>/index.html.
"""
import argparse, html, re, sys, unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CASA_JURIDICO = Path(r"C:\Projetos\ESTRUTURA-VIRTUETECH\administrativo\assessor-juridico")

PAGINAS = {
    "privacidade": dict(
        chave="privacidade", pasta="privacidade",
        titulo="Política de Privacidade",
        descricao="Como o Lav.eco coleta, usa, compartilha e protege os dados pessoais de clientes e parceiros, e como exercer os seus direitos pela LGPD.",
    ),
    "termos": dict(
        chave="termos", pasta="termos",
        titulo="Termos de Uso",
        descricao="Os Termos de Uso do Lav.eco: como funciona a lavagem ecológica a seco, a carteira, a cobrança, o cancelamento e as responsabilidades de cada parte.",
    ),
    "excluir-conta": dict(
        chave="excluir-conta", pasta="excluir-conta",
        titulo="Excluir conta e dados",
        descricao="Como pedir a exclusão da sua conta e dos seus dados no app Laveco (Lav.eco), da VirtueTech: passo a passo, o que é excluído e o que é mantido, e por quanto tempo.",
    ),
}

# ─────────────────────────── markdown → html ───────────────────────────
PEND = re.compile(r"\[PENDENTE:[^\]]*\]", re.I)
ITEM = re.compile(r"^\s*([-*+]|\d+[.)])\s+")


def inline(t: str) -> str:
    guardas = []

    def guarda(h):
        guardas.append(h)
        return f"\x00{len(guardas)-1}\x00"

    t = PEND.sub(lambda m: guarda(f'<mark class="pendente-em-linha">{html.escape(m.group(0))}</mark>'), t)
    t = re.sub(r"`([^`]+)`", lambda m: guarda(f"<code>{html.escape(m.group(1))}</code>"), t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: guarda(f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'), t)
    t = re.sub(r"<((?:https?://|mailto:)[^>\s]+)>",
               lambda m: guarda(f'<a href="{html.escape(m.group(1), quote=True)}">{html.escape(m.group(1).replace("mailto:", ""))}</a>'), t)
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: guardas[int(m.group(1))], t)


def slug(t: str, usados: set) -> str:
    s = unicodedata.normalize("NFKD", re.sub(r"[*`_\[\]]", "", t)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "secao"
    base, n = s, 2
    while s in usados:
        s = f"{base}-{n}"
        n += 1
    usados.add(s)
    return s


def celulas(linha: str):
    linha = linha.strip()
    if linha.startswith("|"):
        linha = linha[1:]
    if linha.endswith("|"):
        linha = linha[:-1]
    return [c.strip() for c in linha.split("|")]


def converte(md: str):
    """Devolve (titulo_h1, html_do_corpo, lista_de_pendentes)."""
    linhas = md.replace("\r\n", "\n").split("\n")
    if linhas and linhas[0].strip() == "---":  # some o frontmatter, se houver
        try:
            fim = next(i for i in range(1, len(linhas)) if linhas[i].strip() == "---")
            linhas = linhas[fim + 1:]
        except StopIteration:
            pass
    saida, usados, h1 = [], set(), None
    i, n = 0, len(linhas)
    while i < n:
        s = linhas[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("<!--"):  # comentario HTML: ignora
            while i < n and "-->" not in linhas[i]:
                i += 1
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*?)\s*#*$", s)
        if m:
            nivel, txt = len(m.group(1)), m.group(2)
            i += 1
            if nivel == 1:
                h1 = h1 or re.sub(r"[*`]", "", txt)  # o H1 vira o titulo da capa
                continue
            tag = f"h{nivel}"
            saida.append(f'<{tag} id="{slug(txt, usados)}">{inline(txt)}</{tag}>')
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            saida.append("<hr>")
            i += 1
            continue
        if s.startswith("|") and i + 1 < n and re.match(r"^\s*\|?\s*:?-{2,}", linhas[i + 1]):
            cab = celulas(s)
            i += 2
            corpo = []
            while i < n and linhas[i].strip().startswith("|"):
                corpo.append(celulas(linhas[i]))
                i += 1
            sem_cabecalho = not any(cab)  # tabela "chave | valor": a 1a coluna vira cabecalho de linha
            h = "" if sem_cabecalho else "<thead><tr>" + "".join(f'<th scope="col">{inline(c)}</th>' for c in cab) + "</tr></thead>"
            if sem_cabecalho:
                corpo = [cab] + corpo if any(cab) else corpo
            def celula(j, c, lin):
                if sem_cabecalho and j == 0:
                    return f'<th scope="row">{inline(c)}</th>'
                rot = "" if sem_cabecalho else re.sub(r"[*`]", "", cab[j]) if j < len(cab) else ""
                return f'<td data-rotulo="{html.escape(rot, quote=True)}">{inline(c)}</td>'
            r = "".join("<tr>" + "".join(celula(j, c, lin) for j, c in enumerate(lin)) + "</tr>" for lin in corpo)
            saida.append(f'<div class="tabela" role="region" tabindex="0" aria-label="Tabela"><table>{h}<tbody>{r}</tbody></table></div>')
            continue
        if s.startswith(">"):
            bloco = []
            while i < n and linhas[i].strip().startswith(">"):
                bloco.append(re.sub(r"^\s*>\s?", "", linhas[i]))
                i += 1
            saida.append(f"<blockquote><p>{inline(' '.join(bloco))}</p></blockquote>")
            continue
        if ITEM.match(linhas[i]):
            ordenada = bool(re.match(r"^\d+[.)]", s))
            itens = []
            while i < n and ITEM.match(linhas[i]):
                itens.append(ITEM.sub("", linhas[i]).strip())
                i += 1
                while i < n and linhas[i].strip() and re.match(r"^\s{2,}\S", linhas[i]) and not ITEM.match(linhas[i]):
                    itens[-1] += " " + linhas[i].strip()
                    i += 1
            tag = "ol" if ordenada else "ul"
            saida.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in itens) + f"</{tag}>")
            continue
        bloco = []  # paragrafo
        while i < n and linhas[i].strip() and not re.match(r"^(#{1,4}\s|\||>|-{3,}$)", linhas[i].strip()) \
                and not (bloco and ITEM.match(linhas[i])):
            bloco.append(linhas[i].strip())
            i += 1
        texto = " ".join(bloco)
        if PEND.fullmatch(texto):
            saida.append(f'<aside class="pendente" role="note"><strong>Pendente de preenchimento</strong><p>{inline(texto)}</p></aside>')
        else:
            saida.append(f"<p>{inline(texto)}</p>")
    return h1, "\n".join(saida), PEND.findall(md)


# ─────────────────────────── molde da pagina ───────────────────────────
CSS = r"""
:root{
  --azul950:#04305F; --azul900:#063A7A; --azul800:#0A57C2; --azul700:#0B63DC;
  --azul500:#2C9FEA; --azul300:#58C0F5; --azul100:#C9EBFC; --azul50:#EAF6FE;
  --verde700:#0B7A5A; --verde500:#12B183; --verde50:#EFFBF6;
  --ambar900:#5C3B00; --ambar500:#D98E04; --ambar50:#FFF6E0;
  --tinta:#0B1B2B; --tinta70:#43596E; --tinta45:#5D7086;
  --linha:#DAE1E7; --fundo:#F2F8FF; --papel:#FFFFFF;
  --superficie:var(--papel); --superficie-fundo:var(--fundo); --superficie-suave:var(--azul50);
  --texto-forte:var(--tinta); --texto-apoio:var(--tinta70); --texto-primario:var(--azul700);
  --texto-sobre-marca:var(--papel); --texto-acento:var(--verde700);
  --borda:var(--linha); --borda-acento:var(--verde500);
  --texto-rodape:var(--azul100); --texto-rodape-forte:var(--papel);
  --grad-marca:
    radial-gradient(150% 60% at 112% 110%, var(--verde500) 0%, rgba(18,177,131,0) 62%),
    linear-gradient(140deg, var(--azul900) 0%, var(--azul800) 40%, var(--azul700) 68%, var(--azul500) 100%);
  --cunha:linear-gradient(118deg, rgba(255,255,255,.12) 0%, rgba(255,255,255,.12) 38%, rgba(255,255,255,0) 38.4%);
  --veu-cabecalho:rgba(4,48,95,.25);
  --sombra-card:0 2px 10px rgba(6,58,122,.07);
  --fonte:"Montserrat",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --limite:1080px; --leitura:70ch; --margem:20px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{font-family:var(--fonte);background:var(--superficie-fundo);color:var(--texto-forte);font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}
svg{display:block;max-width:100%}
a{color:var(--texto-primario)}
:focus-visible{outline:3px solid var(--azul300);outline-offset:3px;border-radius:6px}
.limite{width:100%;max-width:var(--limite);margin-inline:auto;padding-inline:var(--margem)}
.pular{position:absolute;left:8px;top:-100px;background:var(--papel);color:var(--texto-forte);padding:8px 14px;border-radius:8px;z-index:10}
.pular:focus{top:8px}

.capa{position:relative;overflow:hidden;isolation:isolate;background:var(--grad-marca);color:var(--texto-sobre-marca);padding-block:clamp(28px,6vw,48px) clamp(40px,8vw,64px)}
.capa::before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(var(--veu-cabecalho),var(--veu-cabecalho)),var(--cunha)}
.marca{display:inline-flex;align-items:center;gap:12px;color:inherit;text-decoration:none}
.marca svg{width:40px;height:40px;flex:none}
.marca b{font-size:22px;font-weight:700;letter-spacing:-.4px}
.capa h1{margin-top:clamp(24px,5vw,40px);font-size:clamp(28px,6vw,44px);line-height:1.12;font-weight:700;letter-spacing:-.8px}
.capa .sub{margin-top:14px;padding-top:14px;border-top:2px solid var(--borda-acento);display:inline-block;font-size:13px;font-weight:600;letter-spacing:.3px}

.texto{width:100%;max-width:calc(var(--leitura) + 2 * var(--margem));margin-inline:auto;padding:clamp(32px,6vw,56px) var(--margem) clamp(48px,8vw,88px)}
.texto h2{margin-top:2.2em;font-size:clamp(22px,3.6vw,28px);line-height:1.25;font-weight:700;letter-spacing:-.4px;scroll-margin-top:16px}
.texto h3{margin-top:1.8em;font-size:19px;line-height:1.3;font-weight:700;scroll-margin-top:16px}
.texto h4{margin-top:1.6em;font-size:16px;font-weight:700}
.texto > :first-child{margin-top:0}
.texto p,.texto ul,.texto ol,.texto blockquote{margin-top:1em}
.texto h2 + *,.texto h3 + *,.texto h4 + *{margin-top:.7em}
.texto ul,.texto ol{padding-left:1.4em}
.texto li{margin-top:.45em;padding-left:.2em}
.texto li::marker{color:var(--texto-acento);font-weight:600}
.texto strong{font-weight:700}
.texto code{font-size:.9em;background:var(--superficie-suave);border-radius:6px;padding:.1em .4em;overflow-wrap:anywhere}
.texto a{overflow-wrap:anywhere}
.texto hr{margin-block:2.4em;border:0;border-top:1px solid var(--borda)}
.texto blockquote{border-left:4px solid var(--borda-acento);background:var(--verde50);padding:4px 18px;border-radius:0 12px 12px 0}

.tabela{margin-top:1.2em;overflow-x:auto;border:1px solid var(--borda);border-radius:14px;background:var(--superficie);box-shadow:var(--sombra-card)}
.tabela table{width:100%;border-collapse:collapse;font-size:14.5px;line-height:1.5}
.tabela th,.tabela td{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--borda)}
.tabela th{background:var(--superficie-suave);font-weight:700;color:var(--texto-forte)}
.tabela tr:last-child td,.tabela tr:last-child th{border-bottom:0}
.tabela th[scope=row]{background:var(--superficie-suave);width:32%}
.tabela td{color:var(--texto-apoio);overflow-wrap:anywhere}
@media (max-width:640px){
  /* celular: cada linha vira um cartao, com o rotulo da coluna antes do valor */
  .tabela table,.tabela tbody,.tabela tr,.tabela td,.tabela th[scope=row]{display:block;width:100%}
  .tabela th[scope=row]{border:0;padding:10px 14px 2px;background:none}
  .tabela td[data-rotulo='']::before{display:none}
  .tabela thead{position:absolute;left:-999px}
  .tabela tr{border-bottom:1px solid var(--borda);padding:6px 0}
  .tabela tr:last-child{border-bottom:0}
  .tabela td{border:0;padding:6px 14px}
  .tabela td::before{content:attr(data-rotulo);display:block;font-size:11px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--texto-acento)}
}

/* ⚠️ [PENDENTE: ...] do assessor juridico: destacado de proposito, para ninguem publicar sem ver */
.pendente{margin-top:1.2em;background:var(--ambar50);border:2px dashed var(--ambar500);border-radius:14px;padding:14px 18px;color:var(--ambar900)}
.pendente strong{display:block;font-size:11px;letter-spacing:.8px;text-transform:uppercase}
.pendente p{margin-top:6px;font-weight:600}
.pendente .pendente-em-linha{border:0;padding:0;background:none}
.pendente-em-linha{background:var(--ambar50);color:var(--ambar900);border:1px dashed var(--ambar500);border-radius:6px;padding:.05em .4em;font-weight:600}

.rodape{background:var(--azul950);color:var(--texto-rodape);padding-block:40px;font-size:13px}
.rodape .limite{display:flex;flex-wrap:wrap;gap:10px 24px;align-items:center;justify-content:space-between}
.rodape strong{color:var(--texto-rodape-forte);font-weight:700;letter-spacing:-.2px;font-size:15px}
.rodape a{color:var(--texto-rodape-forte)}
@media print{.capa{background:none;color:var(--texto-forte)}.capa::before{display:none}.rodape{display:none}}
"""

MARCA_SVG = (
    '<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
    '<rect width="100" height="100" rx="24" fill="currentColor" fill-opacity=".16"/>'
    '<path fill="currentColor" d="M50 18c11.5 12.4 20 22.6 20 32.6C70 62.4 61 71 50 71S30 62.4 30 50.6C30 40.6 38.5 30.4 50 18Z"/>'
    '<path stroke="var(--borda-acento)" stroke-width="5" stroke-linecap="round" d="M36 82h28"/></svg>'
)


def pagina(cfg, corpo):
    t = cfg["titulo"]
    url = f"https://lav.eco/{cfg['pasta']}"
    desc = html.escape(cfg["descricao"], quote=True)
    atual = lambda c: ' aria-current="page"' if cfg["chave"] == c else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(t)} — Lav.eco</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Lav.eco">
<meta property="og:title" content="{html.escape(t)} — Lav.eco">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://lav.eco/assets/marca/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#063A7A">
<link rel="icon" href="/assets/marca/gota.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/marca/gota.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<!-- GERADO por scripts/gera-paginas-legais.py a partir do texto do assessor juridico. Nao edite aqui: edite o .md e gere de novo. -->
<a class="pular" href="#texto">Ir para o texto</a>
<header class="capa">
  <div class="limite">
    <a class="marca" href="/" aria-label="Lav.eco, página inicial">{MARCA_SVG}<b>Lav.eco</b></a>
    <h1>{html.escape(t)}</h1>
    <p class="sub">Lav.eco · lav.eco</p>
  </div>
</header>

<main class="texto" id="texto">
{corpo}
</main>

<footer class="rodape">
  <div class="limite">
    <strong>Lav.eco</strong>
    <span>Carro limpo, consciência também. · 2026</span>
    <nav aria-label="Documentos legais"><a href="/privacidade/"{atual("privacidade")}>Privacidade</a> · <a href="/termos/"{atual("termos")}>Termos</a> · <a href="/excluir-conta/"{atual("excluir-conta")}>Excluir conta</a></nav>
  </div>
</footer>
</body>
</html>
"""


# ─────────────────────────── localizar os .md ───────────────────────────
def acha(palavra):
    if not CASA_JURIDICO.exists():
        return None
    achados = [p for p in CASA_JURIDICO.rglob("*.md") if palavra in p.name.lower()]
    return max(achados, key=lambda p: p.stat().st_mtime) if achados else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--privacidade")
    ap.add_argument("--termos")
    ap.add_argument("--so-excluir-conta", action="store_true",
                    help="gera so excluir-conta/ (fonte: scripts/excluir-conta.md, escrito aqui, nao pelo juridico)")
    a = ap.parse_args()
    if a.so_excluir_conta:
        h1, corpo, pend = converte((RAIZ / "scripts" / "excluir-conta.md").read_text(encoding="utf-8"))
        cfg = PAGINAS["excluir-conta"]
        destino = RAIZ / cfg["pasta"] / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(pagina(cfg, corpo), encoding="utf-8", newline="\n")
        print(f"{destino}  (pendentes: {len(pend)})")
        return
    fontes = {
        "privacidade": Path(a.privacidade) if a.privacidade else acha("privacidade"),
        "termos": Path(a.termos) if a.termos else acha("termos"),
    }
    faltam = [k for k, v in fontes.items() if not v or not v.exists()]
    if faltam:
        print(f"ERRO: .md do assessor juridico ainda nao existe para: {', '.join(faltam)}", file=sys.stderr)
        print(f"      procurado em {CASA_JURIDICO} (nome com 'privacidade' / 'termos'). Nada foi gerado.", file=sys.stderr)
        sys.exit(2)
    todas = {}
    for chave, fonte in fontes.items():
        h1, corpo, pend = converte(fonte.read_text(encoding="utf-8"))
        cfg = PAGINAS[chave]
        destino = RAIZ / cfg["pasta"] / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(pagina(cfg, corpo), encoding="utf-8", newline="\n")
        print(f"{destino}  <-  {fonte}  (H1 do .md: {h1!r})")
        todas[chave] = pend
    print("\n[PENDENTE] restantes:")
    for k, v in todas.items():
        print(f"  {k}: {len(v)}")
        for p in v:
            print(f"    - {p}")


if __name__ == "__main__":
    main()
