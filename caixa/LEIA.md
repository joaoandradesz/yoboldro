# Dashboard de caixa · Boldró · YO Noronha · Consolidado

Publicado em **joaoandradesz.github.io/yoboldro/caixa.html**.
Adaptado de `painel-amanatopazio/caixa`. Posição de caixa e compromissos, com
seletor de período e clique até o título.

## Atualizar (segunda e sexta)

```
sh caixa/atualiza.sh
```

Lê o Omie das duas empresas, monta o `caixa.html`, commita, publica e confere
se a página responde 200. A tela carimba a data e a hora da geração no topo.

## O que este painel declara, e por que

**Cobertura de lançamento: medida a cada edição, impressa no rodapé.** Do
dinheiro que saiu do banco num período, quanto já tinha título lançado no Omie
na data de corte. Rode o backtest antes de publicar:

```
python3 ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude\ VS/omie-boldro/backtest_cobertura.py
```

Ele grava `backtest.json`, que o `gera_dash.py` lê e transforma na nota de
rodapé. Sem esse arquivo o painel publica uma nota genérica — e aí a cobertura
não está sendo declarada, que é justamente o selo de confiança do documento.

**Estas bases são alimentadas depois do fato**, pela planilha de conciliação do
mês fechado. Enquanto for assim, o que está à frente de hoje na tela é só o que
alguém digitou. O conserto não é técnico: é lançar os fornecedores recorrentes
como previsto antes do dia 25.

## Três coisas que são diferentes da Amana

1. **O saldo é âncora + movimento realizado**, não + movimento *conciliado*. A
   conciliação formal quase não é usada aqui: 1.039 dos 1.179 movimentos do
   Santander da Boldró e 1.190 dos 1.223 do Bradesco da YO estão como "Não
   conciliado". A fórmula da Amana devolveria −0,00 na Boldró e −111.017,19 na
   YO. Realizado = tudo que não é "Previsto".

2. **O extrato é lido mês a mês.** Em período longo o `ListarExtrato` trunca: a
   ContaMax devolve 53 movimentos em setembro, 96 em agosto-setembro e 93 em
   julho-setembro — e neste último o saldo de 30/09 desaparece.

3. **Há um bloco `agenda`** com o que o Omie tem como "Previsto" daqui para a
   frente, separado dos títulos a vencer. Na Boldró são 30 compromissos de
   outubro na conta Fundo Fixo que não aparecem como título em aberto.

## A âncora — atualizar todo fechamento

`ANCORA_DATA` e `ANCORA`, no topo de `coleta_dash.py`: o saldo realizado de cada
conta na última data fechada. Sem atualizar, o saldo de hoje acumula movimento
sobre base velha.

`DIVERGE`, no mesmo lugar, declara quando o Omie não bate com o extrato na data
da âncora. Hoje a Boldró carrega R$ 3,94 de diferença, que apareceu entre 15 e
16/10 por edição de movimento de setembro depois do fechamento. O painel abre um
alerta em vez de tapar o número.

## Credenciais

As chaves da Boldró e da YO vivem em `omie-<empresa>/omie.py`, na pasta do
projeto no iCloud, **fora deste repositório**. O `omie_api.py` lê de lá (ou de
`~/.omie_<empresa>.json`, se existir). Nada de chave entra no git.
