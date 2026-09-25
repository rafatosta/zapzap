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

O workflow `quality.yml` executa `test_download_settings.py`,
`test_taskbar_badge.py` e `test_plain_text_paste.py` também em Ubuntu,
Windows e macOS. Essa matriz protege os contratos portáveis do gerenciador de
downloads, das ativações da bandeja e do atalho nativo de colagem sem
formatação; a aparência exata dos ícones nativos, o comportamento imposto pelo
shell e a integração real com o clipboard ainda exigem validação gráfica em
cada sistema.

## Cobertura por módulo

O inventário abaixo descreve a responsabilidade de cada módulo. O bloco de
nomes é verificado automaticamente; ao criar um teste, acrescente sua linha e
documente o que ele protege.

| Módulo | Contrato protegido |
|---|---|
| `test_about_settings_ui.py` | identidade, links, detalhes técnicos, cópia, licença e créditos |
| `test_account_data_removal.py` | remoção segura e idempotente de dados de perfis desativados |
| `test_accounts_settings_ui.py` | card responsivo com ações diretas, remoção, estados/avisos e diálogo transacional sem moldura |
| `test_appearance_settings_ui.py` | grupos, dependências, subopções condicionais da sidebar, layout responsivo, persistência e acessibilidade |
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
| `test_download_settings.py` | modos persistidos, permissão múltipla sem bypass temporal, fila global, ordem/dispensa de itens, indicador compacto, ícones nativos de tipo, elisão de nomes, sanitização de alvos e abertura separada de PDF/imagens por MIME verificado |
| `test_documentation_structure.py` | camadas de UI, ciclo numérico versionado do changelog e sincronização entre árvore, inventários técnicos, convenção de commits e guia para agentes |
| `test_donations_page.py` | URLs HTTPS oficiais, fallback externo, cartões responsivos/acessíveis, troca imediata de idioma e rota única pela sidebar, Configurações e Sobre |
| `test_external_link_lifecycle.py` | classificação interna/externa de pop-ups, profile compartilhado, entrega única ao navegador e cleanup no fechamento/shutdown |
| `test_floating_account_button.py` | botão flutuante visível apenas com a sidebar oculta, avatar sincronizado com a conta ativa e clique reaproveitando a grade existente de troca de contas |
| `test_freedesktop_notification_backend.py` | avisos nas saídas antecipadas da inicialização D-Bus, falhas de `Notify`/`CloseNotification`, aviso único na transição para indisponível e fachada sem backend |
| `test_global_mute.py` | estado persistente de mute global, sincronização dos controles, fan-out para todas as contas e roteamento do atalho de colagem para a conta ativa |
| `test_gpu_environment.py` | detecção multi-GPU, conectores e seleção de render node |
| `test_browser_grid_view_ui.py` | cartões nativos da grade, avatar/nome, badge de não lidas, atualização por sinal e seleção por ID |
| `test_http_cache_size.py` | cache em MiB, tipos de cache, política de cookies, memória JavaScript, autocura persistida e fallbacks de perfil sem WebEngine real |
| `test_initial_setup_ui.py` | onboarding, som, fechamento, permissões, dicionários e persistência |
| `test_main_window_shortcuts.py` | atalhos da janela principal, ações de menu correspondentes e descoberta do Ctrl+J |
| `test_memory_benchmark.py` | procfs/USS, schema JSON/CSV/Markdown, isolamento WebEngine, factory stub, cenários e comparação relativa |
| `test_native_titlebar_theme.py` | sincronização do esquema claro/escuro com decorações nativas, modo automático e fallback para Qt antigo |
| `test_network_privacy_settings_ui.py` | proxy exclusivamente global, strict proxy, credenciais, aplicar/descartar, feedback de falha do Qt, restauração e WebRTC |
| `test_notification_sound_setting.py` | mapeamento de som e tipos dos hints Portal/Freedesktop |
| `test_notification_window_activation.py` | conexão QtDBus, tokens Portal/Wayland, startup X11, foco e limpeza |
| `test_notifications_settings_ui.py` | rótulos, dependências, privacidade, som e lembrete de apoio |
| `test_performance_experimental_settings_ui.py` | perfis de renderização, controles manuais, migração e reinício |
| `test_permissions_settings_ui.py` | grupos e ações globais/individuais de permissões |
| `test_plain_text_paste.py` | inserção text/plain no editor WebEngine selecionado, resolução de contenteditable pela seleção DOM e fallback PasteAndMatchStyle sem tocar no Ctrl+V |
| `test_portal_notification_backend.py` | ciclo de vida, falhas, ações e token no backend Portal |
| `test_profile_sync.py` | validação de dados pontuais do perfil WhatsApp e normalização da foto |
| `test_qt_parameter_fallbacks.py` | escala, tema da bandeja, geometria, tipos e fail-closed do proxy global, zoom e download inválidos com autocura ou fallback restrito |
| `test_quick_accounts_integration.py` | contrato estático do botão integrado de contas, bridge, fallback e isolamento do JavaScript |
| `test_reporting.py` | sanitização, minimização, Markdown, fila/TTL e captura local de encerramentos inesperados |
| `test_reporting_ui.py` | formulário em duas etapas, prévia canônica, edição, cancelamento, clipboard e abertura segura do GitHub |
| `test_segmented_control.py` | seleção exclusiva, sinais, mouse, teclado, acessibilidade, tamanhos, raios e temas |
| `test_send_message_to_number.py` | normalização/URL, lista de países, validação, acessibilidade e teclado do diálogo de conversa por número |
| `test_settings_card.py` | divisores e grupos do card compartilhado em `ui.components` |
| `test_settings_lazy_loading.py` | subprocessos de importação, registro e instanciação lazy, singleton por painel, diagnóstico, empacotamento, APIs públicas e fechamento de Configurações |
| `test_settings_radio_group.py` | divisores do grupo de rádio em `ui.components` |
| `test_software_video_decoding.py` | presets, flags Chromium de renderização/strict proxy, persistência e ordem do bootstrap |
| `test_spellcheck_language_picker.py` | migração, seleção múltipla transacional, pesquisa, limite, recentes, menu e perfis WebEngine |
| `test_taskbar_badge.py` | contador nativo, zero, preferência, bandeja oculta, ativação primária/contexto por backend, integração StatusNotifier/AppIndicator e compatibilidade com Qt anterior |
| `test_translations.py` | descoberta de catálogos gettext, tradução zh_CN, fallbacks e integridade dos placeholders |
| `test_turkish_translation.py` | catálogo turco sem traduções ativas vazias ou marcadas como fuzzy |
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
- `test_browser_grid_view_ui.py`
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
- `test_download_settings.py`
- `test_external_link_lifecycle.py`
- `test_floating_account_button.py`
- `test_freedesktop_notification_backend.py`
- `test_global_mute.py`
- `test_gpu_environment.py`
- `test_http_cache_size.py`
- `test_initial_setup_ui.py`
- `test_main_window_shortcuts.py`
- `test_memory_benchmark.py`
- `test_native_titlebar_theme.py`
- `test_network_privacy_settings_ui.py`
- `test_notification_sound_setting.py`
- `test_notification_window_activation.py`
- `test_notifications_settings_ui.py`
- `test_performance_experimental_settings_ui.py`
- `test_permissions_settings_ui.py`
- `test_plain_text_paste.py`
- `test_portal_notification_backend.py`
- `test_profile_sync.py`
- `test_qt_parameter_fallbacks.py`
- `test_quick_accounts_integration.py`
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
- `test_taskbar_badge.py`
- `test_translations.py`
- `test_turkish_translation.py`
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

## Validação manual de downloads

Use arquivos de teste sem dados sensíveis e valide cada modo em uma sessão
gráfica real.

1. Em **Comportamento de download**, mantenha o modo de janela e confirme que o diálogo
   Salvar/Abrir/Mais continua sendo exibido.
2. Selecione o modo automático, baixe um arquivo e confirme que ele vai para a
   pasta configurada sem diálogo; ao iniciar, o menu de downloads deve abrir e
   fechar sozinho após cinco segundos.
3. Durante um download, confirme que os dois botões de downloads reduzem o
   ícone e exibem a porcentagem no canto inferior direito. Com dois downloads
   de tamanhos diferentes, confirme que a porcentagem é ponderada pelo total de
   bytes e não pela quantidade de arquivos. Ao terminar a fila ativa, confirme
   o breve efeito de conclusão e o retorno do ícone ao tamanho normal.
4. Abra o menu manualmente pelos botões da barra lateral e da barra de menus e
   confirme que ele não fecha por temporizador, mas fecha ao clicar fora.
5. Selecione **perguntar sempre**, faça um download e confirme que o seletor de
   arquivo aparece para cada download e que cancelar não inicia a transferência.
6. Teste separadamente **abrir PDFs automaticamente** e **abrir imagens
   automaticamente**. Com apenas uma opção ativa, o outro tipo deve permanecer
   fechado. Renomeie um PDF válido para extensão executável, use conteúdo de
   texto com extensão de imagem e teste SVG: nenhum deles deve abrir
   automaticamente. ZIP, texto e outros tipos também devem permanecer fechados.
7. Em cada item do histórico, clique no nome para abrir o arquivo e use o ícone
   de pasta exibido no hover para abrir a pasta. Valide também limpar histórico
   e abrir a pasta de downloads.
8. Troque o idioma da interface e confirme a tradução do menu e dos novos
   controles de download.
9. Inicie sete downloads do WhatsApp após permitir downloads múltiplos.
   Confirme que no máximo seis ficam ativos no ZapZap inteiro, o excedente
   aparece como **Na fila** e inicia automaticamente quando uma vaga é liberada.
   Com várias contas do WhatsApp abertas, confirme que todas compartilham o
   mesmo limite de seis.
10. Sem decisão salva, faça um primeiro download do WhatsApp e confirme que ele
    segue normalmente. Depois faça novos pedidos, inclusive esperando mais de
    dez segundos entre eles: cada pedido posterior deve pedir permissão enquanto
    a decisão permanecer em **perguntar**. Teste **permitir uma vez**, confirme
    que o pedido seguinte volta a perguntar, depois teste **permitir sempre** e
    **bloquear**; por fim use Configurações para limpar a decisão lembrada.
11. Durante um download, confira o ícone de tipo de arquivo fornecido pelo
    sistema, a barra de progresso, o percentual, a velocidade instantânea e a
    estimativa de tempo restante. A velocidade deve permanecer estável o bastante
    para leitura, sem saltos extremos a cada atualização. Pause e retome. Force uma
    interrupção de rede e confirme **Interrompido**; quando Qt indicar que o item é
    retomável, **Retomar** deve continuar a mesma solicitação. Cancele outro
    item e confirme o estado visual **Cancelado** sem animação de sucesso.
12. Teste nomes recebidos como `../../arquivo.pdf`, separadores Windows,
    caracteres de controle e nomes reservados; o destino final deve permanecer
    dentro da pasta escolhida. Crie também um link simbólico no destino apontando
    para fora e confirme que o alvo é rejeitado.
13. Feche o diálogo padrão sem salvar e cancele o seletor de destino antes de a
    transferência começar; nenhum desses pedidos deve aparecer como
    **Cancelado**. Cancele depois uma transferência realmente iniciada e
    confirme que ela permanece na posição original da lista.
14. Baixe um arquivo com nome longo e confirme a elisão no meio, mantendo a
    extensão visível. No botão de downloads não deve aparecer percentual:
    quando a estimativa restante for superior a cinco segundos, confirme um
    anel circular proporcional ao progresso ao redor do ícone. Quando restarem
    cinco segundos ou menos, o anel deve desaparecer sem redimensionar o botão.
15. Abra o menu de downloads pelos botões da barra lateral e da barra de menu.
    Confirme que ele funciona como um menu suspenso compacto e mostra somente
    os cinco itens mais recentes. Passe o ponteiro sobre uma linha e confirme
    que aparecem à direita os ícones de mostrar na pasta e, para itens
    concluídos, excluir o arquivo do disco. Durante um download ativo, confirme
    que aparece um botão **X** à direita e que ele cancela a transferência,
    movendo o item para o estado **Cancelado**. Clique com o botão direito em
    itens ativos/concluídos e confirme as ações contextuais apropriadas:
    pausar/retomar/cancelar, mostrar na pasta, excluir o arquivo e remover
    somente do histórico. O botão inferior deve abrir **Todo o
    histórico de downloads** em uma janela maior, mas ainda compacta, com
    rolagem vertical e histórico ampliado. No rodapé dessa janela confirme três
    controles apenas por ícone: limpar histórico, abrir a pasta de downloads e
    abrir diretamente as configurações de download. O último deve usar um ícone
    de engrenagem, não um símbolo semelhante a sol. Teste tema
    claro, escuro e automático; ambos devem seguir a paleta Qt sem áreas
    ilegíveis. Em Linux, valide pelo menos uma sessão X11 e uma Wayland quando
    disponíveis.
16. Em Linux, Windows e macOS, baixe pelo menos PDF, imagem, arquivo compactado
    e um tipo genérico. Compare com o gerenciador de arquivos do sistema:
    ZapZap deve usar primeiro o ícone MIME do tema de ícones do sistema,
    inclusive para PDF e imagens, sem gerar miniatura do conteúdo. Para um item
    ainda em fila, aceite fallback genérico apenas
    quando a plataforma não fornecer um ícone específico para a extensão.

## Validação manual da barra de título nativa

Use uma sessão gráfica real, pois o modo `offscreen` não desenha a decoração
fornecida pelo compositor/plataforma.

1. Com **Usar decoração personalizada** desativado, selecione o tema **Escuro**
   e confirme que a barra de título nativa acompanha o fundo escuro do ZapZap
   quando a versão instalada do Qt oferece suporte ao override de esquema de cor.
2. Selecione **Claro** e confirme o retorno da decoração nativa clara.
3. Selecione **Automático** e confirme que a decoração volta a seguir o esquema
   claro/escuro do desktop, sem ficar presa ao último override explícito.
4. Em uma distribuição com Qt antigo sem `setColorScheme`, confirme que a
   aplicação continua abrindo normalmente; nesse caso a decoração nativa pode
   continuar sendo controlada exclusivamente pelo compositor.
5. Em GNOME/Pardus com decoração server-side, aceite que o compositor pode
   ignorar o hint mesmo em Qt novo e manter a barra no tema do sistema. Isso não
   deve ativar decoração personalizada, janela frameless ou botões próprios.

## Validação manual do atalho de downloads

1. Com a janela principal ativa, pressione **Ctrl+J** e confirme que a janela
   completa de histórico de downloads é aberta, não apenas o menu compacto.
2. Abra o menu **Exibir** e confirme que **Downloads** aparece com **Ctrl+J**.
3. Confirme que nenhum atalho existente mudou e que clicar nos botões de
   downloads continua usando o fluxo normal.

## Validação manual de colagem sem formatação

Use uma conversa de teste e uma sessão gráfica real.

1. Copie várias células de uma planilha no Excel ou LibreOffice Calc e use
   **Ctrl+Shift+V** no campo de mensagem do WhatsApp Web. No macOS, use
   **Cmd+Shift+V**. Confirme que o conteúdo entra como texto, sem ser convertido
   em imagem ou preservar a formatação rica da planilha. O atalho usa apenas a
   representação textual do clipboard e insere esse texto no editor focado.
2. Repita a mesma cópia com **Ctrl+V** e confirme que o comportamento normal do
   WhatsApp Web permanece inalterado.
3. Repita com texto rico/HTML copiado de um navegador ou editor e confirme que o
   atalho sem formatação usa apenas a apresentação textual compatível com o
   campo de mensagem.

## Validação manual do mute global

1. Com o som aberto, confirme que tray, botão da barra superior e botão da
   sidebar exibem **Mute/Sessize al** e o mesmo ícone de som aberto.
2. Acione qualquer um deles e confirme que os três pontos passam para
   **Unmute/Sesliye al**, mensagens, chamadas/toques e mídia das contas abertas
   ficam sem áudio, mas as notificações continuam aparecendo.
3. Com duas contas e uma janela interna de chamada/popup, alterne entre contas e
   confirme que todas permanecem mudas; abra uma nova página/popup depois do
   mute e confirme que ela nasce muda.
4. Reinicie o ZapZap e confirme que o estado de mute persiste. Desative o mute e
   confirme que a preferência anterior de som de notificações volta a valer sem
   ter sido alterada.

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

## Validação manual da bandeja do sistema

1. Em Windows/macOS ou em um backend Linux que entregue `Trigger`, clique uma
   vez com o botão principal e confirme que a janela alterna entre visível e
   oculta; clique com o botão direito/contexto e confirme o menu.
2. Em GNOME com AppIndicator/StatusNotifier, confirme primeiro o comportamento
   imposto pelo shell. O menu pode abrir tanto no clique principal quanto no
   contexto sem que o aplicativo receba esses eventos.
3. Nesse backend Linux, faça a ação de ativação fornecida pelo shell
   (normalmente duplo clique). Quando ela chegar como `Trigger` ou
   `DoubleClick`, ZapZap deve alternar a janela e não abrir um segundo `QMenu`.
4. Confirme que abrir o menu nativo não deixa o cursor do painel em estado de
   carregamento por causa de um segundo popup criado pelo aplicativo.

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

## Validação manual do backend Freedesktop indisponível

Use um perfil XDG descartável. O objetivo é confirmar que a ausência de balões
deixa rastro no log em vez de parecer um problema do desktop; o som continua
vindo da página do WhatsApp Web e não prova nada sobre o backend.

### Sem bus de sessão

1. Fora do Flatpak, inicie o ZapZap com `DBUS_SESSION_BUS_ADDRESS` apontando
   para um socket inexistente, por exemplo `unix:path=/nonexistent`.
2. Confirme no log um aviso do backend Freedesktop dizendo que não há conexão
   com o bus de sessão e um aviso de `NotificationService` dizendo que as
   notificações foram desabilitadas para a sessão.
3. Confirme que o app continua utilizável e que nenhuma outra exceção aparece.

### Daemon reiniciado durante a sessão

1. Em uma sessão gráfica real, com o ZapZap aberto e conectado, encerre o
   daemon de notificações do desktop (por exemplo, o processo que possui
   `org.freedesktop.Notifications` no bus de sessão).
2. Provoque uma notificação e confirme um único aviso de indisponibilidade no
   log, sem repetição a cada nova mensagem.
3. Restaure o daemon, provoque outra notificação e confirme que o balão volta a
   aparecer sem reiniciar o ZapZap.

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
