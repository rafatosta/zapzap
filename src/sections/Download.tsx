import { useLatestRelease } from "../hooks/useLatestRelease";

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
            badge: "Recommended · Official",
            title: "Flatpak",
            body: "The easiest option for most Linux distributions, distributed through Flathub with automatic updates.",
            highlighted: true,
            options: [
                {
                    label: "Open Flathub",
                    href: "https://flathub.org/apps/com.rtosta.zapzap",
                },
            ],
        },
        {
            badge: "Portable · Official",
            title: "AppImage",
            body: "Run ZapZap without installing it. Choose the build that matches your computer's architecture.",
            options: [
                {
                    label: "Download",
                    detail: "x86_64",
                    href: releaseAsset(`ZapZap-${version}-linux-x86_64.AppImage`),
                },
                {
                    label: "Download",
                    detail: "ARM64",
                    href: releaseAsset(`ZapZap-${version}-linux-aarch64.AppImage`),
                },
            ],
        },
        {
            badge: "Native package · Official",
            title: "Debian / Ubuntu",
            body: "A .deb package for 64-bit Debian, Ubuntu and compatible distributions.",
            options: [
                {
                    label: "Download .deb",
                    detail: "x86_64",
                    href: releaseAsset(`zapzap-${version}-amd64.deb`),
                },
            ],
        },
        {
            badge: "Store · Official",
            title: "Snap",
            body: "Install through Snapcraft and receive updates automatically.",
            options: [
                {
                    label: "Open Snapcraft",
                    href: "https://snapcraft.io/zapzap",
                },
            ],
        },
        {
            badge: "Repository · Official",
            title: "Fedora",
            body: "Install from the official COPR repository and keep ZapZap updated with DNF.",
            options: [
                {
                    label: "Open COPR",
                    href: "https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/",
                },
            ],
        },
        {
            badge: "Community · Unofficial",
            title: "Arch Linux (AUR)",
            body: "This package is maintained by the Arch community. It is not built, published or supported by the ZapZap project.",
            unofficial: true,
            options: [
                {
                    label: "View community package",
                    href: "https://aur.archlinux.org/packages/zapzap",
                },
            ],
        },
    ];

    const desktopDownloads: DownloadCardProps[] = [
        {
            badge: "Official",
            title: "Windows (.exe)",
            body: "Native Windows builds with no additional dependencies. Available for Intel/AMD and ARM PCs.",
            options: [
                {
                    label: "Download",
                    detail: "x86_64",
                    href: releaseAsset(`ZapZap-${version}-windows-x86_64.exe`),
                },
                {
                    label: "Download",
                    detail: "ARM64",
                    href: releaseAsset(`ZapZap-${version}-windows-arm64.exe`),
                },
            ],
        },
        {
            badge: "Official",
            title: "macOS (.dmg)",
            body: "Disk images for modern Apple Silicon Macs and Intel-based Macs.",
            options: [
                {
                    label: "Apple Silicon",
                    detail: "ARM64",
                    href: releaseAsset(`ZapZap-${version}-macos-arm64.dmg`),
                },
                {
                    label: "Intel",
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
                            Download
                        </p>
                        <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                            Choose your platform and format.
                        </h2>
                        <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                            Use a software store for simple automatic updates, or download a standalone package for your system and architecture.
                        </p>
                    </div>
                    <a
                        href={releaseUrl}
                        className="font-mono text-xs text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                        {version ? `Latest · v${version}` : "View latest release"} →
                    </a>
                </div>

                <div className="mt-12">
                    <div className="flex items-baseline justify-between gap-4">
                        <h3 className="text-xl font-semibold tracking-tight">Linux</h3>
                        <p className="text-xs text-muted-foreground">Stores, repositories and portable packages</p>
                    </div>
                    <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {linuxDownloads.map((download) => (
                            <DownloadCard key={download.title} {...download} />
                        ))}
                    </div>
                </div>

                <div className="mt-12 border-t border-hairline pt-10">
                    <div className="flex items-baseline justify-between gap-4">
                        <h3 className="text-xl font-semibold tracking-tight">Windows &amp; macOS</h3>
                        <p className="text-xs text-muted-foreground">Select your processor architecture</p>
                    </div>
                    <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
                        {desktopDownloads.map((download) => (
                            <DownloadCard key={download.title} {...download} />
                        ))}
                    </div>
                </div>

                <div className="mt-8 flex flex-col gap-4 rounded-xl border border-border bg-subtle/60 p-5 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <p className="text-sm font-semibold">Advanced downloads</p>
                        <p className="mt-1 text-sm text-muted-foreground">
                            Find the Python wheel, update files, source archives and SHA-256 digests on GitHub.
                        </p>
                    </div>
                    <a
                        href={releaseUrl}
                        className="inline-flex shrink-0 items-center gap-2 text-sm font-medium text-foreground hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                        View all release files <span aria-hidden="true">→</span>
                    </a>
                </div>
            </div>
        </section>
    );
}

export default Download;
