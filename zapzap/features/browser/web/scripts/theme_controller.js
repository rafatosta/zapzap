{qwebchannel_js_code}

(() => {
    const LOG_PREFIX = "[ZapZap WAWeb Theme Controller]";

    const THEME_CONTEXT_PENDING_TIMEOUT = 60000; // 60 seconds

    const MODULES = {
        prefs: {
            name: "WAWebUserPrefsGeneral",      // require("WAWebUserPrefsGeneral")
            requiredFunctions: [
                "getTheme",                     // require("WAWebUserPrefsGeneral").getTheme()
                "setTheme",                     // require("WAWebUserPrefsGeneral").setTheme()
                "getSystemThemeMode",           // require("WAWebUserPrefsGeneral").getSystemThemeMode()
                "setSystemThemeMode",           // require("WAWebUserPrefsGeneral").setSystemThemeMode()
            ],
        },
        settingsFBT: {
            name: "WAWebSettingsFBT",           // require("WAWebSettingsFBT")
            requiredFunctions: ["themeTitle"],  // require("WAWebSettingsFBT").themeTitle()
        },
    };

    const REACT_FIBER_KEYS = [
        "__reactFiber$",
        "__reactInternalInstance$",
        "__reactContainer$",
    ];

    const ModuleRegistry = {
        _cache: new Map(),

        get(definition) {
            if (this._cache.has(definition.name)) {
                return this._cache.get(definition.name);
            }

            try {
                const module = require(definition.name);

                if (
                    !module ||
                    !definition.requiredFunctions.every(
                        (name) => typeof module[name] === "function"
                    )
                ) {
                    return null;
                }

                this._cache.set(definition.name, module);
                return module;
            } catch (_) {
                return null;
            }
        },
    };

    const ReactHelper = {
        _fiberKeyFor(element) {
            if (!element) {
                return null;
            }

            return Object.keys(element).find((key) =>
                REACT_FIBER_KEYS.some((prefix) => key.startsWith(prefix))
            ) || null;
        },

        _fiberFromElement(element) {
            const key = this._fiberKeyFor(element);
            return key ? element[key] : null;
        },

        _isThemeContext(value) {
            return Boolean(
                value &&
                typeof value === "object" &&
                typeof value.setTheme === "function" &&
                typeof value.setSystemThemeMode === "function"
            );
        },

        findThemeContext() {
            const checkedFibers = new Set();

            for (const element of document.querySelectorAll("*")) {
                let fiber = this._fiberFromElement(element);

                while (fiber && !checkedFibers.has(fiber)) {
                    checkedFibers.add(fiber);

                    const props = fiber.memoizedProps || fiber.pendingProps;
                    const value = props && props.value;

                    if (this._isThemeContext(value)) {
                        return value;
                    }

                    fiber = fiber.return;
                }
            }

            return null;
        },
    };

    const QuickAccountsController = {
        bridge: null,
        observer: null,
        framePending: false,
        visible: {quick_accounts_visible},
        resizeHandler: null,
        iconColor: null,
        hasOtherUnread: false,
        label: {selector_label},
        activityLabel: {selector_activity_label},

        boot() {
            const previous = window._zapZapQuickAccountsController;
            if (previous && previous.observer) {
                previous.observer.disconnect();
            }
            if (previous && previous.resizeHandler) {
                window.removeEventListener("resize", previous.resizeHandler);
            }
            window._zapZapQuickAccountsController = this;
            this.ensureButton();
            this.resizeHandler = () => this.scheduleEnsure();
            window.addEventListener("resize", this.resizeHandler);
            if (document.documentElement) {
                this.observer = new MutationObserver((records) => {
                    // Ignore our own styles to avoid a perpetual animation-frame loop.
                    const own = (node) => node.nodeType === 1 &&
                        (node.matches('[data-zapzap-component="quick-accounts"]') ||
                         node.closest('[data-zapzap-component="quick-accounts"]'));
                    if (records.some((record) => !own(record.target) &&
                        (record.type !== "childList" ||
                         [...record.removedNodes].some((node) => own(node) && !node.isConnected) ||
                         [...record.addedNodes, ...record.removedNodes].some((node) => !own(node))))) {
                        this.scheduleEnsure();
                    }
                });
                this.observer.observe(document.documentElement, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ["class", "style", "fill", "width", "height",
                        "aria-selected", "aria-pressed", "aria-current", "disabled", "aria-disabled"],
                });
            }
        },

        setBridge(bridge) {
            this.bridge = bridge;
            if (this.bridge && typeof this.bridge.on_quick_accounts_controller_ready === "function") {
                this.bridge.on_quick_accounts_controller_ready();
            }
        },

        setVisible(visible) {
            this.visible = Boolean(visible);
            const button = document.querySelector('[data-zapzap-component="quick-accounts"]');
            if (button) {
                button.hidden = !this.visible;
            }
            this.ensureButton();
        },

        setState(visible, hasOtherUnread) {
            this.visible = Boolean(visible);
            this.hasOtherUnread = Boolean(hasOtherUnread);
            this.ensureButton();
        },

        setIconColor(color) {
            this.iconColor = color;
            this.scheduleEnsure();
        },

        syncIconAppearance(button, target) {
            const icon = button.querySelector("svg");
            if (!icon) {
                return;
            }
            let color = this.iconColor || "currentColor";
            let width = "20px";
            let height = "20px";
            // Sample an ordinary native navigation action, never an injected icon or an
            // active/disabled action whose color represents a special state.
            const candidates = target === document.body ? [] : target.querySelectorAll(
                'button svg, [role="button"] svg, [role="tab"] svg'
            );
            for (const candidate of candidates) {
                if (candidate.closest('[data-zapzap-component]') || candidate.closest(
                    '[aria-selected="true"], [aria-pressed="true"], ' +
                    '[aria-current]:not([aria-current="false"]), [disabled], [aria-disabled="true"]'
                )) {
                    continue;
                }
                const bounds = candidate.getBoundingClientRect();
                const style = getComputedStyle(candidate);
                if (bounds.width <= 0 || bounds.height <= 0 || style.visibility === "hidden") {
                    continue;
                }
                const paint = getComputedStyle(candidate.querySelector("path") || candidate);
                color = paint.fill !== "none" && paint.fill !== "rgba(0, 0, 0, 0)"
                    ? paint.fill : paint.color;
                width = style.width;
                height = style.height;
                break;
            }
            icon.style.fill = color;
            icon.style.color = color;
            icon.style.width = width;
            icon.style.height = height;
            icon.style.flexShrink = "0";
        },

        scheduleEnsure() {
            if (this.framePending) {
                return;
            }
            this.framePending = true;
            requestAnimationFrame(() => {
                this.framePending = false;
                this.ensureButton();
            });
        },

        findQuickAccountsMountPoint() {
            const navigationCandidates = new Set(document.querySelectorAll(
                'nav, [role="navigation"], aside'
            ));
            // WhatsApp also uses plain divs for its rail. Discover those from
            // native actions rather than relying on generated class names.
            for (const action of document.querySelectorAll('button, [role="button"], [role="tab"]')) {
                if (action.closest('[data-zapzap-component="quick-accounts"]')) {
                    continue;
                }
                for (let node = action.parentElement; node && node !== document.body; node = node.parentElement) {
                    navigationCandidates.add(node);
                }
            }
            for (const candidate of navigationCandidates) {
                const bounds = candidate.getBoundingClientRect();
                if (
                    bounds.left <= 24 &&
                    bounds.width >= 48 &&
                    bounds.width <= 120 &&
                    bounds.height >= window.innerHeight * 0.5 &&
                    getComputedStyle(candidate).visibility !== "hidden"
                ) {
                    return candidate;
                }
            }

            return null;
        },

        placeButton(button, target) {
            let parent = target;
            let anchor = null;
            // Join the native column containing the bottom actions. Never use
            // viewport offsets: extra actions (including Beta) need real space.
            const actions = [...target.querySelectorAll('button, [role="button"], [role="tab"]')]
                .filter((action) => action !== button && !button.contains(action)
                    && action.getBoundingClientRect().height > 0);
            for (const action of actions.reverse()) {
                let item = action;
                while (item.parentElement && target.contains(item.parentElement)) {
                    const container = item.parentElement;
                    const style = getComputedStyle(container);
                    if (style.display === "flex" && style.flexDirection === "column"
                        && container.children.length >= 2) {
                        parent = container;
                        anchor = item;
                        break;
                    }
                    item = container;
                }
                if (anchor) {
                    break;
                }
            }
            button.style.margin = "4px";
            button.style.position = "relative";
            button.style.left = "auto";
            button.style.top = "auto";
            button.style.bottom = "auto";
            button.style.right = "auto";
            button.style.zIndex = "auto";
            button.style.flexShrink = "0";
            button.style.alignSelf = "center";
            button.style.display = this.visible ? "inline-flex" : "none";
            if (anchor) {
                if (button.parentElement !== parent || button.nextElementSibling !== anchor) {
                    parent.insertBefore(button, anchor);
                }
            } else if (button.parentElement !== target) {
                target.appendChild(button);
            }
        },

        ensureButtonVisible(button, target) {
            if (!this.visible) {
                return;
            }
            const rect = button.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const points = [rect.top + 2, rect.top + rect.height / 2, rect.bottom - 2];
            if (rect.width > 0 && rect.height > 0 && rect.left >= 0 &&
                rect.right <= window.innerWidth && rect.top >= 0 && rect.bottom <= window.innerHeight &&
                points.every((y) => button.contains(document.elementFromPoint(centerX, y)))) {
                return;
            }
            // A fixed-height/overflow-hidden React wrapper can clip injected
            // children. Use a measured empty rail slot outside that wrapper.
            const rail = target.getBoundingClientRect();
            const width = Math.max(40, rect.width);
            const height = Math.max(40, rect.height);
            const occupied = [...target.querySelectorAll('*')].filter((node) =>
                node !== button && !button.contains(node) && !node.contains(button) &&
                (node.matches('button, [role="button"], [role="tab"], img, svg') ||
                 (node.children.length === 0 && node.textContent.trim()))
            ).map((node) => node.getBoundingClientRect()).filter((box) => box.width && box.height);
            let left = Math.max(4, rail.left + (rail.width - width) / 2);
            let top = null;
            if (rail.width >= width && rail.width <= 120) {
                for (let y = Math.min(rail.bottom, window.innerHeight) - height - 4;
                     y >= Math.max(4, rail.top); y -= 4) {
                    if (occupied.every((box) => box.bottom + 4 <= y || box.top - 4 >= y + height)) {
                        top = y;
                        break;
                    }
                }
            }
            if (top === null) {
                button.style.display = "none";
                return;
            }
            if (button.parentElement !== document.body) {
                document.body.appendChild(button);
            }
            button.style.position = "fixed";
            button.style.margin = "0";
            button.style.left = `${left}px`;
            button.style.top = `${top}px`;
            button.style.bottom = "auto";
            button.style.zIndex = "2147483647";
        },

        createButton() {
            const button = document.createElement("button");
            button.type = "button";
            button.setAttribute("data-zapzap-component", "quick-accounts");
            button.setAttribute("aria-label", this.label);
            button.title = this.label;
            button.hidden = !this.visible;
            const styles = [
                "align-items:center",
                "background:transparent",
                "border:0",
                "border-radius:8px",
                "color:inherit",
                "cursor:pointer",
                "display:inline-flex",
                "min-height:40px",
                "box-sizing:border-box",
                "justify-content:center",
                "margin:4px",
                "padding:8px",
                "min-width:40px",
            ];
            button.style.cssText = styles.join(";");
            button.innerHTML = `{quick_accounts_icon}`;
            const icon = button.querySelector("svg");
            if (icon) {
                icon.setAttribute("aria-hidden", "true");
                icon.setAttribute("width", "20");
                icon.setAttribute("height", "20");
                if (this.iconColor) {
                    icon.setAttribute("fill", this.iconColor);
                }
            }
            const badge = document.createElement("span");
            badge.setAttribute("data-zapzap-unread", "true");
            badge.setAttribute("aria-hidden", "true");
            badge.style.cssText = "position:absolute;right:3px;top:3px;width:8px;height:8px;" +
                "border-radius:50%;background:var(--unread-marker-background,#25d366);pointer-events:none";
            button.appendChild(badge);
            button.addEventListener("click", () => {
                try {
                    if (this.bridge && typeof this.bridge.open_recent_accounts === "function") {
                        const rect = button.getBoundingClientRect();
                        this.bridge.open_recent_accounts(Math.round(rect.x), Math.round(rect.y),
                            Math.round(rect.width), Math.round(rect.height));
                    }
                } catch (_) {
                    // The integration is optional and must not affect WhatsApp Web.
                }
            });
            return button;
        },

        ensureButton() {
            try {
                const target = this.findQuickAccountsMountPoint();
                let button = document.querySelector('[data-zapzap-component="quick-accounts"]');
                if (!target || !this.visible) {
                    if (button) button.remove();
                    return;
                }
                if (!button) button = this.createButton();
                button.hidden = false;
                button.querySelector('[data-zapzap-unread]').hidden = !this.hasOtherUnread;
                const label = this.label + (this.hasOtherUnread ? " — " + this.activityLabel : "");
                button.setAttribute("aria-label", label);
                button.title = label;
                this.placeButton(button, target);
                this.syncIconAppearance(button, target);
                this.ensureButtonVisible(button, target);
            } catch (_) {
                // Optional navigation must never interfere with WhatsApp Web.
            }
        },
    };

    const ThemeController = {
        _failed: false,
        _is_ready: false,
        _suppressThemeChangeEvents: false,

        bridge: null,
        ctx: null,
        currentColorScheme: "{current_color_scheme}",
        prefs: null,
        themeContextObserver: null,
        themeContextTimeout: null,
        settingsObserver: null,

        has_failed() {
            return this._failed;
        },

        is_ready() {
            return this._is_ready;
        },

        applyZapZapColorSchemeToWAWeb() {
            if (this._failed) {
                return false;
            }

            if (!this.ctx) {
                this._observeThemeContext();
                return false;
            }

            const prefs = this._requirePrefs();
            if (!prefs) {
                return false;
            }

            this._changeWAWebThemeWithoutDispatchingThemeChangedEvent(prefs);
            return !this._failed;
        },

        boot() {
            window._zapZapWAWebThemeController = this;

            if (!this._initialize()) {
                this._observeThemeContext();
            }
        },

        _initialize(ctx = null) {
            if (this._failed) {
                return false;
            }

            if (this._is_ready) {
                return true;
            }

            this._setupQWebChannel();

            this.ctx = ctx || ReactHelper.findThemeContext();
            if (!this.ctx) {
                return false;
            }

            const prefs = this._requirePrefs();
            if (!prefs) {
                return false;
            }

            this._patchPrefs(prefs);
            this._removeWAWebThemeSettingsOption();
            this._stopThemeContextObserver();

            if (!this.applyZapZapColorSchemeToWAWeb()) {
                return false;
            }

            this._is_ready = true;
            console.log(LOG_PREFIX, "WhatsApp Web theme controller initialized.");
            return true;
        },

        _requirePrefs() {
            if (this._failed) {
                return null;
            }

            const prefs = ModuleRegistry.get(MODULES.prefs);
            if (!prefs) {
                this._fail(
                    "Unable to control WhatsApp Web theme: WAWebUserPrefsGeneral API changed " +
                        "or is unavailable."
                );
                return null;
            }

            this.prefs = prefs;
            return prefs;
        },

        _setupQWebChannel() {
            if (
                this.bridge ||
                typeof QWebChannel === "undefined" ||
                typeof qt === "undefined" ||
                !qt.webChannelTransport
            ) {
                return;
            }

            try {
                new QWebChannel(qt.webChannelTransport, (channel) => {
                    this.bridge = channel.objects && channel.objects.zapZapBridge;
                    QuickAccountsController.setBridge(this.bridge);
                    this._notifyInjectionSuccess();
                });
            } catch (_) {
                console.warn(
                    LOG_PREFIX, "QWebChannel failed to initialize. ZapZap may still be " +
                        "able to change the WhatsApp Web theme, but won't monitor its changes."
                );
            }
        },

        _patchPrefs(prefs) {
            if (prefs.__zapZapPrefsPatched) {
                return;
            }

            prefs.__zapZapOriginalWAWebSetTheme = prefs.setTheme;
            prefs.__zapZapOriginalWAWebSetSystemThemeMode = prefs.setSystemThemeMode;

            prefs.setTheme = (nextTheme, ...args) => {
                const previousTheme = prefs.getTheme();
                const result = prefs.__zapZapOriginalWAWebSetTheme.call(prefs, nextTheme, ...args);
                const currentTheme = prefs.getTheme();

                if (!this._suppressThemeChangeEvents && currentTheme !== previousTheme) {
                    this._notifyWAWebThemeChanged(
                        previousTheme,
                        currentTheme,
                        prefs.getSystemThemeMode()
                    );
                }

                return result;
            };

            prefs.setSystemThemeMode = (nextSystemThemeMode, ...args) => {
                const previousSystemThemeMode = prefs.getSystemThemeMode();
                const result = prefs.__zapZapOriginalWAWebSetSystemThemeMode.call(
                    prefs,
                    nextSystemThemeMode,
                    ...args
                );

                if (
                    !this._suppressThemeChangeEvents &&
                    previousSystemThemeMode !== nextSystemThemeMode
                ) {
                    const currentTheme = prefs.getTheme();
                    this._notifyWAWebThemeChanged(
                        currentTheme,
                        currentTheme,
                        nextSystemThemeMode
                    );
                }

                return result;
            };

            prefs.__zapZapPrefsPatched = true;
        },

        _unpatchPrefs() {
            const prefs = this.prefs || ModuleRegistry.get(MODULES.prefs);
            if (!prefs || !prefs.__zapZapPrefsPatched) {
                return;
            }

            if (typeof prefs.__zapZapOriginalWAWebSetTheme === "function") {
                prefs.setTheme = prefs.__zapZapOriginalWAWebSetTheme;
            }

            if (typeof prefs.__zapZapOriginalWAWebSetSystemThemeMode === "function") {
                prefs.setSystemThemeMode = prefs.__zapZapOriginalWAWebSetSystemThemeMode;
            }

            delete prefs.__zapZapOriginalWAWebSetTheme;
            delete prefs.__zapZapOriginalWAWebSetSystemThemeMode;
            delete prefs.__zapZapPrefsPatched;
        },

        _changeWAWebThemeWithoutDispatchingThemeChangedEvent(prefs) {
            this._suppressThemeChangeEvents = true;

            try {
                // QWebEngine currently does not propagate system theme changes reliably
                // to the embedded page, so ZapZap keeps WAWeb out of system-theme mode
                // and applies the effective theme manually.
                if (prefs.getSystemThemeMode()) {
                    this.ctx.setSystemThemeMode(false);
                }

                if (prefs.getTheme() !== this.currentColorScheme) {
                    this.ctx.setTheme(this.currentColorScheme);
                }
            } catch (_) {
                this._fail("Unable to apply WhatsApp Web theme: ThemeContext API changed or is unavailable.");
            } finally {
                this._suppressThemeChangeEvents = false;
            }
        },

        _removeWAWebThemeSettingsOption() {
            const settingsFBT = ModuleRegistry.get(MODULES.settingsFBT);
            if (!settingsFBT || !document.body) {
                console.warn(
                    LOG_PREFIX, "Unable to hide the WhatsApp Web theme settings option."
                );
                return;
            }

            let selector;
            try {
                const title = String(settingsFBT.themeTitle());
                const escaped_title = window.CSS?.escape ? CSS.escape(title) : title.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
                selector = `[aria-label="${escaped_title}"]`;
            } catch (_) {
                console.warn(
                    LOG_PREFIX, "Unable to hide the WhatsApp Web theme settings option."
                );
                return;
            }

            const removeItem = () => {
                const item = document.querySelector(selector);
                if (item) {
                    item.remove();
                }
            };

            removeItem();

            if (this.settingsObserver) {
                this.settingsObserver.disconnect();
            }

            let scheduled = false;
            this.settingsObserver = new MutationObserver(() => {
                if (scheduled) {
                    return;
                }

                scheduled = true;
                requestAnimationFrame(() => {
                    scheduled = false;
                    removeItem();
                });
            });

            this.settingsObserver.observe(document.body, {
                childList: true,
                subtree: true,
            });
        },

        _observeThemeContext() {
            if (this._failed || this.themeContextObserver) {
                return;
            }

            this.themeContextObserver = new MutationObserver(() => {
                const ctx = ReactHelper.findThemeContext();
                if (ctx) {
                    this._initialize(ctx);
                }
            });

            this.themeContextObserver.observe(document.documentElement, {
                childList: true,
                subtree: true,
            });

            this.themeContextTimeout = setTimeout(() => {
                if (!this._is_ready && !this._failed) {
                    this._fail(
                        `Unable to find WhatsApp Web ThemeContext after ${THEME_CONTEXT_PENDING_TIMEOUT} milliseconds.`
                    );
                }
            }, THEME_CONTEXT_PENDING_TIMEOUT);
        },

        _stopThemeContextObserver() {
            if (this.themeContextObserver) {
                this.themeContextObserver.disconnect();
                this.themeContextObserver = null;
            }

            if (this.themeContextTimeout) {
                clearTimeout(this.themeContextTimeout);
                this.themeContextTimeout = null;
            }
        },

        _stopSettingsObserver() {
            if (!this.settingsObserver) {
                return;
            }

            this.settingsObserver.disconnect();
            this.settingsObserver = null;
        },

        _notifyWAWebThemeChanged(oldTheme, newTheme, systemThemeMode) {
            if (
                this._failed ||
                !this.bridge ||
                typeof this.bridge.on_waweb_theme_changed !== "function"
            ) {
                return;
            }

            this.bridge.on_waweb_theme_changed(newTheme, systemThemeMode);
        },

        _notifyInjectionSuccess() {
            if (
                this._failed ||
                !this.bridge ||
                typeof this.bridge.on_theme_controller_injection_success !== "function"
            ) {
                return;
            }

            this.bridge.on_theme_controller_injection_success();
        },

        _fail(message) {
            // The entire code must be exception-proof, with all caught failures funneling
            // into this function to allow the theme controller to properly signal ZapZap
            // that it must activate the fallback color scheme control via ForceDarkMode.
            if (this._failed) {
                return;
            }

            this._failed = true;
            console.error(LOG_PREFIX, message);

            if (this.bridge && typeof this.bridge.on_theme_controller_failure === "function") {
                this.bridge.on_theme_controller_failure(message);
            }

            this._stopThemeContextObserver();
            this._stopSettingsObserver();
            this._unpatchPrefs();
        },
    };

    QuickAccountsController.boot();
    ThemeController.boot();
})();