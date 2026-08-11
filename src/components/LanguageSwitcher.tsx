import { ChevronDown, Languages } from "lucide-react";

import { useI18n } from "../i18n/useI18n";
import type { Locale } from "../i18n/translations";

type LanguageSwitcherProps = {
    compact?: boolean;
};

export function LanguageSwitcher({ compact = false }: LanguageSwitcherProps) {
    const { locale, setLocale, t } = useI18n();

    return (
        <label
            className={`flex items-center gap-2 text-muted-foreground ${
                compact ? "w-full rounded-md border border-border px-3 py-2" : ""
            }`}
        >
            <Languages className="size-4 shrink-0" aria-hidden="true" />
            <span className={compact ? "text-sm font-medium" : "sr-only"}>
                {t("language.label")}
            </span>
            <span className="relative min-w-0">
                <select
                    value={locale}
                    onChange={(event) => setLocale(event.target.value as Locale)}
                    aria-label={t("language.label")}
                    className="min-w-0 cursor-pointer appearance-none rounded-sm bg-transparent py-1 pr-5 text-xs font-medium text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                    <option value="en">{t("language.english")}</option>
                    <option value="pt-BR">{t("language.portuguese")}</option>
                </select>
                <ChevronDown
                    className="pointer-events-none absolute right-0 top-1/2 size-3 -translate-y-1/2"
                    aria-hidden="true"
                />
            </span>
        </label>
    );
}
