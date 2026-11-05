# -*- coding: utf-8 -*-
"""Simulador de cenarios do grupo Yo / Boldro.

Pagina separada do painel de proposito: o painel mostra o que aconteceu e cada
numero abre no lancamento; aqui nada abre, porque nada aconteceu. Misturar os
dois na mesma tela e convite para alguem fotografar um numero simulado e
mandar como se fosse real.

Base: os grupos da DRE de dados_painel.json, os mesmos do painel. Com todas as
alavancas em zero o cenario reproduz o mes base ao centavo — e a propria pagina
confere isso no carregamento.
"""
import json
import os

from gera_painel import CSS, D

BASE = {
    'meses': D['meses'],
    'meses_nome': {m: D['meses_nome'][m] for m in D['meses']},
    'grupo_nome': D['grupo_nome'],
    'dias': {m: (D.get('dias') or {}).get(m, 30) for m in D['meses']},
    'ents': {},
}
GRUPOS = ['2', '3', '4', '5', '6', '7', '8', '9', '14', '10']
for e, dados in D['ents'].items():
    BASE['ents'][e] = {
        'nome': dados['nome'],
        'meses': {m: {g: round((dados['comp'].get(m) or {}).get('grupos', {}).get(g, 0.0), 2)
                      for g in ['FAT'] + GRUPOS}
                  for m in D['meses']},
    }

JS = r"""
var G=['2','3','4','5','6','7','8','9','14','10'];
/* variavel = acompanha a venda proporcionalmente. Deducao, taxa de cartao e CMV
   nascem variaveis porque e o que a propria base mostra; o resto nasce fixo e
   quem simula decide. Nao ha verdade aqui, ha premissa — por isso ela aparece
   na tela como um botao, nao escondida no codigo. */
var VAR0={'2':1,'3':1,'4':1,'5':0,'6':0,'7':0,'8':0,'9':0,'14':0,'10':0};
var ENT='consol', MES=S.meses[S.meses.length-1];
var L={venda:0};                       /* alavancas, em % */
var VARI={};                           /* variavel por grupo */
G.forEach(function(g){L[g]=0;VARI[g]=VAR0[g]});

function brl(v,d){return (v<0?'−':'')+'R$ '+Math.abs(v).toLocaleString('pt-BR',
 {minimumFractionDigits:d===undefined?0:d,maximumFractionDigits:d===undefined?0:d})}
function pct(v,b){return b?(100*v/b).toFixed(1).replace('.',',')+'%':'—'}
function sg(v){return (v>0?'+':'')+v.toFixed(0)+'%'}

function baseDe(ent,mes){
 if(ent!=='consol')return S.ents[ent].meses[mes];
 var o={};['FAT'].concat(G).forEach(function(k){o[k]=0});
 ['boldro','yo'].forEach(function(e){
  var b=S.ents[e].meses[mes];['FAT'].concat(G).forEach(function(k){o[k]+=b[k]||0})});
 return o;
}

/* o cenario: a venda move os grupos marcados como variaveis, e cada grupo tem
   ainda a sua propria variacao. Os dois efeitos se multiplicam, nao se somam —
   vender 10% a mais E negociar o CMV 5% a menos da 1,10 x 0,95, nao 1,05. */
function cenario(){
 var b=baseDe(ENT,MES), v=1+L.venda/100, o={FAT:b.FAT*v};
 G.forEach(function(g){o[g]=b[g]*(1+L[g]/100)*(VARI[g]?v:1)});
 return o;
}
function ebitda(x){var t=x.FAT;['2','3','4','5','6','7','8','9','14'].forEach(
 function(g){t+=x[g]||0});return t}
function lucro(x){return ebitda(x)+(x['10']||0)}

/* ponto de equilibrio: a receita em que o EBITDA zera, mantido o mix do
   cenario. So existe se a margem de contribuicao for positiva. */
function equilibrio(x){
 var b=baseDe(ENT,MES), v=1+L.venda/100, fix=0, varp=0;
 G.forEach(function(g){
  if(g==='10')return;
  var val=b[g]*(1+L[g]/100);
  if(VARI[g]){varp+= b.FAT? (val*v)/(b.FAT*v) :0}else{fix+=val}
 });
 var mc=1+varp;                        /* varp e negativo */
 return mc>0?(-fix)/mc:null;
}

function linha(rot,base,cen,cls,bfat,cfat){
 var d=cen-base;
 return '<tr'+(cls?' class="'+cls+'"':'')+'><td class="l">'+rot+'</td>'+
  '<td class="num">'+brl(base)+'</td><td class="av">'+pct(base,bfat)+'</td>'+
  '<td class="num">'+brl(cen)+'</td><td class="av">'+pct(cen,cfat)+'</td>'+
  '<td class="num '+(Math.abs(d)<0.5?'':(d>0?'up':'dn'))+'">'+
  (Math.abs(d)<0.5?'—':brl(d))+'</td></tr>';
}

function render(){
 var b=baseDe(ENT,MES), c=cenario();
 var eb=ebitda(b), ec=ebitda(c), lb=lucro(b), lc=lucro(c);
 var dias=S.dias[MES]||30;

 document.getElementById('cards').innerHTML=[
  ['Venda bruta',brl(c.FAT),sg(L.venda)+' sobre '+brl(b.FAT),brl(c.FAT/dias)+' por dia'],
  ['EBITDA',brl(ec),pct(ec,c.FAT)+' sobre a venda bruta',
   'base: '+brl(eb)+' · '+pct(eb,b.FAT)],
  ['Efeito no EBITDA',(ec-eb>0?'+':'')+brl(ec-eb),
   (Math.abs(eb)>0.5?sg(100*(ec-eb)/Math.abs(eb)):'—')+' contra o mês base',
   'é o que o cenário coloca ou tira do bolso'],
  ['Lucro líquido',brl(lc),'depois do resultado financeiro','base: '+brl(lb)],
  (function(){var q=equilibrio(c);
   return q===null?['Ponto de equilíbrio','—','a margem de contribuição do cenário é negativa',
     'cada real vendido custa mais de um real']
    :['Ponto de equilíbrio',brl(q),'venda bruta que zera o EBITDA',
      (c.FAT>=q?'o cenário está ':'o cenário está ')+brl(Math.abs(c.FAT-q))+
      (c.FAT>=q?' acima':' abaixo')+' · '+brl(q/dias)+' por dia'];})()
 /* mesma marcacao do card do painel, para as duas telas lerem igual */
 ].map(function(x){return '<div class="kpi"><div class="t">'+x[0]+'</div>'+
   '<div class="v num">'+x[1]+'</div><div class="d">'+x[2]+'</div>'+
   (x[3]?'<div class="ref">'+x[3]+'</div>':'')+'</div>'}).join('');

 var h='<table class="xtbl sim"><thead><tr><th class="l">DRE do cenário</th>'+
  '<th>Base · '+S.meses_nome[MES]+'</th><th class="av">AV</th>'+
  '<th>Cenário</th><th class="av">AV</th><th>Diferença</th></tr></thead><tbody>';
 h+=linha('Receita bruta (venda)',b.FAT,c.FAT,'res',b.FAT,c.FAT);
 G.forEach(function(g){
  if(!b[g]&&!c[g])return;
  if(g==='10')return;
  h+=linha('('+(g==='2'?'−':'−')+') '+S.grupo_nome[g]+
    (VARI[g]?' <span class="vtag">variável</span>':''),b[g],c[g],'',b.FAT,c.FAT);
 });
 h+=linha('<b>= EBITDA</b>',eb,ec,'res',b.FAT,c.FAT);
 if(b['10']||c['10'])h+=linha('(±) '+S.grupo_nome['10'],b['10'],c['10'],'',b.FAT,c.FAT);
 h+=linha('<b>= Lucro líquido</b>',lb,lc,'res',b.FAT,c.FAT);
 h+='</tbody></table>';
 document.getElementById('tbl').innerHTML=h;

 document.getElementById('lvvenda').textContent=sg(L.venda);
 G.forEach(function(g){
  var e=document.getElementById('lv'+g); if(e)e.textContent=sg(L[g]);
  var t=document.getElementById('vt'+g); if(t)t.className='vsw'+(VARI[g]?' on':'');
 });
}

function setL(k,v){L[k]=Math.max(-100,Math.min(400,parseFloat(v)||0));
 var s=document.getElementById('sl'+k); if(s)s.value=L[k];
 var n=document.getElementById('nb'+k); if(n)n.value=L[k];
 render()}
function setVar(g){VARI[g]=VARI[g]?0:1;render()}
function setEnt(e){ENT=e;document.querySelectorAll('.entsw button').forEach(function(b){
 b.classList.toggle('on',b.dataset.e===e)});render()}
function setMes(m){MES=m;document.querySelectorAll('.mespills button').forEach(function(b){
 b.classList.toggle('on',b.dataset.m===m)});render()}
function zerar(){L.venda=0;G.forEach(function(g){L[g]=0;VARI[g]=VAR0[g]});
 document.querySelectorAll('input[type=range]').forEach(function(s){s.value=0});
 document.querySelectorAll('input[type=number]').forEach(function(n){n.value=0});
 render()}

/* painel de alavancas */
(function(){
 function lev(id,rot,sub,g){
  return '<div class="lev"><div class="lv-h"><span class="lv-n">'+rot+'</span>'+
   (g?'<span class="vsw'+(VARI[g]?' on':'')+'" id="vt'+g+'" onclick="setVar(\''+g+'\')"'+
     ' title="variável acompanha a venda; fixo não">acompanha a venda</span>':'')+
   '<span class="lv-v" id="lv'+id+'">+0%</span></div>'+
   '<div class="lv-r"><input type="range" id="sl'+id+'" min="-100" max="'+(id==='venda'?'200':'200')+
   '" step="1" value="0" oninput="setL(\''+id+'\',this.value)">'+
   '<input type="number" id="nb'+id+'" value="0" step="1" onchange="setL(\''+id+'\',this.value)"><span class="pc">%</span></div>'+
   '<div class="lv-s">'+sub+'</div></div>';
 }
 var h='<div class="lev-g">'+lev('venda','Venda','move a receita e, com ela, tudo que estiver marcado como variável')+'</div>';
 h+='<div class="lev-g lev-cols">';
 G.forEach(function(g){
  if(g==='10')return;
  h+=lev(g,S.grupo_nome[g],'variação própria, além do efeito da venda',g);
 });
 h+='</div>';
 document.getElementById('levers').innerHTML=h;
})();

document.getElementById('mespills').innerHTML=S.meses.map(function(m){
 return '<button data-m="'+m+'" class="'+(m===MES?'on':'')+'" onclick="setMes(\''+m+'\')">'+
  S.meses_nome[m]+'</button>'}).join('');

/* trava: com tudo em zero o cenario TEM que reproduzir o mes base. Se um dia
   alguem mexer na formula e quebrar isso, a pagina avisa em vez de mentir. */
(function(){
 var erro=[];
 S.meses.forEach(function(m){
  ['consol','boldro','yo'].forEach(function(e){
   var g0=ENT,m0=MES;ENT=e;MES=m;
   var b=baseDe(e,m),c=cenario();
   ['FAT'].concat(G).forEach(function(k){
    if(Math.abs((b[k]||0)-(c[k]||0))>0.005)erro.push(e+' '+m+' '+k)});
   ENT=g0;MES=m0;
  });
 });
 if(erro.length){
  document.getElementById('aviso').innerHTML='<div class="aviso erro"><h4>'+
   'O cenário zerado não reproduz o mês base — não confie nestes números</h4><p>'+
   erro.slice(0,8).join(' · ')+'</p></div>';
  if(window.console)console.error('trava do simulador:',erro);
 }
})();
render();
"""

CSS_SIM = """
#cards{grid-template-columns:repeat(5,1fr)}
@media(max-width:1100px){#cards{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){#cards{grid-template-columns:1fr}}
.simwrap{max-width:1180px;margin:0 auto;padding:0 24px}
.lev-g{display:grid;gap:14px;margin-bottom:18px}
.lev-cols{grid-template-columns:repeat(auto-fit,minmax(290px,1fr))}
.lev{background:#fff;border:1px solid var(--g200);border-radius:10px;padding:14px 16px}
.lev-g:first-child .lev{border-left:3px solid var(--orange)}
.lv-h{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.lv-n{font-family:'Plus Jakarta Sans';font-weight:700;font-size:13.5px;color:var(--ink)}
.lv-v{margin-left:auto;font-family:'Plus Jakarta Sans';font-weight:800;font-size:15px;
 color:var(--orange);font-variant-numeric:tabular-nums}
.lv-r{display:flex;align-items:center;gap:10px}
.lv-r input[type=range]{flex:1;accent-color:var(--orange);min-width:0}
.lv-r input[type=number]{width:66px;padding:5px 7px;border:1px solid var(--g300);
 border-radius:6px;font-family:'Plus Jakarta Sans';font-size:13px;text-align:right}
.lv-r .pc{font-size:12px;color:var(--g500)}
.lv-s{font-size:11.5px;color:var(--g500);margin-top:7px;line-height:1.45}
.vsw{font-family:'Plus Jakarta Sans';font-size:10px;font-weight:700;letter-spacing:.06em;
 text-transform:uppercase;color:var(--g400);border:1px solid var(--g300);border-radius:20px;
 padding:3px 9px;cursor:pointer;user-select:none}
.vsw.on{color:#fff;background:var(--orange);border-color:var(--orange)}
.xtbl.sim td.up{color:var(--in);font-weight:600}
.xtbl.sim td.dn{color:var(--out);font-weight:600}
.vtag{font-size:10px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
 color:var(--orange);margin-left:7px}
.simbar{display:flex;align-items:center;gap:12px;margin:0 0 16px}
.simbar .zb{font-family:'Plus Jakarta Sans';font-size:12px;font-weight:700;color:var(--ink2);
 background:#fff;border:1px solid var(--g300);border-radius:7px;padding:7px 13px;cursor:pointer}
.simbar .zb:hover{border-color:var(--orange);color:var(--orange)}
@media(max-width:700px){.simwrap{padding:0 16px}}
"""


def pagina():
    return """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Simulador de cenários · Yó / Boldró</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,400&display=swap" rel="stylesheet">
<style>%s%s</style></head><body>

<nav class="nav"><div class="wrap">
<div class="brand">Grupo <b>Yó / Boldró</b></div>
<div class="nav-links"><a href="index.html">Painel</a><a href="#" class="on">Simulador</a></div>
<div class="entsw" id="entsw">
<button data-e="consol" class="on" onclick="setEnt('consol')">Consolidado</button>
<button data-e="boldro" onclick="setEnt('boldro')">Boldró</button>
<button data-e="yo" onclick="setEnt('yo')">YO</button>
</div>
</div></nav>

<header class="hero"><div class="wrap">
<div class="eyebrow">Simulador de cenários · 2026</div>
<h1>E se <b>mudar</b>?</h1>
<div class="cnpjline">Nada aqui aconteceu. É a DRE de um mês fechado com as alavancas que você mexer — e nenhum número abre em lançamento, porque não existe lançamento de cenário.</div>
<div class="mespills" id="mespills"></div>
</div></header>

<div class="wrap"><div class="kpis" id="cards"></div></div>

<section class="sec-alt"><div class="wrap">
<div class="sec-head"><div class="k">Alavancas</div>
<h2>O que você <span class="light">quer mexer</span></h2>
<p class="lede">A venda move tudo que estiver marcado como <b>acompanha a venda</b>. Cada linha tem ainda a variação dela, que entra por cima — vender 10%% a mais e negociar o CMV 5%% a menos dá 1,10 × 0,95, não 1,05.</p></div>
<div class="simbar"><button class="zb" onclick="zerar()">Zerar tudo</button>
<span class="lv-s">com tudo em zero o cenário reproduz o mês base ao centavo</span></div>
<div id="levers"></div>
</div></section>

<section><div class="wrap">
<div class="sec-head"><div class="k">Resultado</div>
<h2>A DRE <span class="light">do cenário</span></h2>
<p class="lede">Lado a lado com o mês base, com a análise vertical sobre a venda bruta de cada coluna.</p></div>
<div id="aviso"></div>
<div class="rsm-wrap" id="tbl"></div>
<p class="repnote"><b>O que o simulador não sabe:</b> degrau. Ele trata cada linha como proporcional ou fixa, e a vida não é assim — dobrar a venda pede mais gente, mais geladeira e outro contrato de energia, e nada disso aparece aqui. Serve para medir a sensibilidade do resultado a cada alavanca, não para prever o mês. O ponto de equilíbrio sai do mix fixo × variável que você marcou; mude a marcação e ele muda.</p>
</div></section>

<footer class="foot"><div class="wrap"><div class="fg">
<div><div class="sig">João Victor Andrade de Souza</div><div class="r">Sócio-fundador · Exact BR</div></div>
<div style="text-align:right"><div class="r" style="margin-bottom:4px">Disciplina Gera Lucro</div>
<div style="font-family:'Plus Jakarta Sans';font-size:13px;font-weight:500;color:rgba(255,255,255,.85)">Exact BR · Recife — PE</div></div>
</div>
<p class="disc">Simulador de cenários · Grupo Yó / Boldró. A base de cada mês são os mesmos grupos da DRE do painel, lidos do Omie. Nenhum cenário é gravado em lugar nenhum: recarregar a página volta ao mês base. Os números desta tela são hipótese, não resultado — o resultado está no painel.</p>
</div></footer>

<script>const S=%s;%s</script>
</body></html>""" % (CSS, CSS_SIM, json.dumps(BASE, ensure_ascii=False), JS)


if __name__ == '__main__':
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulador.html')
    open(p, 'w').write(pagina())
    print('gerado simulador.html (%.0f KB)' % (os.path.getsize(p) / 1024))
