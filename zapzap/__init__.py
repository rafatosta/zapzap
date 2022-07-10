from PyQt6.QtGui import QIcon

__version__ = '2.9'
__appname__ = 'ZapZap'
__comment__ = 'Whatsapp Desktop for linux'
__domain__ = 'com.rtosta'
__desktopid__ = 'com.rtosta.zapzap'
__appid__ = 'zapzap-F3FF80BA-BA05-4277-8063-82A6DB9245A2'

__author__ = 'Rafael Tosta'
__email__ = 'rafa.ecomp@gmail.com'
__website__ = 'https://github.com/rafatosta/zapzap'
__bugreport__ = 'https://github.com/rafatosta/zapzap/issues'
__releases__ = 'https://github.com/rafatosta/zapzap/releases'
__paypal__ = 'https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD'
__pix__ = 'https://nubank.com.br/pagar/3c3r2/jAK5S45kuO'
__licence__ = 'GNU General Public License v3.0'

__whatsapp_url__ = 'https://web.whatsapp.com/'
# Link para pegar o userAgent: http://httpbin.org/user-agent
__user_agent__ = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39"

# iniciando os paths
from PyQt6.QtCore import QFileInfo
abs_path = QFileInfo(__file__).absolutePath()

# Tray
def getIconTray(theme = 'default', mode='normal'):
    return QIcon(abs_path+f'/assets/icons/tray/{theme}_{mode}.svg')

# Segoe Font
segoe_font = {
    "regular": abs_path + '/assets/segoe-ui/Segoe UI.ttf',
    "bold": abs_path + '/assets/segoe-ui/Segoe UI Bold.ttf',
    "bold-italic": abs_path + '/assets/segoe-ui/Segoe UI Bold Italic.ttf',
    "italic": abs_path + '/assets/segoe-ui/Segoe UI Italic.ttf',
}
