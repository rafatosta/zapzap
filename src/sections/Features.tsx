import { useI18n } from "../i18n/useI18n";

function Features() {
    const { t } = useI18n();
    const features = [
        {
            id: "accounts",
            title: t("features.accounts.title"),
            body: t("features.accounts.body"),
        },
        {
            id: "integration",
            title: t("features.integration.title"),
            body: t("features.integration.body"),
        },
        {
            id: "packages",
            title: t("features.packages.title"),
            body: t("features.packages.body"),
        },
        {
            id: "updates",
            title: t("features.updates.title"),
            body: t("features.updates.body"),
        },
        {
            id: "source",
            title: t("features.source.title"),
            body: t("features.source.body"),
        },
        {
            id: "privacy",
            title: t("features.privacy.title"),
            body: t("features.privacy.body"),
        },
        {
            id: "spellcheck",
            title: t("features.spellcheck.title"),
            body: t("features.spellcheck.body"),
        },
        {
            id: "custom",
            title: t("features.custom.title"),
            body: t("features.custom.body"),
        },
        {
            id: "platforms",
            title: t("features.platforms.title"),
            body: t("features.platforms.body"),
        },
    ];

    return (
        <section id="features" className="border-t border-hairline bg-subtle">
            <div className="mx-auto max-w-6xl px-6 py-24">
                <div className="max-w-2xl">
                    <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                        {t("features.eyebrow")}
                    </p>

                    <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                        {t("features.title")}
                    </h2>

                    <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                        {t("features.description")}
                    </p>
                </div>

                <ul className="mt-14 grid grid-cols-1 gap-x-10 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
                    {features.map((feature, index) => (
                        <li
                            key={feature.id}
                            className="border-t border-hairline pt-5"
                        >
                            <div className="flex items-center gap-3">
                                <span className="font-mono text-[11px] tabular-nums text-muted-foreground">
                                    {String(index + 1).padStart(2, "0")}
                                </span>

                                <h3 className="text-[15px] font-semibold tracking-tight">
                                    {feature.title}
                                </h3>
                            </div>

                            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                                {feature.body}
                            </p>
                        </li>
                    ))}
                </ul>
            </div>
        </section>
    );
}

export default Features;
