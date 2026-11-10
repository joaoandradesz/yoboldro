# -*- coding: utf-8 -*-
"""Gera o painel gerencial Yó / Boldró no esqueleto do painel modelo.

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

# Meses que a base tem mas o painel nao mostra. Outubro saiu em 05/11/2026: a
# carga e a conciliacao do mes ainda nao fecharam e o mes parcial atrapalhava a
# leitura. Esvaziar esta lista traz o mes de volta, sem tocar nos dados.
# 06/11/2026: outubro volta ao painel. A conciliacao do mes fechou contra o
# banco nas duas empresas, mas o faturamento do 3LM de outubro nao esta
# carregado — entao o mes entra SO em caixa, pela lista sem_dre, que ja vem
# do dados_painel.json. Esta lista tira o mes INTEIRO; sem_dre tira so a DRE.
# 06/11/2026: outubro saiu DE NOVO. O mes em si esta conferido contra o banco,
# mas as tabelas mes a mes, as pilhas de mes e a cascata foram desenhadas para
# 06/11/2026: outubro de volta, agora de verdade. A quebra de layout da primeira
# tentativa era UM grid fixo — o eixo da ponte em repeat(5,1fr) contra 6 passos
# do regime de caixa — e nao as tabelas de serie, que se montam com mesesDe() e
# colspan calculado. Com o eixo dinamico, o mes entra sem tocar no resto.
# O mes nao tem DRE (sem relatorio de vendas), entao fica na lista sem_dre, que
# ja vem do dados_painel.json: aparece no caixa e nao no resultado.
FORA_DO_PAINEL = []

for _m in FORA_DO_PAINEL:
    for _k in ('meses', 'parciais', 'sem_dre'):
        if _m in (D.get(_k) or []):
            D[_k].remove(_m)
    D.get('meses_nome', {}).pop(_m, None)
    D.get('dias', {}).pop(_m, None)
    D.get('taxas', {}).pop(_m, None)
    D.get('receita', {}).pop(_m, None)
    for _e in D['ents'].values():
        for _k in ('comp', 'caixa', 'saldos'):
            (_e.get(_k) or {}).pop(_m, None)

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
.hero h1{font-family:'Plus Jakarta Sans';font-weight:300;font-size:clamp(30px,4.4vw,45px);
 line-height:1.08;margin:12px 0 4px;letter-spacing:-.02em}
.hero h1 b{font-weight:700}
.cnpjline{font-size:13px;color:#8A91A6;margin-bottom:18px}
.mespills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.mespills button{font-family:'Plus Jakarta Sans';font-size:12px;font-weight:700;color:#B8BECF;
 background:rgba(255,255,255,.06);border:1px solid transparent;padding:6px 14px;border-radius:20px;cursor:pointer}
.mespills button.on{background:var(--orange);color:var(--navy);border-color:var(--orange)}
.mespills button.parc i{font-style:normal;font-size:9.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;opacity:.75;margin-left:5px}
.mespills button.parc{border-style:dashed}
.regsw{display:flex;align-items:center;gap:7px;margin-bottom:8px}
.reglab{font-size:12px;color:#8A91A6}
.regnota{font-size:11.5px;color:#8A91A6;margin-left:12px;line-height:1.45;max-width:420px}
@media(max-width:820px){.regnota{display:block;margin:8px 0 0}}
.regsw button{font-family:'Plus Jakarta Sans';font-size:12px;font-weight:700;color:#B8BECF;
 background:rgba(255,255,255,.06);border:none;padding:6px 13px;border-radius:7px;cursor:pointer}
.regsw button.on{background:#fff;color:var(--navy)}
.waterfall{margin-top:26px;background:var(--navy2);border:1px solid var(--line);border-radius:16px;
 padding:22px 26px 14px}
/* O svg#wf tem viewBox e NENHUMA regra de tamanho: o navegador aplica o padrao
   de elemento substituido (300x150), o desenho e reduzido para caber e fica
   centralizado com sobra dos lados — na tela parece cortado. Com aspect-ratio
   do proprio viewBox ele ocupa a largura do bloco na proporcao certa. */
.waterfall svg{display:block;width:100%;height:auto}
.wf-x{display:none}
.wf-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;gap:14px;flex-wrap:wrap}
.wf-head .t{font-family:'Plus Jakarta Sans';font-weight:700;font-size:15px}
.wf-head .h{font-size:12.5px;color:#8A91A6}
.wf-x{display:grid;margin-top:6px}
.wf-x span{font-size:11px;color:#8A91A6;text-align:center}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:-30px 0 0;position:relative;z-index:5}
@media(max-width:980px){.kpis{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.kpis{grid-template-columns:1fr}}
.kpi{background:var(--card);border:1px solid var(--g200);border-radius:14px;padding:16px 17px 14px;
 box-shadow:var(--shadow)}
.kpi .t{font-family:'Plus Jakarta Sans',sans-serif;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:#6B7280}
.kpi .v{font-family:'Plus Jakarta Sans',sans-serif;font-size:22px;font-weight:700;letter-spacing:-.02em;margin:7px 0 3px}
.kpi .d{font-family:'Inter',sans-serif;font-size:11.5px;font-weight:400;color:#6B7280}
.kpi .ref{font-family:'Inter',sans-serif;font-size:11px;color:var(--orange);margin-top:5px;font-weight:500}
section{padding:52px 0}
.sec-alt{background:#fff;border-top:1px solid var(--g200);border-bottom:1px solid var(--g200)}
.sec-head{margin-bottom:24px}
.sec-head .k{font-family:'Plus Jakarta Sans';font-size:11px;font-weight:700;letter-spacing:.2em;
 text-transform:uppercase;color:var(--orange);margin-bottom:7px}
.sec-head h2{font-family:'Plus Jakarta Sans';font-weight:700;font-size:30.7px;letter-spacing:-.02em;line-height:1.12}
.sec-head .lede{font-family:'Fraunces',Georgia,serif;color:var(--ink2);font-size:16px;line-height:1.55;max-width:800px;margin-top:9px}
.rsm-wrap{overflow-x:auto}
table.rsm,table.xtbl{width:100%;border-collapse:collapse;font-size:13px;background:#fff;
 border-radius:12px;overflow:hidden;box-shadow:var(--shadow)}
.rsm th,.xtbl th{background:var(--navy);color:#fff;font-family:'Plus Jakarta Sans';font-size:11px;
 font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:10px 13px;text-align:right;white-space:nowrap}
.rsm th.l,.xtbl th.l{text-align:left}
.rsm td,.xtbl td{padding:8px 13px;border-bottom:1px solid var(--g200);text-align:right;white-space:nowrap}
.xtbl.mat td{border-bottom:1px solid #EFEFEC}
.rsm td.l,.xtbl td.l{text-align:left}
.rsm tr:nth-child(even) td,.xtbl:not(.mat) tr:nth-child(even) td{background:#FBFBF9}
.rsm tr.res td{font-weight:800;background:var(--orange-soft);border-top:1px solid #FDBA74}
tr.g td{font-weight:700}
td.av{color:var(--g500);font-size:12px}
.rsm-nota,.repnote{font-size:12px;color:var(--g500);margin-top:12px;max-width:880px}
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
.tx-h3{font-family:'Plus Jakarta Sans';font-weight:700;font-size:17px;margin:30px 0 6px}
.tx-sub{font-family:'Inter';font-size:12.5px;color:var(--ink2);line-height:1.55;
 max-width:860px;margin-bottom:13px}
.xtbl td.neg{color:#B42318}
.xtbl td.obs{font-family:'Inter';font-size:11.5px;color:var(--g500);white-space:normal;max-width:430px;line-height:1.45}
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
/* tipografia medida no painel modelo: rotulo em Inter, numero em Plus
   Jakarta Sans, e o peso acompanhando o nivel da linha. */
.xtbl.mat{font-family:'Inter',sans-serif;font-size:12px;font-weight:400;color:var(--ink)}
.xtbl.mat th{font-family:'Plus Jakarta Sans',sans-serif;background:#EEF0F4;color:#3B4252;
 font-weight:700;font-size:9.5px;letter-spacing:.285px;text-transform:uppercase;
 padding:9px 11px;text-align:right}
.xtbl.mat th.l{text-align:left}
.xtbl.mat td{padding:6px 11px;text-align:right;white-space:nowrap;
 border-bottom:1px solid #EFEFEC}
.xtbl.mat td.num{font-family:'Plus Jakarta Sans',sans-serif}
.xtbl.mat td.l{font-family:'Inter',sans-serif;text-align:left;white-space:normal}
.xtbl.mat i.avin{display:block;font-style:normal;font-size:8.4px;color:#9CA3AF;
 margin-top:1px;font-weight:inherit}
.xtbl.mat .chv{display:inline-block;width:15px;color:var(--orange);font-size:10px}
.xtbl.mat td.n1{padding-left:24px}
.xtbl.mat td.n2{padding-left:48px;font-size:11.5px}
.xtbl.mat td.n3{padding-left:68px;color:var(--g500);font-size:11px}

.xtbl.mat tr.xm td{background:#F1F3F6;color:#374151;cursor:pointer;font-weight:600}
.xtbl.mat tr.xm td.l{font-weight:400}
.xtbl.mat tr.lvl1 td{background:#F6F7F9;color:#374151;font-weight:600;cursor:pointer}
.xtbl.mat tr.lvl2 td{background:#fff;color:#374151;font-weight:500;cursor:pointer;font-size:11.5px}
.xtbl.mat tr.lvl2 td.l{color:#4B5563}
.xtbl.mat tr.lvl2 i.avin{font-size:8.05px}
.xtbl.mat tr.lvl3 td{background:#fff;font-weight:400}
.xtbl.mat tr.r0 td{background:#1F2937;color:#fff;font-weight:800;cursor:pointer}
.xtbl.mat tr.sub td{background:#fff;color:#374151;cursor:pointer;font-weight:400}
.xtbl.mat tr.sub td.n1{padding-left:26px}
.xtbl.mat tr.scc td{background:#fff;color:#374151;font-size:11.5px;font-weight:400}
.xtbl.mat tr.scc td.n2{padding-left:44px}
/* paletas medidas no painel de referencia: o DFC e a DRE nao usam a mesma */
.xtbl.mat tr.op td{background:#E7EAF0;color:#1F2937;font-weight:800;border-top:1px solid #D4D9E2}
.xtbl.mat.dre tr.ebit td{background:#D6E4F5;color:#102C4C;font-weight:800;border-top:1.5px solid #A9C6E8}
.xtbl.mat.dre tr.res td{background:#FBEFE2;color:#7A3E00;font-weight:800;border-top:1.5px solid #E8C9A6}
.xtbl.mat.dfc tr.ebit td{background:#FFF7ED;color:#7A3E00;font-weight:800;border-top:1.5px solid var(--orange)}
.xtbl.mat.dfc tr.res td{background:#0D0F1A;color:#fff;font-weight:800;border-top:1.5px solid #0D0F1A}
.xtbl.mat.dfc tr.res i.avin,.xtbl.mat tr.r0 i.avin{color:rgba(255,255,255,.55)}
.xtbl.mat tr.zero td{opacity:.42}
.cx-tbl tr.flagged td{background:#FFFBEA}
.cx-tbl .flag{display:inline-block;margin-left:6px;padding:1px 6px;border-radius:9px;
 background:#FDE68A;color:#6B4E00;font-size:10px;font-weight:700;letter-spacing:.2px;
 cursor:help;white-space:nowrap}
.cx-nota .flagtxt{color:#6B4E00}
.xtbl.mat tr.sep td{font-family:'Plus Jakarta Sans',sans-serif;background:#fff;color:#9AA1AE;
 font-size:10px;letter-spacing:.09em;text-transform:uppercase;font-weight:700;
 padding:14px 11px 6px;text-align:left;border-bottom:none}
.xtbl.mat tbody tr td.neg{color:#C0392B}
.xtbl.mat.dfc tbody tr.res td.neg,.xtbl.mat tbody tr.r0 td.neg{color:#FFB3A7}
.xtbl.mat tbody tr td.tt{background:#F5F7FA;font-weight:800;border-left:1px solid var(--g200)}
.xtbl.mat tbody tr td.avtot{font-family:'Plus Jakarta Sans',sans-serif;background:#F5F7FA;
 color:var(--g500);font-size:11px;font-weight:600}
.xtbl.mat tr.xm:hover td,.xtbl.mat tr.lvl1:hover td,.xtbl.mat tr.lvl2:hover td{background:var(--orange-soft)}
.xtbl.mat td.clic{cursor:pointer}
.xtbl.mat td.clic:hover{background:var(--orange-soft);box-shadow:inset 0 0 0 1px var(--orange)}
.cx-fundo{position:fixed;inset:0;background:rgba(13,15,26,.45);display:none;z-index:90;
 align-items:center;justify-content:center;padding:28px}
.cx-fundo.on{display:flex}
.cx{background:#fff;border-radius:14px;max-width:900px;width:100%;max-height:82vh;
 overflow:auto;box-shadow:0 24px 70px rgba(13,15,26,.3)}
.cx-cab{display:flex;align-items:center;gap:12px;padding:18px 22px;border-bottom:1px solid var(--g200);
 position:sticky;top:0;background:#fff}
.cx-cab h4{font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;flex:1}
.cx-x{background:none;border:none;font-size:22px;color:var(--g500);cursor:pointer;line-height:1}
.cx-sub{display:flex;justify-content:space-between;padding:12px 22px 0;
 font-family:'Plus Jakarta Sans',sans-serif;font-size:10.5px;font-weight:700;
 letter-spacing:.09em;color:var(--g500)}
.cx-sub b{color:var(--ink)}
.cx-nota{margin:12px 22px;padding:10px 13px;background:var(--orange-soft);border-radius:8px;
 font-size:12px;color:var(--ink2)}
.cx-vazio{padding:26px 22px;color:var(--g500);font-size:13px}
.cx-tbl{width:100%;border-collapse:collapse;font-size:12.5px}
.cx-tbl th{background:#F6F7F9;color:var(--g500);font-family:'Plus Jakarta Sans',sans-serif;
 font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
 padding:9px 22px;text-align:left}
.cx-tbl th.r,.cx-tbl td.r{text-align:right}
.cx-tbl td{padding:9px 22px;border-bottom:1px solid #F0F0ED}
.cx-tbl td.pos{color:var(--in);font-weight:600}
.cx-tbl tr.clA td{background:#F6FBF8}
.cx-tbl tr.clC td{color:var(--g500)}
.pil{display:inline-block;padding:1px 7px;border-radius:9px;font-size:10px;font-weight:700}
.pil.A{background:#D9F2E5;color:#0B6B46}
.pil.B{background:#FFF3D6;color:#8A5B00}
.pil.C{background:#EFEFEC;color:#6B7280}
.xtbl tr.abc-l{cursor:pointer}
.xtbl tr.abc-l:hover td{background:var(--orange-soft)}
.cx-tbl td.neg{color:var(--ink);font-weight:600}
.xtbl.soma .sin{display:inline-block;width:16px;color:var(--orange);font-weight:700}
.xtbl.soma tr.memo td{color:var(--g500);font-size:12.5px}
.rep-t{font-family:'Plus Jakarta Sans';font-weight:700;font-size:17px;margin:26px 0 12px}
.ress{margin-top:30px;border:1px solid var(--g200);border-radius:12px;background:#fff}
.ress summary{cursor:pointer;padding:15px 18px;font-size:13.5px;color:var(--ink2);
 list-style:none;display:flex;align-items:center;gap:8px}
.ress summary::-webkit-details-marker{display:none}
.ress summary b{color:var(--ink)}
.ress .chev{margin-left:auto;color:var(--orange);font-size:12px}
.ress[open] .chev{transform:rotate(180deg)}
.ress[open] summary{border-bottom:1px solid var(--g200)}
.ressin{padding:16px 18px 6px}
.ressin .aviso{margin-bottom:12px}
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
.xtbl td .pq{display:block;font-size:10.5px;font-weight:500;color:var(--g400);line-height:1.3}
.xtbl tr.dfcs td .pq{color:#A8632A;font-weight:700}
.xtbl tr.dfcp td{font-size:11.5px;color:var(--g500);font-style:italic}
.subt{font-family:'Plus Jakarta Sans',sans-serif;margin:30px 0 12px;font-size:14px;font-weight:600;color:var(--ink2);letter-spacing:.02em}
.selo{margin-top:7px;font-size:11.5px;color:rgba(255,255,255,.5);letter-spacing:.01em}
.selo b{color:rgba(255,255,255,.8);font-weight:600}
.aviso.nota{background:var(--orange-soft);border-color:#FDBA74;margin:14px 0 0}
.aviso.nota h4{color:#9A3412}
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

/* ---------- exportar PDF -------------------------------------------------
   Portado do painel modelo em 09/11/2026: foi o modelo que o Tiago
   mandou como padrao ("quero objetividade"), e aquele PDF e exatamente a
   exportacao desta funcao. O documento e montado a parte (.pdoc), em paginas
   A4 deitadas de altura fixa, clonando o que JA esta renderizado na tela —
   entao ele nunca pode divergir do painel. Quem imprime e o navegador.
   ponytail: sem indice clicavel; se precisar, entra uma lib de paginacao. */
.pdfbt{position:fixed;right:20px;bottom:20px;z-index:60;border:none;cursor:pointer;
 display:flex;align-items:center;gap:8px;background:var(--orange);color:#fff;
 font-family:'Plus Jakarta Sans',sans-serif;font-size:12.5px;font-weight:700;
 padding:12px 18px;border-radius:999px;box-shadow:0 10px 26px rgba(249,115,22,.40);transition:.2s}
.pdfbt:hover{background:#EA6A0B;transform:translateY(-1px)}
@media(max-width:620px){.pdfbt{right:12px;bottom:12px;padding:10px 14px;font-size:11.5px}}

.pdoc{display:none;background:#fff;color:var(--ink);font-family:'Inter',sans-serif}
.pdoc .pg{position:relative;width:297mm;height:209.6mm;padding:10mm 13mm 7mm;background:#fff;
 display:flex;flex-direction:column;overflow:hidden;break-after:page;page-break-after:always;
 break-inside:avoid}
.pdoc .pg:last-child{break-after:auto;page-break-after:auto}
.pdoc .pg-h{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;
 border-bottom:1.6px solid var(--navy);padding-bottom:3.5mm;margin-bottom:4mm}
.pdoc .pg-h .ttl{font-family:'Plus Jakarta Sans',sans-serif;font-size:16.5px;font-weight:800;
 letter-spacing:-.025em;color:var(--navy);line-height:1.15}
.pdoc .pg-h .sub{font-family:'Fraunces',serif;font-style:italic;font-weight:300;font-size:10.5px;
 color:var(--g500);margin-top:3px}
.pdoc .pg-h .rt{text-align:right;flex:none}
.pdoc .pg-h .rt b{display:block;font-family:'Plus Jakarta Sans',sans-serif;font-size:10px;
 font-weight:700;color:var(--navy)}
.pdoc .pg-h .rt span{font-family:'Plus Jakarta Sans',sans-serif;font-size:7.5px;font-weight:700;
 letter-spacing:.18em;text-transform:uppercase;color:var(--g400)}
.pdoc .pg-b{flex:1;min-height:0;overflow:hidden}
.pdoc .pg-f{display:flex;justify-content:space-between;align-items:center;margin-top:3mm;
 padding-top:2mm;border-top:1px solid var(--g200);font-family:'Plus Jakarta Sans',sans-serif;
 font-size:7.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--g400)}
.pdoc .pg-f .pn{font-style:normal;color:var(--orange);font-weight:800}

.pdoc .pg.capa{background:var(--navy);color:#fff;padding:0;justify-content:center}
.pdoc .capa-in{padding:0 22mm;display:flex;flex-direction:column;justify-content:center;height:100%}
.pdoc .capa .marca{font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;font-weight:800;
 letter-spacing:.06em;text-transform:uppercase;color:#fff;margin-top:18mm;margin-bottom:auto}
.pdoc .capa .marca b{color:var(--orange)}
.pdoc .capa .k{font-family:'Plus Jakarta Sans',sans-serif;font-size:10px;font-weight:700;
 letter-spacing:.26em;text-transform:uppercase;color:var(--orange);margin-bottom:10px}
.pdoc .capa h1{font-family:'Plus Jakarta Sans',sans-serif;font-weight:300;font-size:46px;
 letter-spacing:-.035em;line-height:1.02;margin-bottom:8px}
.pdoc .capa h1 b{font-weight:800}
.pdoc .capa .per{font-family:'Fraunces',serif;font-style:italic;font-weight:300;font-size:18px;
 color:rgba(255,255,255,.72)}
.pdoc .capa .meta{margin-top:auto;margin-bottom:16mm;padding-top:5mm;
 border-top:1px solid rgba(255,255,255,.16);display:flex;justify-content:space-between;gap:24px}
.pdoc .capa .meta div{font-family:'Plus Jakarta Sans',sans-serif;font-size:8.5px;font-weight:600;
 letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.5)}
.pdoc .capa .meta b{display:block;font-size:12px;letter-spacing:0;text-transform:none;color:#fff;
 margin-bottom:3px}

/* conteudo clonado: tudo cabe na pagina e nada rola */
.pdoc .pg-b table{width:100%!important;border-collapse:collapse;table-layout:fixed;font-size:8.4px}
.pdoc .pg-b th,.pdoc .pg-b td{padding:2.3px 4px!important;white-space:nowrap;overflow:hidden;
 text-overflow:ellipsis;border-radius:0!important}
.pdoc .pg-b thead th{background:var(--navy)!important;color:#fff!important;
 font-family:'Plus Jakarta Sans',sans-serif;font-size:7.4px;font-weight:700;letter-spacing:.05em;
 text-transform:uppercase;border:none!important}
.pdoc .pg-b td.l,.pdoc .pg-b th.l,.pdoc .pg-b td:first-child,.pdoc .pg-b th:first-child{
 position:static!important;box-shadow:none!important;text-align:left;width:200px;
 white-space:normal;line-height:1.25}
.pdoc .pg-b .chv{display:none!important}
.pdoc .pg-b .repwrap,.pdoc .pg-b .xmwrap{overflow:visible!important;border:none!important;
 box-shadow:none!important;border-radius:0!important;margin:0!important;background:none!important}
.pdoc .pg-b .kpis{display:grid!important;grid-template-columns:repeat(4,1fr);gap:6mm;margin:0!important}
.pdoc .pg-b .kpi{box-shadow:none!important;border:1px solid var(--g200)!important;padding:4mm!important}
.pdoc .pg-b .kpi .v{font-size:17px}
.pdoc .pg-b .waterfall{background:none!important;border:1px solid var(--g200);border-radius:10px;
 padding:5mm!important;margin:0!important;color:var(--ink)!important}
.pdoc .pg-b .waterfall .t,.pdoc .pg-b .waterfall .h,.pdoc .pg-b .wf-x span{color:var(--ink2)!important}
.pdoc .pg-b .waterfall svg{max-height:92mm}
.pdoc .pg-b .pz-grid{grid-template-columns:230px 1fr!important;align-items:center;gap:8mm!important}
.pdoc .pg-b .pz-chart svg{max-height:66mm}
.pdoc .pg-b .pz-leg{display:grid!important;grid-template-columns:1fr 1fr!important;
 font-size:8px!important;gap:2mm 6mm!important}
.pdoc .pg-b svg{max-width:100%;height:auto;display:block}
.pdoc .pg-b .aviso,.pdoc .pg-b .panel,.pdoc .pg-b .card{box-shadow:none!important;
 border:1px solid var(--g200)!important;margin:0 0 4mm!important}
.pdoc .pg-b .repnote,.pdoc .pg-b .lede,.pdoc .pg-b .nota,.pdoc .pg-b .disc{font-size:8px!important;
 line-height:1.5!important;color:var(--g500)!important;margin:3mm 0 0!important}
.pdoc .pg-b button,.pdoc .pg-b .rep-switch{display:none!important}
.pdoc .pg-b .mixrow{font-size:9px}

@media print{
 @page{size:A4 landscape;margin:0}
 html,body{background:#fff!important}
 html{scroll-behavior:auto}
 body>*{display:none!important}
 body>.pdoc{display:block!important}
 *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}

"""

JS = r"""
var ENT=(typeof ENT0!=='undefined'?ENT0:'consol'), MES=D.meses[D.meses.length-1], REG='caixa';
var SOCIOS=(typeof SOCIOS!=='undefined')&&SOCIOS;
function brl(v,c){c=c||0;var s=Math.abs(v).toLocaleString('pt-BR',{minimumFractionDigits:c,maximumFractionDigits:c});
 return (v<0?'−':'')+'R$ '+s}
/* base <= 0 nao gera percentual: a YO, sem receita, produzia "1528381,9%" */
function pc(v,b){return (b&&b>0)?(100*v/b).toFixed(1).replace('.',',')+'%':'—'}

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
/* FAT e o faturamento declarado do mes — a receita pelo mes da VENDA, nao do
   credito no banco. AJC e a ponte: faturamento menos o que o Omie lancou no
   grupo 1. Quem nao tem faturamento declarado cai no grupo 1, e AJC fica zero. */
/* mes parcial nao pode parecer fechado: ainda esta em carga, e os
   indicadores que dependem de documento que nao temos ficam em branco */
function parcial(m){return (D.parciais||[]).indexOf(m||MES)>=0}
/* mes sem DRE: a despesa dele ainda esta entrando, entao nao existe linha de
   resultado honesta para o mes — ele sai da tabela de competencia inteira e
   fica so no fluxo de caixa. A venda medida continua no cruzamento de
   faturamento, ao lado do que o Omie lancou. */
function semDre(m){return (D.sem_dre||[]).indexOf(m||MES)>=0}
function mesesDe(reg){return reg==='comp'
 ?D.meses.filter(function(m){return !semDre(m)}):D.meses}
function fatDe(ent,reg,mes){
 if(reg!=='comp')return null;
 if(ent==='consol'){
  var t=0,achou=false;
  ['boldro','yo'].forEach(function(e){
   var b=((D.ents[e]||{}).comp||{})[mes]; if(!b)return;
   if(b.fat){t+=b.fat.valor;achou=true}else{t+=b.grupos['1']||0}
  });
  return achou?t:null;
 }
 var b=((D.ents[ent]||{}).comp||{})[mes];
 return (b&&b.fat)?b.fat.valor:null;
}
function soma(ent,reg,mes,ks){var b=bloco(ent,reg,mes),t=0;
 ks.forEach(function(k){
  if(k==='FAT'){var f=fatDe(ent,reg,mes);t+=(f===null)?(b.grupos['1']||0):f;return}
  if(k==='AJC'){var f2=fatDe(ent,reg,mes);t+=(f2===null)?0:(f2-(b.grupos['1']||0));return}
  t+=b.grupos[k]||0});
 return t}
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

/* Quais grupos sao OPERACIONAIS no caixa. Mora aqui, sozinho, porque tres
   blocos mostram esse numero com o mesmo nome — o card do cabecalho, a ponte e a
   linha da tabela do DFC. Cada um com a sua lista ja deu dois numeros na mesma
   tela (05/11/2026): a ponte esquecia o grupo OR e dizia 204.926,04 enquanto o
   card e a tabela diziam 210.924,08. */
var GRUPOS_OP=['1','OR','2','3','4','5','6','7','8','9','14','10','IR'];

function passosPonte(mes){
 mes=mes||MES;
 /* a ponte segue o regime escolhido: no caixa e saldo -> entradas -> saidas;
    na competencia e receita -> custo -> despesa -> EBITDA, que e o que mostra o
    faturamento do mes em vez do que passou no banco. */
 if(REG==='comp'){
  if(!temDado(ENT)||semDre(mes))return null;
  var rec=soma(ENT,'comp',mes,['FAT']), ded=soma(ENT,'comp',mes,['2']),
      cus=soma(ENT,'comp',mes,['3','4','5']), des=soma(ENT,'comp',mes,['6','7','8','9','14']);
  if(!rec&&!ded&&!cus&&!des)return null;
  return [['Receita bruta',rec,'in'],['Deduções',ded,'out'],['Custos',cus,'out'],
          ['Despesas',des,'out'],['EBITDA',rec+ded+cus+des,'r']];
 }
 var s=saldos(ENT,mes);
 if(!s)return null;
 /* pedido do Tiago em 05/11: entradas x saidas nao dizem se a operacao gera
    caixa. A ponte agora separa o que a casa gerou do que foi obra e aporte,
    nos mesmos grupos da DRE: acima do EBITDA = operacional; 11 = investimento;
    12 = financiamento; o resto (CC, neutras, 13) e transferencia e ajuste.
    A linha operacional le a MESMA lista de grupos da tabela do DFC (BLOCOS_DFC),
    senao a ponte e a tabela mostram dois numeros com o mesmo nome na mesma tela.
    A ultima perna e o residuo, entao a ponte fecha no saldo do banco sempre. */
 var mov=s.entradas+s.saidas,
     op=soma(ENT,'caixa',mes,GRUPOS_OP),
     inv=soma(ENT,'caixa',mes,['11']),
     fin=soma(ENT,'caixa',mes,['12']),
     res=mov-op-inv-fin;
 return [['Saldo inicial',s.ini,'n'],
         ['Geração de caixa operacional',op,op<0?'out':'in'],
         ['Investimentos',inv,inv>0?'in':'out'],
         ['Financiamento',fin,fin<0?'out':'in'],
         ['Não operacional e transferências',res,res<0?'out':'in'],
         ['Saldo final',s.fim,'n']];
}
function ponteSVG(){
 /* Cascata do MES SELECIONADO, uma faixa so. Era uma faixa por mes do regime
    (pedido do Joao em 06/11/2026) e voltou ao mes unico em 09/11/2026, tambem
    por decisao dele: com tres meses ficava sujo, e o modelo que o Tiago mandou
    como padrao mostra a cascata de um mes ("Cascata da DRE . setembro").
    O codigo continua em laco sobre uma lista de meses — trocar MS abaixo por
    mesesDe(REG) traz as faixas de volta. Tudo vive DENTRO do
    svg — inclusive os rotulos dos passos —, porque o eixo em HTML com grid de
    contagem fixa ja desalinhou das barras uma vez. O viewBox cresce com o
    numero de faixas e a pagina acompanha pelo aspect-ratio, entao nada corta.
    Cada faixa tem a SUA escala: os meses tem ordem de grandeza diferente e uma
    escala comum achataria o menor deles. */
 var MS=[MES].filter(function(m){return !!passosPonte(m)});
 if(!MS.length){
  var vazio=(REG==='comp'&&semDre(MES))
   ?D.meses_nome[MES]+' não tem DRE: o faturamento do 3LM do mês ainda não entrou, e sem a receita nenhuma margem tem leitura. O caixa do mês está conferido contra o extrato — veja o Caixa.'
   :'sem movimento lançado neste mês';
  wfBox(1080,150);
  return '<text x="540" y="80" text-anchor="middle" fill="#6D748A" font-size="14" font-family="Inter">'+vazio+'</text>';
 }
 var W=1080, ML=96, MR=14, FX=W-ML-MR,
     BH=118,            /* altura util das barras de uma faixa */
     GAP=34,            /* respiro entre faixas, onde cabe o nome do mes */
     AX=30,             /* faixa dos rotulos dos passos, no pe */
     TOP=10,
     n=passosPonte(MS[0]).length,
     cw=FX/n, bw=Math.min(84,cw-22),
     H=TOP+MS.length*(BH+GAP)+AX,
     out='';
 wfBox(W,H);
 MS.forEach(function(mes,fi){
  var passos=passosPonte(mes),
      y0=TOP+fi*(BH+GAP),
      base=y0+BH;
  /* escala da faixa: faixa da linha acumulada, com o zero sempre dentro, e o
     maior passo isolado, que pode passar do acumulado */
  var pts=[0], cur=(passos[0][2]==='n')?passos[0][1]:0;
  pts.push(cur);
  passos.forEach(function(p){
   if(p[2]==='n'||p[2]==='r'){pts.push(p[1]);return}
   pts.push(cur+p[1]); pts.push(cur); cur+=p[1];
  });
  passos.forEach(function(p){if(p[2]!=='n')pts.push(p[1])});
  var lo=Math.min.apply(null,pts), hi=Math.max.apply(null,pts);
  if(hi===lo)hi=lo+1;
  var esc=BH-20, yOf=function(v){return base-((v-lo)/(hi-lo))*esc}, zero=yOf(0);
  /* nome do mes, a esquerda da faixa */
  out+='<text x="0" y="'+(y0+BH/2-4).toFixed(1)+'" fill="#E7EAF3" font-size="15" '+
       'font-weight="700" font-family="Plus Jakarta Sans">'+D.meses_nome[mes]+'</text>';
  if(lo<0&&hi>0)
   out+='<line x1="'+ML+'" y1="'+zero.toFixed(1)+'" x2="'+(W-MR)+'" y2="'+zero.toFixed(1)+
        '" stroke="#39405A" stroke-width="1" stroke-dasharray="4 4"/>';
  var acum=(passos[0][2]==='n')?passos[0][1]:0;
  passos.forEach(function(p,i){
   var cx=ML+i*cw+cw/2, de, ate, cor;
   if(p[2]==='in'||p[2]==='out'){de=acum; ate=acum+p[1]; acum=ate; cor=(p[1]<0)?'#F87171':'#34D399'}
   else{de=0; ate=p[1]; cor=(p[2]==='r')?'#F97316':'#9CA3AF'}
   var y1=yOf(de), y2=yOf(ate), y=Math.min(y1,y2), alt=Math.max(3,Math.abs(y2-y1));
   out+='<rect x="'+(cx-bw/2).toFixed(1)+'" y="'+y.toFixed(1)+'" width="'+bw.toFixed(1)+
        '" height="'+alt.toFixed(1)+'" rx="5" fill="'+cor+'" opacity=".92"/>';
   /* o rotulo vai ACIMA da barra; se nao cabe, vai abaixo, nunca fora da faixa */
   var ly=(y-7>=y0+9)?(y-7):(y+alt+13);
   out+='<text x="'+cx.toFixed(1)+'" y="'+ly.toFixed(1)+'" text-anchor="middle" fill="#fff" '+
        'font-size="12" font-weight="700" font-family="Plus Jakarta Sans">'+brl(p[1])+'</text>';
  });
 });
 /* eixo dos passos, uma vez, no pe — mesma grade das barras */
 var rot=passosPonte(MS[0]);
 rot.forEach(function(p,i){
  var cx=ML+i*cw+cw/2;
  out+='<text x="'+cx.toFixed(1)+'" y="'+(H-9)+'" text-anchor="middle" fill="#8A91A6" '+
       'font-size="11.5" font-family="Inter">'+p[0]+'</text>';
 });
 return out;
}
/* o viewBox e o aspect-ratio andam juntos: se so o viewBox cresce, o svg mantem
   a proporcao antiga e o conteudo e reduzido para caber — foi o que fez a
   cascata parecer cortada. */
function wfBox(w,h){
 var el=document.getElementById('wf');
 if(!el)return;
 el.setAttribute('viewBox','0 0 '+w+' '+h);
 el.style.aspectRatio=w+'/'+h;
}

function cozinha(mes){
 var b=bloco(ENT,'comp',mes), f=b.familias||{};
 var venda=soma(ENT,'comp',mes,['FAT','2']);
 return {venda:venda, cmv:-soma(ENT,'comp',mes,['4']), food:-(f.cozinha||0), bar:-(f.bar||0),
         comum:-(f.comum||0), pessoal:-soma(ENT,'comp',mes,['6']),
         operacao:-soma(ENT,'comp',mes,['5']), ocupacao:-soma(ENT,'comp',mes,['7']),
         adm:-soma(ENT,'comp',mes,['8']), mkt:-soma(ENT,'comp',mes,['9','14']),
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
function vd(){if(!D.vendas||ENT==='yo')return null; return D.vendas[MES]||null}
/* tem curva ABC mas nao tem dia/turno/hora: e o caso de outubro, que veio do
   Backup do 3LM (item a item, sem data) e nao do relatorio da diretoria. */
function vdTemDia(){var V=vd(); return !!(V&&V.dias&&V.dias.length)}
function vdTemTurno(){var V=vd(); return !!(V&&V.turno&&V.turno.dia)}
function semHora(){
 var com=Object.keys(D.vendas||{}).filter(function(m){
   var v=D.vendas[m]; return v&&v.turno&&v.turno.dia});
 return com.length? 'o relatório com data e hora só existe em '+
   com.map(function(m){return D.meses_nome[m]}).join(' e ')
  : 'ainda não há relatório com data e hora';}
function tkCard(){var V=vd();
 if(!vdTemDia())return ['Ticket médio por conta',emC(ENT==='yo'?'a YO não fatura: a venda está no CNPJ da Boldró':semHora()),'',''];
 return ['Ticket médio por conta',brl(V.ticket),V.contas.toLocaleString('pt-BR')+' contas no mês',
         'fonte: relatório do 3LM · por comanda, não por mesa']}
function turnoCard(){var V=vd();
 if(!vdTemTurno())return ['Share por turno',emC(ENT==='yo'?'a YO não fatura':semHora()),'',''];
 var t=V.turno;
 /* o percentual do 3LM e sobre a soma dos turnos, que e MENOR que o mes: o
    relatorio de horario nao traz a taxa de servico e nao traz 30/09. Mostrar
    "67,8% do mes" seria falso — sobre o mes o almoco e 59,6%. */
 var somaT=t.dia.valor+t.final.valor+((t.antes||{}).valor||0);
 return ['Consumo no almoço',(100*t.dia.valor/somaT).toFixed(1).replace('.',',')+'%',
         brl(t.dia.valor)+' das 11h às 16h, sobre '+brl(somaT)+' com hora registrada',
         'fim de dia: '+(100*t.final.valor/somaT).toFixed(1).replace('.',',')+'% · '+brl(t.final.valor)+
         ' — a base do relatório de horário é '+pc(somaT,V.recebido)+' do mês: não traz a taxa de serviço nem o dia 30/09']}
function diaForteCard(){var V=vd();
 if(!vdTemDia())return ['Venda por dia da semana',emC(ENT==='yo'?'a YO não fatura':semHora()),'',''];
 var s={},c={};
 V.dias.forEach(function(d){s[d.sem]=(s[d.sem]||0)+d.valor;c[d.sem]=(c[d.sem]||0)+d.contas});
 var ks=Object.keys(s).sort(function(a,b){return s[b]-s[a]}), tot=0;
 ks.forEach(function(k){tot+=s[k]});
 var NOME={segunda:'segunda',terca:'terça',quarta:'quarta',quinta:'quinta',sexta:'sexta',sabado:'sábado',domingo:'domingo'};
 return ['Dia mais forte',NOME[ks[0]],brl(s[ks[0]])+' · '+pc(s[ks[0]],tot)+' do mês',
         'o mais fraco é '+NOME[ks[ks.length-1]]+' ('+pc(s[ks[ks.length-1]],tot)+')']}

/* bloco de vendas: dia da semana e curva ABC */
function vendasBloco(){
 var dia=document.getElementById('v-dia'), mix=document.getElementById('v-mix');
 if(!dia||!mix)return;
 var V=vd();
 if(!V){
  var temMes=!!D.vendas;
  dia.innerHTML=mix.innerHTML='<div class="vazio"><h4>'+
   (ENT==='yo'?'A YO não fatura':(temMes?'Sem relatório de vendas de '+D.meses_nome[MES]:'Sem relatório de vendas'))+'</h4>'+
   '<p>'+(ENT==='yo'?'A venda de salão acontece no CNPJ da Boldró. Troque de empresa no topo.'
    :'O 3LM não tem API: estes números vêm do relatório mensal em PDF, e hoje só existe o de '+
      Object.keys(D.vendas||{}).map(function(m){return D.meses_nome[m]}).join(' e ')+'.')+'</p></div>';
  return;
 }
 if(!vdTemDia()){
  dia.innerHTML='<div class="vazio"><h4>Venda por dia e por turno não disponível em '+
   D.meses_nome[MES]+'</h4><p>A curva ABC ao lado sai do relatório <b>Vendas Por '+
   'Funcionário</b> do 3LM, que traz item a item mas <b>não traz data nem hora</b>. '+
   'Dia da semana, turno, número de contas e ticket médio só existem no relatório '+
   'de vendas montado pela diretoria, que ainda não veio para este mês.</p></div>';
  montaMix(V); return;
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
 /* dia a dia: conta, venda, ticket e a divisao do turno */
 var hr={}; (V.horario||[]).forEach(function(x){hr[x.data]=x});
 var NOM={segunda:'segunda',terca:'terça',quarta:'quarta',quinta:'quinta',sexta:'sexta',sabado:'sábado',domingo:'domingo'};
 /* o percentual anda junto do valor do turno, nao numa coluna solta: o que a
    diretoria le e "quanto do dia foi almoco", e isso e do almoco, nao da linha.
    A base e o que tem hora registrada naquele dia — almoco + fim de dia +
    inicio do dia — por isso os dois nao somam 100%. */
 function turno(v,base){
  if(!v)return '<td class="num">–</td>';
  return '<td class="num">'+brl(v)+'<span class="pq">'+
   (base?(100*v/base).toFixed(0).replace('.',',')+'%':'–')+'</span></td>';
 }
 h+='<h4 class="subt">Dia a dia · '+D.meses_nome[V.mes]+'</h4>'+
    '<table class="xtbl"><thead><tr><th class="l">Data</th><th class="l">Dia</th><th>Contas</th>'+
    '<th>Venda</th><th>Ticket</th><th>Almoço</th><th>Fim de dia</th>'+
    '</tr></thead><tbody>';
 var sd=0,sf=0,sa=0;
 V.dias.forEach(function(d){
  var x=hr[d.data]||{}, bs=(x.dia||0)+(x.final||0)+(x.antes||0);
  sd+=x.dia||0; sf+=x.final||0; sa+=x.antes||0;
  h+='<tr><td class="l">'+d.data+'</td><td class="l">'+(NOM[d.sem]||d.sem)+'</td>'+
     '<td class="num">'+(d.contas==null?'–':d.contas)+'</td><td class="num">'+brl(d.valor)+'</td>'+
     '<td class="num">'+(d.ticket==null?'–':brl(d.ticket))+'</td>'+
     turno(x.dia,bs)+turno(x.final,bs)+'</tr>';
 });
 var tc=V.dias.reduce(function(a,d){return a+(d.contas||0)},0)||V.contas||0,
     tv=V.dias.reduce(function(a,d){return a+d.valor},0);
 var sb=sd+sf+sa;
 h+='<tr class="dfcs"><td class="l">Total do mês</td><td class="l"></td><td class="num">'+tc+'</td>'+
    '<td class="num">'+brl(tv)+'</td><td class="num">'+brl(tv/tc)+'</td>'+
    turno(sd,sb)+turno(sf,sb)+'</tr></tbody></table>'+
    (vdTemTurno()?'<p class="repnote" style="margin-top:8px">No mês, <b>'+
    (sb?(100*sd/sb).toFixed(1).replace('.',',')+'%':'–')+' da venda com hora registrada é almoço</b> ('+
    brl(sd)+') e <b>'+(sb?(100*sf/sb).toFixed(1).replace('.',',')+'%':'–')+' é fim de dia</b> ('+
    brl(sf)+'). O resto, '+(sb?(100*sa/sb).toFixed(1).replace('.',',')+'%':'–')+' ('+brl(sa)+
    '), é início do dia. A base são os '+brl(sb)+' que o 3LM carimba com hora — '+
    pc(sb,V.recebido)+' do mês: ele não carimba hora na taxa de serviço nem no dia 30/09.</p>'
    :'<p class="repnote" style="margin-top:8px">'+(V.fonte||'')+
     ' <b>Contas e ticket por dia não aparecem</b> porque este relatório traz o valor '+
     'de cada dia, não a contagem de comandas; o ticket médio do mês ('+brl(V.ticket)+
     ' em '+(V.contas||0).toLocaleString('pt-BR')+' contas) vem do Itens Vendidos '+
     'Analítico. Turno e horário dependem da hora de cada conta, que só o Analítico '+
     'em CSV entrega.</p>');
 h+='<p class="repnote"><b>Ticket individual e por mesa continuam em construção:</b> '+
    'o 3LM exporta a comanda, mas não o número de pessoas nem a mesa física. '+
    'Com essas duas colunas na exportação os dois indicadores entram. '+
    'Fonte: relatório de vendas do 3LM/Gourmet.</p>';
 dia.innerHTML=h;
 montaMix(V);
}
function montaMix(V){
 var mix=document.getElementById('v-mix'); if(!mix)return;
 var cats=Object.keys(V.abc).sort(function(a,b){return V.abc[b].receita-V.abc[a].receita});
 /* o total vem ANTES das linhas: o % de cada tipo sobre a venda de produtos e
    o que o Tiago pediu em 09/11/2026 — "quantos % do faturamento e bebida,
    entrada ou prato principal". */
 var tr=0; cats.forEach(function(k){tr+=V.abc[k].receita});
 var hm='<h4 class="subt">Curva ABC por categoria</h4>'+
    '<table class="xtbl"><thead><tr><th class="l">Categoria</th><th>Receita</th>'+
    '<th class="av">% da venda</th><th>Itens</th>'+
    '<th>Classe A</th><th class="av">% em A</th><th>Classe B</th><th>Classe C</th></tr></thead><tbody>';
 cats.forEach(function(k){var x=V.abc[k];
  hm+='<tr class="abc-l" onclick="abreABC(\''+k+'\')"><td class="l"><span class="chv">▸</span>'+k+
     '</td><td class="num">'+brl(x.receita)+'</td>'+
     '<td class="av"><b>'+(100*x.receita/(tr||1)).toFixed(1).replace('.',',')+'%</b></td>'+
     '<td class="av">'+x.itens+'</td>'+
     '<td class="num">'+brl(x.A.valor)+' <span class="z">('+x.A.itens+')</span></td>'+
     '<td class="av">'+(100*x.A.pct).toFixed(1).replace('.',',')+'%</td>'+
     '<td class="num">'+brl(x.B.valor)+'</td><td class="num">'+brl(x.C.valor)+'</td></tr>';
 });
 hm+='<tr class="dfcs"><td class="l">Venda de cardápio</td><td class="num">'+brl(tr)+'</td>'+
    '<td class="av"><b>100,0%</b></td>'+
    '<td class="av"></td><td class="num"></td><td class="av"></td><td class="num"></td><td class="num"></td></tr>';
 hm+='</tbody></table>';
 hm+='<p class="repnote"><b>A coluna "% da venda" é a fatia de cada tipo na venda de '+
    'cardápio</b> — é o mix do menu. A curva ABC de cada categoria, essa sim, é calculada '+
    'sobre a receita daquela categoria: classe A vai até 80% do faturamento do grupo, B de 80% '+
    'a 95%, C os 5% finais. Clique na categoria para abrir os itens. '+
    '<b>Sai da mesma extração do 3LM que alimenta a DRE</b>, por isso o total desta curva '+
    'é exatamente a <b>venda de cardápio</b> da composição ('+brl(tr)+') — a venda bruta '+
    'do mês menos a taxa de serviço. A classificação por tipo não existe no 3LM: vem do '+
    'relatório da diretoria item a item, do prefixo da própria carta nas bebidas, e de '+
    'decisão da diretoria nos oito itens restantes.</p>';
 hm+=pgtoTabela()+horarioTabela();
 mix.innerHTML=hm;
}

/* forma de pagamento: a mesma abertura que abre no clique da receita bruta */
function pgtoTabela(){
 var F=formasDe();
 if(!F)return '<h4 class="subt">Como o cliente pagou</h4><p class="repnote">'+
  (ENT==='yo'?'A YO não fatura.':'Depende do Extrato de Vendas Detalhado da adquirente, que só existe em agosto e setembro.')+'</p>';
 var o=F.linhas.slice().sort(function(a,b){return b[1]-a[1]});
 var h='<h4 class="subt">Como o cliente pagou · '+D.meses_nome[MES]+'</h4>'+
  '<table class="xtbl"><thead><tr><th class="l">Forma de pagamento</th><th>Valor</th>'+
  '<th class="av">% do total</th></tr></thead><tbody>';
 o.forEach(function(x){h+='<tr><td class="l">'+x[0]+'</td><td class="num">'+brl(x[1])+
  '</td><td class="av">'+pc(x[1],F.total)+'</td></tr>'});
 h+='<tr class="dfcs"><td class="l">Total</td><td class="num">'+brl(F.total)+
  '</td><td class="av">100,0%</td></tr></tbody></table>'+
  '<p class="repnote">Venda a venda do Extrato de Vendas Detalhado da GetNet, mais o dinheiro do fundo fixo. '+
  'O total fecha com a <b>venda bruta</b> a menos do ajuste de medição do 3LM.</p>';
 return h;
}

/* faturamento por horario: o 3LM separa antes do almoco, almoco e fim de dia */
function horarioTabela(){
 var V=vd(); if(!vdTemTurno())return '';
 var t=V.turno, L=[['Início do dia',(t.antes||{}).valor||0],['Almoço (11h às 16h)',t.dia.valor],
  ['Fim de dia',t.final.valor]], tot=0;
 L.forEach(function(x){tot+=x[1]});
 var h='<h4 class="subt">Faturamento por horário · '+D.meses_nome[V.mes]+'</h4>'+
  '<table class="xtbl"><thead><tr><th class="l">Horário</th><th>Valor</th>'+
  '<th class="av">% do total</th></tr></thead><tbody>';
 L.forEach(function(x){h+='<tr><td class="l">'+x[0]+'</td><td class="num">'+brl(x[1])+
  '</td><td class="av">'+pc(x[1],tot)+'</td></tr>'});
 h+='<tr class="dfcs"><td class="l">Com hora registrada</td><td class="num">'+brl(tot)+
  '</td><td class="av">100,0%</td></tr></tbody></table>'+
  '<p class="repnote">A base do relatório de horário é '+pc(tot,V.recebido)+' do mês: '+
  'o 3LM não carimba hora na taxa de serviço nem no dia 30/09. Os percentuais são sobre '+
  'o que tem hora registrada, não sobre o faturamento do mês.</p>';
 return h;
}

/* forma de pagamento: vem do Extrato de Vendas Detalhado da GetNet mais o
   dinheiro do fundo fixo. So existe onde ha extrato da adquirente. */
function formasDe(mes){
 if(ENT==='yo')return null;
 var c=bloco(ENT,'comp',mes||MES).contas, o=[], tot=0;
 Object.keys(c).forEach(function(k){
  if(k.indexOf('FAT|')!==0)return;
  var nome=k.slice(4);
  /* o ajuste ao total do 3LM e residuo de medicao, nao forma de pagamento */
  if(nome.indexOf('Ajuste')===0)return;
  /* no mes sem extrato da adquirente o detalhe e a abertura por item, nao
     forma de pagamento — a leitura seria outra coisa com o mesmo rotulo */
  if(nome==='A&B'||nome==='Taxa de servico'||nome==='Couvert'||nome==='Taxa de rolha')return;
  o.push([nome,c[k]]); tot+=c[k];
 });
 if(tot)return {linhas:o,total:tot};
 /* mes fora da DRE nao tem conta FAT| (SEM_DRE), mas pode ter forma de
    pagamento medida: out/26 veio do relatorio de Tipo de Pagamento do 3LM. */
 var R=(D.receita||{})[mes||MES];
 if(R&&R.formas&&R.formas.length){
  var t2=0; R.formas.forEach(function(x){t2+=x[1]});
  return {linhas:R.formas.map(function(x){return [x[0],x[1]]}),total:t2,nota:R.formas_nota};
 }
 return null;
}
function pgtoCard(){
 var F=formasDe();
 if(!F)return ['Como o cliente pagou',emC(ENT==='yo'?'a YO não fatura'
   :'depende do extrato detalhado da adquirente, que só existe em ago e set'),'',''];
 var o=F.linhas.slice().sort(function(a,b){return b[1]-a[1]});
 function curto(n){return n.replace('Cartão de crédito à vista','crédito')
  .replace('Cartão de débito','débito').replace('Dinheiro (fundo fixo)','dinheiro')}
 var bruta=soma(ENT,'comp',MES,['FAT']), gap=F.total-bruta;
 return ['Como o cliente pagou',pc(o[0][1],F.total)+' '+curto(o[0][0]),
  o.slice(1).map(function(x){return pc(x[1],F.total)+' '+curto(x[0])}).join(' · '),
  'sobre '+brl(F.total)+' reconstruídos da GetNet venda a venda mais o fundo fixo'+
  (Math.abs(gap)>1?(' — '+brl(Math.abs(gap))+(gap>0?' acima':' abaixo')+
   ' da venda bruta de '+brl(bruta)+', que vem do 3LM e é a que vale na DRE'):'')];
}
function contasCard(){
 var V=vd();
 if(!V)return ['Contas no mês',emC(ENT==='yo'?'a YO não fatura':'só há relatório de vendas de set/26'),'',''];
 var pr=(D.prereserva||{})[MES];
 return ['Contas no mês',V.contas.toLocaleString('pt-BR'),
  pr===undefined?'pré-reserva: aguardando a gerência operacional'
   :pc(pr,V.contas)+' vieram de pré-reserva ('+pr.toLocaleString('pt-BR')+')',
  'fonte: 3LM · por comanda, não por mesa'];
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
      cus=soma(ENT,'comp',MES,['4','5','6','7','8','9','14']),
      /* na pre-operacao a receita e o grupo OR (outros recebimentos):
         a YO nao tem grupo 1, e o KPI saia R$ 0,00 com R$ 32.550,21 ao lado */
      rec=soma(ENT,'comp',MES,['1','OR']);
  var qT=0,iT=0,aT=0;
  D.meses.forEach(function(m){qT+=soma(ENT,'comp',m,['4','5','6','7','8','9','14','11']);
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
 var ebitda=k.venda+soma(ENT,'comp',MES,['4','5','3','6','7','8','9','14']);
 var cc=soma(ENT,'comp',MES,['CC']);
 var fixo=k.pessoal+k.ocupacao+k.adm+k.mkt+k.operacao;
 /* Duas coisas diferentes travam um mes parcial, e elas nao andam juntas.
    semVenda: nao ha relatorio de vendas do mes, entao o grupo 1 traz so o que
      ja foi lancado e exibir isso como venda inventa uma queda que nao houve.
    custoEmCarga: a venda esta medida, mas a despesa ainda nao. Qualquer
      indicador de RESULTADO vira elogio falso — em outubro a receita esta
      inteira (3LM) e o custo esta em ~6% do movimento de setembro. */
 var semVenda=parcial(MES)&&fatDe(ENT,'comp',MES)===null;
 var bruta=soma(ENT,'comp',MES,['FAT']);
 /* geracao de caixa OPERACIONAL: a mesma linha do DFC, sem investimento,
    financiamento nem transferencia. E caixa, entao sai do regime 'caixa'. */
 var gco=soma(ENT,'caixa',MES,GRUPOS_OP);
 var custoEmCarga=parcial(MES);
 return [
  semVenda?['Vendas brutas',emC('a venda do 3LM não entra na DRE enquanto o custo do mês estiver em carga — ela está na abertura da venda'),'','']
         :['Vendas brutas',brl(bruta),'o que a casa vendeu em '+D.meses_nome[MES],
           'antes dos tributos · líquida: '+brl(k.venda)],
  semVenda?['Venda por dia',emC('depende da venda do mês'),'','']
         :['Venda por dia',brl(bruta/dias),dias+' dias de operação','é o número que o salão sente'],
  tkCard(),
  (semVenda||custoEmCarga)
    ?['Margem EBITDA',emC(semVenda?'depende da venda do mês'
        :'a venda do mês já está medida, mas o custo ainda está em carga: margem aqui seria elogio falso'),'','']
    :['Margem EBITDA',pc(ebitda,bruta),brl(ebitda)+' no mês','sobre a venda bruta'],
  ['Geração de caixa operacional',brl(gco),'entrou menos saiu na operação, pelo extrato',
   'investimento e aporte ficam fora · caixa do mês: '+brl(s.fim-s.ini)],
  pgtoCard(), contasCard(),
  ['Dinheiro em caixa',brl(s.fim),'no banco ao fim do mês',
   fixo?('dá para '+(s.fim/fixo).toFixed(1).replace('.',',')+' mês de casa aberta'):''],
  turnoCard(), diaForteCard()
 ].map(card).join('');
}

var CORES=['#F97316','#0D0F1A','#0E9F6E','#DC2626','#6366F1','#D97706','#0891B2','#7C3AED',
 '#BE185D','#4D7C0F','#9CA3AF','#334155'];
/* custo de receber: taxa por bandeira e antecipacao. Quem conclui e quem le. */
function custoReceber(){
 var el=document.getElementById('tx-kpis'), tb=document.getElementById('tx-tab');
 if(!el||!tb)return;
 var T=txDe();
 if(!T){
  el.innerHTML='<div class="vazio"><h4>'+(ENT==='yo'?'A YO não recebe de cliente'
    :'Sem extrato detalhado da adquirente em '+(D.meses_nome[MES]||'')) +'</h4><p>'+
   (ENT==='yo'?'Quem fatura o restaurante é a Boldró — o custo de receber vive lá.'
    :'A taxa por bandeira sai do Extrato de Vendas Detalhado da GetNet, que existe em '+
     Object.keys(D.taxas||{}).map(function(m){return D.meses_nome[m]}).join(' e ')+
     '. Escolha um desses meses nas pílulas.')+'</p></div>';
  tb.innerHTML=''; return;
 }
 var c=T.cartao||{}, px=T.pix||{}, an=T.antecipacao||{};
 var total=(c.taxa||0)+(an.custo||0);
 el.innerHTML=[
  ['Custo total de receber',brl(total),'taxa de cartão mais antecipação',
   pc(total,(c.bruto||0)+(px.bruto||0))+' do que entrou por cartão e PIX'],
  ['Taxa de cartão',brl(c.taxa||0),txPc(c.pc||0)+' sobre '+brl(c.bruto||0),
   (c.n||0).toLocaleString('pt-BR')+' vendas no cartão'],
  ['Antecipação',brl(an.custo||0),txPc(an.pc||0)+' sobre '+brl(an.base||0),
   an.total_creditado?('creditado no mês: '+brl(an.total_creditado)):''],
  ['PIX',brl(px.bruto||0),'entrou sem taxa nenhuma',
   (px.n||0).toLocaleString('pt-BR')+' recebimentos · '+
   pc(px.bruto||0,(c.bruto||0)+(px.bruto||0))+' do recebido']
 ].map(card).join('');

 var L=(T.linhas||[]).slice().sort(function(a,b){return b.bruto-a.bruto});
 var h='<div class="repwrap on"><table class="xtbl"><thead><tr><th class="l">Bandeira e modalidade</th>'+
  '<th>Vendas</th><th>Bruto</th><th>Ticket médio</th><th>Taxa</th><th class="av">Taxa efetiva</th></tr></thead><tbody>';
 L.forEach(function(x){
  h+='<tr class="lvl1"><td class="l n1">'+x.bandeira+' · '+x.modalidade+'</td>'+
   '<td class="num">'+x.n.toLocaleString('pt-BR')+'</td>'+
   '<td class="num">'+mv(x.bruto)+'</td><td class="num">'+mv(x.ticket)+'</td>'+
   '<td class="num neg">'+mv(-x.taxa)+'</td><td class="num avtot">'+txPc(x.pc)+'</td></tr>';
 });
 h+='<tr class="ebit"><td class="l">Recebido em cartão</td><td class="num">'+
  (c.n||0).toLocaleString('pt-BR')+'</td><td class="num">'+mv(c.bruto||0)+
  '</td><td class="num">'+mv(c.n?(c.bruto/c.n):0)+'</td><td class="num">'+
  mv(-(c.taxa||0))+'</td><td class="num avtot">'+txPc(c.pc||0)+'</td></tr>';
 h+='</tbody></table></div>'+
  '<p class="repnote">A taxa efetiva é a que a GetNet cobrou de fato em cada venda, não a de tabela. '+
  'As duas cobranças moram em linhas diferentes da DRE: a <b>taxa de cartão</b> ('+
  brl(c.taxa||0)+') entra em despesas variáveis de venda, <b>acima</b> do EBITDA; a '+
  '<b>antecipação</b> ('+brl(an.custo||0)+', '+txPc(an.pc||0)+' sobre '+brl(an.base||0)+
  ') entra em resultado financeiro, <b>abaixo</b> do EBITDA. Nenhuma das duas é '+
  'dedução da receita.</p>';
 tb.innerHTML=h;
}

function pizza(){
 var b=(REG==='comp'&&semDre(MES))?{grupos:{}}:bloco(ENT,REG,MES),itens=[];
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

var ABERTO={};                  /* nos abertos, por chave */
/* na visao dos socios a DRE e o DFC nao abrem: e leitura, nao conferencia */
function tog(k){if(SOCIOS)return;ABERTO[k]=!ABERTO[k];pintaRelatorios()}
function cv(k){return SOCIOS?'':'<span class="chv">'+(ABERTO[k]?'▾':'▸')+'</span>'}

/* celula: valor com a analise vertical dentro, como no painel modelo */
/* na matriz o numero vai sem "R$" e com centavos, como no painel modelo:
   cabe mais mes na largura e a soma visual fecha com o total. */
function mv(v){return (v<0?'-':'')+Math.abs(v).toLocaleString('pt-BR',
 {minimumFractionDigits:2,maximumFractionDigits:2})}
function tdMes(v){return '<td class="num">'+(v?brl(v):'<span class="z">–</span>')+'</td>'}
function cel(v,base,cls,abre){
 if(!v)return '<td class="num '+(cls||'')+'">–</td>';
 cls=(cls||'')+(v<0?' neg':'');
 var a=(abre&&!SOCIOS)?' onclick="abreCaixa(event,\''+abre[0].replace(/'/g,"\\'")+'\',\''+abre[1]+'\',\''+abre[2]+'\')" class="num clic '+(cls||'')+'"'
           :' class="num '+(cls||'')+'"';
 return '<td'+a+'>'+mv(v)+(base?'<i class="avin">'+pc(v,base)+'</i>':'')+'</td>';
}

/* caixa dos itens de uma curva ABC */
function abreABC(cat){
 var V=vd(); if(!V)return; var x=V.abc[cat], its=x.itens_lista||[];
 var h='<div class="cx-cab"><h4>Curva ABC · '+cat+' · '+D.meses_nome[V.mes]+'</h4>'+
   '<button class="cx-x" onclick="fechaCaixa()">×</button></div>'+
   '<div class="cx-sub"><span>'+its.length+' ITENS ATIVOS</span><b>RECEITA: '+mv(x.receita)+'</b></div>'+
   '<div class="cx-nota">Classe A vai até 80% do faturamento da categoria, B de 80% a 95%, C os 5% finais. '+
   'A curva é calculada sobre a receita desta categoria, não sobre o total do mês.</div>';
 h+='<table class="cx-tbl"><thead><tr><th>#</th><th>Item</th><th class="r">Qtde</th>'+
    '<th class="r">Preço médio</th><th class="r">Total</th><th class="r">% da categoria</th>'+
    '<th class="r">Acumulado</th><th>Classe</th></tr></thead><tbody>';
 its.forEach(function(i){
  h+='<tr class="cl'+i.classe+'"><td>'+i.n+'</td><td>'+i.item+'</td><td class="r">'+
     i.qtd.toLocaleString('pt-BR')+'</td><td class="r">'+mv(i.preco)+'</td>'+
     '<td class="r pos">'+mv(i.total)+'</td><td class="r">'+(100*i.pct).toFixed(2).replace('.',',')+'%</td>'+
     '<td class="r">'+(100*i.acum).toFixed(1).replace('.',',')+'%</td>'+
     '<td><span class="pil '+i.classe+'">'+i.classe+'</span></td></tr>';
 });
 h+='</tbody></table>';
 document.getElementById('cx-corpo').innerHTML=h;
 document.getElementById('cx-fundo').classList.add('on');
}

/* caixa de lancamentos: clicar no numero da conta abre a lista daquele mes */
function abreCaixa(ev,ck,mes,reg){
 if(SOCIOS)return;
 ev.stopPropagation();
 var b=bloco(ENT,reg,mes), its=(b.itens||[]).filter(function(i){return i[0]===ck});
 var tot=its.reduce(function(a,i){return a+i[2]},0);
 var nome=ck.split('|')[1], emp=(ENT==='consol')?'Consolidado':((D.ents[ENT]||{}).nome||ENT);
 var h='<div class="cx-cab"><h4>'+nome+' · '+D.meses_nome[mes]+' · '+emp+'</h4>'+
   '<button class="cx-x" onclick="fechaCaixa()">×</button></div>'+
   '<div class="cx-sub"><span>'+its.length+' LANÇAMENTO(S)</span><b>TOTAL: '+mv(tot)+'</b></div>'+
   '<div class="cx-nota">'+(reg==='comp'
     ?'Lançamentos por competência, pela data de emissão — o mesmo critério da linha.'
     :'Lançamentos pelo caixa, na data em que passaram no extrato — o mesmo critério da linha.')+
   (its.some(function(i){return i[6]})
     ?' <b class="flagtxt">Os lançamentos marcados em amarelo são compras parceladas lançadas '+
      'por inteiro no mês da emissão da nota.</b> A forma de pagamento — parcela e vencimento — '+
      'aparece ao passar o mouse na marca, e o desembolso de cada parcela aparece no Fluxo de '+
      'Caixa na data em que for pago.':'')+'</div>';
 if(!its.length){
  h+='<div class="cx-vazio">Esta linha não tem lançamento detalhado.</div>';
 }else{
  /* vencimento e parcela aparecem sempre que o dado existir, nos dois regimes.
     Quem nao tem e o extrato do Omie, que nao traz vencimento nem parcela — ali
     a coluna simplesmente nao nasce, em vez de nascer vazia. */
  var temVenc=its.some(function(i){return i[7]});
  var temParc=its.some(function(i){return i[8]});
  h+='<table class="cx-tbl"><thead><tr><th>'+(reg==='comp'?'Emissão':'Pagamento')+'</th>'+
     (temVenc?'<th>Vencimento</th>':'')+(temParc?'<th>Parcela</th>':'')+
     '<th>Cliente / fornecedor</th>'+
     '<th>Banco / conta</th><th>Documento</th><th class="r">Valor</th></tr></thead><tbody>';
  its.sort(function(a,b2){return Math.abs(b2[2])-Math.abs(a[2])}).forEach(function(i){
   var av=i[6]?' <span class="flag" title="'+i[6].replace(/"/g,'&quot;')+'">100% na competência</span>':'';
   /* "FALTA NF" e marca que o proprio CSC digita. Em venda de salao, forma de
      pagamento, aporte, conta corrente do grupo e imposto a nota fiscal nao
      existe por natureza — ali a marca vira a origem do numero, que e o que de
      fato lastreia o lancamento. */
   var doc=(i[4]||'').trim(), semNF=(!doc||/^(FALTA NF|SEM NF|-)$/i.test(doc));
   var ori=origemDe(nome);
   var cdoc=semNF?(ori?'<span class="z">'+ori+'</span>':'—'):doc;
   h+='<tr'+(i[6]?' class="flagged"':'')+'><td>'+i[1].slice(0,5)+'</td>'+
      (temVenc?('<td>'+((i[7]||'').slice(0,5)||'—')+'</td>'):'')+
      (temParc?('<td>'+(i[8]||'—')+'</td>'):'')+
      '<td>'+(i[3]||'—')+av+'</td><td>'+(i[5]||'—')+'</td>'+
      '<td>'+cdoc+'</td><td class="r '+(i[2]<0?'neg':'pos')+'">'+mv(i[2])+'</td></tr>';
  });
  h+='</tbody></table>';
 }
 document.getElementById('cx-corpo').innerHTML=h;
 document.getElementById('cx-fundo').classList.add('on');
}
/* categorias em que a nota fiscal nao se aplica: o lastro e outro documento */
var ORIGEM=[[/receita operacional|bar e balc|beach club|couvert|eventos e grupos|ajuste ao total/i,'relatório de vendas'],
 [/cart[ãa]o de (cr[ée]dito|d[ée]bito)|^pix$|dinheiro \(fundo fixo\)|voucher|vale/i,'extrato do adquirente'],
 [/aporte|empr[ée]stimo|financiamento|distribui[çc][ãa]o de lucros/i,'contrato e comprovante'],
 [/conta corrente (boldr|yo|amana|pousada)|transfer[êe]ncia/i,'comprovante de transferência'],
 [/pis|cofins|irpj|csll|icms|iss|simples|das|fgts|inss|taxas distritais/i,'guia de recolhimento'],
 [/sal[áa]rio|folha|f[ée]rias|rescis|13|pr[óo]-labore|diarista|extras e free/i,'folha de pagamento'],
 [/rendimento|juros|tarifa|iof|antecipa/i,'extrato bancário']];
function origemDe(cat){
 for(var i=0;i<ORIGEM.length;i++)if(ORIGEM[i][0].test(cat||''))return ORIGEM[i][1];
 return '';
}
function fechaCaixa(){document.getElementById('cx-fundo').classList.remove('on')}
var AV_SAIDAS=false;
/* total de saidas do mes, somando as empresas da visao: e o denominador do
   "% do gasto" no DFC. Sai dos saldos, que e o mesmo numero da ponte. */
function saidasMes(m){
 var ents=(ENT==='consol')?['boldro','yo']:[ENT], v=0;
 ents.forEach(function(e){var s=((D.ents[e]||{}).saldos||{})[m]; if(s)v+=s.saidas||0});
 return v;
}
function linhaMat(rot,vals,bases,cls,chave,nivel,abreCk,abreReg){
 var t=vals.reduce(function(a,b){return a+b},0);
 /* percentual de gasto so faz sentido em linha de gasto: entrada e saldo
    ficam sem o numero, em vez de mostrar 170% das saidas. */
 if(AV_SAIDAS&&t>=0)bases=null;
 var tb=bases?bases.reduce(function(a,b){return a+b},0):0;
 var o='<tr class="'+(cls||'')+'"'+(chave?' onclick="tog(\''+chave+'\')"':'')+'>'+
   '<td class="l n'+(nivel||0)+'">'+(chave?cv(chave):'')+rot+'</td>';
 /* o mes do clique sai da lista EXIBIDA (abreReg diz qual regime), nao de
    D.meses: com um mes escondido no meio, o clique abria o mes errado. */
 var MSx=mesesDe(abreReg||REG);
 vals.forEach(function(v,i){o+=cel(v,bases?bases[i]:0,null,
   (abreCk?[abreCk,MSx[i],abreReg]:null))});
 return o+cel(t,0,'tt')+'<td class="num avtot">'+(tb?pc(t,tb):'')+'</td></tr>';
}

/* ---- estrutura das duas demonstracoes, com os grupos do nosso plano ---- */
var BLOCOS_DFC=[
 ['(+) Recebimentos',['1','OR']],
 ['(−) Deduções e estornos',['2']],
 ['(−) Custos',['3','4','5']],
 ['(−) Despesas',['6','7','8','9','14']],
 ['(−) IRPJ e CSLL pagos',['IR']],
 ['(±) Resultado financeiro',['10']],
 ['=GERAÇÃO DE CAIXA OPERACIONAL',GRUPOS_OP],
 ['(−) Investimentos',['11']],
 ['(±) Financiamento',['12']],
 ['(±) Não operacional e transferências',['CC','NEUTRO','13']],
 ['*GERAÇÃO DE CAIXA FINAL',GRUPOS_OP.concat(['11','12','CC','NEUTRO','13'])]
];
var BLOCOS_DRE=[
 ['Receita bruta (faturamento)',['FAT']],
 ['(−) Deduções',['2']],
 ['+Receita líquida',['FAT','2']],
 ['(−) CMV',['4']],
 ['+Lucro bruto',['FAT','2','4']],
 ['(−) Despesas variáveis de venda',['3']],
 ['(−) Custos de operação',['5']],
 ['(−) Pessoal operacional',['6']],
 ['(−) Ocupação',['7']],
 ['(−) Administrativas',['8']],
 ['(−) Marketing',['9']],
 ['(−) Entretenimento',['14']],
 ['=EBITDA',['FAT','2','3','4','5','6','7','8','9','14']],
 ['(±) Resultado financeiro',['10']],
 ['+LAIR · lucro antes do imposto',['FAT','2','3','4','5','6','7','8','9','14','10']],
 ['(−) IRPJ e CSLL',['IR']],
 ['*LUCRO LÍQUIDO',['FAT','2','3','4','5','6','7','8','9','14','10','IR']],
 ['§ABAIXO DO EBITDA — CAPEX E NÃO OPERACIONAL',null],
 ['(−) Investimentos (capex)',['11']],
 ['(±) Financiamento',['12']],
 ['(+) Outros recebimentos',['OR']],
 ['(±) Transferências e ajustes',['CC','NEUTRO','13']],
 ['*RESULTADO APÓS INVESTIMENTOS',['FAT','2','3','4','5','6','7','8','9','14','10','IR','11','12','OR','CC','NEUTRO','13']],
 /* 09/11/2026: o bloco de reconciliacao da receita saiu da DRE por decisao do
    Joao, "nao precisa ter isso na DRE". A linha do meio era um RESIDUO
    (faturamento menos grupo 1) com nome que afirmava causa — "ajuste de
    competencia" — sem ninguem ter decomposto os R$ 64.439,71 de setembro.
    Ver 06 Aprendizados/ajuste-de-competencia-da-receita-e-residuo.
    O grupo 1 volta a nao aparecer em linha nenhuma da DRE, e isso e de
    proposito: a receita da DRE e o faturamento pelo mes da venda. A trava
    externa ja isenta o grupo 1 em SO_RECONCILIACAO. */
];

function matriz(reg){
 if(!temDado(ENT))return '<tr><td class="l" colspan="'+(mesesDe(reg).length+2)+'">Sem lançamento no Omie.</td></tr>';
 var MS=mesesDe(reg), bl={}, out='';
 MS.forEach(function(m){bl[m]=bloco(ENT,reg,m)});
 /* a analise vertical e sobre a receita bruta DO MES, nao do periodo */
 var base=MS.map(function(m){return Math.abs(
   (reg==='comp'?soma(ENT,reg,m,['FAT']):saidasMes(m)))||0});
 AV_SAIDAS=(reg==='caixa');
 /* sem receita bruta no mes (a YO nao fatura) nao existe analise vertical: a
    base cairia na soma dos grupos negativos, capex incluido, e a coluna
    continuaria rotulada "AV %". Percentual sobre base inventada e pior que
    percentual nenhum — a coluna sai vazia. */
 var SEM_AV=!base.some(function(x){return x});
 if(SEM_AV)base=MS.map(function(){return 0});
 var ESTR=(reg==='caixa')?BLOCOS_DFC:BLOCOS_DRE;

 if(reg==='caixa')out+=linhaSaldo('ini',MS);
 ESTR.forEach(function(B,bi){
  var rot=B[0], gs=B[1], c0=rot.charAt(0);
  if(c0==='§'){out+='<tr class="sep"><td class="l" colspan="'+(MS.length+2)+'">'+rot.slice(1)+'</td></tr>';return}
  if(c0==='='||c0==='+'||c0==='*'){
   out+=linhaMat(rot.slice(1),MS.map(function(m){return soma(ENT,reg,m,gs)}),base,
                 c0==='='?'ebit':(c0==='*'?'res':'op'),null,0);
   return;
  }
  var k=reg+'|b'+bi, vals=MS.map(function(m){return soma(ENT,reg,m,gs)});
  var vazia=!vals.some(function(v){return v});
  if(vazia&&reg==='caixa')return;                 /* no DFC a linha vazia nao informa nada */
  out+=linhaMat(rot,vals,base,(vazia?'xm lvl0 zero':'xm lvl0'+(ABERTO[k]?' open':'')),
                vazia?null:k,0);
  if(vazia||!ABERTO[k])return;
  /* as contas de um grupo, ordenadas pelo peso no periodo */
  function contasDe(g,nivel){
   var contas={};
   MS.forEach(function(m){Object.keys(bl[m].contas).forEach(function(ck){
    if(ck.split('|')[0]===g)contas[ck]=1})});
   Object.keys(contas).sort(function(a,b){
    var sa=0,sb=0;MS.forEach(function(m){sa+=Math.abs(bl[m].contas[a]||0);sb+=Math.abs(bl[m].contas[b]||0)});
    return sb-sa}).forEach(function(ck){
    var vc=MS.map(function(m){return bl[m].contas[ck]||0});
    /* a conta e a folha: o lancamento abre na caixa, ao clicar no numero */
    out+=linhaMat(ck.split('|')[1],vc,base,'lvl'+nivel,null,nivel,ck,reg);
   });
  }
  /* bloco de um grupo so: o nivel do grupo repetiria o nome do bloco, entao o
     clique vai direto para as contas. Com mais de um grupo o nivel informa. */
  if(gs.length===1){contasDe(gs[0],1);return}
  gs.forEach(function(g){
   var vg=MS.map(function(m){return (bl[m].grupos[g]||0)});
   if(!vg.some(function(v){return v}))return;
   var kg=k+'|g'+g;
   out+=linhaMat(D.grupo_nome[g]||g,vg,base,'lvl1'+(ABERTO[kg]?' open':''),kg,1);
   if(!ABERTO[kg])return;
   contasDe(g,2);
  });
 });
 if(reg==='caixa')out+=linhaSaldo('fim',MS);
 return out;
}

/* saldo abre por empresa e, dentro dela, por conta bancaria */
function linhaSaldo(qual,MS){
 var ents=(ENT==='consol')?['boldro','yo']:[ENT];
 function sal(e,m){var x=((D.ents[e]||{}).saldos||{})[m];return x?x[qual]:0}
 var tot=MS.map(function(m){var v=0;ents.forEach(function(e){v+=sal(e,m)});return v});
 var k='sal|'+qual, o='';
 o+='<tr class="r0'+(ABERTO[k]?' open':'')+'" onclick="tog(\''+k+'\')"><td class="l">'+cv(k)+
    (qual==='ini'?'Saldo inicial':'Saldo final')+'</td>';
 tot.forEach(function(v){o+=cel(v,0)});
 o+=cel(qual==='ini'?tot[0]:tot[tot.length-1],0,'tt')+'<td class="num"></td></tr>';
 if(!ABERTO[k])return o;
 ents.forEach(function(e){
  var ke=k+'|'+e, nome=(D.ents[e]||{}).nome||e;
  o+='<tr class="sub'+(ABERTO[ke]?' open':'')+'" onclick="tog(\''+ke+'\')"><td class="l n1">'+cv(ke)+nome+'</td>';
  MS.forEach(function(m){o+=cel(sal(e,m),0)});
  o+='<td class="num"></td><td class="num"></td></tr>';
  if(!ABERTO[ke])return;
  var ccs={};
  MS.forEach(function(m){var x=((D.ents[e]||{}).saldos||{})[m];
   if(x&&x.contas)Object.keys(x.contas).forEach(function(c){ccs[c]=1})});
  Object.keys(ccs).forEach(function(c){
   o+='<tr class="scc"><td class="l n2">'+c+'</td>';
   MS.forEach(function(m){var x=((D.ents[e]||{}).saldos||{})[m];
    o+=cel(x&&x.contas?(x.contas[c]||0):0,0)});
   o+='<td class="num"></td><td class="num"></td></tr>';
  });
 });
 return o;
}

function pintaRelatorios(){
 ['fc','dre'].forEach(function(t){
  var h=document.getElementById(t+'head'); if(!h)return;
  var th='<th class="l">'+(t==='fc'?'Fluxo de caixa':'Categoria')+'</th>';
  mesesDe(t==='fc'?'caixa':'comp').forEach(function(m){th+='<th>'+D.meses_nome[m]+'</th>'});
  var semAv=(t==='dre')&&!mesesDe('comp').some(function(m){return soma(ENT,'comp',m,['FAT'])});
  h.innerHTML=th+'<th>Total</th><th class="av">'+
    (t==='fc'?'% saídas':(semAv?'—':'AV %'))+'</th>';
 });
 var fc=document.getElementById('fcbody'); if(fc)fc.innerHTML=matriz('caixa');
 var dr=document.getElementById('drebody'); if(dr)dr.innerHTML=matriz('comp');
 /* a nota do teto de CMV: o numero exibido na linha nao e a compra do mes, e
    quem le a DRE tem que ver isso na mesma tela, nao so no rodape da pagina. */
 var na=document.getElementById('dre-ajustes');
 if(na){
  var aj=(D.ajustes||{}).cmv||{}, meta=Math.round(((D.ajustes||{}).cmv_meta||0)*100),
      ms=mesesDe('comp').filter(function(m){return aj[m]}), h='';
  if(ms.length){
   /* a nota fala do que a TELA mostra. Desde 09/11/2026 o teto vale no
      consolidado tambem — o CMV da YO sai da linha e vai para pre-operacao —,
      entao o consolidado fecha no teto e nao ha o que ressalvar ali. A frase
      de divergencia so entra se a vertical da tela REALMENTE sair do teto;
      escrita sem essa trava, ela dizia "aparece em 33,0% ... e nao em 33%". */
   var cmvYo=(D.ajustes||{}).cmv_yo||{};
   var fora=ms.filter(function(m){
    var p=-soma(ENT,'comp',m,['4'])/(soma(ENT,'comp',m,['FAT'])||1)*100;
    return Math.abs(p-meta)>0.1;
   });
   var tit=(ENT==='yo')
    ?'O teto de CMV não se aplica à YO'
    :(fora.length
      ?('O CMV da Boldró está lançado a '+meta+'% — nesta visão a vertical sai disso')
      :('O CMV desta DRE está lançado a '+meta+'% da receita'));
   var corpo='Decisão da diretoria em 07/11/2026. O que a casa <b>comprou</b> de insumo foi: '+
     ms.map(function(m){return D.meses_nome[m]+' <b>'+brl(aj[m].comprado)+'</b> ('+
       pc(aj[m].comprado,soma('boldro','comp',m,['FAT'])||1)+' da receita)'}).join(' · ')+
     '. A diferença é estoque comprado e não consumido dentro do mês — o CMV deste painel é '+
     'compra pela data da nota, não consumo.';
   if(ENT==='yo'){
    corpo='A YO não fatura — quem vende é a Boldró. O teto de '+meta+'% foi aplicado '+
      'à DRE da Boldró; aqui o insumo de pré-operação saiu da linha de CMV e está em '+
      'Investimentos, abaixo do EBITDA.';
   }else if(fora.length){
    corpo+=' <b>Nesta visão o CMV aparece em '+
      fora.map(function(m){return pc(-soma(ENT,'comp',m,['4']),soma(ENT,'comp',m,['FAT'])||1)+
        ' em '+D.meses_nome[m]}).join(' e ')+'</b>. Escolha <b>Boldró</b> no seletor de '+
      'empresa para ver o '+meta+'%.';
   }else if(ENT==='consol'&&Object.keys(cmvYo).length){
    corpo+=' O consolidado também fecha no teto porque o insumo que a YO comprou antes de '+
      'a casa abrir — '+ms.filter(function(m){return cmvYo[m]}).map(function(m){
        return brl(cmvYo[m])+' em '+D.meses_nome[m]}).join(' e ')+' — saiu da linha de CMV '+
      'e está em <b>pré-operação</b>, abaixo do EBITDA: a YO não tem receita para dividir.';
   }
   if(ENT!=='yo')corpo+=' O ajuste está como linha própria dentro do CMV — '+
     ms.map(function(m){return brl(aj[m].ajuste)+' em '+D.meses_nome[m]}).join(' e ')+
     ' —, e na tela o grupo <b>CMV</b> abre para ver lançamento a lançamento. '+
     'Nada disso toca o fluxo de caixa.';
   h='<div class="aviso nota"><h4>'+tit+'</h4><p>'+corpo+'</p></div>';
  }
  na.innerHTML=h;
 }
 var er=auditaTabela('caixa').concat(auditaTabela('comp'));
 var av=document.getElementById('tbl-alerta');
 if(av)av.innerHTML=er.length
  ?'<div class="aviso erro"><h4>A tabela não fecha — não confie nestes números</h4><p>'+
    er.slice(0,8).join('<br>')+(er.length>8?'<br>… mais '+(er.length-8):'')+'</p></div>':'';
 if(er.length&&window.console)console.error('auditoria da tabela:',er);
}

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
   ['Receita no mês',brl(soma(ENT,'comp',MES,['1','OR'])),'não é venda de salão',
    'são reembolsos e outras receitas']
  ].map(card).join('');
  var mx0=document.getElementById('op-mix');
  if(mx0){var ks=Object.keys(ac).sort(function(a,b){return ac[a]-ac[b]}),cor=['#F97316','#0E9F6E','#6366F1','#EAB308'];
   mx0.innerHTML=ks.map(function(c,i){return '<div class="mixrow"><div class="mixlab">'+c+'</div>'+
    '<div class="mixbar"><i style="width:'+(100*ac[c]/tA).toFixed(1)+'%;background:'+cor[i%4]+'"></i></div>'+
    '<div class="mixval num">'+brl(-ac[c])+' · '+pc(ac[c],tA)+'</div></div>'}).join('')}
  return;
 }
 /* mes sem DRE nao tem margem: a receita do grupo 1 e parcial e o custo do mes
    esta em carga. Toda margem daqui seria elogio falso — a mesma razao que ja
    deixa o KPI de margem em branco. Ver 02 Decisoes/mes-parcial-entra-marcado. */
 if(semDre(MES)){
  el.innerHTML='<div class="vazio"><h4>'+D.meses_nome[MES]+' entra só no fluxo de caixa</h4>'+
   '<p>O resultado por competência do mês não está publicado, então nenhuma margem '+
   'sobre a venda tem leitura aqui. Escolha '+D.meses_nome[D.meses[D.meses.length-2]]+
   ' nas pílulas de mês para ver onde vai cada real vendido.</p></div>';
  var mxv=document.getElementById('op-mix'); if(mxv)mxv.innerHTML='';
  return;
 }
 var k=cozinha(MES), A=acumCozinha(), dias=(D.dias||{})[MES]||30;
 /* fixo = custo de casa aberta: NAO entra o variavel de venda, porque ele e o
    divisor do card "por dia de operacao". A sobra, sim, desconta tudo — e com
    isso ela passa a ser o MESMO EBITDA da DRE. Antes dava 20,5% contra 9,5%
    na DRE do mesmo PDF, porque esquecia o grupo 3. */
 var fixo=k.pessoal+k.ocupacao+k.adm+k.mkt+k.operacao;
 var ebitdaOp=k.venda-k.cmv-fixo-k.variaveis;
 /* a base dos percentuais desta secao e a RECEITA BRUTA, a mesma da analise
    vertical da DRE. Com a receita liquida a sobra dava 9,8% e a DRE 9,5% para
    o mesmo valor — dois percentuais para um numero so na mesma pagina.
    Ver 03 Padroes/painel-uma-definicao-por-metrica. */
 var base=soma(ENT,'comp',MES,['FAT'])||k.venda;
 var aj=((D.ajustes||{}).cmv||{})[MES];
 el.innerHTML=[
  ['Insumo de A&B',pc(k.cmv,base),
   aj?(brl(k.cmv)+' lançados no mês'):(brl(k.cmv)+' de compra no mês'),
   aj?('a compra do mês foi '+brl(aj.comprado)+' — o CMV entra a '+
       Math.round((D.ajustes.cmv_meta||0)*100)+'% por decisão da diretoria')
     :'a abertura por cozinha e bar entra quando o insumo deixar de vir num balde só'],
  ['Equipe',pc(k.pessoal,base),brl(k.pessoal)+' entre fixos, diaristas e alojamento',
   'referência: 25% a 32%'],
  ['Custo de casa aberta',brl(fixo/dias),'por dia de operação',
   'sem vender nada, a casa custa isso por dia'],
  (ENT==='boldro'&&k.ocupacao<1000)
    ?['Ocupação',emC('a Boldró não paga arrendamento: o ponto é arrendado pela YO, '+
       'por R$ 25.000 ao mês, e não é rateado. Ver o consolidado.'),'','']
    :['Ocupação',pc(k.ocupacao,base),brl(k.ocupacao)+' de arrendamento',
      ENT==='consol'?'arrendamento do ponto, pago pela YO':'referência: até 10%'],
  ['Atrações e mídia',pc(k.mkt,base),brl(k.mkt)+' em DJ, música e divulgação','referência: 3% a 6%'],
  ['Custo de vender',pc(k.variaveis,base),brl(k.variaveis)+' em comissão e taxa de cartão',
   'sai a cada venda, não com a casa aberta'],
  ['Sobra depois de tudo',pc(ebitdaOp,base),brl(ebitdaOp)+' antes do financeiro',
   'é o EBITDA da DRE']
 ].map(card).join('');

 /* mix cozinha x bar */
 var mx=document.getElementById('op-mix'); if(!mx)return;
 var tot=k.food+k.bar+k.comum;
 if(!tot){mx.innerHTML='';return}
 mx.innerHTML=[['Cozinha',k.food,'#F97316'],['Bar',k.bar,'#0E9F6E'],['Frete e diversos',k.comum,'#6366F1']]
  .map(function(i){return '<div class="mixrow"><div class="mixlab">'+i[0]+'</div>'+
   '<div class="mixbar"><i style="width:'+(100*i[1]/tot).toFixed(1)+'%;background:'+i[2]+'"></i></div>'+
   '<div class="mixval num">'+brl(i[1])+' · '+pc(i[1],tot)+'</div></div>'}).join('')
  /* as barras saem de 'familias', que e a COMPRA pela data da nota e inclui a
     YO — base diferente do CMV exibido na linha de cima, que esta no teto de
     33% e e so da Boldro. Sem este rodape eram tres numeros sem rotulo. */
  +'<p class="repnote">Soma das três famílias: <b>'+brl(tot)+'</b>. É a '+
   '<b>compra de insumo pela data da nota</b>'+(ENT==='consol'?', das duas empresas':'')+
   ', não o CMV da DRE'+(aj?(' — que está lançado a '+
    Math.round((D.ajustes.cmv_meta||0)*100)+'% da receita, '+brl(k.cmv)+' no mês'):'')+'.</p>';
}


/* ---- custo de receber: taxa de cartao e antecipacao ----
   Dado, nao conclusao. A tela mostra a taxa efetiva de cada bandeira, o ticket,
   a participacao de cada meio e a serie diaria da antecipacao contra o saldo. O
   que cortar e ate quando antecipar depende de coisa que o numero nao sabe —
   contrato com a adquirente, o que o cliente usa, compromisso que ainda nao
   virou titulo — entao quem conclui e quem le. */
function txDe(m){
 if(!D.taxas||ENT==='yo')return null;
 return D.taxas[m||MES]||null;
}
function txPc(v){return v.toFixed(2).replace('.',',')+'%'}
/* ---- o faturamento por tres fontes independentes ----
   3LM (o PDV), receita declarada (deduzida do PIS e do COFINS pagos) e Omie
   (pela data do credito no banco). Tres criterios diferentes para o mesmo mes:
   a tabela poe os tres lado a lado e mostra a diferenca. Nao conclui nada —
   dizer por que diferem depende de informacao que o numero nao tem. */
function receita(){
 var el=document.getElementById('vendas'), au=document.getElementById('rec-cruz');
 var R=D.receita&&ENT!=='yo'?D.receita[MES]:null;
 if(el&&!R)el.innerHTML='<div class="vazio"><h4>'+(ENT==='yo'?'A YO não fatura'
   :'Sem relatório de vendas de '+D.meses_nome[MES])+'</h4><p>'+
   (ENT==='yo'?'A venda de salão acontece no CNPJ da Boldró. Troque de empresa no topo.'
             :'A composição vem da extração do 3LM, que não tem API e entra por PDF.')+'</p></div>';
 if(au)au.innerHTML='';
 if(!R)return;

 /* a soma e o ponto: cada linha e um item do PDV e as quatro fecham o bruto.
    Era o pedido da diretoria em 05/11 — deixar a conta visivel, com os %. */
 var OBS={'A&B':'comida e bebida do cardápio, líquido do desconto dado no salão',
  'Taxa de servico':'item do PDV (código 100000), lançado no funcionário 0 SERVICO',
  'Couvert':'dois itens no PDV: *Couvert Artístico e Couvert (99997)',
  'Taxa de rolha':'cobrança de rolha, item do PDV'};
 var h='';
 if(el){
  h='<table class="xtbl soma"><thead><tr><th class="l">Composição da venda</th><th>'+
   D.meses_nome[MES]+'</th><th class="av">% do bruto</th><th class="l">De onde vem</th>'+
   '</tr></thead><tbody>';
  function l(sin,rot,v,obs,cls){
   return '<tr'+(cls?' class="'+cls+'"':'')+'><td class="l"><span class="sin">'+(sin||'')+
    '</span>'+rot+'</td><td class="num">'+(v===null?'—':mv(v))+'</td>'+
    '<td class="av">'+(v===null?'':pc(v,R.recebido))+'</td>'+
    '<td class="l obs">'+(obs||'')+'</td></tr>';
  }
  if(R.abertura){
   R.abertura.forEach(function(a,i){
    h+=l(i?'+':'',(a[0]==='Taxa de servico'?'Taxa de serviço':a[0]),a[1],OBS[a[0]]||'item do 3LM')});
  }else if(R.grupos){
   R.grupos.forEach(function(g,i){h+=l(i?'+':'',g[0],g[1],'grupo do cardápio no 3LM')});
  }
  h+=l('=','<b>Venda bruta</b>',R.recebido,
   R.fonte_3lm==='3LM'?'extração bruta do 3LM — '+(R.itens?R.itens.toLocaleString('pt-BR')+' itens, ':'')+
   'líquido de desconto':'reconstruído: GetNet por data da venda + dinheiro do fundo fixo','res');
  if(R.servico&&R.produtos)
   h+=l('','&nbsp;&nbsp;<i>memo:</i> <b>Venda de cardápio</b> — venda bruta menos taxa de serviço',
        R.produtos,
        'A&amp;B, couvert e rolha. A taxa de serviço é '+
        R.servico_pc.toFixed(2).replace('.',',')+'% sobre esta base','memo');
  if(R.desconto)
   h+=l('','&nbsp;&nbsp;<i>memo:</i> desconto concedido no salão',-R.desconto,
        'já deduzido das linhas acima — não é dedução da DRE','memo');
  if(R.declarada!==null&&R.declarada!==undefined){
   h+=l('','&nbsp;&nbsp;<i>memo:</i> <b>Receita declarada</b> — base das guias do mês',R.declarada,
    'base deduzida de PIS a 0,65% e COFINS a 3,00% — '+pc(R.declarada,R.recebido)+
    ' do que o salão vendeu','memo');
  }
  h+='</tbody></table>'+
   '<p class="repnote"><b>Faturamento extra — aluguel de espaço, evento — não aparece como item '+
   'no 3LM:</b> tudo que está aqui é cardápio, couvert, rolha e serviço. Se houve receita de '+
   'evento no mês, ela não passou pelo PDV e não está nesta conta.</p>';
  el.innerHTML=h;
 }

 /* a divergencia entre os dois relatorios e conferencia: fica na auditoria */
 if(au&&R.divergencia){
  var V=R.divergencia, a='<div class="aviso"><h4>Setembro tem um segundo relatório, e ele dá '+
   mv(V.total)+'<span class="tag">divergência</span></h4><p>O <i>'+V.arquivo+'</i> fica '+
   mv(V.diferenca)+' abaixo da extração bruta do 3LM. A diferença fecha ao centavo em quatro '+
   'linhas:</p><div class="rsm-wrap"><table class="xtbl"><thead><tr><th class="l">Linha</th>'+
   '<th>relatório montado</th><th>3LM bruto</th><th>diferença</th><th class="l">Por quê</th>'+
   '</tr></thead><tbody>';
  V.linhas.forEach(function(x){
   a+='<tr><td class="l">'+x[0]+'</td><td>'+mv(x[1])+'</td><td>'+mv(x[2])+'</td><td>'+
      mv(x[3])+'</td><td class="l obs">'+x[4]+'</td></tr>';
  });
  a+='<tr class="res"><td class="l"><b>Total</b></td><td>'+mv(V.total)+'</td><td>'+
     mv(R.recebido)+'</td><td>'+mv(V.diferenca)+'</td><td class="l obs">o painel usa a '+
     'extração bruta, que é o documento de origem</td></tr></tbody></table></div></div>';
  au.innerHTML=a;
 }
}
/* ---------- exportar PDF ---------------------------------------------------
   Portado do painel modelo em 09/11/2026. O modelo que o Tiago mandou
   como padrao ("quero objetividade ... a turma quer bater o olho e entender
   logo") E a saida desta funcao. Cada pagina CLONA o que ja esta na tela,
   entao o PDF nao tem numero proprio e nao pode divergir do painel.
   A paginacao mede a altura real: bloco que nao cabe vai para a pagina
   seguinte, e tabela longa quebra linha a linha repetindo o cabecalho. */
function pdocTs(){
 var d=new Date(), p=function(n){return (n<10?'0':'')+n};
 return p(d.getDate())+'/'+p(d.getMonth()+1)+'/'+d.getFullYear()+' às '+
        p(d.getHours())+':'+p(d.getMinutes());
}
function pdocBuild(){
 var doc=document.getElementById('pdoc'); if(!doc)return;
 var TS=pdocTs(), ENTL=(ENT==='consol'?'Consolidado':(ENT==='boldro'?'Boldró':'YO Noronha')),
     PER=D.meses_nome[MES]||'';
 var TIT=ENT==='consol'?'Grupo <b>Yó + Boldró</b>'
   :(ENT==='boldro'?'Boldró <b>Praia Empreendimentos</b>':'<b>YO Noronha</b>');
 doc.innerHTML='';
 /* precisa estar renderizado para medir; fica fora da tela enquanto monta */
 doc.style.cssText='display:block;position:absolute;left:-20000px;top:0;width:297mm';

 doc.insertAdjacentHTML('beforeend',
  '<section class="pg capa"><div class="capa-in">'
  +'<div class="marca">Exact <b>BR</b></div>'
  +'<div class="k">Relatório Gerencial</div><h1>'+TIT+'</h1>'
  +'<div class="per">'+PER+'</div>'
  +'<div class="meta"><div><b>'+TS+'</b>data e hora da exportação</div>'
  +'<div><b>'+ENTL+'</b>visão</div>'
  +'<div><b>'+(REG==='comp'?'Competência':'Caixa')+'</b>regime na tela</div>'
  +'<div style="text-align:right"><b>Exact BR</b>Disciplina Gera Lucro</div></div>'
  +'</div></section>');

 function page(tit,sub){
  var sec=document.createElement('section'); sec.className='pg';
  sec.innerHTML='<div class="pg-h"><div><div class="ttl">'+tit+'</div>'
   +(sub?'<div class="sub">'+sub+'</div>':'')+'</div>'
   +'<div class="rt"><b>'+ENTL+'</b><span>'+PER+'</span></div></div>'
   +'<div class="pg-b"></div>'
   +'<div class="pg-f"><span>Exact BR · Relatório gerencial · Grupo Yó / Boldró · '+ENTL+'</span>'
   +'<span>Exportado em '+TS+' · <i class="pn"></i></span></div>';
  doc.appendChild(sec); return sec.querySelector('.pg-b');
 }
 var cabe=function(b){return b.scrollHeight<=b.clientHeight};
 function bloco(tit,sub,nodes){
  var ns=nodes.filter(Boolean); if(!ns.length)return;
  var b=page(tit,sub);
  ns.forEach(function(n){ b.appendChild(n);
   if(!cabe(b)&&b.children.length>1){ b.removeChild(n); b=page(tit,sub+' (continuação)'); b.appendChild(n); } });
 }
 /* tabela longa: quebra linha a linha, repetindo o cabecalho */
 function tabela(src,tit,sub){
  if(!src)return;
  var tbl=src.matches('table')?src:src.querySelector('table');
  if(!tbl||!tbl.tBodies[0])return;
  var rows=[].slice.call(tbl.tBodies[0].rows);
  var molde=function(){ var t=tbl.cloneNode(false);
   if(tbl.tHead)t.appendChild(tbl.tHead.cloneNode(true));
   [].slice.call(tbl.querySelectorAll('colgroup')).forEach(function(c){t.appendChild(c.cloneNode(true))});
   t.appendChild(document.createElement('tbody')); return t; };
  var b=page(tit,sub), t=molde(); b.appendChild(t); var n=0;
  rows.forEach(function(r){ t.tBodies[0].appendChild(r.cloneNode(true)); n++;
   if(!cabe(b)&&n>1){ t.tBodies[0].removeChild(t.tBodies[0].lastChild);
    b=page(tit,sub+' (continuação)'); t=molde(); b.appendChild(t);
    t.tBodies[0].appendChild(r.cloneNode(true)); n=1; } });
 }
 var cl=function(sel){var e=document.querySelector(sel);return e?e.cloneNode(true):null};
 var vz=function(sel){var e=document.querySelector(sel);
  return e&&e.innerHTML.trim()?e.cloneNode(true):null};

 bloco('Resumo do período','Os números do período em um olhar',[cl('#kpis')]);
 /* o titulo do bloco segue o REGIME da tela, como o titulo dentro da ponte:
    com REG=comp a pagina dizia "Ponte do caixa" e o desenho dizia "Ponte do
    resultado" — dois nomes para a mesma coisa na mesma folha. */
 bloco(REG==='comp'?'Ponte do resultado':'Ponte do caixa',
       REG==='comp'?'Receita bruta → deduções → custos → despesas → EBITDA'
                   :'Saldo inicial → entradas → saídas → saldo final',
       [cl('.waterfall')]);
 tabela(document.querySelector('#rep-dre table'),'DRE por categoria',
        'Resultado por competência, pela data de emissão dos documentos');
 bloco('A nota da DRE','O que o número do CMV mostra, e o que a casa comprou',
       [vz('#dre-ajustes')]);
 /* o DFC do PDF sai com TODAS as saidas abertas, conta a conta. Reusa o
    proprio renderizador em vez de montar outra tabela — duas tabelas com a
    mesma funcao divergem na primeira mudanca. */
 var _ab=ABERTO; ABERTO={};
 Object.keys(_ab).forEach(function(k){ABERTO[k]=_ab[k]});
 BLOCOS_DFC.forEach(function(B,bi){
  if('§=+*'.indexOf(B[0].charAt(0))>=0)return;
  ABERTO['caixa|b'+bi]=1;
  B[1].forEach(function(g){ABERTO['caixa|b'+bi+'|g'+g]=1});
 });
 var _fc=document.getElementById('fcbody');
 if(_fc)_fc.innerHTML=matriz('caixa');
 tabela(document.querySelector('#rep-fc table'),'Fluxo de caixa por categoria',
        'Todas as saídas abertas conta a conta · % sobre o total de saídas do mês');
 ABERTO=_ab; if(_fc)_fc.innerHTML=matriz('caixa');
 bloco('Composição das saídas','Todas as saídas do período, agrupadas',[cl('.pz-grid')]);
 bloco('Onde vai cada real vendido','Insumo, equipe, casa e atrações',
       [vz('#op-kpis'),vz('#op-mix')]);
 bloco('Quando a casa vende','Venda por dia da semana e por turno',[vz('#v-dia'),vz('#v-mix')]);
 bloco('Custo de receber','Taxa por bandeira, venda a venda, e a antecipação',
       [vz('#tx-kpis'),vz('#tx-tab')]);
 /* volta ao PDF em 09/11/2026 sem o #rec-cruz: o Tiago queria fora a
    divergencia entre relatorios, nao a composicao — e com a ABC unificada a
    divergencia nem existe mais. O relatorio vai a investidores. */
 bloco('Composição da venda','O que foi vendido e como o cliente pagou',[vz('#vendas')]);
 bloco('Ressalvas','O que o número não diz sozinho',[cl('.disc')]);

 /* trava: bloco que ainda passar da pagina reduz ate caber, em vez de cortar */
 [].slice.call(doc.querySelectorAll('.pg-b')).forEach(function(b){
  if(b.scrollHeight<=b.clientHeight+1)return;
  var k=Math.max(.52,(b.clientHeight-2)/b.scrollHeight);
  var dentro=document.createElement('div');
  while(b.firstChild)dentro.appendChild(b.firstChild);
  dentro.style.cssText='transform-origin:top left;transform:scale('+k.toFixed(3)+
   ');width:'+(100/k).toFixed(2)+'%';
  b.appendChild(dentro);
 });
 var tot=doc.querySelectorAll('.pg').length;
 [].slice.call(doc.querySelectorAll('.pg')).forEach(function(p,i){
  var pn=p.querySelector('.pn'); if(pn)pn.textContent='página '+(i+1)+' de '+tot; });
 doc.style.cssText='';   /* volta a ficar escondido na tela */
}
function exportPDF(){ pdocBuild(); window.print(); }
addEventListener('beforeprint',function(){
 var d=document.getElementById('pdoc'); if(d&&!d.children.length)pdocBuild(); });
addEventListener('afterprint',function(){
 var d=document.getElementById('pdoc'); if(d)d.innerHTML=''; });

function render(){
 var e=E();
 document.getElementById('heroTitle').innerHTML=temDado(ENT)
  ? (SOCIOS?'Visão dos <b>sócios</b>':(fase(ENT)==='pre_operacao'
     ?'Implantação em <b>'+D.meses_nome[MES]+'</b>':'A casa em <b>'+D.meses_nome[MES]+'</b>'))
  : '<b>'+e.nome+'</b> — aguardando carga';
 var sl=document.getElementById('selo'); if(sl)sl.textContent=D.gerado;
 document.getElementById('heroCnpj').textContent=e.nome+' · '+(e.cnpj?'CNPJ '+e.cnpj:'')+
  (e.conta?' · '+e.conta:'');
 var pp=passosPonte();
 document.getElementById('wf').innerHTML=ponteSVG();
 document.getElementById('wfTitle').textContent=
  (REG==='comp'?'Ponte do resultado':'Ponte do caixa')+' · '+D.meses_nome[MES];
 document.getElementById('wfHint').textContent=
  ((pp||[]).map(function(x){return x[0]}).join(' → '))
  ||(REG==='comp'?'receita → deduções → custos → despesas → EBITDA':'saldo inicial → geração operacional → investimentos → financiamento → saldo final');
 /* os rotulos dos passos passaram para DENTRO do svg em 06/11/2026, junto das
    barras: eixo em HTML ao lado de desenho em SVG desalinha sozinho. */
 document.getElementById('wfX').innerHTML='';
 document.getElementById('kpis').innerHTML=kpis();
 operacao(); pizza(); custoReceber(); receita();
 pintaRelatorios(); vendasBloco();
}
document.getElementById('mespills').innerHTML=D.meses.map(function(m){
 return '<button data-m="'+m+'" class="'+(m===MES?'on':'')+(parcial(m)?' parc':'')+
  '" onclick="setMes(\''+m+'\')" title="'+(parcial(m)?'mês parcial, ainda em carga':'')+'">'+
  D.meses_nome[m]+(parcial(m)?' <i>parcial</i>':'')+'</button>'}).join('');
window.addEventListener('scroll',function(){
 var y=scrollY+90,at='geral';
 document.querySelectorAll('section,header').forEach(function(s){if(s.offsetTop<=y)at=s.id});
 document.querySelectorAll('.nav-links a').forEach(function(a){
  a.classList.toggle('on',a.getAttribute('href')==='#'+at)});
});
render();
"""

NAV_LINKS = ('<a href="#geral" class="on">Visão geral</a>'
             '<a href="#relatorios">DRE e DFC</a>'
             '<a href="#venda-dia">Venda por dia</a>'
             '<a href="#venda-mix">Curva e mix</a>'
             '<a href="#operacao">Operação</a>'
             '<a href="#auditoria">Auditoria</a>'
             '<a href="#custo-receber">Custo de receber</a>'
             '<a href="#vendas-sec">Composição</a>'
             # 09/11/2026: simulador fora da nav por decisao do Joao, "remova o
             # simulador por hora". gera_simulador.py continua no repo; devolver
             # o link e desfazer esta linha e regerar a pagina dele.
             )

ENTSW = """<div class="entsw" id="entsw">
<button data-ent="consol" class="on" onclick="setEntity('consol')">Consolidado</button>
<button data-ent="boldro" onclick="setEntity('boldro')">Boldró</button>
<button data-ent="yo" onclick="setEntity('yo')">YO</button>
<a href="socios.html">Sócios</a>
</div>"""
ENTSW_SOC = """<div class="entsw" id="entsw">
<button data-ent="consol" class="on" onclick="setEntity('consol')">Consolidado</button>
<button data-ent="boldro" onclick="setEntity('boldro')">Boldró</button>
<button data-ent="yo" onclick="setEntity('yo')">YO</button>
<a href="index.html" title="Abre o painel completo de controladoria">Controladoria</a>
</div>"""

def brlpt(v):
    return 'R$ ' + '{:,.2f}'.format(v).replace(',', '@').replace('.', ',').replace('@', '.')


def ressalva():
    """Monta a ressalva do rodape A PARTIR DO D, nunca como texto fixo.

    Em 09/11/2026 a varredura pegou o rodape afirmando EBITDA consolidado de
    R$ -90.393,73 e CMV de 53,8% com a tabela logo acima mostrando +43.295,74 e
    -39,6%: eram numeros de 06/11 que ficaram no texto quando a base andou. Texto
    fixo sobre numero que muda e divergencia garantida — ver
    03 Padroes/ressalva-nao-pode-afirmar-mais-que-a-base.
    """
    EB = ['FAT', '2', '3', '4', '5', '6', '7', '8', '9', '14']
    def grp(emp, mes, k):
        return ((D['ents'][emp]['comp'].get(mes) or {}).get('grupos') or {}).get(k, 0)
    def soma(mes, ks):
        return round(sum(grp(e, mes, k) for e in ('boldro', 'yo') for k in ks), 2)
    def pct(v, b):
        return ('%.1f%%' % (v / b * 100)).replace('.', ',') if b else '—'

    # o que o painel ignorou da base, e por que. Sem isso quem conferir a DRE
    # do Omie contra este relatorio acha um buraco de R$ 12 mil sem explicacao.
    ig = D.get('ignorado') or {}
    bloco_dup = ''
    # DESLIGADO por decisao do Joao em 09/11/2026 — ver comentario acima.
    # Trocar para `if ig.get('n'):` devolve o paragrafo.
    if False and ig.get('n'):
        bloco_dup = (
            '<b>Este relat&oacute;rio ignora %d t&iacute;tulos de R$ %s que est&atilde;o na base e s&atilde;o '
            'duplicidade.</b> Em 09/11/2026 a taxa de cart&atilde;o de agosto e setembro foi '
            'relan&ccedil;ada venda a venda na conta "Taxa de cart&atilde;o cr&eacute;dito" (2.05.99), '
            'sendo que o mesmo custo j&aacute; estava lan&ccedil;ado desde 15/10 na conta "Taxas de '
            'cart&atilde;o" (2.02.01), de forma consolidada — R$ 2.009,99 em agosto e '
            'R$ 10.451,57 em setembro. Mantivemos o lan&ccedil;amento original e desprezamos o '
            'novo. <b>A DRE do Omie vai mostrar esse custo em dobro at&eacute; o CSC excluir '
            'uma das duas s&eacute;ries</b>; outubro e novembro n&atilde;o t&ecirc;m duplicidade, porque '
            'n&atilde;o havia lan&ccedil;amento anterior. '
            % (ig['n'], brlpt(ig['valor']).replace('R$ ', '')))

    # IRPJ/CSLL e trimestral: o painel rateia pela receita, o Omie nao.
    # Diferenca de CRITERIO tem de estar escrita, senao parece erro de conta.
    bloco_rat = ''
    for r in ((D.get('ajustes') or {}).get('rateio_ir') or []):
        por = ' e '.join('%s em %s' % (brlpt(abs(v)), D['meses_nome'][m].replace('/26', ''))
                         for m, v in sorted(r['por_mes'].items()))
        bloco_rat += (
            '<b>IRPJ e CSLL s&atilde;o apurados por trimestre</b> e est&atilde;o lan&ccedil;ados no Omie '
            'no fechamento do trimestre, junto com a guia. Nesta DRE mensal o tributo '
            'acompanha a receita que o gerou: os %s do trimestre foram rateados pela '
            'receita bruta de cada m&ecirc;s — %s. Multa e juros de R$ %s, por atraso no '
            'pagamento da 1&ordf; quota, ficam inteiros no m&ecirc;s de fechamento, por serem '
            'penalidade e n&atilde;o imposto sobre a receita do m&ecirc;s. '
            % (brlpt(abs(r['tributo'])), por,
               ('%.2f' % r['multa_juros']).replace('.', ',')))

    MESES = [m for m in D['meses'] if m not in (D.get('sem_dre') or [])]
    ult = MESES[-1]
    fat = soma(ult, ['FAT'])
    aju = D.get('ajustes') or {}
    teto = int(round((aju.get('cmv_meta') or 0) * 100))
    cmv = aju.get('cmv') or {}

    # receita bruta mes a mes, do proprio D
    rec = ' e '.join('%s em %s' % (brlpt((D['receita'][m] or {}).get('recebido') or 0),
                                   D['meses_nome'][m].replace('/26', ''))
                     for m in MESES if (D.get('receita') or {}).get(m))

    # o teto de CMV, mes a mes, com a compra real
    if cmv:
        linhas = '; '.join('%s: compra de %s (%s da receita) e CMV exibido de %s'
                           % (D['meses_nome'][m], brlpt(cmv[m]['comprado']),
                              pct(cmv[m]['comprado'],
                                  (D['receita'].get(m) or {}).get('recebido') or 0),
                              brlpt(cmv[m]['exibido']))
                           for m in sorted(cmv))
        bloco_cmv = (
            '<b>O CMV da DRE est&aacute; lan&ccedil;ado a %d%% da receita</b>, por decis&atilde;o '
            'da diretoria em 07/11/2026, e n&atilde;o pela compra do m&ecirc;s. %s. '
            'A diferen&ccedil;a &eacute; estoque comprado e n&atilde;o consumido dentro do m&ecirc;s: '
            'o CMV deste painel &eacute; <b>compra pela data da nota, n&atilde;o consumo</b>, '
            'e agosto comprou o estoque de abertura da casa. O ajuste aparece como '
            'linha pr&oacute;pria dentro do CMV, clic&aacute;vel, e n&atilde;o toca o fluxo de caixa. ' % (teto, linhas))
    else:
        bloco_cmv = ''

    # IRPJ/CSLL: so o que esta na base
    ir = soma(ult, ['IR'])
    bloco_ir = ('<b>IRPJ e CSLL de %s somam %s</b> e entram abaixo do EBITDA, entre o LAIR '
                'e o lucro l&iacute;quido — imposto sobre o lucro n&atilde;o &eacute; dedu&ccedil;&atilde;o de venda. '
                'S&atilde;o t&iacute;tulos lan&ccedil;ados pelo CSC em 06/11/2026, com compet&ecirc;ncia declarada '
                'na observa&ccedil;&atilde;o, e estavam <b>em aberto</b> na leitura desta p&aacute;gina. '
                'N&atilde;o h&aacute; provis&atilde;o calculada por al&iacute;quota presumida: o painel s&oacute; mostra '
                'tributo que existe como t&iacute;tulo. '
                % (D['meses_nome'][ult], brlpt(-ir))) if ir else (
                'N&atilde;o h&aacute; IRPJ nem CSLL lan&ccedil;ado na base, e o resultado est&aacute; melhor do '
                'que ser&aacute; enquanto isso n&atilde;o entrar. ')

    # outubro no caixa: a populacao que a COLUNA mostra, nao a da conciliacao
    fora = [m for m in D['meses'] if m in (D.get('sem_dre') or [])]
    bloco_out = ''
    for m in fora:
        q = []
        for emp, nome in (('boldro', 'Boldr&oacute;'), ('yo', 'Y&oacute;')):
            it = ((D['ents'][emp]['caixa'].get(m) or {}).get('itens') or [])
            dias = len({i[1] for i in it if len(i) > 1 and i[1]})
            q.append('%d lan&ccedil;amentos em %d dias na %s' % (len(it), dias, nome))
        bloco_out += ('<b>%s entra apenas no fluxo de caixa</b>: %s. O resultado por '
                      'compet&ecirc;ncia do m&ecirc;s entra quando a carga e a concilia&ccedil;&atilde;o fecharem. '
                      % (D['meses_nome'][m], ' e '.join(q)))

    dias_ago = (D.get('dias') or {}).get(MESES[0])
    return (
        'Relat&oacute;rio gerencial &middot; Grupo Y&oacute; / Boldr&oacute;. Resultado apurado por '
        'compet&ecirc;ncia, pela data de emiss&atilde;o dos documentos; fluxo de caixa apurado pela '
        'movimenta&ccedil;&atilde;o banc&aacute;ria. O <b>movimento</b> est&aacute; conferido contra o extrato de '
        'cada empresa — Santander 13002614-6 na Boldr&oacute;, Bradesco mais aplica&ccedil;&atilde;o e '
        'Mercado Pago na Y&oacute;. O <b>saldo</b> n&atilde;o: a conta corrente da Boldr&oacute; &eacute; varrida '
        'para a ContaMax todo dia, a ContaMax n&atilde;o tem extrato pr&oacute;prio e o saldo dela &eacute; '
        'derivado do movimento. Adiantamento entre empresas &eacute; transfer&ecirc;ncia, '
        'n&atilde;o custo, e fica fora do resultado; no consolidado o par '
        'Y&oacute;&harr;Boldr&oacute; &eacute; eliminado e os demais permanecem como valor a reembolsar. '
        'A receita bruta &eacute; o faturamento pelo m&ecirc;s da venda e vem da extra&ccedil;&atilde;o bruta do '
        '3LM — relat&oacute;rio "Vendas Por Funcion&aacute;rio", m&ecirc;s inteiro numa extra&ccedil;&atilde;o s&oacute;, '
        'l&iacute;quido do desconto concedido no sal&atilde;o: %s. Agosto foi retificado em '
        '04/11/2026: at&eacute; ent&atilde;o era reconstru&iacute;do do extrato da GetNet mais o fundo fixo '
        '(R$ 191.290,32) e passou a R$ 163.548,50 — &eacute; por isso que a abertura por forma '
        'de pagamento do m&ecirc;s traz uma linha de ajuste ao total do 3LM. Setembro tem um '
        'segundo relat&oacute;rio, montado pela diretoria em 02/10, que d&aacute; R$ 1.047.949,04; a '
        'diferen&ccedil;a de R$ 11.035,23 est&aacute; decomposta nas ressalvas, e &eacute; esse segundo '
        'relat&oacute;rio que alimenta a venda por dia da semana. A venda por dia usa <b>dias de '
        'opera&ccedil;&atilde;o</b>, n&atilde;o dias do calend&aacute;rio: a casa abriu em 18/08 e agosto tem %s '
        'dias com venda. A taxa de cart&atilde;o &eacute; custo e aparece acima do EBITDA, n&atilde;o '
        'deduzida da receita. %s%s'
        '<b>Em 05/11/2026 a conta de luz passou a ter compet&ecirc;ncia no m&ecirc;s anterior ao '
        'pagamento</b> — a fatura paga em julho &eacute; o consumo de junho —, crit&eacute;rio definido '
        'pela diretoria e aplicado &agrave;s oito faturas da Y&oacute;. '
        '<b>Em 09/11/2026 agosto e setembro foram retificados</b>, a pedido da diretoria: '
        'nove t&iacute;tulos de R$ 62.178,27 cuja observa&ccedil;&atilde;o declara compet&ecirc;ncia de setembro '
        'estavam com emiss&atilde;o em outubro e voltaram para setembro — PIS, COFINS, ICMS, '
        'comiss&atilde;o do chef, pontua&ccedil;&atilde;o vari&aacute;vel da diretoria, honor&aacute;rios e telefonia; '
        '"Prestadores de servi&ccedil;os gerais" e "Frete de materiais de opera&ccedil;&atilde;o" passaram a '
        'entrar em Investimentos, mantendo o nome da conta, para serem reclassificados '
        'depois; e R$ 11.174,00 de aluguel que era aloja&shy;mento sa&iacute;ram de Ocupa&ccedil;&atilde;o para '
        'Alojamento em outubro. <b>Na mesma data, 75 t&iacute;tulos das duas empresas foram para '
        'a compet&ecirc;ncia que a pr&oacute;pria observa&ccedil;&atilde;o declara</b> — estavam com emiss&atilde;o na data '
        'do pagamento. Os maiores grupos: 23 comiss&otilde;es sobre vendas de agosto que estavam '
        'em setembro, 14 t&iacute;tulos da Y&oacute; de compet&ecirc;ncia julho que estavam em agosto e 12 da '
        'Y&oacute; de setembro que estavam em outubro. Agosto piorou R$ 21.289,68 na Boldr&oacute; e '
        'melhorou R$ 39.091,05 na Y&oacute;; setembro melhorou R$ 15.159,27 na Boldr&oacute;, e o que '
        'entrou nele pela Y&oacute; &eacute; obra (R$ 19.899,64), que fica abaixo do EBITDA. '
        'Parte desse custo tem compet&ecirc;ncia de <b>junho e julho</b> e por isso deixou de '
        'aparecer: o painel come&ccedil;a em agosto. Cinco t&iacute;tulos ficaram de fora de prop&oacute;sito — '
        'a energia e a &aacute;gua da Y&oacute;, que seguem o crit&eacute;rio de compet&ecirc;ncia no m&ecirc;s anterior ao '
        'pagamento, e um t&iacute;tulo cuja observa&ccedil;&atilde;o declara compet&ecirc;ncia de 2025. %s'
        '<b>O efeito das retifica&ccedil;&otilde;es de 09/11 contra o relat&oacute;rio anterior, de 06/11:</b> '
        'o EBITDA consolidado de agosto saiu de R$ -505.214,12 para %s e o de setembro de '
        'R$ -311,14 para %s; o lucro l&iacute;quido de setembro saiu de R$ -7.813,62 para %s. '
        'Quem guardou o relat&oacute;rio de 06/11 vai encontrar essa diferen&ccedil;a, e ela &eacute; a soma '
        'das linhas acima. '
        '%s%s'
        'Dados lidos da API do Omie em %s.'
        % (rec, dias_ago, bloco_cmv, bloco_ir, bloco_out,
           brlpt(soma(MESES[0], EB)), brlpt(soma(ult, EB)),
           brlpt(soma(ult, EB + ['10', 'IR'])), bloco_dup, bloco_rat, D['gerado']))


SEC_REL = """<section id="relatorios"><div class="wrap">
<div class="sec-head"><div class="k">Relatório detalhado</div>
<h2>Tabelas por categoria <span class="light">— grupo e conta</span></h2>
<p class="lede">O mesmo número de duas maneiras: por competência, como entra na DRE; e pelo caixa, como saiu do extrato. Clique no grupo para abrir as contas e na conta para abrir os lançamentos.</p></div>
<h3 class="rep-t">DRE (competência)</h3>
<div id="rep-dre" class="repwrap on"><table class="xtbl mat dre"><thead><tr id="drehead"></tr></thead><tbody id="drebody"></tbody></table>
<div id="tbl-alerta"></div>
<div id="dre-ajustes"></div>
<p class="repnote"><b>A receita bruta é o faturamento do mês da venda, não o crédito no banco.</b> Clique nela para abrir por forma de pagamento, e no número de cada forma para ver dia a dia o que foi vendido. Nos dois meses ela vem da extração bruta do 3LM — R$ 163.548,50 em agosto e R$ 1.058.984,27 em setembro — e abre em A&amp;B, taxa de serviço, couvert e taxa de rolha, mais a forma de pagamento reconstruída do Extrato de Vendas Detalhado da GetNet.  Competência pela data de emissão do título, mês a mês. Clique no grupo para abrir as contas e na conta para abrir os lançamentos. A conta corrente com partes relacionadas não entra no resultado.</p></div>


<h3 class="rep-t">Fluxo de caixa (DFC)</h3>
<div id="rep-fc" class="repwrap on"><table class="xtbl mat dfc"><thead><tr id="fchead"></tr></thead><tbody id="fcbody"></tbody></table>
<p class="repnote">Demonstração do fluxo de caixa pelo método direto, a partir da movimentação das contas no Omie. Clique na linha com seta para abrir o nível de baixo, e <b>clique em qualquer número para abrir a caixa com os lançamentos</b> daquela conta naquele mês. O saldo abre por empresa e por conta bancária.</p></div>
</div>
</div></section>
"""


SEC_TX = """<section id="custo-receber"><div class="wrap">
<div class="sec-head"><div class="k">Custo de receber</div>
<h2>Quanto custa <span class="light">receber do cliente</span></h2>
<p class="lede">A taxa efetiva de cada bandeira, venda a venda, pelo Extrato de Vendas Detalhado da GetNet — e o que a antecipação cobrou. Dado, não conclusão: o que negociar e até quando antecipar depende de contrato e de compromisso que o número não conhece.</p></div>
<div class="kpis" id="tx-kpis" style="margin:0"></div>
<div style="height:26px"></div>
<div id="tx-tab"></div>
</div></section>"""

SEC_DIA = """<section id="venda-dia"><div class="wrap">
<div class="sec-head"><div class="k">Venda por dia</div>
<h2>Quando a casa <span class="light">vende</span></h2>
<p class="lede">Dia da semana e dia a dia, do relatório mensal do 3LM — que não tem API e entra por PDF.</p></div>
<div id="v-dia"></div>
</div></section>

"""

SEC_MIX = """<section id="venda-mix" class="sec-alt"><div class="wrap">
<div class="sec-head"><div class="k">Curva e mix</div>
<h2>O que vende <span class="light">e como o cliente paga</span></h2>
<p class="lede">Curva ABC por categoria do cardápio, forma de pagamento venda a venda e a divisão do faturamento por horário.</p></div>
<div id="v-mix"></div>
</div></section>

"""

SEC_ANO = """<section id="vendas-sec"><div class="wrap">
<div class="sec-head"><div class="k">Composição da venda</div>
<h2>O que o salão <span class="light">vendeu</span></h2>
<p class="lede">A conta fechada do mês: o que o PDV registrou, item por item, somando até o faturamento bruto.</p></div>
<div id="vendas"></div>
</div></section>

"""

SEC_AUD = """<section id="auditoria" class="sec-alt"><div class="wrap">
<div class="sec-head"><div class="k">Auditoria</div>
<h2>O que não bate <span class="light">e por quê</span></h2>
<p class="lede">Papel de trabalho, não leitura gerencial: a abertura da venda do mês item a item e a diferença entre os dois relatórios de vendas. Está aqui para quem precisa auditar o número — o painel acima já usa a conclusão.</p></div>
<details class="ress"><summary><b>Abrir o dash de auditoria</b> — abertura da venda e divergência entre relatórios<span class="chev">▼</span></summary>
<div class="ressin">
<div id="rec-cruz"></div>
</div></details>
</div></section>
"""




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
<div class="regsw" id="regsw"><span class="reglab">Ver a ponte do topo por:</span>
<button data-r="caixa" class="on" onclick="setRegime('caixa')">Caixa</button>
<button data-r="comp" onclick="setRegime('comp')">Competência</button><span class="regnota">os indicadores e as tabelas abaixo não mudam com este botão: a DRE é sempre por competência e o DFC sempre pelo caixa</span></div>
<div class="waterfall">
<div class="wf-head"><span class="t" id="wfTitle">Ponte do caixa</span>
<span class="h" id="wfHint">Saldo inicial → geração de caixa operacional → investimentos → financiamento → saldo final</span></div>
<svg id="wf" viewBox="0 0 1080 236"></svg>
<div class="wf-x" id="wfX"></div>
</div>
</div></header>
<div class="wrap"><div class="kpis" id="kpis"></div></div>

%s
%s

<section id="operacao" class="sec-alt"><div class="wrap">
<div class="sec-head"><div class="k">Operação</div>
<h2>Onde vai <span class="light">cada real vendido</span></h2>
<p class="lede">Para onde vai cada real que entra: insumo, equipe, casa e atrações. O custo de casa aberta é quanto o dia custa antes de vender o primeiro prato.</p></div>
<div class="kpis" id="op-kpis" style="margin:0"></div>
<div style="height:30px"></div>
<h3 style="font-family:'Plus Jakarta Sans';font-weight:700;font-size:17px;margin-bottom:14px">Composição <span class="light">do que saiu</span></h3>
<div class="pz-grid" style="margin-bottom:30px">
<div class="pz-chart"><svg id="pzSvg" viewBox="0 0 320 320" style="width:100%%;height:auto;display:block"></svg>
<div class="pz-mid"><div class="pz-t">Total que saiu</div><b id="pzTot">—</b></div></div>
<div class="pz-leg" id="pzLeg"></div>
</div>
<div id="op-mix"></div>
<p class="repnote">Sem integração com o PDV não há ticket médio, número de couverts nem venda por canal — salão, bar, beach club e day use vivem no 3LM. O que dá para medir pelo financeiro é o <b>mix de compra</b>: quanto do insumo foi para a cozinha e quanto foi para o bar.</p>
</div></section>


%s
%s

<div class="pdoc" id="pdoc"></div>
<button class="pdfbt" onclick="exportPDF()" title="Monta o relatório em páginas A4 deitadas e abre a caixa de impressão (Salvar como PDF)">&#8681; Relatório em PDF</button>

<div id="cx-fundo" class="cx-fundo" onclick="if(event.target===this)fechaCaixa()">
<div class="cx" id="cx-corpo"></div></div>

<footer class="foot"><div class="wrap"><div class="fg">
<div><div class="sig">João Victor Andrade de Souza</div><div class="r">Sócio-fundador · Exact BR</div></div>
<div style="text-align:right"><div class="r" style="margin-bottom:4px">Disciplina Gera Lucro</div>
<div style="font-family:'Plus Jakarta Sans';font-size:13px;font-weight:500;color:rgba(255,255,255,.85)">Exact BR · Recife — PE</div></div>
</div>
<p class="disc">%s</p>
</div></footer>

<script>const D=%s;var SOCIOS=%s;%s</script>
</body></html>""" % (
        'Sócios · ' if socios else '',
        CSS,
        NAV_LINKS,
        ENTSW_SOC if socios else ENTSW,
        'Visão dos sócios · 2026' if socios else 'Fluxo de Caixa &amp; DRE Gerencial · 2026',
        SEC_REL,
        SEC_TX + SEC_DIA + SEC_MIX,
        SEC_AUD + SEC_ANO,
        '',
        ressalva(),
        json.dumps(D, ensure_ascii=False),
        'true' if socios else 'false',
        JS)


if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    # a copia do JSON ao lado da pagina tem que ser a MESMA que gerou a pagina:
    # uma copia velha aqui ja me fez diffar o painel novo contra o painel novo e
    # concluir "delta zero". Escrever sempre, junto.
    import shutil
    shutil.copyfile(os.path.join(BASE, 'dados_painel.json'),
                    os.path.join(d, 'dados_painel.json'))
    for nome, soc in (('index.html', False), ('socios.html', True)):
        p = os.path.join(d, nome)
        open(p, 'w').write(pagina(soc))
        print('gerado %s (%.0f KB)' % (nome, os.path.getsize(p) / 1024))
