# -*- coding: utf-8 -*-
"""
Servidor local de conferencia, com recarga automatica.

Duas coisas que o `python -m http.server` cru nao faz, e que custam tempo:

1. Ele entrega .webp e .woff2 como application/octet-stream nesta maquina, e o
   Chrome recusa desenhar a imagem. O sintoma engana: a requisicao volta 200,
   nada aparece no console, e a foto some da pagina. O GitHub Pages serve o
   tipo certo; o servidor de teste e que mentia.

2. Ele nao recarrega a pagina quando o arquivo muda. Aqui um vigia percorre o
   diretorio e, mudou alguma coisa, avisa o navegador por SSE - o `<script>` da
   recarga e injetado em toda resposta HTML, entao nada precisa entrar no site.

Uso:
    python scripts/servidor-local.py [porta]      (padrao: 8099)
"""
import functools
import http.server
import json
import mimetypes
import os
import socketserver
import sys
import threading
import time

TIPOS = {
    ".webp": "image/webp",
    ".avif": "image/avif",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".svg": "image/svg+xml",
}
for _ext, _tipo in TIPOS.items():
    mimetypes.add_type(_tipo, _ext)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
IGNORAR = {".git", "docs", "node_modules", "scripts"}

VERSAO = {"n": 0}

RECARGA = """
<script>
(function(){
  var fonte = new EventSource('/__recarga');
  var atual = null;
  fonte.onmessage = function(e){
    if (atual === null) { atual = e.data; return; }
    if (atual !== e.data) location.reload();
  };
})();
</script>
"""


def impressao_do_site():
    """Assinatura do estado dos arquivos: caminho + mtime + tamanho."""
    marcas = []
    for pasta, subpastas, arquivos in os.walk(RAIZ):
        subpastas[:] = [d for d in subpastas if d not in IGNORAR and not d.startswith(".")]
        for nome in arquivos:
            caminho = os.path.join(pasta, nome)
            try:
                st = os.stat(caminho)
                marcas.append((caminho, int(st.st_mtime), st.st_size))
            except OSError:
                pass
    return hash(tuple(sorted(marcas)))


def vigia():
    anterior = impressao_do_site()
    while True:
        time.sleep(0.6)
        atual = impressao_do_site()
        if atual != anterior:
            anterior = atual
            VERSAO["n"] += 1


class Manipulador(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        if self.path == "/__recarga":
            return self.fluxo_de_recarga()
        return super().do_GET()

    def fluxo_de_recarga(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            while True:
                self.wfile.write(("data: %d\n\n" % VERSAO["n"]).encode())
                self.wfile.flush()
                time.sleep(0.6)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    def send_head(self):
        caminho = self.translate_path(self.path)
        if os.path.isdir(caminho):
            caminho = os.path.join(caminho, "index.html")
        if not caminho.endswith(".html") or not os.path.exists(caminho):
            return super().send_head()

        corpo = open(caminho, "rb").read()
        if b"</body>" in corpo:
            corpo = corpo.replace(b"</body>", RECARGA.encode() + b"</body>", 1)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        import io as _io
        return _io.BytesIO(corpo)

    def end_headers(self):
        if "Cache-Control" not in self._headers_buffer_texto():
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _headers_buffer_texto(self):
        return b"".join(getattr(self, "_headers_buffer", []) or []).decode("latin-1", "ignore")

    def log_message(self, *args):
        pass


class Servidor(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = False   # segundo servidor na mesma porta = requisicao no vazio


threading.Thread(target=vigia, daemon=True).start()

try:
    with Servidor(("", PORTA), functools.partial(Manipulador, directory=RAIZ)) as servidor:
        print("servindo %s em http://localhost:%d/  (recarga automatica ligada)" % (RAIZ, PORTA))
        sys.stdout.flush()
        servidor.serve_forever()
except OSError as erro:
    print("porta %d ocupada: %s" % (PORTA, erro))
    sys.exit(1)
