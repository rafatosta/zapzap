# Testes e verificações estáticas

## Estratégia

O projeto usa `unittest`, sem depender de pytest. A suíte mistura testes
unitários puros, testes de contrato com mocks e testes de widgets Qt em modo
`offscreen`. Todos são descobertos pelo padrão `tests/test_*.py`.

O objetivo é proteger comportamento, persistência, integração entre camadas e
regressões de UI verificáveis por propriedades. Um teste `offscreen` não
substitui uma sessão gráfica real para foco, cursor, bandeja, compositor,
Wayland/X11 ou aparência final.

## Como executar

Da raiz do repositório, execute a suíte completa:

```bash
python -m unittest discover -s tests -q
```

Para ver cada teste:

```bash
python -m unittest discover -s tests -v
```

Somente módulos de UI:

```bash
python -m unittest discover -s tests -p 'test_*_ui.py' -v
```

Um módulo por descoberta:

```bash
python -m unittest discover -s tests -p 'test_portal_notification_backend.py' -v
```

Um módulo diretamente:

```bash
python tests/test_about_settings_ui.py -v
```

Prefira descoberta quando um módulo importar helpers pelo nome
`qt_test_case`; ela garante que `tests/` esteja no caminho de importação.

## Isolamento Qt

`tests/qt_test_case.py`:

- coloca o checkout local antes de uma versão instalada;
- define `QT_QPA_PLATFORM=offscreen` se a variável não foi fornecida;
- mantém uma única instância de `QApplication`;
- direciona dados, configurações e cache XDG para um diretório temporário.

Testes que criam widgets devem herdar de `QtTestCase`. Testes puros podem herdar
de `unittest.TestCase`. Restaure monkey patches, singletons e variáveis de
ambiente em `tearDown` ou com `addCleanup`; a suíte roda em um único processo e
vazamentos tornam o resultado dependente da ordem.

Nos testes visuais, importe controles básicos de `zapzap.ui.primitives` e
composições de `zapzap.ui.components`. Imports por caminhos internos de uma
feature não devem ser usados para alcançar widgets compartilhados.

## Cobertura por módulo

O inventário abaixo descreve a responsabilidade de cada módulo. O bloco de
nomes é verificado automaticamente; ao criar um teste, acrescente sua linha e
documente o que ele protege.

| Módulo | Contrato protegido |
|---|---|
| `test_about_settings_ui.py` | identidade, links, detalhes técnicos, cópia, licença e créditos |
| `test_account_data_removal.py` | remoção segura e idempotente de dados de perfis desativados |
| `test_accounts_settings_ui.py` | card responsivo com ações diretas, remoção, estados/avisos e diálogo transacional sem moldura |
| `test_appearance_settings_ui.py` | grupos, dependências, layout responsivo, persistência e acessibilidade |
| `test_appimage_packaging.py` | coerência FFmpeg/Qt WebEngine, verificação de ABI, nome final fornecido ao quick-sharun e ausência de renomeação posterior do AppImage/zsync |
| `test_browser_account_lifecycle.py` | registro estável, criação lazy de contas desativadas, reativação, remoção, notificações e encerramento idempotente |
| `test_browser_page_button_ui.py` | avatar sem número, grayscale de conta desativada, ponto de estado, card, temas, escala e clique |
| `test_check_box.py` | API, variantes, tamanhos, pintura, temas, tri-state, mouse, teclado e acessibilidade do CheckBox |
| `test_component_typography.py` | pesos de fonte de primitives, menus, combos, atalhos e tabs |
| `test_debugging_settings_ui.py` | manutenção, relatórios, informações de runtime, cópia e feedback |
| `test_deeplink.py` | validação de URLs WhatsApp e resistência a injeção de script |
| `test_desktop_application_dbus.py` | interface `org.freedesktop.Application` e ativação D-Bus |
| `test_dictionary_options.py` | descoberta dinâmica, nomes amigáveis, ordenação, redimensionamento e fallback de dicionários personalizados |
| `test_documentation_structure.py` | camadas de UI e sincronização entre árvore, inventários técnicos e guia para agentes |
| `test_donations_page.py` | URLs HTTPS oficiais, fallback externo, cartões responsivos/acessíveis, troca imediata de idioma e rota única pela sidebar, Configurações e Sobre |
| `test_external_link_lifecycle.py` | descarte da página WebEngine transitória após abrir links externos |
| `test_gpu_environment.py` | detecção multi-GPU, conectores e seleção de render node |
| `test_grid_thumbnail_cache.py` | limite físico/DPR, reutilização, fallback, seleção e ciclo de vida das miniaturas da grade |
| `test_initial_setup_ui.py` | onboarding, som, fechamento, permissões, dicionários e persistência |
| `test_memory_benchmark.py` | procfs/USS, schema JSON/CSV/Markdown, isolamento WebEngine, factory stub, cenários e comparação relativa |
| `test_network_privacy_settings_ui.py` | proxy, credenciais, aplicar/descartar, restauração e WebRTC |
| `test_notification_sound_setting.py` | mapeamento de som e tipos dos hints Portal/Freedesktop |
| `test_notification_window_activation.py` | conexão QtDBus, tokens Portal/Wayland, startup X11, foco e limpeza |
| `test_notifications_settings_ui.py` | rótulos, dependências, privacidade, som e lembrete de apoio |
| `test_performance_experimental_settings_ui.py` | seção e reinício da decodificação por software |
| `test_permissions_settings_ui.py` | grupos e ações globais/individuais de permissões |
| `test_portal_notification_backend.py` | ciclo de vida, falhas, ações e token no backend Portal |
| `test_segmented_control.py` | seleção exclusiva, sinais, mouse, teclado, acessibilidade, tamanhos, raios e temas |
| `test_send_message_to_number.py` | normalização/URL, lista de países, validação, acessibilidade e teclado do diálogo de conversa por número |
| `test_settings_card.py` | divisores e grupos do card compartilhado em `ui.components` |
| `test_settings_lazy_loading.py` | subprocessos de importação, registro e instanciação lazy, singleton por painel, diagnóstico, empacotamento, APIs públicas e fechamento de Configurações |
| `test_settings_radio_group.py` | divisores do grupo de rádio em `ui.components` |
| `test_software_video_decoding.py` | flag Chromium, persistência, padrão e ordem do bootstrap |
| `test_spellcheck_language_picker.py` | migração, seleção múltipla transacional, pesquisa, limite, recentes, menu e perfis WebEngine |
| `test_system_startup_settings_ui.py` | semântica de fechamento, diálogo nativo e acessibilidade |
| `test_update_checker.py` | versões, política de builds, respostas/falhas assíncronas, metadados seguros e popover acessível compartilhado entre sidebar e Sobre |
| `test_window_state_restore.py` | ciclo de vida compartilhado, restauração normal, maximizada e fullscreen e destruição segura do host CSR |
| `test_windows_packaging.py` | matriz nativa x86_64/ARM64, arquitetura do Python e nomes dos executáveis Windows |

<!-- structure-check:tests:start -->
- `test_about_settings_ui.py`
- `test_account_data_removal.py`
- `test_accounts_settings_ui.py`
- `test_appearance_settings_ui.py`
- `test_appimage_packaging.py`
- `test_browser_account_lifecycle.py`
- `test_browser_page_button_ui.py`
- `test_check_box.py`
- `test_component_typography.py`
- `test_debugging_settings_ui.py`
- `test_deeplink.py`
- `test_desktop_application_dbus.py`
- `test_dictionary_options.py`
- `test_documentation_structure.py`
- `test_donations_page.py`
- `test_external_link_lifecycle.py`
- `test_gpu_environment.py`
- `test_grid_thumbnail_cache.py`
- `test_initial_setup_ui.py`
- `test_memory_benchmark.py`
- `test_network_privacy_settings_ui.py`
- `test_notification_sound_setting.py`
- `test_notification_window_activation.py`
- `test_notifications_settings_ui.py`
- `test_performance_experimental_settings_ui.py`
- `test_permissions_settings_ui.py`
- `test_portal_notification_backend.py`
- `test_segmented_control.py`
- `test_send_message_to_number.py`
- `test_settings_card.py`
- `test_settings_lazy_loading.py`
- `test_settings_radio_group.py`
- `test_software_video_decoding.py`
- `test_spellcheck_language_picker.py`
- `test_system_startup_settings_ui.py`
- `test_update_checker.py`
- `test_window_state_restore.py`
- `test_windows_packaging.py`
<!-- structure-check:tests:end -->

## Como escrever um teste

1. Nomeie o arquivo `test_<comportamento>.py` e a função
   `test_<resultado_observável>`.
2. Teste a API pública ou o contrato entre camadas; evite confirmar apenas a
   implementação interna.
3. Para regressão, faça o teste falhar sem a correção.
4. Isole `QSettings`, SQLite, filesystem, ambiente, clipboard e singletons.
5. Em UI, verifique texto, estado habilitado, sinal, persistência e
   `accessibleName`; não dependa de pixels se uma propriedade semântica basta.
6. Em backends de sistema, use fakes nas fronteiras D-Bus/Qt e mantenha pelo
   menos um roteiro manual em sessão real quando necessário.
7. Atualize este inventário no mesmo commit.

## Verificações estáticas

O analisador conservador procura imports, variáveis, atributos, métodos e
classes provavelmente não usados e compara pacotes Python com
`tool.setuptools.packages`:

```bash
python tests/check_unused_code.py
```

Como sinais Qt, overrides, scripts JavaScript e chamadas dinâmicas podem gerar
falsos positivos, revise cada achado antes de remover código. Para apenas
inventariar:

```bash
python tests/check_unused_code.py --no-fail
```

Para validar somente o manifesto de pacotes:

```bash
python tests/check_unused_code.py --packages-only
```

Valide o contrato documental:

```bash
python tests/test_documentation_structure.py -v
```

Validações complementares:

```bash
python -m compileall -q zapzap tests tools run.py
git diff --check
```

Para mudanças de tradução, XML, AppStream ou Flatpak, acrescente os validadores
específicos descritos em [manutenção](maintenance.md).

## Ordem recomendada

Durante desenvolvimento, rode o módulo afetado. Antes de entregar:

1. módulo afetado em modo verboso;
2. suíte completa;
3. manifestos de pacote e documentação;
4. `compileall` e `git diff --check`;
5. validação manual nas plataformas ou sessões gráficas afetadas.
