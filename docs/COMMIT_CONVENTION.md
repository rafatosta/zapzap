# Convenção de commits

O ZapZap usa [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/).

## Formato

```text
<type>(<scope>): <description>
```

O escopo é opcional. Escreva a descrição em inglês, no imperativo, de forma
curta e específica, sem ponto final.

## Tipos

- `feat`: nova funcionalidade;
- `fix`: correção;
- `refactor`: alteração interna sem mudança funcional intencional;
- `perf`: desempenho ou eficiência;
- `test`: testes;
- `docs`: documentação;
- `build`: dependências, ferramentas e infraestrutura de build;
- `ci`: workflows e integração contínua;
- `style`: formatação sem mudança de comportamento;
- `chore`: manutenção que não se enquadra nos tipos anteriores;
- `revert`: reversão.

## Escopos sugeridos

`app`, `accounts`, `browser`, `settings`, `ui`, `notifications`,
`dictionaries`, `downloads`, `permissions`, `proxy`, `packaging`, `flatpak`,
`appimage`, `snap`, `windows`, `macos`, `release` e `docs`.

Use um escopo somente quando ele identificar claramente a área principal da
mudança. Não combine vários nomes em um escopo genérico; quando alterações
independentes puderem ser separadas, proponha commits distintos.

## Exemplos

```text
feat(browser): add native app-lock shortcut
fix(proxy): preserve the active proxy after validation failure
refactor(ui): move shared dialogs to components
test(settings): cover invalid persisted cache values
docs(maintenance): clarify the release workflow
ci(windows): validate native runner architecture
```

## Commits não triviais

Use o corpo para registrar o contexto e os testes realmente executados:

```text
fix(browser): preserve disabled account state

Keep disabled accounts registered without constructing a WebEngine profile
and recreate the profile only after explicit activation.

Tests:
- python tests/test_browser_account_lifecycle.py -v
- python -m compileall -q zapzap tests tools run.py
```

Não registre como aprovado um teste que falhou ou não foi executado. Quando uma
validação não puder ser concluída, descreva a limitação fora da mensagem
sugerida, na entrega da tarefa.

## Mudanças incompatíveis

Use `type!:` ou `type(scope)!:` e acrescente um rodapé `BREAKING CHANGE:` com o
impacto e a migração necessária. Registre a mudança também na seção numérica
marcada `In development` de `CHANGELOG.md`.

## Codex e outros agentes

Ao concluir uma unidade lógica, o agente deve revisar `git status` e `git diff`,
executar as verificações aplicáveis, atualizar `CHANGELOG.md` e produzir uma
mensagem Conventional Commit adequada. Toda resposta final após modificar
arquivos do repositório deve incluir pelo menos uma mensagem sugerida, mesmo
para mudanças pequenas.

Alterações independentes devem receber mensagens separadas. Mudanças não
triviais devem incluir também um corpo opcional com contexto e os testes
realmente executados. O agente não deve criar commits nem reescrever histórico
publicado sem instrução explícita.

## Relação com o changelog

A mensagem de commit descreve uma unidade lógica de trabalho; o changelog
mantém o histórico curado do ciclo de versão. Uma não substitui a outra. Toda
mudança ou adição continua obrigada a atualizar `CHANGELOG.md`, conforme o
contrato de [manutenção](maintenance.md#registro-obrigatório-de-mudanças).

## Validação

A convenção é atualmente verificada durante a revisão. Um validador local ou de
CI deve ser introduzido em uma mudança própria, com testes de exemplos aceitos
e rejeitados, antes de ser tratado como requisito automatizado do projeto.
