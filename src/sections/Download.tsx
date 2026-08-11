import { useState } from "react";

import { useLatestRelease } from "../hooks/useLatestRelease";
import { useI18n } from "../i18n/useI18n";

type Platform = "linux" | "windows" | "macos";

type DownloadOption = {
    label: string;
    href?: string;
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

function detectPlatform(): Platform {
    const userAgent = window.navigator.userAgent.toLowerCase();

    if (userAgent.includes("windows")) {
        return "windows";
    }

    if (userAgent.includes("macintosh") || userAgent.includes("mac os")) {
        return "macos";
    }

    return "linux";
}

const optionClass =
    "group inline-flex min-h-11 items-center gap-2 rounded-lg border border-border bg-background px-3.5 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

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
                className={`font-mono text-[11px] uppercase tracking-wider ${
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
                {options.map((option) => {
                    const content = (
                        <>
                            <span>{option.label}</span>
                            {option.detail && (
                                <span className="font-mono text-[11px] font-normal text-muted-foreground">
                                    {option.detail}
                                </span>
                            )}
                            <span
                                aria-hidden="true"
                                className="text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-foreground"
                            >
                                →
                            </span>
                        </>
                    );
                    const accessibleLabel = option.detail
                        ? `${option.label} — ${option.detail}`
                        : option.label;

                    return option.href ? (
                        <a
                            key={`${option.label}-${option.detail ?? option.href}`}
                            href={option.href}
                            className={`${optionClass} hover:border-primary/40 hover:bg-accent`}
                            aria-label={accessibleLabel}
                            target={option.href.includes("/download/") ? undefined : "_blank"}
                            rel={option.href.includes("/download/") ? undefined : "noopener noreferrer"}
                        >
                            {content}
                        </a>
                    ) : (
                        <span
                            key={`${option.label}-${option.detail}`}
                            className={`${optionClass} cursor-wait opacity-50`}
                            aria-label={accessibleLabel}
                            aria-disabled="true"
                        >
                            {content}
                        </span>
                    );
                })}
            </div>
        </article>
    );
}

function Download() {
    const { version, loading, error } = useLatestRelease();
    const { t } = useI18n();
    const [platform, setPlatform] = useState<Platform>(detectPlatform);
    const releasesUrl = "https://github.com/rafatosta/zapzap/releases";
    const releaseUrl = version
        ? `${releasesUrl}/tag/${version}`
        : `${releasesUrl}/latest`;
    const releaseAsset = (filename: string) =>
        version ? `${releasesUrl}/latest/download/${filename}` : undefined;

    const downloads: Record<Platform, DownloadCardProps[]> = {
        linux: [
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
        ],
        windows: [
            {
                badge: t("download.official"),
                title: "Windows (.exe)",
                body: t("download.windows.body"),
                highlighted: true,
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
        ],
        macos: [
            {
                badge: t("download.official"),
                title: "macOS (.dmg)",
                body: t("download.macos.body"),
                highlighted: true,
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
        ],
    };

    const tabs: Array<{ id: Platform; label: string; subtitle: string }> = [
        { id: "linux", label: "Linux", subtitle: t("download.linuxSubtitle") },
        { id: "windows", label: "Windows", subtitle: t("download.windowsSubtitle") },
        { id: "macos", label: "macOS", subtitle: t("download.macosSubtitle") },
    ];
    const activeTab = tabs.find((tab) => tab.id === platform) ?? tabs[0];

    return (
        <section id="download" className="scroll-mt-14 border-t border-hairline">
            <div className="mx-auto max-w-6xl px-6 py-20 md:py-24">
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
                    <p
                        className="font-mono text-xs text-muted-foreground"
                        aria-live="polite"
                    >
                        {loading
                            ? t("download.releaseLoading")
                            : error
                              ? t("download.releaseError")
                              : t("download.latest", { version: version ?? "" })}
                    </p>
                </div>

                <div
                    className="mt-10 inline-flex w-full rounded-xl border border-border bg-subtle p-1 sm:w-auto"
                    role="group"
                    aria-label={t("download.platformLabel")}
                >
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            type="button"
                            aria-pressed={platform === tab.id}
                            onClick={() => setPlatform(tab.id)}
                            className={`min-h-11 flex-1 rounded-lg px-5 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring sm:flex-none ${
                                platform === tab.id
                                    ? "bg-card text-foreground shadow-sm"
                                    : "text-muted-foreground hover:text-foreground"
                            }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div
                    className="mt-8"
                >
                    <div className="mb-5">
                        <h3 className="text-xl font-semibold tracking-tight">{activeTab.label}</h3>
                        <p className="mt-1 text-sm text-muted-foreground">{activeTab.subtitle}</p>
                    </div>
                    <div
                        className={`grid grid-cols-1 gap-4 md:grid-cols-2 ${
                            platform === "linux" ? "lg:grid-cols-3" : ""
                        }`}
                    >
                        {downloads[platform].map((download) => (
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
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-md text-sm font-medium text-foreground hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                        {t("download.advanced.action")} <span aria-hidden="true">→</span>
                    </a>
                </div>
            </div>
        </section>
    );
}

export default Download;
