Estou migrando o Settings UI do ZapZap para uma arquitetura limpa e componentizada, inspirada em React.

Objetivo:
- Separar lógica de UI.
- Controllers devem manipular dados, sinais, SettingsManager e ações.
- Views devem montar interface gráfica.
- Componentes devem ser genéricos e reutilizáveis.

Arquitetura desejada:

zapzap/
  views/
    components/
      Label
      Button
      Card
      ToggleSwitch
      Section
      outros componentes genéricos quando necessário

    pages/
      PageNotifications
      futuras páginas de settings

  controllers/
    PageNotifications
    demais controllers

Regras:
- Evitar usar diretamente `QLabel`, `QPushButton`, etc. nas pages quando existir componente ZapZap equivalente.
- Em vez de `from PyQt6.QtWidgets import QLabel`, usar algo como `from zapzap.views.components import Label`.
- Se um componente genérico não resolver, criar um componente especializado.
- Componentes devem ser theme-aware individualmente.
- Cada componente deve observar mudança de tema/palette e reaplicar seu próprio estilo.
- Não usar um stylesheet global monolítico como fonte principal do tema.
- `ThemeManager` deve apenas:
  - aplicar `app.setPalette(...)`;
  - emitir/notificar mudança de tema;
  - não aplicar `app.setStyleSheet(...)` global.

Tema:
- Componentes usam tokens comuns light/dark.
- Componentes observam mudança de tema via ThemeManager/palette.
- O modelo final desejado é:

ThemeManager
  ├── app.setPalette(...)
  └── emite/notifica theme_changed

Componentes
  ├── observam palette/theme_changed
  ├── aplicam seus próprios estilos
  └── usam tokens comuns

Ponto importante:
- `_install_style_watcher()` e `apply_settings_style()` são considerados ponte temporária/legado.
- O objetivo é remover isso gradualmente quando o Settings shell e seus filhos forem migrados para componentes genéricos.

Página piloto:
- Começar pela PageNotifications.
- Criar `views/pages/PageNotifications.py` contendo apenas a UI.
- `controllers/PageNotifications.py` deve apenas:
  - instanciar a view;
  - carregar SettingsManager;
  - conectar sinais;
  - salvar SettingsManager.
- Preservar as chaves:
  - `notification/app`
  - `notification/show_photo`
  - `notification/show_name`
  - `notification/show_msg`
  - `notification/donation_message`