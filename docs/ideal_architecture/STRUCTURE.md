# Estrutura conceitual gerada

Este diretório contém um espelho conceitual da arquitetura ideal do ZapZap.

- `zapzap/app`: composição, bootstrap e ciclo de vida.
- `zapzap/domain`: modelos, contratos de repositório e regras puras.
- `zapzap/application`: casos de uso, DTOs e portas.
- `zapzap/presentation`: widgets, presenters, dialogs e UI gerada/fonte.
- `zapzap/web`: integração QtWebEngine e bridges.
- `zapzap/infrastructure`: adapters concretos de persistência, plataforma, notificações, filesystem e rede.
- `zapzap/resources`: ícones, temas e assets visuais.
- `zapzap/debugging`: crash handling e relatórios.
- `zapzap/i18n`: internacionalização.
- `zapzap/tools`: ferramentas de desenvolvimento.

Nenhum arquivo contém implementação real. Cada stub descreve sua responsabilidade para orientar a migração incremental.

## Convenção de nomes

Os arquivos e diretórios deste esqueleto seguem nomes em minúsculas com `snake_case`. Consulte [`NAMING.md`](NAMING.md) para regras detalhadas, sufixos recomendados e exceções aceitáveis.
