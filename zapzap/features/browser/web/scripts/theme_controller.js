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

    ThemeController.boot();
})();