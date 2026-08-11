import { Languages } from "lucide-react";

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
            <select
                value={locale}
                onChange={(event) => setLocale(event.target.value as Locale)}
                aria-label={t("language.label")}
                className="min-w-0 cursor-pointer bg-transparent text-xs font-medium text-foreground outline-none"
            >
                <option value="en">{t("language.english")}</option>
                <option value="pt-BR">{t("language.portuguese")}</option>
            </select>
        </label>
    );
}
