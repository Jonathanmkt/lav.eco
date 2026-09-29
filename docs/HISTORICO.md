# Histórico — lav.eco

Diário do repositório, append-only. Entrada mais recente no topo.

## 2026-09-29 — Página /excluir-conta (URL pública de exclusão de conta)

**O quê:** Nova página `excluir-conta/index.html`, gerada por `scripts/gera-paginas-legais.py --so-excluir-conta`
a partir de `scripts/excluir-conta.md`: passo a passo (pedido por e-mail a contato@lav.eco, prazo de 15 dias),
o que é excluído e o que é mantido e por quanto tempo, e o caso das fotos enviadas à DeepSeek. Os rodapés do
`index.html` e das páginas legais agora dizem "Privacidade · Termos · Excluir conta".

**Por quê:** a Google Play exige uma URL pública de exclusão de conta para o app publicado (a mesma pendência
que a privacidade marcava como `[PENDENTE]`). Pedido do CEO. Como ainda não há botão de exclusão no app, o
caminho é só por e-mail, e a página diz isso. Diferente de privacidade e termos, o texto-fonte mora neste
repositório (`scripts/excluir-conta.md`), não vem do assessor jurídico; por isso a flag separada, que não
exige os `.md` dele. Motivo dos prazos de retenção (5 anos, 3 anos, 6 meses) não foi documentado aqui: vêm do
texto da página, que cita as leis. Privacidade e termos foram regerados só para trocar o rodapé.

**Arquivos-chave:** `excluir-conta/index.html`, `scripts/excluir-conta.md`, `scripts/gera-paginas-legais.py`, rodapés.

## 2026-09-29 — Páginas /privacidade e /termos, publicadas com pendências à vista

**O quê:** O site ganhou `privacidade/index.html` e `termos/index.html` (URL sem `.html`), geradas
por `scripts/gera-paginas-legais.py` a partir dos `.md` do assessor jurídico
(`administrativo/assessor-juridico/publicaveis/laveco/`, na estrutura). O script só veste o texto
(sem dependência externa, não reescreve nada) e transforma cada `[PENDENTE: ...]` em destaque
visual, listando-os ao fim da execução. O rodapé do `index.html` passou a ter os links
"Privacidade · Termos".

**Por quê:** o teste interno da Google Play exige política de privacidade em endereço público, e
`lav.eco/privacidade` dava 404 (era pendência da T20, login Google). Decisão do CEO em 29/09/2026:
**publicar já com as 5 marcas `[PENDENTE]` visíveis** e construir depois o que o jurídico apontou.
Deixar as marcas destacadas foi de propósito, para ninguém tomar o texto por final.
As 5 marcas no texto: privacidade — recusa do envio de fotos à DeepSeek, mecanismo de
transferência internacional por fornecedor, caminho de exclusão de conta (app e web, exigido pela
Google Play); termos — lista do que cada serviço inclui/exclui e apólice de seguro de
responsabilidade civil.
**Pendências de construção decididas (fora deste repo, ainda não feitas):** consentimento para
envio das fotos à DeepSeek; exclusão de conta; devolução de saldo; revisão da cobrança pela IA;
exclusão automática das fotos em 3 anos. Ao resolver cada uma, regenerar as páginas com o texto
novo do assessor e conferir que a marca correspondente sumiu.

**Arquivos-chave:** `privacidade/index.html`, `termos/index.html`,
`scripts/gera-paginas-legais.py`, `index.html` (rodapé).

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
