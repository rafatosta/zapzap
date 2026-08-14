# Arquitetura do ZapZap

## Visão geral

ZapZap é um aplicativo desktop PyQt6 que hospeda o WhatsApp Web em perfis
isolados do QtWebEngine. A organização é orientada por camadas:

```text
run.py / zapzap.__main__
        |
        v
zapzap.app                  bootstrap e ciclo de vida
        |
        v
zapzap.app.main_window_controller composição da interface principal
        |
        +--> features.browser       contas e páginas WebEngine
        +--> features.settings      shell e páginas de configurações
        +--> features.notifications integração nativa por plataforma
        +--> outras features        tray, downloads, permissões etc.
        |
        v
zapzap.core                 configuração, ambiente, tema, i18n e diagnóstico
```

`zapzap.assets` contém ícones e estilos. A interface compartilhada fica toda em
`zapzap.ui`: `ui.primitives` reúne controles básicos e `ui.components` reúne
composições visuais. Uma feature pode usar `core`, `assets` e elementos de UI.
`core` não deve depender de páginas de configurações nem de uma feature de
apresentação. Quando duas páginas precisam do mesmo comportamento, ele deve ser
movido para um domínio em `core`; quando compartilham uma composição visual,
ela deve ficar em `ui.components`.

## Inicialização e encerramento

O caminho principal está em `zapzap/app/application.py`:

1. interpreta opções de linha de comando;
2. aplica ambiente e flags do Qt/Chromium por `SetupManager` antes de criar
   `QApplication`;
3. instala idioma e tratamento de falhas;
4. cria `SingleApplication`, impedindo duas instâncias concorrentes;
5. inicia tema e constrói a janela principal;
6. no Flatpak, exporta `org.freedesktop.Application` por D-Bus;
7. aplica proxy, decide visibilidade inicial e mostra o onboarding se preciso;
8. no encerramento, remove notificações, para D-Bus e tema e libera páginas
   WebEngine explicitamente.

Em sistemas POSIX, `app.unix_signal_bridge` converte `SIGTERM` em uma
solicitação normal de saída. O handler Python não chama Qt: o wakeup fd escreve
em um `socketpair` não bloqueante, um `QSocketNotifier` recebe o evento dentro
do loop Qt e chama `QApplication.quit()`. Assim, `aboutToQuit` permanece como a
autoridade do cleanup e continua chegando a `shutdownInterface()` e
`BrowserController.shutdown()`. A ponte restaura o handler e o wakeup fd
anteriores ao encerrar. Windows não instala essa integração; macOS usa o mesmo
mecanismo POSIX. `SIGINT` e `SIGHUP` preservam sua semântica anterior.

Depois que o event loop começa, `MainWindowController` inicia no máximo uma
consulta assíncrona de release por execução. `core.update_checker`
faz a política conservadora por `BuildInfo`, consulta somente a release estável
mais recente e publica um `UpdateState` efêmero. A abertura da janela não aguarda
a rede e falhas não entram no fluxo de alertas. O estado e o checker pertencem
ao `QApplication`, portanto sobrevivem a uma reconstrução apenas da interface
sem repetir a consulta.

`SingleApplication` também coordena mensagens entre instâncias, reinício apenas
da interface e reinício completo do processo. Configurações lidas antes da
criação do QtWebEngine, como escala, plataforma gráfica e flags Chromium,
normalmente exigem reinício completo.

## Janela e navegador

`MainWindowController`, em `zapzap.app`, compõe o navegador, configurações,
atalhos e menus sobre o `MainWindowView` de `ui.components`. A moldura opcional
fica em `ClientSideWindow`; `ClientSideWindowHost` expõe explicitamente o
contrato da janela principal, sem delegação dinâmica de atributos.

`WindowLifecycle` é único para janelas nativas e com decoração do lado cliente.
Ele restaura e persiste geometria, coordena fechamento, segundo plano, bandeja e
o estado normal, maximizado ou fullscreen observado diretamente no Qt. As chaves
legadas `main/geometry` e `main/windowState` são preservadas por
`WindowSettings`; preferências de fechamento e aparência usam seus domínios
tipados existentes. `request_close()` respeita a permanência em segundo plano;
ações explicitamente chamadas “Sair” usam `request_quit()` e encerram o app.
Somente a janela superior registra seu estado ao ser ocultada: no modo CSR, o
host assume essa responsabilidade e eventos tardios do conteúdo incorporado são
ignorados durante a destruição da árvore Qt.

`BrowserController` mantém um registro central indexado por `User.id`. Cada
entrada possui o `User`, o botão lateral, a posição de apresentação, um estado
de ciclo de vida e uma referência opcional para a `WebView`. Uma conta
desativada é registrada sem construir `QWebEngineView` ou perfil; todas as
contas habilitadas, inclusive as que não estão selecionadas, são iniciadas
automaticamente. Ele também possui o cache efêmero da grade, com no máximo uma
miniatura de 480 × 300 pixels físicos por conta, indexada pelo ID estável e
limpa ao desativar, excluir, recarregar ou encerrar páginas. Capturas integrais
não ficam retidas nas `WebView`s. Cada conta usa um perfil WebEngine próprio. O
fluxo básico é:

```text
User (SQLite) -> registro desativado (botão, page=None)
       habilitar -> registro ativo -> WebView -> PageController
       desativar <- destruição única <-+       -> perfil WebEngine isolado
       remover   -> limpeza + retirada definitiva do registro
```

O `user.id` é a identidade usada por sidebar, grade, atalhos e notificações.
Índices da `QStackedWidget` e posições visuais nunca identificam contas. Em
cada entrada há no máximo uma `WebView`; desativar ou remover anula a referência
antes da desmontagem, e encerrar/desativar novamente é uma operação neutra.

Na barra lateral, o contorno do card identifica a conta selecionada e o avatar
não contém texto quantitativo. Um ponto verde-azulado indica não lidos e um
avatar em escala de cinza identifica uma conta explicitamente desativada.
Contas desativadas ou silenciadas não exibem ponto; sem atividade especial,
também não há indicador. Carregamento, falha de conexão e validade da sessão
não são inferidos, pois o `WebView` ainda não os propaga ao botão da conta.
Nos builds oficiais de download manual, uma release estável mais recente torna
visível um botão de atualização 40 × 40, somente com ícone, na parte inferior
da sidebar. Hover ou foco mostram
um popover com versões instalada/recente, data da publicação e ações para notas
da versão e downloads. O clique fixa o foco nas ações; `Esc`, clique externo ou
saída do conjunto botão/popover fecham o painel. A transição do ponteiro possui
um pequeno atraso para não fechar o painel entre os dois elementos. O mesmo
`UpdateState` alimenta a página Sobre, inclusive quando a sidebar está oculta,
sem duplicar consulta ou comparação.
O botão não possui tooltip nativo, pois ele competiria visualmente com o
popover; nome e descrição acessíveis continuam informando a atualização.
O clique de contexto abre um popover compacto com identidade, estado, edição,
Não perturbe, desativação e remoção. As opções avançadas de User-Agent e
personalização do avatar permanecem exclusivamente no diálogo de edição.
No gerenciamento em `Contas`, o card expõe `Editar` e `Remover` diretamente no
cabeçalho; não há menu de três pontos duplicando essas ações. O avatar não
recebe sobreposições e, quando a conta é desativada, usa o mesmo processamento
grayscale compartilhado em memória da barra lateral. O controle `Não perturbe`
fica temporariamente desabilitado, preservando seu valor persistido para a
próxima reativação.

`PageController` aplica permissões, scripts, navegação segura e ações do
WhatsApp. Scripts mantidos em `features/browser/web/scripts/` são ativos em
tempo de execução e devem ser considerados pelo teste de código estático mesmo
quando chamam identificadores Python indiretamente.

A ação de conversa por número é coordenada por `MainWindowController`, que
mantém no máximo um `SendMessageToNumberDialog` modal por vez. O diálogo
reutilizável em `ui.components` coleta país, número nacional e mensagem sem
persistir destinatários. Normalização, validação E.164 e construção segura da
URL ficam em `features/browser/web/open_chat.py`; após a aceitação,
`PageController` navega diretamente para `web.whatsapp.com/send`, sem injetar
`window.prompt` nem interceptar outros prompts do WhatsApp Web.

A central nativa de doações pertence a `features.donation` e é uma página única
da pilha do `BrowserController`, ao lado da grade e das páginas de conta. O
coração da sidebar, Configurações, Sobre, bandeja e lembrete de apoio convergem
para `MainWindowController.open_donations()`; selecionar essa rota não navega
nem recria qualquer `WebView`. `DonationMethod` centraliza os cinco destinos
oficiais (GitHub Sponsors, Pix, PayPal, Wise e Ko-fi), sempre HTTPS. Pix segue o
mesmo fluxo externo dos demais, sem chave, QR code ou dados financeiros na UI.
O botão de fechar e `Esc` retornam à conta ou grade exibida antes da abertura,
sem recarregar a conversa. A página e seus cartões expõem `retranslate_ui()`
para acompanhar imediatamente a troca do catálogo sem recriar a rota.
`features.alerts.external_url` valida o esquema e o host antes de usar
`QDesktopServices` e oferece copiar o endereço quando o navegador não puder ser
aberto.

Páginas transitórias criadas para capturar links externos devem ser
interrompidas e destruídas assim que a URL for entregue ao navegador padrão.

Ao remover ou desativar uma conta, preserve a captura e a limpeza dos diretórios
do perfil. A limpeza de uma conta que nunca foi ativada pode resolver os caminhos
do perfil, mas não deve criar uma `WebView`. Ao encerrar, destrua páginas antes
do `QApplication` para evitar falhas nativas.

## Persistência e dados

Existem dois mecanismos:

- `SettingsManager` usa `QSettings` para preferências simples;
- `Database` usa SQLite para a tabela de contas representada por `User`.

O campo `User.icon` preserva os SVGs existentes e também pode conter uma foto
normalizada em PNG incorporada. A representação mantém a foto e as cores do
ícone padrão ao alternar entre as duas opções, sem depender do arquivo original
escolhido pelo usuário.

O diálogo de edição mantém nome, ícone/foto e User-Agent em estado temporário.
O `SegmentedControl` alterna apenas a pré-visualização; o controlador recebe os
valores definitivos somente após `Salvar`. Cancelar, fechar ou descartar
alterações restaura implicitamente os valores persistidos, sem tocar na sessão.

Novas preferências devem entrar primeiro em uma classe semântica de
`zapzap/core/config/settings/`, com chave, tipo e valor padrão estáveis. A UI
consome propriedades desse domínio. Use `SettingsManager` diretamente apenas
em código legado ou infraestrutura ainda não migrada; não crie uma segunda
abstração dentro de uma página.

`PerformanceSettings` também é a barreira para o limite do cache HTTP do
QtWebEngine. A chave legada `performance/cache_size_max` continua expressa em
MiB, mas valores ausentes, malformados, negativos ou maiores que 2047 são
normalizados e, quando persistidos, reparados para `0`. A aplicação ao perfil
converte o valor seguro para bytes e trata `0` como gerenciamento automático do
Qt, sem permitir que uma falha nessa otimização interrompa a inicialização.

A seleção global do corretor ortográfico é uma lista de até dez códigos
estáveis em `system/spellCheckLanguages`. `DictionariesManager` descobre os
dicionários instalados, normaliza a lista, remove duplicatas e itens ausentes e
migra transparentemente o valor escalar legado `system/spellCheckLanguage`.
A chave legada não é apagada e continua sincronizada com o primeiro idioma,
preservando downgrade e `get_current_dict()`. Idiomas recentes ficam, como lista
ordenada, em `system/recentSpellCheckLanguages`.

Não renomeie chaves persistidas sem migração. Algumas propriedades positivas
invertem chaves legadas negativas, por exemplo `keep_running_in_background`
versus `system/quit_in_close` e `donation_message_enabled` versus
`notification/donation_message`. Essa inversão pertence ao domínio, não à view.

Dados e caches seguem `QStandardPaths`. Testes substituem os diretórios XDG por
temporários; nunca devem usar o perfil real do mantenedor.

## Instrumentação de memória

O benchmark em `tools/memory/` mantém seu processo coordenador limitado à
biblioteca padrão e configura a plataforma Qt antes de importar PyQt6. Cada
repetição nasce em um subprocesso novo. `MainWindowController` encaminha uma
factory opcional ao registro de contas e o modo isolado fornece `StubWebView`.
No bootstrap de produção, a factory real é resolvida depois de configurar o
ambiente, mas obrigatoriamente antes de criar `QCoreApplication`, como exige o
QtWebEngine; reinícios da interface reutilizam essa factory já resolvida.

Imports de tipos WebEngine usados somente no caminho de navegação real, como
downloads e permissões, também são tardios. Assim, todas as páginas de
Configurações podem ser construídas no benchmark sem carregar
`QtWebEngineCore`, `QtWebEngineWidgets` ou `QtWebChannel`. Métricas e limites de
interpretação estão documentados em `docs/memory-benchmark.md`.

## Configurações

O shell é registrado em `SettingsController._pages()`. Cada página segue, tanto
quanto possível, a separação:

- `model.py`: valores, opções e interfaces de domínio;
- `view.py`: widgets, layout, texto visível e acessibilidade;
- `controller.py`: sinais, persistência e efeitos.

`SettingsController._pages()` registra descritores com ID estável, rótulo
traduzido e caminho do controller. Ao abrir Configurações, o shell, a navegação
e somente a página `accounts` são construídos. Cada outra página é importada e
instanciada apenas na primeira seleção, permanece singleton durante aquela
sessão do painel e é destruída com a árvore Qt quando o painel é fechado. APIs
externas selecionam páginas pelo ID ou tipo público, nunca pelo índice físico
do `QStackedWidget`. O loader distingue módulo alvo ausente, dependência interna
ausente, classe inválida e falha do construtor; o diagnóstico mantém ID, módulo
e classe sem deixar o shell em estado parcial.

As páginas consomem composições reutilizáveis de `zapzap.ui.components`.
`SettingsCard.add_row()` cria divisores automaticamente; linhas auxiliares
podem optar por `divider=False`. Mudanças que pedem reinício usam
`SettingsPage.set_restart_required()` e a barra contextual compartilhada. A
feature decide quando exibir ou acionar esses elementos, mas sua implementação
visual permanece localizável em `ui`.

Ao criar uma página:

1. crie o pacote `pages/<nome>/` com `model`, `view`, `controller` e
   `__init__.py`;
2. registre o controlador em `SettingsController._pages()`;
3. inclua o pacote em `pyproject.toml`;
4. use componentes existentes, paleta Qt e `Typography`;
5. adicione nomes acessíveis e teste de UI;
6. atualize os inventários desta documentação.

## Notificações e ativação

`NotificationService` é a fachada. Ele aplica preferências globais e por conta e
seleciona um backend:

| Ambiente | Backend |
|---|---|
| Flatpak/Linux | XDG Desktop Portal |
| Linux fora do Flatpak | `org.freedesktop.Notifications` |
| Windows | backend Windows |
| macOS | backend macOS |

As integrações D-Bus usam exclusivamente `PyQt6.QtDBus`: o backend Portal e o
backend Freedesktop compartilham o event loop do Qt e não dependem de
`dbus-python` nem de um adaptador GLib adicional. No backend Freedesktop, os
hints preservam o mapa `a{sv}` e seus tipos de protocolo, inclusive `urgency`
como `BYTE`.

Fechamento de uma notificação WebEngine e encerramento do app devem retirar a
notificação nativa de forma idempotente. A ativação pode carregar tokens Portal
ou Wayland e dados de inicialização X11. Mudanças nessa área precisam ser
testadas no backend afetado e, para foco/cursor/compositor, em uma sessão gráfica
real; `offscreen` não comprova comportamento do compositor.

## Tema, componentes e internacionalização

`ThemeManager` mantém o tema efetivo, a `QPalette` e observadores. Controles
básicos devem partir de `zapzap/ui/primitives`; composições reutilizáveis ficam
em `zapzap/ui/components`. Ambos usam cores semânticas da paleta e `Typography`,
evitando uma segunda linguagem visual. QSS pode sobrescrever fontes: quando
necessário, aplique `setFont()` depois de `setStyleSheet()`.

Uma classe visual não deve ser escondida dentro de uma feature apenas porque
seu primeiro consumidor surgiu ali. Views completas podem continuar próximas
da feature, mas widgets e diálogos reutilizados por fluxos diferentes devem ser
promovidos para `ui.components`. Modelos, controladores, persistência e efeitos
continuam na feature ou no domínio responsável.

`SegmentedControl` é o seletor exclusivo reutilizável para duas ou mais opções.
Ele mantém valores estáveis separados dos rótulos traduzidos, usa um único foco
de teclado e expõe estados nativos de botão para acessibilidade. A página de
contas apenas mapeia `enabled` e `disabled` para `User.enable`; persistência e
efeitos de sessão permanecem no fluxo existente do `CardUserController`.

`CheckBox` continua herdando de `QCheckBox`, preservando sinais, tri-state,
atalhos, clique no texto e papel acessível nativos. Sua API visual usa os enums
`CheckBoxVariant` (`CLASSIC`, `SURFACE`, `SOFT`), `CheckBoxSize` e
`CheckBoxTone`; caixa, checkmark, estado parcial e foco são vetoriais e pintados
em pixels lógicos a partir da `QPalette`.

Ações marcáveis em `QMenu` continuam sendo `QAction`, preservando a semântica
nativa de menu. O tema representa ações não exclusivas com a mesma geometria
do `CheckBox` pequeno e ações exclusivas como radio buttons; os dois casos não
devem ser substituídos por `QWidgetAction`.

Texto visível usa `gettext`. IDs persistidos de seletores ficam em `itemData` e
`currentData`; somente o rótulo é traduzido. Ao alterar texto:

1. atualize extração/catálogos;
2. preserve placeholders, URLs e atalhos;
3. valide arquivos PO com `msgfmt --check --check-format`;
4. gere os `.mo` empacotados.

Seletores de dicionário seguem o mesmo contrato: `DictionaryOption.code`
preserva exatamente o basename técnico do `.bdic`, enquanto `label` apresenta
o nome legível e ordenável. Associações conhecidas corrigem nomes fora do
padrão de locale; dicionários personalizados desconhecidos permanecem visíveis
pelo basename original.

O menu de contexto do navegador expõe somente a ativação do corretor e a ação
`Idiomas…`; ele não cria uma ação por dicionário. A view reutilizável
`SpellcheckLanguagePickerDialog`, em `ui.components`, mantém pesquisa, chips,
recentes e checkboxes em estado temporário. A feature `dictionaries` coordena a
persistência somente após `Aplicar`, e tanto o navegador quanto a página
`Language and Download` abrem esse mesmo fluxo.

## Funcionalidades transversais

| Área | Responsabilidade principal |
|---|---|
| `accounts` | entidade e persistência de contas |
| `alerts` | diálogos, abertura HTTPS externa e feedback compartilhados |
| `browser` | perfis, páginas, sidebar, scripts e navegação |
| `customizations` | CSS, JavaScript e extensões por escopo |
| `dictionaries` | descoberta, seleção global/migração e instalação de dicionários WebEngine |
| `donation` | lembrete, métodos oficiais e página nativa de apoio |
| `downloads` | destino, nome seguro e diálogo de progresso |
| `initial_setup` | onboarding e persistência das escolhas iniciais |
| `notifications` | fachada, backends e ativação da janela |
| `permissions` | permissões WebEngine por conta |
| `settings` | navegação e edição das preferências |
| `shortcuts` | catálogo e diálogo de atalhos |
| `startup` | inicialização automática por plataforma |
| `tray` | ícone, menu, contador e vínculo com a janela |

## Verificação passiva de versão

`core.update_checker` mantém separadas três responsabilidades: comparação de
versões numéricas, política de ambiente e parsing da fonte remota. A fonte atual
é `https://api.github.com/repos/rafatosta/zapzap/releases/latest`; drafts,
prereleases e tags não numéricas são rejeitados mesmo que a resposta remota
mude. A chamada usa `QNetworkAccessManager`, timeout de cinco segundos, nenhum
retry e nenhum identificador de instalação.

`UpdateInfo` também transporta a data de publicação e a URL de notas. A URL é
aceita somente quando usa HTTPS no caminho de releases de
`github.com/rafatosta/zapzap`; metadados opcionais inválidos são omitidos sem
descartar uma versão estável válida. `ui.components.UpdateAvailablePopover`
apresenta esses dados sem conhecer rede ou política. “Notas da versão” abre a
release validada e “Baixar” abre `https://rtosta.com/zapzap/#download`.
No hover, o painel usa uma janela `Qt.Tool` mostrada sem ativação; não use
`Qt.Popup` nesse caminho, pois a captura do mouse alterna `enter/leave` no botão
e faz o painel piscar.

A política exige simultaneamente canal `Official`, provedor `GitHub Actions`,
repositório `rafatosta/zapzap` e um destes valores reais de `BUILD_PACKAGING`:
`DEB`, `macOS`, `Windows x86_64 (exe)` ou `Windows arm64 (exe)`. `AppImage`,
`Copr`, `Flatpak`, `Python Package (whl)`, `RPM`, `Snap`, builds comunitários,
customizados e checkouts sem `BuildInfo.py` não fazem request. Assim, formatos
com atualização própria ou gerenciada externamente não recebem um aviso
upstream conflitante.

## Empacotamento multiplataforma

O workflow de Windows produz executáveis nativos em uma matriz com `x86_64` e
`arm64`. Cada arquitetura usa um runner e um Python da mesma arquitetura; o
script PowerShell verifica essa correspondência antes do PyInstaller e inclui a
arquitetura no nome final do artefato.

## Mapa do repositório

| Caminho | Conteúdo |
|---|---|
| `CHANGELOG.md` | fonte obrigatória de todas as mudanças e adições do projeto |
| `zapzap/` | código Python distribuído e catálogos `.mo` de runtime |
| `tests/` | testes `unittest`, fixture Qt e verificações estáticas |
| `docs/` | documentação técnica e contratos de manutenção |
| `po/` | fontes gettext (`.po`, `.pot`, POTFILES e LINGUAS) |
| `share/` | desktop entry, ícone, metadados AppStream e screenshots |
| `tools/` | manifesto/runner Flatpak e gerenciador de traduções |
| `.github/packaging/` | scripts e arquivos de build por formato |
| `.github/workflows/` | qualidade, builds, pré-release e publicação |
| `pyproject.toml` | metadados, dependências, entry point e pacotes |
| `run.py` | entrada conveniente para execução pelo checkout |
| `requirements.txt` | dependências usadas por fluxos legados/auxiliares |

Diretórios como `build/`, `.flatpak-builder/`, `__pycache__/` e metadados de
empacotamento gerados não são fontes. Não documente nem edite seus conteúdos
como se fizessem parte da arquitetura.

## Inventário de pacotes distribuídos

Este bloco é verificado automaticamente contra
`tool.setuptools.packages`. Mantenha-o ordenado.

<!-- structure-check:packages:start -->
- `zapzap`
- `zapzap.app`
- `zapzap.assets`
- `zapzap.assets.icons`
- `zapzap.assets.themes`
- `zapzap.core`
- `zapzap.core.config`
- `zapzap.core.config.settings`
- `zapzap.core.diagnostics`
- `zapzap.core.environment`
- `zapzap.core.i18n`
- `zapzap.core.platform`
- `zapzap.core.theme`
- `zapzap.features`
- `zapzap.features.accounts`
- `zapzap.features.accounts.domain`
- `zapzap.features.alerts`
- `zapzap.features.browser`
- `zapzap.features.browser.shell`
- `zapzap.features.browser.web`
- `zapzap.features.customizations`
- `zapzap.features.dictionaries`
- `zapzap.features.donation`
- `zapzap.features.downloads`
- `zapzap.features.downloads.ui`
- `zapzap.features.initial_setup`
- `zapzap.features.notifications`
- `zapzap.features.permissions`
- `zapzap.features.settings`
- `zapzap.features.settings.pages`
- `zapzap.features.settings.pages.about`
- `zapzap.features.settings.pages.accounts`
- `zapzap.features.settings.pages.advanced_customizations`
- `zapzap.features.settings.pages.appearance`
- `zapzap.features.settings.pages.debugging`
- `zapzap.features.settings.pages.language_downloads`
- `zapzap.features.settings.pages.network_privacy`
- `zapzap.features.settings.pages.notifications`
- `zapzap.features.settings.pages.performance_experimental`
- `zapzap.features.settings.pages.permissions`
- `zapzap.features.settings.pages.system_startup`
- `zapzap.features.settings.shell`
- `zapzap.features.shortcuts`
- `zapzap.features.startup`
- `zapzap.features.tray`
- `zapzap.ui`
- `zapzap.ui.components`
- `zapzap.ui.primitives`
<!-- structure-check:packages:end -->
