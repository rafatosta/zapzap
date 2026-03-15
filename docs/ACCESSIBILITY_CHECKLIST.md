# ZapZap Accessibility Checklist (WCAG AA)

This checklist covers Web Content Accessibility Guidelines (WCAG) 2.1 Level AA
requirements as applied to the ZapZap desktop application (PyQt6 / Qt6).

All items must be verified before each major release.

---

## 1. Color & Contrast

### Text Contrast (WCAG 1.4.3 — AA requires 4.5:1 for normal text, 3:1 for large text)

- [ ] Primary body text (`#111B21` on `#FFFFFF`) meets 4.5:1 — Light theme
- [ ] Secondary text (`#667781` on `#FFFFFF`) meets 4.5:1 — Light theme
- [ ] Primary body text (`#E9EDF0` on `#111B21`) meets 4.5:1 — Dark theme
- [ ] Secondary text (`#8696A0` on `#111B21`) meets 4.5:1 — Dark theme
- [ ] Disabled text is visually distinct but does not need to meet contrast requirements
- [ ] Error messages (`#EF4444` on white) meet 4.5:1
- [ ] Warning messages (`#F59E0B` on white) meet 4.5:1
- [ ] Placeholder text in inputs is sufficiently contrasted (3:1 minimum)
- [ ] Text on primary green background (`#FFFFFF` on `#25D366`) meets 4.5:1

### UI Component Contrast (WCAG 1.4.11 — 3:1 for non-text UI components)

- [ ] Input borders meet 3:1 against their background
- [ ] Focus rings are clearly visible (3:1 minimum)
- [ ] Button outlines / boundaries meet 3:1
- [ ] Progress bar fill vs background meets 3:1
- [ ] Tab active indicator meets 3:1
- [ ] Icons used as the sole conveyors of information meet 3:1

### Color Independence (WCAG 1.4.1)

- [ ] Error state is not communicated by color alone (icon or text label also present)
- [ ] Success state is not communicated by color alone
- [ ] Required field indicators use more than color (e.g., asterisk + tooltip)
- [ ] Active/selected states use a shape or text cue in addition to color

---

## 2. Keyboard Navigation (WCAG 2.1.1, 2.1.2)

### General

- [ ] All interactive controls are reachable via `Tab` key
- [ ] Tab order is logical and follows visual layout (left-to-right, top-to-bottom)
- [ ] No keyboard trap: pressing `Tab` or `Escape` always moves focus out of any component
- [ ] Keyboard shortcuts are documented and do not conflict with OS/screen reader shortcuts
- [ ] `Shift+Tab` reverses focus order correctly

### Main Window

- [ ] Sidebar/tray menu is keyboard accessible
- [ ] Account switcher can be opened and navigated entirely by keyboard
- [ ] Switching between accounts with `Enter` / `Space` works correctly
- [ ] All toolbar buttons reachable via `Tab`

### Settings

- [ ] Settings dialog opens with keyboard (e.g., via menu keyboard shortcut)
- [ ] Settings search field is reachable via `Tab` from dialog open
- [ ] Settings categories can be navigated with arrow keys
- [ ] Toggling checkboxes works with `Space`
- [ ] Sliders respond to arrow keys (`Left`/`Right`, `Up`/`Down`)
- [ ] Dropdowns open with `Enter` / `Space` and navigate with arrow keys
- [ ] Settings dialog closes with `Escape`

### Dialogs & Modals

- [ ] Focus moves into dialog/modal when it opens
- [ ] Focus is trapped inside modal while it is open
- [ ] Focus returns to the triggering element when dialog closes
- [ ] Confirmation dialogs default focus to the safe action (Cancel)

### Onboarding Wizard

- [ ] "Next" and "Back" buttons are keyboard accessible
- [ ] "Skip" link is reachable via keyboard
- [ ] Radio buttons navigate with arrow keys within a group
- [ ] Checkboxes toggle with `Space`

---

## 3. Focus Management (WCAG 2.4.3, 2.4.7)

- [ ] All focusable elements show a clearly visible focus indicator (not removed via CSS)
- [ ] Focus indicator uses the brand focus color `#25D366` (3:1 contrast guaranteed by design)
- [ ] Focus is programmatically managed when views change (e.g., page navigation sets focus to heading)
- [ ] Transient notifications / toasts do not steal focus
- [ ] After closing a toast or banner, focus returns to the last focused element

---

## 4. Screen Reader Compatibility (WCAG 4.1.2)

### Roles & Properties

- [ ] All buttons have accessible names (text label or `setAccessibleName`)
- [ ] Icon-only buttons have `setAccessibleDescription` explaining the action
- [ ] Form inputs have associated labels (via `setAccessibleName` or buddy label)
- [ ] Radio button groups have a group label
- [ ] Checkboxes communicate their checked state to assistive technology
- [ ] Progress bars announce value changes via `setAccessibleName`
- [ ] Status updates (e.g., "Settings saved") are announced via live regions

### Images & Icons

- [ ] Decorative icons have empty accessible names (Qt: `setAccessibleName("")`)
- [ ] Informational icons describe their meaning in accessible name
- [ ] Avatar images have the user's name as alt text

### Dynamic Content

- [ ] Search results in settings search are announced when they change
- [ ] Error messages are announced immediately when they appear
- [ ] Loading indicators announce start and completion

---

## 5. Touch Targets (WCAG 2.5.5 — recommended 44×44 px minimum)

- [ ] All clickable buttons are at least 44×44 px
- [ ] Account switcher list items are at least 44 px tall
- [ ] Settings list items are at least 44 px tall
- [ ] Close buttons (×) on dialogs are at least 44×44 px
- [ ] Notification dismiss buttons meet minimum touch target size
- [ ] Slider drag handles are at least 44×44 px

---

## 6. Error Identification (WCAG 3.3.1, 3.3.2, 3.3.3)

- [ ] Form errors are described in text (not color alone)
- [ ] Error messages appear adjacent to the relevant field
- [ ] Error messages are specific (e.g., "Password must be at least 8 characters")
- [ ] Required fields are marked and the requirement is explained before the form
- [ ] Suggestions for correcting input errors are provided where possible
- [ ] On submission failure, focus moves to the first error

---

## 7. Form Labels & Instructions (WCAG 1.3.1, 3.3.2)

- [ ] Every input field has a visible label
- [ ] Labels are not replaced by placeholder text alone
- [ ] Input purpose can be programmatically determined (WCAG 1.3.5)
- [ ] Instructions appear before the control they relate to
- [ ] Group labels exist for related controls (radio groups, checkboxes)

---

## 8. Link & Button Purposes (WCAG 2.4.6, 2.4.4)

- [ ] Every button label describes the action (not just "Click here" or "OK")
- [ ] Duplicate button labels in different contexts have distinguishable accessible names
- [ ] "Learn more" or ambiguous links include context in their accessible name

---

## 9. Text Resize & Zoom (WCAG 1.4.4)

- [ ] Text can be resized up to 200% without loss of content or functionality
- [ ] UI layouts reflow or scroll correctly at large font sizes
- [ ] Application respects system-wide font size preferences

---

## 10. ZapZap-Specific Checks

### Main Window & Chat View

- [ ] WhatsApp web content is loaded in a web engine — note: web content
      accessibility depends on WhatsApp's own implementation
- [ ] Application chrome (menus, toolbars) is fully accessible
- [ ] Keyboard shortcut to switch accounts is documented in Help/Shortcuts dialog

### Settings (Settings Reorganized + Search)

- [ ] Settings search field announces number of results found
- [ ] No-results state communicates "no results found" to screen readers
- [ ] Category navigation announces the active category name on focus

### Account Switcher

- [ ] Each account item announces: account name + active/inactive status
- [ ] "Add account" button has descriptive accessible name
- [ ] Account switcher dropdown closes with `Escape`

### Notifications

- [ ] Notification permission prompt explains what permissions are requested
- [ ] Tray icon has an accessible name ("ZapZap — N unread messages")
- [ ] Do-not-disturb toggle state is announced

### Onboarding

- [ ] Step progress is announced ("Step 2 of 3")
- [ ] "Skip" and "Don't show again" options are clearly labelled

---

## 11. Testing Procedures

### Automated

1. Run `axe-core` or `Accessibility Inspector` (macOS) against the rendered window.
2. Check color contrast with [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/).
3. Use `Qt Accessibility Inspector` (`QT_ACCESSIBILITY=1`) to inspect widget tree.

### Manual — Keyboard

1. Unplug/disable mouse.
2. Open ZapZap and navigate every feature using `Tab`, `Shift+Tab`, `Enter`, `Space`, `Escape`, arrow keys.
3. Confirm focus indicator is always visible.
4. Confirm no keyboard traps exist.

### Manual — Screen Reader

1. **Linux**: Enable Orca (`orca -r`) and navigate the application.
2. **Windows (if tested)**: Enable Narrator or NVDA.
3. Confirm all controls are announced with correct role, name, and state.
4. Confirm dynamic updates (search results, errors) are announced.

### Manual — High Contrast & Large Font

1. Enable system high-contrast mode.
2. Increase system font size to 150% and 200%.
3. Confirm no content is clipped or overlapping.
