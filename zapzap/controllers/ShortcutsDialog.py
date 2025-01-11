from PyQt6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem
from zapzap.views.ui_shortcuts_dialog import Ui_ShortcutsDialog


class ShortcutsDialog(QDialog, Ui_ShortcutsDialog):
    # Atalhos
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

        # Adicionando atalhos na tabela
        self.add_shortcuts_to_table(self.table_whatsapp, self.shortcuts)
        self.add_shortcuts_to_table(self.table_zapzap, self.shortcuts_zapzap)

    def add_shortcuts_to_table(self, table, shortcuts):
        """Adiciona atalhos à tabela especificada."""
        table.setColumnCount(2)
        table.setRowCount(len(shortcuts))

        for row, (action, shortcut) in enumerate(shortcuts):
            table.setItem(row, 0, QTableWidgetItem(action))
            table.setItem(row, 1, QTableWidgetItem(shortcut))

        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
