import os
import urllib.request
from PyQt6.QtCore import QLocale
import zapzap

DATABASE = 'https://cgit.freedesktop.org/libreoffice/dictionaries/plain/'
kDictExtensions = [".dic", ".aff"]

""" 
    Note: Look at the language folder from the link in DATABASE

    Definition:
    'language_country' : 'folder'

"""
kDictionaries = {
    'en_US': 'en',
    'pt_BR': 'pt_BR',
}


def DictionaryFileExist():
    file = os.path.join(zapzap.path_dictionaries,
                        f'{QLocale.system().name()}.bdic')
    return os.path.isfile(file)


def SuportDictionaryExists():
    try:
        kDictionaries[QLocale.system().name()]
    except:
        return False
    else:
        return True

def DownloadDictionaryInBackground():
    LC = QLocale.system().name()
    # Download
    for file in kDictExtensions:
        down_url = f'{DATABASE}{kDictionaries[LC]}/{LC}{file}'
        save_loc = os.path.join(zapzap.path_dictionaries, f'{LC}{file}')
        # Dowloading using urllib
        urllib.request.urlretrieve(down_url, save_loc)
    # Convert
    dic = os.path.join(
        zapzap.path_dictionaries, f'{LC}.dic')
    bdic = os.path.join(zapzap.path_dictionaries, f'{LC}.bdic')
    os.system(f'qwebengine_convert_dict {dic} {bdic}')

