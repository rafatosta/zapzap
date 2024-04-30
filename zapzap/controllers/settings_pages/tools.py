from gettext import gettext as _

def updateTextCheckBox(checkBox):
        if checkBox.isChecked():
            checkBox.setText(_("On"))
        else:
            checkBox.setText(_("Off"))