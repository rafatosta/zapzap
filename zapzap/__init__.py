__version__ = '2.2'
__appname__ = 'ZapZap'
__comment__ = 'Whatsapp Desktop for linux'
__domain__ = 'com.rtosta'
__desktopid__ = 'com.rtosta.zapzap'
__appid__ = 'zapzap-F3FF80BA-BA05-4277-8063-82A6DB9245A2'

__author__ = 'Rafael Tosta'
__email__ = 'rafa.ecomp@gmail.com'
__website__ = 'https://github.com/rafatosta/zapzap'
__bugreport__ = 'https://github.com/rafatosta/zapzap/issues'

__whatsapp_url__ = 'https://web.whatsapp.com/'
# Link para pegar o userAgent: http://httpbin.org/user-agent
__user_agent__ = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"


# iniciando os paths
from PyQt6.QtCore import QFileInfo
abs_path = QFileInfo(__file__).absolutePath()

# Temas
theme_light_path = abs_path+'/assets/stylesheets/light/stylesheet.qss'
theme_dark_path = abs_path+'/assets/stylesheets/dark/stylesheet.qss'

# Tray
tray_path = abs_path+'/assets/icons/tray/tray.svg'
tray_notify_path = abs_path+'/assets/icons/tray/tray_notify.svg'
