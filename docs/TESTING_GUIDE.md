# ZapZap Testing Guide

This guide covers how to set up a development environment, run the application,
and manually test every major feature of ZapZap — including the new UX
improvements introduced in Phases 1–4.

---

## Table of Contents

1. [Development Environment Setup](#1-development-environment-setup)
2. [Running the Application](#2-running-the-application)
3. [Manual Testing Procedures](#3-manual-testing-procedures)
4. [Accessibility Testing](#4-accessibility-testing)
5. [Cross-Platform Testing](#5-cross-platform-testing)
6. [Performance Testing](#6-performance-testing)
7. [Keyboard Navigation Testing](#7-keyboard-navigation-testing)
8. [Usability Testing Methodology](#8-usability-testing-methodology)
9. [Bug Reporting Template](#9-bug-reporting-template)
10. [Test Scenarios by Feature](#10-test-scenarios-by-feature)

---

## 1. Development Environment Setup

### Prerequisites

| Tool | Minimum Version | Notes |
|------|-----------------|-------|
| Python | 3.11 | 3.12 recommended |
| PyQt6 | 6.5 | `pip install PyQt6` |
| PyQt6-WebEngine | 6.5 | `pip install PyQt6-WebEngine` |
| pip | 23+ | `python -m pip install --upgrade pip` |

### Clone and Install

```bash
git clone https://github.com/rafatosta/zapzap.git
cd zapzap
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt
pip install -e .
```

### Verify Installation

```bash
python -c "from zapzap.ui.design_tokens import DesignTokens; print('OK')"
python -c "from zapzap.ui.metrics import UXMetrics; print('OK')"
```

---

## 2. Running the Application

### Direct Run (development mode)

```bash
python run.py
```

### Flatpak (Linux production build)

```bash
flatpak-builder --user --install --force-clean build-dir com.rtosta.zapzap.yaml
flatpak run com.rtosta.zapzap
```

### Environment Variables for Testing

| Variable | Value | Effect |
|----------|-------|--------|
| `ZAPZAP_DEBUG` | `1` | Enables debug logging |
| `QT_SCALE_FACTOR` | `1.5` | Test HiDPI scaling |
| `QT_ACCESSIBILITY` | `1` | Enable Qt accessibility debug |
| `QT_QPA_PLATFORM` | `xcb` / `wayland` | Force display backend |

Example:
```bash
ZAPZAP_DEBUG=1 QT_SCALE_FACTOR=1.5 python run.py
```

---

## 3. Manual Testing Procedures

### 3.1 First Launch (Onboarding)

1. Clear stored settings to simulate first run:
   ```bash
   # Linux: Settings stored in ~/.config/zapzap/
   rm -rf ~/.config/zapzap/
   ```
2. Launch the application.
3. Verify the onboarding wizard appears automatically.
4. Complete each step and verify settings are persisted.
5. Restart the application — wizard should NOT reappear.
6. Repeat steps 1–2, then click "Skip" on the wizard.
7. Verify the skip preference is remembered.

### 3.2 Settings Dialog

1. Open Settings (menu or keyboard shortcut `Ctrl+,`).
2. Navigate each of the 8 categories and verify content loads.
3. Change a setting value, close, reopen — verify persistence.
4. Use the search field to find "notification" — verify relevant results.
5. Clear the search — verify all categories reappear.
6. Search for a term with no results — verify empty state is shown.

### 3.3 Account Switcher

1. Open the account switcher (sidebar or menu).
2. If only one account: verify the switcher shows a single entry and an "Add account" option.
3. Add a second WhatsApp account.
4. Switch between accounts — verify the active tab changes.
5. Verify no data bleeds between accounts.
6. Remove an account and verify the UI updates correctly.

### 3.4 Notifications

1. Navigate to Settings > Notifications.
2. Toggle each notification type off/on; confirm changes apply.
3. Verify a test notification appears when permission is granted.
4. Disable notifications at the OS level; verify ZapZap handles this gracefully.

### 3.5 Theme Switching

1. Navigate to Settings > Appearance.
2. Switch from Light → Dark → Auto (system).
3. Verify the UI updates immediately each time.
4. In "Auto" mode, change the OS theme and verify ZapZap follows.

### 3.6 Metrics Dashboard

1. Open the Metrics Dashboard (Settings > About, or development shortcut).
2. Verify KPI progress bars render without errors.
3. Click "Refresh" — verify the summary updates.
4. Click "Export JSON" — verify a file is saved with valid JSON.
5. Click "Reset Metrics" — confirm the dialog, verify counts reset to zero.

---

## 4. Accessibility Testing

### 4.1 Automated Contrast Check

Use the WebAIM Contrast Checker or browser DevTools to verify:

| Pair | Ratio Required | ZapZap Values |
|------|----------------|---------------|
| Body text / Light bg | 4.5:1 | `#111B21` / `#FFFFFF` |
| Body text / Dark bg | 4.5:1 | `#E9EDF0` / `#111B21` |
| Secondary text / Light bg | 4.5:1 | `#667781` / `#FFFFFF` |
| Primary button text | 4.5:1 | `#FFFFFF` / `#25D366` |

### 4.2 Screen Reader Testing (Linux)

```bash
# Install and launch Orca
sudo apt install gnome-orca
orca &

# Then launch ZapZap
python run.py
```

Walk through:
- Main window navigation
- Opening and navigating Settings
- Using the account switcher
- Completing onboarding

Listen for:
- Correct role announcements (button, checkbox, list item)
- State announcements (checked, unchecked, selected)
- Dynamic content updates (search results, errors)

### 4.3 Qt Accessibility Inspector

```bash
# Enable Qt's built-in accessibility debug output
QT_ACCESSIBILITY=1 python run.py 2>&1 | grep -i "accessible"
```

### 4.4 Keyboard-Only Navigation

See [Section 7](#7-keyboard-navigation-testing).

### 4.5 High-Contrast Mode

```bash
# GNOME: enable high contrast
gsettings set org.gnome.desktop.interface gtk-theme 'HighContrast'
python run.py
# Verify no content is invisible against high-contrast backgrounds
```

### 4.6 Large Font Test

```bash
QT_FONT_DPI=144 python run.py   # Simulates ~150% font scale
```

Verify:
- No text is clipped or truncated incorrectly
- No buttons become too small
- All dialogs remain usable

---

## 5. Cross-Platform Testing

### 5.1 Linux

| Desktop Environment | Compositor | Notes |
|--------------------|-----------|-------|
| GNOME (X11) | Mutter | Primary target |
| GNOME (Wayland) | Mutter | `QT_QPA_PLATFORM=wayland` |
| KDE Plasma (X11) | KWin | Test Qt theming integration |
| KDE Plasma (Wayland) | KWin | `QT_QPA_PLATFORM=wayland` |
| XFCE | Xfwm4 | Check tray icon |

Test checklist for each:
- [ ] Window opens and renders correctly
- [ ] Tray icon appears and is functional
- [ ] Notifications display correctly
- [ ] Theme follows system preference in "Auto" mode

### 5.2 Windows

Minimum: Windows 10 22H2  
Recommended: Windows 11

```powershell
# Install dependencies on Windows
pip install PyQt6 PyQt6-WebEngine
python run.py
```

Test checklist:
- [ ] Font rendering uses DirectWrite (no blurriness)
- [ ] DPI scaling at 100%, 125%, 150%, 200%
- [ ] System tray icon appears
- [ ] Notifications use Windows notification center

### 5.3 Flatpak Sandbox

```bash
# Build and install locally
flatpak-builder --user --install --force-clean build/ com.rtosta.zapzap.yaml

# Run with sandbox
flatpak run com.rtosta.zapzap

# Run with verbose sandbox logging
flatpak run --log-session-bus com.rtosta.zapzap
```

Verify permissions are correctly declared in the manifest.

---

## 6. Performance Testing

### 6.1 Startup Time

```bash
time python run.py &
# Measure time until main window is visible
```

Target: < 3 seconds on modern hardware.

### 6.2 Settings Search Latency

1. Open Settings search.
2. Type rapidly (simulate a fast typist).
3. Verify results appear within 100 ms of stopping typing (debounce).
4. No UI freeze during search.

### 6.3 Account Switching Latency

1. Switch between two accounts rapidly.
2. Verify switching completes within 500 ms.
3. No blank white screens during transition.

### 6.4 Memory Usage

```bash
# Monitor memory while using the app
watch -n1 "ps aux | grep zapzap | grep -v grep"
```

Baseline: ~200 MB for a single account.  
Threshold: < 400 MB for two accounts after 30 minutes of use.

### 6.5 WebEngine Performance

1. Load a chat with many media items.
2. Scroll rapidly.
3. Verify no frame drops or renderer crashes.

---

## 7. Keyboard Navigation Testing

### Procedure

1. Disconnect or disable the mouse.
2. Launch the application.
3. Use only keyboard to complete each scenario below.

### Key Bindings Reference

| Key | Action |
|-----|--------|
| `Tab` | Next focusable element |
| `Shift+Tab` | Previous focusable element |
| `Enter` / `Space` | Activate button / toggle checkbox |
| `Arrow keys` | Navigate within lists, sliders, radio groups |
| `Escape` | Close dialog / cancel |
| `Ctrl+,` | Open Settings |
| `Ctrl+Tab` | Next account tab |
| `Ctrl+Shift+Tab` | Previous account tab |

### Test Scenarios

**Scenario K-1: Navigate to Settings and change a value**
1. Press `Ctrl+,` — Settings should open.
2. `Tab` to the search field.
3. Type "notification".
4. `Tab` to the first result.
5. Press `Enter` to navigate to the Notifications page.
6. `Tab` to a toggle switch.
7. Press `Space` to toggle.
8. Press `Escape` to close Settings.

**Scenario K-2: Switch accounts**
1. Press `Ctrl+Tab` — next account should become active.
2. Press `Ctrl+Shift+Tab` — previous account should become active.

**Scenario K-3: Complete onboarding without mouse**
1. Clear settings to trigger onboarding.
2. Launch app — onboarding wizard opens; focus should be inside.
3. `Tab` to "Next" button, press `Enter`.
4. Complete all steps without using the mouse.

---

## 8. Usability Testing Methodology

### Participant Recruitment

- 5–8 participants for each usability study
- Mix of WhatsApp power users and occasional users
- At least 1 participant with a disability or accessibility need

### Test Protocol

1. **Briefing (5 min)**: Explain the session, remind participants to think aloud.
2. **Warm-up (5 min)**: Ask participant to describe their typical WhatsApp use.
3. **Task scenarios (20–30 min)**: Present tasks one at a time, do not assist.
4. **Debrief (10 min)**: Ask about frustrations, surprises, and suggestions.

### Scenario Tasks

| # | Task | KPI |
|---|------|-----|
| 1 | "Find the notification settings and turn off message previews." | Settings discovery time |
| 2 | "Add a second WhatsApp account." | Onboarding / account switcher |
| 3 | "Change the application theme to dark mode." | Settings discovery |
| 4 | "Find the keyboard shortcuts list." | Feature discoverability |

### Metrics to Collect

- **Task completion rate**: % of participants who complete the task unaided
- **Time on task**: seconds from task start to completion
- **Error count**: number of incorrect actions before success
- **Satisfaction rating**: post-task 1–7 Likert scale

### Success Criteria

| Metric | Target |
|--------|--------|
| Task completion rate | ≥ 90% |
| Avg. settings discovery time | < 30 seconds |
| Onboarding completion rate | ≥ 80% |
| Post-task satisfaction | ≥ 5.5 / 7 |

---

## 9. Bug Reporting Template

When filing a bug, include all fields below.

```
**Title**: [Component] Brief description of the issue

**Environment**
- OS: (e.g., Ubuntu 24.04, Windows 11 23H2)
- Desktop Environment: (e.g., GNOME 46 on Wayland)
- ZapZap version: (e.g., 3.8.1)
- Python version: (e.g., 3.12.3)
- PyQt6 version: (e.g., 6.7.0)
- Installation method: (Flatpak / pip / source)

**Steps to Reproduce**
1. 
2. 
3. 

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens. Include screenshots or screen recordings if possible.

**Accessibility Impact**
Does this issue affect keyboard navigation, screen readers, or contrast?

**Severity**
- [ ] Critical (app crash / data loss)
- [ ] High (feature unusable)
- [ ] Medium (workaround available)
- [ ] Low (cosmetic / minor)

**Additional Context**
Paste relevant log output here (if ZAPZAP_DEBUG=1):
```

---

## 10. Test Scenarios by Feature

### 10.1 Onboarding Wizard

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| ONB-01 | First launch with no stored settings | Wizard opens automatically |
| ONB-02 | Complete all 3 steps | Settings persisted; wizard not shown again |
| ONB-03 | Click "Skip" on step 1 | Wizard dismissed; skip preference stored |
| ONB-04 | Click "Don't show again" | Wizard never shown on subsequent launches |
| ONB-05 | Resize window during wizard | Layout adapts; no content overflow |
| ONB-06 | Complete wizard with keyboard only | All steps completable without mouse |
| ONB-07 | Screen reader: step progress | "Step N of 3" announced on each step |

### 10.2 Settings Search

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| SRH-01 | Search "notification" | Notification-related items shown |
| SRH-02 | Search with uppercase "THEME" | Case-insensitive match works |
| SRH-03 | Search non-existent term "zzz" | Empty state shown with helpful message |
| SRH-04 | Clear search field | All categories restored |
| SRH-05 | Search and click a result | Navigates to the correct settings page |
| SRH-06 | Rapid typing in search field | Debounce prevents excessive updates |
| SRH-07 | Search result count announced | Screen reader hears number of results |

### 10.3 Account Switcher

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| ACC-01 | Single account | Switcher shows one account + "Add account" |
| ACC-02 | Add second account | Account appears in switcher |
| ACC-03 | Switch to second account | WebEngine shows second account's WhatsApp |
| ACC-04 | Switch back to first | First account's data restored correctly |
| ACC-05 | Remove an account | Account removed; first account becomes active |
| ACC-06 | Keyboard switch with `Ctrl+Tab` | Accounts cycle correctly |
| ACC-07 | Account name announced by screen reader | Screen reader reads account name and status |

### 10.4 UX Metrics

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| MET-01 | Open Metrics Dashboard | KPI bars render without errors |
| MET-02 | Perform 10 settings searches | "settings_searches" count increases to 10 |
| MET-03 | Start and end a timed task | Duration recorded in events |
| MET-04 | Export JSON | Valid JSON file saved to disk |
| MET-05 | Reset metrics | All counts return to zero |
| MET-06 | Restart app after tracking events | Events are persisted and reloaded |
| MET-07 | `get_kpis()` with zero events | Returns valid dict without division errors |
