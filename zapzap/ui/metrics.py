"""
UX Metrics tracking for ZapZap.
Tracks local, privacy-safe metrics to measure UX improvements.
All data is stored locally only - never sent externally.
"""

import json
import time
from dataclasses import dataclass, field
from gettext import gettext as _
from typing import Optional

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from zapzap.services.SettingsManager import SettingsManager
from zapzap.ui.design_tokens import DesignTokens

T = DesignTokens

# ---------------------------------------------------------------------------
# KPI targets
# ---------------------------------------------------------------------------

KPI_TARGETS = {
    "settings_discovery_improvement": -30,   # -30% target (faster discovery)
    "advanced_config_errors_reduction": -25,  # -25% target (fewer errors)
    "onboarding_completion_rate": 20,         # +20% target (more completions)
    "ui_satisfaction_improvement": 15,        # +15% target (higher satisfaction)
    "notification_complaints_reduction": -20, # -20% target (fewer complaints)
}

# ---------------------------------------------------------------------------
# Settings keys
# ---------------------------------------------------------------------------

_METRICS_KEY = "ux_metrics/data"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class MetricsEvent:
    """Represents a single recorded UX event."""

    event_type: str
    timestamp: float = field(default_factory=time.time)
    duration_ms: Optional[float] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MetricsEvent":
        return cls(
            event_type=data["event_type"],
            timestamp=data.get("timestamp", 0.0),
            duration_ms=data.get("duration_ms"),
            metadata=data.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# Singleton UXMetrics
# ---------------------------------------------------------------------------

class UXMetrics:
    """
    Singleton that records privacy-safe, local-only UX metrics.

    All events are persisted via :class:`~zapzap.services.SettingsManager.SettingsManager`
    so they survive application restarts.  No data ever leaves the device.
    """

    # ------------------------------------------------------------------
    # Event type constants
    # ------------------------------------------------------------------
    SETTINGS_SEARCH_USED = "settings_search_used"
    SETTINGS_PAGE_OPENED = "settings_page_opened"
    SETTINGS_TIME_TO_FIND = "settings_time_to_find"
    ONBOARDING_STARTED = "onboarding_started"
    ONBOARDING_COMPLETED = "onboarding_completed"
    ONBOARDING_SKIPPED = "onboarding_skipped"
    ONBOARDING_STEP_ABANDONED = "onboarding_step_abandoned"
    ACCOUNT_SWITCHED = "account_switched"
    ERROR_ENCOUNTERED = "error_encountered"
    UPLOAD_FAILED = "upload_failed"
    NOTIFICATION_FAILED = "notification_failed"
    FEATURE_USED = "feature_used"

    _instance: Optional["UXMetrics"] = None

    def __new__(cls) -> "UXMetrics":
        if cls._instance is None:
            obj = super().__new__(cls)
            obj._events: list[MetricsEvent] = []
            obj._active_tasks: dict[str, float] = {}
            obj._load()
            cls._instance = obj
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def track_event(self, event_type: str, metadata: Optional[dict] = None) -> None:
        """Log a single event with an optional metadata dict."""
        event = MetricsEvent(
            event_type=event_type,
            timestamp=time.time(),
            metadata=metadata or {},
        )
        self._events.append(event)
        self._save()

    def start_task(self, task_name: str) -> None:
        """Begin timing a named task.  Call :meth:`end_task` to record duration."""
        self._active_tasks[task_name] = time.time()

    def end_task(self, task_name: str) -> Optional[float]:
        """
        Finish timing *task_name* and record a timed event.

        Returns the elapsed duration in milliseconds, or ``None`` if the task
        was never started.
        """
        start = self._active_tasks.pop(task_name, None)
        if start is None:
            return None
        duration_ms = (time.time() - start) * 1000.0
        event = MetricsEvent(
            event_type=task_name,
            timestamp=time.time(),
            duration_ms=duration_ms,
        )
        self._events.append(event)
        self._save()
        return duration_ms

    def get_summary(self) -> dict:
        """Return a dictionary with aggregated metric summaries."""
        summary: dict = {
            "total_events": len(self._events),
            "settings_searches": 0,
            "avg_settings_find_ms": None,
            "onboarding_starts": 0,
            "onboarding_completions": 0,
            "onboarding_skips": 0,
            "onboarding_step_abandonments": 0,
            "account_switches": 0,
            "errors_encountered": 0,
            "upload_failures": 0,
            "notification_failures": 0,
            "features_used": 0,
            "pages_opened": {},
            "search_terms": [],
        }

        find_times: list[float] = []

        for event in self._events:
            et = event.event_type
            if et == self.SETTINGS_SEARCH_USED:
                summary["settings_searches"] += 1
                term = event.metadata.get("term", "")
                if term:
                    summary["search_terms"].append(term)
            elif et == self.SETTINGS_TIME_TO_FIND and event.duration_ms is not None:
                find_times.append(event.duration_ms)
            elif et == self.SETTINGS_PAGE_OPENED:
                page = event.metadata.get("page", "unknown")
                summary["pages_opened"][page] = summary["pages_opened"].get(page, 0) + 1
            elif et == self.ONBOARDING_STARTED:
                summary["onboarding_starts"] += 1
            elif et == self.ONBOARDING_COMPLETED:
                summary["onboarding_completions"] += 1
            elif et == self.ONBOARDING_SKIPPED:
                summary["onboarding_skips"] += 1
            elif et == self.ONBOARDING_STEP_ABANDONED:
                summary["onboarding_step_abandonments"] += 1
            elif et == self.ACCOUNT_SWITCHED:
                summary["account_switches"] += 1
            elif et == self.ERROR_ENCOUNTERED:
                summary["errors_encountered"] += 1
            elif et == self.UPLOAD_FAILED:
                summary["upload_failures"] += 1
            elif et == self.NOTIFICATION_FAILED:
                summary["notification_failures"] += 1
            elif et == self.FEATURE_USED:
                summary["features_used"] += 1

        if find_times:
            summary["avg_settings_find_ms"] = sum(find_times) / len(find_times)

        return summary

    def get_kpis(self) -> dict:
        """
        Return KPI progress values compared to targets.

        Each entry maps a KPI name to a dict with:
        - ``current``: measured value (percentage change approximation)
        - ``target``: target value from :data:`KPI_TARGETS`
        - ``achieved``: bool
        """
        summary = self.get_summary()
        kpis: dict = {}

        # ---- Settings discovery improvement (proxy: search usage rate) ----
        total = max(summary["total_events"], 1)
        search_rate = (summary["settings_searches"] / total) * 100
        # Higher search usage signals users are relying on search → improvement
        discovery_improvement = min(search_rate * -1, 0)  # negative = improvement
        target = KPI_TARGETS["settings_discovery_improvement"]
        kpis["settings_discovery_improvement"] = {
            "current": round(discovery_improvement, 1),
            "target": target,
            "achieved": discovery_improvement <= target,
        }

        # ---- Advanced config errors reduction ----
        error_rate = (summary["errors_encountered"] / total) * 100
        errors_reduction = min(-error_rate, 0)
        target = KPI_TARGETS["advanced_config_errors_reduction"]
        kpis["advanced_config_errors_reduction"] = {
            "current": round(errors_reduction, 1),
            "target": target,
            "achieved": errors_reduction <= target,
        }

        # ---- Onboarding completion rate ----
        starts = max(summary["onboarding_starts"], 1)
        completion_pct = (summary["onboarding_completions"] / starts) * 100
        target = KPI_TARGETS["onboarding_completion_rate"]
        kpis["onboarding_completion_rate"] = {
            "current": round(completion_pct, 1),
            "target": target,
            "achieved": completion_pct >= target,
        }

        # ---- UI satisfaction improvement (proxy: feature usage) ----
        feature_rate = (summary["features_used"] / total) * 100
        target = KPI_TARGETS["ui_satisfaction_improvement"]
        kpis["ui_satisfaction_improvement"] = {
            "current": round(feature_rate, 1),
            "target": target,
            "achieved": feature_rate >= target,
        }

        # ---- Notification complaints reduction ----
        notif_failure_rate = (summary["notification_failures"] / total) * 100
        notif_reduction = min(-notif_failure_rate, 0)
        target = KPI_TARGETS["notification_complaints_reduction"]
        kpis["notification_complaints_reduction"] = {
            "current": round(notif_reduction, 1),
            "target": target,
            "achieved": notif_reduction <= target,
        }

        return kpis

    def reset(self) -> None:
        """Clear all recorded events and active tasks (mainly for testing)."""
        self._events.clear()
        self._active_tasks.clear()
        SettingsManager.remove(_METRICS_KEY)

    def export_json(self) -> str:
        """Serialize all events and summary to a JSON string."""
        payload = {
            "events": [e.to_dict() for e in self._events],
            "summary": self.get_summary(),
            "kpis": self.get_kpis(),
            "exported_at": time.time(),
        }
        return json.dumps(payload, indent=2)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _save(self) -> None:
        """Persist current events to :class:`SettingsManager`."""
        data = json.dumps([e.to_dict() for e in self._events])
        SettingsManager.set(_METRICS_KEY, data)

    def _load(self) -> None:
        """Load persisted events from :class:`SettingsManager`."""
        raw = SettingsManager.get(_METRICS_KEY, None)
        if not raw:
            return
        try:
            records = json.loads(raw)
            self._events = [MetricsEvent.from_dict(r) for r in records]
        except (json.JSONDecodeError, KeyError, TypeError):
            self._events = []


# ---------------------------------------------------------------------------
# MetricsDashboard widget
# ---------------------------------------------------------------------------

_DASHBOARD_QSS = f"""
QWidget#metrics_dashboard {{
    background-color: {T.LIGHT_BACKGROUND};
}}
QLabel#dashboard_title {{
    font-size: {T.FONT_SIZE_H2}px;
    font-weight: 700;
    color: {T.LIGHT_TEXT_PRIMARY};
}}
QLabel#section_header {{
    font-size: {T.FONT_SIZE_H3}px;
    font-weight: 600;
    color: {T.LIGHT_TEXT_PRIMARY};
}}
QLabel#kpi_label {{
    font-size: {T.FONT_SIZE_BODY}px;
    color: {T.LIGHT_TEXT_SECONDARY};
}}
QLabel#kpi_value {{
    font-size: {T.FONT_SIZE_BODY}px;
    font-weight: 600;
    color: {T.LIGHT_TEXT_PRIMARY};
}}
QProgressBar {{
    border: 1px solid {T.LIGHT_BORDER};
    border-radius: {T.RADIUS_SM}px;
    background-color: {T.LIGHT_SURFACE_RAISED};
    height: 10px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {T.LIGHT_PRIMARY};
    border-radius: {T.RADIUS_SM}px;
}}
QPushButton#action_btn {{
    background-color: {T.LIGHT_SURFACE_RAISED};
    border: 1px solid {T.LIGHT_BORDER};
    border-radius: {T.RADIUS_MD}px;
    padding: 8px 16px;
    font-size: {T.FONT_SIZE_BODY}px;
    color: {T.LIGHT_TEXT_PRIMARY};
}}
QPushButton#action_btn:hover {{
    background-color: {T.LIGHT_SURFACE_OVERLAY};
    border-color: {T.LIGHT_BORDER_STRONG};
}}
QPushButton#reset_btn {{
    background-color: {T.COLOR_ERROR_BG_LIGHT};
    border: 1px solid {T.COLOR_ERROR};
    border-radius: {T.RADIUS_MD}px;
    padding: 8px 16px;
    font-size: {T.FONT_SIZE_BODY}px;
    color: {T.COLOR_ERROR};
}}
QPushButton#reset_btn:hover {{
    background-color: {T.COLOR_ERROR};
    color: #FFFFFF;
}}
"""

_KPI_DISPLAY_NAMES = {
    "settings_discovery_improvement": _("Settings Discovery Time"),
    "advanced_config_errors_reduction": _("Config Error Rate"),
    "onboarding_completion_rate": _("Onboarding Completion"),
    "ui_satisfaction_improvement": _("UI Feature Adoption"),
    "notification_complaints_reduction": _("Notification Failure Rate"),
}

_KPI_DESCRIPTIONS = {
    "settings_discovery_improvement": _("Target: −30% time to find settings"),
    "advanced_config_errors_reduction": _("Target: −25% config errors"),
    "onboarding_completion_rate": _("Target: +20% onboarding completions"),
    "ui_satisfaction_improvement": _("Target: +15% feature adoption"),
    "notification_complaints_reduction": _("Target: −20% notification failures"),
}


class MetricsDashboard(QWidget):
    """
    A simple QWidget dashboard that visualises KPI progress toward targets.

    Intended to be embedded inside the Settings dialog or shown as a standalone
    window during development / QA sessions.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("metrics_dashboard")
        self.setStyleSheet(_DASHBOARD_QSS)

        self._metrics = UXMetrics()
        self._kpi_bars: dict[str, QProgressBar] = {}
        self._kpi_value_labels: dict[str, QLabel] = {}

        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        root.setSpacing(T.SPACING_MD)

        # Title
        title = QLabel(_("UX Metrics Dashboard"))
        title.setObjectName("dashboard_title")
        root.addWidget(title)

        subtitle = QLabel(_("All data is stored locally only — never sent externally."))
        subtitle.setObjectName("kpi_label")
        root.addWidget(subtitle)

        # Separator
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {T.LIGHT_BORDER};")
        root.addWidget(line)

        # KPI section header
        kpi_header = QLabel(_("Key Performance Indicators"))
        kpi_header.setObjectName("section_header")
        root.addWidget(kpi_header)

        # Scrollable KPI list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)
        kpi_container = QWidget()
        kpi_layout = QVBoxLayout(kpi_container)
        kpi_layout.setSpacing(T.SPACING_MD)
        kpi_layout.setContentsMargins(0, 0, 0, 0)

        for kpi_key in KPI_TARGETS:
            self._build_kpi_row(kpi_layout, kpi_key)

        kpi_layout.addStretch()
        scroll.setWidget(kpi_container)
        root.addWidget(scroll, 1)

        # Summary stats label
        self._summary_label = QLabel("")
        self._summary_label.setObjectName("kpi_label")
        self._summary_label.setWordWrap(True)
        root.addWidget(self._summary_label)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(T.SPACING_SM)

        refresh_btn = QPushButton(_("Refresh"))
        refresh_btn.setObjectName("action_btn")
        refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(refresh_btn)

        export_btn = QPushButton(_("Export JSON"))
        export_btn.setObjectName("action_btn")
        export_btn.clicked.connect(self._on_export)
        btn_row.addWidget(export_btn)

        btn_row.addStretch()

        reset_btn = QPushButton(_("Reset Metrics"))
        reset_btn.setObjectName("reset_btn")
        reset_btn.clicked.connect(self._on_reset)
        btn_row.addWidget(reset_btn)

        root.addLayout(btn_row)

    def _build_kpi_row(self, layout: QVBoxLayout, kpi_key: str) -> None:
        """Add a labelled progress-bar row for one KPI."""
        name = _KPI_DISPLAY_NAMES.get(kpi_key, kpi_key)
        description = _KPI_DESCRIPTIONS.get(kpi_key, "")
        target = KPI_TARGETS[kpi_key]

        row_widget = QWidget()
        row_layout = QVBoxLayout(row_widget)
        row_layout.setSpacing(T.SPACING_XS)
        row_layout.setContentsMargins(0, 0, 0, 0)

        # Header row: name + current value
        header_row = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setObjectName("kpi_label")
        header_row.addWidget(name_label)
        header_row.addStretch()

        value_label = QLabel("—")
        value_label.setObjectName("kpi_value")
        header_row.addWidget(value_label)
        self._kpi_value_labels[kpi_key] = value_label

        row_layout.addLayout(header_row)

        # Progress bar
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bar.setFixedHeight(10)
        self._kpi_bars[kpi_key] = bar
        row_layout.addWidget(bar)

        # Description / target
        desc_label = QLabel(description)
        desc_label.setObjectName("kpi_label")
        row_layout.addWidget(desc_label)

        layout.addWidget(row_widget)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Re-read metrics and update all widgets."""
        kpis = self._metrics.get_kpis()
        summary = self._metrics.get_summary()

        for kpi_key, data in kpis.items():
            current = data["current"]
            target = KPI_TARGETS[kpi_key]
            achieved = data["achieved"]

            value_label = self._kpi_value_labels.get(kpi_key)
            bar = self._kpi_bars.get(kpi_key)
            if value_label is None or bar is None:
                continue

            value_label.setText(f"{current:+.1f}%")

            if target < 0:
                # Reduction target: progress = how close we are to the target
                progress = int(min(abs(current) / abs(target) * 100, 100))
            else:
                # Increase target: progress = how close we are to the target
                progress = int(min(current / target * 100, 100)) if target else 0

            bar.setValue(progress)

            color = T.COLOR_SUCCESS if achieved else T.LIGHT_PRIMARY
            bar.setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {color}; "
                f"border-radius: {T.RADIUS_SM}px; }}"
            )

        self._summary_label.setText(
            _(
                "Total events: {total}  |  Searches: {searches}  |  "
                "Errors: {errors}  |  Account switches: {switches}"
            ).format(
                total=summary["total_events"],
                searches=summary["settings_searches"],
                errors=summary["errors_encountered"],
                switches=summary["account_switches"],
            )
        )

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _on_export(self) -> None:
        """Write JSON export to a file and show confirmation."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        path, _ = QFileDialog.getSaveFileName(
            self,
            _("Export Metrics"),
            "zapzap_metrics.json",
            _("JSON Files (*.json)"),
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(self._metrics.export_json())
                QMessageBox.information(self, _("Export"), _("Metrics exported successfully."))
            except OSError as exc:
                QMessageBox.warning(self, _("Export Failed"), str(exc))

    def _on_reset(self) -> None:
        """Confirm and reset all metrics."""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            _("Reset Metrics"),
            _("Are you sure you want to clear all recorded metrics? This cannot be undone."),
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._metrics.reset()
            self.refresh()
