# Documentação técnica do ZapZap

## 1) Visão geral

O **ZapZap** é um cliente desktop Linux para WhatsApp Web construído com **PyQt6 + QtWebEngine**. A aplicação encapsula `https://web.whatsapp.com/` em uma janela nativa, adicionando recursos de desktop (múltiplas contas, tray, notificações, tema, customizações CSS/JS, atalhos e integrações de empacotamento). 

## 2) Stack e componentes principais

- **Linguagem:** Python 3.8+
- **UI:** PyQt6
- **Engine Web:** PyQt6-WebEngine
- **Persistência de configurações:** `QSettings`
- **Persistência de contas:** SQLite (`zapzap.db`)
- **Internacionalização:** gettext (`po/*.po` + `zapzap/po/*/LC_MESSAGES/*.mo`)
- **Empacotamento suportado:** Flatpak, AppImage, RPM e instalação não oficial (pip/source)

## 3) Fluxo de inicialização

Entrada principal:

1. `python -m zapzap` (ou script `zapzap`) chama `zapzap.__main__:main`.
2. `SetupManager.apply()` configura variáveis de ambiente (plataforma gráfica, escala, dicionários e flags do QtWebEngine/Chromium).
3. `TranslationManager.apply()` define domínio e diretório de traduções.
4. O handler global de crash é registrado.
5. A aplicação cria `SingleApplication` para impedir múltiplas instâncias simultâneas.
6. `MainWindow` é criada e restaura estado (geometria, window state, sys tray e tema).
7. `Browser` carrega as contas e instancia um `WebView` por conta habilitada.
8. Cada `WebView` cria um `QWebEngineProfile` isolado e carrega o WhatsApp Web.

## 4) Arquitetura em camadas

### 4.1 UI e controle

- `controllers/` concentra comportamento da janela principal e páginas de configurações.
- `views/` contém classes Python geradas a partir de `.ui` do Qt Designer.
- `ui/` contém os arquivos-fonte `.ui`.

### 4.2 Navegação e sessão web

- `webengine/WebView.py` gerencia perfil web, download, spellcheck, menu de contexto e eventos da aba.
- `webengine/PageController.py` estende `QWebEnginePage` para:
  - controlar navegação,
  - interceptar novas janelas (abrindo no navegador padrão),
  - injetar addons/customizações,
  - aplicar permissões e tema.

### 4.3 Serviços de domínio

- `SettingsManager`: fachada estática para `QSettings`.
- `CustomizationsManager`: catálogo/importação/ordenação/injeção de CSS e JS (global e por conta).
- `ThemeManager`: aplica tema claro/escuro/auto via palette + stylesheet.
- `SysTrayManager`: menu e interação do ícone de bandeja.
- `DownloadManager`: tratamento de downloads do QtWebEngine.
- `DictionariesManager` + `PathManager`: resolução de caminho de dicionários por tipo de empacotamento.
- `AddonsManager`: carrega scripts JS internos para injeção.

### 4.4 Notificações

`NotificationService` atua como fachada e escolhe backend em runtime:

- **Flatpak:** backend Portal.
- **Outros ambientes:** backend Freedesktop (quando disponível).

As regras de exibição respeitam preferências globais e por conta, incluindo ocultação de nome/mensagem.

### 4.5 Persistência

- **Banco SQLite:** metadados de contas (`users`) e preferências associadas (ex.: zoom).
- **QSettings:** configuração funcional (tema, comportamento de janela, performance, spellcheck, etc.).
- **Disco local de customizações:**
  - `customizations/global/css`
  - `customizations/global/js`
  - `customizations/accounts/<id>/css`
  - `customizations/accounts/<id>/js`
  - `customizations/extensions` (reservado)

## 5) Modelo de contas

Cada conta cria:

- um botão lateral (`PageButton`),
- uma aba web (`WebView`) com perfil isolado,
- regras próprias de notificação e customização.

A primeira conta usa alias lógico `storage-whats` para compatibilidade com estrutura histórica do projeto.

## 6) Build, execução e release

Script orquestrador: `run.py`

### 6.1 Desenvolvimento

- `python run.py dev`
- `python run.py dev --build-translations`

O fluxo gera classes de janela a partir dos `.ui` e inicia o app em seguida.

### 6.2 Preview

- Flatpak: `python run.py preview --flatpak`
- AppImage (local): `python run.py preview --appimage`

### 6.3 Build

- AppImage: `python run.py build --appimage <version>`
- Flatpak onefile: `python run.py build --flatpak-onefile`

## 7) Estrutura de diretórios (resumo)

- `zapzap/controllers`: janelas, páginas de configuração e fluxos de UI.
- `zapzap/webengine`: integração com QtWebEngine.
- `zapzap/services`: serviços transversais (configuração, tema, notificações, customizações, ambiente).
- `zapzap/models`: entidades persistidas (contas).
- `zapzap/config`: infraestrutura local (SQLite).
- `zapzap/resources`: ícones, estilos e recursos de UI.
- `po/` e `zapzap/po/`: catálogo fonte e binário de traduções.
- `_scripts/`: scripts auxiliares de build/empacotamento.

## 8) Extensão e manutenção

### Pontos de extensão recomendados

1. **Novos serviços**: adicionar em `services/` e integrar via controller específico.
2. **Novos ajustes**: persistir em `SettingsManager` com chaves versionáveis.
3. **Nova feature de injeção web**: priorizar `CustomizationsManager` (quando orientada a usuário) ou `AddonsManager` (comportamento interno).
4. **Notificações**: implementar backend adicional e plugar na seleção do `NotificationService`.

### Cuidados técnicos

- Mudanças em `SetupManager` afetam inicialização de QtWebEngine; validar em X11/Wayland.
- Mudanças em notificações devem ser testadas em Flatpak e ambiente não sandbox.
- Chaves de `QSettings` devem manter compatibilidade retroativa para evitar regressões em upgrades.

## 9) Troubleshooting rápido

- **Sem upload de arquivos (Flatpak/Wayland):** revisar permissões de filesystem (Documents, Downloads, Pictures, Videos).
- **Sem spellcheck:** verificar caminho de dicionários conforme empacotamento.
- **Tema não sincroniza:** confirmar backend de portal/DBus disponível no ambiente.
- **Notificações ausentes:** validar preferência global/por conta e backend selecionado.

---

Se necessário, esta documentação pode ser evoluída para um padrão “Architecture Decision Records (ADR)” com histórico de decisões por feature crítica.
