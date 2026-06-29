# Arquitetura ideal do ZapZap

Estrutura conceitual completa proposta para o projeto ZapZap, organizada em camadas de apresentação, aplicação, domínio, infraestrutura, web, recursos e debugging.

> Este diretório documenta uma arquitetura ideal/conceitual. Os arquivos aqui
> são stubs descritivos e não fazem parte do runtime atual da aplicação.

## Convenções

- [Padrão de nomenclatura de arquivos e diretórios](NAMING.md)

## Ferramentas de desenvolvimento

As ferramentas auxiliares ficam em `docs/ideal_architecture/tools`, fora do pacote conceitual `zapzap`, para deixar claro que elas servem ao desenvolvimento e não ao runtime do aplicativo.

## Entrypoint

A arquitetura ideal mantém `zapzap/__main__.py` como entrypoint do pacote para `python -m zapzap`, delegando o bootstrap para `zapzap/app/main.py`.
