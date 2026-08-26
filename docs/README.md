# Documentação técnica do ZapZap

Este diretório é o ponto de entrada para quem mantém o ZapZap, revisa uma
alteração ou atua no projeto por meio de um agente de IA. O `README.md` da raiz
continua voltado a usuários; decisões de implementação e procedimentos
repetíveis pertencem aqui.

## Leitura recomendada

1. [Arquitetura](architecture.md): componentes, fluxo de inicialização,
   persistência, integrações e inventário de pacotes.
2. [Manutenção](maintenance.md): como alterar cada área, invariantes,
   documentação obrigatória, empacotamento e checklist de entrega.
3. [Testes e verificações estáticas](testing.md): suíte `unittest`, isolamento
   Qt, cobertura por módulo e comandos de validação.
4. [Convenção de commits](COMMIT_CONVENTION.md): formato, tipos, escopos,
   exemplos e regras para mensagens sugeridas por agentes.
5. [Opções experimentais de desempenho](performance-experimental.md):
   comportamento e impacto das opções de renderização.
6. [Relatórios de problemas](reporting.md): revisão, sanitização, fila local e
   publicação conduzida pela pessoa no GitHub.

Inventário de documentos técnicos:

<!-- structure-check:docs:start -->
- `COMMIT_CONVENTION.md`
- `README.md`
- `architecture.md`
- `maintenance.md`
- `memory-benchmark.md`
- `performance-experimental.md`
- `reporting.md`
- `testing.md`
<!-- structure-check:docs:end -->

## Fontes de verdade

| Assunto | Fonte de verdade |
|---|---|
| Alterações e histórico de versões | `CHANGELOG.md` |
| Convenção e descrição de commits | `docs/COMMIT_CONVENTION.md` |
| Pacotes distribuídos | `pyproject.toml`, seção `tool.setuptools.packages` |
| Arquitetura e responsabilidades | `docs/architecture.md` |
| Configurações persistidas | classes de domínio em `zapzap/core/config/settings/` |
| Contas | `zapzap/features/accounts/domain/user.py` e banco SQLite |
| Páginas de configurações | `SettingsController._pages()` |
| Traduções-fonte | `po/*.po`, `po/zapzap.pot`, `po/POTFILES` e `po/LINGUAS` |
| Testes automatizados | `tests/test_*.py` |
| Builds e releases | `.github/workflows/` e `.github/packaging/` |

## Regras de atualização

Toda mudança ou adição ao repositório deve atualizar obrigatoriamente a seção
numérica marcada `In development` em `CHANGELOG.md` no mesmo commit ou pull
request. Essa seção deve corresponder a `zapzap.__version__` e acumula todo o
trabalho do ciclo atual sem incrementar a versão a cada mudança. A exigência
também se aplica a documentação, testes, manutenção interna, dependências,
empacotamento e workflows; o histórico Git e as notas geradas pelo GitHub não
substituem o registro curado.

Uma alteração estrutural não está completa sem atualizar esta documentação.
Isso inclui adicionar, remover, renomear ou mover pacotes, funcionalidades,
páginas de configuração, testes, scripts de manutenção, integrações,
empacotamentos ou workflows.

Toda entrega que altere código ou estrutura também deve incluir uma sugestão
de mensagem no padrão Conventional Commits. O formato, os tipos aceitos e a
exigência de corpo para mudanças não triviais estão definidos no guia de
[convenção de commits](COMMIT_CONVENTION.md).

O teste `tests/test_documentation_structure.py` compara inventários marcados nos
documentos com a árvore real. Ele detecta as mudanças estruturais mais objetivas
e é executado pelo workflow de qualidade. Mudanças semânticas — por exemplo,
transferir uma responsabilidade entre duas classes existentes — ainda exigem
revisão humana ou do agente e atualização manual de `architecture.md` ou
`maintenance.md`.
