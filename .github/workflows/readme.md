# Workflows

## Publicação do Snap

O workflow `release.yml` compila o pacote Snap e publica na Snap Store somente
quando uma GitHub Release normal é publicada.

### Comportamento final

| Evento | Build snap | Anexa `.snap` na GitHub Release | Publica na Snapcraft |
| --- | ---: | ---: | ---: |
| `workflow_dispatch` com `publish = false` | Sim | Não, só artifact | Não |
| `workflow_dispatch` com `publish = true` | Sim | Sim | Não |
| `push` de tag | Sim | Sim | Não |
| GitHub pre-release publicada | Sim | Sim | Não |
| GitHub release normal publicada | Sim | Sim | Sim, em `stable` |

### Secret necessário

Para publicar na Snap Store, configure o secret `STORE_LOGIN` em:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

O valor do secret deve ser gerado uma vez em uma máquina com Snapcraft
autenticado e será usado no workflow como `SNAPCRAFT_STORE_CREDENTIALS`:

```bash
snapcraft login
snapcraft export-login --snaps zapzap --channels stable -
```
