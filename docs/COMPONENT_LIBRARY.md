# ZapZap Component Library Reference

This document describes every reusable UI component available in the
`zapzap/ui/` module.  For each component, the import path, constructor
parameters, available states, and accessibility notes are provided.

---

## Table of Contents

1. [Buttons](#1-buttons)
2. [Inputs](#2-inputs)
3. [Cards](#3-cards)
4. [Dialogs](#4-dialogs)
5. [Empty States](#5-empty-states)
6. [Loading States](#6-loading-states)
7. [Metrics](#7-metrics)

---

## 1. Buttons

**Import path**: `from zapzap.ui.components.buttons import <ComponentName>`

---

### `PrimaryButton`

The main call-to-action button.  Uses the brand green `#25D366`.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | Button label |
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from zapzap.ui.components.buttons import PrimaryButton

btn = PrimaryButton(_("Save changes"), parent=self)
btn.clicked.connect(self.on_save)
layout.addWidget(btn)
```

**States**

| State | Visual |
|-------|--------|
| Default | `#25D366` background, white text |
| Hover | `#1EBE59` background |
| Pressed | `#17A34A` background |
| Disabled | Muted green, 40% opacity |
| Focus | 2 px `#25D366` focus ring offset by 2 px |

**Accessibility**
- Sets `setAccessibleName(text)` automatically.
- Minimum height: 36 px (keyboard-accessible target).
- Focus ring is WCAG AA compliant (3:1 contrast on common backgrounds).

---

### `SecondaryButton`

Outlined button for secondary actions.

**Parameters**: same as `PrimaryButton`.

**Usage**

```python
from zapzap.ui.components.buttons import SecondaryButton

btn = SecondaryButton(_("Cancel"), parent=self)
```

**States**

| State | Visual |
|-------|--------|
| Default | Transparent background, `#25D366` border and text |
| Hover | Slight green tint background |
| Pressed | Darker border |
| Disabled | Grey border and text |

---

### `GhostButton`

Text-only button with no border or background.  For low-emphasis actions.

**Usage**

```python
from zapzap.ui.components.buttons import GhostButton

btn = GhostButton(_("Skip"), parent=self)
```

---

### `DangerButton`

Destructive action button.  Uses `#EF4444` error red.

**Usage**

```python
from zapzap.ui.components.buttons import DangerButton

btn = DangerButton(_("Delete account"), parent=self)
btn.clicked.connect(self.on_delete)
```

**Accessibility**
- Sets accessible description: "Destructive action — cannot be undone."
- Recommended to pair with a `ConfirmationDialog`.

---

### `IconButton`

Icon-only button.  Requires a descriptive tooltip for accessibility.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `icon` | `QIcon` | required | Button icon |
| `tooltip` | `str` | required | Tooltip text (also used as accessible name) |
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from PyQt6.QtGui import QIcon
from zapzap.ui.components.buttons import IconButton

btn = IconButton(
    icon=QIcon.fromTheme("edit-clear"),
    tooltip=_("Clear search"),
    parent=self,
)
```

**Accessibility**
- `setAccessibleName(tooltip)` is set automatically.
- Minimum size: 36×36 px.

---

## 2. Inputs

**Import path**: `from zapzap.ui.components.inputs import <ComponentName>`

---

### `SearchInput`

A text input with a leading search icon and an optional clear button.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `placeholder` | `str` | `""` | Placeholder text |
| `parent` | `QWidget` | `None` | Parent widget |

**Signals**

| Signal | Args | Description |
|--------|------|-------------|
| `textChanged` | `str` | Emitted on every keystroke |
| `cleared` | — | Emitted when clear (×) button is pressed |
| `returnPressed` | — | Emitted on Enter key |

**Usage**

```python
from zapzap.ui.components.inputs import SearchInput

search = SearchInput(placeholder=_("Search settings…"), parent=self)
search.textChanged.connect(self.on_search)
```

**Accessibility**
- `setAccessibleName(_("Search"))` set automatically.
- `setAccessibleDescription(placeholder)`.
- Announces result count updates via `QAccessible.updateAccessibility()`.

---

### `LabelledInput`

A single-line input with an integrated visible label above it.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | required | Visible label text |
| `placeholder` | `str` | `""` | Placeholder text |
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from zapzap.ui.components.inputs import LabelledInput

name_input = LabelledInput(label=_("Display name"), placeholder=_("Enter your name"))
```

**States**

| State | Visual |
|-------|--------|
| Default | `#D0D4D8` border |
| Focused | `#25D366` border |
| Error | `#EF4444` border + error message below |
| Disabled | `#F0F2F5` background, greyed text |

**Methods**

| Method | Description |
|--------|-------------|
| `set_error(msg)` | Show error message below the input |
| `clear_error()` | Remove the error state |
| `value()` | Return the current text |

---

### `TextAreaInput`

Multi-line text input with a visible label.

**Parameters**: same as `LabelledInput` plus:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_height` | `int` | `80` | Minimum height in pixels |

---

## 3. Cards

**Import path**: `from zapzap.ui.components.cards import <ComponentName>`

---

### `CardWidget`

A panel with a subtle border and shadow for grouping content.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from zapzap.ui.components.cards import CardWidget
from PyQt6.QtWidgets import QVBoxLayout, QLabel

card = CardWidget(parent=self)
card_layout = QVBoxLayout(card)
card_layout.addWidget(QLabel(_("Card content")))
layout.addWidget(card)
```

**Notes**
- Uses `LIGHT_CARD_BG` / `DARK_CARD_BG` for background.
- Border radius: `RADIUS_MD` (8 px).
- Internal content margin: `SPACING_MD` (16 px).

---

### `SelectableCard`

A card that can be clicked / selected.  Emits `selected(bool)` on toggle.

**Signals**

| Signal | Args | Description |
|--------|------|-------------|
| `selected` | `bool` | `True` when card becomes selected |

**Usage**

```python
from zapzap.ui.components.cards import SelectableCard

card = SelectableCard(parent=self)
card.selected.connect(lambda checked: print("Card selected:", checked))
```

**States**

| State | Visual |
|-------|--------|
| Default | Normal card style |
| Hover | `LIGHT_SURFACE_OVERLAY` background |
| Selected | `#25D366` border, slight tint background |
| Focused | `#25D366` focus ring |

**Accessibility**
- `setCheckable(True)` equivalent behaviour; state announced to screen readers.

---

## 4. Dialogs

**Import path**: `from zapzap.ui.components.dialogs import <ComponentName>`

---

### `ConfirmationDialog`

A modal dialog asking the user to confirm or cancel an action.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | required | Dialog title |
| `message` | `str` | required | Explanation text |
| `confirm_text` | `str` | `_("Confirm")` | Text on confirm button |
| `cancel_text` | `str` | `_("Cancel")` | Text on cancel button |
| `destructive` | `bool` | `False` | If True, confirm button uses danger style |
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from zapzap.ui.components.dialogs import ConfirmationDialog

dlg = ConfirmationDialog(
    title=_("Remove account"),
    message=_("Are you sure you want to remove this account? You can add it again later."),
    confirm_text=_("Remove"),
    destructive=True,
    parent=self,
)
if dlg.exec() == ConfirmationDialog.DialogCode.Accepted:
    self.remove_account()
```

**Accessibility**
- Focus is set to the Cancel button by default (safe default).
- Focus is trapped inside the dialog while it is open.
- Title and message are read by screen readers on open.

---

### `InfoDialog`

A simple informational dialog with an OK button.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | required | Dialog title |
| `message` | `str` | required | Informational message |
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from zapzap.ui.components.dialogs import InfoDialog

InfoDialog(
    title=_("Settings saved"),
    message=_("Your settings have been saved successfully."),
    parent=self,
).exec()
```

---

## 5. Empty States

**Import path**: `from zapzap.ui.empty_states import EmptyStateWidget, EmptyStateFactory`

---

### `EmptyStateWidget`

A centred widget displaying an icon, headline, description, and optional CTA.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `icon_name` | `str` | required | Theme icon name (e.g. `"folder-open"`) |
| `title` | `str` | required | Headline text |
| `description` | `str` | `""` | Supporting description |
| `action_text` | `str` | `""` | CTA button label (omit to hide) |
| `parent` | `QWidget` | `None` | Parent widget |

**Signals**

| Signal | Description |
|--------|-------------|
| `action_clicked` | Emitted when CTA button is clicked |

**Usage**

```python
from zapzap.ui.empty_states import EmptyStateWidget

widget = EmptyStateWidget(
    icon_name="folder-open",
    title=_("No chats yet"),
    description=_("Your conversations will appear here."),
    parent=self,
)
layout.addWidget(widget)
```

---

### `EmptyStateFactory`

Convenience factory methods for common empty states.

| Method | Description |
|--------|-------------|
| `EmptyStateFactory.no_accounts(parent)` | No WhatsApp accounts added |
| `EmptyStateFactory.no_chats(parent)` | No conversations yet |
| `EmptyStateFactory.no_search_results(term, parent)` | Search returned nothing |
| `EmptyStateFactory.loading_error(parent)` | Failed to load content |
| `EmptyStateFactory.no_notifications(parent)` | No unread notifications |
| `EmptyStateFactory.offline(parent)` | No network connection |

**Usage**

```python
from zapzap.ui.empty_states import EmptyStateFactory

empty = EmptyStateFactory.no_search_results("my query", parent=self)
empty.action_clicked.connect(self.clear_search)
layout.addWidget(empty)
```

---

## 6. Loading States

**Import path**: `from zapzap.ui.loading_states import <ComponentName>`

---

### `LoadingSpinner`

An animated circular spinner using the brand primary color.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `size` | `int` | `32` | Diameter in pixels |
| `color` | `str` | `LIGHT_PRIMARY` | Spinner color (hex) |
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from zapzap.ui.loading_states import LoadingSpinner

spinner = LoadingSpinner(size=48, parent=self)
spinner.start()
# ... once loading is done:
spinner.stop()
```

**Accessibility**
- `setAccessibleName(_("Loading"))` set automatically.
- Emits an accessibility event when started/stopped.

---

### `SkeletonLoader`

A shimmer-effect placeholder that matches the shape of the content being loaded.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | `int` | `200` | Width in pixels |
| `height` | `int` | `16` | Height in pixels |
| `radius` | `int` | `RADIUS_SM` | Border radius |
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from zapzap.ui.loading_states import SkeletonLoader

# Three skeleton lines simulating a text block
for _ in range(3):
    skeleton = SkeletonLoader(width=300, height=14, parent=self)
    layout.addWidget(skeleton)
```

---

### `LoadingOverlay`

A semi-transparent overlay with a centered spinner and optional message.
Covers the entire parent widget.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | `_("Loading…")` | Message below spinner |
| `parent` | `QWidget` | `None` | Widget to overlay |

**Usage**

```python
from zapzap.ui.loading_states import LoadingOverlay

overlay = LoadingOverlay(message=_("Switching account…"), parent=self)
overlay.show()
# ... once done:
overlay.hide()
```

---

## 7. Metrics

**Import path**: `from zapzap.ui.metrics import UXMetrics, MetricsDashboard, KPI_TARGETS`

---

### `UXMetrics`

Singleton class for tracking privacy-safe, local UX metrics.

**Usage**

```python
from zapzap.ui.metrics import UXMetrics

metrics = UXMetrics()  # Always returns the same instance

# Track an event
metrics.track_event(UXMetrics.SETTINGS_SEARCH_USED, {"term": "notification"})

# Time a task
metrics.start_task("settings_find")
# ... user action ...
elapsed_ms = metrics.end_task("settings_find")

# Get summary
summary = metrics.get_summary()
print(summary["settings_searches"])   # int

# Get KPIs vs targets
kpis = metrics.get_kpis()
print(kpis["onboarding_completion_rate"]["achieved"])  # bool

# Export to JSON
json_str = metrics.export_json()

# Reset (e.g., in tests)
metrics.reset()
```

**Event Type Constants**

| Constant | Value |
|----------|-------|
| `SETTINGS_SEARCH_USED` | `"settings_search_used"` |
| `SETTINGS_PAGE_OPENED` | `"settings_page_opened"` |
| `SETTINGS_TIME_TO_FIND` | `"settings_time_to_find"` |
| `ONBOARDING_STARTED` | `"onboarding_started"` |
| `ONBOARDING_COMPLETED` | `"onboarding_completed"` |
| `ONBOARDING_SKIPPED` | `"onboarding_skipped"` |
| `ONBOARDING_STEP_ABANDONED` | `"onboarding_step_abandoned"` |
| `ACCOUNT_SWITCHED` | `"account_switched"` |
| `ERROR_ENCOUNTERED` | `"error_encountered"` |
| `UPLOAD_FAILED` | `"upload_failed"` |
| `NOTIFICATION_FAILED` | `"notification_failed"` |
| `FEATURE_USED` | `"feature_used"` |

---

### `MetricsDashboard`

A `QWidget` showing KPI progress toward targets with export/reset controls.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | `QWidget` | `None` | Parent widget |

**Usage**

```python
from zapzap.ui.metrics import MetricsDashboard

dashboard = MetricsDashboard(parent=self)
layout.addWidget(dashboard)
# Or show as standalone window:
dashboard.setWindowTitle(_("UX Metrics"))
dashboard.resize(600, 500)
dashboard.show()
```

**Methods**

| Method | Description |
|--------|-------------|
| `refresh()` | Re-read metrics and update all progress bars |

---

### `KPI_TARGETS`

Dictionary of target values for each KPI:

```python
from zapzap.ui.metrics import KPI_TARGETS

print(KPI_TARGETS)
# {
#   "settings_discovery_improvement": -30,
#   "advanced_config_errors_reduction": -25,
#   "onboarding_completion_rate": 20,
#   "ui_satisfaction_improvement": 15,
#   "notification_complaints_reduction": -20,
# }
```
