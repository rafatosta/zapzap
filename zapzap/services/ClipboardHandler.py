import base64
from PyQt6.QtGui import QImage, QPixmap, QGuiApplication
from PyQt6.QtCore import QMimeData, QUrl, QByteArray


class ClipboardHandler:
    """Classe para gerenciar a área de transferência sem modificar a global"""

    def __init__(self):
        self.clipboard = QGuiApplication.clipboard()
        self.local_clipboard = None  # Armazena o conteúdo localmente
        self.last_mime_type = ""  # Guarda o último tipo de dado copiado

        # Conectar o evento de mudança do clipboard
        self.clipboard.dataChanged.connect(self.on_clipboard_change)

        print("Monitorando a área de transferência...")

    def on_clipboard_change(self):
        """Captura qualquer novo conteúdo copiado e armazena localmente"""
        mime_data = self.clipboard.mimeData()

        if mime_data.hasText():
            new_data = mime_data.text()
            mime_type = "text/plain"

            # Verificar se o texto contém uma imagem base64
            if new_data.startswith("data:image"):
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
            pixmap = QPixmap.fromImage(self.local_clipboard).scaled(100, 100)
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
        return image.scaled(200, 200)  # Exemplo de redimensionamento da imagem

    def paste_modified(self):
        """Exemplo de modificação antes de colar"""
        if self.local_clipboard:
            modified_content = None
            if isinstance(self.local_clipboard, str):
                modified_content = self.modify_text(self.local_clipboard)

            elif isinstance(self.local_clipboard, list):
                modified_content = self.modify_urls(self.local_clipboard)

            elif isinstance(self.local_clipboard, QImage):
                modified_content = self.modify_image(self.local_clipboard)

            if modified_content:
                # Atualiza o clipboard com o conteúdo modificado
                self.set_clipboard_data(modified_content)

    def set_clipboard_data(self, modified_content):
        """Configura o conteúdo modificado na área de transferência"""
        new_mime = QMimeData()

        # Dependendo do tipo de conteúdo, o novo MIME é configurado
        if isinstance(modified_content, str):
            new_mime.setText(modified_content)
            self.copy_local_image(modified_content) 
            return
        elif isinstance(modified_content, list):
            urls = [QUrl(url) for url in modified_content]
            new_mime.setUrls(urls)
        elif isinstance(modified_content, QImage):
            # A função setImageData espera um QImage diretamente
            new_mime.setImageData(modified_content)

        # Aplica o novo MIME ao clipboard
        self.clipboard.setMimeData(new_mime)

        

    def copy_local_image(self, file_path):
        """Copia uma imagem local para o clipboard"""
        image = QImage(file_path)
        if image.isNull():
            print("Falha ao carregar a imagem.")
            return
        
        # Adiciona a imagem ao clipboard como QMimeData
        new_mime = QMimeData()
        new_mime.setImageData(image)
        self.clipboard.setMimeData(new_mime)
