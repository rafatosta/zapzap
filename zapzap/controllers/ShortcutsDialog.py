from PyQt6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem

from zapzap.views.ui_shortcuts_dialog import Ui_ShortcutsDialog


class ShortcutsDialog(QDialog, Ui_ShortcutsDialog):

    # Adicionando os atalhos à tabela
    shortcuts = [
        ("Marcar como não lida", "Ctrl + Alt + Shift + U"),
        ("Arquivar conversa", "Ctrl + Alt + Shift + E"),
        ("Fixar conversa", "Ctrl + Alt + Shift + P"),
        ("Pesquisar na conversa", "Ctrl + Alt + Shift + F"),
        ("Próxima conversa", "Ctrl + Alt + Tab"),
        ("Fechar conversa", "Escape"),
        ("Perfil e recado", "Ctrl + Alt + P"),
        ("Diminuir a velocidade da mensagem de voz selecionada", "Shift + ,"),
        ("Painel de emojis", "Ctrl + Alt + E"),
        ("Painel de figurinhas", "Ctrl + Alt + S"),
        ("Bloquear o app", "Ctrl + Alt + L"),
        ("Silenciar", "Ctrl + Alt + Shift + M"),
        ("Apagar conversa", "Ctrl + Alt + Backspace"),
        ("Pesquisar", "Ctrl + Alt + /"),
        ("Nova conversa", "Ctrl + Alt + N"),
        ("Conversa anterior", "Ctrl + Alt + Shift + Tab"),
        ("Novo grupo", "Ctrl + Alt + Shift + N"),
        ("Aumentar a velocidade da mensagem de voz selecionada", "Shift + ."),
        ("Configurações", "Ctrl + Alt + ,"),
        ("Painel de GIFs", "Ctrl + Alt + G"),
        ("Pesquisa estendida", "Alt + K"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Ação", "Atalho"])

        self.tableWidget.setRowCount(len(self.shortcuts))
        for row, (action, shortcut) in enumerate(self.shortcuts):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(action))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(shortcut))

        self.tableWidget.resizeColumnsToContents()

        self.tableWidget.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
