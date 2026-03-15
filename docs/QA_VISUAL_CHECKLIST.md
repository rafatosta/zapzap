# ZapZap QA Visual Checklist

Use this checklist during QA cycles before each release.  
Testers should verify each item on both Linux (Flatpak and native) and Windows builds.

---

## 1. Light Theme

### Global

- [ ] Background color is `#FFFFFF` (pure white), not off-white or grey
- [ ] Surface elevated areas use `#F0F2F5`
- [ ] Primary brand color `#25D366` is used consistently for primary actions
- [ ] Secondary color `#128C7E` used for secondary accents only
- [ ] All borders use `#D0D4D8`; strong borders `#A0A8B0`
- [ ] Text: primary `#111B21`, secondary `#667781`, disabled `#A6AEB6`

### Typography — Light

- [ ] H1 headings: 24 px, weight 700
- [ ] H2 headings: 20 px, weight 700
- [ ] H3 headings: 16 px, weight 600
- [ ] Body text: 14 px, weight 400
- [ ] Caption text: 12 px, weight 400
- [ ] Labels: 11 px, weight 500
- [ ] No mixed font families within a single component
- [ ] Line height does not cause text to overlap adjacent elements

### Cards — Light

- [ ] Cards use `#FFFFFF` background with `#E8ECF0` border
- [ ] Card shadow is subtle `rgba(0,0,0,0.08)`
- [ ] Card border radius is 8 px (MD)
- [ ] Card padding is consistent (16 px internal padding)

### Inputs — Light

- [ ] Input background `#FFFFFF`, border `#D0D4D8`
- [ ] Focused input border changes to `#25D366`
- [ ] Placeholder text is visually distinct from entered text
- [ ] Input corner radius is 8 px

### Buttons — Light

- [ ] Primary button: `#25D366` background, white text
- [ ] Primary hover: `#1EBE59`
- [ ] Primary pressed: `#17A34A`
- [ ] Secondary/ghost button: transparent background, `#25D366` text/border
- [ ] Disabled button: muted colors, `not-allowed` cursor
- [ ] Button minimum height is 36 px; touch-friendly variant 44 px

### Scrollbars — Light

- [ ] Scrollbar track: `#F0F2F5`
- [ ] Scrollbar thumb: `#C1C7CE`; hover: `#A0A8B0`
- [ ] Scrollbar width is proportionate and not oversized

---

## 2. Dark Theme

### Global

- [ ] Background color is `#111B21`
- [ ] Surface: `#1E2A33`; surface raised: `#2A3942`; overlay: `#374854`
- [ ] Borders: `#2A3942`; strong: `#3B4A54`
- [ ] Text: primary `#E9EDF0`, secondary `#8696A0`, disabled `#4A5568`
- [ ] Primary brand color `#25D366` unchanged between themes
- [ ] Secondary dark color: `#00BFA5`

### Typography — Dark

- [ ] All heading and body text uses dark-theme text tokens (no hardcoded light colors)
- [ ] Text remains readable on dark surfaces without appearing washed-out

### Cards — Dark

- [ ] Cards use `#1E2A33` background with `#2A3942` border
- [ ] Card shadow uses `rgba(0,0,0,0.3)` for proper depth in dark mode

### Inputs — Dark

- [ ] Input background `#2A3942`, border `#374854`
- [ ] Focused input border changes to `#25D366`

### Buttons — Dark

- [ ] All button states look correct on dark backgrounds (sufficient contrast)
- [ ] Ghost/outlined buttons are visible against `#111B21`

### Scrollbars — Dark

- [ ] Scrollbar track: `#1E2A33`
- [ ] Scrollbar thumb: `#374854`; hover: `#4A5A66`

---

## 3. Theme Switching

- [ ] Switching theme (light ↔ dark) applies immediately without restart
- [ ] No visual artifacts or flash during theme switch
- [ ] System theme (auto) follows OS dark/light preference
- [ ] Icons update correctly when theme changes
- [ ] All custom QSS stylesheets respond to theme change

---

## 4. Cross-Platform Checks

### Linux (Primary)

- [ ] Flatpak build renders fonts correctly (system fonts accessible)
- [ ] HiDPI / fractional scaling (1.5×, 2×) renders without blurriness
- [ ] Window decorations follow GTK/KDE theme settings
- [ ] Tray icon appears in system tray and has correct size
- [ ] Notification popups appear on all common desktop environments (GNOME, KDE, XFCE)

### Windows

- [ ] Application renders correctly on Windows 10 / Windows 11
- [ ] ClearType / DirectWrite font rendering is sharp
- [ ] DPI-aware scaling works at 100%, 125%, 150%, 200%
- [ ] Windows taskbar icon is correct resolution
- [ ] System tray icon is present and functional

---

## 5. Typography Consistency

- [ ] Font family is consistent throughout: `system-ui, -apple-system, sans-serif`
- [ ] No fallback font (e.g., Times New Roman) visible anywhere
- [ ] Text truncation uses `…` (ellipsis), not abrupt cutting
- [ ] No orphaned words in wrapped text within dialog descriptions
- [ ] Translated strings (long German/French text) do not overflow containers
- [ ] Monospace text (e.g., version numbers, paths) uses a monospace font

---

## 6. Icon Consistency

- [ ] All icons are from the same icon set / design language
- [ ] Icon sizes are consistent within the same context (e.g., all toolbar icons 20 px)
- [ ] Icons have correct padding / optical centering
- [ ] Icons render at correct resolution on HiDPI displays (SVG preferred)
- [ ] No placeholder or missing icons visible
- [ ] Icon colors follow theme tokens (not hardcoded)

---

## 7. Spacing & Alignment

- [ ] Internal padding follows spacing scale: XS=4, SM=8, MD=16, LG=24, XL=32
- [ ] Elements are not "touching" container edges without padding
- [ ] Labels are vertically centered with their associated controls
- [ ] Columns/grids are aligned (pixel-perfect alignment in key views)
- [ ] Settings rows have consistent left indent / hierarchy
- [ ] Dialog footer buttons are right-aligned (or centered per platform convention)
- [ ] Modal dialogs are centered on screen

---

## 8. Responsive / Resize Behavior

- [ ] Main window resizes gracefully from minimum (800×600) to full-screen
- [ ] Settings dialog is scrollable when window is too small to show all content
- [ ] Account switcher popover repositions correctly near screen edges
- [ ] Onboarding wizard maintains layout at minimum dialog size (480×500)
- [ ] Text does not overflow buttons or labels at 150% system font scale

---

## 9. Component States

### Hover

- [ ] Buttons show hover state (background color change)
- [ ] List items show hover highlight
- [ ] Links show underline or color change on hover
- [ ] Cursor changes to pointer on interactive elements

### Focus

- [ ] Focus ring is `#25D366` or high-contrast equivalent
- [ ] Focus ring is not hidden by overflow or z-index
- [ ] Only one element is focused at a time

### Disabled

- [ ] Disabled buttons are visually muted (`#A6AEB6` / `#4A5568`)
- [ ] Disabled inputs have a distinct background
- [ ] Disabled controls do not respond to hover styles
- [ ] Cursor changes to `not-allowed` on disabled elements

### Error / Validation

- [ ] Error borders change to `#EF4444`
- [ ] Error icon appears alongside error message
- [ ] Error background uses `#FEE2E2` (light) or `#3A1414` (dark)
- [ ] Inline error text is 12 px and `#EF4444`

### Loading

- [ ] Loading spinner matches brand color
- [ ] Loading overlay dims background appropriately
- [ ] Skeleton loaders match the shape of real content
- [ ] Loading text ("Loading…") is present for accessibility

### Empty State

- [ ] Empty state illustrations are centered
- [ ] Empty state includes a headline and descriptive text
- [ ] Empty state includes a call-to-action where appropriate
- [ ] Empty state background matches theme surface color

---

## 10. Animation & Transitions

- [ ] Transitions use design-token durations: Fast=100 ms, Normal=200 ms, Slow=300 ms
- [ ] No jarring jumps or flashes during transitions
- [ ] Animations respect `prefers-reduced-motion` system setting
- [ ] Dialogs open/close with a subtle fade or slide
- [ ] Toast notifications slide in and auto-dismiss smoothly

---

## 11. ZapZap-Specific Screens

### Main Window

- [ ] Account tabs/sidebar shows correct account avatar and name
- [ ] Unread badge count is visible and formatted correctly (99+ for large counts)
- [ ] Tray icon reflects unread message state
- [ ] WhatsApp web content fills the available area without white borders

### Settings Dialog

- [ ] All 8 settings categories are visible and navigable
- [ ] Settings search field is prominent and visually distinct
- [ ] Search results highlight matching text
- [ ] No-results illustration is shown when search returns nothing
- [ ] Category icons are present and consistent

### Account Switcher

- [ ] Account list is scrollable when many accounts are added
- [ ] Active account is visually indicated (checkmark, highlight, or accent color)
- [ ] "Add account" button is at the bottom of the list
- [ ] Account switcher animates open/closed

### Notifications Settings

- [ ] Toggle switches for notification types are clearly labelled
- [ ] Preview of notification appearance is shown where possible
- [ ] Permission status (granted / denied) is clearly communicated

### Onboarding Wizard

- [ ] Step indicator (dots or progress) is visible
- [ ] "Skip" option is unobtrusive but accessible
- [ ] Illustrations/icons are shown for each step
- [ ] Wizard is correctly sized (not too large on small screens)

---

## 12. Metrics Dashboard

- [ ] KPI progress bars render correctly in both themes
- [ ] "Reset Metrics" button has destructive styling (red)
- [ ] "Export JSON" saves file dialog opens correctly
- [ ] Summary stats update after refresh

---

## Sign-Off

| Tester | Date | Platform | Theme | Result |
|--------|------|----------|-------|--------|
|        |      | Linux    | Light |        |
|        |      | Linux    | Dark  |        |
|        |      | Windows  | Light |        |
|        |      | Windows  | Dark  |        |
