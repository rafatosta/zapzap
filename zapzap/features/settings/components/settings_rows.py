from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget, QVBoxLayout

from zapzap.ui.components import Button, ComboBox, Label, LineEdit, ToggleSwitch


class SettingsToggleSwitch(ToggleSwitch):
    """
    Toggle switch específico para telas de configurações.

    Especializa o componente genérico ToggleSwitch apenas para definir um
    objectName próprio, permitindo estilização específica via QSS/CSS.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingsToggleSwitch")


class _BaseRow(QWidget):
    """
    Classe base para linhas de configuração.

    Fornece a estrutura visual comum das linhas de configurações:
    título, descrição opcional e um controle alinhado à direita.

    Esta classe deve ser usada como base para componentes mais específicos,
    como linhas com switch, combo box, botão, campo de texto ou seletor de caminho.
    """

    def __init__(
        self,
        title,
        description="",
        control=None,
        parent=None,
        control_stretch=0,
    ):
        super().__init__(parent)

        self.setMinimumHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)

        text_col = QWidget()
        col = QVBoxLayout(text_col)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(3)

        self.title_label = Label(title, "row_title")
        self.title_label.setObjectName("SettingsRowTitle")
        col.addWidget(self.title_label)

        self.description_label = None

        if description:
            self.description_label = Label(description, "row_description")
            self.description_label.setObjectName("SettingsRowDescription")
            self.description_label.setWordWrap(True)
            col.addWidget(self.description_label)

        layout.addWidget(text_col, 1)

        if control:
            layout.addWidget(
                control,
                control_stretch,
                Qt.AlignmentFlag.AlignVCenter,
            )

        self.control = control


class SettingsSwitchRow(_BaseRow):
    """
    Linha de configuração com switch liga/desliga.

    Indicada para opções booleanas, como habilitar notificações,
    iniciar minimizado ou ativar algum recurso experimental.
    """

    def __init__(self, title, description="", checked=False, parent=None):
        self.checkbox = SettingsToggleSwitch()
        self.checkbox.setChecked(checked)
        super().__init__(title, description, self.checkbox, parent)


class SettingsComboBox(ComboBox):
    """
    ComboBox específico para telas de configurações.

    Define um objectName próprio para manter a estilização visual consistente
    com os demais componentes de configuração.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsComboBox")


class SettingsSelectRow(_BaseRow):
    """
    Linha de configuração com lista suspensa.

    Indicada para configurações que exigem a escolha de uma opção entre várias,
    como idioma, tema, modo de execução ou perfil de desempenho.
    """

    def __init__(self, title, description="", items=None, parent=None):
        self.combo = SettingsComboBox()

        if items:
            self.combo.addItems(items)

        super().__init__(title, description, self.combo, parent)


class SettingsPathRow(_BaseRow):
    """
    Linha de configuração para caminhos de arquivos ou diretórios.

    Combina um campo de texto expansível com um botão de navegação,
    normalmente usado para abrir um QFileDialog.
    """

    def __init__(
        self,
        title,
        description="",
        path="",
        button_text="Browse…",
        parent=None,
    ):
        box = QWidget()
        box.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QHBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line_edit = LineEdit(path)
        self.line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.button = Button(button_text)

        layout.addWidget(self.line_edit, 1)
        layout.addWidget(self.button)

        super().__init__(
            title,
            description,
            box,
            parent,
            control_stretch=1,
        )


class SettingsActionRow(_BaseRow):
    """
    Linha de configuração com botão de ação.

    Indicada para comandos diretos, como abrir logs, limpar cache,
    restaurar configurações ou testar uma funcionalidade.
    """

    def __init__(self, title, description="", button_text="Open", parent=None):
        self.button = Button(button_text)
        super().__init__(title, description, self.button, parent)


class SettingsTextRow(_BaseRow):
    """
    Linha de configuração com campo de texto simples.

    Indicada para valores textuais editáveis, como nome, URL,
    comando customizado ou outro valor livre.
    """

    def __init__(self, title, description="", text="", parent=None):
        self.line_edit = LineEdit(text)
        super().__init__(title, description, self.line_edit, parent)


class SettingsPasswordRow(SettingsTextRow):
    """
    Linha de configuração com campo de senha.

    Reutiliza SettingsTextRow, mas configura o LineEdit para ocultar
    o conteúdo digitado usando EchoMode.Password.
    """

    def __init__(self, title, description="", text="", parent=None):
        super().__init__(title, description, text, parent)
        self.line_edit.setEchoMode(LineEdit.EchoMode.Password)