"""Accessible release details shown from the passive update indicator."""

from gettext import gettext as _

from PyQt6.QtCore import QDate, QEvent, QLocale, QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QColor

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.ui.primitives import Button, Label


class UpdateAvailablePopover(QFrame):
    """Compact interactive details for one available stable release."""

    download_requested = pyqtSignal()
    release_notes_requested = pyqtSignal(str)
    pointer_entered = pyqtSignal()
    pointer_exited = pyqtSignal()

    WIDTH = 410
    SHADOW_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self._info = None
        self.setObjectName("UpdateAvailablePopover")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedWidth(self.WIDTH)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
        )

        self.surface = QFrame(self)
        self.surface.setObjectName("UpdateAvailablePopoverSurface")
        outer.addWidget(self.surface)

        shadow = QGraphicsDropShadowEffect(self.surface)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.surface.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.surface)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        self.title_label = Label(_("Update available"), "section_title", self.surface)
        layout.addWidget(self.title_label)

        details = QWidget(self.surface)
        details_layout = QHBoxLayout(details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(14)

        self.icon_label = QLabel(details)
        self.icon_label.setFixedSize(58, 58)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setPixmap(UserIcon.get_icon().pixmap(54, 54))
        self.icon_label.setAccessibleName(_("ZapZap application icon"))
        details_layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignTop)

        text = QWidget(details)
        text_layout = QVBoxLayout(text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)
        self.app_label = Label("ZapZap", "row_title", text)
        self.current_version_label = Label("", "row_description", text)
        self.latest_version_label = Label("", "row_description", text)
        self.release_date_label = Label("", "row_description", text)
        for label in (
            self.app_label,
            self.current_version_label,
            self.latest_version_label,
            self.release_date_label,
        ):
            text_layout.addWidget(label)
        details_layout.addWidget(text, 1)
        layout.addWidget(details)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(10)
        self.release_notes_button = Button(_("Release notes"), parent=self.surface)
        self.release_notes_button.setAccessibleName(_("Open release notes"))
        self.download_button = Button(
            _("Download"),
            variant=Button.PRIMARY,
            parent=self.surface,
        )
        self.download_button.setAccessibleName(_("Open downloads page"))
        actions.addWidget(self.release_notes_button)
        actions.addStretch(1)
        actions.addWidget(self.download_button)
        layout.addLayout(actions)

        self.release_notes_button.clicked.connect(self._request_release_notes)
        self.download_button.clicked.connect(self._request_download)
        self.release_notes_button.installEventFilter(self)
        self.download_button.installEventFilter(self)

    def _apply_style(self):
        self.setStyleSheet(
            """
            QFrame#UpdateAvailablePopover {
                background: transparent;
                border: 0;
            }
            QFrame#UpdateAvailablePopoverSurface {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 12px;
            }
            """
        )

    def set_update_info(self, info):
        self._info = info
        if info is None:
            self.hide()
            return

        self.current_version_label.setText(
            _("Current version: {version}").format(version=info.current_version)
        )
        self.latest_version_label.setText(
            _("Latest version: {version}").format(version=info.latest_version)
        )
        if info.published_on is None:
            self.release_date_label.hide()
        else:
            value = info.published_on
            language = TranslationManager.get_current_language()
            locale = (
                QLocale.system()
                if language == TranslationManager.SYSTEM_LANGUAGE
                else QLocale(language)
            )
            localized = locale.toString(
                QDate(value.year, value.month, value.day),
                QLocale.FormatType.LongFormat,
            )
            self.release_date_label.setText(
                _("Released on {date}").format(date=localized)
            )
            self.release_date_label.show()
        self.release_notes_button.setVisible(bool(info.release_notes_url))
        description = _(
            "ZapZap {latest} is available. Current version: {current}."
        ).format(latest=info.latest_version, current=info.current_version)
        self.setAccessibleName(_("Update available"))
        self.setAccessibleDescription(description)

    def popup_for(self, anchor, focus_actions=False):
        if self._info is None or not self._info.available:
            return False

        self.adjustSize()
        anchor_top_right = anchor.mapToGlobal(QPoint(anchor.width() + 8, 0))
        target = QPoint(
            anchor_top_right.x(),
            anchor_top_right.y() + (anchor.height() - self.height()) // 2,
        )
        screen = (
            QGuiApplication.screenAt(anchor.mapToGlobal(anchor.rect().center()))
            or QGuiApplication.primaryScreen()
        )
        if screen is not None:
            available = screen.availableGeometry()
            target.setX(
                min(max(target.x(), available.left()), available.right() - self.width() + 1)
            )
            target.setY(
                min(max(target.y(), available.top()), available.bottom() - self.height() + 1)
            )
        self.move(target)
        self.show()
        self.raise_()
        if focus_actions:
            self.activateWindow()
            target_button = (
                self.release_notes_button
                if not self.release_notes_button.isHidden()
                else self.download_button
            )
            target_button.setFocus(Qt.FocusReason.PopupFocusReason)
        return True

    def _request_release_notes(self):
        url = self._info.release_notes_url if self._info is not None else ""
        self.close()
        if url:
            self.release_notes_requested.emit(url)

    def _request_download(self):
        self.close()
        self.download_requested.emit()

    def enterEvent(self, event):
        self.pointer_entered.emit()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.pointer_exited.emit()
        super().leaveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.close()
            return True
        return super().eventFilter(watched, event)
