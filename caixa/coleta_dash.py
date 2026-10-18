# -*- coding: utf-8 -*-
"""Coleta do dashboard de caixa da Boldro e da YO.

Adaptado de painel-amanatopazio/caixa/coleta_dash.py. Tres coisas mudaram, e
cada uma por um motivo medido nestas bases:

1. SALDO = ancora + movimento REALIZADO, nao + movimento 'Conciliado'.
   A conciliacao formal quase nao e usada aqui: 1.039 dos 1.179 movimentos do
   Santander da Boldro e 1.190 dos 1.223 do Bradesco da YO estao como
   'Nao conciliado'. A formula da Amana devolve lixo nestas bases (-0,00 na
   Boldro, -111.017,19 na YO). Realizado = tudo que nao e 'Previsto'.

2. O EXTRATO E LIDO MES A MES. Em periodo longo o ListarExtrato trunca: a
   ContaMax devolve 53 movimentos em setembro, 96 em agosto-setembro e 93 em
   julho-setembro, e nesse ultimo o saldo de 30/09 desaparece. Periodo longo
   mente, e o saldo vem do nSaldo do ultimo movimento realizado.

3. AGENDA PREVISTA e um bloco proprio, separado dos titulos em aberto. Na
   Boldro ha 30 compromissos de outubro lancados como 'Previsto' na conta
   Fundo Fixo (R$ 80.159,10) que nao aparecem como titulo a vencer.

Uso:  python3 caixa/coleta_dash.py [dd/mm/aaaa]   -> grava dados_caixa.json
"""
import collections
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omie_api import call, paginas  # noqa: E402

R2 = (lambda v: round((v or 0) + 0.0, 2))


def dt(s):
    return datetime.datetime.strptime(s, '%d/%m/%Y').date()


# ---------------------------------------------------------------- ancora
# Saldo REALIZADO por conta na ultima data fechada. Atualizar a cada fechamento.
# Conferido em 16/10/2026 contra o extrato: a YO fecha exata; a Boldro devolve
# R$ 599.861,24 contra R$ 599.857,30 do extrato de 30/09 — diferenca de R$ 3,94
# que apareceu entre 15 e 16/10 por edicao de movimento de setembro, ainda sem
# explicacao. Fica declarada em DIVERGE para o painel mostrar, nao ser tapada.
ANCORA_DATA = datetime.date(2026, 9, 30)
# Saldo do EXTRATO DO BANCO na data da ancora. E o unico ancoramento externo que
# existe: de 01/10 em diante so ha o que o Omie diz. A divergencia e calculada
# contra a ancora em vez de escrita a mao, para nao ficar desatualizada.
EXTRATO = {'boldro': 599857.30, 'yo': 142214.80}
NOTA_DIVERGE = {'boldro': 'apareceu entre 15 e 16/10, por edicao de movimento de '
                          'setembro depois do fechamento — nao foi lancamento novo'}

EMP = {
    'boldro': {
        'nome': 'Boldró',
        'ancora': {'Santander c/c': 5.44, 'Santander ContaMax': 599855.80,
                   'Santander CDB': 0.00, 'Fundo Fixo - Restaurante': 0.00, 'GetNet': 0.00},
        'contas': [(2886694320, 'Santander c/c'), (2886694903, 'Santander ContaMax'),
                   (2886695824, 'Santander CDB'), (2878729940, 'Fundo Fixo - Restaurante'),
                   (2899732241, 'GetNet')],
        'getnet': 2899732241,
    },
    'yo': {
        'nome': 'YO Noronha',
        'ancora': {'Bradesco c/c': 9.00, 'Bradesco Invest Fácil': 142205.80,
                   'Bradesco CDB': 0.00, 'Mercado Pago': 0.00},
        'contas': [(11806749900, 'Bradesco c/c'), (11806752455, 'Bradesco Invest Fácil'),
                   (11806755245, 'Bradesco CDB'), (11811341545, 'Mercado Pago')],
        'getnet': None,          # a YO nao tem conta de adquirente no Omie
    },
}

# Titulos que sao ajuste de competencia, nao compromisso: ficam fora do caixa.
IGNORA = ('BOL-BRUTO-GN-', 'BOL-TAXA-GN-', 'BOLDRO-REND-')
# Contrapartes de intercompany, para marcar e poder ocultar no consolidado.
INTER = ('BOLDRO PRAIA', 'YO NORONHA', 'POUSADA TOPAZIO', 'AMANA EMPREENDIMENTOS')
HORIZONTE = 90


def nomes(emp):
    o = {}
    for c in paginas(emp, 'geral/clientes', 'ListarClientesResumido',
                     'clientes_cadastro_resumido', rpp=500, limite=30):
        o[c['codigo_cliente']] = (c.get('razao_social') or c.get('nome_fantasia')
                                  or '—').strip()
    return o


def cats(emp):
    o = {}
    for c in paginas(emp, 'geral/categorias', 'ListarCategorias', 'categoria_cadastro',
                     rpp=100, limite=30):
        o[c.get('codigo')] = c.get('descricao')
    return o


def meses(ini, fim):
    """Lista (primeiro, ultimo) de cada mes do intervalo. O extrato trunca em
    periodo longo, entao cada mes vai numa chamada."""
    out = []
    a = ini.replace(day=1)
    while a <= fim:
        prox = (a.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        out.append((max(a, ini), min(prox - datetime.timedelta(days=1), fim)))
        a = prox
    return out


def extrato(emp, cc, ini, fim):
    r = call(emp, 'financas/extrato', 'ListarExtrato',
             {'nCodCC': cc, 'dPeriodoInicial': ini.strftime('%d/%m/%Y'),
              'dPeriodoFinal': fim.strftime('%d/%m/%Y')})
    return [x for x in (r.get('listaMovimentos') or [])
            if not (x.get('cDesCliente') or '').startswith('SALDO')]


def coleta(HOJE):
    FIM = HOJE + datetime.timedelta(days=HORIZONTE)
    out = {'hoje': HOJE.strftime('%d/%m/%Y'), 'fim': FIM.strftime('%d/%m/%Y'),
           'horizonte': HORIZONTE, 'ancora': ANCORA_DATA.strftime('%d/%m/%Y'),
           'gerado': datetime.datetime.now().strftime('%d/%m/%Y às %H:%M'),
           'ents': {}}
    for emp, cfg in EMP.items():
        NM, CT = nomes(emp), cats(emp)
        contas, agenda = [], []
        ultimo = None
        for cc, nome in cfg['contas']:
            mov = naoconc = 0.0
            nnc = 0
            ult_cc = None
            for a, b in meses(ANCORA_DATA + datetime.timedelta(days=1), HOJE):
                for x in extrato(emp, cc, a, b):
                    if x.get('cSituacao') == 'Previsto':
                        continue
                    mov += x.get('nValorDocumento') or 0
                    try:
                        dd = dt(x.get('dDataLancamento') or '')
                    except Exception:
                        dd = None
                    if dd and (ult_cc is None or dd > ult_cc):
                        ult_cc = dd
                    if x.get('cSituacao') != 'Conciliado':
                        nnc += 1
                        naoconc += x.get('nValorDocumento') or 0
            if ult_cc and (ultimo is None or ult_cc > ultimo):
                ultimo = ult_cc
            # agenda: o que o Omie ja tem como previsto daqui para a frente
            for a, b in meses(HOJE, FIM):
                for x in extrato(emp, cc, a, b):
                    if x.get('cSituacao') != 'Previsto':
                        continue
                    v = x.get('nValorDocumento') or 0
                    agenda.append({'lado': 'receber' if v > 0 else 'pagar',
                                   'd': x.get('dDataLancamento'),
                                   'nome': (x.get('cDesCliente')
                                            or x.get('cRazCliente') or '—'),
                                   'cat': x.get('cDesCategoria') or '—',
                                   'v': R2(abs(v)), 'conta': nome,
                                   'doc': '', 'st': 'Previsto', 'fonte': 'agenda'})
            a0 = cfg['ancora'].get(nome, 0.0)
            contas.append({'n': nome, 'ini': R2(a0), 'mov': R2(mov), 'hoje': R2(a0 + mov),
                           'naoconc': nnc, 'vnaoconc': R2(naoconc),
                           'ultimo': ult_cc.strftime('%d/%m/%Y') if ult_cc else None})

        itens, atr = [], []
        for lado, ep, cn, raiz in (
                ('receber', 'financas/contareceber', 'ListarContasReceber',
                 'conta_receber_cadastro'),
                ('pagar', 'financas/contapagar', 'ListarContasPagar',
                 'conta_pagar_cadastro')):
            for t in paginas(emp, ep, cn, raiz, rpp=500):
                cint = t.get('codigo_lancamento_integracao') or ''
                if any(cint.startswith(p) for p in IGNORA):
                    continue
                st = (t.get('status_titulo') or '').upper()
                if st in ('PAGO', 'RECEBIDO', 'CANCELADO'):
                    continue
                v = t.get('data_vencimento') or ''
                if len(v) != 10:
                    continue
                try:
                    d = dt(v)
                except Exception:
                    continue
                reg = {'lado': lado, 'd': v,
                       'nome': NM.get(t.get('codigo_cliente_fornecedor'), '—'),
                       'cat': (CT.get(t.get('codigo_categoria'))
                               or ('rateio' if not t.get('codigo_categoria')
                                   else t.get('codigo_categoria'))),
                       'v': R2(t.get('valor_documento')),
                       'doc': (t.get('numero_documento') or '').strip(),
                       'st': st.title(), 'fonte': 'titulo'}
                if HOJE <= d <= FIM:
                    itens.append(reg)
                elif d < HOJE:
                    atr.append(reg)

        gn = {'n': 0, 'bruto': 0.0, 'taxa': 0.0}
        if cfg['getnet']:
            pv = [x for x in extrato(emp, cfg['getnet'], HOJE, FIM)
                  if x.get('cSituacao') == 'Previsto']
            gn = {'n': len(pv),
                  'bruto': R2(sum(x['nValorDocumento'] for x in pv
                                  if (x.get('nValorDocumento') or 0) > 0)),
                  'taxa': R2(sum(x['nValorDocumento'] for x in pv
                                 if (x.get('nValorDocumento') or 0) < 0))}

        # Atualidade: o painel nao pode chamar de "caixa hoje" um saldo que para
        # no dia 2. Em 16/10 a Boldro tinha outubro carregado so ate 02/10, com
        # as saidas de dois dias e nenhum recebimento — a conta corrente ficava
        # negativa e o total era ficcao. O dado carrega a data real e os dias de
        # atraso, e o painel abre alerta quando passa de 2 dias.
        atraso = (HOJE - ultimo).days if ultimo else None
        uteis = sum(1 for i in range((HOJE - ANCORA_DATA).days)
                    if (ANCORA_DATA + datetime.timedelta(days=i + 1)).weekday() < 5)
        # divergencia da ancora contra o extrato, calculada e nao escrita a mao
        anc = R2(sum(c['ini'] for c in contas))
        ext = EXTRATO.get(emp)
        diverge = None
        if ext is not None and abs(anc - ext) >= 0.01:
            diverge = {'extrato': ext, 'omie': anc, 'dif': R2(anc - ext),
                       'nota': NOTA_DIVERGE.get(emp, 'sem explicacao levantada ainda')}
        out['ents'][emp] = {
            'nome': cfg['nome'], 'contas': contas, 'itens': itens, 'agenda': agenda,
            'atrasados': {'n': len(atr),
                          'receber': R2(sum(x['v'] for x in atr if x['lado'] == 'receber')),
                          'pagar': R2(sum(x['v'] for x in atr if x['lado'] == 'pagar'))},
            'getnet': gn, 'diverge': diverge,
            'ultimo_mov': ultimo.strftime('%d/%m/%Y') if ultimo else None,
            'atraso_dias': atraso, 'uteis_desde_ancora': uteis,
            'extrato_ancora': EXTRATO.get(emp)}
        print('  %-7s contas %d | titulos %3d | agenda %3d | atrasados %3d | ultimo mov %s'
              % (emp, len(contas), len(itens), len(agenda), len(atr),
                 ultimo.strftime('%d/%m') if ultimo else '—'))
    return out


if __name__ == '__main__':
    H = dt(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
    D = coleta(H)
    AQUI = os.path.dirname(os.path.abspath(__file__))
    bt = os.path.join(os.path.dirname(os.path.dirname(AQUI)),
                      'Library/Mobile Documents/com~apple~CloudDocs/Claude VS',
                      'omie-boldro', 'backtest.json')
    if os.path.exists(bt):
        D['backtest'] = json.load(open(bt))
    json.dump(D, open(os.path.join(AQUI, 'dados_caixa.json'), 'w'), ensure_ascii=False)
    f = (lambda v: format(R2(v), ',.2f').replace(',', '@').replace('.', ',').replace('@', '.'))
    for e, x in D['ents'].items():
        s = sum(c['hoje'] for c in x['contas'])
        r = sum(i['v'] for i in x['itens'] if i['lado'] == 'receber')
        p = sum(i['v'] for i in x['itens'] if i['lado'] == 'pagar')
        ag = sum(i['v'] for i in x['agenda'] if i['lado'] == 'pagar')
        print('%-11s saldo %13s | a receber %11s | a pagar %11s | agenda %11s | nao conc %d'
              % (x['nome'], f(s), f(r), f(p), f(ag),
                 sum(c['naoconc'] for c in x['contas'])))
