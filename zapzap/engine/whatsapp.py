from PyQt6.QtCore import QEvent, Qt, QUrl, QSettings
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QApplication
from zapzap import __whatsapp_url__, __appname__
from zapzap.services.dbus_theme import getSystemTheme


class WhatsApp(QWebEnginePage):

    link_url = ''
    link_context = ''
    light_theme = "document.body.classList.remove('dark');"
    dark_theme = "document.body.classList.add('dark');"

    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)

        self.qset = QSettings(__appname__, __appname__)

        # Ativa o EventFilter
        QApplication.instance().installEventFilter(self)

        # Acionar a resposta de permissão do recurso.
        self.featurePermissionRequested.connect(self.permission)

        # Este sinal é emitido quando o mouse passa sobre um link
        self.linkHovered.connect(self.link_hovered)

        self.loadFinished.connect(self.load_finished)

        # self.setAudioMuted(True)
        # self.setAudioMuted(self.qset.value('notification/show_sound', False, bool))

    def load_finished(self, flag):
        # Ativa a tela cheia para telas de proporção grande no WhatsApp Web.
        if flag:
            maximize = """
                const checkExist = setInterval(() => {
                    const classElement = document.getElementsByClassName("two _aigs")[0];
                    INSERT_THEME
                    if (classElement != null) {
                        classElement.style = 'max-width: initial; width: 100%; height: 100%; position: unset;margin: 0';
                        clearInterval(checkExist);
                    }
                    
                }, 100);
            """
            # Verifica o tema e aplica no carregamento
            settings = QSettings(__appname__, __appname__, self)
            theme_mode = settings.value("system/theme", 'auto', str)
            if theme_mode == 'auto':
                theme_mode = getSystemTheme()

            if theme_mode == 'dark':
                self.runJavaScript(maximize.replace(
                    "INSERT_THEME", self.dark_theme))
            else:
                self.runJavaScript(maximize.replace(
                    "INSERT_THEME", self.light_theme))

            # Permissão automática para notificações
            self.setFeaturePermission(self.url(), QWebEnginePage.Feature.Notifications,
                                      QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    def setTheme(self, theme='light'):
        """Defines the page theme:
            - light
            - dark """
        if theme == 'light':  # light
            self.runJavaScript(self.light_theme)
        else:  # dark
            self.runJavaScript(self.dark_theme)

    def link_hovered(self, url):
        # url contém o URL de destino do link. Ao mover o mouse para fora da url o seu valor é definido como uma string vazia
        self.link_url = url

        # Keep the last link visited to be used by the context menu
        if self.link_url != "":
            self.link_context = url

    def permission(self, frame, feature):
        self.setFeaturePermission(
            frame, feature,  QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    # Abrindo links no navegador padrão do usuário
    # Solução alternativa ao acceptNavigationRequest, pois não funcionou dentro do whatsapp.
    # Mapeia os eventos do Mouse e abre o link a partir do capturado do signal linkHovered.
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.link_url != '' and self.link_url != __whatsapp_url__ and not 'faq.whatsapp.com/web/download-and-installation/how-to-log-in-or-out' in self.link_url:
                    QDesktopServices.openUrl(QUrl(self.link_url))
                    return True
            self.link_url = ''
        return False

    def closeConversation(self):
        script = """document.dispatchEvent(new KeyboardEvent("keydown",{'key': 'Escape'}));"""
        self.runJavaScript(script)

    def newConversation(self):
        script = """function triggerCtrlAltN() {
                        var event = new KeyboardEvent('keydown', {
                            key: 'n',
                            code: 'KeyN',
                            ctrlKey: true,
                            altKey: true,
                            shiftKey: false,
                            metaKey: false,
                            bubbles: true,
                            cancelable: true
                        });
                    document.dispatchEvent(event);
                    }
                triggerCtrlAltN();
                """
        self.runJavaScript(script)

    def openPerfil(self):
        script = """function triggerCtrlAltP() {
                        var event = new KeyboardEvent('keydown', {
                            key: 'p',
                            code: 'KeyN',
                            ctrlKey: true,
                            altKey: true,
                            shiftKey: false,
                            metaKey: false,
                            bubbles: true,
                            cancelable: true
                        });
                    document.dispatchEvent(event);
                    }
                triggerCtrlAltP();
                """
        self.runJavaScript(script)
    
    def openWhatsappSettings(self):
        script = """function triggerCtrlAltP() {
                        var event = new KeyboardEvent('keydown', {
                            key: ',',
                            code: 'KeyN',
                            ctrlKey: true,
                            altKey: true,
                            shiftKey: false,
                            metaKey: false,
                            bubbles: true,
                            cancelable: true
                        });
                    document.dispatchEvent(event);
                    }
                triggerCtrlAltP();
                """
        self.runJavaScript(script)

    def openChat(self, url):
        script = """(function(){var a = document.createElement("a");a.href=\"""" + \
            url + \
            """\";document.body.appendChild(a);a.click();a.remove(); return;})();"""

        self.runJavaScript(script)
