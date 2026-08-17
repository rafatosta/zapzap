# Guia para agentes de manutenção

Antes de alterar o ZapZap, leia `CHANGELOG.md`, `docs/README.md`,
`docs/architecture.md`, `docs/maintenance.md` e a seção pertinente de
`docs/testing.md`.

- Preserve comportamento, chaves e valores persistidos; migre explicitamente
  quando uma mudança for inevitável.
- Prefira domínios em `zapzap/core/config/settings/`, `ui.primitives` para
  controles básicos, `ui.components` para composições visuais, paleta Qt,
  `QFont` e `Typography`; não coloque widgets reutilizáveis dentro de features.
- Mantenha IDs persistidos separados de rótulos traduzidos.
- Audite páginas, backends e plataformas irmãs quando a mudança for transversal.
- Não considere `offscreen` prova de foco, cursor, compositor ou aparência real.
- Registre obrigatoriamente toda mudança ou adição na seção numérica marcada
  `In development` de `CHANGELOG.md`, inclusive documentação, testes,
  manutenção interna, dependências, empacotamento e workflows.
- Mantenha `zapzap.__version__` numérica e igual à versão em desenvolvimento.
  Ao abrir o ciclo seguinte depois de publicar, derive-a da última tag estável
  publicada (`X.Y` vira `X.Y.1`; `X.Y.Z` vira `X.Y.(Z+1)`). Saltos minor ou
  major exigem uma versão de destino informada explicitamente pelo mantenedor.
- Não conclua uma alteração estrutural sem atualizar a documentação técnica e
  seus inventários marcados no mesmo conjunto de mudanças.

Antes da entrega, execute:

```bash
python -m unittest discover -s tests -q
python tests/check_unused_code.py --packages-only
python tests/test_documentation_structure.py -v
python -m compileall -q zapzap tests tools run.py
git diff --check
```

Se uma validação não puder ser executada, registre claramente qual foi e por
quê. Consulte `docs/maintenance.md` para validadores específicos de tradução,
AppStream, Flatpak e empacotamento.
