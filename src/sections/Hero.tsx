import { useLatestRelease } from "../hooks/useLatestRelease";
import { useFlathubStats } from "../hooks/useFlathubStats";
import { useI18n } from "../i18n/useI18n";

function Hero() {
    const { version } = useLatestRelease();
    const { stats, loading, error } = useFlathubStats();
    const { numberLocale, t } = useI18n();

    const formatNumber = (value?: number | string) => {
        if (loading || error || value === undefined || value === null) {
            return "—";
        }

        const number = Number(value);

        if (Number.isNaN(number)) {
            return value;
        }

        return new Intl.NumberFormat(numberLocale, {
            notation: number >= 10000 ? "compact" : "standard",
            maximumFractionDigits: 1,
        }).format(number);
    };

    const metrics = [
        [formatNumber(stats?.totalDownloads), t("hero.flathubDownloads")],
        ["3", t("hero.platforms")],
        ["GPL-3.0", t("hero.license")],
    ];

    return (
        <section className="mx-auto max-w-6xl px-6 pb-16 pt-16 md:pb-20 md:pt-28">
            <div className="mx-auto max-w-3xl text-center">
                <a
                    href="https://github.com/rafatosta/zapzap/releases"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 font-mono text-[11px] uppercase tracking-wider text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" aria-hidden />
                    {version
                        ? t("hero.release", { version })
                        : t("hero.latest")}
                </a>

                <h1 className="mt-7 text-5xl font-semibold leading-[1.05] tracking-tight md:text-7xl text-whatsapp-gradient">
                    ZapZap
                    <br />
                    <span className="text-3xl text-muted-foreground md:text-5xl">
                        {t("hero.tagline")}
                    </span>
                </h1>

                <p className="mx-auto mt-6 max-w-xl text-[17px] leading-relaxed text-muted-foreground">
                    {t("hero.description")}
                </p>


                <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
                    <a
                        href="#download"
                        className="inline-flex min-h-11 items-center gap-2 rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                        {t("hero.download")}
                    </a>

                    <a
                        href="https://github.com/rafatosta/zapzap"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex min-h-11 items-center gap-2 rounded-md border border-border bg-card px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                        {t("hero.github")}
                    </a>
                </div>

                <div className="mt-6 flex flex-wrap items-center justify-center gap-2 text-xs text-muted-foreground">
                    <span>Linux</span>
                    <span>• Windows</span>
                    <span>• macOS</span>
                </div>

                <div className="mt-4 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
                    <span>✓ {t("hero.multiAccount")}</span>
                    <span>✓ {t("hero.notifications")}</span>
                    <span>✓ {t("hero.spellChecker")}</span>
                    <span>✓ {t("hero.openSource")}</span>
                </div>

                <dl className="mx-auto mt-14 grid max-w-lg grid-cols-3 gap-6 border-t border-hairline pt-8">
                    {metrics.map(([value, label]) => (
                        <div key={label} className="text-center">
                            <dt className="text-2xl font-semibold tracking-tight">
                                {value}
                            </dt>

                            <dd className="mt-1 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                                {label}
                            </dd>
                        </div>
                    ))}
                </dl>
            </div>
        </section>
    );
}

export default Hero;
