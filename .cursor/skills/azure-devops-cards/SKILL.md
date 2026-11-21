---
name: azure-devops-cards
description: >-
  Formata entregas e respostas para cards Azure DevOps (work items, HTML de
  evidências, anexos). Use ao encerrar etapas S1–I15, preparar evidências para
  postar no ADO ou estruturar comunicação com negócios. O agente pergunta antes
  de cada postagem: posta ele (com "sim") ou entrega o comando ao usuário.
---

# Azure DevOps — cards e evidências

## Documentação oficial

| Tema | URL |
|------|-----|
| Azure Boards — work items | https://learn.microsoft.com/en-us/azure/devops/boards/work-items/ |
| Markdown in Azure DevOps | https://learn.microsoft.com/en-us/azure/devops/project/wiki/markdown-guidance |
| Attach files to work items | https://learn.microsoft.com/en-us/azure/devops/boards/backlogs/add-link |

## Identificadores no projeto

| Elemento | Formato | Exemplo |
|----------|---------|---------|
| Card / work item | número ADO no título ou pasta | `149010` |
| `{tipo}` | kebab-case, domínio | `alteracao-cnpj-alfa-numerico` |
| `{card-id}` | kebab-case, título do card | `149010-Desenvolvimento-de-alteracoes-CNPJ-Alfanumerico` |

Guia de paths: [estrutura-docs.md](../../arquitetura/estrutura-docs.md)

## Artefatos por fase

| Fase | Artefato | Caminho |
|------|----------|---------|
| S3 | Análise + HTML diagnóstico | `docs/analises/{tipo}/{card-id}.md` |
| S3 | Prints de queries | `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/{card-id}-qN.png` |
| I1 | Plano | `docs/implementacoes/plano/impl-*.md` |
| I5–I11 | Executada | `docs/implementacoes/executada/impl-*.md` |
| I8 | Resultado E2E | `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/testes-e2e.md` |
| I9–I11 | Evidências finais | `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html` |

## Escrever no ADO — PERGUNTE ANTES, A CADA POSTAGEM

> **Antes de postar, pergunte no chat e aguarde:** *"Posto eu o `<arquivo>` no card `<n>`, ou te entrego o comando para você postar?"* Poste **só com "sim" explícito** — a autorização vale para **aquela** postagem, não para a sessão. Só o **contexto principal** posta; **subagente nunca posta**. Estado/campos do work item, links e anexo avulso continuam proibidos. Leitura do card (`mcp__azure-devops__wit_work_item`, comentários, campos) continua liberada.

Comando canônico (o agente roda após o "sim", ou entrega ao usuário se ele preferir):
```bash
ADO_PROJECT=<GUID-do-projeto-do-card> python3 .cursor/scripts/ado_update_comment.py <html_path> <work_item_id> [comment_id]
```

O agente preenche `<GUID-do-projeto-do-card>`, `<html_path>` e `<work_item_id>` com os valores reais — quem rodar só copia e executa.

### Fluxo completo — do print colado ao comentário COM imagens
1. **Imagens que o usuário colou no chat NÃO ficam em disco** — estão no transcript `~/.cursor/projects/<slug-do-cwd>/<sessão>.jsonl` em base64. Extrair (script Python que decodifica os blocos `{"type":"base64","media_type":"image/png"}` na ordem de aparição), salvar em `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/` e embutir no HTML com `figure/img` (src relativo). Ver [evidencias-html-ado](../evidencias-html-ado/SKILL.md) e memória `feedback-extrair-imagens-chat`.
2. O **usuário** roda o script acima apontando o HTML. Ele: inlina o CSS (o comentário ignora `<style>`); para cada `<img>` faz **upload do PNG como anexo**, **vincula** ao work item e reescreve o `src` para a URL do anexo **COM o GUID do projeto** — assim as imagens ficam **embutidas no comentário** (confirmado nos cards 152069 e 156576).

### Regra crítica das imagens
A `<img>` só renderiza no comentário com o `src` **contendo o GUID do projeto**:
`https://dev.azure.com/solidestech/<GUID-projeto>/_apis/wit/attachments/<attachment-guid>?fileName=<nome>.png`
URL **org-level** (sem o GUID do projeto) → **HTTP 400 "Sequence contains no elements"**. O script já monta no formato certo.

### Flags e regras
- **`ADO_PROJECT` OBRIGATÓRIO** = GUID do projeto do card. Incidentes (ex. 152069) = `9ab3afca-3b1a-4a80-bc36-b0e3625d3a69` (TI CORP - Antiga Operação); testes homol (ex. 156576) = `3acd1fd1-e624-4002-bdbd-532f45aeb902` (TI CORP - Sustentação). O agente confirma o projeto do card com `mcp__azure-devops__wit_work_item` (campo `System.TeamProject`) e já entrega o GUID no comando.
- Sem `comment_id` → **cria**; com `comment_id` → **atualiza** (PATCH). Se retornar **404 "Comment does not exist"**, rode **sem** `comment_id` para criar novo.
- **O HTML entregue precisa ter `<body>` sem atributos.** O script casa `<body>(.*?)</body>` **literal** (`ado_update_comment.py:111`); um `<body style="…">` faz o script quebrar (`AttributeError`). Seja o agente (após o "sim") ou o usuário quem roda o comando, o arquivo precisa sair já compatível — ou apontar no chat a cópia com o body limpo.
- `ADO_ATTACH=0` → não (re)anexa (use ao repostar só texto, para não duplicar anexos). `ADO_EMBED=0` → não embute imagens.
- Usa a credencial de `.mcp.json`; api-version `7.0-preview.3`.
- **Não** citar caminhos internos `docs/`/`.md` no corpo visível.

Este script é o método canônico de postagem do projeto — o agente o executa **só após o "sim"** da pergunta acima, ou entrega o comando (a tool MCP de comentário também serve, mas não sobe imagem). O script embute as imagens no comentário (upload do PNG como anexo + `src` com o GUID do projeto) — não há passo manual de colagem.

Detalhe e histórico: memória `feedback-postar-evidencias-ado`. Skill do HTML: [evidencias-html-ado](../evidencias-html-ado/SKILL.md)

### Observações do HTML
- HTML **não** deve citar caminhos internos `docs/`/`.md` (público negócios).
- Imagens relativas no HTML: `../../../assets/{tema-slug}/{card-id}-{Titulo-Slug}/...`
- Card de **estudo/refinamento técnico**: é aceitável incluir componentes técnicos (controllers, helpers, endpoints) e uma **matriz consolidada** (fluxo As-Is × análise) — o público é técnico. Isso **não** é vazamento.
- Limitação cosmética conhecida: o sanitizador do ADO pode truncar `font-family` com vírgulas/aspas em `<pre>` (ex.: vira `font-family:Consolas,;`). O conteúdo continua íntegro e monoespaçado — **não** reprovar o HTML por isso.

## Formato de resposta no chat (por etapa)

### Sustentação

Seguir [sustentacao/resposta-chat.md](../../sustentacao/resposta-chat.md):

1. Resumo do documento
2. **Caminho do arquivo** para revisão
3. Resultado da validação subagente
4. Decisão: análise suficiente **ou** implementação necessária

### Implementação

Seguir [implementacao/resposta-chat.md](../../implementacao/resposta-chat.md) — uma seção por etapa I1–I15.

Exemplo I7:

```
Comando: cd testes && npm run test:e2e
Resultado: 10/10 pass (100%)
Próximo: I8 testes-e2e.md
```

Exemplo I11 (HTML local — **não** é encerramento):

```
Validação HTML local: Aprovado
Próximo: Pós-I11 (posto eu ou te entrego o comando?) → I12
Caminho: docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html
Comando (se preferir postar você): ADO_PROJECT=<GUID> python3 .cursor/scripts/ado_update_comment.py <caminho> <card>
```

Exemplo I15 (**único encerramento** do card com implementação):

```
Validação HTML homol: Aprovado
Card encerrado — evidenciashomol.html pronto: posto eu no card ou te entrego o comando?
Caminho: docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidenciashomol.html
Comando (se preferir postar você, no card de DESENVOLVIMENTO):
  ADO_PROJECT=<GUID> python3 .cursor/scripts/ado_update_comment.py <caminho> <card-de-dev>
```

### Pós-I15 — `evidenciashomol.html` para o card de DESENVOLVIMENTO

- **Só quando houve desenvolvimento/implementação** (card encerrado como análise suficiente **não** gera entrega de homol).
- O `evidenciashomol.html` destina-se ao **card de DESENVOLVIMENTO**, que **pode ser diferente** do card do incidente/sustentação (ex.: card 152069 — incidente e desenvolvimento/teste em cards distintos). O agente **sinaliza isso** e deixa `<card-de-dev>` como placeholder no comando.
- **Pergunte antes de postar** (posto eu ou entrego o comando?) — posta só com "sim"; senão entrega caminho + comando.
- Mesmo método canônico (script `ado_update_comment.py`), com `ADO_PROJECT` = GUID do projeto do **card de desenvolvimento**.

## Conteúdo esperado no work item

| Momento | O que vai para o card |
|---------|-----------------------------------|
| Análise aprovada | HTML diagnóstico + prints `{card-id}-qN.png` → card do incidente/sustentação |
| Implementação | `evidencias.html` (I9 E2E + I11 local) → card do incidente; `evidenciashomol.html` (I14) → **card de DESENVOLVIMENTO** (Pós-I15) |
| Discussão técnica | Plano `docs/implementacoes/plano/` · executada `docs/implementacoes/executada/` |

## Checklist antes de marcar Done

- [ ] I11 aprovada (subagente) — HTML local `evidencias.html`
- [ ] Pós-I11 — caminho no chat + pergunta "posto eu ou entrego o comando?" respondida (nada postado sem "sim")
- [ ] **I15 aprovada (subagente)** — HTML homol `evidenciashomol.html` · **encerramento**
- [ ] Pós-I15 *(só se houve dev)* — caminho + comando entregues, sinalizando destino no **card de desenvolvimento**
- [ ] HTML 100% conforme análise + plano
- [ ] E2E e homol registrados no HTML (se houve implementação)
- [ ] Imagens embutidas no comentário (`src` com o GUID do projeto — via script)
- [ ] Sem dados sensíveis (tokens, senhas, PII desnecessária)

## MR GitLab (complementar)

Template: `.gitlab/merge_request_templates/Checklist.md`  
Deploy fica **fora do fluxo do agente** (responsabilidade humana) — ver [gitlab-deploy-cicd](../gitlab-deploy-cicd/SKILL.md)
