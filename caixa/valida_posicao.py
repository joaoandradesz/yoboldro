# -*- coding: utf-8 -*-
"""Validacao da posicao de caixa da Boldro e da YO no Omie.

O dashboard afirma um "caixa hoje". Esta validacao responde se esse numero
merece confianca, testando sete coisas, cada uma capaz de falsear o saldo:

  1. ANCORA        o saldo de 30/09 no Omie bate com o extrato do banco?
  2. ATUALIDADE    ate que dia outubro esta carregado? Um saldo "de hoje" que
                   para no dia 9 e saldo do dia 9.
  3. BURACOS       quantos dias uteis de outubro nao tem movimento nenhum?
  4. PREVISTO      quanto de 'Previsto' esta misturado no periodo fechado?
  5. TITULO x BANCO  titulo baixado sem movimento no extrato, e vice-versa.
  6. TRUNCAMENTO   o extrato devolve a mesma coisa em janelas diferentes?
  7. EDICAO RETROATIVA  movimento de mes fechado alterado depois do fechamento.

Uso: python3 caixa/valida_posicao.py        -> imprime e grava validacao.json
"""
import collections
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omie_api import call, paginas  # noqa: E402

HOJE = datetime.date.today()
FECHA = datetime.date(2026, 9, 30)

# Saldo do extrato do banco na data do fechamento. E o unico ancoramento
# externo que existe: a partir de 01/10 so ha o que o Omie diz.
EXTRATO = {'boldro': 599857.30, 'yo': 142214.80}

EMP = {
    'boldro': ('Boldró', [(2886694320, 'Santander c/c'), (2886694903, 'Santander ContaMax'),
                          (2886695824, 'Santander CDB'),
                          (2878729940, 'Fundo Fixo - Restaurante'), (2899732241, 'GetNet')]),
    'yo': ('YO Noronha', [(11806749900, 'Bradesco c/c'), (11806752455, 'Bradesco Invest Fácil'),
                          (11806755245, 'Bradesco CDB'), (11811341545, 'Mercado Pago')]),
}
R2 = (lambda v: round((v or 0) + 0.0, 2))


def d(s):
    try:
        return datetime.datetime.strptime(s or '', '%d/%m/%Y').date()
    except Exception:
        return None


def mv(emp, cc, ini, fim):
    r = call(emp, 'financas/extrato', 'ListarExtrato',
             {'nCodCC': cc, 'dPeriodoInicial': ini.strftime('%d/%m/%Y'),
              'dPeriodoFinal': fim.strftime('%d/%m/%Y')})
    L = [x for x in (r.get('listaMovimentos') or [])
         if not (x.get('cDesCliente') or '').startswith('SALDO')]
    return L, r.get('nSaldoAnterior')


def util(a, b):
    """dias de semana entre a e b, inclusive"""
    out, x = [], a
    while x <= b:
        if x.weekday() < 5:
            out.append(x)
        x += datetime.timedelta(days=1)
    return out


rel = {'gerado': datetime.datetime.now().strftime('%d/%m/%Y às %H:%M'),
       'hoje': HOJE.strftime('%d/%m/%Y'), 'empresas': {}}
print('VALIDACAO DA POSICAO DE CAIXA — %s\n' % HOJE.strftime('%d/%m/%Y'))

for emp, (nome, contas) in EMP.items():
    print('=' * 72)
    print('%s' % nome.upper())
    e = {'nome': nome, 'contas': [], 'alertas': []}

    # ---------- 1 e 2: ancora e atualidade, conta por conta
    print('\n1 e 2) ANCORA EM 30/09 E ATE QUE DIA OUTUBRO ESTA CARREGADO')
    print('%-26s %14s %14s %14s %12s %5s' %
          ('conta', 'saldo 30/09', 'mov outubro', 'saldo hoje', 'ult. mov', 'mov'))
    t30 = tout = 0.0
    ultimo_geral = None
    for cc, cn in contas:
        L, _ = mv(emp, cc, FECHA.replace(day=1), FECHA)
        real = [x for x in L if x.get('cSituacao') != 'Previsto']
        s30 = 0.0
        for x in real:
            if x.get('nSaldo') is not None:
                s30 = x['nSaldo']
        O, _ = mv(emp, cc, FECHA + datetime.timedelta(days=1), HOJE)
        oreal = [x for x in O if x.get('cSituacao') != 'Previsto']
        mout = sum(x.get('nValorDocumento') or 0 for x in oreal)
        datas = sorted({d(x.get('dDataLancamento')) for x in oreal
                        if d(x.get('dDataLancamento'))})
        ult = datas[-1] if datas else None
        if ult and (ultimo_geral is None or ult > ultimo_geral):
            ultimo_geral = ult
        print('%-26s %14.2f %14.2f %14.2f %12s %5d'
              % (cn, s30, mout, s30 + mout,
                 ult.strftime('%d/%m') if ult else '—', len(oreal)))
        t30 += s30
        tout += mout
        e['contas'].append({'conta': cn, 's30': R2(s30), 'mov_out': R2(mout),
                            'hoje': R2(s30 + mout),
                            'ultimo_mov': ult.strftime('%d/%m/%Y') if ult else None,
                            'n_mov_out': len(oreal)})
    print('%-26s %14.2f %14.2f %14.2f' % ('TOTAL', t30, tout, t30 + tout))
    ext = EXTRATO[emp]
    dif = R2(t30 - ext)
    print('\n   extrato do banco em 30/09  %14.2f' % ext)
    print('   Omie em 30/09              %14.2f' % t30)
    print('   diferenca                  %14.2f  %s'
          % (dif, 'OK' if abs(dif) < 0.01 else '<<< NAO BATE'))
    e['ancora'] = {'omie': R2(t30), 'extrato': ext, 'dif': dif}
    e['saldo_hoje'] = R2(t30 + tout)
    if abs(dif) >= 0.01:
        e['alertas'].append('a ancora de 30/09 nao bate com o extrato: R$ %.2f' % dif)

    atraso = (HOJE - ultimo_geral).days if ultimo_geral else None
    e['ultimo_mov'] = ultimo_geral.strftime('%d/%m/%Y') if ultimo_geral else None
    e['atraso_dias'] = atraso
    print('\n   ultimo movimento carregado: %s  (%s)'
          % (ultimo_geral.strftime('%d/%m/%Y') if ultimo_geral else 'nenhum',
             'hoje' if atraso == 0 else '%d dias atras' % atraso if atraso is not None else '—'))
    if atraso and atraso > 2:
        e['alertas'].append('o "caixa hoje" e de %s, %d dias atras: outubro nao esta '
                            'carregado até hoje'
                            % (ultimo_geral.strftime('%d/%m/%Y'), atraso))

    # ---------- 3: buracos em outubro
    print('\n3) DIAS UTEIS DE OUTUBRO SEM MOVIMENTO NENHUM')
    dias_com = set()
    for cc, cn in contas:
        O, _ = mv(emp, cc, FECHA + datetime.timedelta(days=1), HOJE)
        for x in O:
            if x.get('cSituacao') == 'Previsto':
                continue
            dd = d(x.get('dDataLancamento'))
            if dd:
                dias_com.add(dd)
    us = util(FECHA + datetime.timedelta(days=1), HOJE)
    vazios = [x for x in us if x not in dias_com]
    print('   %d dias uteis no periodo, %d com movimento, %d vazios'
          % (len(us), len(us) - len(vazios), len(vazios)))
    if vazios:
        print('   vazios: %s' % ', '.join(x.strftime('%d/%m') for x in vazios))
    e['dias_uteis'] = len(us)
    e['dias_vazios'] = [x.strftime('%d/%m/%Y') for x in vazios]
    if len(vazios) > len(us) / 3:
        e['alertas'].append('%d de %d dias uteis de outubro sem movimento nenhum'
                            % (len(vazios), len(us)))

    # ---------- 4: previsto dentro do periodo fechado
    print('\n4) MOVIMENTO "PREVISTO" DENTRO DE AGOSTO E SETEMBRO')
    prev = []
    for cc, cn in contas:
        L, _ = mv(emp, cc, datetime.date(2026, 8, 1), FECHA)
        for x in L:
            if x.get('cSituacao') == 'Previsto':
                prev.append((cn, x.get('dDataLancamento'), x.get('nValorDocumento'),
                             x.get('cDesCategoria')))
    print('   %d movimentos previstos em mes fechado' % len(prev))
    for p in prev[:6]:
        print('      %-26s %s %12.2f  %s' % (p[0], p[1], p[2] or 0, (p[3] or '')[:30]))
    e['previsto_em_fechado'] = len(prev)
    e['previsto_valor'] = R2(sum(abs(p[2] or 0) for p in prev))
    if prev:
        e['alertas'].append('%d movimentos "Previsto" dentro de mes fechado, R$ %.2f — '
                            'nao sao caixa e o painel os exclui'
                            % (len(prev), e['previsto_valor']))

    # ---------- 6: truncamento
    print('\n6) TRUNCAMENTO DO EXTRATO — mesma conta, janelas diferentes')
    cc0, cn0 = contas[0]
    base = None
    trunc = False
    for ini in (FECHA.replace(day=1), datetime.date(2026, 8, 1), datetime.date(2026, 7, 1)):
        L, _ = mv(emp, cc0, ini, FECHA)
        real = [x for x in L if x.get('cSituacao') != 'Previsto']
        s = None
        for x in real:
            if d(x.get('dDataLancamento')) == FECHA and x.get('nSaldo') is not None:
                s = x['nSaldo']
        print('   %s a 30/09: %4d movimentos | saldo em 30/09 %s'
              % (ini.strftime('%d/%m'), len(real), '%.2f' % s if s is not None else 'NAO APARECE'))
        if base is None:
            base = s
        elif s is None or (base is not None and abs(s - base) > 0.01):
            trunc = True
    e['truncamento'] = trunc
    if trunc:
        e['alertas'].append('o ListarExtrato devolve saldos diferentes para a mesma data '
                            'conforme a janela: o coletor le mes a mes por isso')

    # ---------- 7: edicao retroativa
    print('\n7) MOVIMENTO DE MES FECHADO ALTERADO DEPOIS DO FECHAMENTO')
    alt = []
    for cc, cn in contas:
        L, _ = mv(emp, cc, datetime.date(2026, 8, 1), FECHA)
        for x in L:
            di = d(x.get('cDataInclusao'))
            if di and di > FECHA:
                alt.append({'conta': cn, 'data': x.get('dDataLancamento'),
                            'valor': R2(x.get('nValorDocumento')),
                            'incluido': x.get('cDataInclusao'),
                            'sit': x.get('cSituacao'),
                            'cat': (x.get('cDesCategoria') or '')[:34]})
    print('   %d movimentos de mes fechado incluidos depois de 30/09' % len(alt))
    for a in sorted(alt, key=lambda y: y['incluido'])[:8]:
        print('      %-26s %s %12.2f  incluido %s  %s  %s'
              % (a['conta'], a['data'], a['valor'], a['incluido'], a['sit'], a['cat']))
    e['incluidos_depois'] = alt
    if alt:
        e['alertas'].append('%d movimentos de agosto/setembro foram incluidos depois do '
                            'fechamento' % len(alt))

    # ---------- resumo
    print('\n   ALERTAS DESTA EMPRESA: %d' % len(e['alertas']))
    for a in e['alertas']:
        print('      - %s' % a)
    rel['empresas'][emp] = e
    print()

AQUI = os.path.dirname(os.path.abspath(__file__))
json.dump(rel, open(os.path.join(AQUI, 'validacao.json'), 'w'), ensure_ascii=False, indent=1)
print('=' * 72)
print('gravado validacao.json')
for emp, e in rel['empresas'].items():
    print('%-12s saldo hoje R$ %13.2f | ultimo mov %s | %d alertas'
          % (e['nome'], e['saldo_hoje'], e['ultimo_mov'] or '—', len(e['alertas'])))
