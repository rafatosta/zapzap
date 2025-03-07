from PyQt6.QtGui import QImage, QGuiApplication, QPixmap


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

    def on_clipboard_updated(self):
        """Atualiza a interface gráfica com o novo conteúdo armazenado"""
        self.local_clipboard = self.get_local_clipboard()

        if isinstance(self.local_clipboard, str):
            print(f"Texto: {self.local_clipboard}")

        elif isinstance(self.local_clipboard, list):
            print(f"URLs: {', '.join(self.local_clipboard)}")

        elif isinstance(self.local_clipboard, QImage):
            pixmap = QPixmap.fromImage(self.local_clipboard).scaled(100, 100)
            print(pixmap)

    def get_local_clipboard(self):
        """Retorna o conteúdo armazenado localmente"""
        return self.local_clipboard

    def paste_modified(self):
        """Exemplo de modificação antes de colar"""
        if self.local_clipboard:
            if isinstance(self.local_clipboard, str):
                return self.local_clipboard.upper()  # Converte texto para maiúsculas

            elif isinstance(self.local_clipboard, list):
                return self.local_clipboard  # URLs sem alteração

            elif isinstance(self.local_clipboard, QImage):
                return self.local_clipboard  # Pode ser editada antes de colar

        return None
