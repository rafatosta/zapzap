import { createContext } from "react";

import type { Locale, TranslationKey } from "./translations";

export type Translate = (
    key: TranslationKey,
    variables?: Record<string, string | number>,
) => string;

export type I18nContextValue = {
    locale: Locale;
    numberLocale: string;
    setLocale: (locale: Locale) => void;
    t: Translate;
};

export const I18nContext = createContext<I18nContextValue | null>(null);
