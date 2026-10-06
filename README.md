# Painel Yó / Boldró

Painel gerencial do grupo Yó / Boldró (Fernando de Noronha), no mesmo esqueleto do painel
Amana/Topázio — nav fixa, cascata da DRE no hero, indicadores, evolução, tabelas e ressalvas —
com os KPIs trocados: lá é pousada (serviço), aqui é restaurante e beach club (comércio de A&B).

- **Boldró**: dados reais, vindos da API do Omie (títulos por competência + extrato do Santander).
- **YO**: ainda sem lançamento no Omie; os números mostrados vêm da conciliação do CSC e estão
  marcados como tal.

## Como atualizar

```
python3 "Claude VS/omie-boldro/dados_painel.py"   # lê o Omie e monta dados_boldro.json
python3 gera_painel.py                            # gera o index.html
git commit -am "mes X" && git push                # publica no GitHub Pages
```

## Indicadores

Food cost (CMV sobre receita), prime cost (CMV + pessoal), custo de pessoal, margem EBITDA,
caixa e exposição com partes relacionadas. As referências de mercado ao lado de cada indicador
são escala, não meta aprovada.

## Ressalvas da versão 1

1. A receita está pelo **líquido da GetNet** — receita bruta e taxa de cartão ainda não existem na base.
2. O universo é o que **passou pelo banco** em agosto e setembro, então a margem aparece alta demais.
3. Não há abertura por canal: salão, bar, beach club e eventos vivem no PDV (3LM), sem integração.
