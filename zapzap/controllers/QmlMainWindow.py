from pathlib import Path

from PyQt6.QtCore import QObject, QUrl
from PyQt6.QtQml import QQmlApplicationEngine


class QmlMainWindow(QObject):
    """Janela principal em QML (migração incremental)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._engine = QQmlApplicationEngine()
        qml_path = Path(__file__).resolve().parents[1] / "qml" / "MainWindow.qml"
        self._engine.load(QUrl.fromLocalFile(str(qml_path)))

        if not self._engine.rootObjects():
            raise RuntimeError("Falha ao carregar a interface QML principal.")

        self._window = self._engine.rootObjects()[0]

    def load_settings(self):
        """Hook para manter compatibilidade com o fluxo atual de inicialização."""
        return

    def show(self):
        self._window.show()

    def hide(self):
        self._window.hide()

    def close(self):
        self._window.close()
