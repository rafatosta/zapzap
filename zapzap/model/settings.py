from PyQt6.QtCore import QStandardPaths
from zapzap import __appname__

from os.path import expanduser, isdir
from os import makedirs, remove
from json import dump, load

path_settings = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.ConfigLocation)

j_folder = expanduser(path_settings+'/' + __appname__)
j_file = j_folder + '/settings.json'

default_js = {
    "start_system": False,
    "start_hide": False,
    "night_mode": False,
    "notify_desktop": True,
    "show_photo": True,
    "show_name": True,
    "show_msg": True
}

settings_js = None


def checkSettings():
    try:
        with open(j_file):
            pass
    except Exception as msg:
        print('>>>>>> ', msg)
        if not isdir(j_folder):
            makedirs(j_folder)
        with open(j_file, 'w') as jfile:
            dump(default_js, jfile, indent=2)


def get_setting(op):
    if settings_js == None:
        get_json()
    return settings_js[op]


def get_json():
    global settings_js
    with open(j_file) as jf:
        settings_js = load(jf)


def write_json(op, val):
    with open(j_file, 'r') as jf:
        objJson = load(jf)
        objJson[op] = val

    # Replace original file
    remove(j_file)
    with open(j_file, 'w') as jf:
        dump(objJson, jf, indent=2)
