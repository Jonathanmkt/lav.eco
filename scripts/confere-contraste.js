/*
  Passo 1 de 2 da medida de contraste: CAPTURA.

  Grava, para cada largura, tres arquivos em `medidas/`:
    <nome>.png        o quadro normal
    <nome>-fundo.png  o mesmo quadro com o tipo APAGADO (a "gemea")
    <nome>.json       a caixa, a cor e o tamanho de cada texto visivel

  A gemea existe por DOIS motivos, e o segundo so' aparece medindo:

  1. Separar letra de fundo dentro de um quadro so' devolve reprovacao falsa - a
     borda suavizada de uma letra branca sobre azul vira um pixel que nenhum
     limiar distingue de fundo claro legitimo (licao ja' paga no `confere-tipo.py`
     do app).
  2. A caixa de um texto contem coisa que NAO e' texto - o filete verde do
     `::before` do rotulo, o ponto do selo. Medir a caixa inteira reprova o
     rotulo pelo proprio acento decorativo dele, que letra nenhuma cobre.

  A conta so' olha, entao, os pixels em que os dois quadros DIFEREM: e' ali, e
  so' ali, que ha' letra.

  Quem faz a conta e' o `confere-contraste.py`, ao lado.

  Uso:
    python -m http.server 8102 --directory .      (na raiz do repositorio)
    node scripts/confere-contraste.js
    python scripts/confere-contraste.py
*/
const fs = require('fs');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_CORE
  || 'C:/Projetos/SITES/luizeduardodf/node_modules/playwright-core';
const URL = process.env.URL || 'http://localhost:8102/';
const LARGURAS = [[360, 740, '360'], [414, 896, '414'], [768, 1024, '768'], [1280, 900, 'desktop']];
const SAIDA = path.join(__dirname, '..', 'medidas');

const { chromium } = require(PLAYWRIGHT);

/* apaga o tipo sem mexer no fundo: cor transparente, e o icone sai junto */
const APAGA = `*{color:transparent!important;text-shadow:none!important}
               svg{visibility:hidden!important}`;

(async () => {
  fs.mkdirSync(SAIDA, { recursive: true });
  const navegador = await chromium.launch({ channel: 'chrome' });

  for (const [width, height, nome] of LARGURAS) {
    const pagina = await navegador.newPage({ viewport: { width, height } });
    await pagina.goto(URL, { waitUntil: 'networkidle' });

    const textos = await pagina.evaluate(() => {
      const alvo = [...document.querySelectorAll('h1,h2,h3,p,span,li,b,a,strong')];
      return alvo.filter((e) => {
        const proprio = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
        const c = e.getBoundingClientRect();
        return proprio && c.width > 2 && c.height > 2;
      }).map((e) => {
        const s = getComputedStyle(e);
        const b = e.getBoundingClientRect();
        return {
          texto: e.textContent.trim().slice(0, 40),
          cor: s.color,
          tamanho: parseFloat(s.fontSize),
          peso: parseInt(s.fontWeight, 10) || 400,
          caixa: [b.x + window.scrollX, b.y + window.scrollY, b.width, b.height],
        };
      });
    });

    await pagina.screenshot({ path: path.join(SAIDA, `${nome}.png`), fullPage: true });
    await pagina.addStyleTag({ content: APAGA });
    await pagina.screenshot({ path: path.join(SAIDA, `${nome}-fundo.png`), fullPage: true });
    fs.writeFileSync(path.join(SAIDA, `${nome}.json`), JSON.stringify(textos, null, 1));

    console.log(nome, '·', textos.length, 'textos capturados');
    await pagina.close();
  }

  await navegador.close();
})();
