# -*- coding: utf-8 -*-
"""Simulador de cenarios do grupo Yo / Boldro.

Pagina separada do painel de proposito: o painel mostra o que aconteceu e cada
numero abre no lancamento; aqui nada abre, porque nada aconteceu. Misturar os
dois na mesma tela e convite para alguem fotografar um numero simulado e
mandar como se fosse real.

Layout de dashboard: alavancas fixas a esquerda, os tres cenarios a direita,
sem precisar rolar entre mexer e ver. Base: os grupos da DRE de
dados_painel.json, os mesmos do painel. Com todas as alavancas em zero o
cenario reproduz o mes base ao centavo — e a propria pagina confere isso no
carregamento.
"""
import json
import os

from gera_painel import CSS, D

GRUPOS = ['2', '3', '4', '5', '6', '7', '8', '9', '14', '10']
BASE = {
    'meses': D['meses'],
    'meses_nome': {m: D['meses_nome'][m] for m in D['meses']},
    'grupo_nome': D['grupo_nome'],
    'dias': {m: (D.get('dias') or {}).get(m, 30) for m in D['meses']},
    'ents': {e: {'nome': v['nome'],
                 'meses': {m: {g: round((v['comp'].get(m) or {}).get('grupos', {}).get(g, 0.0), 2)
                               for g in ['FAT'] + GRUPOS}
                           for m in D['meses']}}
             for e, v in D['ents'].items()},
}

JS = r"""
var G=['2','3','4','5','6','7','8','9','14','10'];
var GOP=['2','3','4','5','6','7','8','9','14'];     /* o que entra no EBITDA */
/* variavel = acompanha a venda proporcionalmente. Deducao, taxa de cartao e CMV
   nascem variaveis porque e o que a base mostra; o resto nasce fixo e quem
   simula decide. Nao ha verdade aqui, ha premissa — por isso ela e um botao
   na tela, nao uma regra escondida no codigo. */
var VAR0={'2':1,'3':1,'4':1,'5':0,'6':0,'7':0,'8':0,'9':0,'14':0,'10':0};
var CHAVE='yoboldro.simulador.v1';

function cenZero(nome){
 var c={nome:nome,L:{venda:0},V:{}};
 G.forEach(function(g){c.L[g]=0;c.V[g]=VAR0[g]});
 return c;
}
var EST={ent:'consol',mes:S.meses[S.meses.length-1],ativo:0,
 cen:[cenZero('Cenário A'),cenZero('Cenário B'),cenZero('Cenário C')]};

/* a visao fica no navegador de quem abre: nao viaja, nao e dado da empresa e
   nunca volta para mim. Se o storage estiver bloqueado a pagina funciona igual,
   so nao lembra. */
function salvar(){try{localStorage.setItem(CHAVE,JSON.stringify(EST));
 marcaSalvo()}catch(e){}}
function carregar(){
 try{
  var x=JSON.parse(localStorage.getItem(CHAVE)||'null');
  if(!x||!x.cen||x.cen.length!==3)return false;
  if(S.meses.indexOf(x.mes)<0)x.mes=S.meses[S.meses.length-1];
  EST=x;return true;
 }catch(e){return false}
}
function marcaSalvo(){
 var e=document.getElementById('savmark'); if(!e)return;
 var d=new Date();
 e.textContent='visão salva neste navegador · '+
  ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2);
}
function limpar(){
 if(!confirm('Apaga os três cenários e volta ao padrão. Continuar?'))return;
 try{localStorage.removeItem(CHAVE)}catch(e){}
 EST={ent:EST.ent,mes:EST.mes,ativo:0,
  cen:[cenZero('Cenário A'),cenZero('Cenário B'),cenZero('Cenário C')]};
 montaAlavancas();render();
 var e=document.getElementById('savmark'); if(e)e.textContent='voltou ao padrão';
}

function brl(v,d){return (v<0?'−':'')+'R$ '+Math.abs(v).toLocaleString('pt-BR',
 {minimumFractionDigits:d===undefined?0:d,maximumFractionDigits:d===undefined?0:d})}
function pct(v,b){return b?(100*v/b).toFixed(1).replace('.',',')+'%':'—'}
function sg(v){return (v>0?'+':'')+(+v).toFixed(0)+'%'}
function cen(){return EST.cen[EST.ativo]}

function baseDe(){
 var mes=EST.mes;
 if(EST.ent!=='consol')return S.ents[EST.ent].meses[mes];
 var o={};['FAT'].concat(G).forEach(function(k){o[k]=0});
 ['boldro','yo'].forEach(function(e){
  var b=S.ents[e].meses[mes];['FAT'].concat(G).forEach(function(k){o[k]+=b[k]||0})});
 return o;
}
/* a venda move os grupos marcados como variaveis, e cada grupo tem ainda a sua
   propria variacao. Os dois efeitos se MULTIPLICAM: vender 10% a mais e
   negociar o CMV 5% a menos da 1,10 x 0,95, nao 1,05. */
function projeta(c,b){
 b=b||baseDe();
 var v=1+c.L.venda/100, o={FAT:b.FAT*v};
 G.forEach(function(g){o[g]=b[g]*(1+c.L[g]/100)*(c.V[g]?v:1)});
 return o;
}
function ebitda(x){var t=x.FAT;GOP.forEach(function(g){t+=x[g]||0});return t}
function lucro(x){return ebitda(x)+(x['10']||0)}
function mexido(c){
 if(c.L.venda)return true;
 for(var i=0;i<G.length;i++){if(c.L[G[i]])return true;
  if(c.V[G[i]]!==VAR0[G[i]])return true}
 return false;
}
/* ponto de equilibrio: a receita em que o EBITDA zera, mantido o mix do
   cenario. So existe se a margem de contribuicao for positiva. */
function equilibrio(c,b){
 b=b||baseDe();
 var fix=0,taxa=0;
 GOP.forEach(function(g){
  var val=b[g]*(1+c.L[g]/100);
  if(c.V[g]){taxa+= b.FAT?val/b.FAT:0}else{fix+=val}
 });
 var mc=1+taxa;
 return mc>0?(-fix)/mc:null;
}

/* ---------- alavancas ---------- */
function montaAlavancas(){
 var c=cen();
 function lev(id,rot,sub,g){
  return '<div class="lev"><div class="lv-h"><span class="lv-n">'+rot+'</span>'+
   '<span class="lv-v" id="lv'+id+'">'+sg(c.L[id])+'</span></div>'+
   '<div class="lv-r"><input type="range" id="sl'+id+'" min="-100" max="200" step="1" '+
   'value="'+c.L[id]+'" oninput="setL(\''+id+'\',this.value)">'+
   '<input type="number" id="nb'+id+'" value="'+c.L[id]+'" step="1" '+
   'onchange="setL(\''+id+'\',this.value)"><span class="pc">%</span></div>'+
   (g?'<div class="lv-f"><span class="vsw'+(c.V[g]?' on':'')+'" id="vt'+g+'" '+
     'onclick="setVar(\''+g+'\')">acompanha a venda</span></div>'
     :'<div class="lv-s">'+sub+'</div>')+'</div>';
 }
 var h='<div class="lev-top">'+lev('venda','Venda',
   'move a receita e tudo que estiver marcado como variável')+'</div>';
 G.forEach(function(g){h+=lev(g,S.grupo_nome[g],'',g)});
 document.getElementById('levers').innerHTML=h;
}
function setL(k,v){
 cen().L[k]=Math.max(-100,Math.min(200,Math.round(parseFloat(v)||0)));
 var s=document.getElementById('sl'+k); if(s)s.value=cen().L[k];
 var n=document.getElementById('nb'+k); if(n)n.value=cen().L[k];
 var e=document.getElementById('lv'+k); if(e)e.textContent=sg(cen().L[k]);
 render();salvar();
}
function setVar(g){
 cen().V[g]=cen().V[g]?0:1;
 var t=document.getElementById('vt'+g); if(t)t.className='vsw'+(cen().V[g]?' on':'');
 render();salvar();
}
function setAtivo(i){EST.ativo=i;montaAlavancas();render();salvar()}
function setEnt(e){EST.ent=e;render();salvar()}
function setMes(m){EST.mes=m;render();salvar()}
function renomeia(i){
 var n=prompt('Nome do cenário:',EST.cen[i].nome);
 if(n===null)return;
 EST.cen[i].nome=(n.trim()||'Cenário '+'ABC'[i]).slice(0,28);
 render();salvar();
}
function zeraCen(i){EST.cen[i]=cenZero(EST.cen[i].nome);
 if(i===EST.ativo)montaAlavancas();render();salvar()}
function copia(i){
 var o=EST.cen[EST.ativo];
 EST.cen[i]={nome:EST.cen[i].nome,L:JSON.parse(JSON.stringify(o.L)),
             V:JSON.parse(JSON.stringify(o.V))};
 render();salvar();
}

/* ---------- render ---------- */
function render(){
 var b=baseDe(), P=EST.cen.map(function(c){return projeta(c,b)});
 var ebB=ebitda(b), ebP=P.map(ebitda);

 document.querySelectorAll('.entsw button').forEach(function(x){
  x.classList.toggle('on',x.dataset.e===EST.ent)});
 document.querySelectorAll('.mespills button').forEach(function(x){
  x.classList.toggle('on',x.dataset.m===EST.mes)});

 /* abas dos cenarios */
 document.getElementById('tabs').innerHTML=EST.cen.map(function(c,i){
  var d=ebP[i]-ebB;
  return '<button class="ctab'+(i===EST.ativo?' on':'')+(mexido(c)?'':' zero')+'" '+
   'onclick="setAtivo('+i+')" ondblclick="renomeia('+i+')">'+
   '<span class="cn">'+c.nome+(i===EST.ativo?'<span class="edt">editando</span>':'')+'</span>'+
   '<span class="cv '+(Math.abs(d)<0.5?'':(d>0?'up':'dn'))+'">'+
   (mexido(c)?(d>0?'+':'')+brl(d):'sem alteração')+'</span></button>';
 }).join('')+'<span class="tabtools">'+
  '<button class="tb" onclick="renomeia('+EST.ativo+')" title="renomear o cenário ativo">renomear</button>'+
  '<button class="tb" onclick="copia('+((EST.ativo+1)%3)+')" title="copia o ativo para o próximo">duplicar →</button>'+
  '<button class="tb" onclick="zeraCen('+EST.ativo+')" title="zera só o cenário ativo">zerar</button>'+
  '</span>';

 /* faixa de indicadores do cenario ativo */
 var c=cen(), p=P[EST.ativo], dias=S.dias[EST.mes]||30;
 var qB=equilibrio(cenZero(''),b), q=equilibrio(c,b);
 document.getElementById('cards').innerHTML=[
  ['Venda bruta',brl(p.FAT),sg(c.L.venda)+' · base '+brl(b.FAT),brl(p.FAT/dias)+' por dia'],
  ['EBITDA',brl(ebitda(p)),pct(ebitda(p),p.FAT)+' da venda bruta',
   'base '+brl(ebB)+' · '+pct(ebB,b.FAT)],
  ['Efeito no EBITDA',(ebitda(p)-ebB>0?'+':'')+brl(ebitda(p)-ebB),
   'contra o mês base','é o que o cenário põe ou tira do bolso'],
  ['Lucro líquido',brl(lucro(p)),'depois do resultado financeiro','base '+brl(lucro(b))],
  ['Custo fixo do mês',brl(-custoFixo(c,b)),'o que corre sem vender',
   'variável: '+pct(-(somaVar(c,b)),p.FAT)+' da venda'],
  (q===null?['Ponto de equilíbrio','—','margem de contribuição negativa',
    'cada real vendido custa mais de um real']
   :['Ponto de equilíbrio',brl(q),'venda que zera o EBITDA',
     (p.FAT>=q?'cenário '+brl(p.FAT-q)+' acima':'cenário '+brl(q-p.FAT)+' abaixo')+
     ' · base '+(qB===null?'—':brl(qB))])
 ].map(function(x){return '<div class="kpi"><div class="t">'+x[0]+'</div>'+
   '<div class="v num">'+x[1]+'</div><div class="d">'+x[2]+'</div>'+
   '<div class="ref">'+x[3]+'</div></div>'}).join('');

 /* DRE dos tres cenarios lado a lado */
 function cel(v,bv,fat){
  var d=v-bv;
  return '<td class="num cc"><span class="cvl">'+brl(v)+'</span>'+
   '<span class="cpc">'+pct(v,fat)+'</span>'+
   '<span class="cdl '+(Math.abs(d)<0.5?'':(d>0?'up':'dn'))+'">'+
   (Math.abs(d)<0.5?'—':(d>0?'+':'')+brl(d))+'</span></td>';
 }
 var h='<table class="xtbl sim"><thead><tr><th class="l">DRE</th>'+
  '<th>Base · '+S.meses_nome[EST.mes]+'</th>'+
  EST.cen.map(function(x,i){return '<th'+(i===EST.ativo?' class="ath"':'')+'>'+
   x.nome+'</th>'}).join('')+'</tr></thead><tbody>';
 function lin(rot,k,cls){
  var bv=(k==='EB')?ebB:((k==='LL')?lucro(b):b[k]);
  var o='<tr'+(cls?' class="'+cls+'"':'')+'><td class="l">'+rot+'</td>'+
   '<td class="num cc"><span class="cvl">'+brl(bv)+'</span>'+
   '<span class="cpc">'+pct(bv,b.FAT)+'</span></td>';
  P.forEach(function(x){
   var v=(k==='EB')?ebitda(x):((k==='LL')?lucro(x):x[k]);
   o+=cel(v,bv,x.FAT)});
  return o+'</tr>';
 }
 h+=lin('Receita bruta (venda)','FAT','res');
 GOP.forEach(function(g){
  if(!b[g])return;
  h+=lin('(−) '+S.grupo_nome[g]+(c.V[g]?' <span class="vtag">var</span>':''),g);
 });
 h+=lin('<b>= EBITDA</b>','EB','res');
 if(b['10'])h+=lin('(±) '+S.grupo_nome['10'],'10');
 h+=lin('<b>= Lucro líquido</b>','LL','res');
 h+='</tbody></table>';
 document.getElementById('tbl').innerHTML=h;

 /* comparacao visual do EBITDA */
 var tudo=[ebB].concat(ebP), mx=Math.max.apply(null,tudo.map(Math.abs))||1;
 document.getElementById('bars').innerHTML=
  [['Base · '+S.meses_nome[EST.mes],ebB,'base']].concat(
   EST.cen.map(function(x,i){return [x.nome,ebP[i],i===EST.ativo?'at':'']}))
  .map(function(x){
   return '<div class="bar '+x[2]+'"><div class="bl">'+x[0]+'</div>'+
    '<div class="bt"><i style="width:'+(100*Math.abs(x[1])/mx).toFixed(1)+'%;'+
    'background:'+(x[1]<0?'var(--out)':'var(--orange)')+'"></i></div>'+
    '<div class="bv num">'+brl(x[1])+'</div>'+
    '<div class="bp">'+pct(x[1],x[2]==='base'?b.FAT:P[['','at'].indexOf(x[2])>=0?0:0].FAT)+'</div></div>';
  }).join('');
 /* o percentual de cada barra e sobre a venda DAQUELA coluna */
 var bl=document.querySelectorAll('#bars .bp');
 if(bl[0])bl[0].textContent=pct(ebB,b.FAT);
 EST.cen.forEach(function(x,i){if(bl[i+1])bl[i+1].textContent=pct(ebP[i],P[i].FAT)});
}
function custoFixo(c,b){
 var t=0;GOP.forEach(function(g){if(!c.V[g])t+=b[g]*(1+c.L[g]/100)});return t}
function somaVar(c,b){
 var t=0;GOP.forEach(function(g){if(c.V[g])t+=b[g]*(1+c.L[g]/100)*(1+c.L.venda/100)});return t}

/* ---------- montagem ---------- */
document.getElementById('mespills').innerHTML=S.meses.map(function(m){
 return '<button data-m="'+m+'" onclick="setMes(\''+m+'\')">'+S.meses_nome[m]+'</button>'}).join('');

/* trava: com tudo em zero o cenario TEM que reproduzir o mes base. Se alguem
   mexer na formula e quebrar isso, a pagina avisa em vez de mentir. */
(function(){
 var erro=[], g0=EST.ent, m0=EST.mes, z=cenZero('');
 S.meses.forEach(function(m){['consol','boldro','yo'].forEach(function(e){
  EST.ent=e;EST.mes=m;
  var b=baseDe(), c=projeta(z,b);
  ['FAT'].concat(G).forEach(function(k){
   if(Math.abs((b[k]||0)-(c[k]||0))>0.005)erro.push(e+' '+m+' '+k)});
 })});
 EST.ent=g0;EST.mes=m0;
 if(erro.length){
  document.getElementById('aviso').innerHTML='<div class="aviso erro"><h4>'+
   'O cenário zerado não reproduz o mês base — não confie nestes números</h4><p>'+
   erro.slice(0,8).join(' · ')+'</p></div>';
  if(window.console)console.error('trava do simulador:',erro);
 }
})();

if(carregar())marcaSalvo();
montaAlavancas();
render();
"""

CSS_SIM = """
.dashbar{display:flex;align-items:center;gap:14px;flex-wrap:wrap;
 padding:12px 0;border-bottom:1px solid var(--line)}
.dash{display:grid;grid-template-columns:318px minmax(0,1fr);gap:20px;
 align-items:start;padding:20px 0 40px}
.lcol{position:sticky;top:14px;max-height:calc(100vh - 28px);overflow-y:auto;
 padding-right:6px}
.lcol::-webkit-scrollbar{width:7px}
.lcol::-webkit-scrollbar-thumb{background:var(--g300);border-radius:4px}
.lev{background:#fff;border:1px solid var(--g200);border-radius:9px;
 padding:10px 12px;margin-bottom:8px}
.lev-top .lev{border-left:3px solid var(--orange);padding:12px 14px}
.lv-h{display:flex;align-items:baseline;gap:8px}
.lv-n{font-family:'Plus Jakarta Sans';font-weight:700;font-size:12.5px;color:var(--ink);
 line-height:1.25}
.lev-top .lv-n{font-size:15px}
.lv-v{margin-left:auto;font-family:'Plus Jakarta Sans';font-weight:800;font-size:13.5px;
 color:var(--orange);font-variant-numeric:tabular-nums;white-space:nowrap}
.lv-r{display:flex;align-items:center;gap:8px;margin-top:6px}
.lv-r input[type=range]{flex:1;accent-color:var(--orange);min-width:0;height:18px}
.lv-r input[type=number]{width:58px;padding:4px 6px;border:1px solid var(--g300);
 border-radius:5px;font-family:'Plus Jakarta Sans';font-size:12px;text-align:right}
.lv-r .pc{font-size:11px;color:var(--g500)}
.lv-s{font-size:11px;color:var(--g500);margin-top:6px;line-height:1.4}
.lv-f{margin-top:7px}
.vsw{display:inline-block;font-family:'Plus Jakarta Sans';font-size:9.5px;font-weight:700;
 letter-spacing:.05em;text-transform:uppercase;color:var(--g400);border:1px solid var(--g300);
 border-radius:20px;padding:2px 8px;cursor:pointer;user-select:none}
.vsw.on{color:#fff;background:var(--orange);border-color:var(--orange)}
.rcol{display:flex;flex-direction:column;gap:16px;min-width:0}
#cards{grid-template-columns:repeat(3,1fr);margin:0}
@media(max-width:1250px){#cards{grid-template-columns:repeat(2,1fr)}}
#cards .kpi{padding:14px 15px}
#cards .v{font-size:23px}
#tabs{display:flex;flex-direction:column;gap:6px}
.ctab{width:100%}
.ctab{display:flex;flex-direction:column;align-items:flex-start;gap:2px;
 background:#fff;border:1px solid var(--g300);border-radius:9px;padding:8px 14px;
 cursor:pointer;min-width:150px;text-align:left}
.ctab.on{border-color:var(--orange);box-shadow:0 0 0 1px var(--orange)}
.ctab .cn{font-family:'Plus Jakarta Sans';font-weight:700;font-size:12.5px;color:var(--ink);
 display:flex;align-items:center;gap:7px;width:100%}
.ctab .edt{margin-left:auto;font-size:9px;font-weight:700;letter-spacing:.06em;
 text-transform:uppercase;color:var(--orange)}
.ctab .cv{font-family:'Plus Jakarta Sans';font-weight:700;font-size:12px;
 font-variant-numeric:tabular-nums;color:var(--g500)}
.ctab.zero .cv{color:var(--g400);font-weight:500}
.ctab .cv.up{color:var(--in)}.ctab .cv.dn{color:var(--out)}
.tabtools{display:flex;gap:6px;margin-top:2px}
.tabtools .tb{flex:1}
.tb{font-family:'Plus Jakarta Sans';font-size:11px;font-weight:700;color:var(--ink2);
 background:#fff;border:1px solid var(--g300);border-radius:6px;padding:5px 10px;cursor:pointer}
.tb:hover{border-color:var(--orange);color:var(--orange)}
.xtbl.sim td.cc{text-align:right;white-space:nowrap;line-height:1.3;padding-top:7px;
 padding-bottom:7px}
.xtbl.sim .cvl{display:block;font-variant-numeric:tabular-nums}
.xtbl.sim .cpc{display:block;font-size:10.5px;color:var(--g400)}
.xtbl.sim .cdl{display:block;font-size:10.5px;font-weight:600;color:var(--g400)}
.xtbl.sim .cdl.up{color:var(--in)}.xtbl.sim .cdl.dn{color:var(--out)}
.xtbl.sim th.ath{color:var(--orange)}
.vtag{font-size:9px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
 color:var(--orange);border:1px solid var(--orange);border-radius:10px;padding:0 5px;
 margin-left:6px;vertical-align:1px}
#bars{background:#fff;border:1px solid var(--g200);border-radius:10px;padding:16px 18px}
.bar{display:grid;grid-template-columns:150px minmax(0,1fr) 110px 54px;align-items:center;
 gap:12px;padding:6px 0}
.bar .bl{font-family:'Plus Jakarta Sans';font-size:12px;font-weight:600;color:var(--ink2);
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar.at .bl{color:var(--orange)}
.bar.base .bl{color:var(--g500);font-weight:500}
.bar .bt{height:14px;background:var(--g200);border-radius:7px;overflow:hidden}
.bar .bt i{display:block;height:100%;border-radius:7px}
.bar .bv{font-family:'Plus Jakarta Sans';font-weight:700;font-size:13px;text-align:right;
 font-variant-numeric:tabular-nums}
.bar .bp{font-size:11.5px;color:var(--g500);text-align:right}
.savline{display:flex;align-items:center;gap:10px;font-size:11.5px;color:var(--g500)}
@media(max-width:980px){
 .dash{grid-template-columns:1fr}
 .lcol{position:static;max-height:none;overflow:visible}
 .bar{grid-template-columns:110px minmax(0,1fr) 92px;gap:8px}
 .bar .bp{display:none}
}
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

<div class="wrap">
<div class="dashbar">
<div><div class="eyebrow" style="margin:0">Simulador de cenários</div>
<div style="font-family:'Plus Jakarta Sans';font-weight:800;font-size:19px;letter-spacing:-.02em">E se <span style="color:var(--orange)">mudar</span>?</div></div>
<div class="mespills" id="mespills" style="margin:0"></div>
<div class="savline" style="margin-left:auto">
<span id="savmark">a visão se salva sozinha neste navegador</span>
<button class="tb" onclick="limpar()">limpar tudo</button></div>
</div>

<div id="aviso"></div>

<div class="dash">
<div class="lcol">
<div id="tabs" style="margin-bottom:12px"></div>
<div id="levers"></div>
<p class="lv-s" style="padding:10px 2px 0">Clique duas vezes na aba para renomear o cenário. A venda move tudo que estiver marcado como <b>acompanha a venda</b>; cada linha tem ainda a variação dela, que entra por cima. Os dois efeitos multiplicam.</p>
</div>

<div class="rcol">
<div class="kpis" id="cards"></div>
<div id="bars"></div>
<div class="rsm-wrap" id="tbl"></div>
<p class="repnote" style="margin:0"><b>Nada aqui aconteceu</b> — é a DRE de um mês fechado com as alavancas que você mexer, e nenhum número abre em lançamento porque não existe lançamento de cenário. <b>O que o simulador não sabe é degrau:</b> ele trata cada linha como proporcional ou fixa, e dobrar a venda pede mais gente, mais geladeira e outro contrato de energia. Serve para medir a sensibilidade do resultado a cada alavanca, não para prever o mês. O ponto de equilíbrio sai do mix fixo × variável que você marcou — mude a marcação e ele muda. A visão fica guardada só no seu navegador: não viaja e não volta para o Omie.</p>
</div>
</div>
</div>

<footer class="foot"><div class="wrap"><div class="fg">
<div><div class="sig">João Victor Andrade de Souza</div><div class="r">Sócio-fundador · Exact BR</div></div>
<div style="text-align:right"><div class="r" style="margin-bottom:4px">Disciplina Gera Lucro</div>
<div style="font-family:'Plus Jakarta Sans';font-size:13px;font-weight:500;color:rgba(255,255,255,.85)">Exact BR · Recife — PE</div></div>
</div>
<p class="disc">Simulador de cenários · Grupo Yó / Boldró. A base de cada mês são os mesmos grupos da DRE do painel, lidos do Omie. Os números desta tela são hipótese, não resultado — o resultado está no painel.</p>
</div></footer>

<script>const S=%s;%s</script>
</body></html>""" % (CSS, CSS_SIM, json.dumps(BASE, ensure_ascii=False), JS)


if __name__ == '__main__':
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulador.html')
    open(p, 'w').write(pagina())
    print('gerado simulador.html (%.0f KB)' % (os.path.getsize(p) / 1024))
