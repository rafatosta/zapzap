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
| `test_browser_account_lifecycle.py` | registro estável, criação lazy de contas desativadas, isolamento/retentativa de perfil com erro, reativação, remoção, notificações e encerramento idempotente |
| `test_browser_page_button_ui.py` | avatar sem número, grayscale de conta desativada, ponto de estado, card, temas, escala e clique |
| `test_check_box.py` | API, variantes, tamanhos, pintura, temas, tri-state, mouse, teclado e acessibilidade do CheckBox |
| `test_component_typography.py` | pesos de fonte de primitives, menus, combos, atalhos e tabs |
| `test_debugging_settings_ui.py` | manutenção, relatórios, informações de runtime, cópia e feedback |
| `test_deeplink.py` | validação de URLs WhatsApp e resistência a injeção de script |
| `test_desktop_application_dbus.py` | interface `org.freedesktop.Application` e ativação D-Bus |
| `test_dictionary_manager.py` | store próprio, migração, catálogo/cache, rede segura, downloads atômicos, importação/remoção, diálogo compartilhado, provisionamento único do idioma do sistema e ausência de dicionários nos pacotes oficiais |
| `test_dictionary_options.py` | descoberta dinâmica, nomes amigáveis, ordenação, redimensionamento e fallback de dicionários personalizados |
| `test_display_backend.py` | seleção automática/forçada do backend Qt, precedência de ambiente/CLI/plataforma e migração da chave Wayland legada |
| `test_documentation_structure.py` | camadas de UI, ciclo numérico versionado do changelog e sincronização entre árvore, inventários técnicos, convenção de commits e guia para agentes |
| `test_donations_page.py` | URLs HTTPS oficiais, fallback externo, cartões responsivos/acessíveis, troca imediata de idioma e rota única pela sidebar, Configurações e Sobre |
| `test_external_link_lifecycle.py` | classificação interna/externa de pop-ups, profile compartilhado, entrega única ao navegador e cleanup no fechamento/shutdown |
| `test_gpu_environment.py` | detecção multi-GPU, conectores e seleção de render node |
| `test_grid_thumbnail_cache.py` | limite físico/DPR, reutilização, fallback, seleção e ciclo de vida das miniaturas da grade |
| `test_http_cache_size.py` | cache em MiB, tipos de cache, política de cookies, memória JavaScript, autocura persistida e fallbacks de perfil sem WebEngine real |
| `test_initial_setup_ui.py` | onboarding, som, fechamento, permissões, dicionários e persistência |
| `test_memory_benchmark.py` | procfs/USS, schema JSON/CSV/Markdown, isolamento WebEngine, factory stub, cenários e comparação relativa |
| `test_network_privacy_settings_ui.py` | proxy exclusivamente global, strict proxy, credenciais, aplicar/descartar, feedback de falha do Qt, restauração e WebRTC |
| `test_notification_sound_setting.py` | mapeamento de som e tipos dos hints Portal/Freedesktop |
| `test_notification_window_activation.py` | conexão QtDBus, tokens Portal/Wayland, startup X11, foco e limpeza |
| `test_notifications_settings_ui.py` | rótulos, dependências, privacidade, som e lembrete de apoio |
| `test_performance_experimental_settings_ui.py` | perfis de renderização, controles manuais, migração e reinício |
| `test_permissions_settings_ui.py` | grupos e ações globais/individuais de permissões |
| `test_portal_notification_backend.py` | ciclo de vida, falhas, ações e token no backend Portal |
| `test_qt_parameter_fallbacks.py` | escala, tema da bandeja, geometria, tipos e fail-closed do proxy global, zoom e download inválidos com autocura ou fallback restrito |
| `test_reporting.py` | sanitização, minimização, Markdown, fila/TTL e captura local de encerramentos inesperados |
| `test_reporting_ui.py` | formulário em duas etapas, prévia canônica, edição, cancelamento, clipboard e abertura segura do GitHub |
| `test_segmented_control.py` | seleção exclusiva, sinais, mouse, teclado, acessibilidade, tamanhos, raios e temas |
| `test_send_message_to_number.py` | normalização/URL, lista de países, validação, acessibilidade e teclado do diálogo de conversa por número |
| `test_settings_card.py` | divisores e grupos do card compartilhado em `ui.components` |
| `test_settings_lazy_loading.py` | subprocessos de importação, registro e instanciação lazy, singleton por painel, diagnóstico, empacotamento, APIs públicas e fechamento de Configurações |
| `test_settings_radio_group.py` | divisores do grupo de rádio em `ui.components` |
| `test_software_video_decoding.py` | presets, flags Chromium de renderização/strict proxy, persistência e ordem do bootstrap |
| `test_spellcheck_language_picker.py` | migração, seleção múltipla transacional, pesquisa, limite, recentes, menu e perfis WebEngine |
| `test_system_startup_settings_ui.py` | semântica de fechamento, diálogo nativo, seleção do backend gráfico, reinício e acessibilidade |
| `test_unix_signal_shutdown.py` | ponte POSIX, restauração do estado global e `SIGTERM` real chegando a `aboutToQuit` em subprocesso isolado |
| `test_update_checker.py` | versões, política de builds, respostas/falhas assíncronas, metadados seguros e popover acessível compartilhado entre sidebar e Sobre |
| `test_whatsapp_app_lock.py` | botão acessível da sidebar, conta ativa, foco, sequência Qt nativa e estados transitórios do WebView |
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
- `test_dictionary_manager.py`
- `test_dictionary_options.py`
- `test_display_backend.py`
- `test_documentation_structure.py`
- `test_donations_page.py`
- `test_external_link_lifecycle.py`
- `test_gpu_environment.py`
- `test_grid_thumbnail_cache.py`
- `test_http_cache_size.py`
- `test_initial_setup_ui.py`
- `test_memory_benchmark.py`
- `test_network_privacy_settings_ui.py`
- `test_notification_sound_setting.py`
- `test_notification_window_activation.py`
- `test_notifications_settings_ui.py`
- `test_performance_experimental_settings_ui.py`
- `test_permissions_settings_ui.py`
- `test_portal_notification_backend.py`
- `test_qt_parameter_fallbacks.py`
- `test_reporting.py`
- `test_reporting_ui.py`
- `test_segmented_control.py`
- `test_send_message_to_number.py`
- `test_settings_card.py`
- `test_settings_lazy_loading.py`
- `test_settings_radio_group.py`
- `test_software_video_decoding.py`
- `test_spellcheck_language_picker.py`
- `test_system_startup_settings_ui.py`
- `test_unix_signal_shutdown.py`
- `test_update_checker.py`
- `test_whatsapp_app_lock.py`
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

## Validação manual do proxy estrito

Use um perfil XDG descartável e nunca credenciais reais. Estes cenários
confirmam comportamento observável, não uma alegação de ausência absoluta de
vazamentos.

### Proxy indisponível no startup

1. Configure um proxy HTTP ou SOCKS5 em `127.0.0.1` e uma porta sem serviço.
2. Ative **Strict proxy isolation**, aplique e reinicie o ZapZap.
3. Confirme nos diagnósticos que
   `--force-webrtc-ip-handling-policy=disable_non_proxied_udp` está presente.
4. Confirme que o WhatsApp Web falha ao conectar e que as chaves `proxy/*` não
   mudam para `NoProxy`.

### Proxy interrompido durante a sessão

1. Inicie um proxy local de teste e abra o ZapZap por ele.
2. Interrompa o proxy e provoque uma nova conexão ou recarregamento.
3. Confirme a falha de conexão e a ausência de troca automática para uma
   conexão direta.

### WebRTC

Com proxy HTTP/SOCKS5 explícito e modo estrito ativos após reinício, confirme a
flag nativa nos diagnósticos. Se houver captura de tráfego disponível, verifique
que o Chromium não cria UDP WebRTC não proxyficado. Desative separadamente o
WebRTC Shield legado para confirmar que a política nativa não depende do script
`webrtc_shield.js`. Repita com proxy do sistema e confirme que a UI não promete
isolamento estrito e que a flag não é aplicada.

## Validação manual do bloqueio do WhatsApp Web

Use contas de teste e uma sessão gráfica real; `offscreen` confirma a sequência
Qt, mas não o foco do compositor nem a reação de uma versão remota do WhatsApp
Web.

1. Com o bloqueio ainda não configurado, clique no cadeado da sidebar e confirme
   que o WhatsApp Web abre o próprio fluxo de configuração, sem tela do ZapZap.
2. Conclua a configuração dentro do WhatsApp Web e clique novamente; confirme
   que somente a conta selecionada é bloqueada.
3. Com duas contas, alterne entre elas e repita o clique, verificando que a conta
   em segundo plano não recebe a ação.
4. Repita durante carregamento, após desativar uma conta e depois de reconstruir
   a interface; confirme ausência de travamento, ação duplicada ou referência à
   página anterior.
5. Confirme também o atalho digitado diretamente dentro do WhatsApp Web e os
   modos de janela nativa e CSR em cada plataforma mantida.

## Validação manual de dicionários QtWebEngine

Use uma sessão gráfica real e diretórios XDG temporários; `offscreen` valida a
UI e as fronteiras, mas não comprova que o processo Chromium recarrega arquivos
durante a execução.

1. Inicie com um diretório padrão cujo `manifest.json` corresponda exatamente
   aos nomes e tamanhos dos `.bdic`. Confirme que
   `QTWEBENGINE_DICTIONARIES_PATH` permanece nesse diretório, sem cópia, rede ou
   ações de gerenciamento. Em um perfil limpo, confirme a seleção inicial do
   idioma do sistema e que uma escolha manual posterior é preservada.
2. Abra **Gerenciar dicionários**, instale um idioma e selecione-o em
   **Idiomas ativos**. Em um campo editável real do WhatsApp Web, confirme a
   disponibilidade da correção e a atualização dos perfis já abertos.
3. Cancele um download grande e confirme que não existe `.bdic` final/parcial;
   repita com a rede indisponível e confirme que instalados e cache continuam
   visíveis.
4. Remova um idioma não ativo e, separadamente, o último idioma ativo. Confirme
   a pergunta reforçada, a desativação explícita e o comportamento do WebEngine.
5. Reinicie e confirme persistência, migração idempotente e ausência de
   alteração na pasta legada. Repita nos formatos/plataformas mantidos antes de
   retirar qualquer semente embarcada.
6. Repita com o diretório padrão ausente, vazio e com cinco `.bdic` mas sem
   manifesto. Confirme em todos esses casos o uso do store gerenciado, a ação
   **Gerenciar** visível e um único download automático para o locale do sistema
   (ou uma variante do mesmo idioma), nunca para um idioma sem relação. Os
   demais só podem ser instalados manualmente. Reinicie, remova voluntariamente
   o idioma provisionado e confirme que ele não é baixado de novo em silêncio.
7. Nos artefatos oficiais de AppImage, Snap e Flatpak, confirme que nenhum
   `.bdic` ou `QTWEBENGINE_DICTIONARIES_PATH` interno é instalado/configurado,
   que **Gerenciar** aparece e que o idioma do sistema é salvo exclusivamente
   no store gravável. No Flatpak, confirme também que o cleanup retirou o
   diretório herdado da base PyQt do artefato final.

Se o Chromium falhar com `sandbox_host_linux.cc ... Operation not permitted`,
repita fora do sandbox e registre a limitação; não considere esse cenário como
validação do spellchecker em runtime.

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

Esse contrato lê `zapzap.__version__` estaticamente, sem importar PyQt, e exige
que ela seja numérica e corresponda à primeira seção versionada. Durante o
desenvolvimento, essa seção deve ser a única marcada `In development` e seu
link de comparação deve terminar em `HEAD`; no fechamento para publicação, ela
deve conter uma data válida e o link deve terminar na própria versão. O teste
também verifica a release datada imediatamente anterior e a ordem das versões,
sem impor um incremento patch que impediria uma mudança minor ou major decidida
pelo mantenedor.

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
