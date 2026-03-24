from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.services.ThemeManager import ThemeManager


class _OnboardingPage(QWidget):
    """Página base do onboarding com título, subtítulo e conteúdo."""

    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; font-weight: 700;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #666;")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        layout.addLayout(self.content_layout)
        layout.addStretch()


class _TipItem(QWidget):
    """Componente visual para uma dica com ícone, título e descrição."""

    def __init__(self, icon: str, title: str, description: str, parent=None):
        super().__init__(parent)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        icon_label.setFixedWidth(24)
        row.addWidget(icon_label)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        title_label = QLabel(f"<b>{title}</b>")
        title_label.setWordWrap(True)
        text_col.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666;")
        text_col.addWidget(desc_label)

        row.addLayout(text_col, 1)


class _PermissionsPage(_OnboardingPage):
    def __init__(self, parent=None):
        super().__init__(
            _("Permissions and files"),
            _("Some permissions are required to send and download media without errors."),
            parent,
        )

        tips = [
            (
                "📁",
                _("Downloads folder"),
                _("Received files will be saved in the folder defined in Settings → General."),
            ),
            (
                "📎",
                _("Attach media"),
                _("To attach images, videos, and documents, allow access to your folders."),
            ),
            (
                "🔒",
                _("Flatpak users"),
                _(
                    "If you have trouble attaching files, use Flatseal to allow access "
                    "to Documents, Downloads, Pictures, and Videos."
                ),
            ),
        ]

        for icon, title, description in tips:
            self.content_layout.addWidget(
                _TipItem(icon, title, description, self))


class _NotificationsPage(_OnboardingPage):
    def __init__(self, parent=None):
        super().__init__(
            _("Notifications"),
            _("Choose how ZapZap should notify you about new messages."),
            parent,
        )

        self.enable_notifications = QCheckBox(_("Enable notifications"))
        self.enable_notifications.setChecked(
            SettingsManager.get("notification/app", True))
        self.enable_notifications.toggled.connect(
            lambda value: SettingsManager.set("notification/app", value)
        )
        self.content_layout.addWidget(self.enable_notifications)

        self.enable_tray = QCheckBox(_("Show system tray icon"))
        self.enable_tray.setChecked(
            SettingsManager.get("system/tray_icon", True))
        self.enable_tray.toggled.connect(self._on_tray_toggled)
        self.content_layout.addWidget(self.enable_tray)

        self.enable_counter = QCheckBox(_("Remove notification indicator"))
        self.enable_counter.setChecked(
            SettingsManager.get("system/notificationCounter", False))
        self.enable_counter.toggled.connect(self._on_counter_toggled)
        self.content_layout.addWidget(self.enable_counter)

        note = QLabel(
            _("Notifications may also depend on your operating system permissions.")
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-style: italic;")
        self.content_layout.addWidget(note)

    def _on_counter_toggled(self, value: bool):
        SettingsManager.set("system/notificationCounter", value)
        SysTrayManager.refresh()

    def _on_tray_toggled(self, value: bool):
        SysTrayManager.set_state(value)


class _VisualPage(_OnboardingPage):
    def __init__(self, parent=None):
        super().__init__(
            _("Appearance"),
            _("Adjust the theme and scale to make the interface more comfortable."),
            parent,
        )

        self.content_layout.addWidget(QLabel(f"<b>{_('Theme')}</b>"))

        theme = SettingsManager.get(
            "system/theme", ThemeManager.Type.Auto.value)

        self.theme_auto = QRadioButton(_("Automatic (follow system theme)"))
        self.theme_light = QRadioButton(_("Light"))
        self.theme_dark = QRadioButton(_("Dark"))

        mapping = {
            ThemeManager.Type.Auto.value: self.theme_auto,
            ThemeManager.Type.Light.value: self.theme_light,
            ThemeManager.Type.Dark.value: self.theme_dark,
        }
        mapping.get(theme, self.theme_auto).setChecked(True)

        self.content_layout.addWidget(self.theme_auto)
        self.content_layout.addWidget(self.theme_light)
        self.content_layout.addWidget(self.theme_dark)

        self.theme_auto.toggled.connect(
            lambda checked: checked and ThemeManager.set_theme(
                ThemeManager.Type.Auto)
        )
        self.theme_light.toggled.connect(
            lambda checked: checked and ThemeManager.set_theme(
                ThemeManager.Type.Light)
        )
        self.theme_dark.toggled.connect(
            lambda checked: checked and ThemeManager.set_theme(
                ThemeManager.Type.Dark)
        )

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        self.content_layout.addWidget(line)

        label_row = QHBoxLayout()
        label_row.addWidget(QLabel(f"<b>{_('Scale')}</b>"))
        label_row.addStretch()

        self.scale_label = QLabel()
        label_row.addWidget(self.scale_label)
        self.content_layout.addLayout(label_row)

        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(75, 200)
        self.scale_slider.setSingleStep(5)
        self.scale_slider.setPageStep(10)
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.setTickInterval(25)

        current_scale = int(SettingsManager.get("system/scale", 100))
        self.scale_slider.setValue(current_scale)
        self._update_scale_label(current_scale)

        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        self.content_layout.addWidget(self.scale_slider)

        hint = QLabel(_("The scale will be applied after restarting ZapZap."))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666; font-style: italic;")
        self.content_layout.addWidget(hint)

    def _on_scale_changed(self, value: int):
        self._update_scale_label(value)
        SettingsManager.set("system/scale", value)

    def _update_scale_label(self, value: int):
        self.scale_label.setText(f"{value} %")


class OnboardingDialog(QDialog):
    TOTAL_STEPS = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Welcome to ZapZap"))
        self.setModal(True)
        self.resize(560, 480)

        self.current_step = 0
        self._dots = []

        self._setup_ui()
        self._go_to_step(0)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget(self)
        self.stack.addWidget(_PermissionsPage(self))
        self.stack.addWidget(_NotificationsPage(self))
        self.stack.addWidget(_VisualPage(self))
        layout.addWidget(self.stack)

        layout.addWidget(self._build_footer())

    def _build_footer(self):
        footer = QWidget(self)
        footer.setStyleSheet(
            "background: #f8f8f8; border-top: 1px solid #ddd;")

        col = QVBoxLayout(footer)
        col.setContentsMargins(12, 8, 12, 8)
        col.setSpacing(6)

        dots_row = QHBoxLayout()
        dots_row.addStretch()
        for step_index in range(self.TOTAL_STEPS):
            dot = QLabel()
            dot.setFixedSize(10, 10)
            self._dots.append(dot)
            dots_row.addWidget(dot)
        dots_row.addStretch()
        col.addLayout(dots_row)

        nav_row = QHBoxLayout()

        self.btn_skip = QPushButton(_("Skip"))
        self.btn_skip.clicked.connect(self._on_skip)
        nav_row.addWidget(self.btn_skip)

        nav_row.addStretch()

        self.btn_previous = QPushButton(_("Previous"))
        self.btn_previous.clicked.connect(self._on_previous)
        nav_row.addWidget(self.btn_previous)

        self.btn_next = QPushButton(_("Next"))
        self.btn_next.clicked.connect(self._on_next)
        nav_row.addWidget(self.btn_next)

        col.addLayout(nav_row)

        self.chk_dont_show = QCheckBox(_("Don't show again"))
        col.addWidget(self.chk_dont_show)

        return footer

    def _go_to_step(self, step: int):
        self.current_step = step
        self.stack.setCurrentIndex(step)

        for index, dot in enumerate(self._dots):
            if index == self.current_step:
                dot.setStyleSheet("background: #25d366; border-radius: 5px;")
            else:
                dot.setStyleSheet("background: #bbb; border-radius: 5px;")

        is_last = self.current_step == self.TOTAL_STEPS - 1
        self.btn_previous.setVisible(self.current_step > 0)
        self.btn_next.setText(_("Finish") if is_last else _("Next"))

    def _on_next(self):
        if self.current_step < self.TOTAL_STEPS - 1:
            self._go_to_step(self.current_step + 1)
            return

        OnboardingManager.mark_complete()
        self.accept()

    def _on_previous(self):
        if self.current_step > 0:
            self._go_to_step(self.current_step - 1)

    def _on_skip(self):
        if self.chk_dont_show.isChecked():
            OnboardingManager.mark_complete()
        self.reject()

    def closeEvent(self, event):  # noqa: N802 - método do Qt
        if self.chk_dont_show.isChecked():
            OnboardingManager.mark_complete()
        super().closeEvent(event)


class OnboardingManager:
    SETTING_KEY = "onboarding/completed"

    @staticmethod
    def should_show() -> bool:
        return not SettingsManager.get(OnboardingManager.SETTING_KEY, False)

    @staticmethod
    def show(parent=None) -> bool:
        if not OnboardingManager.should_show():
            return False

        dialog = OnboardingDialog(parent)
        result = dialog.exec()

        return result == QDialog.DialogCode.Accepted

    @staticmethod
    def mark_complete():
        SettingsManager.set(OnboardingManager.SETTING_KEY, True)

    @staticmethod
    def reset():
        SettingsManager.remove(OnboardingManager.SETTING_KEY)
