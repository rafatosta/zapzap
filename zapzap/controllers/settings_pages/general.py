from PyQt6.QtWidgets import QWidget, QCheckBox
from PyQt6.QtCore import QSettings, pyqtSignal, QLocale
from zapzap.view.general_page import Ui_General
from ...services.spellCheckLanguages import SpellCheckLanguages
from zapzap.services.portal_desktop import createDesktopFile
from .tools import updateTextCheckBox
from gettext import gettext as _
import zapzap


class General(QWidget, Ui_General):

    # checkSpellChecker
    emitSetSpellChecker = pyqtSignal(str)
    emitDisableSpellChecker = pyqtSignal(bool)

    # openSWhatsapp
    emitOpenSettingsWhatsapp = pyqtSignal()

    def __init__(self):
        super(General, self).__init__()
        self.setupUi(self)
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)
        self.load()
        self.loadSpellChecker()
        self.setActionCheckBox()
        self.btnOpenSWhatsapp.clicked.connect(
            lambda: self.emitOpenSettingsWhatsapp.emit())
        
        if zapzap.isFlatpak:
            self.wayland.setVisible(False)
            self.labelWayland.setVisible(False)

    def loadSpellChecker(self):
        def action():
            currentLanguage = self.comboSpellChecker.currentData()
            self.settings.setValue(
                "system/spellCheckLanguage", currentLanguage)
            self.emitSetSpellChecker.emit(currentLanguage)

        self.comboSpellChecker.textActivated.connect(action)

        for chave, valor in SpellCheckLanguages.languages.items():
            self.comboSpellChecker.addItem(f'{_(valor)} ({chave})', chave)

        lang = self.settings.value(
            "system/spellCheckLanguage", QLocale.system().name(), str)

        try:
            sys_lang = SpellCheckLanguages.languages[lang]
        except:  # se não for um idioma suportado não fecha o app
            v = _("System Language")
            sys_lang = f'{v} (??)'
            self.comboSpellChecker.addItem(sys_lang, chave)

        index = self.comboSpellChecker.findData(lang)
        self.comboSpellChecker.setCurrentIndex(index)

    def setActionCheckBox(self):
        for children in self.general_scrollArea.findChildren(QCheckBox):
            children.clicked.connect(self.checkClick)
            updateTextCheckBox(children)

    def checkClick(self):
        children = self.sender()
        childrenName = children.objectName()

        if childrenName == 'start_system':
            # cria ou remove o arquivo
            createDesktopFile(bool(self.start_system.isChecked()))

        if childrenName == 'checkSpellChecker':
            self.comboSpellChecker.setEnabled(
                self.checkSpellChecker.isChecked())
            self.emitDisableSpellChecker.emit(
                self.checkSpellChecker.isChecked())

        updateTextCheckBox(children)
        self.save()

    def save(self):
        self.settings.setValue("system/start_system",
                               self.start_system.isChecked())
        self.settings.setValue("system/keep_background",
                               self.keepBackground.isChecked())
        self.settings.setValue("system/wayland",
                               self.wayland.isChecked())
        self.settings.setValue("system/spellCheckers",
                               self.checkSpellChecker.isChecked())

    def load(self):
        self.start_system.setChecked(self.settings.value(
            "system/start_system", False, bool))  # Start_system
        self.keepBackground.setChecked(self.settings.value(
            "system/keep_background", True, bool))  # keep_background
        self.wayland.setChecked(self.settings.value(
            "system/wayland", True, bool))  # wayland
