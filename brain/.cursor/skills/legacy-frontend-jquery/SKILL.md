---
name: legacy-frontend-jquery
description: >-
  Altera views PHP, JavaScript legado e assets jQuery do projeto atual. Use ao
  editar máscaras de input, validação client-side, formulários CRM ou arquivos
  em application/views/ e assets/js/.
---

# Frontend legado — jQuery + views PHP

## Documentação oficial (consultar quando necessário)

| Tema | URL |
|------|-----|
| jQuery 3 API | https://api.jquery.com/ |
| jQuery `.on()` / delegação | https://api.jquery.com/on/ |
| MDN JavaScript | https://developer.mozilla.org/en-US/docs/Web/JavaScript |
| MDN HTML forms | https://developer.mozilla.org/en-US/docs/Learn/Forms |
| MDN input types | https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input |
| jQuery Mask Plugin | https://igorescobar.github.io/jQuery-Mask-Plugin/ |

## Estrutura no projeto

```
application/views/          # PHP embarca HTML, scripts inline
assets/js/                  # cnpj-validator.js, cliente-cnpj-handler.js, ...
assets/css/
```

Controllers declaram assets:

```php
public $js = array('cnpj-validator.js', 'cliente-cnpj-handler.js');
```

## Padrões deste codebase

- **jQuery** (não React/Vue) — eventos via `$(document).ready()` ou delegação
- Máscaras de CNPJ/CPF em JS dedicado; validação duplicada server-side obrigatória
- Views misturam PHP (`<?=`, `<?php echo`) com HTML — manter o padrão do arquivo
- Bootstrap legado + Font Awesome em `assets/`

## Regras

1. Validação client-side é **UX**; regra de negócio fica no PHP (library/helper)
2. Não introduzir bundler, TypeScript ou framework SPA
3. Testar máscaras alfanuméricas (CNPJ IN RFB 2.229/2024) em create **e** edit
4. Evitar XSS: escapar output com helpers/views existentes (`htmlspecialchars` onde já usado)

## Testes relacionados

- E2E validator: `testes/E2E/specs/{card-id}/` — skill [ambientes-e-testes](../ambientes-e-testes/SKILL.md)
- Homol URL (telas): `testes/homol/specs/{card-id}/`

## UX de formulários

- Labels e mensagens de erro já existentes no módulo — reutilizar textos
- Campos obrigatórios: evidência homol exige formulário preenchido antes do POST
