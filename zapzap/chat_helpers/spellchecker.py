import os
import urllib.request
from PyQt6.QtCore import QThreadPool, QLocale, QProcess
import zapzap
from zapzap.chat_helpers.worker import Worker

database = 'https://cgit.freedesktop.org/libreoffice/dictionaries/tree/'
kDictExtensions = [".dic", ".aff"]

""" language_country : folder in database 
    Os arquivos serão baixados na forma: database/folder/language_country.kDictExtensions[0:1]
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


def UpdateLanguages(profile):
    if DictionaryFileExist():  # o arquivo existe?
        setSpellCheck(profile)
    elif SuportDictionaryExists():  # a linguagem é suportada?
        DownloadDictionary(profile)


def DownloadDictionary(profile):
    threadpool = QThreadPool()
    worker = Worker(DownloadDictionaryInBackground)
    worker.signals.finished.connect(lambda p=profile: setSpellCheck(p))
    worker.signals.error.connect(lambda erro: print(f'deu merda: {erro}'))
    threadpool.start(worker)


def setSpellCheck(profile):
    profile.setSpellCheckLanguages((QLocale.system().name(),))


def DownloadDictionaryInBackground():
    LC = QLocale.system().name()
    # Download
    for file in kDictExtensions:
        down_url = f'{database}{kDictionaries[LC]}/{LC}{file}'
        print(down_url)
        save_loc = os.path.join(zapzap.path_dictionaries, f'{LC}{file}')
        print(save_loc)
        # Dowloading using urllib
        urllib.request.urlretrieve(down_url, save_loc, Handle_Progress)
    # Convert
    dic = os.path.join(
        zapzap.path_dictionaries, f'{LC}.dic')
    bdic = os.path.join(zapzap.path_dictionaries, f'{LC}.bdic')
    os.system(f'qwebengine_convert_dict {dic} {bdic}')
    print("Acabou!")


def Handle_Progress(blocknum, blocksize, totalsize):
    #print(blocknum, blocksize, totalsize)
    readed_data = blocknum * blocksize
    print(readed_data/1000000)
