# ZapZap UX/UI Improvements

## Executive Summary

This document describes the complete UX/UI improvement initiative for ZapZap,
a WhatsApp desktop client built with PyQt6.  The work was structured into four
phases spanning 12 weeks, targeting measurable improvements in five key areas:

| KPI | Target |
|-----|--------|
| Settings discovery time | −30% |
| Advanced configuration errors | −25% |
| Onboarding completion rate | +20% |
| UI satisfaction | +15% |
| Notification complaint rate | −20% |

All improvements are privacy-respecting, accessible (WCAG AA), and designed to
work seamlessly on both Linux and Windows without external dependencies.

---

## Problem Statement

ZapZap had grown organically over multiple releases.  As new features were added,
several UX pain points emerged:

1. **Settings fragmentation** — Users could not quickly find the setting they
   needed; there was no search capability, and category names were unclear.
2. **No onboarding** — First-time users were dropped directly into the application
   with no guidance on permissions, notifications, or theme preferences.
3. **Inconsistent visual language** — Colors, spacing, and typography were
   specified inline across many files, making it difficult to maintain consistency
   and support themes.
4. **Account switching friction** — Switching between WhatsApp accounts required
   navigating through menus; there was no dedicated, glanceable switcher widget.
5. **Missing feedback states** — Empty screens and long-loading operations
   showed a blank white area with no indication of what was happening.
6. **No metrics** — There was no way to measure whether UX improvements were
   working, making it impossible to prioritize future work.

---

## Solution Overview

The solution was divided into four phases, each building on the previous:

```
Phase 1: Foundation         → Design tokens, shared components, accessibility
Phase 2: Structure & Discovery → Settings reorganization, search, onboarding
Phase 3: High-Impact Flows  → Account switcher, empty states, loading states
Phase 4: Quality & Metrics  → Metrics tracking, dashboards, QA checklists
```

Each phase ships independently and does not break existing functionality.

---

## Phase 1: Foundation

**Goal**: Establish a design system that every other phase can rely on.

### What Was Implemented

#### `zapzap/ui/design_tokens.py` — `DesignTokens`

A single class providing:
- **Color palette**: Full light and dark theme tokens (background, surface,
  primary, secondary, semantic colors for success/warning/error/info).
- **Typography scale**: H1–H3, body, caption, label — sizes and weights.
- **Spacing scale**: XS (4 px) through XXXL (64 px).
- **Border radii**: XS (2 px) through full (9999 px).
- **Animation durations**: Fast (100 ms), Normal (200 ms), Slow (300 ms).
- **Helper methods**: `get_color()`, `get_spacing()`, `qss_color()`, etc.

```python
from zapzap.ui.design_tokens import DesignTokens as T

# Use in a stylesheet
style = f"""
    QPushButton {{
        background-color: {T.LIGHT_PRIMARY};
        color: {T.LIGHT_TEXT_ON_PRIMARY};
        border-radius: {T.RADIUS_MD}px;
        padding: {T.SPACING_SM}px {T.SPACING_MD}px;
    }}
"""
```

#### `zapzap/ui/components/` — Component Library

- **`buttons.py`**: `PrimaryButton`, `SecondaryButton`, `GhostButton`,
  `DangerButton`, `IconButton` — all with hover, pressed, disabled states.
- **`inputs.py`**: `SearchInput`, `LabelledInput`, `TextAreaInput`.
- **`cards.py`**: `CardWidget`, `SelectableCard`.
- **`dialogs.py`**: `ConfirmationDialog`, `InfoDialog`, `BaseDialog`.

#### `zapzap/ui/accessibility.py` — `AccessibilityHelper`

Utilities for:
- Setting accessible names and descriptions
- Focus management (saving and restoring focus)
- Announcing dynamic text changes to screen readers
- Applying the WCAG-compliant focus style to any widget

---

## Phase 2: Structure & Discovery

**Goal**: Help users find settings faster and reduce first-run confusion.

### What Was Implemented

#### `zapzap/ui/settings_reorganized.py` — `SettingsReorganized`

A reorganized settings dialog with:
- Clear category names and icons
- Logical grouping of related options
- Visual hierarchy using design tokens

#### `zapzap/ui/search_settings.py` — `SettingsSearchWidget`

An in-dialog search field that:
- Filters settings categories and individual items in real time
- Highlights matching text in search results
- Shows an empty state with a helpful message when no results are found
- Records `SETTINGS_SEARCH_USED` events to the metrics system

#### `zapzap/ui/onboarding.py` — `OnboardingDialog` + `OnboardingManager`

A 3-step wizard shown on first launch:

| Step | Content |
|------|---------|
| 1 — Permissions | File/folder access, Flatpak notice |
| 2 — Notifications | Desktop notifications, tray icon enable/disable |
| 3 — Preferences | Theme selection, display scale |

Features:
- "Skip" button with "Don't show again" option
- Settings persisted via `SettingsManager`
- Step progress indicator
- Keyboard-navigable throughout
- Records `ONBOARDING_STARTED`, `ONBOARDING_COMPLETED`, `ONBOARDING_SKIPPED`
  events to the metrics system

---

## Phase 3: High-Impact Flows

**Goal**: Remove the two biggest sources of friction: account switching and
blank states.

### What Was Implemented

#### `zapzap/ui/account_switcher_improved.py` — `AccountSwitcherImproved`

A dedicated account-switching widget:
- Shows all accounts with avatar, name, and unread badge
- Active account is visually highlighted
- "Add account" button at the bottom
- Keyboard shortcuts (`Ctrl+Tab` / `Ctrl+Shift+Tab`) for power users
- Accessible: each account item announces name and active status

#### `zapzap/ui/empty_states.py` — `EmptyStateWidget`, `EmptyStateFactory`

Contextual empty-state screens with:
- Illustrative icon
- Headline and descriptive body text
- Optional call-to-action button
- Pre-built states: no accounts, no chats, no search results, loading error,
  no notifications, offline

```python
from zapzap.ui.empty_states import EmptyStateFactory

widget = EmptyStateFactory.no_accounts(parent=self)
# or
widget = EmptyStateFactory.no_search_results("my search term", parent=self)
```

#### `zapzap/ui/loading_states.py` — `LoadingSpinner`, `SkeletonLoader`, `LoadingOverlay`

- `LoadingSpinner`: animated brand-colored spinner
- `SkeletonLoader`: shimmering placeholder matching content shape
- `LoadingOverlay`: full-screen or partial overlay with spinner and message

---

## Phase 4: Quality & Metrics

**Goal**: Measure the impact of phases 1–3 and provide quality assurance tools.

### What Was Implemented

#### `zapzap/ui/metrics.py` — `UXMetrics`, `MetricsDashboard`

See the [Metrics Architecture](#metrics-architecture) section below.

#### `docs/ACCESSIBILITY_CHECKLIST.md`

Complete WCAG AA checklist for ZapZap covering contrast, keyboard navigation,
screen reader compatibility, focus management, touch targets, error handling,
and ZapZap-specific checks.

#### `docs/QA_VISUAL_CHECKLIST.md`

Visual QA checklist for both themes, cross-platform, typography, icons,
spacing, component states, animations, and all ZapZap-specific screens.

#### `docs/TESTING_GUIDE.md`

Comprehensive testing guide with setup instructions, manual test procedures,
accessibility testing tools, cross-platform guide, performance testing,
keyboard navigation testing, usability testing methodology, bug template, and
test scenarios for each feature.

---

## Architecture of the New UI Module

```
zapzap/ui/
├── design_tokens.py          # Single source of truth for colors, spacing, typography
├── accessibility.py          # Accessibility helper utilities
├── metrics.py                # UX metrics tracking (Phase 4)
├── onboarding.py             # First-run onboarding wizard (Phase 2)
├── search_settings.py        # Settings search widget (Phase 2)
├── settings_reorganized.py   # Reorganized settings dialog (Phase 2)
├── account_switcher_improved.py  # Account switcher (Phase 3)
├── empty_states.py           # Empty state components (Phase 3)
├── loading_states.py         # Loading state components (Phase 3)
└── components/
    ├── __init__.py
    ├── buttons.py            # Button variants (Phase 1)
    ├── inputs.py             # Input components (Phase 1)
    ├── cards.py              # Card components (Phase 1)
    └── dialogs.py            # Dialog helpers (Phase 1)
```

### Dependency Graph

```
metrics.py
    ├── SettingsManager (persistence)
    └── design_tokens (styling)

onboarding.py, search_settings.py, account_switcher_improved.py
    ├── SettingsManager
    ├── design_tokens
    └── components/

empty_states.py, loading_states.py
    └── design_tokens

components/*
    └── design_tokens
```

---

## Metrics Architecture

`UXMetrics` is a **singleton** that:

1. Records `MetricsEvent` objects with `event_type`, `timestamp`,
   optional `duration_ms`, and optional `metadata`.
2. Persists all events as JSON via `SettingsManager` so they survive restarts.
3. Provides `get_summary()` for human-readable aggregates.
4. Provides `get_kpis()` to compare current measurements against targets.
5. Is **entirely local** — no network requests, no external services.

```python
from zapzap.ui.metrics import UXMetrics

metrics = UXMetrics()  # Singleton — same instance everywhere

# Track a simple event
metrics.track_event(UXMetrics.SETTINGS_SEARCH_USED, {"term": "notification"})

# Time a task
metrics.start_task("settings_find_notifications")
# ... user navigates ...
duration = metrics.end_task("settings_find_notifications")

# Read KPIs
kpis = metrics.get_kpis()
print(kpis["onboarding_completion_rate"])
# → {"current": 85.0, "target": 20, "achieved": True}
```

---

## Design Principles

### 1. Progressive Disclosure
Show only what users need at each step. Advanced options are available but not
in the way.

### 2. Consistency Over Novelty
All components use `DesignTokens`. No hardcoded colors or sizes outside of
`design_tokens.py`.

### 3. Accessibility First
Every new component is keyboard-navigable, screen-reader-friendly, and meets
WCAG AA contrast requirements.

### 4. Measure, Don't Guess
The metrics system provides objective data to validate every UX decision.
If a feature isn't improving a KPI, we know.

### 5. Privacy by Design
Metrics are stored locally using `QSettings`. Nothing is ever transmitted.

---

## Future Improvements

| Area | Idea | Priority |
|------|------|----------|
| Metrics | Export to clipboard as Markdown table | Low |
| Onboarding | Add a "What's new" step for updates | Medium |
| Search | Fuzzy search / typo tolerance | Medium |
| Account switcher | Drag-to-reorder accounts | Low |
| Accessibility | Automated WCAG contrast test on startup | High |
| Performance | Lazy-load settings pages | Medium |
| Metrics | A/B test two onboarding flows | High |
| Theming | Custom accent color picker | Low |
