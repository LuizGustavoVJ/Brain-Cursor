# Alterações de código para ambiente local — {projeto}

Patches e ajustes que **só valem na máquina de dev** e não devem ir para `origin`. Cada repositório de produto documenta aqui o que precisa para subir localmente.

## Checklist

1. Listar arquivos alterados apenas para dev (dotenv opcional, whitelist de sessão, etc.).
2. Indicar onde os patches vivem **fora do git** (pasta em `~/`, variável de ambiente).
3. Comando para aplicar e reverter antes de commit/PR (gate do `AGENTS.md`).

## Brain-Cursor (harness)

Este repositório **não** aplica patches de aplicação — só carrega a frota, skills transversais e scripts. Repositórios que herdarem o Brain copiam este modelo para `alteracoes-ambiente-local-{nome-do-repo}.md` e preenchem com o produto real.