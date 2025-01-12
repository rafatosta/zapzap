from PyQt6.QtCore import QTimer
from PyQt6.QtDBus import QDBusInterface
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from enum import Enum
from zapzap.services.SettingsManager import SettingsManager


class ThemeManager:
    class Type(Enum):
        Auto = "auto"
        Light = "light"
        Dark = "dark"

    _instance = None

    # Dicionário com temas
    themes = {
        "light": """
            /* genéricos */
            /* QStackedWidget#pages*/
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

            /* Sidebar geral */
            QWidget#sidebar {
                background-color: #f0f2f5;
                border-right: 1px solid #c0c1c4;
                padding: 10px; /* Para espaçamento interno */
            }

            /* Botões da Sidebar */
            /* Estilo exclusivo para botões de QWidget#menu_layout */
            QWidget#menu_layout QPushButton {
                background-color: #f0f2f5; /* Estilo exclusivo */
                color: #202c33;
                border: none;
                padding: 10px 15px;
                text-align: left;
                font-size: 14px;
                border-radius: 4px;
                border-left: 3px solid #a8a9ab;
            }

            /* Efeito hover exclusivo */
            QWidget#menu_layout QPushButton:hover {
                background-color: #f9f9fb;
                border-left: 4px solid #00BD95;
            }

            /* Estilo pressionado exclusivo */
            QWidget#menu_layout QPushButton:pressed {
                background-color: #d8d9dc;
                color: #202c33;
            }

            /* Estilo desativado exclusivo */
            QWidget#menu_layout QPushButton:disabled {
                background-color: #d8d9dc;
                border-left: 4px solid #00BD95;
            }

            /* Labels na Sidebar */
            QWidget#menu_layout QLabel {
                color: #78797a;
                padding: 2px 0;
                margin-top: 8px; /* Espaçamento entre labels */
            }

            /* Botões do settings_buttons_layout (Browser)*/
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

            QFrame[frameShape="4"] {
                border: none;
                border-bottom: 1px solid rgba(192, 191, 188, 0.2);
            }
            QFrame[frameShape="5"] {
                border: none;
                border-left: 1px solid rgba(192, 191, 188, 0.2);
            } 

			#btn_back{
				color: rgb(61, 56, 70);
				text-align: left;
			}
			#btn_back:hover{
				color: rgb(98, 160, 234);
			}

			#btn_quit{
				color: rgb(61, 56, 70);
				text-align: left;
			}
			#btn_quit:hover{
				color: rgb(224, 27, 36);
			}

             """,
        "dark":
            """
                /* Sidebar geral */
                QWidget#sidebar {
                    background-color: #202C33;
                    border-right: 1px solid #192328;
                    padding: 10px; /* Espaçamento interno */
                }

                /* Botões da Sidebar */
                QWidget#menu_layout QPushButton {
                    background-color: #202C33;
                    color: #F0F2F5;
                    border: none;
                    padding: 10px 15px;
                    text-align: left;
                    font-size: 14px;
                    border-radius: 4px;
                    border-left: 3px solid rgb(154, 153, 150);
                }
                QWidget#menu_layout QPushButton:hover {
                    background-color: #161e23;
                    border-left: 4px solid #00BD95;
                }
                QWidget#menu_layout QPushButton:pressed {
                    background-color: #0c1114;
                    color: #F0F2F5;
                }
                QWidget#menu_layout QPushButton:disabled {
                    background-color: #161e23;
                    border-left: 4px solid #00BD95;
                }

                /* Labels na Sidebar */
                QWidget#menu_layout QLabel {
                    color: #a6a9ab;
                    padding: 2px 0;
                    margin-top: 8px; /* Espaçamento entre labels */
                }

                /* Botões do browser */
                QWidget#settings_buttons_layout QPushButton {
                    qproperty-flat: true;
                }
                QWidget#settings_buttons_layout QPushButton:hover {
                    border-radius: 2px;
                    border-left: 3px solid #a8a9ab;
                }
                QWidget#settings_buttons_layout QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 2px;
                    height: 30px;
                    border-left: 3px solid #00BD95;
                }

                /* Linhas de separação */
                QFrame[frameShape="4"] {
                    border: none;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                QFrame[frameShape="5"] {
                    border: none;
                    border-left: 1px solid rgba(255, 255, 255, 0.1);
                }

                /* Botões específicos */
                #btn_back, #btn_quit {
                    color: rgb(200, 200, 200);
                    text-align: left;
                }
                #btn_back:hover {
                    color: rgb(98, 160, 234);
                }
                #btn_quit:hover {
                    color: rgb(224, 27, 36);
                }"""
    }

    def __new__(cls, *args, **kwargs):
        """Implementação do padrão Singleton."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa o ThemeManager com as configurações do sistema."""
        if not self._initialized:
            self._initialized = True
            self.current_theme = ThemeManager.Type(
                SettingsManager.get("system/theme", ThemeManager.Type.Auto)
            )
            self.timer = QTimer()
            # Verifica o tema do sistema a cada segundo
            self.timer.setInterval(1000)
            self.timer.timeout.connect(self.sync_system_theme)

    # === Métodos Públicos ===
    @staticmethod
    def instance() -> 'ThemeManager':
        """Obtém a instância singleton do ThemeManager."""
        if ThemeManager._instance is None:
            ThemeManager()
        return ThemeManager._instance

    @staticmethod
    def start():
        """Inicia o ThemeManager e sincroniza o tema com as configurações."""
        instance = ThemeManager.instance()
        if instance.current_theme == ThemeManager.Type.Auto:
            instance.timer.start()
            instance.sync_system_theme()
        else:
            instance._apply_theme()

    @staticmethod
    def set_theme(theme: Type):
        """Define o tema de acordo com a preferência do usuário."""
        instance = ThemeManager.instance()
        instance._set_user_theme(theme)
        # Salva o tema nas configurações
        SettingsManager.set("system/theme", theme.value)

    @staticmethod
    def get_current_theme() -> Type:
        """Obtém o tema atual."""
        return ThemeManager.instance().current_theme

    @staticmethod
    def sync():
        """Força a sincronização do tema atual."""
        instance = ThemeManager.instance()
        instance._apply_theme()

    # === Sincronização e Aplicação de Temas ===
    def sync_system_theme(self):
        """Sincroniza o tema do sistema com o tema atual."""
        theme = self._detect_system_theme()
        if self.current_theme != theme:
            self.current_theme = theme
            self._apply_theme()

    def _set_user_theme(self, theme: Type):
        """Define o tema com base na escolha do usuário."""
        if theme == ThemeManager.Type.Auto:
            self.timer.start()
        else:
            self.timer.stop()
            self.current_theme = theme
            self._apply_theme()

    def _apply_theme(self):
        """Aplica o tema atual."""
        if self.current_theme == ThemeManager.Type.Light:
            self._apply_light_theme()
        elif self.current_theme == ThemeManager.Type.Dark:
            self._apply_dark_theme()

    # === Implementação dos Temas Claro e Escuro ===
    def _apply_light_theme(self):
        """Aplica o tema claro."""
        print("Aplicando tema claro...")
        palette = self._create_palette(
            window="#f0f2f5", text="#000000", base="#f0f0f0", highlight="#0066cc"
        )
        self._apply_palette(palette)
        QApplication.instance().getWindow().browser.set_theme_light()
        QApplication.instance().setStyleSheet(self.themes['light'])

    def _apply_dark_theme(self):
        """Aplica o tema escuro."""
        print("Aplicando tema escuro...")
        palette = self._create_palette(
            window="#202C33", text="#ffffff", base="#3a3a3a", highlight="#0099ff"
        )
        self._apply_palette(palette)
        QApplication.instance().getWindow().browser.set_theme_dark()
        QApplication.instance().setStyleSheet(self.themes['dark'])

    def _create_palette(self, window, text, base, highlight):
        """Cria uma paleta com cores fornecidas."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(window))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text))
        palette.setColor(QPalette.ColorRole.Base, QColor(base))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(base))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(text))
        palette.setColor(QPalette.ColorRole.Text, QColor(text))
        palette.setColor(QPalette.ColorRole.Button, QColor(base))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(text))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(highlight))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(text))
        return palette

    def _apply_palette(self, palette):
        """Aplica a paleta ao aplicativo."""
        QApplication.instance().setPalette(palette)

    # === Detecção do Tema do Sistema ===
    def _detect_system_theme(self) -> Type:
        """
        Determina o tema do sistema usando a interface D-Bus.
        Retorna:
            - ThemeManager.Type.Dark se o tema escuro for preferido
            - ThemeManager.Type.Light se o tema claro for preferido
        """
        try:
            interface = QDBusInterface(
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.Settings",
            )
            msg = interface.call(
                "Read", "org.freedesktop.appearance", "color-scheme")
            color_scheme = msg.arguments()[0]
            return ThemeManager.Type.Dark if color_scheme == 1 else ThemeManager.Type.Light
        except Exception as e:
            print(f"Erro ao obter o tema do sistema: {e}")
            return ThemeManager.Type.Light
