# -*- coding: utf-8 -*-
"""Dashboard de caixa — Boldro, YO Noronha e consolidado.
Gera ../caixa.html a partir de dados_caixa.json (coleta_dash.py).

Adaptado do painel-amanatopazio. O que muda alem dos nomes: carrega o bloco
agenda (compromissos que o Omie tem como Previsto), a divergencia declarada da
ancora e o resultado do backtest de cobertura, e escreve os textos de rodape
no proprio dado em vez de no dash.js."""
import sys,os,json,base64,datetime,collections
AQUI=os.path.dirname(os.path.abspath(__file__))
D=json.load(open(os.path.join(AQUI,"dados_caixa.json"),encoding="utf-8"))
BLACK=base64.b64encode(open(os.path.join(AQUI,"logo-preta.png"),"rb").read()).decode()
WHITE=base64.b64encode(open(os.path.join(AQUI,"logo-branca.png"),"rb").read()).decode()
dt=lambda s: datetime.datetime.strptime(s,"%d/%m/%Y").date()
R2=lambda v: round((v or 0)+0.0,2)
HOJE=dt(D["hoje"]); FIM=dt(D["fim"])
MESES=["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
DOW=["dom","seg","ter","qua","qui","sex","sáb"]
INTER=("BOLDRO PRAIA","YO NORONHA","POUSADA TOPAZIO","AMANA EMPREENDIMENTOS")

# consolidado = soma, com o intercompany marcado
ents=dict(D["ents"])
cons={"nome":"Consolidado","contas":[],"itens":[],"agenda":[],"diverge":None,
      "atrasados":{"n":0,"receber":0.0,"pagar":0.0},"getnet":{"n":0,"bruto":0.0,"taxa":0.0}}
for e,x in D["ents"].items():
    for c in x["contas"]: cons["contas"].append({**c,"n":"%s · %s"%(x["nome"],c["n"])})
    for i in x["itens"]: cons["itens"].append({**i,"emp":x["nome"]})
    for i in x.get("agenda") or []: cons["agenda"].append({**i,"emp":x["nome"]})
    for k in ("n","receber","pagar"): cons["atrasados"][k]=R2(cons["atrasados"][k]+x["atrasados"][k])
    for k in ("n","bruto","taxa"): cons["getnet"][k]=R2(cons["getnet"][k]+x["getnet"][k])
for e,x in ents.items():
    for i in x["itens"]: i["emp"]=x["nome"]
ents["consol"]=cons

# a janela e escolhida na tela; aqui so marcamos o intercompany
# o consolidado herda a PIOR atualidade: se uma empresa para no dia 2, o total
# tambem para no dia 2, e dizer "caixa hoje" ali seria o mesmo erro duas vezes
_at=[x.get("atraso_dias") for e,x in D["ents"].items() if x.get("atraso_dias") is not None]
_ul=[x.get("ultimo_mov") for e,x in D["ents"].items() if x.get("ultimo_mov")]
cons["atraso_dias"]=max(_at) if _at else None
cons["ultimo_mov"]=min(_ul,key=lambda s:(s[6:],s[3:5],s[:2])) if _ul else None

for e,x in ents.items():
    x["inter"]=sum(1 for i in x["itens"] if any(t in i["nome"].upper() for t in INTER))
    x["saldo_hoje"]=R2(sum(c["hoje"] for c in x["contas"]))
    x["ancora_total"]=R2(sum(c["ini"] for c in x["contas"]))
    x["naoconc"]=sum(c["naoconc"] for c in x["contas"])

# Textos que na versao da Amana viviam dentro do dash.js. Ficam no dado para o
# mesmo dash.js servir os dois paineis.
fm=lambda v: "R$ "+format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
BT=D.get("backtest")
if BT:
    NOTA_COB=("Este painel mostra <b>posição e compromissos</b>, não previsão: enxerga só o que "
              "já está lançado no Omie. Backtest com corte em %s: do dinheiro que saiu do banco "
              "entre %s e %s, %s de %s já tinha título lançado na data do corte — cobertura de "
              "<b>%.1f%%</b>. Nestas duas bases o Omie é alimentado depois do fato, pela planilha "
              "de conciliação do mês fechado. Enquanto for assim, o que está à frente de hoje "
              "nesta tela é só o que alguém digitou, não o compromisso real do período."
              %(BT["corte"],BT["corte"],BT["fim"],fm(BT["coberto"]),fm(BT["total"]),
                BT["cobertura_pct"]))
else:
    NOTA_COB=("Este painel mostra <b>posição e compromissos</b>, não previsão: enxerga só o que "
              "já está lançado no Omie. O backtest de cobertura ainda não foi rodado nesta edição.")
META={k:D[k] for k in ("hoje","fim","ancora","gerado")}
META.update({"inter_rotulo":"Boldró ↔ YO ↔ Topázio ↔ Amana",
             "inter_rx":"|".join(INTER),
             "nota_saldo":("Âncora de %s mais todo o movimento realizado desde então. "
                           "A conciliação formal quase não é usada nestas bases, então somar só "
                           "o que está marcado como conciliado devolveria um saldo falso."
                           %D["ancora"]),
             "nota_cobertura":NOTA_COB})
BLOB=json.dumps({"meta":META,
                 "horizonte":D.get("horizonte",90),
                 "backtest":BT,
                 "ents":{k:{kk:vv for kk,vv in v.items()} for k,v in ents.items()}},ensure_ascii=False)
CSS=open(os.path.join(AQUI,"dash.css"),encoding="utf-8").read()
JS=open(os.path.join(AQUI,"dash.js"),encoding="utf-8").read()
HTML=f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Boldró e YO Noronha · Caixa e compromissos · Exact BR</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Fraunces:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header class="top"><img class="logo" src="data:image/png;base64,{BLACK}" alt="Exact BR">
<div class="tt"><h1>Boldró e YO Noronha</h1><p class="st">Caixa e compromissos</p><p id="sub"></p></div>
<div class="ents" id="ents"></div>
<button class="pbt" onclick="window.print()">Exportar PDF</button></header>
<main id="app"></main>
<div class="mbg" id="mbg" onclick="if(event.target===this)fechar()"><div class="mcard">
<div class="mhead"><h3 id="mtit"></h3><button onclick="fechar()">&times;</button></div>
<div class="mbody" id="mbody"></div></div></div>
<script>const D={BLOB};
{JS}</script></body></html>"""
open(os.path.join(os.path.dirname(AQUI),"caixa.html"),"w",encoding="utf-8").write(HTML)
f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
print("gravado caixa.html | %d bytes | horizonte de %d dias"%(len(HTML),D.get("horizonte",90)))
for k,x in ents.items():
    print("  %-11s saldo %14s | %4d titulos no horizonte | %d nao conciliados"%(
        x["nome"],f(x["saldo_hoje"]),len(x["itens"]),x["naoconc"]))
