# -*- coding: utf-8 -*-
"""Gera o painel gerencial Yó / Boldró no esqueleto do painel Amana/Topázio.

Mesma estrutura: nav com seletor de entidade (Boldró · YO · Consolidado · Sócios),
hero com pills de mês, switch de regime (caixa × competência) e a ponte do caixa em SVG,
KPIs abaixo do hero, indicadores mês a mês com análise vertical, orçado × real,
composição das saídas em donut, leitura do mês, seção operacional e relatórios com
switch DFC × DRE. O miolo é que muda: lá é pousada, aqui é restaurante e beach club.

Gera index.html e socios.html (a visão dos sócios, sem o detalhe mês a mês).
Rodar:  python3 gera_painel.py
"""
import json
import os

BASE = os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/Claude VS/omie-boldro')
D = json.load(open(os.path.join(BASE, 'dados_painel.json')))

CSS = r"""
:root{--navy:#0D0F1A;--navy2:#141726;--navy3:#1C2032;--line:#262B40;--orange:#F97316;
 --orange-soft:#FFF7ED;--offwhite:#FAFAF7;--ink:#0D0F1A;--ink2:#374151;--g400:#9CA3AF;
 --g500:#6B7280;--g300:#D1D5DB;--g200:#E5E7EB;--in:#0E9F6E;--out:#DC2626;
 --card:#fff;--shadow:0 1px 3px rgba(13,15,26,.06),0 8px 24px rgba(13,15,26,.05)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Inter',sans-serif;background:var(--offwhite);color:var(--ink);
 -webkit-font-smoothing:antialiased;line-height:1.55}
.num{font-family:'Plus Jakarta Sans',sans-serif;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.light{font-weight:300;color:var(--g500)}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px}
.nav{position:sticky;top:0;z-index:50;background:rgba(13,15,26,.92);backdrop-filter:blur(10px);
 border-bottom:1px solid rgba(255,255,255,.08)}
.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:60px;gap:16px}
.brand{font-family:'Plus Jakarta Sans';font-weight:800;font-size:13px;color:#fff;letter-spacing:.04em;
 text-transform:uppercase;white-space:nowrap}
.brand b{color:var(--orange)}
.nav-links{display:flex;gap:2px;flex:1;justify-content:center}
.nav-links a{font-family:'Plus Jakarta Sans';font-size:12.5px;font-weight:600;color:#B8BECF;
 text-decoration:none;padding:7px 11px;border-radius:8px;transition:.2s;white-space:nowrap}
.nav-links a:hover{color:#fff;background:rgba(255,255,255,.07)}
.nav-links a.on{color:var(--navy);background:var(--orange)}
.entsw{display:flex;gap:3px;background:rgba(255,255,255,.06);padding:3px;border-radius:9px}
.entsw button,.entsw a{font-family:'Plus Jakarta Sans';font-size:11.5px;font-weight:700;color:#B8BECF;
 background:none;border:none;padding:6px 11px;border-radius:7px;cursor:pointer;transition:.2s;
 text-decoration:none;display:inline-block}
.entsw button:hover,.entsw a:hover{color:#fff}
.entsw button.on,.entsw a.on{background:#fff;color:var(--navy)}
@media(max-width:1100px){.nav-links{display:none}}
.hero{background:var(--navy);color:#fff;padding:40px 0 52px;position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;top:-40%;right:-10%;width:520px;height:520px;
 background:radial-gradient(circle,rgba(249,115,22,.18),transparent 62%);pointer-events:none}
.eyebrow{font-family:'Plus Jakarta Sans';font-size:11px;font-weight:700;letter-spacing:.22em;
 text-transform:uppercase;color:var(--orange)}
.hero h1{font-family:'Plus Jakarta Sans';font-weight:300;font-size:clamp(28px,4vw,44px);
 line-height:1.08;margin:12px 0 4px;letter-spacing:-.02em}
.hero h1 b{font-weight:700}
.cnpjline{font-size:13px;color:#8A91A6;margin-bottom:18px}
.mespills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.mespills button{font-family:'Plus Jakarta Sans';font-size:12px;font-weight:700;color:#B8BECF;
 background:rgba(255,255,255,.06);border:1px solid transparent;padding:6px 14px;border-radius:20px;cursor:pointer}
.mespills button.on{background:var(--orange);color:var(--navy);border-color:var(--orange)}
.regsw{display:flex;align-items:center;gap:7px;margin-bottom:8px}
.reglab{font-size:12px;color:#8A91A6}
.regsw button{font-family:'Plus Jakarta Sans';font-size:12px;font-weight:700;color:#B8BECF;
 background:rgba(255,255,255,.06);border:none;padding:6px 13px;border-radius:7px;cursor:pointer}
.regsw button.on{background:#fff;color:var(--navy)}
.waterfall{margin-top:26px;background:var(--navy2);border:1px solid var(--line);border-radius:16px;
 padding:22px 26px 14px}
.wf-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;gap:14px;flex-wrap:wrap}
.wf-head .t{font-family:'Plus Jakarta Sans';font-weight:700;font-size:15px}
.wf-head .h{font-size:12.5px;color:#8A91A6}
.wf-x{display:grid;grid-template-columns:repeat(5,1fr);margin-top:6px}
.wf-x span{font-size:11px;color:#8A91A6;text-align:center}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:-30px 0 0;position:relative;z-index:5}
@media(max-width:980px){.kpis{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.kpis{grid-template-columns:1fr}}
.kpi{background:var(--card);border:1px solid var(--g200);border-radius:14px;padding:16px 17px 14px;
 box-shadow:var(--shadow)}
.kpi .t{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:var(--g500)}
.kpi .v{font-family:'Plus Jakarta Sans';font-size:25px;font-weight:800;letter-spacing:-.025em;margin:7px 0 3px}
.kpi .d{font-size:12px;color:var(--ink2)}
.kpi .ref{font-size:11px;color:var(--orange);margin-top:5px;font-weight:600}
section{padding:52px 0}
.sec-alt{background:#fff;border-top:1px solid var(--g200);border-bottom:1px solid var(--g200)}
.sec-head{margin-bottom:24px}
.sec-head .k{font-family:'Plus Jakarta Sans';font-size:11px;font-weight:700;letter-spacing:.2em;
 text-transform:uppercase;color:var(--orange);margin-bottom:7px}
.sec-head h2{font-family:'Plus Jakarta Sans';font-weight:700;font-size:25px;letter-spacing:-.02em}
.sec-head .lede{color:var(--ink2);font-size:14.5px;max-width:800px;margin-top:7px}
.rsm-wrap{overflow-x:auto}
table.rsm,table.xtbl{width:100%;border-collapse:collapse;font-size:13px;background:#fff;
 border-radius:12px;overflow:hidden;box-shadow:var(--shadow)}
.rsm th,.xtbl th{background:var(--navy);color:#fff;font-family:'Plus Jakarta Sans';font-size:11px;
 font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:10px 13px;text-align:right;white-space:nowrap}
.rsm th.l,.xtbl th.l{text-align:left}
.rsm td,.xtbl td{padding:8px 13px;border-bottom:1px solid var(--g200);text-align:right;white-space:nowrap}
.rsm td.l,.xtbl td.l{text-align:left}
.rsm tr:nth-child(even) td,.xtbl tr:nth-child(even) td{background:#FBFBF9}
tr.res td{font-weight:800;background:var(--orange-soft)!important;border-top:1px solid #FDBA74}
tr.g td{font-weight:700}
td.av{color:var(--g500);font-size:12px}
.rsm-nota,.repnote{font-size:12.5px;color:var(--g500);margin-top:12px;max-width:880px}
.pz-grid{display:grid;grid-template-columns:320px 1fr;gap:34px;align-items:center}
@media(max-width:820px){.pz-grid{grid-template-columns:1fr}}
.pz-chart{position:relative}
.pz-mid{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;pointer-events:none}
.pz-mid .pz-t{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:var(--g500)}
.pz-mid b{font-family:'Plus Jakarta Sans';font-size:21px;font-weight:800}
.pz-leg{display:flex;flex-direction:column;gap:9px}
.pz-item{display:grid;grid-template-columns:12px 1fr auto auto;gap:11px;align-items:center;font-size:13.5px}
.pz-item i{width:12px;height:12px;border-radius:3px;display:block}
.pz-item .p{color:var(--g500);font-size:12.5px;width:52px;text-align:right}
.bridge{background:var(--navy);color:#fff;border-radius:18px;padding:30px 34px}
.bridge .bk{font-family:'Plus Jakarta Sans';font-size:11px;font-weight:700;letter-spacing:.2em;
 text-transform:uppercase;color:var(--orange)}
.bridge h3{font-family:'Plus Jakarta Sans';font-weight:300;font-size:clamp(21px,2.6vw,29px);
 margin:11px 0 8px;letter-spacing:-.02em}
.bridge h3 b{font-weight:700}
.bridge .bsub{color:#AEB4C6;font-size:14.5px;max-width:840px}
.bflow{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:13px;margin-top:22px}
.bflow .bx{background:var(--navy2);border:1px solid var(--line);border-radius:12px;padding:15px 16px}
.bflow .bx .t{font-size:11px;text-transform:uppercase;letter-spacing:.09em;color:#8A91A6}
.bflow .bx .v{font-family:'Plus Jakarta Sans';font-size:20px;font-weight:800;margin:6px 0 3px}
.bflow .bx .d{font-size:12px;color:#AEB4C6}
.rep-switch{display:flex;gap:4px;background:var(--g200);padding:4px;border-radius:10px;
 width:fit-content;margin-bottom:20px}
.rep-switch button{font-family:'Plus Jakarta Sans';font-size:12.5px;font-weight:700;color:var(--g500);
 background:none;border:none;padding:8px 16px;border-radius:7px;cursor:pointer}
.rep-switch button.on{background:#fff;color:var(--navy);box-shadow:var(--shadow)}
.repwrap{display:none}.repwrap.on{display:block}
.mixrow{display:grid;grid-template-columns:150px 1fr 190px;gap:14px;align-items:center;margin-bottom:9px}
.mixlab{font-family:'Plus Jakarta Sans';font-weight:700;font-size:13.5px}
.mixbar{height:20px;border-radius:6px;background:var(--g200);overflow:hidden}
.mixbar i{display:block;height:100%;border-radius:6px}
.mixval{font-size:13px;text-align:right;color:var(--ink2)}
@media(max-width:720px){.mixrow{grid-template-columns:1fr;gap:4px}.mixval{text-align:left}}
.vazio{background:#fff;border:1px dashed var(--g300);border-radius:14px;padding:28px 30px;text-align:center}
.vazio h4{font-family:'Plus Jakarta Sans';font-size:15px;font-weight:700;margin-bottom:6px}
.vazio p{font-size:13.5px;color:var(--ink2);max-width:660px;margin:0 auto}
.aviso{background:#fff;border:1px solid var(--g200);border-left:3px solid var(--orange);border-radius:12px;
 padding:16px 19px;margin-bottom:12px;box-shadow:var(--shadow)}
.aviso h4{font-family:'Plus Jakarta Sans';font-size:14px;font-weight:700;margin-bottom:4px}
.aviso p{font-size:13.5px;color:var(--ink2)}
.tag{display:inline-block;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.09em;
 padding:3px 9px;border-radius:20px;background:var(--orange-soft);color:#B45309;margin-left:9px;vertical-align:middle}
.foot{background:var(--navy);color:#8A91A6;padding:40px 0 34px;font-size:12.5px}
.foot .fg{display:flex;justify-content:space-between;gap:26px;flex-wrap:wrap;
 padding-bottom:20px;border-bottom:1px solid var(--line)}
.foot .sig{font-family:'Fraunces',serif;font-style:italic;font-size:19px;color:#fff}
.curva{display:flex;align-items:flex-end;gap:5px;margin:16px 0 8px;overflow-x:auto;padding-bottom:4px}
.cb{flex:1 0 46px;text-align:center}
.cbv{font-size:10px;color:var(--g500);margin-bottom:4px;white-space:nowrap}
.cbb{background:var(--in);border-radius:3px 3px 0 0;margin:0 auto;width:72%}
.cb.n .cbb{background:var(--out)}
.cb.n .cbv{color:var(--out);font-weight:700}
.cbl{font-size:10px;color:var(--g500);margin-top:5px;white-space:nowrap}
.xtbl td.pos{color:var(--in)}
.xtbl td.neg{color:var(--out)}
.xtbl.dfc{margin-bottom:10px}
.xtbl tr.dfct td{background:var(--navy);color:#fff;font-size:11px;font-weight:700;
 letter-spacing:.09em;text-transform:uppercase;padding:9px 12px}
.xtbl tr.dfcs td{background:var(--orange-soft);font-weight:700;border-top:1.5px solid var(--orange)}
.xtbl tr.dfcp td{font-size:11.5px;color:var(--g500);font-style:italic}
.subt{margin:26px 0 10px;font-size:13px;font-weight:700;color:var(--ink2);
 letter-spacing:.04em;text-transform:uppercase}
.selo{margin-top:7px;font-size:11.5px;color:rgba(255,255,255,.5);letter-spacing:.01em}
.selo b{color:rgba(255,255,255,.8);font-weight:600}
.aviso.erro{border-color:var(--out);background:#FFF5F5}
.aviso.erro h4{color:var(--out)}
.emc{display:inline-block;font-size:15px;font-weight:600;color:var(--orange);
 background:var(--orange-soft);border-radius:6px;padding:3px 9px;letter-spacing:-.01em}
.emcm{display:block;margin-top:7px;font-size:11.5px;color:var(--g500);line-height:1.5;font-weight:400}
.xtbl tr.abre{cursor:pointer}
.xtbl td.n2{padding-left:30px;color:var(--ink2)}
.xtbl td.n3{padding-left:54px;color:var(--g500);font-size:12px}
.xtbl tr.i td{font-size:12px;color:var(--g500);background:#FCFCFB}
.xtbl tr.c td{font-weight:500}
.xtbl td.tt{font-weight:700}
.xtbl .z{color:var(--g300)}
.xtbl tr.abre:hover td{background:var(--orange-soft)}
.caret{display:inline-block;width:15px;color:var(--orange);font-size:11px}
.foot .disc{margin-top:18px;font-size:11.5px;line-height:1.7;color:#6D748A}
@media(max-width:720px){.wrap{padding:0 18px}.kpis{margin-top:18px}}
"""

JS = r"""
var ENT=(typeof ENT0!=='undefined'?ENT0:'boldro'), MES=D.meses[D.meses.length-1], REG='caixa';
var SOCIOS=(typeof SOCIOS!=='undefined')&&SOCIOS;
function brl(v,c){c=c||0;var s=Math.abs(v).toLocaleString('pt-BR',{minimumFractionDigits:c,maximumFractionDigits:c});
 return (v<0?'−':'')+'R$ '+s}
function pc(v,b){return b?(100*v/b).toFixed(1).replace('.',',')+'%':'—'}

function elim(k){return /YO Noronha|Yo - Boldr|corrente Boldr/i.test(k)}
/* entidade virtual: consolidado soma as duas e elimina a conta corrente entre elas,
   mas só no resultado — no caixa o dinheiro passou pelos dois bancos */
function bloco(ent,reg,mes){
 if(ent==='consol'){
  var o={grupos:{},contas:{},lanc:{},familias:{},itens:[]};
  ['boldro','yo'].forEach(function(e){
   var b=((D.ents[e]||{})[reg]||{})[mes]; if(!b)return;
   Object.keys(b.familias||{}).forEach(function(f){o.familias[f]=(o.familias[f]||0)+b.familias[f]});
   /* a eliminacao intercompany vale para o RESULTADO, nao para o caixa: no extrato
      o dinheiro saiu de um banco e entrou no outro de verdade. Eliminar no DFC fazia
      a geracao de caixa final deixar de bater com a variacao do saldo. */
   (b.itens||[]).forEach(function(i){if(reg!=='comp'||!elim(i[0]))o.itens.push(i)});
   Object.keys(b.grupos).forEach(function(g){o.grupos[g]=(o.grupos[g]||0)+b.grupos[g]});
   Object.keys(b.contas).forEach(function(k){
    if(reg==='comp'&&elim(k))return;              /* eliminação intercompany: só no resultado */
    o.contas[k]=(o.contas[k]||0)+b.contas[k];
    o.lanc[k]=(o.lanc[k]||0)+(b.lanc[k]||0);
   });
  });
  /* o grupo CC perde a parte YO<->Boldró, sobra o que é com a Topázio */
  var cc=0; Object.keys(o.contas).forEach(function(k){if(k.indexOf('CC|')===0)cc+=o.contas[k]});
  o.grupos['CC']=cc;
  return o;
 }
 return ((D.ents[ent]||{})[reg]||{})[mes]||{grupos:{},contas:{},lanc:{},familias:{},itens:[]};
}
function E(){return ENT==='consol'?{nome:'Consolidado Yó + Boldró',cnpj:'45.270.781/0002-53 e 55.526.039/0001-39',
 status:'ok',conta:'soma das duas bases, sem a conta corrente entre elas'}:D.ents[ENT]}
function soma(ent,reg,mes,ks){var b=bloco(ent,reg,mes),t=0;ks.forEach(function(k){t+=b.grupos[k]||0});return t}
function saldos(ent,mes){
 if(ent!=='consol')return ((D.ents[ent]||{}).saldos||{})[mes];
 var o=null;['boldro','yo'].forEach(function(e){var s=((D.ents[e]||{}).saldos||{})[mes];if(!s)return;
  o=o||{ini:0,fim:0,entradas:0,saidas:0};
  o.ini+=s.ini;o.fim+=s.fim;o.entradas+=s.entradas;o.saidas+=s.saidas});
 return o;
}
function temDado(ent){return ent==='consol'||(D.ents[ent]||{}).status==='ok'}
function fase(ent){return ent==='consol'?'operando':((D.ents[ent]||{}).fase||'operando')}
function soGrupo(ent,reg,mes,gs){var b=bloco(ent,reg,mes),o={};
 Object.keys(b.contas).forEach(function(k){var g=k.split('|')[0];
  if(gs.indexOf(g)>=0)o[k.split('|')[1]]=(o[k.split('|')[1]]||0)+b.contas[k]});return o}

function setEntity(e){ENT=e;document.querySelectorAll('.entsw button').forEach(function(b){
 b.classList.toggle('on',b.dataset.ent===e)});render()}
function setMes(m){MES=m;document.querySelectorAll('.mespills button').forEach(function(b){
 b.classList.toggle('on',b.dataset.m===m)});render()}
function setRegime(r){REG=r;document.querySelectorAll('.regsw button,.rep-switch button').forEach(function(b){
 b.classList.toggle('on',b.dataset.r===r)});render()}

function ponteSVG(){
 var s=saldos(ENT,MES);
 if(!s)return '<text x="540" y="120" text-anchor="middle" fill="#6D748A" font-size="14" font-family="Inter">sem movimento lançado neste mês</text>';
 var passos=[['Saldo inicial',s.ini,'n'],['Entradas',s.entradas,'in'],['Saídas',s.saidas,'out'],
             ['Resultado',s.entradas+s.saidas,'r'],['Saldo final',s.fim,'n']];
 var mx=Math.max.apply(null,passos.map(function(p){return Math.abs(p[1])}))||1;
 var W=1080,H=236,cw=W/5,bw=92,base=H-38,esc=base-30,out='',acum=s.ini;
 passos.forEach(function(p,i){
  var cx=i*cw+cw/2,cor,y,alt;
  if(p[2]==='in'){cor='#34D399';alt=Math.abs(p[1])/mx*esc;y=base-((acum+p[1])/mx*esc);acum+=p[1]}
  else if(p[2]==='out'){cor='#F87171';alt=Math.abs(p[1])/mx*esc;y=base-(acum/mx*esc);acum+=p[1]}
  else{cor=p[2]==='r'?'#F97316':'#9CA3AF';alt=Math.abs(p[1])/mx*esc;y=base-alt}
  if(y<18)y=18;
  out+='<rect x="'+(cx-bw/2)+'" y="'+y.toFixed(1)+'" width="'+bw+'" height="'+Math.max(3,alt).toFixed(1)+
       '" rx="5" fill="'+cor+'" opacity=".92"/>'+
       '<text x="'+cx+'" y="'+(y-9).toFixed(1)+'" text-anchor="middle" fill="#fff" font-size="13" '+
       'font-weight="700" font-family="Plus Jakarta Sans">'+brl(p[1])+'</text>';
 });
 return out;
}

function cozinha(mes){
 var b=bloco(ENT,'comp',mes), f=b.familias||{};
 var venda=soma(ENT,'comp',mes,['1','2']);
 return {venda:venda, cmv:-soma(ENT,'comp',mes,['4']), food:-(f.cozinha||0), bar:-(f.bar||0),
         comum:-(f.comum||0), pessoal:-soma(ENT,'comp',mes,['6']),
         operacao:-soma(ENT,'comp',mes,['5']), ocupacao:-soma(ENT,'comp',mes,['7']),
         adm:-soma(ENT,'comp',mes,['8']), mkt:-soma(ENT,'comp',mes,['9']),
         variaveis:-soma(ENT,'comp',mes,['3']), deducoes:-soma(ENT,'comp',mes,['2'])};
}
function acumCozinha(){
 var t={venda:0,cmv:0,food:0,bar:0,comum:0,pessoal:0,operacao:0,ocupacao:0,adm:0,mkt:0,
        variaveis:0,deducoes:0};
 D.meses.forEach(function(m){var k=cozinha(m);
  Object.keys(t).forEach(function(x){t[x]+=k[x]})});
 return t;
}
function card(k){return '<div class="kpi"><div class="t">'+k[0]+'</div><div class="v num">'+k[1]+
 '</div><div class="d">'+k[2]+'</div>'+(k[3]?'<div class="ref">'+k[3]+'</div>':'')+'</div>'}
/* KPIs que vem do relatorio de vendas do 3LM. So existem para quem fatura:
   a venda esta no CNPJ da Boldro, entao na visao YO eles nao aparecem. */
function vd(){var V=D.vendas; if(!V||ENT==='yo')return null;
 return (MES===V.mes)?V:null}
function tkCard(){var V=vd();
 if(!V)return ['Ticket médio por conta',emC(ENT==='yo'?'a YO não fatura: a venda está no CNPJ da Boldró':'só há relatório de vendas de set/26'),'',''];
 return ['Ticket médio por conta',brl(V.ticket),V.contas.toLocaleString('pt-BR')+' contas no mês',
         'fonte: relatório do 3LM · por comanda, não por mesa']}
function turnoCard(){var V=vd();
 if(!V)return ['Share por turno',emC(ENT==='yo'?'a YO não fatura':'só há relatório de vendas de set/26'),'',''];
 var t=V.turno;
 return ['Consumo no almoço',(100*t.dia.pct).toFixed(1).replace('.',',')+'%',
         brl(t.dia.valor)+' das 11h às 16h',
         'fim de dia: '+(100*t.final.pct).toFixed(1).replace('.',',')+'% · '+brl(t.final.valor)]}
function diaForteCard(){var V=vd();
 if(!V)return ['Venda por dia da semana',emC(ENT==='yo'?'a YO não fatura':'só há relatório de vendas de set/26'),'',''];
 var s={},c={};
 V.dias.forEach(function(d){s[d.sem]=(s[d.sem]||0)+d.valor;c[d.sem]=(c[d.sem]||0)+d.contas});
 var ks=Object.keys(s).sort(function(a,b){return s[b]-s[a]}), tot=0;
 ks.forEach(function(k){tot+=s[k]});
 var NOME={segunda:'segunda',terca:'terça',quarta:'quarta',quinta:'quinta',sexta:'sexta',sabado:'sábado',domingo:'domingo'};
 return ['Dia mais forte',NOME[ks[0]],brl(s[ks[0]])+' · '+pc(s[ks[0]],tot)+' do mês',
         'o mais fraco é '+NOME[ks[ks.length-1]]+' ('+pc(s[ks[ks.length-1]],tot)+')']}

/* bloco de vendas: dia da semana e curva ABC */
function vendasBloco(){
 var el=document.getElementById('vendas'); if(!el)return;
 var V=vd();
 if(!V){
  var temMes=D.vendas&&MES!==D.vendas.mes;
  el.innerHTML='<div class="vazio"><h4>'+
   (ENT==='yo'?'A YO não fatura':(temMes?'Sem relatório de vendas de '+D.meses_nome[MES]:'Sem relatório de vendas'))+'</h4>'+
   '<p>'+(ENT==='yo'?'A venda de salão acontece no CNPJ da Boldró. Troque de empresa no topo.'
    :'O 3LM não tem API: estes números vêm do relatório mensal em PDF, e hoje só existe o de '+
      (D.vendas?D.meses_nome[D.vendas.mes]:'setembro')+'.')+'</p></div>';
  return;
 }
 var s={},c={},NOME={segunda:'segunda',terca:'terça',quarta:'quarta',quinta:'quinta',sexta:'sexta',sabado:'sábado',domingo:'domingo'};
 V.dias.forEach(function(d){s[d.sem]=(s[d.sem]||0)+d.valor;c[d.sem]=(c[d.sem]||0)+d.contas});
 var ordem=['segunda','terca','quarta','quinta','sexta','sabado','domingo'];
 var mx=Math.max.apply(null,ordem.map(function(k){return s[k]||0}))||1, tot=0;
 ordem.forEach(function(k){tot+=s[k]||0});
 var h='<h4 class="subt">Venda por dia da semana · '+D.meses_nome[V.mes]+'</h4><div class="curva">';
 ordem.forEach(function(k){
  var v=s[k]||0;
  h+='<div class="cb"><div class="cbv">'+pc(v,tot)+'</div><div class="cbb" style="height:'+
     Math.max(4,Math.round(68*v/mx))+'px"></div><div class="cbl">'+NOME[k].slice(0,3)+'</div>'+
     '<div class="cbl" style="color:var(--g300)">'+brl(v/1000,0)+'k</div></div>';
 });
 h+='</div>';
 h+='<h4 class="subt">Curva ABC por categoria</h4>'+
    '<table class="xtbl"><thead><tr><th class="l">Categoria</th><th>Receita</th><th>Itens</th>'+
    '<th>Classe A</th><th class="av">% em A</th><th>Classe B</th><th>Classe C</th></tr></thead><tbody>';
 var cats=Object.keys(V.abc).sort(function(a,b){return V.abc[b].receita-V.abc[a].receita});
 cats.forEach(function(k){var x=V.abc[k];
  h+='<tr><td class="l">'+k+'</td><td class="num">'+brl(x.receita)+'</td><td class="av">'+x.itens+'</td>'+
     '<td class="num">'+brl(x.A.valor)+' <span class="z">('+x.A.itens+')</span></td>'+
     '<td class="av">'+(100*x.A.pct).toFixed(1).replace('.',',')+'%</td>'+
     '<td class="num">'+brl(x.B.valor)+'</td><td class="num">'+brl(x.C.valor)+'</td></tr>';
 });
 var tr=0; cats.forEach(function(k){tr+=V.abc[k].receita});
 h+='<tr class="dfcs"><td class="l">Venda de produtos</td><td class="num">'+brl(tr)+'</td>'+
    '<td class="av"></td><td class="num"></td><td class="av"></td><td class="num"></td><td class="num"></td></tr>';
 h+='</tbody></table><p class="repnote">Fonte: relatório de vendas do 3LM/Gourmet. '+
    'A curva de cada categoria é calculada sobre a receita daquela categoria, não sobre o total. '+
    'Classe A vai até 80% do faturamento do grupo, B de 80% a 95%, C os 5% finais. '+
    'A venda de produtos exclui taxa de serviço e rolha, por isso é menor que o recebido no mês.</p>';
 el.innerHTML=h;
}

function emC(motivo){return '<span class="emc">em construção</span><span class="emcm">'+motivo+'</span>'}
function kpis(){
 if(!temDado(ENT)){
  var c=D.ents[ENT].conciliacao;
  return [['Situação','Sem carga','nenhum lançamento financeiro no Omie',''],
   ['Conciliação do CSC',c.linhas+' linhas',c.periodo,'ainda não lançada no sistema'],
   ['Saldo no início',brl(c.saldo_ini),'em 01/07/2026',''],
   ['Saldo no fim',brl(c.saldo_fim),'em 18/09/2026','consumo de '+brl(c.saldo_ini-c.saldo_fim)]].map(card).join('');
 }
 var s=saldos(ENT,MES)||{ini:0,fim:0,entradas:0,saidas:0};
 if(fase(ENT)==='pre_operacao'){
  var inv=soma(ENT,'comp',MES,['11']), apo=soma(ENT,'comp',MES,['12']),
      cus=soma(ENT,'comp',MES,['4','5','6','7','8','9']), rec=soma(ENT,'comp',MES,['1']);
  var qT=0,iT=0,aT=0;
  D.meses.forEach(function(m){qT+=soma(ENT,'comp',m,['4','5','6','7','8','9','11']);
   iT+=soma(ENT,'comp',m,['11']);aT+=soma(ENT,'comp',m,['12'])});
  var ccq=soma(ENT,'comp',MES,['CC']);
  return [
   ['Fase','Implantação','a casa ainda não fatura no CNPJ da YO',
    'a venda de salão está na Boldró'],
   ['Investimento no mês',brl(-inv),'obra, equipamento, frete de obra e pré-operação',
    'no período: '+brl(-iT)],
   ['Custo de estrutura no mês',brl(-cus),'insumo, equipe, arrendamento e administrativo',
    'corre mesmo sem venda'],
   ['Queima do mês',brl(-(inv+cus)),'investimento mais estrutura',
    'no período: '+brl(-qT)],
   ['Aporte no mês',brl(apo),'entrada de sócio','no período: '+brl(aT)],
   ['Receita no mês',brl(rec),'reembolso e outras receitas','não é venda de salão'],
   ['Dinheiro em caixa',brl(s.fim),'conta corrente mais aplicação',
    cus?('dá para '+(s.fim/-cus).toFixed(1).replace('.',',')+' mês de estrutura'):''],
   ['Share por turno',emC('a YO não fatura: a venda está no CNPJ da Boldró'),'','']
  ].map(card).join('');
 }
 var k=cozinha(MES), A=acumCozinha(), dias=(D.dias||{})[MES]||30;
 var ebitda=k.venda+soma(ENT,'comp',MES,['4','5','3','6','7','8','9']);
 var cc=soma(ENT,'comp',MES,['CC']);
 var fixo=k.pessoal+k.ocupacao+k.adm+k.mkt+k.operacao;
 return [
  ['Venda líquida',brl(k.venda),'o que a casa vendeu em '+D.meses_nome[MES],'líquido da maquininha'],
  ['Venda por dia',brl(k.venda/dias),dias+' dias de operação','é o número que o salão sente'],
  tkCard(),
  ['Ticket médio individual',emC('o 3LM não exporta nº de pessoas por conta'),'',''],
  ['Ticket médio por mesa',emC('o 3LM exporta comanda, não mesa física'),'',''],
  ['Margem EBITDA',pc(ebitda,k.venda),brl(ebitda)+' no mês','distorcida pelo recorte'],
  ['Dinheiro em caixa',brl(s.fim),'no banco ao fim do mês',
   fixo?('dá para '+(s.fim/fixo).toFixed(1).replace('.',',')+' mês de casa aberta'):''],
  turnoCard(), diaForteCard()
 ].map(card).join('');
}

var LINHAS=[['1','Receita bruta','g'],['2','Deduções',''],['=RL','Receita líquida','res'],
 ['4','CMV',''],['5','Custos de operação',''],['=LB','Lucro bruto','res'],
 ['3','Despesas variáveis de venda',''],['6','Pessoal operacional',''],['7','Ocupação',''],
 ['8','Administrativas',''],['9','Marketing e entretenimento',''],['=EB','EBITDA','res'],
 ['10','Resultado financeiro',''],['=LL','Lucro líquido','res'],
 ['11','Investimentos',''],['12','Financiamento','']];
function valorLinha(mes,cod){
 var f=function(ks){return soma(ENT,'comp',mes,ks)};
 if(cod==='=RL')return f(['1','2']);
 if(cod==='=LB')return f(['1','2','4','5']);
 if(cod==='=EB')return f(['1','2','4','5','3','6','7','8','9']);
 if(cod==='=LL')return f(['1','2','4','5','3','6','7','8','9','10']);
 return f([cod]);
}
function rsm(){
 if(!temDado(ENT))return '<tr><td class="l" colspan="9">Sem lançamento no Omie.</td></tr>';
 var th='<tr><th class="l">Linha</th>';
 D.meses.forEach(function(m){th+='<th>'+D.meses_nome[m]+'</th><th class="av">AV%</th>'});
 th+='<th>acumulado</th><th class="av">AV%</th></tr>';
 var rbt=D.meses.reduce(function(a,m){return a+soma(ENT,'comp',m,['1'])},0),body='';
 LINHAS.forEach(function(l){
  var tot=0,tds='';
  D.meses.forEach(function(m){
   var v=valorLinha(m,l[0]);tot+=v;
   tds+='<td class="num">'+brl(v)+'</td><td class="av">'+pc(v,soma(ENT,'comp',m,['1']))+'</td>';
  });
  body+='<tr class="'+l[2]+'"><td class="l">'+l[1]+'</td>'+tds+'<td class="num">'+brl(tot)+
        '</td><td class="av">'+pc(tot,rbt)+'</td></tr>';
 });
 return '<thead>'+th+'</thead><tbody>'+body+'</tbody>';
}

var CORES=['#F97316','#0D0F1A','#0E9F6E','#DC2626','#6366F1','#D97706','#0891B2','#7C3AED',
 '#BE185D','#4D7C0F','#9CA3AF','#334155'];
function pizza(){
 var b=bloco(ENT,REG,MES),itens=[];
 Object.keys(b.grupos).forEach(function(g){
  if(b.grupos[g]<0&&g!=='CC'&&g!=='NEUTRO')itens.push([D.grupo_nome[g]||g,-b.grupos[g]]);
 });
 itens.sort(function(a,c){return c[1]-a[1]});
 var tot=itens.reduce(function(a,i){return a+i[1]},0);
 if(!tot){document.getElementById('pzSvg').innerHTML='';
  document.getElementById('pzLeg').innerHTML='<p class="repnote">Sem saídas lançadas neste mês.</p>';
  document.getElementById('pzTot').textContent='—';return}
 var r=140,c=2*Math.PI*r,off=0,svg='',leg='';
 itens.forEach(function(it,i){
  var frac=it[1]/tot,cor=CORES[i%CORES.length];
  svg+='<circle cx="160" cy="160" r="'+r+'" fill="none" stroke="'+cor+'" stroke-width="38" stroke-dasharray="'+
       (frac*c)+' '+c+'" stroke-dashoffset="'+(-off*c)+'" transform="rotate(-90 160 160)"/>';
  off+=frac;
  leg+='<div class="pz-item"><i style="background:'+cor+'"></i><span>'+it[0]+'</span><span class="num">'+
       brl(it[1])+'</span><span class="p">'+pc(it[1],tot)+'</span></div>';
 });
 document.getElementById('pzSvg').innerHTML=svg;
 document.getElementById('pzLeg').innerHTML=leg;
 document.getElementById('pzTot').textContent=brl(tot);
}

function ponteTexto(){
 if(!temDado(ENT)){
  document.getElementById('brTitle').innerHTML='A YO ainda <b>não tem lançamento</b> no Omie';
  document.getElementById('brSub').textContent='Plano de contas aplicado e contas bancárias cadastradas, mas nenhum título lançado. Os números da conciliação do CSC servem de dimensão, não de resultado.';
  document.getElementById('bflow').innerHTML='';return;
 }
 var s=saldos(ENT,MES)||{ini:0,fim:0,entradas:0,saidas:0};
 var rl=soma(ENT,'comp',MES,['1','2']);
 var ebitda=rl+soma(ENT,'comp',MES,['4','5','3','6','7','8','9']);
 var cc=soma(ENT,'comp',MES,['CC']),inv=soma(ENT,'comp',MES,['11']);
 document.getElementById('brTitle').innerHTML='O caixa variou <b>'+brl(s.fim-s.ini)+
  '</b> e o resultado do mês foi <b>'+brl(ebitda)+'</b>';
 document.getElementById('brSub').textContent='A diferença de '+brl((s.fim-s.ini)-ebitda)+
  ' é o que não passa pela DRE: conta corrente com o grupo, investimento e o descasamento entre a emissão do título e o pagamento.';
 document.getElementById('bflow').innerHTML=[
  ['Saldo inicial',brl(s.ini),'início de '+D.meses_nome[MES]],
  ['Entradas',brl(s.entradas),'tudo que creditou'],
  ['Saídas',brl(Math.abs(s.saidas)),'tudo que debitou'],
  ['EBITDA do mês',brl(ebitda),'competência'],
  ['Investimento',brl(Math.abs(inv)),'fora do EBITDA'],
  ['Saldo final',brl(s.fim),'fim de '+D.meses_nome[MES]]
 ].map(function(b){return '<div class="bx"><div class="t">'+b[0]+'</div><div class="v num">'+b[1]+
  '</div><div class="d">'+b[2]+'</div></div>'}).join('');
}

var ABERTO={};                     /* o que o usuario abriu: grupo e conta */
function togNo(k){
 ABERTO[k]=!ABERTO[k];
 var dh=document.getElementById('dfchead');
 if(dh){var th='<th class="l">Fluxo de caixa</th>';
  D.meses.forEach(function(m){th+='<th>'+D.meses_nome[m]+'</th>'});
  dh.innerHTML=th+'<th>acumulado</th>';}
 var db=document.getElementById('dfcbody'); if(db)db.innerHTML=dfcEstruturado();
 orcado(); vendasBloco();
 ['fc','dre'].forEach(function(t){
  var h=document.getElementById(t+'head'); if(!h)return;
  var th='<th class="l">'+(t==='fc'?'Demonstrativo do caixa':'Categoria')+'</th>';
  D.meses.forEach(function(m){th+='<th>'+D.meses_nome[m]+'</th>'});
  h.innerHTML=th+'<th>acumulado</th><th class="av">AV %</th>';
 });
 var fc=document.getElementById('fcbody'); if(fc)fc.innerHTML=tabela('caixa');
 var dr=document.getElementById('drebody'); if(dr)dr.innerHTML=tabela('comp');
 var er=auditaTabela('caixa').concat(auditaTabela('comp'));
 var av=document.getElementById('auditoria');
 if(av)av.innerHTML=er.length
  ?'<div class="aviso erro"><h4>A tabela não fecha — não confie nestes números</h4><p>'+
    er.slice(0,8).join('<br>')+(er.length>8?'<br>… mais '+(er.length-8):'')+'</p></div>'
  :'';
 if(er.length&&window.console)console.error('auditoria da tabela:',er);
}
function tdMes(v){return '<td class="num">'+(v?brl(v):'<span class="z">—</span>')+'</td>'}

/* DFC no formato do grupo: tres blocos fechando em geracao de caixa operacional
   e geracao de caixa final. A linha e a soma dos grupos do plano gerencial. */
var DFC=[
 ['t','1. ATIVIDADES OPERACIONAIS',null],
 ['l','Recebimentos de clientes',['1']],
 ['l','Outros recebimentos (reembolso e rateio)',['OR']],
 ['l','(−) Estornos e devoluções a clientes',['2']],
 ['l','(−) Pagamentos de CMV (insumos e fretes)',['4']],
 ['l','(−) Pessoal',['6']],
 ['l','(−) Custos de operação',['5']],
 ['l','(−) Ocupação',['7']],
 ['l','(−) Artistas e entretenimento',['9']],
 ['l','(−) Administrativas e gerais',['8']],
 ['l','(−) Despesas variáveis de venda',['3']],
 ['l','(+/−) Resultado financeiro',['10']],
 ['s','(=) GERAÇÃO DE CAIXA OPERACIONAL',['1','OR','2','3','4','5','6','7','8','9','10']],
 ['t','2. IMPLANTAÇÃO E INVESTIMENTO',null],
 ['l','(−) Obra, equipamentos e pré-operação',['11']],
 ['s','(=) Caixa líquido de investimento',['11']],
 ['t','3. FINANCIAMENTO',null],
 ['l','(+) Aporte de sócios e empréstimos',['12']],
 ['s','(=) Caixa líquido de financiamento',['12']],
 ['t','4. MOVIMENTAÇÕES ENTRE CONTAS DO GRUPO',null],
 ['l','Transferência entre empresas do grupo',['CC']],
 ['l','Transferência entre contas próprias e ajustes',['NEUTRO','13']],
 ['s','(=) GERAÇÃO DE CAIXA FINAL',['1','OR','2','3','4','5','6','7','8','9','10','11','12','CC','NEUTRO','13']]
];
function dfcEstruturado(){
 if(!temDado(ENT))return '<tr><td class="l" colspan="'+(D.meses.length+2)+'">Sem lançamento no Omie.</td></tr>';
 var MS=D.meses, out='';
 var base=0; MS.forEach(function(m){base+=Math.abs(soma(ENT,'caixa',m,['1']))}); base=base||1;
 DFC.forEach(function(L){
  var tipo=L[0], rot=L[1], gs=L[2];
  if(tipo==='t'){
   out+='<tr class="dfct"><td class="l" colspan="'+(MS.length+2)+'">'+rot+'</td></tr>';
   return;
  }
  var v=MS.map(function(m){return soma(ENT,'caixa',m,gs)});
  var t=v.reduce(function(a,b){return a+b},0);
  if(tipo==='l'&&!t&&!v.some(function(x){return x}))return;          /* linha zerada some */
  out+='<tr class="'+(tipo==='s'?'dfcs':'')+'"><td class="l">'+rot+'</td>';
  v.forEach(function(x){out+=tdMes(x)});
  out+='<td class="num tt">'+brl(t)+'</td></tr>';
 });
 /* saldo: vem do extrato, nao da soma das linhas */
 var si=saldos(ENT,MS[0]), sf=saldos(ENT,MS[MS.length-1]);
 out+='<tr class="dfct"><td class="l" colspan="'+(MS.length+2)+'">SALDO DE CAIXA</td></tr>';
 out+='<tr><td class="l">Saldo inicial</td>';
 MS.forEach(function(m){var x=saldos(ENT,m);out+=tdMes(x?x.ini:0)});
 out+='<td class="num tt">'+brl(si?si.ini:0)+'</td></tr>';
 out+='<tr class="dfcs"><td class="l">SALDO FINAL</td>';
 MS.forEach(function(m){var x=saldos(ENT,m);out+=tdMes(x?x.fim:0)});
 out+='<td class="num tt">'+brl(sf?sf.fim:0)+'</td></tr>';
 /* prova: saldo final menos inicial tem que ser a geracao de caixa final */
 var ger=MS.reduce(function(a,m){return a+soma(ENT,'caixa',m,
   ['1','OR','2','3','4','5','6','7','8','9','10','11','12','CC','NEUTRO','13'])},0);
 var var_=(sf?sf.fim:0)-(si?si.ini:0), dif=ger-var_;
 out+='<tr class="dfcp"><td class="l">Prova: variação do saldo no extrato</td>';
 MS.forEach(function(){out+='<td></td>'});
 out+='<td class="num">'+brl(var_)+(Math.abs(dif)<0.02?' ✓':' <b>✗ '+brl(dif)+'</b>')+'</td></tr>';
 return out;
}

/* Audita a tabela nos tres niveis contra o dado. Roda a cada render e, se algo nao
   fechar, aparece em tela em vez de passar batido. Nasceu do bug de 14/10, em que
   o total de uma conta nao correspondia aos lancamentos abertos embaixo dela. */
function auditaTabela(reg){
 var erros=[], MS=D.meses;
 MS.forEach(function(m){
  var b=bloco(ENT,reg,m);
  /* 1. conta = soma dos seus lancamentos */
  var porConta={};
  (b.itens||[]).forEach(function(i){porConta[i[0]]=(porConta[i[0]]||0)+i[2]});
  Object.keys(b.contas).forEach(function(k){
   var s=porConta[k]||0;
   if(Math.abs(b.contas[k]-s)>0.011)
    erros.push(m+' · '+k+': conta '+b.contas[k].toFixed(2)+' x lançamentos '+s.toFixed(2));
  });
  /* 2. lancamento orfao: item sem conta correspondente */
  Object.keys(porConta).forEach(function(k){
   if(!(k in b.contas))erros.push(m+' · '+k+': lançamento sem conta');
  });
  /* 3. grupo = soma das contas do grupo */
  var porGrupo={};
  Object.keys(b.contas).forEach(function(k){var g=k.split('|')[0];porGrupo[g]=(porGrupo[g]||0)+b.contas[k]});
  Object.keys(b.grupos).forEach(function(g){
   if(Math.abs(b.grupos[g]-(porGrupo[g]||0))>0.011)
    erros.push(m+' · grupo '+g+': '+b.grupos[g].toFixed(2)+' x contas '+(porGrupo[g]||0).toFixed(2));
  });
 });
 return erros;
}

/* tres niveis: grupo -> conta -> lancamento. Uma coluna por mes, nunca somado. */
function tabela(reg){
 if(!temDado(ENT))return '<tr><td class="l" colspan="'+(D.meses.length+3)+'">Sem lançamento no Omie.</td></tr>';
 var MS=D.meses, blocos={}, base=0;
 MS.forEach(function(m){blocos[m]=bloco(ENT,reg,m); base+=Math.abs(blocos[m].grupos['1']||0)});
 base=base||1;
 var grupos={}, contas={};
 MS.forEach(function(m){
  Object.keys(blocos[m].contas).forEach(function(k){
   var g=k.split('|')[0];
   grupos[g]=grupos[g]||{}; contas[g]=contas[g]||{};
   grupos[g][m]=(blocos[m].grupos[g]||0);
   contas[g][k]=contas[g][k]||{};
   contas[g][k][m]=blocos[m].contas[k];
  });
 });
 function tot(o){var t=0;MS.forEach(function(m){t+=o[m]||0});return t}
 var out='';
 Object.keys(grupos).filter(function(g){return !(reg==='comp'&&(g==='CC'||g==='NEUTRO'))})
 .sort(function(a,c){return Math.abs(tot(grupos[c]))-Math.abs(tot(grupos[a]))})
 .forEach(function(g){
  var kg=reg+'|g|'+g, tg=tot(grupos[g]), ab=!!ABERTO[kg];
  out+='<tr class="g abre" onclick="togNo(\''+kg+'\')"><td class="l"><span class="caret">'+
       (ab?'▾':'▸')+'</span>'+(D.grupo_nome[g]||g)+'</td>';
  MS.forEach(function(m){out+=tdMes(grupos[g][m])});
  out+='<td class="num tt">'+brl(tg)+'</td><td class="av">'+pc(tg,base)+'</td></tr>';
  if(!ab)return;
  Object.keys(contas[g]).sort(function(a,c){return Math.abs(tot(contas[g][c]))-Math.abs(tot(contas[g][a]))})
  .forEach(function(k){
   var kc=reg+'|c|'+k, tc=tot(contas[g][k]), nome=k.split('|')[1], ac=!!ABERTO[kc];
   out+='<tr class="c abre" onclick="togNo(\''+kc.replace(/'/g,"\\'")+'\')"><td class="l n2">'+
        '<span class="caret">'+(ac?'▾':'▸')+'</span>'+nome+'</td>';
   MS.forEach(function(m){out+=tdMes(contas[g][k][m])});
   out+='<td class="num">'+brl(tc)+'</td><td class="av">'+pc(tc,base)+'</td></tr>';
   if(!ac)return;
   var itens=[];
   MS.forEach(function(m){
    ((blocos[m].itens)||[]).forEach(function(i){if(i[0]===k)itens.push({m:m,d:i[1],v:i[2],q:i[3]})});
   });
   itens.sort(function(a,b){return a.d.slice(6)+a.d.slice(3,5)+a.d.slice(0,2)>
                                   b.d.slice(6)+b.d.slice(3,5)+b.d.slice(0,2)?1:-1});
   if(!itens.length){
    out+='<tr class="i"><td class="l n3" colspan="'+(MS.length+3)+'">sem detalhe de lançamento</td></tr>';
   }
   itens.forEach(function(i){
    out+='<tr class="i"><td class="l n3">'+i.d+' · '+(i.q||'—')+'</td>';
    MS.forEach(function(m){out+=tdMes(m===i.m?i.v:0)});
    out+='<td class="num"></td><td class="av"></td></tr>';
   });
  });
 });
 return out;
}

function operacao(){
 var el=document.getElementById('op-kpis'); if(!el)return;
 if(!temDado(ENT)){el.innerHTML='<div class="vazio"><h4>A casa ainda não abriu no sistema</h4><p>A YO entra aqui quando a carga for feita.</p></div>';return}
 if(fase(ENT)==='pre_operacao'){
  var inv=soGrupo(ENT,'comp',MES,['11']), ac={};
  D.meses.forEach(function(m){var x=soGrupo(ENT,'comp',m,['11']);
   Object.keys(x).forEach(function(c){ac[c]=(ac[c]||0)+x[c]})});
  var tI=0;Object.keys(inv).forEach(function(c){tI+=inv[c]});
  var tA=0;Object.keys(ac).forEach(function(c){tA+=ac[c]});
  var fin=soma(ENT,'comp',MES,['12']), cmv=soma(ENT,'comp',MES,['4']),
      pes=soma(ENT,'comp',MES,['6']), ocu=soma(ENT,'comp',MES,['7']);
  el.innerHTML=[
   ['Investimento no mês',brl(-tI),'obra, equipamento, frete de obra e pré-operação',
    'no período todo: '+brl(-tA)],
   ['Aporte no mês',brl(fin),'entrada de sócio','é o que banca a obra'],
   ['Estoque e insumo já comprado',brl(-cmv),'comprado antes de abrir a casa',
    'está quase todo em uma conta genérica de insumos'],
   ['Equipe já contratada',brl(-pes),'folha, diarista, alimentação e passagem',
    'a casa paga equipe antes de faturar'],
   ['Arrendamento do ponto',brl(-ocu),'corre desde antes da abertura',''],
   ['Receita no mês',brl(soma(ENT,'comp',MES,['1'])),'não é venda de salão',
    'são reembolsos e outras receitas']
  ].map(card).join('');
  var mx0=document.getElementById('op-mix');
  if(mx0){var ks=Object.keys(ac).sort(function(a,b){return ac[a]-ac[b]}),cor=['#F97316','#0E9F6E','#6366F1','#EAB308'];
   mx0.innerHTML=ks.map(function(c,i){return '<div class="mixrow"><div class="mixlab">'+c+'</div>'+
    '<div class="mixbar"><i style="width:'+(100*ac[c]/tA).toFixed(1)+'%;background:'+cor[i%4]+'"></i></div>'+
    '<div class="mixval num">'+brl(-ac[c])+' · '+pc(ac[c],tA)+'</div></div>'}).join('')}
  return;
 }
 var k=cozinha(MES), A=acumCozinha(), dias=(D.dias||{})[MES]||30;
 var fixo=k.pessoal+k.ocupacao+k.adm+k.mkt+k.operacao;
 el.innerHTML=[
  ['Insumo de A&B',pc(k.cmv,k.venda),brl(k.cmv)+' de compra no mês',
   'a abertura por cozinha e bar entra quando o insumo deixar de vir num balde só'],
  ['Equipe',pc(k.pessoal,k.venda),brl(k.pessoal)+' entre fixos, diaristas e alojamento',
   'referência: 25% a 32%'],
  ['Custo de casa aberta',brl(fixo/dias),'por dia de operação',
   'sem vender nada, a casa custa isso por dia'],
  ['Ocupação',pc(k.ocupacao,k.venda),brl(k.ocupacao)+' de arrendamento','referência: até 10%'],
  ['Atrações e mídia',pc(k.mkt,k.venda),brl(k.mkt)+' em DJ, música e divulgação','referência: 3% a 6%'],
  ['Sobra depois de tudo',pc(k.venda-k.cmv-fixo,k.venda),
   brl(k.venda-k.cmv-fixo)+' antes do financeiro','']
 ].map(card).join('');

 /* mix cozinha x bar */
 var mx=document.getElementById('op-mix'); if(!mx)return;
 var tot=k.food+k.bar+k.comum;
 if(!tot){mx.innerHTML='';return}
 mx.innerHTML=[['Cozinha',k.food,'#F97316'],['Bar',k.bar,'#0E9F6E'],['Frete e diversos',k.comum,'#6366F1']]
  .map(function(i){return '<div class="mixrow"><div class="mixlab">'+i[0]+'</div>'+
   '<div class="mixbar"><i style="width:'+(100*i[1]/tot).toFixed(1)+'%;background:'+i[2]+'"></i></div>'+
   '<div class="mixval num">'+brl(i[1])+' · '+pc(i[1],tot)+'</div></div>'}).join('');
}

/* ponto de equilibrio: quanto a casa precisa vender para empatar */
function equilibrio(){
 var el=document.getElementById('eq-box'); if(!el)return;
 if(!temDado(ENT)){el.innerHTML='<div class="vazio"><h4>Sem venda lançada</h4><p>O ponto de equilíbrio aparece quando houver movimento.</p></div>';return}
 if(fase(ENT)==='pre_operacao'){
  var P0=D.premissas||{},q=0,ap=0;
  D.meses.forEach(function(m){q+=soma(ENT,'comp',m,['4','5','6','7','8','9','11']);
   ap+=soma(ENT,'comp',m,['12'])});
  var s0=saldos(ENT,D.meses[0]),s1=saldos(ENT,D.meses[D.meses.length-1]);
  el.innerHTML=[
   ['Queima no período',brl(q),'tudo que saiu sem a casa estar vendendo',
    'inclui obra, equipe, insumo e arrendamento'],
   ['Aporte no período',brl(ap),'entrada de sócio no mesmo intervalo',
    ap+q<0?('faltou '+brl(-(ap+q))+' de aporte para cobrir'):'cobriu a queima'],
   ['Caixa que restou',brl(s1?s1.fim:0),'conta corrente mais aplicação',
    s0?('começou o período com '+brl(s0.ini)):''],
   ['Ponto de equilíbrio do plano',brl(P0.ponto_equilibrio||0),
    'premissa do material de gestão orçamentária',
    'passa a valer quando a casa abrir e faturar no CNPJ da YO']
  ].map(card).join('');
  return;
 }
 var P=D.premissas||{}, k=cozinha(MES);
 var fixo=k.pessoal+k.ocupacao+k.adm+k.mkt+k.operacao;
 var cmvPct=k.venda?k.cmv/k.venda:0, varPct=k.venda?(k.variaveis+k.deducoes)/k.venda:0;
 var mc=1-cmvPct-varPct;                         /* margem de contribuição real */
 var be=mc>0?fixo/mc:0;
 var falta=be-k.venda;
 var fixoPlano=P.fixo_mes||0;
 el.innerHTML=[
  ['Precisa vender por mês',be?brl(be):'—','para empatar com a estrutura que existe HOJE',
   'margem de contribuição de '+(100*mc).toFixed(0)+'%'],
  ['Vendeu',brl(k.venda),'em '+D.meses_nome[MES],
   falta>0?('faltaram '+brl(falta)):('passou em '+brl(-falta))],
  ['Custo fixo de hoje',brl(fixo),'equipe, casa, administrativo e mídia',
   fixoPlano?('o plano previa '+brl(fixoPlano)+' por mês'):''],
  ['Equilíbrio com a casa cheia',brl(P.ponto_equilibrio||0),
   'premissa do plano de investimento',
   fixoPlano&&fixo?('a estrutura de hoje é '+(100*fixo/fixoPlano).toFixed(0)+'% da planejada'):'']
 ].map(card).join('');
}

/* orcado x realizado e a curva de caixa projetada */
function orcado(){
 var cx=document.getElementById('orc-box'), pj=document.getElementById('orc-proj');
 if(!cx)return;
 var O=D.orcamento;
 if(!O){cx.innerHTML='<div class="vazio"><h4>Orçamento não carregado</h4></div>';return}
 if(ENT!=='consol'){
  cx.innerHTML='<div class="vazio"><h4>O orçamento é consolidado</h4>'+
   '<p>A planilha do Tiago projeta YO e Boldró juntas, sem separar por CNPJ. '+
   'Troque para <b>Consolidado</b> no topo para ver o confronto.</p></div>';
  pj.innerHTML=''; return;
 }
 /* meses em que ha orcamento E realizado */
 var comuns=D.meses.filter(function(m){return O.linhas.saldo_fim&&(m in O.linhas.saldo_fim)});
 var L=[['Entradas de clientes','entradas',['1','OR']],
        ['Saídas operacionais','saidas_op',['2','3','4','5','6','7','8','9','10']],
        ['Geração de caixa operacional','ger_operacional',['1','OR','2','3','4','5','6','7','8','9','10']],
        ['Investimento','investimento',['11']],
        ['Geração de caixa final','ger_final',['1','OR','2','3','4','5','6','7','8','9','10','11','12','CC','NEUTRO','13']]];
 if(!comuns.length){
  cx.innerHTML='<div class="vazio"><h4>Ainda não há mês com orçamento e realizado juntos</h4>'+
   '<p>O orçamento começa em '+O.meses_nome[O.meses[0]]+' e o realizado vai até '+
   D.meses_nome[D.meses[D.meses.length-1]]+'.</p></div>';
 }else{
  var h='<table class="xtbl"><thead><tr><th class="l">Linha</th>';
  comuns.forEach(function(m){h+='<th>'+D.meses_nome[m]+' orçado</th><th>'+D.meses_nome[m]+' realizado</th><th>variação</th>'});
  h+='</tr></thead><tbody>';
  L.forEach(function(l){
   h+='<tr'+(l[1].indexOf('ger_')===0?' class="dfcs"':'')+'><td class="l">'+l[0]+'</td>';
   comuns.forEach(function(m){
    var o=(O.linhas[l[1]]||{})[m]||0, r=soma(ENT,'caixa',m,l[2]);
    var d=r-o, bom=(l[0].indexOf('Saídas')===0||l[0]==='Investimento')?(d>0):(d>=0);
    h+=tdMes(o)+tdMes(r)+'<td class="num '+(Math.abs(d)<1?'':(bom?'pos':'neg'))+'">'+brl(d)+'</td>';
   });
   h+='</tr>';
  });
  h+='</tbody></table>';
  cx.innerHTML=h;
 }
 /* curva do saldo projetado */
 var sf=O.linhas.saldo_fim||{}, ms=O.meses.filter(function(m){return m in sf});
 var vs=ms.map(function(m){return sf[m]}), mx=Math.max.apply(null,vs.map(Math.abs))||1;
 var neg=ms.filter(function(m){return sf[m]<0});
 var g='<div class="curva">';
 ms.forEach(function(m){
  var v=sf[m], alt=Math.max(4,Math.round(62*Math.abs(v)/mx));
  g+='<div class="cb'+(v<0?' n':'')+'"><div class="cbv">'+brl(v/1000,0)+'k</div>'+
     '<div class="cbb" style="height:'+alt+'px"></div>'+
     '<div class="cbl">'+(O.meses_nome[m]||m)+'</div></div>';
 });
 g+='</div>';
 if(neg.length)g+='<div class="aviso erro"><h4>O caixa projetado fica negativo em '+neg.length+' meses</h4>'+
   '<p>'+neg.map(function(m){return O.meses_nome[m]+' ('+brl(sf[m])+')'}).join(' · ')+
   '. O pior é '+O.meses_nome[neg.reduce(function(a,b){return sf[a]<sf[b]?a:b})]+'.</p></div>';
 pj.innerHTML=g;
}

function socios(){
 var el=document.getElementById('soc-kpis'); if(!el)return;
 var pro=0,dist=0,adi=0;
 D.meses.forEach(function(m){
  var b=bloco(ENT,'comp',m);
  Object.keys(b.contas).forEach(function(k){
   var n=k.split('|')[1].toLowerCase();
   if(n.indexOf('pró-labore')>=0||n.indexOf('pro-labore')>=0)pro+=b.contas[k];
   if(n.indexOf('distribuição de lucros')>=0)dist+=b.contas[k];
   if(n.indexOf('adiantamento de resultado')>=0)adi+=b.contas[k];
  });
 });
 var rl=D.meses.reduce(function(a,m){return a+soma(ENT,'comp',m,['1','2'])},0);
 var eb=D.meses.reduce(function(a,m){return a+soma(ENT,'comp',m,['1','2','4','5','3','6','7','8','9'])},0);
 var s0=saldos(ENT,D.meses[0]),s1=saldos(ENT,D.meses[D.meses.length-1]);
 el.innerHTML=[
  ['Receita líquida do período',brl(rl),D.meses_nome[D.meses[0]]+' a '+D.meses_nome[D.meses[D.meses.length-1]],''],
  ['EBITDA do período',brl(eb),pc(eb,rl)+' sobre a receita','com o pró-labore já deduzido (D8)'],
  ['Pró-labore',brl(Math.abs(pro)),'acima do EBITDA, decisão D8',''],
  ['Distribuição de lucros',brl(Math.abs(dist)),'financiamento, fora do resultado',''],
  ['Adiantamento a sócio operador',brl(Math.abs(adi)),'compensa na distribuição',''],
  ['Caixa no fim',s1?brl(s1.fim):'—','conta corrente',s0?('abriu em '+brl(s0.ini)):''],
  ['Investimento',brl(Math.abs(D.meses.reduce(function(a,m){return a+soma(ENT,'comp',m,['11'])},0))),
   'fora do EBITDA','critério D7']
 ].map(card).join('');
}

function render(){
 var e=E();
 document.getElementById('heroTitle').innerHTML=temDado(ENT)
  ? (SOCIOS?'Visão dos <b>sócios</b>':(fase(ENT)==='pre_operacao'
     ?'Implantação em <b>'+D.meses_nome[MES]+'</b>':'A casa em <b>'+D.meses_nome[MES]+'</b>'))
  : '<b>'+e.nome+'</b> — aguardando carga';
 var sl=document.getElementById('selo'); if(sl)sl.textContent=D.gerado;
 document.getElementById('heroCnpj').textContent=e.nome+' · '+(e.cnpj?'CNPJ '+e.cnpj:'')+
  (e.conta?' · '+e.conta:'');
 document.getElementById('wf').innerHTML=ponteSVG();
 document.getElementById('wfTitle').textContent='Ponte do caixa · '+D.meses_nome[MES];
 document.getElementById('kpis').innerHTML=kpis();
 var t=document.getElementById('rsm'); if(t)t.innerHTML=rsm();
 pizza(); ponteTexto(); operacao(); equilibrio(); socios();
 var dh=document.getElementById('dfchead');
 if(dh){var th='<th class="l">Fluxo de caixa</th>';
  D.meses.forEach(function(m){th+='<th>'+D.meses_nome[m]+'</th>'});
  dh.innerHTML=th+'<th>acumulado</th>';}
 var db=document.getElementById('dfcbody'); if(db)db.innerHTML=dfcEstruturado();
 orcado(); vendasBloco();
 ['fc','dre'].forEach(function(t){
  var h=document.getElementById(t+'head'); if(!h)return;
  var th='<th class="l">'+(t==='fc'?'Demonstrativo do caixa':'Categoria')+'</th>';
  D.meses.forEach(function(m){th+='<th>'+D.meses_nome[m]+'</th>'});
  h.innerHTML=th+'<th>acumulado</th><th class="av">AV %</th>';
 });
 var fc=document.getElementById('fcbody'); if(fc)fc.innerHTML=tabela('caixa');
 var dr=document.getElementById('drebody'); if(dr)dr.innerHTML=tabela('comp');
 var er=auditaTabela('caixa').concat(auditaTabela('comp'));
 var av=document.getElementById('auditoria');
 if(av)av.innerHTML=er.length
  ?'<div class="aviso erro"><h4>A tabela não fecha — não confie nestes números</h4><p>'+
    er.slice(0,8).join('<br>')+(er.length>8?'<br>… mais '+(er.length-8):'')+'</p></div>'
  :'';
 if(er.length&&window.console)console.error('auditoria da tabela:',er);
 document.querySelectorAll('.repwrap').forEach(function(w){
  w.classList.toggle('on',(REG==='caixa')===(w.id==='rep-fc'))});
}
document.getElementById('mespills').innerHTML=D.meses.map(function(m){
 return '<button data-m="'+m+'" class="'+(m===MES?'on':'')+'" onclick="setMes(\''+m+'\')">'+
  D.meses_nome[m]+'</button>'}).join('');
window.addEventListener('scroll',function(){
 var y=scrollY+90,at='geral';
 document.querySelectorAll('section,header').forEach(function(s){if(s.offsetTop<=y)at=s.id});
 document.querySelectorAll('.nav-links a').forEach(function(a){
  a.classList.toggle('on',a.getAttribute('href')==='#'+at)});
});
render();
"""

NAV_LINKS = ('<a href="#geral" class="on">Visão geral</a><a href="#tend">Ano</a>'
             '<a href="#orcado">Orçado × Real</a><a href="#pizza">Saídas</a>'
             '<a href="#ponte">DRE × Caixa</a><a href="#operacao">Cozinha e bar</a>'
             '<a href="#equilibrio">Equilíbrio</a><a href="#relatorios">Relatórios</a>')
NAV_LINKS_SOC = ('<a href="#geral" class="on">Visão geral</a><a href="#socios">Sócios</a>'
                 '<a href="#pizza">Saídas</a><a href="#ponte">DRE × Caixa</a>'
                 '<a href="#operacao">Cozinha e bar</a>')

ENTSW = """<div class="entsw" id="entsw">
<button data-ent="boldro" class="on" onclick="setEntity('boldro')">Boldró</button>
<button data-ent="yo" onclick="setEntity('yo')">YO</button>
<button data-ent="consol" onclick="setEntity('consol')">Consolidado</button>
<a href="socios.html">Sócios</a>
</div>"""
ENTSW_SOC = """<div class="entsw" id="entsw">
<button data-ent="boldro" class="on" onclick="setEntity('boldro')">Boldró</button>
<button data-ent="yo" onclick="setEntity('yo')">YO</button>
<button data-ent="consol" onclick="setEntity('consol')">Consolidado</button>
<a href="index.html" class="on">Sócios</a>
</div>"""

SEC_ANO = """<section id="tend" class="sec-alt"><div class="wrap">
<div class="sec-head"><div class="k">O período de 2026</div><h2>A casa <span class="light">mês a mês</span></h2>
<p class="lede">Venda, custo de insumo, equipe e resultado, com o peso de cada linha sobre a venda do mês — a leitura vertical que se usa em operação de A&amp;B.</p></div>
<div class="rsm-wrap"><table class="rsm" id="rsm"></table></div>
<p class="rsm-nota">Análise vertical sobre a receita bruta do mês. <b>CMV</b> são os insumos de A&amp;B; <b>custos de operação</b> incluem energia, água, limpeza, manutenção e o alojamento da equipe, que por decisão de 22/09 é custo direto. Transferência entre empresas do grupo, transferência entre contas próprias e ajustes ficam fora do resultado.</p>
</div></section>

<section id="vendas-sec"><div class="wrap">
<div class="sec-head"><div class="k">Vendas</div><h2>O que o salão <span class="light">vendeu</span></h2>
<p class="lede">Dia da semana, turno e curva ABC — do relatório mensal do 3LM, que não tem API e entra por PDF.</p></div>
<div id="vendas"></div>
</div></section>

<section id="orcado"><div class="wrap">
<div class="sec-head"><div class="k">Orçamento 2026</div><h2>Orçado <span class="light">× realizado</span></h2>
<p class="lede">Confronto do orçamento com o que de fato aconteceu, linha a linha, no plano de contas.</p></div>
<div id="orc-box"></div>
<h4 class="subt">Projeção de caixa até o fim de 2027</h4>
<div id="orc-proj"></div>
<p class="repnote">Orçamento revisado enviado pelo Tiago. É <b>consolidado</b>: a planilha não separa YO de Boldró, então o confronto com o realizado só vale na visão Consolidado. O realizado vem do extrato das contas no Omie.</p>
</div></section>"""

SEC_SOCIOS = """<section id="socios" class="sec-alt"><div class="wrap">
<div class="sec-head"><div class="k">Para os sócios</div><h2>O que sobrou <span class="light">e o que foi retirado</span></h2>
<p class="lede">Resultado do período, o que já saiu como pró-labore e distribuição, e o que está preso em conta corrente com as outras empresas do grupo.</p></div>
<div class="kpis" id="soc-kpis" style="margin:0"></div>
</div></section>"""


def pagina(socios=False):
    return """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%sFluxo de Caixa &amp; DRE · Yó / Boldró · 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,400&display=swap" rel="stylesheet">
<style>%s</style></head><body>

<nav class="nav"><div class="wrap">
<div class="brand">Grupo <b>Yó / Boldró</b></div>
<div class="nav-links">%s</div>
%s
</div></nav>

<header class="hero" id="geral"><div class="wrap">
<div class="eyebrow">%s</div>
<h1 id="heroTitle"></h1>
<div class="cnpjline" id="heroCnpj"></div>
<div class="selo">dados lidos do Omie em <b id="selo"></b></div>
<div class="mespills" id="mespills"></div>
<div class="regsw" id="regsw"><span class="reglab">Ver por:</span>
<button data-r="caixa" class="on" onclick="setRegime('caixa')">Caixa</button>
<button data-r="comp" onclick="setRegime('comp')">Competência</button></div>
<div class="waterfall">
<div class="wf-head"><span class="t" id="wfTitle">Ponte do caixa</span>
<span class="h">Saldo inicial → entradas → saídas → resultado → saldo final</span></div>
<svg id="wf" viewBox="0 0 1080 236"></svg>
<div class="wf-x"><span>Saldo inicial</span><span>Entradas</span><span>Saídas</span><span>Resultado</span><span>Saldo final</span></div>
</div>
</div></header>
<div class="wrap"><div class="kpis" id="kpis"></div></div>

%s

<section id="pizza" class="sec-alt"><div class="wrap">
<div class="sec-head"><div class="k">Para onde foi</div><h2>Para onde foi <span class="light">o dinheiro do mês</span></h2>
<p class="lede">Tudo que saiu no mês, do insumo ao arrendamento, com o peso de cada bloco. É a conta que o gerente faz de cabeça antes de aprovar compra.</p></div>
<div class="pz-grid">
<div class="pz-chart"><svg id="pzSvg" viewBox="0 0 320 320"></svg>
<div class="pz-mid"><span class="pz-t">total</span><b id="pzTot"></b></div></div>
<div class="pz-leg" id="pzLeg"></div>
</div>
</div></section>

<section id="ponte"><div class="wrap">
<div class="bridge"><div class="bk">A leitura do mês</div>
<h3 id="brTitle"></h3><p class="bsub" id="brSub"></p>
<div class="bflow" id="bflow"></div></div>
</div></section>

<section id="operacao" class="sec-alt"><div class="wrap">
<div class="sec-head"><div class="k">Cozinha, bar e salão</div>
<h2>Onde vai <span class="light">cada real vendido</span></h2>
<p class="lede">Casa de comida se mede por food cost, bar cost e prime cost — não por diária e ocupação. As referências ao lado de cada número são escala de mercado para operação de praia com alta sazonalidade; não são meta aprovada.</p></div>
<div class="kpis" id="op-kpis" style="margin:0"></div>
<div style="height:30px"></div>
<h3 style="font-family:'Plus Jakarta Sans';font-weight:700;font-size:17px;margin-bottom:14px">Mix de insumo <span class="light">— cozinha × bar</span></h3>
<div id="op-mix"></div>
<p class="repnote">Sem integração com o PDV não há ticket médio, número de couverts nem venda por canal — salão, bar, beach club e day use vivem no 3LM. O que dá para medir pelo financeiro é o <b>mix de compra</b>: quanto do insumo foi para a cozinha e quanto foi para o bar.</p>
</div></section>

<section id="equilibrio"><div class="wrap">
<div class="sec-head"><div class="k">Ponto de equilíbrio</div>
<h2>Quanto a casa precisa <span class="light">vender para empatar</span></h2>
<p class="lede">Calculado com a estrutura real do mês: custo fixo dividido pela margem de contribuição que sobra depois do CMV e das deduções. Ao lado, a premissa que o plano de investimento assumiu.</p></div>
<div class="kpis" id="eq-box" style="margin:0"></div>
<p class="repnote"><b>Os dois números não se contradizem — medem casas diferentes.</b> O da esquerda é o que a operação de hoje precisa vender para empatar, com a equipe e a estrutura que existem agora. O da direita é o equilíbrio da casa em regime pleno, como o plano de investimento projetou: CMV de 33%%, impostos e comissões de 17%% e custo fixo com folha de R$ 510.000 por mês. Conforme o quadro de pessoal e a operação completam, o número da esquerda sobe em direção ao da direita — e é essa convergência que vale acompanhar mês a mês.</p>
</div></section>
%s
<section id="relatorios"><div class="wrap">
<div class="sec-head"><div class="k">Relatório detalhado</div>
<h2>Tabelas por categoria <span class="light">— grupo e conta</span></h2>
<p class="lede">O mesmo número de duas maneiras: pelo caixa, como saiu do extrato; e por competência, como entra na DRE.</p></div>
<div class="rep-switch">
<button data-r="caixa" class="on" onclick="setRegime('caixa')">Fluxo de Caixa (DFC)</button>
<button data-r="comp" onclick="setRegime('comp')">DRE (competência)</button></div>
<div id="rep-fc" class="repwrap on">
<table class="xtbl dfc"><thead><tr id="dfchead"></tr></thead><tbody id="dfcbody"></tbody></table>
<p class="repnote">Demonstração do fluxo de caixa pelo método direto, a partir da movimentação das contas correntes no Omie. O saldo inicial e o final vêm do extrato, não da soma das linhas — a última linha prova que as duas coisas fecham.</p>
<h4 class="subt">Abertura por categoria e lançamento</h4>
<table class="xtbl"><thead><tr id="fchead"></tr></thead><tbody id="fcbody"></tbody></table>
<p class="repnote">Fonte: extrato das contas no Omie, conferido movimento a movimento contra o extrato do banco. Uma coluna por mês, sem somar. Clique no grupo para abrir as contas e na conta para abrir os lançamentos, com data e contraparte.</p></div>
<div id="rep-dre" class="repwrap"><table class="xtbl"><thead><tr id="drehead"></tr></thead><tbody id="drebody"></tbody></table>
<div id="auditoria"></div>
<p class="repnote">Competência pela data de emissão do título, mês a mês. Clique no grupo para abrir as contas e na conta para abrir os lançamentos. A conta corrente com partes relacionadas não entra no resultado.</p></div>

<div style="margin-top:34px">
<div class="aviso"><h4>A receita está pelo líquido da GetNet<span class="tag">ressalva</span></h4>
<p>O que entra no banco é o repasse líquido da adquirente. A receita bruta e a taxa de cartão ainda não existem na base, e o custo de antecipação também não — com o extrato de vendas detalhado da GetNet isso é reclassificado e a margem muda.</p></div>
<div class="aviso"><h4>Caixa e competência já não contam a mesma história</h4>
<p>O fluxo de caixa é o que passou pelo banco em agosto e setembro de 2026. A competência vai além: a folha de setembro da Boldró e as compras a prazo que vencem em outubro já estão lançadas como título em aberto e entram no resultado do mês em que foram geradas — são 54 títulos que não vieram da conciliação bancária. Por isso a margem por competência é menor, e mais honesta, que a do caixa.</p></div>
<div class="aviso"><h4>A YO está carregada, mas a casa fatura no CNPJ da Boldró<span class="tag">leitura</span></h4>
<p>A base da YO está carregada até 09/10 e o caixa fecha com o extrato do Bradesco. A venda de salão aparece inteira na Boldró: na YO o que existe é obra, pré-operação, estoque inicial, equipe e arrendamento. A receita de setembro da YO é de R$ 5.998 e é o PIX que a Boldró mandou em 15/09 — até 12/10 havia R$ 5.206 a mais ali, que eram transferências da conta Mercado Pago da própria YO lançadas como receita e já foram reclassificadas.</p></div>
<div class="aviso"><h4>Os dois caixas fecham no centavo com o extrato do banco<span class="tag">conciliado</span></h4>
<p>Boldró em 30/09: R$ 599.857,30 no Omie e R$ 599.857,30 no Santander. YO em 30/09: R$ 142.214,80 no Omie e R$ 142.214,80 no Bradesco. Os 1.048 movimentos de setembro da Boldró batem um a um por data e valor. Três coisas tiveram que ser arrumadas na base para chegar aqui: as pernas da varredura automática das duas aplicações, que o banco mostra todo dia e o Omie não tinha; as quatro tarifas de PIX de 24/09 da YO, que faltavam na conciliação do CSC; e o piso de R$ 1,00 da conta corrente da YO, que estava contado duas vezes na abertura.</p></div>
<div class="aviso"><h4>A conta corrente entre as duas não fecha<span class="tag">ressalva</span></h4>
<p>Em 20/08 a YO transferiu R$ 100 mil para a Boldró — conferido no extrato do Santander, PIX recebido do CNPJ da YO. Esse par tem as duas pernas e foi eliminado no consolidado. Mas a Boldró ainda registra R$ 107.162,82 que pagou por conta da YO e que a YO nunca lançou do lado dela. Enquanto esse espelho não for feito, esse custo não aparece no resultado de nenhuma das duas.</p></div>
<div class="aviso"><h4>O insumo da YO está num saco só</h4>
<p>R$ 336.706,60 de compra da YO em agosto e setembro estão na conta genérica de insumos, sem separar proteína, hortifrúti, secos ou bebida. É por isso que o mix de cozinha e bar da YO não é confiável e o da Boldró é.</p></div>
</div>
</div></section>

<footer class="foot"><div class="wrap"><div class="fg">
<div><div class="sig">João Victor Andrade de Souza</div><div class="r">Sócio-fundador · Exact BR</div></div>
<div style="text-align:right"><div class="r" style="margin-bottom:4px">Disciplina Gera Lucro</div>
<div style="font-family:'Plus Jakarta Sans';font-size:13px;font-weight:500;color:rgba(255,255,255,.85)">Exact BR · Recife — PE</div></div>
</div>
<p class="disc">Relatório gerencial · Grupo Yó / Boldró. Resultado apurado por competência, pela data de emissão dos documentos; fluxo de caixa apurado pela movimentação bancária, conferido contra o extrato bancário de cada empresa até 30 de setembro de 2026 — Santander 13002614-6 na Boldró e Bradesco mais aplicação na YO — com saldo igual ao da conciliação do CSC. A conta corrente entre as empresas do grupo é transferência, não custo, e fica fora do resultado; no consolidado, o par Yó↔Boldró é eliminado. A receita está lançada pelo valor líquido repassado pela adquirente enquanto o extrato de vendas detalhado da GetNet não é incorporado. Dados lidos da API do Omie em %s.</p>
</div></footer>

<script>const D=%s;var SOCIOS=%s;%s</script>
</body></html>""" % (
        'Sócios · ' if socios else '',
        CSS,
        NAV_LINKS_SOC if socios else NAV_LINKS,
        ENTSW_SOC if socios else ENTSW,
        'Visão dos sócios · 2026' if socios else 'Fluxo de Caixa &amp; DRE Gerencial · 2026',
        SEC_SOCIOS if socios else SEC_ANO,
        SEC_SOCIOS if not socios else '',
        D['gerado'],
        json.dumps(D, ensure_ascii=False),
        'true' if socios else 'false',
        JS)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    for nome, soc in (('index.html', False), ('socios.html', True)):
        p = os.path.join(d, nome)
        open(p, 'w').write(pagina(soc))
        print('gerado %s (%.0f KB)' % (nome, os.path.getsize(p) / 1024))
