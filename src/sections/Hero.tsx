import { useLatestRelease } from "@/hooks/useLatestRelease";
import { useFlathubStats } from "@/hooks/useFlathubStats";


function Hero() {
    const version = useLatestRelease();

    const { stats, loading } = useFlathubStats();

    if (loading || !stats) {
        return <div>Loading...</div>;
    }

    return (<section className="mx-auto max-w-6xl px-6 pt-24 pb-16 md:pt-32 md:pb-20">
        <div className="mx-auto max-w-3xl text-center">
            <a
                href="https://github.com/rafatosta/zapzap/releases"
                className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 font-mono text-[11px] uppercase tracking-wider text-muted-foreground transition-colors hover:text-foreground"
            >
                <span className="h-1.5 w-1.5 rounded-full bg-primary" aria-hidden />
                v{version} available
            </a>

            <h1 className="mt-7 text-5xl font-semibold leading-[1.05] tracking-tight md:text-7xl">
                A native WhatsApp,
                <br />
                <span className="text-muted-foreground">built for Linux.</span>
            </h1>

            <p className="mx-auto mt-6 max-w-xl text-[17px] leading-relaxed text-muted-foreground">
                A desktop experience for WhatsApp that feels at home on Linux.
                Multi-account support, spell checking, native notifications and
                deep desktop integration.
            </p>

            <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
                <a
                    href="#download"
                    className="inline-flex items-center gap-2 rounded-md bg-foreground px-5 py-2.5 text-sm font-medium text-background transition-opacity hover:opacity-90"
                >
                    Download free
                </a>
                <a
                    href="https://github.com/rafatosta/zapzap"
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
                <span>RPM</span>
                <span>•</span>
                <span>DEB</span>
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
                {[
                    [stats.totalDownloads, "Downloads"],
                    [stats.totalInstalls, "Installs"],
                    ["GPL-3.0", "License"],
                ].map(([n, l]) => (
                    <div key={l as string} className="text-center">
                        <dt className="text-2xl font-semibold tracking-tight">{n}</dt>
                        <dd className="mt-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                            {l}
                        </dd>
                    </div>
                ))}
            </dl>
        </div>
    </section>);
}

export default Hero;