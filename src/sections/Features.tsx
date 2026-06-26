function Features() {

    const features = [
        { title: "Multiple accounts", body: "Run several WhatsApp accounts side by side in one window." },
        { title: "Native notifications", body: "Desktop notifications that integrate with your Linux environment." },
        { title: "Drag & drop media", body: "Send photos, videos and documents straight from your file manager." },
        { title: "Adaptive theming", body: "Follows your system light or dark theme automatically." },
        { title: "Privacy first", body: "No telemetry, no data collection. The source is open and auditable." },
        { title: "Background mode", body: "Stay reachable from the system tray, even when minimized." },
    ];

    return (
        <section id="features" className="border-t border-hairline bg-subtle">
            <div className="mx-auto max-w-6xl px-6 py-24">
                <div className="max-w-2xl">
                    <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                        Features
                    </p>
                    <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                        Everything you expect from a desktop app.
                    </h2>
                    <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                        ZapZap focuses on a complete, native WhatsApp experience for the
                        Linux desktop — without the bloat.
                    </p>
                </div>

                <ul className="mt-14 grid grid-cols-1 gap-x-10 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
                    {features.map((f, i) => (
                        <li key={f.title} className="border-t border-hairline pt-5">
                            <div className="flex items-center gap-3">
                                <span className="font-mono text-[11px] tabular-nums text-muted-foreground">
                                    {String(i + 1).padStart(2, "0")}
                                </span>
                                <h3 className="text-[15px] font-semibold tracking-tight">
                                    {f.title}
                                </h3>
                            </div>
                            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                                {f.body}
                            </p>
                        </li>
                    ))}
                </ul>
            </div>
        </section>
    );
}

export default Features;