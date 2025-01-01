from PyQt6.QtWidgets import QMessageBox

from zapzap import LIMITE_USERS

class AlertManager:
    @staticmethod
    def information(parent, title: str, message: str):
        QMessageBox.information(parent, title, message)
    
    @staticmethod
    def warning(parent, title: str, message: str):
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def critical(parent, title: str, message: str):
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def question(parent, title: str, message: str) -> bool:
        response = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return response == QMessageBox.StandardButton.Yes

    @staticmethod
    def limit_users(parent):
        QMessageBox.information(
                parent, "Informação", f"Limite de {
                    LIMITE_USERS} usuários atingido. Não é possível criar mais usuários.")