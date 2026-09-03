/*
  A conferencia que responde "abre limpo?": console sem erro, nenhuma requisicao
  quebrada, e o cache do navegador VAZIO em toda visita.

  O cache limpo e' o ponto: fonte que ja' esta' na maquina de quem desenhou nao
  prova nada sobre a maquina do visitante. Cada largura abre num contexto novo.

  Uso:
    python -m http.server 8102 --directory .
    node scripts/confere-console.js
*/
const PLAYWRIGHT = process.env.PLAYWRIGHT_CORE
  || 'C:/Projetos/SITES/luizeduardodf/node_modules/playwright-core';
const URL = process.env.URL || 'http://localhost:8102/';
const LARGURAS = [[360, 740, '360'], [1280, 900, 'desktop']];

const { chromium } = require(PLAYWRIGHT);

(async () => {
  const navegador = await chromium.launch({ channel: 'chrome' });
  let problemas = 0;

  for (const [width, height, nome] of LARGURAS) {
    const contexto = await navegador.newContext({ viewport: { width, height } });
    const pagina = await contexto.newPage();

    const erros = [];
    pagina.on('console', (m) => { if (m.type() === 'error') erros.push('console: ' + m.text()); });
    pagina.on('pageerror', (e) => erros.push('excecao: ' + e.message));
    pagina.on('requestfailed', (r) => erros.push('requisicao falhou: ' + r.url()));
    pagina.on('response', (r) => { if (r.status() >= 400) erros.push(r.status() + ': ' + r.url()); });

    await pagina.goto(URL, { waitUntil: 'networkidle' });

    /* a fonte da marca precisa ter CARREGADO, nao so' ter sido pedida */
    const montserrat = await pagina.evaluate(() =>
      document.fonts.check('700 24px Montserrat'));

    /* navegacao por teclado: todo foco tem que ser visivel em algum lugar */
    const focaveis = await pagina.evaluate(() =>
      document.querySelectorAll('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])').length);

    problemas += erros.length + (montserrat ? 0 : 1);
    console.log(`${nome} · ${erros.length} problema(s) · Montserrat carregada: ${montserrat}`
      + ` · ${focaveis} elemento(s) focavel(is)`);
    erros.forEach((e) => console.log('   ' + e));
    if (!montserrat) console.log('   a Montserrat nao carregou - o site cairia na fonte do sistema');

    await contexto.close();
  }

  await navegador.close();
  console.log(problemas ? `${problemas} problema(s)` : 'console e rede: limpos');
  process.exit(problemas ? 1 : 0);
})();
