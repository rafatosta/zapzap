# ZapZap Implementation Roadmap

This document describes the 4-phase UX/UI improvement plan for ZapZap,
including integration guides, migration notes, timeline, and success metrics.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Phase 1: Foundation](#2-phase-1-foundation)
3. [Phase 2: Structure & Discovery](#3-phase-2-structure--discovery)
4. [Phase 3: High-Impact Flows](#4-phase-3-high-impact-flows)
5. [Phase 4: Quality & Metrics](#5-phase-4-quality--metrics)
6. [Integration Guide](#6-integration-guide)
7. [Migration Guide](#7-migration-guide)
8. [Timeline](#8-timeline)
9. [Success Metrics](#9-success-metrics)

---

## 1. Overview

The roadmap follows a **progressive enhancement** strategy: each phase delivers
independent, mergeable improvements without breaking any existing behavior.

```
Week 1–3    Phase 1: Foundation
Week 4–6    Phase 2: Structure & Discovery
Week 7–9    Phase 3: High-Impact Flows
Week 10–12  Phase 4: Quality & Metrics
```

**Guiding principles**:
- No breaking changes to existing public APIs.
- Each phase is independently deployable.
- New modules live in `zapzap/ui/`; existing views are incrementally updated.
- All new UI must pass the Accessibility Checklist before merge.

---

## 2. Phase 1: Foundation

**Weeks 1–3**  
**Goal**: Establish the design system so all subsequent phases are consistent.

### Deliverables

| File | Description | Status |
|------|-------------|--------|
| `zapzap/ui/design_tokens.py` | Color palette, typography, spacing, radii | ✅ Done |
| `zapzap/ui/components/buttons.py` | Primary, Secondary, Ghost, Danger, Icon buttons | ✅ Done |
| `zapzap/ui/components/inputs.py` | Search, Labelled, TextArea inputs | ✅ Done |
| `zapzap/ui/components/cards.py` | CardWidget, SelectableCard | ✅ Done |
| `zapzap/ui/components/dialogs.py` | ConfirmationDialog, InfoDialog | ✅ Done |
| `zapzap/ui/accessibility.py` | AccessibilityHelper, FocusManager | ✅ Done |

### Acceptance Criteria

- [ ] All existing views continue to work unchanged after adding these modules.
- [ ] `DesignTokens` provides light and dark values for every color in the app.
- [ ] All component states (hover, focus, disabled, error) are implemented.
- [ ] Components pass keyboard navigation and screen reader checks.

### Integration

Phase 1 modules are passive — they are not imported by existing code until
Phase 2 explicitly adopts them.  No integration steps required for Phase 1 alone.

---

## 3. Phase 2: Structure & Discovery

**Weeks 4–6**  
**Goal**: Help users find settings faster and reduce first-run drop-off.

### Deliverables

| File | Description | Status |
|------|-------------|--------|
| `zapzap/ui/settings_reorganized.py` | Reorganized settings with clear categories | ✅ Done |
| `zapzap/ui/search_settings.py` | In-dialog settings search with results highlighting | ✅ Done |
| `zapzap/ui/onboarding.py` | 3-step onboarding wizard + `OnboardingManager` | ✅ Done |

### Acceptance Criteria

- [ ] Settings dialog has a working search field.
- [ ] Search results match by category name and setting label.
- [ ] Empty state shown when no results found.
- [ ] Onboarding wizard shown on first launch; not shown again after completion or skip.
- [ ] Onboarding persists all selections via `SettingsManager`.
- [ ] All flows keyboard-accessible.

### Integration Steps

#### 1. Trigger onboarding on startup

In `zapzap/__main__.py` or the main window `__init__`:

```python
from zapzap.ui.onboarding import OnboardingManager

# After the main window is shown:
OnboardingManager.maybe_show(parent=main_window)
```

#### 2. Replace the existing settings dialog

In the code that opens the Settings dialog:

```python
# Before:
# dlg = SettingsDialog(parent=self)

# After:
from zapzap.ui.settings_reorganized import SettingsReorganized
dlg = SettingsReorganized(parent=self)
dlg.exec()
```

---

## 4. Phase 3: High-Impact Flows

**Weeks 7–9**  
**Goal**: Remove the two highest-friction UX moments: account switching and
blank screens.

### Deliverables

| File | Description | Status |
|------|-------------|--------|
| `zapzap/ui/account_switcher_improved.py` | Dedicated account-switching widget | ✅ Done |
| `zapzap/ui/empty_states.py` | Contextual empty-state components + factory | ✅ Done |
| `zapzap/ui/loading_states.py` | Spinner, skeleton loader, loading overlay | ✅ Done |

### Acceptance Criteria

- [ ] Account switcher shows all accounts with name, avatar, unread badge.
- [ ] Switching accounts via keyboard works (`Ctrl+Tab`).
- [ ] Empty state shown wherever no content exists (no chats, no search results).
- [ ] Loading overlay shown during account switching.
- [ ] All new components match both light and dark themes.

### Integration Steps

#### 1. Replace the account switcher widget

```python
from zapzap.ui.account_switcher_improved import AccountSwitcherImproved

# Replace the old account switcher in the sidebar:
switcher = AccountSwitcherImproved(parent=sidebar_widget)
switcher.account_changed.connect(self.on_account_changed)
sidebar_layout.addWidget(switcher)
```

#### 2. Add empty states to chat/account areas

```python
from zapzap.ui.empty_states import EmptyStateFactory

# In the accounts area when no accounts are configured:
empty = EmptyStateFactory.no_accounts(parent=self)
empty.action_clicked.connect(self.on_add_account)
stacked_widget.addWidget(empty)
stacked_widget.setCurrentWidget(empty)
```

#### 3. Wrap long operations with the loading overlay

```python
from zapzap.ui.loading_states import LoadingOverlay

overlay = LoadingOverlay(message=_("Switching account…"), parent=self)
overlay.show()
try:
    self.do_account_switch()
finally:
    overlay.hide()
```

---

## 5. Phase 4: Quality & Metrics

**Weeks 10–12**  
**Goal**: Validate the impact of phases 1–3 and deliver QA tooling.

### Deliverables

| File | Description | Status |
|------|-------------|--------|
| `zapzap/ui/metrics.py` | `UXMetrics` singleton + `MetricsDashboard` | ✅ Done |
| `docs/ACCESSIBILITY_CHECKLIST.md` | WCAG AA checklist | ✅ Done |
| `docs/QA_VISUAL_CHECKLIST.md` | Visual QA checklist | ✅ Done |
| `docs/TESTING_GUIDE.md` | Complete testing guide | ✅ Done |
| `docs/UX_UI_IMPROVEMENTS.md` | Full UX improvements summary | ✅ Done |
| `docs/DESIGN_SYSTEM.md` | Design system documentation | ✅ Done |
| `docs/COMPONENT_LIBRARY.md` | Component library reference | ✅ Done |
| `docs/IMPLEMENTATION_ROADMAP.md` | This document | ✅ Done |

### Acceptance Criteria

- [ ] `UXMetrics` records events correctly and persists across restarts.
- [ ] `get_kpis()` returns valid values even with zero recorded events.
- [ ] `MetricsDashboard` renders without errors in both themes.
- [ ] Export produces valid JSON.
- [ ] Reset clears all data.
- [ ] All documentation files are complete and accurate.

### Integration Steps

#### 1. Instrument key events

Add tracking calls at the points described below.

**Settings search** (`search_settings.py`):

```python
from zapzap.ui.metrics import UXMetrics

metrics = UXMetrics()

def on_search_text_changed(self, text: str) -> None:
    if text:
        metrics.track_event(UXMetrics.SETTINGS_SEARCH_USED, {"term": text})
```

**Onboarding** (`onboarding.py`):

```python
# On wizard open:
metrics.track_event(UXMetrics.ONBOARDING_STARTED)

# On completion:
metrics.track_event(UXMetrics.ONBOARDING_COMPLETED)

# On skip:
metrics.track_event(UXMetrics.ONBOARDING_SKIPPED)

# On step abandon (wizard closed mid-flow):
metrics.track_event(
    UXMetrics.ONBOARDING_STEP_ABANDONED,
    {"step": current_step_index}
)
```

**Account switching** (`account_switcher_improved.py`):

```python
metrics.track_event(UXMetrics.ACCOUNT_SWITCHED, {"account_index": idx})
```

**Settings discovery timing** (wrap navigation to a settings page):

```python
metrics.start_task(UXMetrics.SETTINGS_TIME_TO_FIND)
# ... user navigates to desired page ...
metrics.end_task(UXMetrics.SETTINGS_TIME_TO_FIND)
```

#### 2. Expose the dashboard in the About/Settings page (optional)

```python
from zapzap.ui.metrics import MetricsDashboard

# Inside a developer/debug settings section:
dashboard = MetricsDashboard(parent=self)
layout.addWidget(dashboard)
```

---

## 6. Integration Guide

### General Principles

1. **Import design tokens** at the top of any new UI file:
   ```python
   from zapzap.ui.design_tokens import DesignTokens as T
   ```

2. **Use `SettingsManager`** for any persistent state:
   ```python
   from zapzap.services.SettingsManager import SettingsManager
   SettingsManager.set("my/key", value)
   value = SettingsManager.get("my/key", default)
   ```

3. **Use `AccessibilityHelper`** when adding new interactive components:
   ```python
   from zapzap.ui.accessibility import AccessibilityHelper
   AccessibilityHelper.set_name(widget, _("Widget label"))
   AccessibilityHelper.apply_focus_style(widget)
   ```

4. **Track user actions** with `UXMetrics`:
   ```python
   from zapzap.ui.metrics import UXMetrics
   UXMetrics().track_event(UXMetrics.FEATURE_USED, {"feature": "my_feature"})
   ```

5. **Wrap long operations** with `LoadingOverlay`.

6. **Handle empty states** instead of showing a blank area.

### File Naming Conventions

| Purpose | Naming Pattern | Example |
|---------|---------------|---------|
| Reusable component | `lowercase_name.py` | `buttons.py` |
| Feature module | `feature_description.py` | `account_switcher_improved.py` |
| Settings page | `page_<name>.py` (existing) | `page_notifications.py` |

---

## 7. Migration Guide

### Replacing Hardcoded Colors

**Before:**
```python
label.setStyleSheet("color: #25D366; font-size: 14px;")
```

**After:**
```python
from zapzap.ui.design_tokens import DesignTokens as T

label.setStyleSheet(f"color: {T.LIGHT_PRIMARY}; font-size: {T.FONT_SIZE_BODY}px;")
```

For dynamic theming, use `T.get_color("primary", dark_mode=is_dark)`.

### Replacing `QMessageBox` with `ConfirmationDialog`

**Before:**
```python
reply = QMessageBox.question(self, "Remove", "Remove this account?")
if reply == QMessageBox.StandardButton.Yes:
    ...
```

**After:**
```python
from zapzap.ui.components.dialogs import ConfirmationDialog

dlg = ConfirmationDialog(
    title=_("Remove account"),
    message=_("Remove this account?"),
    confirm_text=_("Remove"),
    destructive=True,
    parent=self,
)
if dlg.exec() == ConfirmationDialog.DialogCode.Accepted:
    ...
```

### Replacing Plain `QPushButton` with Design System Buttons

**Before:**
```python
btn = QPushButton("Save")
btn.setStyleSheet("background-color: #25D366; color: white;")
```

**After:**
```python
from zapzap.ui.components.buttons import PrimaryButton

btn = PrimaryButton(_("Save"), parent=self)
```

---

## 8. Timeline

```
Week  1   Design token audit; DesignTokens class written and reviewed
Week  2   Component library (buttons, inputs, cards, dialogs)
Week  3   AccessibilityHelper; accessibility audit of Phase 1 components

Week  4   Settings reorganization (categories, icons, layout)
Week  5   Settings search (widget, debounce, highlight, empty state)
Week  6   Onboarding wizard (3 steps, skip, persistence, keyboard nav)

Week  7   Account switcher redesign (list, badge, add account)
Week  8   Empty states (all contexts) + loading states (spinner, skeleton, overlay)
Week  9   Integration of Phase 3 components into main app; regression testing

Week 10   UXMetrics class (events, timing, persistence, KPIs)
Week 11   MetricsDashboard widget; instrument key flows with tracking calls
Week 12   QA checklists, testing guide, documentation, final accessibility audit
```

---

## 9. Success Metrics

### KPI Targets

| KPI | Baseline | Target | Measurement Method |
|-----|----------|--------|--------------------|
| Settings discovery time | ~ 45 s | ≤ 31.5 s (−30%) | `start_task` / `end_task` around settings navigation |
| Advanced config error rate | ~ 12% | ≤ 9% (−25%) | `ERROR_ENCOUNTERED` / total events |
| Onboarding completion rate | ~ 55% | ≥ 75% (+20 pts) | `ONBOARDING_COMPLETED` / `ONBOARDING_STARTED` |
| UI satisfaction (feature adoption) | ~ 35% | ≥ 50% (+15 pts) | `FEATURE_USED` / total events |
| Notification failure rate | ~ 8% | ≤ 6.4% (−20%) | `NOTIFICATION_FAILED` / total events |

### Review Cadence

| Milestone | Review |
|-----------|--------|
| End of Phase 1 | Internal review; accessibility audit |
| End of Phase 2 | Usability test with 5 participants |
| End of Phase 3 | Usability test with 5 participants; compare to Phase 2 baseline |
| End of Phase 4 | KPI dashboard review; stakeholder presentation |

### Rollback Plan

Each phase is independently reversible:
- Phase 1 (design tokens): Only affects new code that explicitly imports tokens.
  Reverting removes the `ui/` additions with no impact on existing views.
- Phase 2 (settings/onboarding): The new settings dialog is opt-in. The old
  dialog remains in place until explicitly replaced.
- Phase 3 (switcher/empty states): New widgets are additive; old code paths
  remain until explicitly updated.
- Phase 4 (metrics): `UXMetrics` is a passive singleton; removing it requires
  only deleting the instrumentation call-sites.
