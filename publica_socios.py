# -*- coding: utf-8 -*-
"""Gera o painel dos SOCIOS como site proprio, em ~/painel-yoboldro-socios.

Por que repositorio separado: o painel de controladoria e o dos socios moram
no mesmo repo e o link "Controladoria" liga um no outro. Para entregar so a
visao dos socios, a pagina vira index.html de um site que nao tem o outro lado
— e o link para ele sai.

A visao dos socios abre as linhas da DRE e do DFC, mas nao abre lancamento:
o clique no numero esta desligado E a lista de lancamentos nao e embarcada no
arquivo (senao bastaria ver o codigo-fonte da pagina).
"""
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gera_painel as g

DEST = os.path.expanduser('~/painel-yoboldro-socios')
LINK = ('<a href="index.html" title="Abre o painel completo de controladoria">'
        'Controladoria</a>\n')

html = g.pagina(socios=True)
assert html.count(LINK) == 1, 'nao achei o link da controladoria'
html = html.replace(LINK, '')

# CONTROLE: nenhum lancamento no arquivo entregue
m = re.search(r'<script>const D=(\{.*?\});var SOCIOS=', html, re.S)
D = json.loads(m.group(1))
for ent, d in D['ents'].items():
    for reg in ('comp', 'caixa'):
        for mes, b in d[reg].items():
            assert 'itens' not in b, 'lancamento embarcado em %s/%s/%s' % (ent, reg, mes)
assert 'index.html' not in html, 'sobrou link para o painel interno'

if not os.path.isdir(DEST):
    os.makedirs(DEST)
io.open(os.path.join(DEST, 'index.html'), 'w', encoding='utf-8').write(html)
io.open(os.path.join(DEST, 'README.md'), 'w', encoding='utf-8').write(
    u'# Painel Yó / Boldró — visão dos sócios\n\n'
    u'DRE por competência e DFC por caixa, abertos por linha. Gerado por\n'
    u'`publica_socios.py` no repositório de controladoria; não editar à mão.\n\n'
    u'As linhas abrem até o nível da conta. Lançamento individual não existe\n'
    u'neste arquivo — é a diferença em relação ao painel de controladoria.\n')
print('%s/index.html (%.0f KB)' % (DEST, os.path.getsize(os.path.join(DEST, 'index.html')) / 1024))
