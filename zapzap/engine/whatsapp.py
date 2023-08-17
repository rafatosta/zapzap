from PyQt6.QtCore import QEvent, Qt, QUrl, QSettings
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QApplication
from zapzap import __whatsapp_url__, __appname__
from zapzap.services.dbus_theme import getSystemTheme


class WhatsApp(QWebEnginePage):

    link_url = ''
    light_theme = "document.body.classList.remove('dark');"
    dark_theme = "document.body.classList.add('dark');"

    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)
        # Ativa o EventFilter
        QApplication.instance().installEventFilter(self)

        # Acionar a resposta de permissão do recurso.
        self.featurePermissionRequested.connect(self.permission)

        # Este sinal é emitido quando o mouse passa sobre um link
        self.linkHovered.connect(self.link_hovered)

        self.loadFinished.connect(self.load_finished)

    def load_finished(self, flag):
        # Ativa a tela cheia para telas de proporção grande no WhatsApp Web.
        if flag:
            maximize = """
                const checkExist = setInterval(() => {
                    const classElement = document.getElementsByClassName("_1jJ70 two")[0];
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
        script = """var closeConvoClassName = "Iaqxu FCS6Q jScby";
                    function isConversationOpen() {
                        return document.getElementsByClassName("n5hs2j7m oq31bsqd gx1rr48f qh5tioqs").length > 0 //conversation class
                            && document.getElementsByClassName("lhggkp7q mvj9yovn f804f6gw fyy3ld6e svlsagor dntxsmpk ixn6u0rb s2vc4xk1 o0wkt7aw t1844p82 esbo3we0 qizq0yyl bs7a17vp eg0stril").length == 0 //close emoji
                            && document.getElementsByClassName("_2cNrC _1CTfw").length == 0 //attachment popup
                            && document.getElementsByClassName("o--vV wGJyi").length == 0 //more options menu
                            && document.getElementsByClassName("_23JDg _3x1a0").length == 0; //media view
                    }
                    function hideOptions() {
                        document.getElementsByClassName("o--vV wGJyi")[0].style.display = "none";
                    }
                    function getMoreOptions() {
                        if (document.getElementsByClassName("_3ndVb").length == 7){
                            return document.getElementsByClassName("_3ndVb")[5];
                        }
                        return document.getElementsByClassName("_3ndVb")[6];
                    }
                    function invokeEscKey() {
                        window.dispatchEvent(new KeyboardEvent("keydown", {altKey: false, code: "Escape", ctrlKey: false, isComposing: false, key: "Escape", 
                                            location: 0, metaKey: false, repeat: false, shiftKey: false, which: 27, charCode: 0, keyCode: 27,})
                        );
                    }
 
                    function closeConversation() {
                        if (!isConversationOpen()) {
                            invokeEscKey();
                            return;
                        }
                        getMoreOptions().click();
                        setTimeout(function() {
                            var buttons = document.getElementsByClassName(closeConvoClassName);
                            if (buttons.length === 5) { //it's a group
                                //hideOptions();
                                invokeEscKey();
                                return;
                            }
                            var index = buttons.length === 9 ? 2 : 2;
                            buttons[index].click()
                            hideOptions();
                        }, 1);
                    }
                    closeConversation();
                    """
        self.runJavaScript(script)

    def openChat(self, url):
        script = """(function(){var a = document.createElement("a");a.href=\"""" + \
            url + \
            """\";document.body.appendChild(a);a.click();a.remove(); return;})();"""

        self.runJavaScript(script)
