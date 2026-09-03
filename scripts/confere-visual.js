/*
  Captura a pagina em Chrome de verdade, nas larguras que importam.
  Existe porque o navegador do harness nao compoe quadro com o painel fechado:
  screenshot devolve "timed out" e medida de animacao devolve numero falso.

  Uso:
    python -m http.server 8099 --directory .      (na raiz do repositorio)
    node scripts/confere-visual.js                (noutro terminal)

  playwright-core nao esta instalado globalmente nesta maquina (20/08/2026);
  PLAYWRIGHT define de onde carrega-lo.
*/
const PLAYWRIGHT = process.env.PLAYWRIGHT_CORE
  || 'C:/Projetos/SITES/luizeduardodf/node_modules/playwright-core';
const URL = process.env.URL || 'http://localhost:8099/';
const LARGURAS = [[360, 740, '360'], [414, 896, '414'], [768, 1024, '768'], [1280, 900, 'desktop']];

const { chromium } = require(PLAYWRIGHT);

(async () => {
  const navegador = await chromium.launch({ channel: 'chrome' });
  for (const [width, height, nome] of LARGURAS) {
    const pagina = await navegador.newPage({ viewport: { width, height } });
    await pagina.goto(URL, { waitUntil: 'networkidle' });

    /* transbordo: nenhum texto pode passar da viewport */
    const transbordo = await pagina.evaluate((w) =>
      [...document.querySelectorAll('h1,h2,p,span,li,a')]
        .filter((e) => { const b = e.getBoundingClientRect(); return b.right > w + 0.5 || b.left < -0.5; })
        .map((e) => e.className || e.tagName), width);

    await pagina.screenshot({ path: `confere-${nome}.png`, fullPage: true });
    console.log(nome, 'transbordo:', transbordo.length ? transbordo : 0);
    await pagina.close();
  }
  await navegador.close();
})();
