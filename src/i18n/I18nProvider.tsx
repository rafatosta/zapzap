import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";

import { I18nContext, type Translate } from "./context";
import { translations, type Locale } from "./translations";

const STORAGE_KEY = "zapzap.website.locale";

function detectLocale(): Locale {
    try {
        const savedLocale = window.localStorage.getItem(STORAGE_KEY);

        if (savedLocale === "en" || savedLocale === "pt-BR") {
            return savedLocale;
        }
    } catch {
        // Storage may be unavailable in private or restricted browser contexts.
    }

    return window.navigator.language.toLowerCase().startsWith("pt")
        ? "pt-BR"
        : "en";
}

export function I18nProvider({ children }: { children: ReactNode }) {
    const [locale, setLocaleState] = useState<Locale>(detectLocale);

    const t = useCallback<Translate>(
        (key, variables) => {
            const message = translations[locale][key];

            if (!variables) {
                return message;
            }

            return Object.entries(variables).reduce(
                (translated, [name, value]) =>
                    translated.replaceAll(`{${name}}`, String(value)),
                message,
            );
        },
        [locale],
    );

    const setLocale = useCallback((nextLocale: Locale) => {
        setLocaleState(nextLocale);

        try {
            window.localStorage.setItem(STORAGE_KEY, nextLocale);
        } catch {
            // The in-memory preference still applies when storage is unavailable.
        }
    }, []);

    useEffect(() => {
        document.documentElement.lang = locale;
        document.title = t("meta.title");

        const description = document.querySelector<HTMLMetaElement>(
            'meta[name="description"]',
        );

        if (description) {
            description.content = t("meta.description");
        }
    }, [locale, t]);

    const value = useMemo(
        () => ({ locale, numberLocale: locale, setLocale, t }),
        [locale, setLocale, t],
    );

    return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
