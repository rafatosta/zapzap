class ThemeStylesheet:

    # Componentes separados como strings
    PUSHBUTTON = {
        "light": """
            QPushButton {
                background-color: #ffffff;
                color: #1d1f1f;
                border: 1px solid #D0D4D8;
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #f7f5f3;
                border: 1px solid #B0B6BB;
            }
            QPushButton:pressed {
                background-color: #DDE2E6;
                border: 1px solid #A0A6AB;
                color: #161E23;
            }
            QPushButton:disabled {
                background-color: #f7f5f3;
                color: #A6AEB6;
                border: 1px solid #D0D4D8;
            }
        """,
        "dark": """
            QPushButton {
                background-color: #242626;
                color: #E1E1E1;
                border: 1px solid #242626;
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #242626;
                border: 1px solid #6A6A6A;
            }
            QPushButton:pressed {
                background-color: #192328;
                border: 1px solid #242626;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #242626;
                color: #1d1f1f;
                border: 1px solid #242626;
            }
        """
    }

    TOOLTIP = {
        "light": """
            QToolTip {
                background-color: #ffffff; /* Fundo branco */
                color: #000000; /* Texto preto */
                border: 1px solid #cccccc; /* Borda cinza clara */
                border-radius: 4px; /* Bordas arredondadas */
                padding: 4px; /* Espaçamento interno */
                font-size: 12px; /* Tamanho da fonte */
            }
            """,
        "dark": """
            QToolTip {
                background-color: #333333; /* Fundo cinza escuro */
                color: #ffffff; /* Texto branco */
                border: 1px solid #aaaaaa; /* Borda cinza média */
                border-radius: 4px; /* Bordas arredondadas */
                padding: 4px; /* Espaçamento interno */
                font-size: 12px; /* Tamanho da fonte */
            }
        """
    }

    CHECKABLE_PUSHBUTTON = {
        "light": """
            QPushButton:checked {
                background-color: #21c063;
                color: #FFFFFF;
                border: 1px solid #6C6C70;
            }
            QPushButton:checked:hover {
                background-color: #6C6C70;
                border: 1px solid #4A4A4F;
            }
            QPushButton:checked:pressed {
                background-color: #4A4A4F;
                border: 1px solid #38383C;
            }
        """,
        "dark": """
            QPushButton:checked {
                background-color: #21c063;
                color: #FFFFFF;
                border: 1px solid #6C6C70;
            }
            QPushButton:checked:hover {
                background-color: #6C6C70;
                border: 1px solid #4A4A4F;
            }
            QPushButton:checked:pressed {
                background-color: #4A4A4F;
                border: 1px solid #38383C;
            }
        """
    }

    SIDEBAR = {
        "light": """
            QWidget#sidebar {
                background-color: #f7f5f3;
                border-right: 1px solid #c0c1c4;
                padding: 10px;
            }
        """,
        "dark": """
            QWidget#sidebar {
                background-color: #1d1f1f;
                border-right: 1px solid #1d1f1f;
                padding: 10px;
            }
        """
    }

    SIDEBAR_SETTINGS_BUTTONS = {
        "light": """
            QWidget#menu_layout QPushButton {
                background-color: #f7f5f3;
                color: #1d1f1f;
                border: none;
                padding: 10px 15px;
                text-align: left;
                font-size: 14px;
                border-radius: 4px;
                border-left: 3px solid #1daa61;
            }
            QWidget#menu_layout QPushButton:hover {
                background-color: #f7f5f3;
                border-left: 4px solid #1daa61;
            }
            QWidget#menu_layout QPushButton:pressed {
                background-color: #eae9e7;
                color: #1d1f1f;
            }
            QWidget#menu_layout QPushButton:disabled {
                background-color: #eae9e7;
                border-left: 4px solid #21c063;
            }
        """,
        "dark": """
            QWidget#menu_layout QPushButton {
                background-color: #1d1f1f;
                color: #E1E1E1;
                border: none;
                padding: 10px 15px;
                text-align: left;
                font-size: 14px;
                border-radius: 4px;
                border-left: 3px solid #1d1f1f;
            }
            QWidget#menu_layout QPushButton:hover {
                background-color: #1d1f1f;
                border-left: 4px solid #21c063;
            }
            QWidget#menu_layout QPushButton:pressed {
                background-color: #242626;
                color: #FFFFFF;
            }
            QWidget#menu_layout QPushButton:disabled {
                background-color: #242626;
                border-left: 4px solid #21c063;
            }
        """
    }

    LABELS = {
        "light": """
            QLabel {
                color: #1d1f1f; /* Cor do texto */
                font-size: 14px; /* Tamanho do texto */
                background-color: transparent; /* Fundo transparente */
                padding: 2px 0; /* Espaçamento interno */
            }

            /* Estilo para QLabel com texto de destaque */
            QLabel[role="highlight"] {
                color: #21c063; /* Texto destacado em cinza */
                
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
        """,
        "dark": """
            QLabel {
                color: #E1E1E1; /* Cor do texto */
                font-size: 14px; /* Tamanho do texto */
                background-color: transparent; /* Fundo transparente */
                padding: 2px 0; /* Espaçamento interno */
            }

            /* Estilo para QLabel com texto de destaque */
            QLabel[role="highlight"] {
                color: #21c063; /* Texto destacado em cinza */
                 /* Negrito para destaque */
            }

            /* Estilo para QLabel desativado */
            QLabel:disabled {
                color: #A6AEB6; /* Texto desbotado */
            }
            QWidget#menu_layout QLabel {
                color: #A6AEB6;
                padding: 2px 0;
                margin-top: 8px;
            }
        """
    }

    SIDEBAR_BROWSER_BUTTONS = {
        "light": """
            QWidget#settings_buttons_layout QPushButton {
                background-color: #f7f5f3;
                border: none;
                border-radius: none;
                qproperty-flat: true;
            }
            QWidget#settings_buttons_layout QPushButton:hover {
                border-radius: 2px;
                border-left: 3px solid #1daa61;
            }
            QWidget#settings_buttons_layout QPushButton:pressed {
                background-color: rgba(225, 225, 225, 0.3);
                border-radius: 2px;
                height: 30px;
                border-left: 3px solid #1daa61;
            }
        """,
        "dark": """
            QWidget#settings_buttons_layout QPushButton {
                background-color: #1d1f1f;
                border: none;
                border-radius: none;
                qproperty-flat: true;
            }
            QWidget#settings_buttons_layout QPushButton:hover {
            background-color: #292a2a;
                border-radius: 2px;
                border-left: 3px solid #1daa61;
            }
            QWidget#settings_buttons_layout QPushButton:pressed {
                background-color: rgba(60, 60, 60, 0.3);
                border-radius: 2px;
                height: 30px;
                border-left: 3px solid #1daa61;
            }
        """
    }

    FRAMES = {
        "light": """
            QFrame[frameShape="4"] {
                border: none;
                border-bottom: 1px solid rgba(192, 191, 188, 0.2);
            }
            QFrame[frameShape="5"] {
                border: none;
                border-left: 1px solid rgba(192, 191, 188, 0.2);
            }
            #frame_accounts #frame_carduser {
                background-color: #ffffff; /* Fundo claro */
                border: 1px solid #D0D4D8; /* Borda suave */
                border-radius: 6px; /* Bordas arredondadas */
                padding: 10px; /* Espaçamento interno */
            }
        """,
        "dark": """
            QFrame[frameShape="4"] {
                border: none;
                border-bottom: 1px solid #626b70;
            }
            QFrame[frameShape="5"] {
                border: none;
                border-left: 1px solid #626b70;
            }
            #frame_accounts #frame_carduser {
                background-color: #1d1f1f; /* Fundo escuro */
                border: 1px solid #1d1f1f; /* Borda suave */
                border-radius: 6px; /* Bordas arredondadas */
                padding: 10px; /* Espaçamento interno */
            }
        """
    }

    SPECIAL_BUTTONS = {
        "light": """
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
        """,
        "dark": """
            #btn_back {
                color: rgb(191, 191, 191);
                text-align: left;
            }
            #btn_back:hover {
                color: rgb(98, 160, 234);
            }
            #btn_quit {
                color: rgb(191, 191, 191);
                text-align: left;
            }
            #btn_quit:hover {
                color: rgb(224, 27, 36);
            }
        """
    }

    COMBOBOX = {
        "light": """
            QComboBox {
                background-color: #ffffff;
                color: #1d1f1f;
                border: 1px solid #D0D4D8;
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 6px;
                combobox-popup: 0;
            }
            QComboBox:hover {
                background-color: #f7f5f3;
                border: 1px solid #B0B6BB;
            }
            QComboBox:pressed {
                background-color: #DDE2E6;
                border: 1px solid #A0A6AB;
            }
            QComboBox:disabled {
                background-color: #f7f5f3;
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
        """,
        "dark": """
            QComboBox {
                background-color: #1d1f1f;
                color: #E1E1E1;
                border: 1px solid #1d1f1f;
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 6px;
                combobox-popup: 0;
            }
            QComboBox:hover {
                background-color: #242626;
                border: 1px solid #1d1f1f;
            }
            QComboBox:pressed {
                background-color: #1d1f1f;
                border: 1px solid #A0A6AB;
            }
            QComboBox:disabled {
                background-color: #1d1f1f;
                color: #A6AEB6;
                border: 1px solid #1d1f1f;
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
            QComboBox QAbstractItemView {
                background-color: #161e23;
                selection-background-color: #21c063;
                padding: 6px 12px;
                margin: 2px 0;
                border-radius: 4px;
            }   
        """
    }

    LINE_EDIT = {
        "light": """
            QLineEdit {
                background-color: #ffffff;
                color: #1d1f1f;
                border: 1px solid #D0D4D8;
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 6px;
            }
            QLineEdit:hover {
                background-color: #f7f5f3;
                border: 1px solid #B0B6BB;
            }
            QLineEdit:focus {
                background-color: #FFFFFF;
                border: 1px solid #21c063;
                outline: none;
            }
            QLineEdit:disabled {
                background-color: #f7f5f3;
                color: #A6AEB6;
                border: 1px solid #D0D4D8;
            }
        """,
        "dark": """
            QLineEdit {
                background-color: #1d1f1f;
                color: #E1E1E1;
                border: 1px solid #1d1f1f;
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 6px;
            }
            QLineEdit:hover {
                background-color: #242626;
                border: 1px solid #1d1f1f;
            }
            QLineEdit:focus {
                background-color: #242626;
                border: 1px solid #21c063;
                outline: none;
            }
            QLineEdit:disabled {
                background-color: #1d1f1f;
                color: #A6AEB6;
                border: 1px solid #1d1f1f;
            }
        """
    }

    MENU = {
        "light": """
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #D0D4D8;
                border-radius: 6px;
                padding: 5px;
                color: #1d1f1f;
                font-size: 14px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 6px 12px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f7f5f3;
                color: #1d1f1f;
            }
            QMenu::item:pressed {
                background-color: #DDE2E6;
                color: #161E23;
            }
            QMenu:disabled {
                background-color: #ffffff;
                border: 1px solid #D0D4D8;
                color: #A6AEB6;
            }
            QMenu::item:disabled {
                color: #A6AEB6;
                background-color: transparent;
            }
            QMenu::indicator {
                width: 10px;
                height: 10px;
                border: 2px solid #D0D4D8;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QMenu::indicator:checked {
                background-color: #21c063;
                border: 2px solid #21c063;
            }
            QMenu::indicator:unchecked {
                background-color: #ffffff;
                border: 2px solid #D0D4D8;
            }
            QMenu::right-arrow {
                padding-left: 8px;
            }
        """,
        "dark": """
            QMenu {
                background-color: #2E2E2E;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 5px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 6px 12px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #444444;
                color: #FFFFFF;
            }
            QMenu::item:pressed {
                background-color: #666666;
                color: #FFFFFF;
            }
            QMenu:disabled {
                background-color: #333333;
                border: 1px solid #555555;
                color: #777777;
            }
            QMenu::item:disabled {
                color: #777777;
                background-color: transparent;
            }
            QMenu::indicator {
                width: 10px;
                height: 10px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #333333;
            }
            QMenu::indicator:checked {
                background-color: #21c063;
                border: 2px solid #21c063;
            }
            QMenu::indicator:unchecked {
                background-color: #444444;
                border: 2px solid #555555;
            }
            QMenu::right-arrow {
                padding-left: 8px;
            }
            """
    }

    TABLE = {
        "light": """
            QTableWidget {
                background-color: #ffffff;
                color: #1d1f1f;
                border: 1px solid #D0D4D8;
                gridline-color: #D0D4D8;
                font-size: 14px;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #f7f5f3;
                color: #1d1f1f;
                padding: 5px;
                border: 1px solid #D0D4D8;
            }
            QHeaderView::section:hover {
                background-color: #DDE2E6;
                border: 1px solid #B0B6BB;
            }
            QTableWidget::item:selected {
                background-color: #21c063;
                color: #FFFFFF;
            }
            QTableWidget::item {
                background-color: #FFFFFF;
            }
            QTableWidget::item:nth-child(even) {
                background-color: #f7f5f3;
            }
            QScrollBar:vertical {
                background: #f7f5f3;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #B0B6BB;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #21c063;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            QTableWidget::item:disabled {
                background-color: #f7f5f3;
                color: #A6AEB6;
            }
        """,
        "dark": """
            QTableWidget {
                background-color: #2E2E2E;
                color: #E1E1E1;
                border: 1px solid #444444;
                gridline-color: #555555;
                font-size: 14px;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #444444;
                color: #E1E1E1;
                padding: 5px;
                border: 1px solid #555555;
            }
            QHeaderView::section:hover {
                background-color: #555555;
                border: 1px solid #666666;
            }
            QTableWidget::item:selected {
                background-color: #21c063;
                color: #FFFFFF;
            }
            QTableWidget::item {
                background-color: #333333;
            }
            QTableWidget::item:nth-child(even) {
                background-color: #444444;
            }
            QScrollBar:vertical {
                background: #444444;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #21c063;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            QTableWidget::item:disabled {
                background-color: #444444;
                color: #777777;
            }
            """
    }

    GROUP_BOX = {
        "light": """
            QGroupBox {
                background-color: #ffffff;
                color: #1d1f1f;
                border: 1px solid #D0D4D8;
                border-radius: 6px;
                margin-top: 20px;
                padding: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                color: #1d1f1f;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                font-size: 14px;
            }
            QGroupBox:disabled {
                background-color: #f7f5f3;
                color: #A6AEB6;
                border: 1px solid #D0D4D8;
            }
            QGroupBox:disabled::title {
                color: #A6AEB6;
            }

            QGroupBox:checked::title {
                color: #21c063;
            }
            QGroupBox::indicator {
                width: 10px;
                height: 10px;
                border: 2px solid #D0D4D8;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QGroupBox::indicator:checked {
                background-color: #21c063;
                border: 2px solid #21c063;
            }
            QGroupBox::indicator:unchecked {
                background-color: #ffffff;
                border: 2px solid #D0D4D8;
            }
        """,
        "dark": """
            QGroupBox {
                background-color: #242626;
                color: #E1E1E1;
                border: 1px solid #444444;
                border-radius: 6px;
                margin-top: 20px;
                padding: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                color: #E1E1E1;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;

                font-size: 14px;
            }
            QGroupBox:disabled {
                background-color: #333333;
                color: #777777;
                border: 1px solid #555555;
            }
            QGroupBox:disabled::title {
                color: #777777;
            }
            QGroupBox:checked::title {
                color: #21c063;
            }
            QGroupBox::indicator {
                width: 10px;
                height: 10px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #444444;
            }
            QGroupBox::indicator:checked {
                background-color: #21c063;
                border: 2px solid #21c063;
            }
            QGroupBox::indicator:unchecked {
                background-color: #2D3E44;
                border: 2px solid #555555;
            }
        """
    }

    CHECK_BOX = {
        "light": """
            QCheckBox {
                color: #1d1f1f;
                font-size: 14px;
                padding: 5px 0;
            }
            QCheckBox::indicator {
                width: 10px;
                height: 10px;
                border: 2px solid #D0D4D8;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #21c063;
                border: 2px solid #21c063;
            }
            QCheckBox::indicator:unchecked {
                background-color: #ffffff;
                border: 2px solid #D0D4D8;
            }
            QCheckBox:hover {
                color: #21c063;
            }
            QCheckBox:disabled {
                color: #A6AEB6;
            }
        """,
        "dark": """
            QCheckBox {
                color: #E1E1E1;
                font-size: 14px;
                padding: 5px 0;
            }
            QCheckBox::indicator {
                width: 10px;
                height: 10px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #333333;
            }
            QCheckBox::indicator:checked {
                background-color: #21c063;
                border: 2px solid #21c063;
            }
            QCheckBox::indicator:unchecked {
                background-color: #444444;
                border: 2px solid #555555;
            }
            QCheckBox:hover {
                color: #21c063;
            }
            QCheckBox:disabled {
                color: #777777;
            }
        """
    }

    RADIO_BUTTON = {
        "light": """
            QRadioButton {
                color: #1d1f1f;
                font-size: 14px;
                padding: 5px 0;
            }
            QRadioButton::indicator {
                width: 10px;
                height: 10px;
                border: 2px solid #D0D4D8;
                border-radius: 6px;
                background-color: #FFFFFF;
            }
            QRadioButton::indicator:checked {
                background-color: #21c063;
                border: 2px solid #21c063;
            }
            QRadioButton::indicator:unchecked {
                background-color: #ffffff;
                border: 2px solid #D0D4D8;
            }
            QRadioButton:disabled {
                color: #A6AEB6;
            }
            QRadioButton::indicator:disabled {
                background-color: #f7f5f3;
                border: 2px solid #D0D4D8;
            }
        """,
        "dark": """
            QRadioButton {
                color: #E1E1E1;
                font-size: 14px;
                padding: 5px 0;
            }
            QRadioButton::indicator {
                width: 10px;
                height: 10px;
                border: 2px solid #555555;
                border-radius: 6px;
                background-color: #333333;
            }
            QRadioButton::indicator:checked {
                background-color: #21c063;
                border: 2px solid #21c063;
            }
            QRadioButton::indicator:unchecked {
                background-color: #444444;
                border: 2px solid #555555;
            }
            QRadioButton:disabled {
                color: #777777;
            }
            QRadioButton::indicator:disabled {
                background-color: #444444;
                border: 2px solid #555555;
            }
        """
    }

    @staticmethod
    def get_stylesheet(theme) -> str:
        components = [
            ThemeStylesheet.PUSHBUTTON[theme],
            ThemeStylesheet.CHECKABLE_PUSHBUTTON[theme],
            ThemeStylesheet.SIDEBAR[theme],
            ThemeStylesheet.SIDEBAR_SETTINGS_BUTTONS[theme],
            ThemeStylesheet.LABELS[theme],
            ThemeStylesheet.SIDEBAR_BROWSER_BUTTONS[theme],
            ThemeStylesheet.FRAMES[theme],
            ThemeStylesheet.SPECIAL_BUTTONS[theme],
            ThemeStylesheet.COMBOBOX[theme],
            ThemeStylesheet.LINE_EDIT[theme],
            ThemeStylesheet.MENU[theme],
            ThemeStylesheet.TABLE[theme],
            ThemeStylesheet.GROUP_BOX[theme],
            ThemeStylesheet.CHECK_BOX[theme],
            ThemeStylesheet.RADIO_BUTTON[theme],
            ThemeStylesheet.TOOLTIP[theme]
        ]
        return "\n".join(components)