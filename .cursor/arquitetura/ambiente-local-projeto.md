# Ambiente local — {projeto}

Referência para desenvolvimento local e testes **E2E (I7)** no repositório de produto que usa o Brain.

**Documentos relacionados:**

- [Alterações de código para ambiente local](alteracoes-ambiente-local-projeto.md)
- [Consultas BD (produção)](../sustentacao/consultas-bd.md) — quando existir no repo

---

## Gate L0 — antes da bifurcação (B0) e do fluxo (S1/I1)

**Obrigatório** antes de qualquer card. Agente sobe o ambiente, valida e **informa a URL no chat**.

| Passo | Comando / critério |
|-------|-------------------|
| 1. Subir | Comando de subida do perfil (ex.: `docker compose up -d`) |
| 2. Banco | Validar conexão conforme perfil (host, porta, schema) |
| 3. HTTP | `curl -sI <URL-local> \| head -5` |
| **URL no chat** | URL local que o time usa para dev |

Somente após L0 ok → **B0 (bifurcação)**: perguntar *“SUSTENTAÇÃO ou IMPLEMENTAÇÃO?”* e aguardar a resposta explícita antes de iniciar **S1** ou **I1**.

---

## Dois ambientes — não confundir

| Ambiente | Uso | URL | Banco |
|----------|-----|-----|-------|
| **Local (I7 / I10)** | Dev + testes Playwright na matriz local | *(preencher)* | *(preencher)* |
| **Homol remoto (I13)** | Validação pós-deploy | *(preencher)* | BD **ao vivo** do servidor de homol |

- Confirme no perfil se o MySQL local é dump congelado ou dado ao vivo.
- **I13** usa URL remota — nunca localhost após deploy.

Guias: [testes-local.md](../implementacao/testes-local.md), [testes-homol.md](../implementacao/testes-homol.md) — quando existirem no repo.

---

## Manutenção deste arquivo

Copie este modelo para o repositório de produto como `ambiente-local-{nome-do-repo}.md` e preencha portas, URLs, credenciais de dev e comandos reais. No repositório **Brain-Cursor** (harness) este arquivo é só referência — não descreve um app em execução.