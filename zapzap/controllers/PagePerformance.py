from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from zapzap.services.SettingsManager import SettingsManager


class PagePerformance(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_performance.ui", self)

        self._load_settings()
        self._configure_signals()

    def _load_settings(self):
        self.in_process_gpu.setChecked(SettingsManager.get("performance/in_process_gpu", False))
        self.disable_gpu.setChecked(SettingsManager.get("performance/disable_gpu", False))
        self.single_process.setChecked(SettingsManager.get("performance/single_process", False))

    def _configure_signals(self):
        self.in_process_gpu.clicked.connect(lambda: SettingsManager.set(
            "performance/in_process_gpu", self.in_process_gpu.isChecked()))
        self.disable_gpu.clicked.connect(lambda: SettingsManager.set(
            "performance/disable_gpu", self.disable_gpu.isChecked()))
        self.single_process.clicked.connect(lambda: SettingsManager.set(
            "performance/single_process", self.single_process.isChecked()))
