# -*- coding: utf-8 -*-
"""Gera o painel gerencial Yó / Boldró (index.html).

Esqueleto herdado do painel Amana/Topázio: nav fixa, hero com a cascata da DRE,
indicadores, composição, tabelas por categoria e ressalvas. Os KPIs é que mudam —
lá é pousada (serviço), aqui é restaurante e beach club (comércio de A&B).

Fonte: omie-boldro/dados_boldro.json, montado por dados_painel.py a partir da API do Omie.
Rodar:  python3 gera_painel.py
"""
import json
import os

BASE = os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/Claude VS/omie-boldro')
D = json.load(open(os.path.join(BASE, 'dados_boldro.json')))
FECHADOS = D['fechados']
MES_NOME = {'2026-08': 'agosto', '2026-09': 'setembro'}

# YO: ainda não lançada no Omie. Números vêm da conciliação do CSC e estão marcados como tal.
YO = {'periodo': '01/07 a 18/09/2026', 'linhas': 1618, 'credito': 2356759.55,
      'debito': 3329777.29, 'saldo_ini': 1202894.61, 'saldo_fim': 229876.34,
      'aporte': 2271313.67, 'obra': 364, 'operacao': 314, 'preop': 40, 'sem_destino': 743}


def acum(campo):
    return sum(D['dre'][m][campo] for m in FECHADOS)


def brl(v, casas=0):
    s = '{:,.{}f}'.format(abs(v), casas)
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('\u2212' if v < 0 else '') + 'R$ ' + s


def pct(v, base):
    return '%.1f%%' % (100 * v / base) if base else '—'


RL = acum('receita_liquida')
CMV = -acum('cmv')
COP = -acum('custos_operacao')
PES = -acum('pessoal')
OCU = -acum('ocupacao')
ADM = -acum('administrativas')
MKT = -acum('marketing')
LB = acum('lucro_bruto')
EBITDA = acum('ebitda')
FIN = acum('financeiro')
LL = acum('lucro_liquido')
RB = acum('receita_bruta')
DED = -acum('deducoes')
INV = -acum('investimento')
PRIME = CMV + PES
CC = sum(D['fora_da_dre'].get('CC', {}).values())
CAIXA = D['dfc']['saldo_final']

CASCATA = [('Receita bruta', RB, 'in'), ('Deduções', -DED, 'out'),
           ('Receita líquida', RL, 'sub'), ('CMV', -CMV, 'out'),
           ('Custos de operação', -COP, 'out'), ('Lucro bruto', LB, 'sub'),
           ('Pessoal', -PES, 'out'), ('Ocupação', -OCU, 'out'),
           ('Administrativas', -ADM, 'out'), ('Marketing', -MKT, 'out'),
           ('EBITDA', EBITDA, 'sub'), ('Resultado financeiro', FIN, 'out'),
           ('Lucro líquido', LL, 'tot')]

KPIS = [
    ('Receita líquida', brl(RL), 'o que entrou pelo banco em %s e %s' % (MES_NOME[FECHADOS[0]], MES_NOME[FECHADOS[1]]), ''),
    ('CMV sobre a receita', pct(CMV, RL), 'food cost — insumos de A&B', 'referência de mercado: 28% a 35%'),
    ('Prime cost', pct(PRIME, RL), 'CMV + pessoal, o indicador que manda em restaurante', 'referência de mercado: 60% a 65%'),
    ('Custo de pessoal', pct(PES, RL), 'salários, diaristas, encargos, alojamento fora', ''),
    ('Margem EBITDA', pct(EBITDA, RL), 'antes de depreciação, acima do pró-labore', 'distorcida pelo recorte — ver ressalvas'),
    ('Caixa em 30/09', brl(CAIXA), 'conta corrente Santander, conferida com o extrato', 'abriu o período em zero'),
    ('Exposição com a YO', brl(abs(CC)), 'conta corrente de partes relacionadas', 'R$ 107,2 mil pagos pela Boldró por conta da YO'),
    ('Investimento', brl(INV), 'fora do EBITDA, critério D7', 'coqueiros e guarda-sol'),
]


def barras():
    """evolução mensal: receita x despesa operacional"""
    out = []
    mx = max(max(D['dre'][m]['receita_liquida'] for m in FECHADOS),
             max(-(D['dre'][m]['cmv'] + D['dre'][m]['custos_operacao'] + D['dre'][m]['pessoal'] +
                   D['dre'][m]['ocupacao'] + D['dre'][m]['administrativas'] + D['dre'][m]['marketing'])
                 for m in FECHADOS))
    for m in FECHADOS:
        x = D['dre'][m]
        desp = -(x['cmv'] + x['custos_operacao'] + x['pessoal'] + x['ocupacao'] +
                 x['administrativas'] + x['marketing'])
        out.append((MES_NOME[m], x['receita_liquida'], desp, x['ebitda'],
                    100 * x['receita_liquida'] / mx, 100 * desp / mx))
    return out


def tabela_grupos():
    linhas = []
    for nome, por_mes in sorted(D['grupos'].items(), key=lambda i: -abs(sum(i[1].values()))):
        v = {m: por_mes.get(m, 0) for m in FECHADOS}
        tot = sum(v.values())
        if abs(tot) < 0.01:
            continue
        linhas.append((nome, v[FECHADOS[0]], v[FECHADOS[1]], tot))
    return linhas


def tabela_contas():
    linhas = []
    for chave, por_mes in D['contas'].items():
        g, _, nome = chave.partition('|')
        v = {m: por_mes.get(m, 0) for m in FECHADOS}
        tot = sum(v.values())
        if abs(tot) < 0.01:
            continue
        linhas.append((nome, v[FECHADOS[0]], v[FECHADOS[1]], tot))
    return sorted(linhas, key=lambda x: -abs(x[3]))


CSS = """
:root{--navy:#0D0F1A;--navy2:#141726;--navy3:#1C2032;--line:#262B40;--orange:#F97316;
 --orange-soft:#FFF7ED;--offwhite:#FAFAF7;--ink:#0D0F1A;--ink2:#374151;--g400:#9CA3AF;
 --g500:#6B7280;--g300:#D1D5DB;--g200:#E5E7EB;--in:#0E9F6E;--in-soft:#E7F6F0;--out:#DC2626;
 --out-soft:#FCECEC;--card:#fff;--shadow:0 1px 3px rgba(13,15,26,.06),0 8px 24px rgba(13,15,26,.05)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Inter',sans-serif;background:var(--offwhite);color:var(--ink);
 -webkit-font-smoothing:antialiased;line-height:1.55}
.num{font-family:'Plus Jakarta Sans',sans-serif;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.ital{font-family:'Fraunces',serif;font-style:italic;font-weight:400}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px}
.nav{position:sticky;top:0;z-index:50;background:rgba(13,15,26,.92);backdrop-filter:blur(10px);
 border-bottom:1px solid rgba(255,255,255,.08)}
.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:60px}
.nav .mark{font-family:'Plus Jakarta Sans';font-weight:700;font-size:14px;color:#fff;letter-spacing:.02em}
.nav .mark b{color:var(--orange)}
.nav-links{display:flex;gap:4px}
.nav-links a{font-family:'Plus Jakarta Sans';font-size:12.5px;font-weight:600;color:#B8BECF;
 text-decoration:none;padding:8px 13px;border-radius:8px;transition:.2s}
.nav-links a:hover{color:#fff;background:rgba(255,255,255,.07)}
.nav-links a.on{color:var(--navy);background:var(--orange)}
@media(max-width:820px){.nav-links{display:none}}
.hero{background:var(--navy);color:#fff;padding:48px 0 56px;position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;top:-40%;right:-10%;width:520px;height:520px;
 background:radial-gradient(circle,rgba(249,115,22,.18),transparent 62%);pointer-events:none}
.eyebrow{font-family:'Plus Jakarta Sans';font-size:11px;font-weight:700;letter-spacing:.22em;
 text-transform:uppercase;color:var(--orange)}
.hero h1{font-family:'Plus Jakarta Sans';font-weight:300;font-size:clamp(30px,4.4vw,50px);
 line-height:1.08;margin:14px 0 6px;letter-spacing:-.02em}
.hero h1 b{font-weight:700}
.hero .sub{font-size:15px;color:#AEB4C6;max-width:680px}
.hero .sub .ital{color:#fff;font-size:16px}
.waterfall{margin-top:36px;background:var(--navy2);border:1px solid var(--line);border-radius:16px;
 padding:26px 28px 20px}
.wf-row{display:grid;grid-template-columns:200px 1fr 150px;align-items:center;gap:14px;
 padding:7px 0;border-bottom:1px solid rgba(255,255,255,.05)}
.wf-row:last-child{border-bottom:none}
.wf-row .lab{font-size:13px;color:#C3C9D9}
.wf-row.sub .lab,.wf-row.tot .lab{font-weight:700;color:#fff;font-family:'Plus Jakarta Sans'}
.wf-row.tot{background:rgba(249,115,22,.09);margin:6px -14px 0;padding:12px 14px;border-radius:10px}
.wf-bar{height:9px;border-radius:5px;background:rgba(255,255,255,.07);overflow:hidden}
.wf-bar i{display:block;height:100%;border-radius:5px}
.wf-row .val{text-align:right;font-size:14px;font-weight:600}
.wf-row.sub .val,.wf-row.tot .val{font-size:16px;font-weight:800}
.v-in{color:#34D399}.v-out{color:#F87171}.v-neutral{color:#fff}
section{padding:54px 0}
.sec-alt{background:#fff;border-top:1px solid var(--g200);border-bottom:1px solid var(--g200)}
h2{font-family:'Plus Jakarta Sans';font-weight:700;font-size:25px;letter-spacing:-.02em;margin-bottom:6px}
h2 .ital{font-weight:400;color:var(--g500)}
.lead{color:var(--ink2);font-size:14.5px;max-width:760px;margin-bottom:26px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
@media(max-width:980px){.kpis{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.kpis{grid-template-columns:1fr}}
.kpi{background:var(--card);border:1px solid var(--g200);border-radius:14px;padding:18px 18px 16px;
 box-shadow:var(--shadow)}
.kpi .t{font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:var(--g500)}
.kpi .v{font-family:'Plus Jakarta Sans';font-size:27px;font-weight:800;letter-spacing:-.025em;margin:8px 0 4px}
.kpi .d{font-size:12.5px;color:var(--ink2)}
.kpi .ref{font-size:11.5px;color:var(--orange);margin-top:6px;font-weight:600}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:#fff;border-radius:12px;overflow:hidden;
 box-shadow:var(--shadow)}
th{background:var(--navy);color:#fff;font-family:'Plus Jakarta Sans';font-size:11.5px;font-weight:700;
 text-transform:uppercase;letter-spacing:.07em;padding:11px 14px;text-align:right}
th:first-child{text-align:left}
td{padding:9px 14px;border-bottom:1px solid var(--g200);text-align:right}
td:first-child{text-align:left}
tr:nth-child(even) td{background:#FBFBF9}
tr.destaque td{font-weight:700;background:var(--orange-soft)}
.bars{display:grid;gap:18px;margin-top:8px}
.bar-row{background:#fff;border:1px solid var(--g200);border-radius:14px;padding:16px 18px;box-shadow:var(--shadow)}
.bar-row .mes{font-family:'Plus Jakarta Sans';font-weight:700;font-size:14px;text-transform:capitalize}
.bar{height:22px;border-radius:6px;margin:7px 0 3px;position:relative;background:var(--g200)}
.bar i{display:block;height:100%;border-radius:6px}
.bar span{position:absolute;right:9px;top:1px;font-size:12px;font-weight:700;color:#fff}
.aviso{background:#fff;border:1px solid var(--g200);border-left:3px solid var(--orange);border-radius:12px;
 padding:18px 20px;margin-bottom:14px;box-shadow:var(--shadow)}
.aviso h4{font-family:'Plus Jakarta Sans';font-size:14px;font-weight:700;margin-bottom:5px}
.aviso p{font-size:13.5px;color:var(--ink2)}
.tag{display:inline-block;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;
 padding:3px 9px;border-radius:20px;background:var(--orange-soft);color:#B45309;margin-left:8px}
.tag.cinza{background:var(--g200);color:var(--g500)}
@media(max-width:720px){
 .wf-row{grid-template-columns:1fr auto;gap:8px}
 .wf-row .wf-bar{grid-column:1/-1;order:3}
 .wrap{padding:0 18px}
 .hero{padding:34px 0 40px}
 table{font-size:12px}
 th,td{padding:8px 9px}
}
footer{background:var(--navy);color:#8A91A6;padding:30px 0;font-size:12.5px}
footer b{color:#fff}
"""


def html():
    mx = max(abs(v) for _, v, _ in CASCATA)
    wf = []
    for lab, val, kind in CASCATA:
        cor = '#34D399' if val >= 0 else '#F87171'
        if kind in ('sub', 'tot'):
            cor = '#F97316'
        cls = {'in': '', 'out': '', 'sub': ' sub', 'tot': ' tot'}[kind]
        vcl = 'v-in' if val > 0 else ('v-out' if val < 0 else 'v-neutral')
        wf.append('<div class="wf-row%s"><div class="lab">%s</div>'
                  '<div class="wf-bar"><i style="width:%.1f%%;background:%s"></i></div>'
                  '<div class="val num %s">%s</div></div>'
                  % (cls, lab, 100 * abs(val) / mx, cor, vcl, brl(val)))

    k = ''.join('<div class="kpi"><div class="t">%s</div><div class="v num">%s</div>'
                '<div class="d">%s</div>%s</div>'
                % (t, v, d, '<div class="ref">%s</div>' % r if r else '')
                for t, v, d, r in KPIS)

    bars = ''.join(
        '<div class="bar-row"><div class="mes">%s</div>'
        '<div class="bar"><i style="width:%.1f%%;background:#0E9F6E"></i><span>%s de receita</span></div>'
        '<div class="bar"><i style="width:%.1f%%;background:#DC2626"></i><span>%s de despesa</span></div>'
        '<div class="d num" style="font-size:12.5px;color:var(--ink2);margin-top:6px">EBITDA %s</div></div>'
        % (mes, pr, brl(rec), pd, brl(desp), brl(eb))
        for mes, rec, desp, eb, pr, pd in barras())

    tg = ''.join('<tr%s><td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>'
                 % (' class="destaque"' if n == 'Receita bruta' else '', n, brl(a), brl(s), brl(t))
                 for n, a, s, t in tabela_grupos())
    tc = ''.join('<tr><td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>'
                 % (n, brl(a), brl(s), brl(t)) for n, a, s, t in tabela_contas())

    return """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fluxo de Caixa &amp; DRE · Yó / Boldró · 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,400&display=swap" rel="stylesheet">
<style>%s</style></head><body>

<nav class="nav"><div class="wrap">
  <div class="mark">Grupo <b>Yó / Boldró</b></div>
  <div class="nav-links">
    <a href="#geral" class="on">Visão geral</a><a href="#indicadores">Indicadores</a>
    <a href="#evolucao">Evolução</a><a href="#tabelas">Tabelas</a>
    <a href="#yo">YO</a><a href="#ressalvas">Ressalvas</a>
  </div>
</div></nav>

<header class="hero" id="geral"><div class="wrap">
  <div class="eyebrow">Boldró Praia Empreendimentos · 45.270.781/0002-53</div>
  <h1>Resultado de <b>agosto e setembro</b> de 2026</h1>
  <p class="sub">Primeiro fechamento da Boldró no Omie. <span class="ital">669 lançamentos conciliados com o extrato do Santander</span>, saldo do sistema igual ao da conciliação, diferença zero.</p>
  <div class="waterfall">%s</div>
</div></header>

<section id="indicadores"><div class="wrap">
  <h2>Indicadores <span class="ital">de operação de A&amp;B</span></h2>
  <p class="lead">Restaurante e beach club se medem por food cost e prime cost, não por diária e ocupação. As referências de mercado estão ao lado de cada indicador para dar escala — não são meta aprovada.</p>
  <div class="kpis">%s</div>
</div></section>

<section id="evolucao" class="sec-alt"><div class="wrap">
  <h2>Evolução <span class="ital">mês a mês</span></h2>
  <p class="lead">Os dois meses não são comparáveis entre si: agosto concentra o abastecimento inicial e setembro concentra o crédito das vendas em cartão. Leia o acumulado, não a variação.</p>
  <div class="bars">%s</div>
</div></section>

<section id="tabelas"><div class="wrap">
  <h2>Tabelas <span class="ital">por grupo e por conta</span></h2>
  <p class="lead">Mesma estrutura do painel Amana/Topázio: o grupo abre em conta, e cada conta soma os títulos pela competência da emissão.</p>
  <table><thead><tr><th>Grupo gerencial</th><th>agosto</th><th>setembro</th><th>acumulado</th></tr></thead><tbody>%s</tbody></table>
  <div style="height:26px"></div>
  <table><thead><tr><th>Conta</th><th>agosto</th><th>setembro</th><th>acumulado</th></tr></thead><tbody>%s</tbody></table>
</div></section>

<section id="yo" class="sec-alt"><div class="wrap">
  <h2>YO Noronha <span class="tag cinza">aguardando carga</span></h2>
  <p class="lead">A base da YO tem o plano de contas aplicado, mas <b>nenhum lançamento financeiro</b>. Os números abaixo vêm da conciliação do CSC e ainda <b>não estão no Omie</b> — servem de dimensão, não de resultado.</p>
  <div class="kpis">
    <div class="kpi"><div class="t">Período</div><div class="v num" style="font-size:19px">%s</div><div class="d">%d lançamentos na conciliação</div></div>
    <div class="kpi"><div class="t">Saldo no início</div><div class="v num">%s</div><div class="d">em 01/07/2026</div></div>
    <div class="kpi"><div class="t">Saldo no fim</div><div class="v num">%s</div><div class="d">em 18/09/2026</div><div class="ref">consumo de %s no período</div></div>
    <div class="kpi"><div class="t">Aporte de investidor</div><div class="v num">%s</div><div class="d">20 lançamentos</div><div class="ref">depende de decisão societária</div></div>
  </div>
  <div style="height:16px"></div>
  <div class="aviso"><h4>A YO é obra, a Boldró é operação</h4>
    <p>Na conciliação da YO, %d lançamentos estão marcados como <b>obra</b>, %d como operação e %d como pré-operação — e %d linhas estão <b>sem destino</b>. Enquanto o destino não for preenchido, não há como separar o que entra no EBITDA do que é investimento.</p></div>
</div></section>

<section id="ressalvas"><div class="wrap">
  <h2>Ressalvas <span class="ital">que mudam a leitura</span></h2>
  <p class="lead">Três limitações desta versão. Nenhuma é erro de carga: são do recorte e das fontes disponíveis hoje.</p>
  <div class="aviso"><h4>A receita está pelo líquido da GetNet</h4>
    <p>O que entrou no banco é o repasse líquido da adquirente. A <b>receita bruta e a taxa de cartão não aparecem</b>, e o custo de antecipação também não. Com o extrato de vendas detalhado da GetNet isso é reclassificado e a margem muda.</p></div>
  <div class="aviso"><h4>O regime é de caixa bancário, não de competência</h4>
    <p>A DRE segue a emissão do título, mas o universo é o que passou pela conta em agosto e setembro. Compra com prazo e folha paga em outubro ficam de fora — por isso a margem EBITDA aparece alta demais para uma operação de A&amp;B.</p></div>
  <div class="aviso"><h4>Não há abertura por canal</h4>
    <p>Salão, bar, beach club e eventos só existem no PDV (3LM), que não tem integração por API. O Omie é controle financeiro: a receita entra em uma conta só.</p></div>
</div></section>

<footer><div class="wrap">
  <b>Exact BR</b> · CSC Noronha · painel gerencial Yó / Boldró · versão 1 · dados do Omie em 06/10/2026<br>
  Fonte: API do Omie (títulos e extrato) para a Boldró; conciliação do CSC para a YO, ainda não lançada.
</div></footer>

<script>
var secs=[].slice.call(document.querySelectorAll('section,header')),links=[].slice.call(document.querySelectorAll('.nav-links a'));
window.addEventListener('scroll',function(){var y=scrollY+90,at=secs[0].id;
 secs.forEach(function(s){if(s.offsetTop<=y)at=s.id});
 links.forEach(function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+at)})});
</script>
</body></html>""" % (CSS, ''.join(wf), k, bars, tg, tc,
                      YO['periodo'], YO['linhas'], brl(YO['saldo_ini']), brl(YO['saldo_fim']),
                      brl(YO['saldo_ini'] - YO['saldo_fim']), brl(YO['aporte']),
                      YO['obra'], YO['operacao'], YO['preop'], YO['sem_destino'])


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    open(out, 'w').write(html())
    print('gerado %s (%.0f KB)' % (out, os.path.getsize(out) / 1024))
    print('RL %.2f | CMV %.1f%% | prime %.1f%% | EBITDA %.2f (%.1f%%) | caixa %.2f'
          % (RL, 100 * CMV / RL, 100 * PRIME / RL, EBITDA, 100 * EBITDA / RL, CAIXA))
