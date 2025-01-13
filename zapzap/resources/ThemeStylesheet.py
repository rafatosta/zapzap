

class ThemeStylesheet:

    themes = {
        'light': "ThemeStylesheet.get_full_stylesheet()",
        'dark': ""
    }

    # Componentes separados como strings
    GENERAL_PUSHBUTTON = """
    QPushButton {
        background-color: #F5F7F9;
        color: #202C33;
        border: 1px solid #D0D4D8;
        padding: 5px 10px;
        font-size: 14px;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #E9ECEF;
        border: 1px solid #B0B6BB;
    }
    QPushButton:pressed {
        background-color: #DDE2E6;
        border: 1px solid #A0A6AB;
        color: #161E23;
    }
    QPushButton:disabled {
        background-color: #F0F2F5;
        color: #A6AEB6;
        border: 1px solid #D0D4D8;
    }
    """

    CHECKABLE_PUSHBUTTON = """
    QPushButton:checked {
        background-color: #00BD95;
        color: #FFFFFF;
        border: 1px solid #009C7A;
    }
    QPushButton:checked:hover {
        background-color: #009C7A;
        border: 1px solid #007F63;
    }
    QPushButton:checked:pressed {
        background-color: #007F63;
        border: 1px solid #006C55;
    }
    """

    SIDEBAR = """
    QWidget#sidebar {
        background-color: #f0f2f5;
        border-right: 1px solid #c0c1c4;
        padding: 10px;
    }
    """

    SIDEBAR_MENU_BUTTONS = """
    QWidget#menu_layout QPushButton {
        background-color: #f0f2f5;
        color: #202c33;
        border: none;
        padding: 10px 15px;
        text-align: left;
        font-size: 14px;
        border-radius: 4px;
        border-left: 3px solid #a8a9ab;
    }
    QWidget#menu_layout QPushButton:hover {
        background-color: #f9f9fb;
        border-left: 4px solid #00BD95;
    }
    QWidget#menu_layout QPushButton:pressed {
        background-color: #d8d9dc;
        color: #202c33;
    }
    QWidget#menu_layout QPushButton:disabled {
        background-color: #d8d9dc;
        border-left: 4px solid #00BD95;
    }
    """

    LABELS = """
    QLabel {
        color: #202C33; /* Cor do texto */
        font-size: 14px; /* Tamanho do texto */
        background-color: transparent; /* Fundo transparente */
        padding: 2px 0; /* Espaçamento interno */
    }

    /* Estilo para QLabel com texto de destaque */
    QLabel[role="highlight"] {
        color: #00BD95; /* Texto destacado em verde */
        font-weight: bold; /* Negrito para destaque */
    }

    /* Estilo para QLabel desativado */
    QLabel:disabled {
        color: #A6AEB6; /* Texto desbotado */
    }
    QWidget#menu_layout QLabel {
        color: #78797a;
        padding: 2px 0;
        margin-top: 8px;
    }
    """

    SETTINGS_BUTTONS = """
    QWidget#settings_buttons_layout QPushButton {
        background-color: #f0f2f5;
        border: none;
        border-radius: none;
        qproperty-flat: true;
    }
    QWidget#settings_buttons_layout QPushButton:hover {
        border-radius: 2px;
        border-left: 3px solid #a8a9ab;
    }
    QWidget#settings_buttons_layout QPushButton:pressed {
        background-color: rgba(225, 225, 225, 0.3);
        border-radius: 2px;
        height: 30px;
        border-left: 3px solid #00BD95;
    }
    """

    FRAMES = """
    QFrame[frameShape="4"] {
        border: none;
        border-bottom: 1px solid rgba(192, 191, 188, 0.2);
    }
    QFrame[frameShape="5"] {
        border: none;
        border-left: 1px solid rgba(192, 191, 188, 0.2);
    }
    #frame_accounts #frame_carduser {
        background-color: #F5F7F9; /* Fundo claro */
        border: 1px solid #D0D4D8; /* Borda suave */
        border-radius: 6px; /* Bordas arredondadas */
        padding: 10px; /* Espaçamento interno */
    }
    """

    SPECIAL_BUTTONS = """
    #btn_back {
        color: rgb(61, 56, 70);
        text-align: left;
    }
    #btn_back:hover {
        color: rgb(98, 160, 234);
    }
    #btn_quit {
        color: rgb(61, 56, 70);
        text-align: left;
    }
    #btn_quit:hover {
        color: rgb(224, 27, 36);
    }
    """

    COMBOBOX = """
    QComboBox {
        background-color: #F5F7F9;
        color: #202C33;
        border: 1px solid #D0D4D8;
        padding: 5px 10px;
        font-size: 14px;
        border-radius: 6px;
        combobox-popup: 0;
    }
    QComboBox:hover {
        background-color: #E9ECEF;
        border: 1px solid #B0B6BB;
    }
    QComboBox:pressed {
        background-color: #DDE2E6;
        border: 1px solid #A0A6AB;
    }
    QComboBox:disabled {
        background-color: #F0F2F5;
        color: #A6AEB6;
        border: 1px solid #D0D4D8;
    }
    QComboBox::drop-down {
        border: none;
        background-color: transparent;
        width: 30px;
    }
    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
    }
    """

    LINE_EDIT = """
    QLineEdit {
        background-color: #F5F7F9;
        color: #202C33;
        border: 1px solid #D0D4D8;
        padding: 5px 10px;
        font-size: 14px;
        border-radius: 6px;
    }
    QLineEdit:hover {
        background-color: #E9ECEF;
        border: 1px solid #B0B6BB;
    }
    QLineEdit:focus {
        background-color: #FFFFFF;
        border: 1px solid #00BD95;
        outline: none;
    }
    QLineEdit:disabled {
        background-color: #F0F2F5;
        color: #A6AEB6;
        border: 1px solid #D0D4D8;
    }
    """

    MENU = """
    /* Estilo geral do QMenu */
    QMenu {
        background-color: #FFFFFF; /* Fundo do menu */
        border: 1px solid #D0D4D8; /* Borda suave */
        border-radius: 6px; /* Bordas arredondadas */
        padding: 5px; /* Espaçamento interno */
        color: #202C33; /* Cor do texto */
        font-size: 14px; /* Tamanho do texto */
    }

    /* Itens do QMenu */
    QMenu::item {
        background-color: transparent; /* Fundo transparente por padrão */
        padding: 6px 12px; /* Espaçamento interno para cada item */
        margin: 2px 0; /* Espaçamento entre itens */
        border-radius: 4px; /* Bordas arredondadas dos itens */
    }

    /* Itens ao passar o mouse */
    QMenu::item:selected {
        background-color: #E9ECEF; /* Fundo claro ao passar o mouse */
        color: #202C33; /* Cor do texto ao passar o mouse */
    }

    /* Itens pressionados */
    QMenu::item:pressed {
        background-color: #DDE2E6; /* Fundo mais escuro ao pressionar */
        color: #161E23; /* Texto mais escuro ao pressionar */
    }

    /* QMenu desativado */
    QMenu:disabled {
        background-color: #F5F7F9; /* Fundo mais claro */
        border: 1px solid #D0D4D8; /* Borda suave */
        color: #A6AEB6; /* Texto desbotado para indicar desativado */
    }

    /* Itens do QMenu desativados */
    QMenu::item:disabled {
        color: #A6AEB6; /* Texto desbotado */
        background-color: transparent; /* Fundo transparente */
    }

    /* Sombra para o QMenu */
    QMenu::indicator {
        border: none;
        width: 16px;
        height: 16px;
    }

    /* Submenu indicador */
    QMenu::right-arrow {
        padding-left: 8px;
    }
    """

    TABLE = """
    /* Estilo geral para QTableWidget */
    QTableWidget {
        background-color: #F5F7F9; /* Fundo claro */
        color: #202C33; /* Texto escuro */
        border: 1px solid #D0D4D8; /* Borda suave */
        gridline-color: #D0D4D8; /* Cor das linhas de grade */
        font-size: 14px; /* Tamanho do texto */
        border-radius: 6px; /* Bordas arredondadas */
    }

    /* Cabeçalho horizontal */
    QHeaderView::section {
        background-color: #E9ECEF; /* Fundo do cabeçalho */
        color: #202C33; /* Texto do cabeçalho */
        padding: 5px; /* Espaçamento interno */
        border: 1px solid #D0D4D8; /* Borda das seções */
        font-weight: bold; /* Negrito para destaque */
    }

    /* Hover no cabeçalho */
    QHeaderView::section:hover {
        background-color: #DDE2E6; /* Fundo ao passar o mouse */
        border: 1px solid #B0B6BB; /* Realce da borda */
    }

    /* Linhas selecionadas */
    QTableWidget::item:selected {
        background-color: #00BD95; /* Fundo da linha selecionada */
        color: #FFFFFF; /* Texto da linha selecionada */
    }

    /* Alternância de linhas */
    QTableWidget::item {
        background-color: #FFFFFF; /* Fundo padrão */
    }

    QTableWidget::item:nth-child(even) {
        background-color: #F0F2F5; /* Fundo alternado */
    }

    /* Roladores (scrollbars) */
    QScrollBar:vertical {
        background: #E9ECEF; /* Fundo do scrollbar */
        width: 10px; /* Largura do scrollbar */
        margin: 0px 0px 0px 0px;
        border: none;
    }

    QScrollBar::handle:vertical {
        background: #B0B6BB; /* Cor do manipulador */
        min-height: 20px;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical:hover {
        background: #00BD95; /* Realce ao passar o mouse */
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        background: none;
        border: none;
    }

    /* Estado desativado */
    QTableWidget::item:disabled {
        background-color: #F0F2F5; /* Fundo desativado */
        color: #A6AEB6; /* Texto desativado */
    }
    """

    GROUP_BOX = """
    /* Estilo geral do QGroupBox */
    QGroupBox {
        background-color: #F5F7F9; /* Fundo claro */
        color: #202C33; /* Cor do texto */
        border: 1px solid #D0D4D8; /* Borda suave */
        border-radius: 6px; /* Bordas arredondadas */
        margin-top: 20px; /* Espaço entre o título e o conteúdo */
        padding: 10px; /* Espaçamento interno */
    }

    /* Título do QGroupBox */
    QGroupBox::title {
        background-color: transparent; /* Fundo transparente */
        color: #202C33; /* Cor do texto do título */
        subcontrol-origin: margin; /* Posicionamento do título */
        subcontrol-position: top left; /* Alinhado à esquerda, no topo */
        padding: 0 5px; /* Espaçamento interno no título */
        font-weight: bold; /* Título em negrito */
        font-size: 14px; /* Tamanho do texto */
    }

    /* QGroupBox desativado */
    QGroupBox:disabled {
        background-color: #F0F2F5; /* Fundo mais claro */
        color: #A6AEB6; /* Texto desbotado */
        border: 1px solid #D0D4D8; /* Borda neutra */
    }

    /* Título desativado */
    QGroupBox:disabled::title {
        color: #A6AEB6; /* Título desbotado */
    }
    """
    
    CHECK_BOX = """
    /* Estilo geral para QCheckBox */
    QCheckBox {
        color: #202C33; /* Cor do texto */
        font-size: 14px; /* Tamanho do texto */
        padding: 5px 0; /* Espaçamento interno */
    }

    /* Estilo do marcador (caixa) do QCheckBox */
    QCheckBox::indicator {
        width: 10px; /* Largura da caixa */
        height: 10px; /* Altura da caixa */
        border: 2px solid #D0D4D8; /* Borda suave */
        border-radius: 4px; /* Bordas arredondadas */
        background-color: #FFFFFF; /* Fundo da caixa */
    }

    /* Quando o QCheckBox estiver marcado */
    QCheckBox::indicator:checked {
        background-color: #00BD95; /* Fundo verde para marcado */
        border: 2px solid #00BD95; /* Borda verde */
    }

    /* Quando o QCheckBox estiver desmarcado */
    QCheckBox::indicator:unchecked {
        background-color: #F5F7F9; /* Fundo claro para desmarcado */
        border: 2px solid #D0D4D8; /* Borda suave */
    }

    /* Efeito ao passar o mouse */
    QCheckBox:hover {
        color: #00BD95; /* Texto com realce */
    }

    /* QCheckBox desativado */
    QCheckBox:disabled {
        color: #A6AEB6; /* Texto mais claro para indicar desativado */
    }
    """

    RADIO_BUTTON = """
    QRadioButton {
        color: #202C33; /* Cor do texto */
        font-size: 14px; /* Tamanho do texto */
        padding: 5px 0; /* Espaçamento interno */
    }

    /* Estilo do indicador (círculo) */
    QRadioButton::indicator {
        width: 10px; /* Largura do círculo */
        height: 10px; /* Altura do círculo */
        border: 2px solid #D0D4D8; /* Borda suave */
        border-radius: 6px; /* Círculo perfeito */
        background-color: #FFFFFF; /* Fundo do círculo */
    }

    /* Quando o QRadioButton estiver marcado */
    QRadioButton::indicator:checked {
        background-color: #00BD95; /* Fundo verde para marcado */
        border: 2px solid #00BD95; /* Borda verde */
    }

    /* Quando o QRadioButton estiver desmarcado */
    QRadioButton::indicator:unchecked {
        background-color: #F5F7F9; /* Fundo claro para desmarcado */
        border: 2px solid #D0D4D8; /* Borda suave */
    }

    /* Estilo desativado */
    QRadioButton:disabled {
        color: #A6AEB6; /* Texto desbotado */
    }

    QRadioButton::indicator:disabled {
        background-color: #F0F2F5; /* Fundo claro desativado */
        border: 2px solid #D0D4D8; /* Borda neutra */
    }
    """
    def get_stylesheet() -> str:
        components = [
            ThemeStylesheet.GENERAL_PUSHBUTTON,
            ThemeStylesheet.CHECKABLE_PUSHBUTTON,
            ThemeStylesheet.SIDEBAR,
            ThemeStylesheet.SIDEBAR_MENU_BUTTONS,
            ThemeStylesheet.LABELS,
            ThemeStylesheet.SETTINGS_BUTTONS,
            ThemeStylesheet.FRAMES,
            ThemeStylesheet.SPECIAL_BUTTONS,
            ThemeStylesheet.COMBOBOX,
            ThemeStylesheet.LINE_EDIT,
            ThemeStylesheet.MENU,
            ThemeStylesheet.TABLE,
            ThemeStylesheet.GROUP_BOX,
            ThemeStylesheet.CHECK_BOX,
            ThemeStylesheet.RADIO_BUTTON,
        ]
        return "\n".join(components)
