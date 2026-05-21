from pathlib import Path

from PyQt6.QtCore import QObject, QStandardPaths, QUrl, pyqtProperty
from PyQt6.QtQml import QQmlApplicationEngine

from zapzap import __user_agent__, __whatsapp_url__, __appname__
from zapzap.services.ThemeManager import ThemeManager


class QmlWebEngineConfig(QObject):
    """Expõe configuração do WebEngine para o QML."""

    def __init__(self, parent=None):
        super().__init__(parent)
        base_data_dir = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            )
        ) / __appname__

        profile_dir = base_data_dir / "qml-profile"
        profile_dir.mkdir(parents=True, exist_ok=True)

        self._persistent_storage_path = str(profile_dir / "storage")
        self._cache_path = str(profile_dir / "cache")

        Path(self._persistent_storage_path).mkdir(parents=True, exist_ok=True)
        Path(self._cache_path).mkdir(parents=True, exist_ok=True)

    @pyqtProperty(str, constant=True)
    def whatsappUrl(self):
        return __whatsapp_url__

    @pyqtProperty(str, constant=True)
    def userAgent(self):
        return __user_agent__

    @pyqtProperty(str, constant=True)
    def persistentStoragePath(self):
        return self._persistent_storage_path

    @pyqtProperty(str, constant=True)
    def cachePath(self):
        return self._cache_path


class QmlMainWindow(QObject):
    """Janela principal em QML com WebEngine e perfil persistente."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._engine = QQmlApplicationEngine()
        self._webengine_config = QmlWebEngineConfig(self)
        self._engine.rootContext().setContextProperty(
            "webEngineConfig", self._webengine_config
        )

        qml_path = Path(__file__).resolve().parents[1] / "qml" / "MainWindow.qml"
        self._engine.load(QUrl.fromLocalFile(str(qml_path)))

        if not self._engine.rootObjects():
            raise RuntimeError("Falha ao carregar a interface QML principal.")

        self._window = self._engine.rootObjects()[0]

        self._webview = self._window.findChild(QObject, "zapzapWebView")
        if self._webview:
            self._webview.loadFinished.connect(
                lambda _ok: self.apply_theme(ThemeManager.get_current_theme())
            )

    def load_settings(self):
        return

    def show(self):
        self._window.show()

    def hide(self):
        self._window.hide()

    def close(self):
        self._window.close()


    def apply_theme(self, theme):
        if not self._webview:
            return

        theme_value = theme.value if hasattr(theme, "value") else str(theme)
        force_dark = theme_value == ThemeManager.Type.Dark.value

        script = f"""
            (function() {{
                var isDark = {str(force_dark).lower()};
                document.documentElement.style.colorScheme = isDark ? 'dark' : 'light';
                document.documentElement.classList.toggle('dark', isDark);
                document.body && document.body.classList.toggle('dark', isDark);
            }})();
        """
        self._webview.runJavaScript(script)

    def xdgOpenChat(self, url: str):
        webview = self._window.findChild(QObject, "zapzapWebView")
        if not webview:
            return

        script = (
            "(function(){var a = document.createElement('a');"
            f"a.href={url!r};"
            "document.body.appendChild(a);a.click();a.remove();})();"
        )
        webview.runJavaScript(script)
