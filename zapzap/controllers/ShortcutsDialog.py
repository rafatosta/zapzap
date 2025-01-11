from PyQt6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem

from zapzap.views.ui_shortcuts_dialog import Ui_ShortcutsDialog


class ShortcutsDialog(QDialog, Ui_ShortcutsDialog):

    # Adicionando os atalhos à tabela
    shortcuts = [
        # Conversas
        ("Nova conversa", "Ctrl + Alt + N"),
        ("Marcar como não lida", "Ctrl + Alt + Shift + U"),
        ("Arquivar conversa", "Ctrl + Alt + Shift + E"),
        ("Fixar conversa", "Ctrl + Alt + Shift + P"),
        ("Próxima conversa", "Ctrl + Alt + Tab"),
        ("Fechar conversa", "Escape"),
        ("Pesquisar na conversa", "Ctrl + Alt + Shift + F"),
        ("Conversa anterior", "Ctrl + Alt + Shift + Tab"),
        ("Apagar conversa", "Ctrl + Alt + Backspace"),

        # Configurações e Perfis
        ("Perfil e recado", "Ctrl + Alt + P"),
        ("Configurações", "Ctrl + Alt + ,"),

        # Mensagens de Voz
        ("Diminuir a velocidade da mensagem de voz selecionada", "Shift + ,"),
        ("Aumentar a velocidade da mensagem de voz selecionada", "Shift + ."),

        # Ferramentas de Mídia
        ("Painel de emojis", "Ctrl + Alt + E"),
        ("Painel de figurinhas", "Ctrl + Alt + S"),
        ("Painel de GIFs", "Ctrl + Alt + G"),

        # Outros
        ("Bloquear o app", "Ctrl + Alt + L"),
        ("Silenciar", "Ctrl + Alt + Shift + M"),
        ("Pesquisar", "Ctrl + Alt + /"),
        ("Novo grupo", "Ctrl + Alt + Shift + N"),
        ("Pesquisa estendida", "Alt + K"),
    ]

    shortcuts_zapzap = [
        # Configurações e Navegação
        ("Configurações", "Ctrl + P"),
        ("Esconder", "Ctrl + W"),
        ("Sair", "Ctrl + Q"),

        # Visualização
        ("Tela cheia", "F11"),
        ("Reset zoom", "Ctrl + 0"),
        ("Zoom in", "Ctrl + +"),
        ("Zoom out", "Ctrl + -"),

        # Atualização
        ("Recarregar páginas", "F5"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Whatsapp Web Atalhos
        self.table_whatsapp.setColumnCount(2)

        self.table_whatsapp.setRowCount(len(self.shortcuts))
        for row, (action, shortcut) in enumerate(self.shortcuts):
            self.table_whatsapp.setItem(row, 0, QTableWidgetItem(action))
            self.table_whatsapp.setItem(row, 1, QTableWidgetItem(shortcut))

        self.table_whatsapp.resizeColumnsToContents()

        self.table_whatsapp.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.table_whatsapp.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)

        # ZapZap atalhos
        self.table_zapzap.setColumnCount(2)

        self.table_zapzap.setRowCount(len(self.shortcuts_zapzap))
        for row, (action, shortcut) in enumerate(self.shortcuts_zapzap):
            self.table_zapzap.setItem(row, 0, QTableWidgetItem(action))
            self.table_zapzap.setItem(row, 1, QTableWidgetItem(shortcut))

        self.table_zapzap.resizeColumnsToContents()

        self.table_zapzap.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.table_zapzap.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
