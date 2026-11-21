# HTML de evidências — atualização pós-implementação

Guias das etapas **I9**, **I11** e **I14** do [fluxo-implementacao.md](fluxo-implementacao.md).

**Três arquivos por card** em `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/`:

| Arquivo | Etapas | Conteúdo | Guia |
|---------|--------|----------|------|
| `plano.html` | **I2-html** (validação **I2-val**) | O **plano**: antes × depois, decisões, conformidade (8 itens) — **sem PNG** e **sem citar agente da frota**; revisões de especialistas ficam no `_processo-revisoes.md` interno (regras.md § 11) | [documento-plano-html.md](documento-plano-html.md) |
| `evidencias.html` | S3, I9, I11 | Diagnóstico + implementação + E2E + **local** L01–LN | este arquivo |
| `evidenciashomol.html` | I14, I15 | **E2E (mesmo padrão)** + **homol** U01–UN | este arquivo |

O `plano.html` **não** é descrito aqui: esqueleto das 13 seções, checklist de conformidade e
entrega em Pós-I2-val estão no guia próprio — [documento-plano-html.md](documento-plano-html.md).
Os três arquivos compartilham o **mesmo `<style>` canônico** (skill
[evidencias-html-ado](../skills/evidencias-html-ado/SKILL.md)) e o **mesmo método de postagem**
(script executado **pelo usuário**).

---

## Template canônico (estrutura OBRIGATÓRIA — igual em toda demanda)

**Referência canônica (copiar sempre):**
- `docs/evidencias/html/troca-cnpj/152361-Troca-de-CNPJ/evidencias.html` (diagnóstico S3)
- `docs/evidencias/html/alteracao-cnpj-alfa-numerico/149010-Desenvolvimento-de-alteracoes-CNPJ-Alfanumerico/evidenciashomol.html` (E2E + homol)

Todo HTML de evidências **copia o bloco `<style>` do template** (não inventar CSS) e segue o **esqueleto de seções** abaixo. Assim toda demanda sai no mesmo padrão de qualidade.

### Classes CSS canônicas (do `<style>` de referência)

`:root` vars (`--head #0f3d5c`, `--ok #f4fff6`, `--warn #fff3cd`, `--muted`, `--border`) · `.card-meta` (metadados sob o `h1`) · `.objetivo` (nota cinza) · `.info-block` (caixa azul de objetivo/escopo) · `.solucao` (caixa verde de proposta/conclusão) · `.table-wrap` + `table`/`th`/`td` · `tr.highlight` (linha verde `#d4edda`) · `tr.warn` (amarela) · `pre.cmd` (SQL/código) · `.resultado` / `.resultado.ok` (faixa de resultado) · `figure.evidence` + `figure.evidence img` + `figcaption` (print) · `.http-evidence` + `.http-evidence-title` (bloco GET/POST 200) · `.footer`.

### Esqueleto de `evidenciashomol.html` (ordem fixa — padrão 149010)

1. `h1` + `p.card-meta` (Card · Sistema · Ambiente · Data)
2. `div.info-block` → `h2` **Objetivo e escopo dos testes** + `ul` (E2E / Homol URL / Evidência de BD)
3. `h2` **Cenários homol URL (U01–UN) — por que cada um** → `table-wrap`/`table` (Cenário · Rota/Ação · Tipo · AC · Por que testar)
4. `h2` **Testes automatizados (E2E)** + `p.objetivo` (Ferramenta · Resultado N/N · Data)
   - `h3` **1. Relatório Playwright — execução completa** → `figure.evidence` (print) + `p.resultado.ok`
   - `h3` **2. Detalhamento dos cenários E2E** → `table-wrap`/`table` (# · Cenário · Documento/entrada · AC · Resultado)
5. `h2` **Testes via URL — Homol remota (I13/I14)** + `p.objetivo`
   - `h3` **Detalhamento — cenários homol (U01–UN)** → `table-wrap`/`table` (Método · URL · Status · Retorno)
   - `h3` **Evidências visuais homol** → por cenário: `h4` + `figure.evidence` (tela) + `div.http-evidence` (tabela GET/POST **200** + corpo). Para ação que altera dados: incluir o **estado no BD (antes/depois)** em `table-wrap`.
6. `div.footer`

### Esqueleto de `evidencias.html` (diagnóstico + impl + local)

`h1`+`card-meta` → Resposta ao incidente (`solucao`) → Proposta de solução (`solucao`, com `pre.cmd` de SQL) → Resumo executivo (tabela 2 col) → Evidências das consultas (por consulta: `h3` + `pre.cmd` + `table` + `resultado`) → **I9** E2E (Relatório `figure` + Detalhamento) → **I11** bloco local L01–LN (`h4` + `figure.evidence` + `http-evidence`) → `footer`.

### Regras do template

- **Query/comando acima do print** (regra do usuário, 23/09/2026). Todo print de resultado — screenshot de banco, tela ou terminal — vem **precedido do texto exato** da query/comando que o produziu, em bloco de código (`pre.cmd`), logo acima do `figure.evidence`. Print sem a query/comando que o gerou imediatamente acima é montagem fora do padrão e **reprova** no gate do HTML.
- **Copiar o `<style>` do template** (classes acima) — no arquivo `.html`. Ao **postar no comentário do card** (via script), o CSS é convertido para **estilos inline** (o ADO ignora `<style>`), mantendo a mesma estrutura de seções.
- **Testar a ação da demanda de fato** (POST/UPDATE): estado antes → ação → estado depois → reenvio, com print + retorno + BD (ver [testes-homol.md](testes-homol.md#ações-que-alteram-dados-postupdate--testar-a-ação-de-fato)).
- **Sempre o mesmo conjunto de seções** — não omitir matriz de cenários, detalhamento E2E (print+tabela), detalhamento homol e evidências visuais.

---

## Padrão de diagnóstico (S3) obrigatório — layout canônico

**Referência canônica:** `docs/evidencias/html/troca-cnpj/152361-Troca-de-CNPJ/evidencias.html`. Todo `evidencias.html` de diagnóstico (S3) segue **exatamente** este layout, com estilos que no comentário do ADO viram **inline** (o ADO ignora `<style>`), pt-BR, sem caminhos internos `docs/`/`.md`.

### Paleta e tipografia (fixas)

| Elemento | Estilo |
|----------|--------|
| Fonte | `"Segoe UI", Calibri, Arial, sans-serif`; corpo `11pt`, `line-height:1.45`, cor `#1a1a1a` |
| `h1` | `14pt`, cor `#0f3d5c` |
| `h2` | `12pt`, cor `#0f3d5c`, `margin-top:22px` |
| `h3` | `11pt`, cor `#333` |
| Caixa **verde** (positivo/resultado/proposta) | `border:1px solid #b8dfc4; border-left:4px solid #28a745; background:#f4fff6` |
| Aviso **verde** (resultado inline) | `background:#f4fff6; border-left:3px solid #28a745; padding:8px 12px` |
| Aviso **amarelo** (pendência/atenção) | `background:#fff3cd; border-left:3px solid #ffc107` |
| Aviso **vermelho** (divergência/bug) | `background:#fff5f5; border-left:3px solid #dc3545` |
| Cabeçalho de tabela | `background:#f0f4f8; color:#0f3d5c` |
| Linha destaque positivo | `bgcolor="#d4edda"` · atenção `bgcolor="#fff3cd"` · negativo `bgcolor="#f8d7da"` · neutro `bgcolor="#eef4fa"` |
| SQL | `<pre>` `font-family:Consolas,monospace; font-size:8.5pt; background:#f4f4f4; border:1px solid #ddd; white-space:pre-wrap; overflow-x:auto` |

### Ordem das seções (fixa)

1. **`h1`** título + **`p`** de metadados: `Card | Ticket | Sistema | Data | Ambiente` (separador `&nbsp;|&nbsp;`).
2. **Resposta ao incidente** — caixa verde com `h2` + parágrafo + `<ul>` de bullets objetivos.
3. **Proposta de solução** — caixa verde; SQL em `<pre>` quando houver; avisos verde/amarelo conforme o caso.
4. **Resumo executivo** — tabela 2 colunas: `table-layout:fixed`, `colgroup` 32%/68%, `max-width:820px`, `word-break:break-word`; linhas-chave com `bgcolor` (ação `#d4edda`, pendência `#fff3cd`, divergência `#f8d7da`).
5. **(Opcional) Causa raiz** — parágrafos numerados + aviso amarelo de síntese.
6. **Evidências — consultas SQL executadas (produção · data)** — para **cada** consulta:
   - `h3` `Consulta N — {título}`
   - `<pre>` com o **SQL** executado
   - tabela de resultado: `width:100%`, `table-layout:fixed`, `colgroup` com larguras somando 100%, cabeçalho `#f0f4f8`
   - **`p` “Resultado:”** em caixa verde (ou vermelha se for a divergência-chave) resumindo a leitura
7. **Conclusão** — caixa verde com o fechamento.
8. **`p` Status da análise** — `CONCLUÍDA` / ações.
9. **Rodapé** — `<div>` com `border-top:1px solid #d0d0d0; font-size:9pt; color:#555` e a linha de identificação do card.

### Regras

- **Toda** consulta traz **SQL (`<pre>`) + tabela de resultado + parágrafo “Resultado:”** — nunca só a tabela nem só o texto.
- Tabelas sempre dentro de `<div style="width:100%;overflow-x:auto">` para rolagem horizontal no ADO.
- Imagens (prints de query) via caminho relativo `../../../assets/{tema-slug}/{card-id}-{Titulo-Slug}/` — **não** base64. No comentário do ADO as imagens são embutidas pelo script de postagem, executado **pelo usuário** (ver [Entrega para postagem no card ADO](#entrega-para-postagem-no-card-ado--conteúdo-completo)).
- Quando **S5 = análise suficiente**, este mesmo layout é o conteúdo entregue ao usuário para postar no card (Pós-S6a).

---

## Padrão E2E obrigatório (todos os cards, todos os repositórios)

**Referência canônica:** seção “Testes automatizados (E2E)” do `evidencias.html` de referência do projeto (mesmo padrão em todos os repositórios Solides).

Todo bloco E2E em **`evidencias.html` (I9)** e **`evidenciashomol.html` (I14)** deve ter **exatamente** a mesma estrutura. **Proibido** substituir por tabela resumida, `<pre>` com comando ou texto “N/N pass” sem print.

### Estrutura HTML obrigatória

1. **`h2`** — `Testes automatizados (E2E)`
2. **`p.objetivo`** — Ferramenta (Playwright) · Resultado N/N pass (100%) · Data
3. **`h3`** — `1. Relatório Playwright — execução completa`
4. **`figure.evidence`** — print embutido do relatório Playwright (PNG)
5. **`p.resultado.ok`** — resumo textual N/N pass
6. **`h3`** — `2. Detalhamento dos cenários`
7. **Tabela** com colunas: **#** · **Cenário** · **Documento / entrada** · **AC** · **Resultado**

### Asset PNG obrigatório

| Item | Valor |
|------|--------|
| Caminho | `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/{card-id}-e2e-playwright.png` |
| Origem | Screenshot de `testes/playwright-report/index.html` após `npm run test:e2e` 100% pass |
| HTML | `<figure class="evidence">` + `<img src="../../../assets/...">` + `<figcaption>` |

### Comando para gerar o print (após I7)

```bash
cd testes && npm run test:e2e
# em seguida: screenshot fullPage de playwright-report/index.html → PNG no caminho acima
```

### Tabela “Detalhamento dos cenários”

- **Uma linha por teste** do spec E2E (condizente com `testes-e2e.md` e stdout I7)
- Coluna **Documento / entrada** com o valor testado (`<code>`) ou marcador de inspeção de fonte
- Coluna **AC** alinhada ao plano
- Coluna **Resultado** = `Pass` (só incluir após 100% pass na I7)
- Linhas alternadas com `class="highlight"` (padrão de referência)

### Onde aplicar

| Arquivo | Etapa | Regra |
|---------|-------|-------|
| `evidencias.html` | **I9** | Bloco E2E completo (print + tabela) **antes** de I10 |
| `evidenciashomol.html` | **I14** | **Repetir** o mesmo bloco E2E (não resumir) + bloco homol U01–UN |

**Proibido:** encerrar I9 ou I14 com E2E incompleto; aprovar I11/I15 sem verificar print + tabela E2E.

---

## I9 — Após testes E2E

**Somente quando** I6 aprovada, I7 **100% pass**, I8 concluída.

### Secções a acrescentar (I9)

1. **Status da implementação** — validada (I6), testada E2E (I7/I8); local e homol **pendentes**.
2. **Plano executado**
3. **Alterações realizadas** (tabela completa)
4. **Critérios de aceite**
5. **Testes automatizados (E2E)** — conforme [Padrão E2E obrigatório](#padrão-e2e-obrigatório-todos-os-cards-todos-os-repositórios) (**print + tabela detalhada**)

**Não** declarar card encerrado na I9.

### Checklist I9 (agente — antes de I10)

- [ ] I7 **100% pass** refletido (N/N)
- [ ] PNG `{card-id}-e2e-playwright.png` existe em `docs/evidencias/assets/`
- [ ] `figure.evidence` com print embutido no HTML
- [ ] `h3` “1. Relatório Playwright — execução completa”
- [ ] `h3` “2. Detalhamento dos cenários” com **todas** as colunas obrigatórias
- [ ] Tabela com **uma linha por cenário** do spec E2E

---

## I11 — Bloco local em `evidencias.html`

**Somente após** `npm run test:local` com **100% pass** e prints gerados (I10).

### Conteúdo obrigatório

- **Ambiente:** URL local L0 (ver o perfil `arquitetura/ambiente-local-{projeto}.md`)
- **Resultado:** **N/N pass (100%)**, sem skip
- **Tabela de cenários:** rota, view, tipo, evidências
- **Figuras embutidas — L01–LN** (prefixo **local**):
  - Secção **“Evidências visuais local — N cenários”**
  - **Tela:** `<figure class="evidence">` com `*-local-tela.png` ou equivalente
  - **HTTP:** `<div class="http-evidence">` com tabela compacta — dados de `*-local-api.json`
  - Cadastro/edição: mesmas regras de evidência dupla da matriz homol, com prefixo **L**
- **Comando:**

```bash
cd testes && npm run test:local
```

**Não incluir** bloco homol (U01–UN) neste arquivo — homol vai em `evidenciashomol.html` (I14).

**Não encerrar o card na I11** — segue I12 (gate deploy) → I13–I15.

Subagente valida bloco local — [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i11).

---

## I14 — `evidenciashomol.html`

**Somente após I13** (`npm run test:homol` 100% pass na homol remota).

### Conteúdo obrigatório

- **Bloco E2E** — **copiar** o bloco de `evidencias.html` (I9): mesmo print Playwright + mesma tabela “Detalhamento dos cenários”. **Não re-executar** os testes E2E — os resultados são os mesmos (E2E valida lógica, não ambiente). Atualizar apenas referências de URL se o bloco mencionar explicitamente a URL local. Ver [Padrão E2E obrigatório](#padrão-e2e-obrigatório-todos-os-cards-todos-os-repositórios).
- **Bloco homol URL** — ambiente homol remota (URL do perfil `arquitetura/ambiente-local-{projeto}.md`)
- **Resultado homol:** **N/N pass (100%)**
- **Figuras U01–UN** — um bloco por cenário da matriz homol
- Mesmas regras visuais de tela + HTTP 200 (cadastro, edição, listagem, asset)

**Não incluir:** plano executado, alterações de código, bloco local L01–LN.

Detalhes de evidência por tipo de cenário: [testes-homol.md](testes-homol.md).

**Não encerrar o card na I14** — segue **I15** (validação subagente).

---

## Regras gerais

- Estilos **inline** no comentário do ADO (o script converte), pt-BR, sem caminhos internos `docs/` ou `.md`.
- Preservar conteúdo da sustentação em `evidencias.html`.
- **Nunca** misturar prefixos L (local) e U (homol) no mesmo bloco.
- Toda alteração de código do card na tabela (I9).

## Entrega para postagem no card ADO — conteúdo COMPLETO

O agente monta o HTML no formato final e **pergunta antes de postar** (posto eu ou entrego o comando? — só com "sim") (**Pós-I2-val** para o `plano.html` · Pós-S6a / Pós-I11 / Pós-I15 para os demais). Por isso o arquivo entregue deve estar **completo** (todas as seções: objetivo, E2E print+tabela, blocos local/homol U01–UN, tabelas HTTP, evidência de BD, conclusão) — **nunca uma parte** —, já que não há passo posterior de conferência da postagem.

- **Método único de postagem:** o script `.claude/scripts/ado_update_comment.py` (ver skill [azure-devops-cards](../skills/azure-devops-cards/SKILL.md)), **executado pelo usuário**. Numa única chamada ele inlina o CSS, sobe os PNGs como anexos, vincula ao work item e **embute as imagens no comentário**.
- **O que o agente entrega no chat:** caminho do HTML validado + GUID do projeto do card (`mcp__azure-devops__wit_work_item`, campo `System.TeamProject`) + o comando pronto `ADO_PROJECT=<GUID> python3 .claude/scripts/ado_update_comment.py <html_path> <work_item_id> [comment_id]`.
- **Imagens:** renderizam **inline** no comentário — o script reescreve o `src` para a URL **com o GUID do projeto** (`.../<GUID>/_apis/wit/attachments/<guid>?fileName=...`). URL org-level (sem GUID) dá HTTP 400. No HTML entregue, manter os caminhos relativos dos PNGs em `assets/`.

---

## Fontes

| Fonte | Uso |
|-------|-----|
| Plano `docs/implementacoes/plano/` | Passos, ACs, matrizes local e homol |
| Executada `docs/implementacoes/executada/` | Alterações, validações I6/I11/I15 |
| `testes-e2e.md` (I8) | Resumo E2E |
| `testes-local.md` (I11) | Resumo local |
| `docs/evidencias/assets/` | PNGs e JSON |

---

## I15 — Validação final (subagente)

**Somente após I14** — `evidenciashomol.html` completo.

Subagente confere condizência com análise + plano + resultados I7/I10/I13.

| Resultado | Próximo passo |
|-----------|---------------|
| **Aprovado** | Encerramento do card (e Pós-I15: perguntar se posta o `evidenciashomol.html` ou entrega o comando — card de **desenvolvimento**) |
| **Recusado** | Agente corrige → revalidação obrigatória |

Registrar em `## Validação do HTML homol` em `executada/`.

---

## Checklist do agente

### Antes de I11 (subagente local)

- [ ] I10 local **100% pass** refletido
- [ ] Cada cenário **L01–LN** com evidência no HTML
- [ ] Nenhum bloco homol (U) em `evidencias.html`
- [ ] **Bloco E2E (I9)** no mesmo arquivo: print Playwright + tabela “Detalhamento dos cenários” (padrão obrigatório)

### Antes de I15 (subagente homol)

- [ ] I13 homol **100% pass** refletido
- [ ] Cada cenário **U01–UN** em `evidenciashomol.html`
- [ ] Arquivo **sem** bloco implementação/local
- [ ] **Bloco E2E** em `evidenciashomol.html`: print + tabela detalhada (mesmo padrão I9)
- [ ] Patches locais revertidos após I13 (comando de restauração do perfil `arquitetura/ambiente-local-{projeto}.md`)

---

## Registro no chat

- **I9:** HTML atualizado (E2E) → segue I10 local.
- **I11:** HTML local + validação subagente → segue I12 gate deploy.
- **I14:** `evidenciashomol.html` criado → segue I15.
- **I15:** status validação → encerramento ou correções (e Pós-I15: entrega do HTML + comando, destinado ao card de desenvolvimento).
