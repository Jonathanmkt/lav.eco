# Histórico — lav.eco

Diário do repositório, append-only. Entrada mais recente no topo.

## 2026-09-03 — Cartão de compartilhamento em duas proporções

**O quê:** O CEO pediu um cartão de compartilhamento mais no padrão do projeto (fundo azul,
degradê verde no canto, só o logo) e perguntou se um formato mais largo (3:1) era viável. Não é: o
cartão grande do WhatsApp/Facebook recorta a imagem para 1,91:1, e uma arte mais larga perde
margem nas bordas. `scripts/gera-og.py` passou a gerar dois cartões — `assets/marca/og.png`
(1200×630, o principal) e `assets/marca/og-quadrado.png` (1080×1080, novo), os dois com o mesmo
desenho do cabeçalho do site (degradê a 140° + camada radial verde no canto + cunha clara em véu,
gota e wordmark), sem os textos de slogan da versão anterior. `index.html` ganhou a segunda tag
`og:image` para o quadrado.

**Por quê:** a proporção do cartão grande não é escolha de layout do site — é o que o consumidor
da metatag (WhatsApp, Facebook) decidiu e recorta sem avisar. Oferecer as duas variantes cobre o
caso em que o consumidor da tag prefere quadrado, sem abrir mão do formato recomendado como
principal.

**Arquivos-chave:** `scripts/gera-og.py`, `assets/marca/og.png`, `assets/marca/og-quadrado.png`,
`index.html`.

## 2026-09-03 — Site "em breve" do lav.eco

**O quê:** Criação do repositório e da página "em breve" do Lav.eco — marketplace de lavagem de
carro ecológica a seco, feita onde o carro já está parado. Uma página só (`index.html`), sem
build, sem JavaScript, sem dependência de servidor de aplicação, pronta para GitHub Pages na raiz
da branch principal (`CNAME` com `lav.eco`, `.nojekyll`). Inclui marca própria
(`assets/marca/gota.svg`, favicon; `assets/marca/og.png`, cartão de compartilhamento 1200×630,
gerado por script) e quatro medidores em `scripts/` (transbordo/captura, console e rede, e o par
de contraste pelo método dos dois quadros).

**Por quê:** O produto ainda está em construção (`C:\Projetos\APPS\laveco\`), mas o domínio
precisa responder algo antes de o app existir. O design copia a camada `USO` do design system do
app (`ds-laveco.ts`) para variáveis CSS, para que a página não desalinhe da marca quando o app for
ao ar. A marca usa uma gota própria, e não o símbolo do app, porque o símbolo nasceu do pôster de
outra marca e está sob trava de publicação — este site vai ao ar antes de essa trava sair.

**Arquivos-chave:** `index.html`, `design-systems/laveco/ds-laveco.ts` (fonte do design, em
`tecnologia/desenvolvedor-de-sites/` na ESTRUTURA-VIRTUETECH), `assets/marca/`, `scripts/`.
