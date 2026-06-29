# Padrão de nomenclatura da arquitetura ideal

Este documento define o padrão de nomes usado no esqueleto conceitual em
`docs/ideal_architecture/zapzap`.

## Regra geral

Todos os diretórios e arquivos do esqueleto usam nomes em **minúsculas** e, quando
necessário, separados por **underscore** (`snake_case`).

Exemplos:

- `main_window.py`
- `settings_registry.py`
- `notification_gateway.py`
- `download_location_provider.py`
- `freedesktop_backend.py`

Essa escolha segue a convenção mais comum em projetos Python e evita misturar
nomes de arquivos em `PascalCase`, `camelCase` ou formatos diferentes dentro da
mesma árvore.

## Diretórios

Diretórios devem representar camadas, features ou adapters e também devem usar
`snake_case` em minúsculas.

Exemplos:

- `application/use_cases`
- `application/interfaces`
- `domain/models`
- `domain/repositories`
- `presentation/main_window`
- `presentation/client_side_rendering`
- `infrastructure/notifications/freedesktop`
- `infrastructure/platform/autostart`

## Arquivos Python

Arquivos Python devem usar `snake_case.py`.

Regras:

- usar substantivos para modelos, DTOs, repositories e adapters;
- usar verbo + objeto para casos de uso;
- usar sufixos consistentes para papéis arquiteturais.

Exemplos por categoria:

| Categoria | Padrão | Exemplo |
| --- | --- | --- |
| Modelo de domínio | `<conceito>.py` | `user.py` |
| DTO | `<conceito>_dto.py` | `notification_dto.py` |
| Repository | `<conceito>_repository.py` | `settings_repository.py` |
| Gateway/porta | `<conceito>_gateway.py` | `download_gateway.py` |
| Caso de uso | `<verbo>_<objeto>.py` | `create_user.py` |
| Presenter | `<contexto>_presenter.py` | `appearance_settings_presenter.py` |
| Adapter | `<plataforma>_<papel>_adapter.py` | `windows_autostart_adapter.py` |
| Factory | `<conceito>_factory.py` | `profile_factory.py` |
| Configurator | `<conceito>_configurator.py` | `proxy_configurator.py` |
| Provider | `<conceito>_provider.py` | `user_agent_provider.py` |
| Service | `<conceito>_service.py` | `autostart_service.py` |

## Casos de uso

Casos de uso devem ter nomes orientados a ação, pois representam operações da
aplicação.

Formato recomendado:

```text
<verbo>_<objeto>.py
```

Exemplos:

- `create_user.py`
- `update_user.py`
- `remove_user.py`
- `load_users.py`
- `apply_theme.py`
- `configure_proxy.py`
- `handle_download.py`
- `show_notification.py`
- `run_onboarding.py`

## Interfaces, ports e adapters

Interfaces da camada `application/interfaces` usam sufixo `_gateway.py` para
indicar portas consumidas pela aplicação.

Exemplos:

- `notification_gateway.py`
- `theme_gateway.py`
- `download_gateway.py`
- `platform_gateway.py`
- `web_profile_gateway.py`

Implementações concretas ficam em `infrastructure` e devem usar nomes que
explicitem tecnologia, plataforma ou backend.

Exemplos:

- `qt_settings_repository.py`
- `sqlite_user_repository.py`
- `freedesktop_backend.py`
- `portal_backend.py`
- `windows_backend.py`
- `linux_autostart_adapter.py`
- `windows_autostart_adapter.py`

## Arquivos de UI

Arquivos fonte do Qt Designer devem manter a extensão `.ui` e também usar
`snake_case`.

Exemplos:

- `mainwindow.ui`
- `browser.ui`
- `settings.ui`

Arquivos Python gerados a partir de `.ui` devem usar o prefixo `ui_`:

- `ui_mainwindow.py`
- `ui_browser.py`
- `ui_settings.py`
- `ui_pages.py`

## Scripts e assets

Scripts JavaScript e arquivos CSS também devem seguir nomes em minúsculas com
`snake_case` quando houver mais de uma palavra.

Exemplos:

- `theme_controller.js`
- `webrtc_shield.js`
- `nord.css`

## Nomes de classes dentro dos arquivos

Embora os arquivos usem `snake_case`, as classes Python devem seguir `PascalCase`.

Exemplos:

| Arquivo | Classe esperada |
| --- | --- |
| `main_window.py` | `MainWindow` |
| `settings_registry.py` | `SettingsRegistry` |
| `notification_gateway.py` | `NotificationGateway` |
| `download_location_provider.py` | `DownloadLocationProvider` |
| `freedesktop_backend.py` | `FreedesktopNotificationBackend` |

## Exceções aceitáveis

Exceções devem ser raras e documentadas no próprio diretório ou arquivo. São
aceitáveis apenas quando houver integração com ferramenta externa, padrão de
empacotamento ou compatibilidade com arquivo legado.

Exemplos possíveis:

- nomes exigidos por ferramentas de build;
- arquivos gerados automaticamente por Qt ou empacotadores;
- assets cujo nome seja definido por convenção externa.

## Objetivo do padrão

O objetivo é tornar a árvore previsível, facilitar navegação, reduzir variação de
estilo e deixar claro o papel arquitetural de cada arquivo apenas pelo nome.

## Localização de ferramentas

Ferramentas de desenvolvimento devem ficar em `tools/`, fora do pacote `zapzap`.
Esses arquivos seguem as mesmas regras de nomenclatura (`snake_case`) por serem
scripts auxiliares do repositório, mas não devem ser tratados como módulos do
runtime do aplicativo.
