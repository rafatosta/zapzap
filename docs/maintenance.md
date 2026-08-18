# Guia de manutenção

## Preparação do ambiente

O projeto requer Python 3.8 ou superior, PyQt6 e PyQt6-WebEngine. Para trabalhar
em um ambiente virtual:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

As integrações D-Bus usam `PyQt6.QtDBus`, já fornecido pelo PyQt6. Não instale
`dbus-python` nem configure um segundo adaptador de event loop para elas.

Execute o aplicativo da raiz com `python run.py` ou `python -m zapzap`. Não use
dados reais para testes destrutivos de conta, cache ou configurações.

## Antes de alterar

1. Leia [a arquitetura](architecture.md) e a seção pertinente deste guia.
2. Verifique `git status --short` e preserve alterações que não sejam suas.
3. Localize a fonte de verdade, os consumidores e os testes existentes.
4. Registre comportamento persistido: chave, padrão, tipo e possíveis inversões
   legadas.
5. Considere Linux/Flatpak, Linux nativo, Windows e macOS quando a mudança tocar
   integração de sistema.
6. Planeje a entrada correspondente em `CHANGELOG.md`; nenhuma mudança ou
   adição está dispensada desse registro.

## Matriz de impacto

| Tipo de mudança | Locais a revisar | Validação mínima |
|---|---|---|
| Preferência | domínio em `core/config/settings`, model/controller, onboarding e consumidores | teste de persistência e UI |
| Página de configurações | `pages/`, shell, componentes, acessibilidade e traduções | teste `*_settings_ui.py` |
| Conta/perfil | `User`, `BrowserController`, `WebView`, cache e remoção | isolamento XDG e teste de ciclo de vida |
| WebEngine/Chromium | `SetupManager`, perfil, scripts e empacotamentos | teste de flags e execução real |
| Notificação | fachada e todos os backends relevantes | unidade por backend e sessão gráfica |
| Tema/widget | `ThemeManager`, paleta, QSS e componentes irmãos | teste de tipografia/estado e inspeção visual |
| Tradução | fonte Python, POTFILES, POT, todos os PO e MO | `msgfmt` e carregamento do catálogo |
| Download/permissão | manager, `PageController`, diálogo e preferências | unidade e operação manual |
| Ciclo de vida do processo | bootstrap, `aboutToQuit`, páginas WebEngine e plataformas | subprocesso isolado e suíte completa |
| Estrutura Python | árvore, imports e `pyproject.toml` | manifestos de pacote e documentação |
| Build/release | workflow e script de plataforma | lint/sintaxe e build da plataforma |

## Receitas de mudança

### Encerramento provocado pelo sistema

- Mantenha o cleanup de notificações, tema, D-Bus e WebEngine conectado a
  `aboutToQuit`; integrações de plataforma devem apenas solicitar a saída
  normal do Qt.
- Em POSIX, não chame APIs Qt dentro de handlers Unix. Encaminhe `SIGTERM` pelo
  wakeup fd e pelo `QSocketNotifier` existentes em `app.unix_signal_bridge`.
- Restaure handlers, wakeup fd e descritores ao desmontar a integração. Falhas
  ao instalá-la não podem impedir a inicialização.
- Não acrescente `SIGINT`, `SIGHUP`, Session Management ou drenagem manual de
  `DeferredDelete` sem um cenário reproduzível e cobertura específica.
- Teste sinais reais somente em subprocesso Unix isolado; nunca envie
  `SIGTERM` ao runner principal nem faça esse teste depender de semântica Unix
  no Windows.

### Nova configuração

- Acrescente a chave e o padrão a uma classe de domínio existente ou nova em
  `core/config/settings/`.
- Exponha propriedade com semântica de produto; esconda inversões de chaves
  legadas no domínio.
- Preserve a chave antiga ou implemente migração explícita.
- Decida quando o valor é lido: valores usados antes de `QApplication` ou da
  criação do perfil WebEngine precisam de reinício completo.
- Atualize onboarding e páginas irmãs quando expõem a mesma preferência.
- Cubra padrão, persistência, alteração e restauração.

### Nova página de configurações

- Siga o contrato descrito em `architecture.md`.
- Registre um descritor lazy com ID estável em `SettingsController._pages()`;
  não importe nem instancie o controller ao construir o shell. Navegação e
  restauração devem usar o ID, pois o índice físico contém somente páginas já
  visitadas.
- Como os builds macOS e Windows usam PyInstaller, preserve a coleta explícita
  de `zapzap.features.settings.pages` quando adicionar loaders dinâmicos. Os
  pacotes Python comuns continuam cobertos pelo inventário de `pyproject.toml`.
- Reutilize `SettingsPage`, `SettingsSection`, `SettingsCard` e as linhas
  semânticas existentes.
- Mantenha texto curto, descrição útil, estado padrão real e nome acessível.
- Não persista rótulos traduzidos; persista um ID estável.
- Se houver ação destrutiva, peça confirmação e separe-a visualmente.

### Mudança no navegador ou em contas

- Preserve um perfil WebEngine por conta e o ID especial da conta padrão.
- Use `User.id` como identidade do registro de runtime; índices da pilha e
  posições de botões servem somente à apresentação.
- Contas desativadas devem manter apenas modelo e botão. Não instancie
  `QWebEngineView`/perfil até a ativação; contas habilitadas continuam iniciando
  automaticamente em segundo plano.
- Garanta no máximo uma `WebView` por entrada: ativação repetida reutiliza a
  instância; desativação a destrói e anula; reativação cria uma nova.
- Preserve os SVGs existentes em `User.icon`; fotos de conta são recortadas,
  reduzidas e incorporadas como PNG no mesmo campo, junto às cores do ícone
  padrão, para permitir alternância sem depender de caminhos externos.
- No diálogo de edição, mantenha nome, ícone/foto e User-Agent em rascunho até
  `Salvar`; `Cancelar`, `Esc` e o botão de fechar devem seguir o mesmo fluxo de
  descarte, com confirmação quando houver alterações.
- Mantenha `Editar` e `Remover` descobertos no cabeçalho do card. A conta
  padrão conserva `Remover` visível, porém desabilitado; durante uma remoção,
  bloqueie ativações duplicadas e reutilize a confirmação destrutiva.
- Desativar a conta pode desabilitar visualmente `Não perturbe`, mas nunca deve
  sobrescrever a preferência persistida que será restaurada na reativação.
- Mantenha o menu de contexto da barra lateral limitado a identidade, edição,
  Não perturbe, desativação e remoção. User-Agent e personalização do avatar
  pertencem ao diálogo transacional de edição.
- Não reutilize armazenamento, cache ou scripts entre perfis por conveniência.
- Capture caminhos antes de destruir o perfil quando for necessário remover
  dados.
- Faça o encerramento idempotente; QtWebEngine é sensível à ordem de destruição.
- Injete uma fábrica falsa de `WebView` nos testes de ciclo de vida para contar
  criação, desmontagem, limpeza e callbacks sem iniciar Chromium.
- Preserve o cache de miniaturas da grade sob propriedade do
  `BrowserController`: capture apenas páginas visíveis, limite buffers em
  pixels físicos e invalide-os antes de desativar, excluir, recarregar ou
  encerrar a conta.
- Na conversa por número, preserve a separação entre código do país e número
  nacional. O diálogo apenas coleta e apresenta erros; `open_chat.py` normaliza,
  valida e codifica a URL, e o `PageController` realiza a navegação direta sem
  JavaScript injetado. Nunca persista número ou mensagem.
- Revalide grid, sidebar, conta ativa, zoom, downloads e notificações.
- Para `performance/cache_size_max`, use as constantes, normalização e aplicação
  segura de `core.config.settings.performance`; nunca converta MiB para bytes
  diretamente na `WebView` nem envie ao Qt um valor maior que `INT32_MAX`.
- Para qualquer valor persistido passado ao Qt, valide tipo, enum e faixa antes
  da chamada. O fallback deve permanecer restrito ao parâmetro opcional: cache,
  cookies, zoom, spellcheck e tema não podem abortar todas as contas.
- Ao aplicar proxy, inspecione `ProxyApplyResult`. Em falha, não substitua o
  proxy ativo por `NoProxy`, não limpe o estado pendente e nunca registre host,
  usuário ou senha.
- Se uma construção de `WebView` falhar, mantenha a entrada sem página no estado
  recuperável `ERROR`; ativação posterior deve tentar novamente sem recriar as
  contas que já estão ativas.
- Mantenha `performance/js_memory_limit_index` como fonte atual e sincronize
  `performance/js_memory_limit_mb` para compatibilidade. A preferência de
  cookies persistentes deve chegar a `setPersistentCookiesPolicy()`.

### Proxy global e isolamento estrito

- Mantenha `proxy/*` como única fonte efetiva. Não leia nem migre
  `<user_id>/proxy/*` e não reaplique proxy ao trocar de conta.
- Aplique `ProxyManager.apply()` depois de criar `SingleApplication`, mas antes
  de construir a janela, o `BrowserController` ou qualquer perfil WebEngine.
- Em falha de validação ou do Qt, preserve o proxy anterior e o rascunho da UI;
  nunca tente `NoProxy`, `DIRECT` ou outro fallback automático e nunca registre
  host, usuário ou senha.
- Considere `privacy/strict_proxy` efetivo somente com proxy habilitado dos
  tipos `HttpProxy` ou `Socks5Proxy`. A flag Chromium correspondente deve ser
  montada por `SetupManager` antes do WebEngine, sem duplicar nem apagar flags
  externas, e mudanças na preferência exigem reinício completo.
- Trate `webrtc_shield.js` somente como proteção JavaScript legada. Ele não
  substitui a política nativa e não comprova isolamento de rede.
- Valide alterações de proxy com testes sem rede e repita os cenários manuais
  fail-closed de `docs/testing.md` em uma sessão descartável.

### Mudança no corretor ortográfico

- Mantenha descoberta, normalização, migração, limite e recentes em
  `DictionariesManager`; views não devem persistir rótulos nem validar sozinhas.
- Preserve `DictionaryStore` como única fonte do diretório gravável gerenciado.
  Ele deve preparar a pasta e concluir a migração antes de
  `load_webview_factory()`; nunca faça rede no bootstrap.
- Em qualquer formato, preserve como fonte efetiva o diretório padrão definido
  em `PathManager` somente quando `manifest.json` corresponder exatamente aos
  nomes e tamanhos de todos os `.bdic`. Não copie um catálogo comprovadamente
  completo, não ofereça importação/remoção/download e não construa
  `DictionaryService`; a seleção de idiomas instalados permanece disponível.
- Use o store gerenciado quando o diretório padrão estiver ausente, vazio,
  parcial, sem manifesto ou divergente. A mera presença de um `.bdic` nunca
  prova completude; em particular, as cinco variantes de inglês da base
  Flatpak não devem ocultar o gerenciador.
- `SystemDictionaryProvisioner` pode baixar automaticamente apenas a
  correspondência do idioma do sistema, uma única vez e depois da criação da
  aplicação Qt. Os demais idiomas exigem ação explícita do usuário; nunca
  substitua uma seleção manual nem reinstale silenciosamente após remoção.
- Preserve `system/spellCheckLanguage` como chave escalar de compatibilidade e
  use `system/spellCheckLanguages` como a fonte atual da seleção múltipla.
- Use `SpellcheckLanguagePickerDialog` nos pontos de entrada do menu e de
  Configurações. Cancelar, fechar e `Esc` descartam o rascunho; apenas
  `Aplicar` persiste e chama `browser.update_spellcheck()`.
- Não volte a criar submenus ou uma `QAction` por dicionário. Valide listas
  grandes, pesquisa por código/rótulo, ausência de dicionários e perfis ativos.
- Downloads pertencem a `DictionaryService`: mantenha HTTPS e repositório em
  allowlist, revisão imutável na URL, limites de tamanho/concorrência, validação
  de hash e escrita temporária atômica. Uma falha nunca pode substituir um
  `.bdic` instalado nem deixar parcial com extensão final.
- O catálogo validado em cache é o fallback offline. Um catálogo novo só
  substitui o anterior depois do parsing completo; sem nenhum catálogo, os
  arquivos locais continuam listados e ativáveis.
- Falha no provisionamento inicial é não fatal e pode ser repetida em outra
  inicialização. Só marque o locale como provisionado depois de encontrar um
  dicionário compatível já instalado ou concluir download e metadados; não use
  um idioma sem relação como fallback de download.

#### Atualização do catálogo-fonte

O repositório `rafatosta/qtwebengine_dictionaries` mantém uma coleção plana de
`.bdic` e um `manifest.json` determinístico. Para atualizar a partir do corpus
Qt 6.11 fornecido pelo mantenedor, preserve a união com os arquivos legados e
execute, no checkout daquele repositório:

```bash
python tools/dictionary_manifest.py generate \
  --archive /caminho/para/locale-qt6.11.zip
python tools/dictionary_manifest.py validate
```

O gerador aceita somente
`locale/<idioma>/qtwebengine_dictionaries/<basename>.bdic`, verifica colisões,
compara cada arquivo do ZIP que também existe no checkout e exige que o
manifesto represente exatamente todos os `.bdic` publicados. Cada entrada
registra código, nome, tamanho, SHA-256, versão Qt, origem e commit que introduziu
o arquivo. Metadados de runtime Flatpak e arquitetura permanecem `null` quando
não há evidência rastreável; não os deduza de timestamps ou nomes do arquivo.
Antes de publicar, revise atribuição/licença na fonte real e não faça afirmação
jurídica sem referência verificável.

AppImage e Snap devem instalar `manifest.json` junto com os `.bdic`. Se o
manifesto faltar ou a cópia não corresponder a ele, o comportamento correto é
usar o store gerenciado; não relaxe a validação com contagem mínima ou lista
fixa de idiomas.

Ao diagnosticar o gerenciador, registre apenas caminho efetivo, resultado da
migração, revisão/idade do cache e categoria técnica da operação. Não registre
conteúdo dos arquivos, caminhos externos escolhidos pelo usuário ou dados de
rede que possam ser sensíveis.

### Mudança em notificação ou ativação

- Aplique regras comuns em `NotificationService`, não as duplique nos backends.
- Use `PyQt6.QtDBus` nos backends Linux e preserve as assinaturas do protocolo;
  hints Freedesktop são `a{sv}` e `urgency` é um `BYTE`.
- Mantenha IDs e remoção idempotentes.
- Fechar no WhatsApp deve fechar a notificação nativa; o encerramento retira as
  restantes.
- Preserve tokens de ativação Portal/Wayland e o caminho X11.
- Teste pelo menos o backend alterado e as preferências de privacidade/som.

### Mudança visual compartilhada

- Corrija primeiro o componente central e audite consumidores.
- Coloque controles Qt básicos em `ui.primitives` e composições visuais
  reutilizáveis em `ui.components`; não esconda widgets compartilhados dentro
  da feature que os criou primeiro.
- Mantenha modelos, controladores, persistência e efeitos na feature ou domínio
  responsável. Componentes visuais devem receber dados e callbacks pelas suas
  interfaces públicas.
- Use `QPalette`, `QFont` e `Typography`; evite cores e pesos paralelos.
- Em seletores segmentados, mantenha IDs estáveis em `SegmentOption.value` e
  rótulos traduzidos em `SegmentOption.label`; não persista o texto visível.
- Em checkboxes, preserve a semântica nativa de `QCheckBox`. Use
  `CheckBoxVariant.SURFACE` em formulários, `SOFT` para opções discretas e
  `CLASSIC` em confirmações; escolha o tamanho pelos enums compartilhados.
- Em menus, preserve `QAction.setCheckable(True)`: use o indicador não exclusivo
  do tema para opções booleanas e o exclusivo para grupos de rádio, sem embutir
  `CheckBox` por meio de `QWidgetAction`.
- Verifique estados normal, hover, pressed, disabled, foco e alto contraste.
- `offscreen` valida propriedades e sinais, não posição do cursor, foco do
  compositor nem aparência final.

### Mudança na janela principal

- Mantenha a estrutura visual em `ui.components` e a coordenação global em
  `app`; não volte a criar controladores dentro da camada de UI.
- Preserve `main/geometry`, `main/windowState` e a semântica das preferências de
  fechamento. Use `WindowSettings`, `SystemSettings` e `AppearanceSettings`.
- Aplique mudanças de mostrar, ocultar, fechar e restaurar em `WindowLifecycle`
  para manter o comportamento idêntico entre a janela nativa e a moldura CSR.
- Ao tratar `hideEvent`, identifique a janela de origem. No modo CSR, somente o
  host superior pode consultar e persistir seu estado; o conteúdo incorporado
  também recebe eventos durante a destruição, quando o host já pode ser inválido.
- Não conecte sinais de ação diretamente a `closeEvent`: solicite `close()` para
  que o Qt forneça um evento real. Fechar a janela usa `request_close()` e
  respeita o segundo plano; ações “Sair” usam `request_quit()`.
- Valide restauração normal, maximizada e fullscreen. Aparência, movimento e
  redimensionamento da moldura CSR ainda exigem uma sessão gráfica real.

### Verificação passiva de versão

- Mantenha comparação, parsing da release e política centralizados em
  `core.update_checker`; widgets apenas consomem `UpdateState`.
- Use os valores literais produzidos por `.github/packaging/common/build-info.sh`
  e pelos workflows. Ao adicionar ou alterar um formato, decida explicitamente
  se sua atualização é manual, própria ou gerenciada por uma distribuição.
- Preserve o padrão conservador: canal, provedor, repositório ou packaging
  desconhecido não inicia request. AppImage, Flatpak, Snap, RPM/COPR e pacotes
  comunitários não devem receber o aviso manual.
- A consulta deve continuar assíncrona, única por execução, com timeout curto,
  sem retry, persistência, telemetria, popup de erro ou `AlertManager` para
  falhas.
- A sidebar e Sobre devem observar o mesmo estado. O botão com ícone abre o popover
  compartilhado por hover, foco ou clique; notas aceitam somente uma URL HTTPS
  oficial da release e o botão de download abre
  `https://rtosta.com/zapzap/#download`, nunca um asset ou instalador direto.
- Preserve acesso por teclado, `Esc`, fechamento externo e o atraso que permite
  mover o ponteiro do botão para o popover sem fechá-lo no trajeto. No hover,
  use `Qt.Tool` sem ativação, não `Qt.Popup`, para não capturar o mouse. Não dependa
  apenas de cor para comunicar a atualização.
- Teste política, ordenação numérica, resposta inválida, draft, prerelease,
  timeout, ausência de rede, URL não oficial, metadados do popover e propriedades
  semânticas da UI sem Internet real.

### Doações e links externos

- Preserve uma única `DonationsPageController` sob propriedade do
  `BrowserController`; todos os pontos de entrada chamam
  `MainWindowController.open_donations()` e não abrem o site de doações na
  `WebView` do WhatsApp.
- Mantenha GitHub Sponsors, Pix, PayPal, Wise e Ko-fi em
  `donation_methods()`, usando somente URLs oficiais HTTPS centralizadas em
  `zapzap.__init__`. Não incorpore chaves Pix, QR codes, credenciais ou dados de
  pagamento.
- Abra destinos por `features.alerts.external_url.open_external_url()`. O
  utilitário rejeita esquemas não HTTPS e oferece cópia manual se
  `QDesktopServices` falhar.
- Ao alterar a página, valide o coração selecionado, reutilização da instância,
  retorno pelo botão de fechar e `Esc`, entradas de
  Configurações/Sobre/bandeja/lembrete, reflow em uma a três colunas, teclado,
  acessibilidade, temas, `retranslate_ui()` e catálogos gettext.

### Traduções

Inventarie entradas vazias e `fuzzy`, preserve tokens técnicos e valide todos os
catálogos. Com GNU gettext instalado:

```bash
msgattrib --untranslated --no-obsolete po/pt_BR.po
msgattrib --only-fuzzy --no-obsolete po/pt_BR.po
msgfmt --check --check-format --statistics -o /tmp/zapzap.mo po/pt_BR.po
```

Repita para cada catálogo alterado e gere os `.mo` que o pacote distribui.

### Benchmark de memória

- Execute campanhas manuais com ao menos cinco repetições em processos novos:
  `python tools/memory/benchmark_memory.py --without-webengine --accounts
  1,3,5 --repeat 5 --output-dir memory-results`.
- Confirme que o relatório registra uma `StubWebView` por conta solicitada e
  nenhum módulo `PyQt6.QtWebEngine*`/`PyQt6.QtWebChannel`.
- Compare mediana de PSS/USS na mesma máquina. RSS e números absolutos não são
  contrato de CI; uma falha por regressão só pode ser habilitada por regra
  relativa explícita no comparador.
- Preserve imports tardios na fronteira WebEngine. O benchmark não pode
  mascarar um import anterior por monkeypatch posterior.
- Consulte `docs/memory-benchmark.md` para cenários, schema e interpretação.

## Registro obrigatório de mudanças

`CHANGELOG.md`, na raiz do repositório, é a fonte de verdade do histórico do
ZapZap. Toda mudança ou adição deve atualizar a seção numérica marcada
`In development` no mesmo commit ou pull request. A regra inclui
funcionalidades, correções, mudanças de comportamento, documentação, testes,
refatorações, dependências, ferramentas, empacotamento e workflows. A versão
dessa seção deve ser igual a `zapzap.__version__`, que permanece estritamente
numérica; o estado de desenvolvimento pertence somente ao cabeçalho do
changelog. Todas as mudanças do ciclo se acumulam nessa mesma seção, sem um
incremento por commit ou por entrada.

Use as categorias `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed` e
`Security`. Escreva entradas curtas que expliquem o efeito da mudança; para
trabalho interno, descreva o impacto na manutenção, confiabilidade, desempenho
ou processo de entrega. Não copie o `git log` e não considere commits, pull
requests ou notas automáticas do GitHub substitutos do changelog.

O ciclo permanente de versão e release é:

1. **Desenvolvimento:** mantenha a próxima versão numérica em
   `zapzap.__version__` e na primeira seção versionada do changelog, marcada
   `In development`. Registre ali toda mudança do ciclo.
2. **Fechamento:** revise as entradas e substitua somente `In development` pela
   data real no formato `YYYY-MM-DD`. Mantenha `zapzap.__version__` nessa mesma
   versão e altere o link de comparação para terminar na tag que será
   publicada.
3. **Tag, build e publicação:** gere as notas do GitHub Release a partir da
   seção fechada e mantenha a versão inalterada durante o commit, a tag, os
   builds e a publicação. Não abra a próxima versão antes dessa etapa, pois os
   artefatos declarariam a versão errada.
4. **Próximo ciclo:** somente depois da publicação, faça um novo commit que
   atualize `zapzap.__version__`, crie no topo a nova seção marcada
   `In development` e adicione seu link da última tag publicada até `HEAD`.

Antes de abrir automaticamente o próximo ciclo, consulte as tags do Git e
confirme qual é a última tag estável efetivamente publicada. Considere somente
tags estritamente numéricas, com prefixo `v` quando essa for a convenção real;
ignore drafts, prereleases, tags não numéricas e versões encontradas apenas em
documentos, AppStream ou artefatos locais. Se as tags locais estiverem
desatualizadas ou houver ambiguidade, confirme a tag oficial antes de editar e
não invente a base.

A próxima versão automática incrementa a última parte da tag publicada:

```text
7.4   -> 7.4.1
7.4.2 -> 7.4.3
7.4.3 -> 7.4.4
7.5   -> 7.5.1
7.5.1 -> 7.5.2
```

Uma versão minor ou major diferente desse resultado só pode ser usada quando o
mantenedor informar explicitamente o destino. Nesse caso, use exatamente a
versão pedida em `zapzap.__version__` e no cabeçalho em desenvolvimento,
preserve todas as entradas acumuladas e ajuste o link dessa versão. O lado
esquerdo do link continua sendo a última tag realmente publicada, nunca o nome
anterior da seção ainda não lançada.

O bloco `<releases>` de
`share/metainfo/com.rtosta.zapzap.appdata.xml` existe somente para a publicação
no Flathub. Ele não é a fonte do histórico e não precisa ser atualizado a cada
mudança. Na preparação de uma release do Flatpak, atualize-o manualmente com um
resumo curto e voltado ao usuário, derivado das entradas de `CHANGELOG.md`
acumuladas entre a versão anterior e a nova.

## Contrato de documentação estrutural

Toda alteração estrutural deve atualizar os documentos no mesmo commit ou pull
request. Considere estrutural:

- adicionar, remover, renomear ou mover pacote, feature ou página;
- mudar responsabilidades ou dependências entre camadas;
- adicionar, remover ou renomear um módulo de teste;
- criar ou alterar uma integração de plataforma;
- adicionar, remover ou renomear ferramenta, formato de pacote ou workflow;
- mudar bootstrap, persistência, diretórios de dados ou processo de release.

Atualize:

- `architecture.md` para estrutura, fluxo, dependências ou fonte de verdade;
- `maintenance.md` para procedimentos, impacto, empacotamento ou release;
- `testing.md` para cobertura, fixture, comando ou limitação;
- `docs/README.md` ao criar ou remover um documento;
- `AGENTS.md` somente quando o contrato geral para agentes mudar.

O comando abaixo falha se os inventários verificáveis divergirem da árvore:

```bash
python tests/test_documentation_structure.py -v
```

Ele cobre pacotes declarados, módulos de teste, formatos de empacotamento e
workflows. Alterações semânticas dentro de arquivos existentes não podem ser
inferidas com segurança e permanecem item obrigatório da revisão.

## Empacotamento e release

`pyproject.toml` define metadados Python, dependências, entry point, pacotes e
dados incluídos. `tools/com.rtosta.zapzap.yaml` é o manifesto Flatpak usado no
projeto. Scripts de outras plataformas ficam em `.github/packaging/`.

Ferramentas e manifestos locais mantidos em `tools/`:

<!-- structure-check:tools:start -->
- `com.rtosta.zapzap.yaml`
- `flatpak_runner.py`
- `translation_manager.py`
<!-- structure-check:tools:end -->

Formatos mantidos:

<!-- structure-check:packaging:start -->
- `appimage`
- `common`
- `deb`
- `macos`
- `python`
- `rpm`
- `snap`
- `windows`
<!-- structure-check:packaging:end -->

Workflows mantidos:

<!-- structure-check:workflows:start -->
- `build-appimage.yml`
- `build-copr.yml`
- `build-deb.yml`
- `build-macos.yml`
- `build-python.yml`
- `build-rpm.yml`
- `build-snap.yml`
- `build-windows.yml`
- `quality.yml`
- `release-candidate.yml`
- `release-deploy.yml`
<!-- structure-check:workflows:end -->

Antes de uma release, revise a versão em `zapzap/__init__.py`, consolide a
seção correspondente de `CHANGELOG.md`, feche-a com a data real e verifique
artefatos desktop/ícone e catálogos compilados. Não altere
`zapzap.__version__` até concluir a tag, os builds e a publicação dessa versão;
abra o próximo ciclo somente depois. Quando houver publicação no Flathub,
produza manualmente um resumo do changelog no bloco `<releases>` dos metadados
AppStream em `share/metainfo/`; versões ainda em desenvolvimento não entram
nesse bloco. Valide então XML/AppStream e o manifesto Flatpak com as ferramentas
disponíveis, pois avisos do Flathub podem bloquear a publicação.

No AppImage, o nome publicado deve ser definido antes da geração do arquivo
`.zsync`. O script de geração fornece o basename final ao `quick-sharun` pela
variável `OUTNAME`, permitindo que o AppImage e seu controle `.zsync` sejam
criados diretamente com o mesmo nome. Não renomeie os artefatos depois dessa
etapa: os metadados internos do `.zsync` poderiam apontar para um nome anterior
e o atualizador receberia HTTP 404.

Instale FFmpeg e Qt WebEngine na mesma transação dos repositórios oficiais do
Arch. Não substitua FFmpeg por `ffmpeg-mini` do canal contínuo de pacotes
reduzidos: as arquiteturas podem ser publicadas em momentos diferentes e expor
ABIs incompatíveis. Antes do `quick-sharun`, valide com `ldd` que as bibliotecas
Qt WebEngine não contêm dependências `not found`; essa verificação deve falhar
antes da coleta, exibindo as bibliotecas ausentes.

No Windows, `build-windows.yml` executa uma matriz nativa para `x86_64` e
`arm64`. Preserve a correspondência entre runner, arquitetura solicitada ao
`setup-python`, argumento de `build.ps1` e sufixo do artefato; o script deve
falhar antes do PyInstaller quando o Python estiver executando em outra
arquitetura. O runner `windows-11-arm` ainda é uma imagem em prévia pública do
GitHub, portanto o build ARM64 precisa ser confirmado no Actions antes da
publicação de cada release.

## Checklist de entrega

- [ ] comportamento e valores persistidos foram preservados ou migrados;
- [ ] estados vazios, erros, cancelamento e encerramento foram considerados;
- [ ] acessibilidade, tema e traduções foram revisados;
- [ ] plataformas e backends irmãos foram auditados;
- [ ] testes novos cobrem a regressão e os testes existentes passam;
- [ ] `python tests/check_unused_code.py --packages-only` passa;
- [ ] `python -m compileall -q zapzap tests tools run.py` passa;
- [ ] `git diff --check` passa;
- [ ] toda mudança ou adição foi registrada em `CHANGELOG.md`;
- [ ] documentação estrutural e inventários foram atualizados;
- [ ] foi feita validação gráfica real quando `offscreen` não é suficiente.
