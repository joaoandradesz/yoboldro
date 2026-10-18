#!/bin/sh
# Atualiza e publica o dashboard de caixa da Boldro e da YO.
# Um comando so, porque a rotina agendada pede uma aprovacao por comando.
set -e
cd "$(dirname "$0")/.."
echo "== lendo o Omie das duas empresas"
python3 caixa/coleta_dash.py
echo "== montando o caixa.html"
python3 caixa/gera_dash.py
if git diff --quiet -- caixa.html; then
  echo "== nada mudou no caixa.html, nao ha o que publicar"
else
  git add caixa.html caixa/dados_caixa.json
  git commit -q -m "caixa $(date +%d/%m/%Y)"
  git push -q origin HEAD
  echo "== publicado: $(git log --oneline -1)"
fi
echo "== conferindo a publicacao"
curl -s -o /dev/null -w "   caixa.html responde %{http_code}\n" \
  https://joaoandradesz.github.io/yoboldro/caixa.html
