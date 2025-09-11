from PyQt6.QtCore import QFileInfo
__version__ = '6.2.1'
__appname__ = 'ZapZap'
__comment__ = 'WhatsApp Messenger for linux'
__domain__ = 'com.rtosta'
__desktopid__ = 'com.rtosta.zapzap'
__appid__ = 'zapzap-application'

__author__ = 'Rafael Tosta'
__email__ = 'rafa.ecomp@gmail.com'
__website__ = 'https://rtosta.com/zapzap/'
__bugreport__ = 'https://github.com/rafatosta/zapzap/issues'
__releases__ = 'https://github.com/rafatosta/zapzap/releases'
__paypal__ = 'https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD'
__pix__ = 'https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv'
__kofi__ = 'https://ko-fi.com/rafaeltosta'
__githubSponor__ = 'https://github.com/sponsors/rafatosta'
__licence__ = 'GNU General Public License v3.0'

__donationPage__ = 'https://rtosta.com/zapzap/#donate'

__whatsapp_url__ = 'https://web.whatsapp.com/'
# Link para pegar o userAgent: http://httpbin.org/user-agent
__user_agent__ = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

LIMITE_USERS = 3

APP_PATH = QFileInfo(__file__).absolutePath()
