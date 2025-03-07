import os
from PyQt6.QtGui import QImage, QPixmap, QGuiApplication
from PyQt6.QtCore import QMimeData, QUrl, QByteArray

from PyQt6.QtCore import QUrl, QEventLoop
from PyQt6.QtGui import QImage
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QSslConfiguration, QSslSocket


class ClipboardHandler:
    """Classe para gerenciar a área de transferência sem modificar a global"""

    def __init__(self):
        self.clipboard = QGuiApplication.clipboard()
        self.local_clipboard = None  # Armazena o conteúdo localmente
        self.last_mime_type = ""  # Guarda o último tipo de dado copiado

        # Conectar o evento de mudança do clipboard
        self.clipboard.dataChanged.connect(self.on_clipboard_change)

        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.handle_image_reply)
        self._image_data = None

        # Desabilitar a verificação SSL
        ssl_config = QSslConfiguration.defaultConfiguration()
        ssl_config.setPeerVerifyMode(QSslSocket.PeerVerifyMode.VerifyNone)
        QSslConfiguration.setDefaultConfiguration(ssl_config)

        print("Monitorando a área de transferência...")

    def on_clipboard_change(self):
        """Captura qualquer novo conteúdo copiado e armazena localmente"""
        mime_data = self.clipboard.mimeData()

        if mime_data.hasText():
            new_data = mime_data.text()
            mime_type = "text/plain"

            # Verificar se o texto contém um caminho de imagem
            if self.is_image_path(new_data):
                new_data = self.load_image_from_path(new_data)
                mime_type = "image/png"
            elif new_data.startswith("data:image"):
                new_data = self.decode_base64_image(new_data)
                mime_type = "image/png"

        elif mime_data.hasImage():
            new_data = self.clipboard.image()
            mime_type = "image/png"

        elif mime_data.hasUrls():
            urls = mime_data.urls()
            new_data = [url.toString() for url in urls]
            mime_type = "text/uri-list"

        else:
            return  # Tipo de dado não suportado

        # Se o conteúdo mudou, armazena no clipboard local
        if mime_type != self.last_mime_type or new_data != self.local_clipboard:
            self.local_clipboard = new_data
            self.last_mime_type = mime_type
            self.on_clipboard_updated()

    def is_image_path(self, path):
        """Verifica se o caminho é de uma imagem com base na extensão"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        _, ext = os.path.splitext(path)
        return ext.lower() in image_extensions

    def load_image_from_path(self, path):
        """Carrega uma imagem de um caminho de arquivo"""
        image = QImage(path)
        if image.isNull():
            print(f"Falha ao carregar a imagem de: {path}")

            print('Realizando request url')
            image = self.load_image_from_url(path)

            if image:
                print("Imagem carregada com sucesso!")
                return image

            return None
        return image

    def load_image_from_url(self, url):
        loop = QEventLoop()

        request = QNetworkRequest(QUrl(url))
        reply = self.manager.get(request)

        # Esperar a resposta
        reply.finished.connect(loop.quit)
        loop.exec()

        return self._image_data


    def handle_image_reply(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            image_data = reply.readAll()
            image = QImage()
            if image.loadFromData(image_data):
                print("handle_image_reply: Imagem carregada com sucesso")
                self._image_data = image
            else:
                print("Erro ao converter os dados em QImage")
                self._image_data = None
        else:
            print(f"Erro ao baixar a imagem: {reply.errorString()}")

        reply.deleteLater()

    def decode_base64_image(self, base64_data):
        """Decodifica uma string base64 para um QImage"""
        # Remover a parte 'data:image/jpeg;base64,' ou similar
        base64_data = base64_data.split(',')[1]
        img_data = QByteArray.fromBase64(base64_data.encode())

        # Criar o QImage a partir dos dados decodificados
        image = QImage()
        image.loadFromData(img_data)
        return image

    def on_clipboard_updated(self):
        """Atualiza a interface gráfica com o novo conteúdo armazenado"""
        if isinstance(self.local_clipboard, str):
            print(f"Texto: {self.local_clipboard}")
            modified_text = self.modify_text(self.local_clipboard)
            self.set_clipboard_data(modified_text)

        elif isinstance(self.local_clipboard, list):
            print(f"URLs: {', '.join(self.local_clipboard)}")
            modified_urls = self.modify_urls(self.local_clipboard)
            self.set_clipboard_data(modified_urls)

        elif isinstance(self.local_clipboard, QImage):
            pixmap = QPixmap.fromImage(self.local_clipboard)
            print(f"Imagem: {pixmap}")
            modified_image = self.modify_image(self.local_clipboard)
            self.set_clipboard_data(modified_image)          

    def get_local_clipboard(self):
        """Retorna o conteúdo armazenado localmente"""
        return self.local_clipboard

    def modify_text(self, text):
        """Modifica o texto antes de colar (exemplo: converte para maiúsculas)"""
        return text  # Aqui você pode adicionar outras modificações no texto

    def modify_urls(self, urls):
        """Modifica as URLs antes de colar (exemplo: adicionar um prefixo)"""
        return [f"https://modified-url.com/{url}" for url in urls]  # Exemplo de modificação

    def modify_image(self, image):
        """Modifica a imagem antes de colar (exemplo: redimensiona)"""
        return image  # Exemplo de redimensionamento da imagem

    def set_clipboard_data(self, modified_content):
        """Configura o conteúdo modificado na área de transferência"""
        new_mime = QMimeData()

        # Dependendo do tipo de conteúdo, o novo MIME é configurado
        if isinstance(modified_content, str):
            new_mime.setText(modified_content)
        elif isinstance(modified_content, list):
            urls = [QUrl(url) for url in modified_content]
            new_mime.setUrls(urls)
        elif isinstance(modified_content, QImage):
            # A função setImageData espera um QImage diretamente
            new_mime.setImageData(modified_content)

        # Aplica o novo MIME ao clipboard
        self.clipboard.setMimeData(new_mime)
