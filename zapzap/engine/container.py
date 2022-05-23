from zapzap.engine.browser import Browser


class Container():
    """Classe Container
        A ideia é definir para cada usuário seu próprio conjunto de configurações e
        gerencia-los.
            Mantém os dados sobre:
                + NameSpace para o WebEngine;
                + Nome do arquivo de configuração

    """

    def __init__(self, nameSpace='storage-whats', name='default'):
        self.nameSpace = nameSpace
        self.name = name

        #self.createWebEngine()

    def createWebEngine(self):
        """Cria o objeto Browser com as configurações definidas"""
        self.browser = Browser(self.nameSpace)
        # self.browser.setZoomFactor(self.settings.value(
        #    "browser/zoomFactor", 1.0, float))
        self.browser.doReload()

    def remove(self):
        """Remove todas as informações persistente do container
            + Arquivo de configuração
            + Pasta do Webengine
        """
        pass
