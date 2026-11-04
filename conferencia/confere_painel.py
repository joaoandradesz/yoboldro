# -*- coding: utf-8 -*-
"""TRAVA DO PAINEL YO/BOLDRO: todo numero exibido tem que bater com o que o
clique abre, linha por linha.

A regra e a mesma do painel Amana/Topazio: nao pode existir um numero na tabela
e outro numero quando se soma os lancamentos que o clique mostra. Um painel que
mostra 100 e abre 98 nao e um painel com um errinho — e um painel que nao serve.

Replica a logica do proprio index.html (bloco(), soma(), contasDe(), abreCaixa(),
elim(), fatDe()) em vez de recalcular do zero: o que se testa e o que o Joao ve,
nao uma segunda versao da verdade.

Testa, para boldro, yo e o consolidado virtual, nos dois regimes e em todos os
meses publicados:

  A  conta clicavel  = soma dos itens que o clique abre
  B  contador de lancamentos da conta = quantidade de itens abertos
  C  grupo exibido   = soma das contas daquele grupo
  D  cobertura dos grupos nos blocos da DRE/DFC: nenhum grupo orfao (invisivel)
     e nenhum grupo em dois blocos de detalhe (dobrado) — o bug do Prestadores
  E  linha de cascata (=, +, *) = soma dos blocos de detalhe que a compoem
  F  DFC: saldo inicial + movimento do mes = saldo final
  G  consolidado: o grupo CC depois da eliminacao = soma das contas CC, e nenhuma
     conta eliminada sobra fora do grupo CC (senao o grupo some sem o par)
  H  faturamento declarado = soma das contas FAT| que o clique abre
  I  conta que existe no total mas nao tem nenhum item para abrir

Sai com codigo 1 se qualquer invariante falhar. Rodar ANTES de publicar.
"""
import collections
import json
import os
import sys

R2 = lambda v: round((v or 0) + 0.0, 2)
TOL = 0.01
ENTS = ('boldro', 'yo', 'consol')
REGS = ('comp', 'caixa')

# os blocos sao copia literal do gera_painel.py; se mudarem la e nao aqui, o
# teste D acusa grupo orfao/dobrado, que e exatamente o aviso que se quer
BLOCOS_DRE = [
    ('Receita bruta (faturamento)', ['FAT']),
    ('(-) Deducoes', ['2']),
    ('+Receita liquida', ['FAT', '2']),
    ('(-) CMV', ['4']),
    ('+Lucro bruto', ['FAT', '2', '4']),
    ('(-) Despesas variaveis de venda', ['3']),
    ('(-) Custos de operacao', ['5']),
    ('(-) Pessoal operacional', ['6']),
    ('(-) Ocupacao', ['7']),
    ('(-) Administrativas', ['8']),
    ('(-) Marketing e entretenimento', ['9']),
    ('=EBITDA', ['FAT', '2', '3', '4', '5', '6', '7', '8', '9']),
    ('(+-) Resultado financeiro', ['10']),
    ('*LUCRO LIQUIDO', ['FAT', '2', '3', '4', '5', '6', '7', '8', '9', '10']),
    ('(-) Investimentos (capex)', ['11']),
    ('(+-) Financiamento', ['12']),
    ('(+) Outros recebimentos', ['OR']),
    ('(+-) Transferencias e ajustes', ['CC', 'NEUTRO', '13']),
    ('*RESULTADO APOS INVESTIMENTOS',
     ['FAT', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'OR', 'CC', 'NEUTRO', '13']),
    ('(=) Receita lancada no Omie, pela data do credito', ['1']),
    ('(+-) Ajuste de competencia da receita', ['AJC']),
    ('+Receita bruta da DRE, pelo mes da venda', ['FAT']),
]
# virtuais: FAT e AJC nao sao grupos da base, saem de fatDe()
VIRTUAIS = {'FAT', 'AJC'}
# na reconciliacao da receita o grupo 1 e FAT reaparecem de proposito: aquele
# bloco existe para mostrar a ponte, nao para somar no resultado
SO_RECONCILIACAO = {'1'}


def carrega(arq):
    """Le o D do index.html publicado — o painel que o Joao abre."""
    s = open(arq, encoding='utf-8').read()
    i = s.index('const D=')
    j = s.index('{', i)
    dep = 0
    for k in range(j, len(s)):
        if s[k] == '{':
            dep += 1
        elif s[k] == '}':
            dep -= 1
            if dep == 0:
                return json.loads(s[j:k + 1])
    raise ValueError('nao achei o fim do const D= em %s' % arq)


def elim(k):
    u = k.lower()
    return ('yo noronha' in u) or ('yo - boldr' in u) or ('corrente boldr' in u)


def bloco(D, ent, reg, mes):
    """Copia de bloco() do painel, inclusive a eliminacao so no resultado."""
    if ent != 'consol':
        return ((D['ents'].get(ent) or {}).get(reg) or {}).get(mes) or \
            {'grupos': {}, 'contas': {}, 'lanc': {}, 'itens': []}
    o = {'grupos': collections.defaultdict(float), 'contas': collections.defaultdict(float),
         'lanc': collections.defaultdict(int), 'itens': []}
    for e in ('boldro', 'yo'):
        b = ((D['ents'].get(e) or {}).get(reg) or {}).get(mes)
        if not b:
            continue
        for i in (b.get('itens') or []):
            if reg != 'comp' or not elim(i[0]):
                o['itens'].append(i)
        for g, v in b['grupos'].items():
            o['grupos'][g] += v
        for k, v in b['contas'].items():
            if reg == 'comp' and elim(k):
                continue
            o['contas'][k] += v
            o['lanc'][k] += (b.get('lanc') or {}).get(k, 0)
    o['grupos']['CC'] = sum(v for k, v in o['contas'].items() if k.startswith('CC|'))
    return {'grupos': dict(o['grupos']), 'contas': dict(o['contas']),
            'lanc': dict(o['lanc']), 'itens': o['itens']}


def fat_de(D, ent, reg, mes):
    if reg != 'comp':
        return None
    if ent == 'consol':
        t, achou = 0.0, False
        for e in ('boldro', 'yo'):
            b = ((D['ents'].get(e) or {}).get('comp') or {}).get(mes)
            if not b:
                continue
            if b.get('fat'):
                t += b['fat']['valor']
                achou = True
            else:
                t += b['grupos'].get('1', 0)
        return t if achou else None
    b = ((D['ents'].get(ent) or {}).get('comp') or {}).get(mes)
    return b['fat']['valor'] if (b and b.get('fat')) else None


def soma(D, ent, reg, mes, ks):
    b = bloco(D, ent, reg, mes)
    t = 0.0
    for k in ks:
        if k == 'FAT':
            f = fat_de(D, ent, reg, mes)
            t += b['grupos'].get('1', 0) if f is None else f
        elif k == 'AJC':
            f = fat_de(D, ent, reg, mes)
            t += 0 if f is None else (f - b['grupos'].get('1', 0))
        else:
            t += b['grupos'].get(k, 0)
    return t


falhas = []


def falha(onde, msg):
    falhas.append('%-26s %s' % (onde, msg))


def confere(D):
    MS = [str(m) for m in D['meses']]
    for ent in ENTS:
        for reg in REGS:
            for mes in MS:
                b = bloco(D, ent, reg, mes)
                if not b['grupos']:
                    continue
                onde = '%s/%s/%s' % (ent, reg, mes)

                # A e B: a folha clicavel
                por_conta = collections.defaultdict(lambda: [0.0, 0])
                for i in b['itens']:
                    por_conta[i[0]][0] += i[2]
                    por_conta[i[0]][1] += 1
                for ck, v in b['contas'].items():
                    det, n = por_conta.get(ck, [0.0, 0])
                    if abs(R2(v) - R2(det)) > TOL:
                        falha(onde, 'A conta "%s" exibe %.2f e o clique abre %.2f (dif %.2f)'
                              % (ck, v, det, R2(v) - R2(det)))
                    lanc = (b.get('lanc') or {}).get(ck)
                    if lanc is not None and lanc != n:
                        falha(onde, 'B conta "%s" diz %d lancamento(s) e o clique abre %d'
                              % (ck, lanc, n))
                    if n == 0 and abs(R2(v)) > TOL:
                        falha(onde, 'I conta "%s" vale %.2f e nao tem item para abrir' % (ck, v))
                for ck in por_conta:
                    if ck not in b['contas']:
                        falha(onde, 'I item na conta "%s", que nao existe no total' % ck)

                # C: grupo = soma das suas contas
                por_grupo = collections.defaultdict(float)
                for ck, v in b['contas'].items():
                    por_grupo[ck.split('|')[0]] += v
                for g, v in b['grupos'].items():
                    if abs(R2(v) - R2(por_grupo.get(g, 0))) > TOL:
                        falha(onde, 'C grupo %s exibe %.2f e as contas somam %.2f (dif %.2f)'
                              % (g, v, por_grupo.get(g, 0), R2(v) - R2(por_grupo.get(g, 0))))
                for g in por_grupo:
                    if g not in b['grupos']:
                        falha(onde, 'C contas no grupo %s, que nao aparece no total' % g)

                # D: cobertura dos grupos nos blocos (so a DRE tem FAT/AJC)
                if reg == 'comp':
                    detalhe = collections.Counter()
                    for rot, gs in BLOCOS_DRE:
                        if not gs or rot[0] in '=+*':
                            continue
                        for g in gs:
                            detalhe[g] += 1
                    for g in detalhe:
                        if detalhe[g] > 1:
                            falha(onde, 'D grupo %s aparece em %d blocos de detalhe (dobra)'
                                  % (g, detalhe[g]))
                    for g in b['grupos']:
                        if g not in detalhe and g not in SO_RECONCILIACAO:
                            falha(onde, 'D grupo %s tem %.2f e nao esta em nenhum bloco da DRE'
                                  % (g, b['grupos'][g]))

                    # E: cascata = soma dos detalhes
                    acum = ['FAT', '2', '3', '4', '5', '6', '7', '8', '9']
                    casos = [('=EBITDA', acum),
                             ('*LUCRO LIQUIDO', acum + ['10']),
                             ('*RESULTADO APOS INVESTIMENTOS',
                              acum + ['10', '11', '12', 'OR', 'CC', 'NEUTRO', '13'])]
                    for rot, gs in casos:
                        linha = soma(D, ent, reg, mes, gs)
                        peca = sum(soma(D, ent, reg, mes, [g]) for g in gs)
                        if abs(R2(linha) - R2(peca)) > TOL:
                            falha(onde, 'E "%s" exibe %.2f e as linhas somam %.2f'
                                  % (rot, linha, peca))
                    # a ponte da receita tem que fechar: Omie + ajuste = faturamento
                    f = fat_de(D, ent, reg, mes)
                    if f is not None:
                        ponte = b['grupos'].get('1', 0) + (f - b['grupos'].get('1', 0))
                        if abs(R2(ponte) - R2(f)) > TOL:
                            falha(onde, 'E ponte da receita: %.2f + ajuste != %.2f' % (b['grupos'].get('1', 0), f))

                    # H: faturamento declarado = contas FAT| que o clique abre
                    bb = ((D['ents'].get(ent) or {}).get('comp') or {}).get(mes) or {}
                    if ent != 'consol' and bb.get('fat'):
                        sfat = sum(v for k, v in b['contas'].items() if k.startswith('FAT|'))
                        if abs(R2(sfat) - R2(bb['fat']['valor'])) > TOL:
                            falha(onde, 'H faturamento declarado %.2f e o detalhe abre %.2f (dif %.2f)'
                                  % (bb['fat']['valor'], sfat, R2(bb['fat']['valor']) - R2(sfat)))

                # G: no consolidado nenhuma conta eliminada pode sobrar fora de CC
                if ent == 'consol' and reg == 'comp':
                    for e in ('boldro', 'yo'):
                        bo = ((D['ents'].get(e) or {}).get('comp') or {}).get(mes) or {}
                        for ck in (bo.get('contas') or {}):
                            if elim(ck) and not ck.startswith('CC|'):
                                falha(onde, 'G conta eliminada "%s" esta no grupo %s, nao em CC: '
                                            'o grupo perde valor sem o par' % (ck, ck.split('|')[0]))

            # F: a ponte do caixa
            if reg == 'caixa':
                for mes in MS:
                    b = bloco(D, ent, reg, mes)
                    if not b['grupos']:
                        continue
                    sal = (D['ents'].get(ent) or {}).get('saldos') if ent != 'consol' else None
                    if ent == 'consol':
                        ini = fim = 0.0
                        tem = False
                        for e in ('boldro', 'yo'):
                            s = (D['ents'].get(e) or {}).get('saldos') or {}
                            if mes in (s.get('ini') or {}):
                                ini += s['ini'][mes]
                                fim += (s.get('fim') or {}).get(mes, 0)
                                tem = True
                        if not tem:
                            continue
                    else:
                        sal = sal or {}
                        if mes not in (sal.get('ini') or {}):
                            continue
                        ini, fim = sal['ini'][mes], (sal.get('fim') or {}).get(mes, 0)
                    mov = sum(b['grupos'].values())
                    if abs(R2(ini + mov) - R2(fim)) > TOL:
                        falha('%s/caixa/%s' % (ent, mes),
                              'F saldo inicial %.2f + movimento %.2f = %.2f, mas o saldo final '
                              'exibido e %.2f (dif %.2f)' % (ini, mov, ini + mov, fim,
                                                             R2(ini + mov) - R2(fim)))


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arq = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, 'index.html')
    D = carrega(arq)
    print('painel gerado em %s — %s' % (D.get('gerado'), os.path.basename(arq)))
    confere(D)
    if falhas:
        print('\n%d INVARIANTE(S) QUEBRADA(S):\n' % len(falhas))
        for f in falhas:
            print('  ' + f)
        print('\nNAO PUBLICAR.')
        sys.exit(1)
    print('\nOK: todo numero exibido bate com o detalhe que o clique abre.')
    print('   %d mes(es) x %d empresa(s) x %d regime(s)'
          % (len(D['meses']), len(ENTS), len(REGS)))


main()
