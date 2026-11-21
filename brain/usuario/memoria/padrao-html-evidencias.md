---
name: padrao-html-evidencias
description: "Layout OBRIGATÓRIO do evidencias.html: <style> mínimo no head + TODO estilo inline; modelo de referência 155045 (solides-crm)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6caeefc6-08aa-47ac-96bc-325bef5d426b
  modified: 2026-07-20T19:27:48.736Z
---

O `evidencias.html` de sustentação segue o **layout de referência 155045** (definido pelo usuário em 16/07/2026, substitui o antigo modelo 150624 baseado em classes CSS).

**Arquivo de referência (modelo canônico):** `/var/www/html/solides-crm/docs/evidencias/html/consumo-creditos-profiler/155045/evidencias.html`

**Princípio central:** `<style>` no `<head>` é **mínimo** (só reset e tipografia base); **TODO o resto é estilo inline** em cada elemento. Isso torna o HTML portável e sobrevive ao sanitizador do ADO (que remove classes e trunca CSS do head).

**`<style>` mínimo do head (copiar tal qual):**
```
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Calibri, Arial, sans-serif; font-size: 11pt; line-height: 1.45; color: #1a1a1a; margin: 0; padding: 16px 12px 32px; background: #fff; }
h1 { font-size: 14pt; color: #0f3d5c; margin: 0 0 4px; }
h2 { font-size: 12pt; color: #0f3d5c; margin-top: 22px; margin-bottom: 8px; }
h3 { font-size: 11pt; color: #333; margin-top: 20px; margin-bottom: 6px; }
p { margin: 8px 0; }
```

**Ordem das seções:** (1) `h1` + `<p>` de meta (Card | Origem/Ticket | Sistema | Data | Ambiente); (2) **Resposta ao incidente** (div verde); (3) **Proposta de solução** (`h2` + div verde, com SQL de correção em `<pre>` quando houver); (4) **Resumo executivo** (`h2` + tabela);

**CONTEÚDO de cada bloco (erro recorrido no card 156704 em 20/07/2026 — não repetir):** o bloco **"Resposta ao incidente"** contém a CONTEXTUALIZAÇÃO (o que a área pediu + o diagnóstico/achado), NÃO a ação. O bloco **"Proposta de solução"** contém a AÇÃO CONCRETA a executar (comando/SQL/passos, ex.: adicionar var no `.env`, query de correção). Não inverter: descrição do problema → "Resposta ao incidente"; o que fazer → "Proposta de solução". Convém diferenciar visualmente: incidente em bloco azul (`border-left:#0f3d5c;background:#f8fbfd`), proposta em bloco verde (`border-left:#28a745;background:#f4fff6`), como no exemplo `partners/.../152069-Login-Unificado-Parceiros-LoveCRM/evidencias.html`. (5) **Causa raiz** (`h2` + parágrafos, síntese destacada); (6) **Evidências — consultas SQL executadas (produção · data)** (`h2`; cada consulta = `h3` + `<pre>` SQL + tabela de resultado + `<p>` resultado); (7) **Conclusão** (div verde); (8) **Status da análise** (`<p>`); (9) **Rodapé** (div border-top).

**Padrões de estilo inline (fixos):**
- Cabeçalho azul: `#0f3d5c`. Borda cinza: `#d0d0d0`. Texto: `#1a1a1a`. Muted: `#555`.
- **Bloco verde** (resposta/proposta/conclusão): `<div style="border:1px solid #b8dfc4;border-left:4px solid #28a745;background:#f4fff6;padding:12px 14px;margin:8px 0 16px;">`.
- **Tabela**: envolver em `<div style="width:100%;overflow-x:auto;margin:12px 0 16px;">` + `<table border="1" cellpadding="5/6" cellspacing="0" style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:8-9.5pt;word-break:break-word;">` + `<colgroup>` com larguras + `<thead><tr style="background:#f0f4f8;color:#0f3d5c;">`.
- **Linhas de destaque**: `bgcolor="#f8d7da"` (vermelho/erro), `bgcolor="#fff3cd"` (amarelo/atenção), `bgcolor="#d4edda"` (verde/ok).
- **SQL**: `<pre style="font-family:Consolas,monospace;font-size:8.5pt;background:#f4f4f4;padding:12px;border:1px solid #ddd;overflow-x:auto;white-space:pre-wrap;margin:8px 0 12px;">` (SQL de correção usa `background:#eef7f0;border:1px solid #cfe6d6`). Escapar `<` `>` como `&lt;` `&gt;`.
- **Bloco de resultado** (após cada consulta): `<p style="font-size:10pt;background:#f4fff6;border-left:3px solid #28a745;padding:8px 12px;margin:8px 0 16px;">` (ok verde); atenção `background:#fff3cd;border-left:3px solid #ffc107`; erro `background:#fff5f5;border-left:3px solid #dc3545`.
- **Rodapé**: `<div style="margin-top:28px;padding-top:12px;border-top:1px solid #d0d0d0;font-size:9pt;color:#555;">` — linha única com card/cliente/chaves/data.

**Prints:** NÃO usar `<img>`. Citar por nome no texto ("Print anexado ao card: nome.png ..."), pois o ADO remove imagens via API. Os PNGs ficam em `docs/evidencias/assets/{tipo}/{card-id}/`.

**Why:** o usuário definiu esse layout como padrão único ("deixe registrado qual é o layout e definições para fazer sempre do mesmo jeito") apontando o 155045. O estilo inline pesado é mais robusto no ADO que o modelo antigo com classes no `<head>` (o sanitizador do ADO derruba classes e trunca `font-family` de `pre`).

**How to apply:** antes de montar qualquer `evidencias.html`, reler o 155045 e replicar estrutura/estilos inline acima. Postagem no ADO: ver [[ado-postagem-script-guid-projeto]]. Nomenclatura: [[nomenclatura-docs-card-id]]. Ambiente: [[ambiente-cit-porta-banco-divergentes]].
