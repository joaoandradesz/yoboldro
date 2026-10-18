# -*- coding: utf-8 -*-
"""Helper do Omie para a Boldro e a YO.

Duas diferencas em relacao ao omie_api.py do painel-amanatopazio:

1. TRANSPORTE. A versao da Amana usa urllib com verificacao de TLS desligada.
   Contra estas duas bases isso derruba a coleta com "Connection reset by peer"
   de forma sistematica, e esgotou 6 retries com espera crescente. O omie.py do
   projeto chama por curl e nunca falhou. Entao o transporte aqui e curl, o
   mesmo que ja esta provado, em vez de uma camada HTTP nova.

2. CREDENCIAIS. As chaves destas empresas vivem em omie-<empresa>/omie.py, na
   pasta do projeto no iCloud, fora deste repositorio. O loader le de la em vez
   de exigir ~/.omie_<empresa>.json — nao ha copia de segredo em lugar novo e
   nada de chave entra no git.

A interface (call, paginas) e a mesma da versao da Amana, de proposito: o
coleta_dash.py e o gera_dash.py nao precisam saber qual transporte esta embaixo.
"""
import json
import os
import re
import subprocess
import time

PROJETO = os.environ.get('OMIE_PROJETO') or os.path.expanduser(
    '~/Library/Mobile Documents/com~apple~CloudDocs/Claude VS')
EMPRESAS = ('boldro', 'yo')
URL = 'https://app.omie.com.br/api/v1/%s/'


def _do_omie_py(emp):
    """Le as constantes K e S do omie.py da empresa, sem importar o modulo.
    K e S costumam vir na mesma linha separados por ';', entao nao ancora no
    inicio da linha."""
    p = os.path.join(PROJETO, 'omie-%s' % emp, 'omie.py')
    if not os.path.exists(p):
        return None
    txt = open(p, encoding='utf-8').read()
    k = re.search(r'(?:^|[;\s])K\s*=\s*["\']([^"\']+)["\']', txt, re.M)
    s = re.search(r'(?:^|[;\s])S\s*=\s*["\']([^"\']+)["\']', txt, re.M)
    return {'app_key': k.group(1), 'app_secret': s.group(1)} if (k and s) else None


CRED = {}
for _e in EMPRESAS:
    _p = os.path.expanduser('~/.omie_%s.json' % _e)
    if os.path.exists(_p):
        CRED[_e] = json.load(open(_p))
        continue
    _c = _do_omie_py(_e)
    if _c:
        CRED[_e] = _c

FALTA = [e for e in EMPRESAS if e not in CRED]
if FALTA:
    raise SystemExit(
        'sem credencial para %s. Esperado ~/.omie_<empresa>.json ou as constantes '
        'K e S em %s/omie-<empresa>/omie.py' % (', '.join(FALTA), PROJETO))


def call(emp, ep, cn, param, tent=6):
    """Chama a API tratando as tres falhas que aparecem numa coleta inteira:
    bloqueio de consumo (pede espera explicita), REDUNDANT (repeticao) e queda
    de conexao. Uma coleta faz ~45 chamadas; sem isso ela morre no meio."""
    c = CRED[emp]
    body = json.dumps({'call': cn, 'app_key': c['app_key'],
                       'app_secret': c['app_secret'], 'param': [param]})
    espera = 5
    for i in range(tent):
        r = subprocess.run(['curl', '-s', '--max-time', '120', '--retry', '2',
                            '-X', 'POST', URL % ep,
                            '-H', 'Content-Type: application/json', '-d', body],
                           capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            if i == tent - 1:
                raise RuntimeError('rede falhou em %s/%s: curl %s %s'
                                   % (ep, cn, r.returncode, (r.stderr or '')[:120]))
            time.sleep(espera)
            espera = min(espera * 2, 60)
            continue
        try:
            j = json.loads(r.stdout)
        except Exception:
            if i == tent - 1:
                raise RuntimeError('resposta ilegivel em %s/%s: %s'
                                   % (ep, cn, r.stdout[:200]))
            time.sleep(espera)
            espera = min(espera * 2, 60)
            continue
        s = json.dumps(j)
        if 'MISUSE_API_PROCESS' in s:
            m = re.search(r'Aguarde (\d+) segundos', s)
            time.sleep(int(m.group(1)) + 3 if m else 60)
            continue
        if 'REDUNDANT' in s:
            time.sleep(26)
            continue
        return j
    raise RuntimeError('bloqueio persistente do Omie em %s/%s' % (ep, cn))


def paginas(emp, ep, cn, raiz, rpp=500, limite=40):
    out = []
    p = 1
    while True:
        r = call(emp, ep, cn, {'pagina': p, 'registros_por_pagina': rpp})
        out += r.get(raiz) or []
        if p >= int(r.get('total_de_paginas') or 1) or p >= limite:
            break
        p += 1
        time.sleep(1)
    return out
