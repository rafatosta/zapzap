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

No Linux, integrações D-Bus fora do Flatpak também podem precisar da dependência
opcional:

```bash
python -m pip install -e '.[dbus]'
```

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
| Estrutura Python | árvore, imports e `pyproject.toml` | manifestos de pacote e documentação |
| Build/release | workflow e script de plataforma | lint/sintaxe e build da plataforma |

## Receitas de mudança

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
- Reutilize `SettingsPage`, `SettingsSection`, `SettingsCard` e as linhas
  semânticas existentes.
- Mantenha texto curto, descrição útil, estado padrão real e nome acessível.
- Não persista rótulos traduzidos; persista um ID estável.
- Se houver ação destrutiva, peça confirmação e separe-a visualmente.

### Mudança no navegador ou em contas

- Preserve um perfil WebEngine por conta e o ID especial da conta padrão.
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
- Revalide grid, sidebar, conta ativa, zoom, downloads e notificações.

### Mudança em notificação ou ativação

- Aplique regras comuns em `NotificationService`, não as duplique nos backends.
- Mantenha IDs e remoção idempotentes.
- Fechar no WhatsApp deve fechar a notificação nativa; o encerramento retira as
  restantes.
- Preserve tokens de ativação Portal/Wayland e o caminho X11.
- Teste pelo menos o backend alterado e as preferências de privacidade/som.

### Mudança visual compartilhada

- Corrija primeiro o componente central e audite consumidores.
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

### Traduções

Inventarie entradas vazias e `fuzzy`, preserve tokens técnicos e valide todos os
catálogos. Com GNU gettext instalado:

```bash
msgattrib --untranslated --no-obsolete po/pt_BR.po
msgattrib --only-fuzzy --no-obsolete po/pt_BR.po
msgfmt --check --check-format --statistics -o /tmp/zapzap.mo po/pt_BR.po
```

Repita para cada catálogo alterado e gere os `.mo` que o pacote distribui.

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

Antes de uma release, revise a versão em `zapzap/__init__.py`, metadados
AppStream em `share/metainfo/`, artefatos desktop/ícone, catálogos compilados e
histórico real de mudanças. Valide XML/AppStream e o manifesto Flatpak com as
ferramentas disponíveis; avisos do Flathub podem bloquear a publicação.

No AppImage, o nome publicado deve ser definido antes da geração do arquivo
`.zsync`. O script de normalização renomeia o AppImage, regenera o controle com
`zsyncmake` e valida que `Filename` e `URL` correspondem exatamente ao basename
publicado. Não renomeie apenas o `.zsync`: seus metadados internos continuariam
apontando para o nome anterior e o atualizador receberia HTTP 404.

## Checklist de entrega

- [ ] comportamento e valores persistidos foram preservados ou migrados;
- [ ] estados vazios, erros, cancelamento e encerramento foram considerados;
- [ ] acessibilidade, tema e traduções foram revisados;
- [ ] plataformas e backends irmãos foram auditados;
- [ ] testes novos cobrem a regressão e os testes existentes passam;
- [ ] `python tests/check_unused_code.py --packages-only` passa;
- [ ] `python -m compileall -q zapzap tests tools run.py` passa;
- [ ] `git diff --check` passa;
- [ ] documentação estrutural e inventários foram atualizados;
- [ ] foi feita validação gráfica real quando `offscreen` não é suficiente.
