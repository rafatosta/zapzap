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

    @property
    def nameSpace(self):
        return self.nameSpace

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        self.name = value

    def create(self):
        """Cria o objeto Browser com as configurações definidas"""
        pass

    def remove(self):
        """Remove todas as informações persistente do container
            + Arquivo de configuração
            + Pasta do Webengine
        """
        pass
