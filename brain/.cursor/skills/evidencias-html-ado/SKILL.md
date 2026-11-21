---
name: evidencias-html-ado
description: >-
  Produz e valida HTML do Solides CRM para Azure DevOps (I2-html, I2-val, I9,
  I11, I14, I15). Use ao montar plano.html, evidencias.html ou
  evidenciashomol.html, embutir prints ou validar conformidade com análise e
  plano.
---

# HTML de evidências — UX para ADO

Guias: [documento-evidencias-html.md](../../implementacao/documento-evidencias-html.md) ·
`plano.html` (I2-html): [documento-plano-html.md](../../implementacao/documento-plano-html.md)

## Padrão visual/estrutural (OBRIGATÓRIO — usar sempre)

**Template canônico:** [`template-evidencias.html`](template-evidencias.html) — copiar e preencher. **Sempre** produzir o HTML nesse padrão.

Cards de referência (padrão aprovado pelo usuário):
- `partners`: `docs/evidencias/html/alteracao-cnpj-alfa-numerico/149212-Desenvolvimento-de-alteracoes-CNPJ-Alfanumerico/evidencias.html`
- `solides-crm`: `docs/evidencias/html/consumo-creditos-profiler/150225-Consumo-de-creditos-base-CRM/evidencias.html`
- `partners`: `docs/evidencias/html/transferencia-de-base/153391-Transferencia-de-base/evidencias.html`
- `cit`: `docs/evidencias/html/alteracao-mensalidade/150624-Apoio-Ticket-2151687-alteracao-mensalidades/evidencias.html` — exemplo **neste repositório**, idêntico ao template

Regras de ouro:
1. **HTML completo** — `<!DOCTYPE html>` + `<html lang="pt-BR">` + `<head>` com `<meta charset>`, `<meta viewport>`, `<title>` e `<style>` (CSS com `:root`). **Não** usar só `<div>` com estilos inline soltos.
2. **Paleta fixa:** `--head #0f3d5c` · verde `#28a745` · ok `#f4fff6` · warn `#fff3cd` · border `#d0d0d0`. Fonte `"Segoe UI", Calibri, Arial`; corpo 11pt.
3. **Ordem dos blocos** (`evidencias.html` e `evidenciashomol.html`; o `plano.html` tem corpo próprio — ver abaixo)**:** H1 + `p.card-meta` → **Resposta ao incidente** (`div.info-block`) → **Proposta de solução** (`div.solucao`) → `div.status-pills` → **Resumo executivo** (tabela 2 col., linhas `.highlight`) → Diagnóstico (`div.info-block`) → Evidências (tabelas, SQL em `pre.cmd`, prints em `figure.evidence` + `.http-evidence`) → Testes E2E/local → `div.footer`.
4. pt-BR; **sem** caminhos internos `docs/`/`.md`/`.php` no corpo visível; imagens por caminho relativo (**nunca** base64).
5. **Query/comando acima do print** — todo print de resultado (banco, tela, terminal) vem precedido do **texto exato** da query/comando que o produziu, em `pre.cmd` logo acima do `figure.evidence`. Print sem a query/comando imediatamente acima reprova no gate.
6. **Documento oficial não cita agente da frota** — nada de nome de subagente/especialista, "revisado pelo especialista-X" ou seção "Revisões de especialistas"; esse registro vive no `_processo-revisoes.md` interno (`.claude/frota/regras.md` § 11). Nome de coluna/tabela/balde do banco é exceção.

## Três arquivos por card

```
docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html            # I2-html, I2-val
docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html       # S3, I9, I11
docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidenciashomol.html  # I14, I15
```

- **`{tema-slug}`** — tema/assunto em kebab-case (ex.: `login-unificado-lovecrm`).
- **`{Titulo-Slug}`** — `{card-id}-Titulo-Do-Card-Em-Kebab-Capitalizado` (ex.: `152069-Login-Unificado-Parceiros-LoveCRM`).

### `plano.html` (I2-html) — mesmo `<style>`, corpo diferente

Usa o **mesmo** `<style>` canônico e as mesmas regras de ouro acima (HTML completo, paleta fixa,
pt-BR, sem caminho interno visível, imagem por caminho relativo). O que muda é **o corpo**: em vez
dos blocos de incidente/evidência, o `plano.html` tem **13 seções fixas** (nunca apagar seção —
`N/A + motivo`). Esqueleto, checklist de conformidade e regra de entrega:
[documento-plano-html.md](../../implementacao/documento-plano-html.md) — **não** duplicar aqui.

**Duas restrições do comentário do ADO moldam o formato** (valem para os três arquivos):

1. **O comentário remove `<style>`** — o CSS só chega porque `ado_update_comment.py` **inlina** os
   estilos na postagem. Por isso o HTML é escrito com `<style>` canônico e **nada** depende de
   seletor que o inliner não resolva.
2. **O comentário não renderiza mermaid** — logo, o **antes/depois** do `plano.html` é
   **tabela lado a lado + fluxo numerado**; diagrama mermaid fica **só no `.md`** do plano.

Sem PNG/Playwright em I2-html: o plano é anterior ao código.

## Padrão E2E obrigatório (todos os cards)

**Referência:** `evidencias.html` de um card já validado — seção “Testes automatizados (E2E)”.

Todo bloco E2E deve ter **print + tabela detalhada** — em `evidencias.html` (I9) **e** `evidenciashomol.html` (I14):

1. `h2` Testes automatizados (E2E)
2. `h3` **1. Relatório Playwright — execução completa**
3. `figure.evidence` + PNG `{card-id}-e2e-playwright.png`
4. `p.resultado.ok` — N/N pass
5. `h3` **2. Detalhamento dos cenários**
6. Tabela: **#** · **Cenário** · **Documento / entrada** · **AC** · **Resultado**

**Proibido:** só tabela resumida, só `<pre>` com comando, ou “N/N pass” sem print.

PNG: `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/{card-id}-e2e-playwright.png` (screenshot de `playwright-report/index.html` após I7).

## Ciclo de vida

| Etapa | Arquivo | Conteúdo | Encerra? |
|-------|---------|----------|----------|
| **I2-html** | `plano.html` | Plano em 13 seções (sem print) | Não |
| **I2-val** | `plano.html` | Subagente `validador-tecnico` valida — **gate do I4** | Não |
| **Pós-I2-val** | `plano.html` | Pergunta "posto eu ou entrego o comando?" (caminho + GUID + comando) | — |
| **I9** | `evidencias.html` | Impl + **E2E (print + tabela)** | Não |
| **I11** | `evidencias.html` | Bloco **local** L01–LN | Não |
| **I14** | `evidenciashomol.html` | **E2E (mesmo padrão)** + **homol** U01–UN | Não |
| **I15** | `evidenciashomol.html` | Subagente valida | **Sim** |
| **Pós-I15** *(só se houve dev)* | `evidenciashomol.html` | Pergunta "posto eu ou entrego o comando?" — destino **card de DESENVOLVIMENTO** | — |

## Prefixos de figuras

- **L01–LN** — testes local (I10/I11) em `evidencias.html`
- **U01–UN** — testes homol (I13/I14) em `evidenciashomol.html`
- **Nunca misturar** L e U no mesmo arquivo/bloco

## Padrões visuais

- **E2E:** print Playwright + tabela detalhada (obrigatório)
- **Tela local/homol:** `<figure class="evidence">` + PNG
- **HTTP:** `<div class="http-evidence">` — dados de `*-api.json` (tabela compacta)

## Validação

- **I2-val:** subagente `validador-tecnico` valida o `plano.html` (13 seções, conformidade sem
  campo em branco, revisões registradas) — é o que **sustenta o I4**; aprovação pelo agente **não conta**
- **I11:** subagente `validador-tecnico` valida bloco local **e** bloco E2E em `evidencias.html` — aprovação pelo agente **não conta**
- **I15:** subagente valida `evidenciashomol.html` (E2E print+tabela + homol) vs análise + plano

## Imagens coladas no chat → PNG para o HTML

Quando o usuário **cola prints no chat**, os arquivos **NÃO** ficam no disco (não estão em Downloads/Imagens/assets). Ficam no **transcript da sessão** em base64: `~/.claude/projects/<slug-do-cwd>/<session>.jsonl` — blocos `{"type":"base64","media_type":"image/png","data":"..."}`.

Para montar o HTML com essas imagens:
1. Localizar o `.jsonl` mais recente em `~/.claude/projects/<slug>/` (slug = caminho do projeto com `/` → `-`).
2. Script Python: percorrer o `.jsonl`, extrair os base64 de imagem → PNG na **ordem de aparição** (a linha do JSONL agrupa as imagens de uma mesma mensagem; header PNG bytes 16–24 = `WxH`, ajuda a mapear cada tela).
3. Copiar para `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/` e embutir com `figure`/`img`.

**Não** dizer "não consigo salvar imagem do chat" — elas estão no `.jsonl`. Detalhe: memória `feedback-extrair-imagens-chat`.

## Azure DevOps — pergunte antes de postar

**Pergunte antes, a cada postagem:** *"Posto eu o `<arquivo>` no card `<n>`, ou te entrego o comando para você postar?"* Só o contexto principal posta, e só com "sim" explícito (vale para aquela postagem). Se o usuário preferir, entregue no chat caminho do arquivo, GUID do projeto e o comando canônico já preenchido:

```bash
ADO_PROJECT=<GUID-do-projeto> python3 .claude/scripts/ado_update_comment.py <html_path> <work_item_id> [comment_id]
```

Sem `comment_id` cria; com `comment_id` atualiza (PATCH). O script converte o CSS em estilos inline (o comentário do ADO não renderiza `<style>`), sobe as imagens como anexos e as embute (`src` com o GUID do projeto), usa a credencial de `.mcp.json` e envia numa única chamada. Requer `ADO_PROJECT`=GUID do projeto. Ver skill [azure-devops-cards](../azure-devops-cards/SKILL.md).

**Destino de cada HTML (para o comando entregue):**
- `plano.html` (Pós-I2-val): card da implementação — entregue/postado (após perguntar) **antes** do I4.
- `evidencias.html` (S3 diagnóstico → Pós-S6a / Pós-I11): card do incidente/sustentação.
- `evidenciashomol.html` (Pós-I15): **somente quando houve desenvolvimento/implementação**, e no **card de DESENVOLVIMENTO** — que pode ser **diferente** do card do incidente (ex.: card 152069). Sinalizar isso no chat e deixar `<card-de-dev>` como placeholder; nunca assumir que é o mesmo card do incidente. `ADO_PROJECT` = GUID do projeto do card de desenvolvimento.

**Postado pelo agente ou entregue ao usuário, o HTML precisa estar completo e validado antes** (I2-val / S6a-val / I11 / I15) — sem pendências, sem placeholders de conteúdo.
