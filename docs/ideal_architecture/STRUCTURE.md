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
- `tools`: ferramentas de desenvolvimento fora do pacote do aplicativo.

Nenhum arquivo contém implementação real. Cada stub descreve sua responsabilidade para orientar a migração incremental.

## Convenção de nomes

Os arquivos e diretórios deste esqueleto seguem nomes em minúsculas com `snake_case`. Consulte [`NAMING.md`](NAMING.md) para regras detalhadas, sufixos recomendados e exceções aceitáveis.

## Ferramentas de desenvolvimento

A pasta `tools` fica fora de `zapzap` porque não pertence ao runtime do aplicativo. Ela representa comandos auxiliares de desenvolvimento, execução local, empacotamento, compilação de UI e manutenção de traduções. A dependência permitida é `tools -> zapzap`; o pacote `zapzap` não deve importar `tools`.
