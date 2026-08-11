import { useLatestRelease } from "../hooks/useLatestRelease";
import { useI18n } from "../i18n/useI18n";

type DownloadOption = {
    label: string;
    href: string;
    detail?: string;
};

type DownloadCardProps = {
    badge: string;
    title: string;
    body: string;
    options: DownloadOption[];
    highlighted?: boolean;
    unofficial?: boolean;
};

function DownloadCard({
    badge,
    title,
    body,
    options,
    highlighted = false,
    unofficial = false,
}: DownloadCardProps) {
    return (
        <article
            className={`flex h-full flex-col rounded-xl border p-6 ${
                highlighted
                    ? "border-primary/35 bg-accent/45"
                    : unofficial
                      ? "border-border border-dashed bg-subtle/60"
                      : "border-border bg-card"
            }`}
        >
            <p
                className={`font-mono text-[10px] uppercase tracking-wider ${
                    highlighted ? "text-accent-foreground" : "text-muted-foreground"
                }`}
            >
                {badge}
            </p>
            <h3 className="mt-2 text-lg font-semibold tracking-tight">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {body}
            </p>

            <div className="mt-auto flex flex-wrap gap-2 pt-5">
                {options.map((option) => (
                    <a
                        key={`${option.label}-${option.detail ?? option.href}`}
                        href={option.href}
                        className="group inline-flex min-h-10 items-center gap-2 rounded-lg border border-border bg-background px-3.5 py-2 text-sm font-medium transition-colors hover:border-primary/40 hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        aria-label={option.detail ? `${option.label} — ${option.detail}` : option.label}
                    >
                        <span>{option.label}</span>
                        {option.detail && (
                            <span className="font-mono text-[10px] font-normal text-muted-foreground">
                                {option.detail}
                            </span>
                        )}
                        <span
                            aria-hidden="true"
                            className="text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-foreground"
                        >
                            →
                        </span>
                    </a>
                ))}
            </div>
        </article>
    );
}

function Download() {
    const version = useLatestRelease();
    const { t } = useI18n();
    const releasesUrl = "https://github.com/rafatosta/zapzap/releases";
    const releaseUrl = version
        ? `${releasesUrl}/tag/${version}`
        : `${releasesUrl}/latest`;
    const releaseAsset = (filename: string) =>
        version
            ? `${releasesUrl}/latest/download/${filename}`
            : `${releasesUrl}/latest`;

    const linuxDownloads: DownloadCardProps[] = [
        {
            badge: t("download.recommendedOfficial"),
            title: "Flatpak",
            body: t("download.flatpak.body"),
            highlighted: true,
            options: [
                {
                    label: t("download.flatpak.action"),
                    href: "https://flathub.org/apps/com.rtosta.zapzap",
                },
            ],
        },
        {
            badge: t("download.portableOfficial"),
            title: "AppImage",
            body: t("download.appimage.body"),
            options: [
                {
                    label: t("download.action"),
                    detail: "x86_64",
                    href: releaseAsset(`ZapZap-${version}-linux-x86_64.AppImage`),
                },
                {
                    label: t("download.action"),
                    detail: "ARM64",
                    href: releaseAsset(`ZapZap-${version}-linux-aarch64.AppImage`),
                },
            ],
        },
        {
            badge: t("download.nativeOfficial"),
            title: "Debian / Ubuntu",
            body: t("download.debian.body"),
            options: [
                {
                    label: t("download.debian.action"),
                    detail: "x86_64",
                    href: releaseAsset(`zapzap-${version}-amd64.deb`),
                },
            ],
        },
        {
            badge: t("download.storeOfficial"),
            title: "Snap",
            body: t("download.snap.body"),
            options: [
                {
                    label: t("download.snap.action"),
                    href: "https://snapcraft.io/zapzap",
                },
            ],
        },
        {
            badge: t("download.repositoryOfficial"),
            title: "Fedora",
            body: t("download.fedora.body"),
            options: [
                {
                    label: t("download.fedora.action"),
                    href: "https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/",
                },
            ],
        },
        {
            badge: t("download.communityUnofficial"),
            title: "Arch Linux (AUR)",
            body: t("download.aur.body"),
            unofficial: true,
            options: [
                {
                    label: t("download.aur.action"),
                    href: "https://aur.archlinux.org/packages/zapzap",
                },
            ],
        },
    ];

    const desktopDownloads: DownloadCardProps[] = [
        {
            badge: t("download.official"),
            title: "Windows (.exe)",
            body: t("download.windows.body"),
            options: [
                {
                    label: t("download.action"),
                    detail: "x86_64",
                    href: releaseAsset(`ZapZap-${version}-windows-x86_64.exe`),
                },
                {
                    label: t("download.action"),
                    detail: "ARM64",
                    href: releaseAsset(`ZapZap-${version}-windows-arm64.exe`),
                },
            ],
        },
        {
            badge: t("download.official"),
            title: "macOS (.dmg)",
            body: t("download.macos.body"),
            options: [
                {
                    label: t("download.appleSilicon"),
                    detail: "ARM64",
                    href: releaseAsset(`ZapZap-${version}-macos-arm64.dmg`),
                },
                {
                    label: t("download.intel"),
                    detail: "x86_64",
                    href: releaseAsset(`ZapZap-${version}-macos-x86_64.dmg`),
                },
            ],
        },
    ];

    return (
        <section id="download" className="border-t border-hairline">
            <div className="mx-auto max-w-6xl px-6 py-24">
                <div className="flex flex-wrap items-end justify-between gap-4">
                    <div className="max-w-2xl">
                        <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                            {t("download.eyebrow")}
                        </p>
                        <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                            {t("download.title")}
                        </h2>
                        <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                            {t("download.description")}
                        </p>
                    </div>
                    <a
                        href={releaseUrl}
                        className="font-mono text-xs text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                        {version
                            ? t("download.latest", { version })
                            : t("download.viewLatest")} →
                    </a>
                </div>

                <div className="mt-12">
                    <div className="flex items-baseline justify-between gap-4">
                        <h3 className="text-xl font-semibold tracking-tight">Linux</h3>
                        <p className="text-xs text-muted-foreground">{t("download.linuxSubtitle")}</p>
                    </div>
                    <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {linuxDownloads.map((download) => (
                            <DownloadCard key={download.title} {...download} />
                        ))}
                    </div>
                </div>

                <div className="mt-12 border-t border-hairline pt-10">
                    <div className="flex items-baseline justify-between gap-4">
                        <h3 className="text-xl font-semibold tracking-tight">{t("download.desktopTitle")}</h3>
                        <p className="text-xs text-muted-foreground">{t("download.desktopSubtitle")}</p>
                    </div>
                    <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
                        {desktopDownloads.map((download) => (
                            <DownloadCard key={download.title} {...download} />
                        ))}
                    </div>
                </div>

                <div className="mt-8 flex flex-col gap-4 rounded-xl border border-border bg-subtle/60 p-5 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <p className="text-sm font-semibold">{t("download.advanced.title")}</p>
                        <p className="mt-1 text-sm text-muted-foreground">
                            {t("download.advanced.body")}
                        </p>
                    </div>
                    <a
                        href={releaseUrl}
                        className="inline-flex shrink-0 items-center gap-2 text-sm font-medium text-foreground hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                        {t("download.advanced.action")} <span aria-hidden="true">→</span>
                    </a>
                </div>
            </div>
        </section>
    );
}

export default Download;
