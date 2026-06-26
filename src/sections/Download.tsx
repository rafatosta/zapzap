import { useLatestRelease } from "../hooks/useLatestRelease";

function Download() {


    const version = useLatestRelease();

    const downloads = [
        {
            tag: "Recommended",
            title: "Flatpak",
            body: "Sandboxed package distributed through Flathub. Automatic updates and broad compatibility across Linux distributions.",
            href: "https://flathub.org/apps/com.rtosta.zapzap",
        },
        {
            tag: "Portable",
            title: "AppImage aarch64",
            body: "Portable package for ARM64 devices. No installation required and supports automatic update checks.",
            href: `https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-${version}-linux-aarch64.AppImage`,
        },
        {
            tag: "Portable",
            title: "AppImage x86_64",
            body: "Portable package for 64-bit PCs. Download, make executable and run. Supports automatic update checks.",
            href: `https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-${version}-linux-x86_64.AppImage`,
        },
        {
            tag: "Fedora",
            title: "DNF / Copr",
            body: "Official Copr repository for Fedora with native DNF integration and automatic system updates.",
            href: "https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/",
        },
        {
            tag: "Debian",
            title: "APT (.deb)",
            body: "Native package for Debian, Ubuntu and derivatives. Integrates with the system package manager.",
            href: `https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-${version}-linux-amd64.deb`,
        },
        {
            tag: "Universal",
            title: "Snap",
            body: "Containerized package with automatic updates through the Snap Store.",
            href: "https://snapcraft.io/zapzap",
        },
        {
            tag: "Arch",
            title: "AUR",
            body: "Install using your preferred AUR helper. Community-maintained package for Arch Linux.",
            href: "https://aur.archlinux.org/packages/zapzap",
        },
        {
            tag: "Windows",
            title: "Portable (.exe)",
            body: "Portable Windows build. Extract and run without installation. Ideal for restricted environments.",
            href: `https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-${version}-windows-x86_64.exe`,
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
                            Choose your distribution.
                        </h2>
                        <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                            Four formats covering virtually every Linux distribution.
                            Checksums published with every release.
                        </p>
                    </div>
                    <p className="font-mono text-xs text-muted-foreground">
                        Latest&nbsp;·&nbsp;v{version}
                    </p>
                </div>

                <div className="mt-12 grid grid-cols-1 divide-y divide-hairline overflow-hidden rounded-xl border border-border bg-card md:grid-cols-2 md:divide-y-0 md:[&>*:nth-child(odd)]:border-r md:[&>*:nth-child(odd)]:border-hairline md:[&>*:nth-child(n+3)]:border-t md:[&>*:nth-child(n+3)]:border-hairline">
                    {downloads.map((d) => (
                        <a
                            key={d.title}
                            href={d.href}
                            className="group flex items-start justify-between gap-6 p-7 transition-colors hover:bg-subtle"
                        >
                            <div>
                                <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                                    {d.tag}
                                </p>
                                <h3 className="mt-2 text-lg font-semibold tracking-tight">
                                    {d.title}
                                </h3>
                                <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">
                                    {d.body}
                                </p>
                            </div>
                            <span
                                aria-hidden
                                className="mt-1 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-foreground"
                            >
                                →
                            </span>
                        </a>
                    ))}
                </div>
            </div>
        </section>


    );
}

export default Download;