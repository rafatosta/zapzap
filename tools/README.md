# Ferramentas de desenvolvimento

Este diretório representa ferramentas de apoio ao desenvolvimento e à manutenção
do projeto. Ele fica **fora** do pacote `zapzap` porque não faz parte do runtime
do aplicativo.

## Responsabilidade

As ferramentas neste diretório devem cuidar de tarefas como:

- executar o aplicativo localmente em modo de desenvolvimento;
- executar ou preparar ambientes de empacotamento, como Flatpak;
- compilar arquivos `.ui` para Python;
- atualizar, compilar ou validar traduções;
- automatizar rotinas auxiliares de desenvolvimento.

## Regra arquitetural

Arquivos em `tools/` podem importar o pacote `zapzap` para executar ou preparar o
aplicativo, mas o pacote `zapzap` não deve depender de `tools/`.

Fluxo permitido:

```text
tools -> zapzap
```

Fluxo proibido:

```text
zapzap -> tools
```

Essa separação mantém o pacote do aplicativo limpo e evita que utilitários de
desenvolvimento sejam carregados em produção.
