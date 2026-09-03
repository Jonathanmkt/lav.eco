# lav.eco — página "em breve"

Uma página só, estática, sem build e sem dependência de servidor de aplicação. Diz o que o
Lav.eco vai ser e que ainda não está no ar.

O produto é um **marketplace de lavagem de carro ecológica a seco, feita onde o carro já está
parado** — na rua ou na garagem do condomínio, em janela de horário marcada. O app está em
construção em `C:\Projetos\APPS\laveco\`; este repositório é só o site.

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `index.html` | **A página inteira** — marcação, CSS e SVG, tudo num arquivo. Sem JavaScript. |
| `assets/marca/gota.svg` | O ícone da aba (favicon). |
| `assets/marca/og.png` | O cartão de compartilhamento, 1200×630 — gerado, não desenhado à mão. |
| `CNAME` | `lav.eco` — o domínio do GitHub Pages. |
| `.nojekyll` | Desliga o Jekyll no Pages: o site é servido como está. |

## O design vem do app, não deste repositório

🔴 **A fonte da verdade das cores é `ds-laveco.ts`**, em
`ESTRUTURA-VIRTUETECH\tecnologia\desenvolvedor-de-sites\design-systems\laveco\`. O CSS daqui
copia a camada `USO` daquele arquivo para variáveis CSS, e **nenhuma regra escreve hex direto** —
quem trocar a marca troca só o bloco `:root`.

Três coisas mudaram na travessia do app para a web, e as três estão comentadas no próprio
`index.html`, com a medida que as justifica:

1. **Véu escuro de 25% sobre o cabeçalho.** No app o degradê da marca ocupa um cabeçalho; aqui
   ocupa uma tela inteira, e esticado ele leva o trecho claro para debaixo do texto branco.
2. **O canto verde encolhe no celular.** O raio é fração da caixa — a mesma conta que no desktop
   deixa o verde num canto, num cabeçalho alto e estreito o sobe até a última linha de texto.
3. **A marca aqui é uma gota, não o símbolo do app.** O símbolo do app nasceu do pôster de outra
   marca e tem trava de publicação até virar vetor próprio (ver `docs/laveco/PLANO.md` no app).
   Este site vai ao ar, então não podia usá-lo.

## Como conferir

Nenhuma das medidas abaixo é opinião — todas devolvem número, e o site não é dado por pronto sem
elas.

```bash
python -m http.server 8102 --directory .

node scripts/confere-visual.js       # transbordo de texto e captura em 360, 414, 768 e desktop
node scripts/confere-console.js      # console, requisições quebradas e a fonte, com cache limpo
node scripts/confere-contraste.js    # captura os dois quadros e as caixas de texto
python scripts/confere-contraste.py  # a conta do contraste, no pior pixel de cada texto
python scripts/gera-og.py            # refaz o cartão de compartilhamento
```

⚠️ **`confere-visual.js` e `confere-contraste.js` esperam `networkidle` e o
`scripts/servidor-local.py` mantém um fluxo SSE aberto para recarga automática** — nesse servidor
a espera nunca termina. Use o `http.server` cru para medir, e o servidor local para desenhar.

⚠️ **O Chrome guarda o HTML em cache mesmo servido pelo `http.server`.** Duas medidas seguidas
podem devolver o mesmo número com o arquivo já alterado — aconteceu aqui. Passe uma consulta nova
a cada rodada: `URL="http://localhost:8102/?v=2" node scripts/...`.

### O que a última medida disse (03/09/2026)

| Medida | Resultado |
|---|---|
| Transbordo de texto em 360, 414, 768 e 1280 | 0 |
| Console, requisições e `Montserrat` carregada, com cache limpo | limpos |
| Contraste, pior par da página inteira | **4,73:1** (a 414px), acima do piso de 4,5:1 |

## Por que a medida de contraste precisa de DOIS quadros

O medidor tira dois retratos da mesma página: o normal e um gêmeo com o tipo apagado. Só os
pixels em que os dois **diferem** são letra; o contraste é lido no quadro limpo, naquele ponto.

São dois motivos, e o segundo só apareceu medindo:

1. Separar letra de fundo dentro de um quadro só devolve reprovação falsa — a borda suavizada de
   uma letra branca sobre azul vira um pixel que nenhum limiar distingue de fundo claro legítimo.
   Essa lição já tinha sido paga quatro vezes no `confere-tipo.py` do app.
2. **A caixa de um texto contém coisa que não é texto.** O filete verde do rótulo e o ponto do
   selo moram dentro dela. Medindo a caixa inteira, o rótulo reprovava por causa do próprio
   acento decorativo — 1,94:1 contra um verde que letra nenhuma cobre.

## Publicação

Pronto para GitHub Pages servindo a branch principal, na raiz. Falta só o que **não é deste
cargo**: criar o repositório remoto, ligar o Pages e apontar o DNS de `lav.eco`. Isso é do
`devops-infra`.
