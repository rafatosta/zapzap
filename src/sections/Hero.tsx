import { useLatestRelease } from "@/hooks/useLatestRelease";
import { useFlathubStats } from "@/hooks/useFlathubStats";

function Hero() {
    const version = useLatestRelease();
    const { stats, loading } = useFlathubStats();

    const formatNumber = (value?: number | string) => {
        if (loading || value === undefined || value === null) {
            return "—";
        }

        const number = Number(value);

        if (Number.isNaN(number)) {
            return value;
        }

        return new Intl.NumberFormat("en-US", {
            notation: number >= 10000 ? "compact" : "standard",
            maximumFractionDigits: 1,
        }).format(number);
    };

    const metrics = [
        [formatNumber(stats?.totalDownloads), "Downloads"],
        [formatNumber(stats?.totalInstalls), "Installs"],
        ["GPL-3.0", "License"],
    ];

    return (
        <section className="mx-auto max-w-6xl px-6 pt-24 pb-16 md:pt-32 md:pb-20">
            <div className="mx-auto max-w-3xl text-center">
                <a
                    href="https://github.com/rafatosta/zapzap/releases"
                    className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 font-mono text-[11px] uppercase tracking-wider text-muted-foreground transition-colors hover:text-foreground"
                >
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" aria-hidden />
                    v{version || "latest"} available
                </a>

                <h1 className="mt-7 text-5xl font-semibold leading-[1.05] tracking-tight md:text-7xl text-whatsapp-gradient">
                    ZapZap
                    <br />
                    <span className="text-3xl text-muted-foreground md:text-5xl">
                        WhatsApp, better on Linux.
                    </span>
                </h1>

                <p className="mx-auto mt-6 max-w-xl text-[17px] leading-relaxed text-muted-foreground">
                    A dedicated desktop application with multi-account support, native
                    notifications, spell checking and deep Linux integration.
                </p>


                <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
                    <a
                        href="#download"
                        className="inline-flex items-center gap-2 rounded-md bg-foreground px-5 py-2.5 text-sm font-medium text-background transition-opacity hover:opacity-90"
                    >
                        Download ZapZap
                    </a>

                    <a
                        href="https://github.com/rafatosta/zapzap"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
                    >
                        View on GitHub
                    </a>
                </div>

                <div className="mt-6 flex flex-wrap items-center justify-center gap-2 text-xs text-muted-foreground">
                    <span>Flatpak</span>
                    <span>•</span>
                    <span>AppImage</span>
                    <span>•</span>
                    <span>Snap</span>
                    <span>•</span>
                    <span>DEB</span>
                    <span>•</span>
                    <span>Fedora COPR</span>
                    <span>•</span>
                    <span>Windows</span>
                </div>

                <div className="mt-4 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
                    <span>✓ Multi-account</span>
                    <span>✓ Native notifications</span>
                    <span>✓ Spell checker</span>
                    <span>✓ Open source</span>
                </div>

                <dl className="mx-auto mt-14 grid max-w-lg grid-cols-3 gap-6 border-t border-hairline pt-8">
                    {metrics.map(([value, label]) => (
                        <div key={label} className="text-center">
                            <dt className="text-2xl font-semibold tracking-tight">
                                {value}
                            </dt>

                            <dd className="mt-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
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