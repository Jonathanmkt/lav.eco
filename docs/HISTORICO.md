# Histórico — lav.eco

Diário do repositório, append-only. Entrada mais recente no topo.

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
