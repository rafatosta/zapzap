function Features() {
    const features = [
        {
            title: "Multiple accounts",
            body: "Manage multiple WhatsApp accounts simultaneously in a single application.",
        },
        {
            title: "Native desktop integration",
            body: "System tray, notifications and desktop behavior designed for Linux.",
        },
        {
            title: "Native Linux packages",
            body: "Available as Flatpak, AppImage, Snap, DEB and Fedora COPR.",
        },
        {
            title: "Automatic updates",
            body: "AppImage releases support efficient delta updates through .zsync.",
        },
        {
            title: "Open source",
            body: "GPL-3.0 licensed, transparent and community-driven development.",
        },
        {
            title: "Privacy focused",
            body: "A dedicated desktop application without relying on a browser session.",
        },
        {
            title: "Spell checking",
            body: "Built-in spell checker with multiple dictionaries and language support.",
        },
        {
            title: "Custom CSS & JavaScript",
            body: "Personalize the WhatsApp interface with your own styles and scripts.",
        },
        {
            title: "Cross-platform",
            body: "Available for Linux, Windows and Python environments.",
        },
    ];

    return (
        <section id="features" className="border-t border-hairline bg-subtle">
            <div className="mx-auto max-w-6xl px-6 py-24">
                <div className="max-w-2xl">
                    <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                        Why ZapZap?
                    </p>

                    <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                        A better desktop experience for WhatsApp.
                    </h2>

                    <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                        ZapZap stays close to the official WhatsApp Web experience while
                        adding the native integrations Linux users expect from a modern
                        desktop application.
                    </p>
                </div>

                <ul className="mt-14 grid grid-cols-1 gap-x-10 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
                    {features.map((feature, index) => (
                        <li
                            key={feature.title}
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