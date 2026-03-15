# ZapZap Design System

The ZapZap design system provides a single source of truth for all visual
decisions in the application.  It is implemented in
`zapzap/ui/design_tokens.py` as the `DesignTokens` class.

---

## 1. Color Palette

### Light Theme

| Token | Hex | Usage |
|-------|-----|-------|
| `LIGHT_PRIMARY` | `#25D366` | Primary buttons, active indicators, focus rings |
| `LIGHT_PRIMARY_HOVER` | `#1EBE59` | Primary button hover state |
| `LIGHT_PRIMARY_PRESSED` | `#17A34A` | Primary button pressed state |
| `LIGHT_PRIMARY_TEXT` | `#FFFFFF` | Text on primary-colored backgrounds |
| `LIGHT_SECONDARY` | `#128C7E` | Secondary accents, links |
| `LIGHT_SECONDARY_HOVER` | `#0D7A6D` | Secondary hover |
| `LIGHT_SECONDARY_PRESSED` | `#0A6559` | Secondary pressed |
| `LIGHT_BACKGROUND` | `#FFFFFF` | Main window background |
| `LIGHT_BACKGROUND_ALT` | `#F7F8FA` | Alternate row backgrounds |
| `LIGHT_SURFACE` | `#FFFFFF` | Card surfaces |
| `LIGHT_SURFACE_RAISED` | `#F0F2F5` | Elevated surface (toolbar, sidebar) |
| `LIGHT_SURFACE_OVERLAY` | `#EDEFF2` | Hover / active overlay on surfaces |
| `LIGHT_BORDER` | `#D0D4D8` | Default borders |
| `LIGHT_BORDER_STRONG` | `#A0A8B0` | Emphasized borders |
| `LIGHT_BORDER_FOCUS` | `#25D366` | Focus ring color |
| `LIGHT_TEXT_PRIMARY` | `#111B21` | Primary body text |
| `LIGHT_TEXT_SECONDARY` | `#667781` | Secondary / supporting text |
| `LIGHT_TEXT_DISABLED` | `#A6AEB6` | Disabled control labels |
| `LIGHT_TEXT_ON_PRIMARY` | `#FFFFFF` | Text on primary-colored backgrounds |
| `LIGHT_INPUT_BG` | `#FFFFFF` | Input field background |
| `LIGHT_INPUT_BORDER` | `#D0D4D8` | Input field border |
| `LIGHT_INPUT_BORDER_FOCUS` | `#25D366` | Input focus border |
| `LIGHT_CARD_BG` | `#FFFFFF` | Card background |
| `LIGHT_CARD_BORDER` | `#E8ECF0` | Card border |
| `LIGHT_CARD_SHADOW` | `rgba(0,0,0,0.08)` | Card drop shadow |
| `LIGHT_SCROLLBAR_BG` | `#F0F2F5` | Scrollbar track |
| `LIGHT_SCROLLBAR_HANDLE` | `#C1C7CE` | Scrollbar thumb |
| `LIGHT_SCROLLBAR_HANDLE_HOVER` | `#A0A8B0` | Scrollbar thumb hover |

### Dark Theme

| Token | Hex | Usage |
|-------|-----|-------|
| `DARK_PRIMARY` | `#25D366` | Same primary — brand color is theme-invariant |
| `DARK_PRIMARY_HOVER` | `#1EBE59` | Primary hover |
| `DARK_PRIMARY_PRESSED` | `#17A34A` | Primary pressed |
| `DARK_SECONDARY` | `#00BFA5` | Secondary accents (teal, slightly lighter than light theme) |
| `DARK_SECONDARY_HOVER` | `#00A896` | Secondary hover |
| `DARK_SECONDARY_PRESSED` | `#009183` | Secondary pressed |
| `DARK_BACKGROUND` | `#111B21` | Main background |
| `DARK_BACKGROUND_ALT` | `#1A2530` | Alternate rows |
| `DARK_SURFACE` | `#1E2A33` | Card / panel surfaces |
| `DARK_SURFACE_RAISED` | `#2A3942` | Elevated surfaces |
| `DARK_SURFACE_OVERLAY` | `#374854` | Hover / active overlay |
| `DARK_BORDER` | `#2A3942` | Default borders |
| `DARK_BORDER_STRONG` | `#3B4A54` | Strong borders |
| `DARK_BORDER_FOCUS` | `#25D366` | Focus ring (same as light) |
| `DARK_TEXT_PRIMARY` | `#E9EDF0` | Primary text |
| `DARK_TEXT_SECONDARY` | `#8696A0` | Secondary text |
| `DARK_TEXT_DISABLED` | `#4A5568` | Disabled text |
| `DARK_INPUT_BG` | `#2A3942` | Input background |
| `DARK_INPUT_BORDER` | `#374854` | Input border |
| `DARK_CARD_BG` | `#1E2A33` | Card background |
| `DARK_CARD_BORDER` | `#2A3942` | Card border |
| `DARK_CARD_SHADOW` | `rgba(0,0,0,0.3)` | Stronger shadow for dark mode |

### Semantic Colors (Theme-Independent)

| Token | Hex | Usage |
|-------|-----|-------|
| `COLOR_SUCCESS` | `#25D366` | Success indicators |
| `COLOR_SUCCESS_BG_LIGHT` | `#DCFCE7` | Success background — light theme |
| `COLOR_SUCCESS_BG_DARK` | `#1A3A2A` | Success background — dark theme |
| `COLOR_WARNING` | `#F59E0B` | Warnings |
| `COLOR_WARNING_BG_LIGHT` | `#FEF3C7` | Warning background — light |
| `COLOR_WARNING_BG_DARK` | `#3A2D10` | Warning background — dark |
| `COLOR_ERROR` | `#EF4444` | Errors, destructive actions |
| `COLOR_ERROR_BG_LIGHT` | `#FEE2E2` | Error background — light |
| `COLOR_ERROR_BG_DARK` | `#3A1414` | Error background — dark |
| `COLOR_INFO` | `#3B82F6` | Informational messages |
| `COLOR_INFO_BG_LIGHT` | `#DBEAFE` | Info background — light |
| `COLOR_INFO_BG_DARK` | `#1A2A4A` | Info background — dark |

---

## 2. Typography Scale

| Token | Size (px) | Weight | Line Height | Usage |
|-------|-----------|--------|-------------|-------|
| `FONT_SIZE_H1` | 24 | 700 (`BOLD`) | 1.2 | Page titles, major headings |
| `FONT_SIZE_H2` | 20 | 700 (`BOLD`) | 1.3 | Section headings |
| `FONT_SIZE_H3` | 16 | 600 (`SEMIBOLD`) | 1.4 | Sub-section headings, card titles |
| `FONT_SIZE_BODY` | 14 | 400 (`REGULAR`) | 1.5 | Body text, descriptions |
| `FONT_SIZE_CAPTION` | 12 | 400 (`REGULAR`) | 1.4 | Captions, helper text, timestamps |
| `FONT_SIZE_LABEL` | 11 | 500 (`MEDIUM`) | 1.3 | Input labels, badges |

**Font family**: `system-ui, -apple-system, sans-serif`  
(Falls back to the best system UI font on each platform.)

### Usage in QSS

```python
from zapzap.ui.design_tokens import DesignTokens as T

style = f"""
    QLabel#title {{
        font-size: {T.FONT_SIZE_H1}px;
        font-weight: {T.FONT_WEIGHT_BOLD};
    }}
    QLabel#description {{
        font-size: {T.FONT_SIZE_BODY}px;
        font-weight: {T.FONT_WEIGHT_REGULAR};
        color: {T.LIGHT_TEXT_SECONDARY};
    }}
"""
```

---

## 3. Spacing System

All spacing values are in pixels and follow a scale:

| Token | Value (px) | Common Usage |
|-------|-----------|--------------|
| `SPACING_XS` | 4 | Icon gap, tight component padding |
| `SPACING_SM` | 8 | Button icon gap, small section gaps |
| `SPACING_10` | 10 | Slight extra gap |
| `SPACING_12` | 12 | Medium-small padding |
| `SPACING_MD` | 16 | Default content padding, form field gap |
| `SPACING_20` | 20 | Section padding |
| `SPACING_LG` | 24 | Dialog content margin, between sections |
| `SPACING_XL` | 32 | Large section spacing |
| `SPACING_40` | 40 | Extra-large gaps |
| `SPACING_XXL` | 48 | Hero section padding |
| `SPACING_XXXL` | 64 | Maximum content padding |

### Usage in Python

```python
from zapzap.ui.design_tokens import DesignTokens as T

layout = QVBoxLayout()
layout.setSpacing(T.SPACING_MD)          # 16 px between items
layout.setContentsMargins(
    T.SPACING_LG, T.SPACING_LG,          # 24 px on all sides
    T.SPACING_LG, T.SPACING_LG
)
```

---

## 4. Border Radius

| Token | Value (px) | Usage |
|-------|-----------|-------|
| `RADIUS_XS` | 2 | Very subtle rounding (badges) |
| `RADIUS_SM` | 4 | Inputs, small chips |
| `RADIUS_MD` | 8 | Buttons, cards, inputs (default) |
| `RADIUS_LG` | 12 | Dialogs, larger cards |
| `RADIUS_XL` | 16 | Hero cards, onboarding panels |
| `RADIUS_FULL` | 9999 | Pill buttons, avatars, tags |

---

## 5. Shadows

Qt does not natively support CSS `box-shadow`, but shadows are documented here
for reference in custom painting or drop-shadow effects:

| Token | Value | Usage |
|-------|-------|-------|
| `SHADOW_SM` | `0 1px 2px rgba(0,0,0,0.08)` | Subtle card elevation |
| `SHADOW_MD` | `0 4px 6px rgba(0,0,0,0.10)` | Standard card / dialog shadow |
| `SHADOW_LG` | `0 10px 15px rgba(0,0,0,0.12)` | Floating panels, popovers |

---

## 6. Animation Durations

| Token | Value (ms) | Usage |
|-------|-----------|-------|
| `ANIM_FAST` | 100 | Hover state color transitions |
| `ANIM_NORMAL` | 200 | Standard transitions (dialogs, panels) |
| `ANIM_SLOW` | 300 | Page-level transitions, sliding panels |

```python
from PyQt6.QtCore import QPropertyAnimation

anim = QPropertyAnimation(widget, b"geometry")
anim.setDuration(T.ANIM_NORMAL)  # 200 ms
```

---

## 7. Dark / Light Theme Guide

### Detecting the Current Theme

```python
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette

def is_dark_mode() -> bool:
    palette = QApplication.instance().palette()
    window_color = palette.color(QPalette.ColorRole.Window)
    # Luminance threshold: dark if lightness < 0.5
    return window_color.lightness() < 128
```

### Applying the Correct Token

```python
dark = is_dark_mode()
bg = T.DARK_BACKGROUND if dark else T.LIGHT_BACKGROUND
text = T.DARK_TEXT_PRIMARY if dark else T.LIGHT_TEXT_PRIMARY

# Or use the helper:
bg = T.get_color("background", dark_mode=dark)
text = T.get_color("text_primary", dark_mode=dark)
```

### Using `get_color()` with Token Names

The `DesignTokens.get_color(token, dark_mode)` method accepts short token names
from the color maps built by `_build_maps()`:

```python
T.get_color("primary")           # → "#25D366"
T.get_color("background", True)  # → "#111B21" (dark)
T.get_color("error_bg", True)    # → "#3A1414" (dark)
```

---

## 8. Component Inventory

| Component | File | Description |
|-----------|------|-------------|
| `PrimaryButton` | `components/buttons.py` | Main CTA button |
| `SecondaryButton` | `components/buttons.py` | Outlined secondary action |
| `GhostButton` | `components/buttons.py` | Text-only button |
| `DangerButton` | `components/buttons.py` | Destructive action |
| `IconButton` | `components/buttons.py` | Icon-only button with tooltip |
| `SearchInput` | `components/inputs.py` | Search field with icon |
| `LabelledInput` | `components/inputs.py` | Input with floating label |
| `TextAreaInput` | `components/inputs.py` | Multi-line text input |
| `CardWidget` | `components/cards.py` | Basic content card |
| `SelectableCard` | `components/cards.py` | Clickable/selectable card |
| `ConfirmationDialog` | `components/dialogs.py` | Yes/No confirm dialog |
| `InfoDialog` | `components/dialogs.py` | Information / OK dialog |
| `EmptyStateWidget` | `empty_states.py` | Empty state with icon + CTA |
| `LoadingSpinner` | `loading_states.py` | Animated brand spinner |
| `SkeletonLoader` | `loading_states.py` | Shimmer skeleton placeholder |
| `LoadingOverlay` | `loading_states.py` | Full-area loading overlay |
| `UXMetrics` | `metrics.py` | Singleton metrics tracker |
| `MetricsDashboard` | `metrics.py` | Metrics visualization widget |
