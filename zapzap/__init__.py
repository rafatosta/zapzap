import os
from PyQt6.QtCore import QStandardPaths
__version__ = '5.3'
__appname__ = 'ZapZap'
__comment__ = 'WhatsApp Messenger for linux'
__domain__ = 'com.rtosta'
__desktopid__ = 'com.rtosta.zapzap'
__appid__ = 'zapzap-application'

__author__ = 'Rafael Tosta'
__email__ = 'rafa.ecomp@gmail.com'
__website__ = 'https://zapzap-linux.github.io/'
__bugreport__ = 'https://github.com/zapzap-linux/zapzap/issues'
__releases__ = 'https://github.com/zapzap-linux/zapzap/releases'
__paypal__ = 'https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD'
__pix__ = 'https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv'
__kofi__ = 'https://ko-fi.com/rafaeltosta'
__githubSponor__ = 'https://github.com/sponsors/rafatosta'
__licence__ = 'GNU General Public License v3.0'

__ddiHelper__ = 'https://www.ddi-ddd.com.br/Codigos-Telefone-Internacional/'

__whatsapp_url__ = 'https://web.whatsapp.com/'
# Link para pegar o userAgent: http://httpbin.org/user-agent
__user_agent__ = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

# iniciando os paths
from PyQt6.QtCore import QFileInfo
abs_path = QFileInfo(__file__).absolutePath()

fonts_path = abs_path + '/assets/fonts'

# Segoe Font
segoe_font = {
    "regular": fonts_path + '/segoe-ui/Segoe UI.ttf',
    "bold": fonts_path + '/segoe-ui/Segoe UI Bold.ttf',
    "bold-italic": fonts_path + '/segoe-ui/Segoe UI Bold Italic.ttf',
    "italic": fonts_path + '/segoe-ui/Segoe UI Italic.ttf',
}

# Path /tmp
# tmp directory for user photos used in notifications

path_tmp = os.path.join(
    QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation), __appname__, 'tmp'
)
if not os.path.exists(path_tmp):
    os.makedirs(path_tmp)

# Path translations
po_path = os.path.join(abs_path, 'po')

# Is Flatpak?
isFlatpak = abs_path.startswith('/app/')

# Path DataBase
DATABASE_DIR = os.path.join(
    QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation), __appname__, 'db'
)

if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

DATABASE_FILE = os.path.join(DATABASE_DIR, 'zapzap.db')

# Path
path_storage = os.path.join(
    QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation), __appname__, "QtWebEngine"
)

COUNT_DONATE_MAX = 15